"""Session-phase assignment and RMSSD recovery deltas."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from itertools import pairwise

import pandas as pd

from neurojitsu.core.models import PhaseBoundary, SessionPhase


def validate_boundaries(boundaries: Iterable[PhaseBoundary]) -> list[PhaseBoundary]:
    """Sort and validate non-overlapping phase boundaries."""
    ordered = sorted(boundaries, key=lambda item: item.start)
    if not ordered:
        raise ValueError("At least one phase boundary is required")
    for previous, current in pairwise(ordered):
        if current.start < previous.end:
            raise ValueError(f"Overlapping phases: {previous.phase} and {current.phase}")
    return ordered


def tag_phases(
    metrics_df: pd.DataFrame,
    boundaries: Iterable[PhaseBoundary],
    timestamp_column: str = "timestamp",
) -> pd.DataFrame:
    """Add a canonical phase to each timestamped metric row.

    Missing intervals are explicitly tagged ``unassigned`` instead of being silently
    attributed to a neighboring phase.
    """
    if timestamp_column not in metrics_df.columns:
        raise ValueError(f"Missing timestamp column: {timestamp_column}")

    ordered = validate_boundaries(boundaries)
    result = metrics_df.copy()
    result[timestamp_column] = pd.to_datetime(result[timestamp_column], utc=True, errors="raise")
    result["phase"] = SessionPhase.UNASSIGNED.value

    for boundary in ordered:
        start = pd.Timestamp(boundary.start)
        end = pd.Timestamp(boundary.end)
        mask = (result[timestamp_column] >= start) & (result[timestamp_column] < end)
        result.loc[mask, "phase"] = boundary.phase.value
    return result


def calculate_delta_rmssd_recovery(
    tagged_df: pd.DataFrame,
    rmssd_column: str = "rmssd_ms",
) -> pd.DataFrame:
    """Calculate phase-to-phase changes in median RMSSD.

    This function describes change; it does not interpret autonomic state or stress.
    """
    required = {"phase", rmssd_column}
    missing = required.difference(tagged_df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    usable = tagged_df[tagged_df["phase"] != SessionPhase.UNASSIGNED.value].copy()
    usable[rmssd_column] = pd.to_numeric(usable[rmssd_column], errors="coerce")
    grouped = (
        usable.dropna(subset=[rmssd_column])
        .groupby("phase", sort=False)[rmssd_column]
        .median()
        .reset_index(name="median_rmssd_ms")
    )
    grouped["delta_rmssd_from_previous_phase_ms"] = grouped["median_rmssd_ms"].diff()
    return grouped


def boundaries_from_minutes(
    session_start: datetime,
    phases: list[tuple[SessionPhase, float, float]],
) -> list[PhaseBoundary]:
    """Build absolute boundaries from minute offsets."""
    return [
        PhaseBoundary(
            phase=phase,
            start=session_start + pd.Timedelta(minutes=start_minute),
            end=session_start + pd.Timedelta(minutes=end_minute),
        )
        for phase, start_minute, end_minute in phases
    ]
