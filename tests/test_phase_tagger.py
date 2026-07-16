from datetime import UTC, datetime, timedelta

import pandas as pd

from neurojitsu.analysis.phase_tagger import calculate_delta_rmssd_recovery, tag_phases
from neurojitsu.core.models import PhaseBoundary, SessionPhase


def test_tag_phases_marks_gaps_as_unassigned() -> None:
    start = datetime(2026, 7, 16, tzinfo=UTC)
    dataframe = pd.DataFrame(
        {
            "timestamp": [
                start + timedelta(minutes=1),
                start + timedelta(minutes=15),
                start + timedelta(minutes=70),
            ],
            "rmssd_ms": [30, 25, 20],
        }
    )
    boundaries = [
        PhaseBoundary(phase=SessionPhase.WARM_UP, start=start, end=start + timedelta(minutes=10)),
        PhaseBoundary(
            phase=SessionPhase.TECHNICAL_DRILLS,
            start=start + timedelta(minutes=10),
            end=start + timedelta(minutes=35),
        ),
    ]
    result = tag_phases(dataframe, boundaries)
    assert result["phase"].tolist() == ["warm_up", "technical_drills", "unassigned"]


def test_overlapping_boundaries_are_rejected() -> None:
    start = datetime(2026, 7, 16, tzinfo=UTC)
    boundaries = [
        PhaseBoundary(phase=SessionPhase.WARM_UP, start=start, end=start + timedelta(minutes=10)),
        PhaseBoundary(
            phase=SessionPhase.TECHNICAL_DRILLS,
            start=start + timedelta(minutes=9),
            end=start + timedelta(minutes=20),
        ),
    ]
    try:
        tag_phases(pd.DataFrame({"timestamp": [start]}), boundaries)
    except ValueError as exc:
        assert "Overlapping" in str(exc)
    else:
        raise AssertionError("Expected overlap validation error")


def test_delta_rmssd_uses_phase_medians() -> None:
    tagged = pd.DataFrame(
        {
            "phase": ["warm_up", "warm_up", "cool_down", "cool_down"],
            "rmssd_ms": [20, 30, 40, 50],
        }
    )
    result = calculate_delta_rmssd_recovery(tagged)
    assert result.loc[0, "median_rmssd_ms"] == 25
    assert result.loc[1, "delta_rmssd_from_previous_phase_ms"] == 20
