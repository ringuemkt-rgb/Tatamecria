from datetime import UTC, datetime, timedelta

import pytest

from neurojitsu.analysis.camera_metrics import frames_to_windows
from neurojitsu.core.models import IdentityStatus, PoseFrame


def _frames(confirmed=True, bad=False):
    pts = [(0.5, 0.5, 0.0, 0.99) for _ in range(33)]
    for index, x, y in ((11,.44,.27),(12,.56,.27),(23,.44,.52),
                        (24,.56,.52),(25,.44,.72),(26,.56,.72),
                        (27,.44,.91),(28,.56,.91)):
        pts[index] = (x, y, 0.0, 0.99)
    start = datetime(2026, 10, 1, tzinfo=UTC)
    return [
        PoseFrame(
            session_id="LAB-001", participant_id="A001",
            timestamp=start + timedelta(milliseconds=i * 33),
            frame_index=i, frame_width=640, frame_height=480,
            landmarks_xyzc=[] if bad else pts,
            valid_landmark_ratio=0.0 if bad else 1.0,
            tracking_confidence=0.0 if bad else 0.99,
            identity_status=(
                IdentityStatus.CONFIRMED if confirmed else IdentityStatus.UNCERTAIN
            ),
        ) for i in range(10)
    ]


def test_synthetic_angles() -> None:
    windows = frames_to_windows(_frames(), "stand", "cam", "cal-v1", "pose-v1")
    left = next(m for m in windows[0].metrics if m.name == "left_knee_angle")
    assert left.valid and left.value == pytest.approx(180.0)
    assert windows[0].metadata["task_id"] == "stand"


def test_uncertain_identity_invalidates_metrics() -> None:
    windows = frames_to_windows(_frames(confirmed=False), "stand", "cam", "cal", "pose")
    assert all(not m.valid and m.value is None for m in windows[0].metrics)


def test_missing_keypoints_invalidates_metrics() -> None:
    windows = frames_to_windows(_frames(bad=True), "stand", "cam", "cal", "pose")
    assert all(not m.valid for m in windows[0].metrics)


def test_mixed_identity_rejected() -> None:
    f = _frames()
    f[3].participant_id = "A002"
    with pytest.raises(ValueError, match="Mixed"):
        frames_to_windows(f, "stand", "cam", "cal", "pose")
