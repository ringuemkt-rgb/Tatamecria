"""Runtime bridge between NeuroJitsu contracts and Roboflow Supervision.

Supervision is used as a model-agnostic computer-vision transport layer. It does
not decide identity, clinical meaning, or biomechanical validity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from neurojitsu.vision.wholebody import LandmarkRegion, PersonWholeBodyPose


@dataclass(frozen=True, slots=True)
class DetectionRecord:
    """Model-independent person detection with an already assigned temporary track."""

    track_id: int
    xyxy: tuple[float, float, float, float]
    confidence: float
    class_id: int = 0
    participant_id: str | None = None

    def __post_init__(self) -> None:
        x1, y1, x2, y2 = self.xyxy
        if self.track_id < 0:
            raise ValueError("track_id must be non-negative")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if x2 <= x1 or y2 <= y1:
            raise ValueError("xyxy must describe a positive-area box")


@dataclass(frozen=True, slots=True)
class ZoneDefinition:
    """Named image-space polygon used for tatame and pause-area events."""

    name: str
    points: tuple[tuple[int, int], ...]
    dwell_threshold_ms: int = 0

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("zone name is required")
        if len(self.points) < 3:
            raise ValueError("a polygon zone requires at least three points")
        if self.dwell_threshold_ms < 0:
            raise ValueError("dwell_threshold_ms must be non-negative")


def _load_supervision() -> Any:
    try:
        import supervision as sv
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Install the vision extra to use Supervision") from exc
    return sv


def detections_to_supervision(
    records: list[DetectionRecord],
    metadata: dict[str, Any] | None = None,
) -> Any:
    """Convert validated detections into ``sv.Detections``.

    Participant identifiers are pseudonymous application data. Supervision's
    ``tracker_id`` remains a temporary visual-track identifier and must never be
    treated as a clinical or legal identity by itself.
    """

    sv = _load_supervision()
    if not records:
        detections = sv.Detections.empty()
        detections.tracker_id = np.array([], dtype=np.int64)
        detections.data = {"participant_id": []}
    else:
        detections = sv.Detections(
            xyxy=np.asarray([record.xyxy for record in records], dtype=np.float32),
            confidence=np.asarray(
                [record.confidence for record in records], dtype=np.float32
            ),
            class_id=np.asarray([record.class_id for record in records], dtype=np.int64),
            tracker_id=np.asarray([record.track_id for record in records], dtype=np.int64),
            data={"participant_id": [record.participant_id for record in records]},
        )
    if metadata is not None and hasattr(detections, "metadata"):
        detections.metadata = dict(metadata)
    return detections


def wholebody_pose_to_supervision(
    pose: PersonWholeBodyPose,
    region: LandmarkRegion | None = None,
) -> Any:
    """Convert one whole-body estimate into ``sv.KeyPoints``.

    Keypoint coordinates are preserved in the coordinate system supplied by the
    pose backend. The caller is responsible for converting normalized coordinates
    to pixels before preview annotation.
    """

    sv = _load_supervision()
    points = pose.region(region) if region is not None else pose.keypoints
    if not points:
        return sv.KeyPoints.empty()
    xy = np.asarray([[[point.x, point.y] for point in points]], dtype=np.float32)
    confidence = np.asarray(
        [[point.confidence for point in points]], dtype=np.float32
    )
    return sv.KeyPoints(xy=xy, confidence=confidence)


def create_polygon_zone(definition: ZoneDefinition) -> Any:
    """Create a bottom-center anchored ``sv.PolygonZone``."""

    sv = _load_supervision()
    polygon = np.asarray(definition.points, dtype=np.int64)
    return sv.PolygonZone(polygon=polygon)


def tracked_ids_in_zone(zone: Any, detections: Any) -> set[int]:
    """Return temporary tracker IDs whose bottom-center anchor is in a zone."""

    tracker_ids = detections.tracker_id
    if tracker_ids is None:
        raise ValueError("tracked detections are required for zone membership")
    inside = zone.trigger(detections)
    if len(inside) != len(tracker_ids):
        raise RuntimeError("zone result length does not match tracker ids")
    return {
        int(track_id)
        for track_id, is_inside in zip(tracker_ids, inside, strict=True)
        if bool(is_inside)
    }


def memberships_for_zones(
    zones: dict[str, Any],
    detections: Any,
) -> dict[str, set[int]]:
    """Evaluate all named zones for one tracked-detection frame."""

    return {
        zone_name: tracked_ids_in_zone(zone, detections)
        for zone_name, zone in zones.items()
    }
