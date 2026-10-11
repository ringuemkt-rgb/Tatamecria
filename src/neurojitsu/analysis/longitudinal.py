"""Within-person descriptive comparison with explicit acquisition comparability gates."""
from __future__ import annotations

from statistics import mean
from typing import Any

from neurojitsu.core.models import IdentityStatus
from neurojitsu.storage.database import Database


def longitudinal_summary(
    database: Database, participant_id: str, task_id: str, metric_name: str
) -> dict[str, Any]:
    """Compare valid, operator-confirmed metrics of the same standardized task.

    Differences are descriptive, not a judgement of development or clinical improvement.
    """
    records: list[dict[str, Any]] = []
    for session in database.list_sessions():
        if session["participant_id"] != participant_id:
            continue
        windows = database.load_windows(str(session["session_id"]))
        matching = [w for w in windows if w.metadata.get("task_id") == task_id]
        if not matching:
            continue
        reference = matching[0].metadata
        values: list[float] = []
        units: set[str] = set()
        for window in matching:
            if window.identity_status is not IdentityStatus.CONFIRMED:
                continue
            for metric in window.metrics:
                if metric.name == metric_name and metric.valid and metric.value is not None:
                    values.append(metric.value)
                    units.add(metric.unit)
        if len(units) > 1:
            raise ValueError("Incompatible metric units within a session")
        records.append(
            {
                "session_id": session["session_id"],
                "timestamp": matching[0].timestamp_start.isoformat(),
                "value": float(mean(values)) if values else None,
                "valid_windows": len(values),
                "total_windows": len(matching),
                "unit": next(iter(units), None),
                "camera_id": reference.get("camera_id"),
                "calibration_id": reference.get("calibration_id"),
                "backend_version": reference.get("backend_version"),
            }
        )
    records.sort(key=lambda row: (str(row["timestamp"]), str(row["session_id"])))
    baseline = next((r for r in records if r["value"] is not None), None)
    for row in records:
        comparable = (
            baseline is not None
            and row["value"] is not None
            and row["unit"] == baseline["unit"]
            and bool(row["calibration_id"])
            and row["calibration_id"] == baseline["calibration_id"]
            and row["camera_id"] == baseline["camera_id"]
            and row["backend_version"] == baseline["backend_version"]
        )
        row["comparable_to_baseline"] = comparable
        row["delta_from_baseline"] = (
            float(row["value"] - baseline["value"]) if comparable and baseline else None
        )
        row["percent_change_from_baseline"] = (
            100.0 * float(row["value"] - baseline["value"]) / abs(float(baseline["value"]))
            if comparable and baseline and baseline["value"] != 0
            else None
        )
    return {
        "participant_id": participant_id,
        "task_id": task_id,
        "metric_name": metric_name,
        "baseline_session_id": baseline["session_id"] if baseline else None,
        "sessions": records,
        "notice": (
            "Descriptive research measurements only. Changes can reflect camera geometry, "
            "practice, task execution, measurement error or other factors. "
            "Not an autism or clinical development score."
        ),
    }
