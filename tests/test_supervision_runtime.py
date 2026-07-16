from types import SimpleNamespace

import numpy as np
import pytest

from neurojitsu.vision import supervision_runtime
from neurojitsu.vision.supervision_runtime import (
    DetectionRecord,
    ZoneDefinition,
    detections_to_supervision,
)


class FakeDetections:
    def __init__(
        self,
        xyxy: np.ndarray,
        confidence: np.ndarray | None = None,
        class_id: np.ndarray | None = None,
        tracker_id: np.ndarray | None = None,
        data: dict[str, object] | None = None,
    ) -> None:
        self.xyxy = xyxy
        self.confidence = confidence
        self.class_id = class_id
        self.tracker_id = tracker_id
        self.data = data or {}
        self.metadata: dict[str, object] = {}

    @classmethod
    def empty(cls) -> "FakeDetections":
        return cls(np.empty((0, 4), dtype=np.float32))


def test_detection_record_rejects_invalid_box() -> None:
    with pytest.raises(ValueError):
        DetectionRecord(track_id=1, xyxy=(10.0, 10.0, 5.0, 20.0), confidence=0.9)


def test_zone_definition_requires_polygon() -> None:
    with pytest.raises(ValueError):
        ZoneDefinition(name="tatame", points=((0, 0), (10, 0)))


def test_detection_conversion_preserves_track_and_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_sv = SimpleNamespace(Detections=FakeDetections)
    monkeypatch.setattr(supervision_runtime, "_load_supervision", lambda: fake_sv)

    detections = detections_to_supervision(
        [
            DetectionRecord(
                track_id=4,
                xyxy=(1.0, 2.0, 30.0, 40.0),
                confidence=0.88,
                participant_id="C001",
            )
        ],
        metadata={"camera_id": "CAM-A"},
    )

    assert detections.tracker_id.tolist() == [4]
    assert detections.data["participant_id"] == ["C001"]
    assert detections.metadata == {"camera_id": "CAM-A"}
