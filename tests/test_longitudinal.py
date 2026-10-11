from datetime import UTC, datetime, timedelta

from neurojitsu.analysis.longitudinal import longitudinal_summary
from neurojitsu.core.models import IdentityStatus, MetricValue, SessionPhase, SessionWindow
from neurojitsu.storage.database import Database


def test_longitudinal_requires_same_calibration(tmp_path) -> None:
    db = Database(tmp_path / "test.db")
    db.register_participant("A001", synthetic=True)
    for week, value, calib in [(0, 15.0, "same"), (4, 12.0, "same"), (8, 9.0, "other")]:
        sid = f"LAB-{week}"
        start = datetime(2026, 10, 1, tzinfo=UTC) + timedelta(weeks=week)
        db.create_session(sid, "A001", start)
        db.store_windows([SessionWindow(
            session_id=sid, participant_id="A001", timestamp_start=start,
            timestamp_end=start + timedelta(seconds=2),
            phase=SessionPhase.TECHNICAL_DRILLS,
            identity_status=IdentityStatus.CONFIRMED,
            metrics=[MetricValue(name="trunk_inclination_image", value=value,
                                 unit="deg", confidence=0.95, valid=True)],
            metadata={"task_id":"stand", "camera_id":"cam", "calibration_id":calib,
                      "backend_version":"v1"},
        )])
    summary = longitudinal_summary(db,"A001","stand","trunk_inclination_image")
    assert len(summary["sessions"]) == 3
    assert summary["sessions"][1]["delta_from_baseline"] == -3.0
    assert summary["sessions"][2]["delta_from_baseline"] is None
