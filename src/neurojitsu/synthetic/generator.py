"""Reproducible synthetic data for development without participant privacy risk."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd

from neurojitsu.core.models import (
    IdentityStatus,
    MetricValue,
    SessionPhase,
    SessionWindow,
)

_PHASES = [
    SessionPhase.WARM_UP,
    SessionPhase.TECHNICAL_DRILLS,
    SessionPhase.COOPERATIVE_GAMES,
    SessionPhase.COOL_DOWN,
]


def generate_session_dataframe(
    participant_id: str = "C001",
    session_id: str = "NJ-DEMO-001",
    windows_per_phase: int = 12,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate timestamped metrics that match the real processing contract."""
    rng = np.random.default_rng(seed)
    started = datetime.now(UTC).replace(microsecond=0)
    rows: list[dict[str, object]] = []
    offset = 0
    for phase_index, phase in enumerate(_PHASES):
        for _index in range(windows_per_phase):
            timestamp = started + timedelta(seconds=offset)
            movement = max(0.0, rng.normal(0.45 + phase_index * 0.08, 0.08))
            participation = float(np.clip(rng.normal(0.72, 0.12), 0.0, 1.0))
            confidence = float(np.clip(rng.normal(0.84, 0.08), 0.0, 1.0))
            rows.append(
                {
                    "session_id": session_id,
                    "participant_id": participant_id,
                    "timestamp": timestamp,
                    "phase": phase.value,
                    "movement_index": movement,
                    "participation_ratio": participation,
                    "symmetry_difference_percent": abs(rng.normal(12 - phase_index, 3)),
                    "rmssd_ms": max(8.0, rng.normal(34 - phase_index * 3, 4)),
                    "confidence": confidence,
                }
            )
            offset += 30
    return pd.DataFrame(rows)


def dataframe_to_windows(dataframe: pd.DataFrame) -> list[SessionWindow]:
    """Convert synthetic rows into the same windows used by the analytic agents."""
    windows: list[SessionWindow] = []
    for row in dataframe.to_dict(orient="records"):
        start = pd.Timestamp(row["timestamp"]).to_pydatetime()
        confidence = float(row["confidence"])
        windows.append(
            SessionWindow(
                session_id=str(row["session_id"]),
                participant_id=str(row["participant_id"]),
                timestamp_start=start,
                timestamp_end=start + timedelta(seconds=30),
                phase=SessionPhase(str(row["phase"])),
                identity_status=IdentityStatus.CONFIRMED,
                metrics=[
                    MetricValue(
                        name="movement_index",
                        value=float(row["movement_index"]),
                        unit="a.u.",
                        confidence=confidence,
                        valid=True,
                    ),
                    MetricValue(
                        name="participation_ratio",
                        value=float(row["participation_ratio"]),
                        unit="ratio",
                        confidence=confidence,
                        valid=True,
                    ),
                    MetricValue(
                        name="symmetry_difference_percent",
                        value=float(row["symmetry_difference_percent"]),
                        unit="%",
                        confidence=confidence,
                        valid=True,
                    ),
                    MetricValue(
                        name="rmssd_ms",
                        value=float(row["rmssd_ms"]),
                        unit="ms",
                        confidence=confidence,
                        valid=True,
                    ),
                ],
            )
        )
    return windows
