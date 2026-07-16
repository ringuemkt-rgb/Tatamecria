"""Contracts for whole-body, hand, foot, and face landmark backends."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class LandmarkRegion(StrEnum):
    BODY = "body"
    LEFT_HAND = "left_hand"
    RIGHT_HAND = "right_hand"
    FACE = "face"
    LEFT_FOOT = "left_foot"
    RIGHT_FOOT = "right_foot"


@dataclass(frozen=True, slots=True)
class Keypoint2D:
    """One image-space keypoint with normalized confidence."""

    name: str
    region: LandmarkRegion
    x: float
    y: float
    confidence: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class PersonWholeBodyPose:
    """Whole-body estimate for one temporary visual track."""

    track_id: int
    keypoints: tuple[Keypoint2D, ...]
    detector_confidence: float
    occlusion_ratio: float

    def __post_init__(self) -> None:
        if self.track_id < 0:
            raise ValueError("track_id must be non-negative")
        if not 0.0 <= self.detector_confidence <= 1.0:
            raise ValueError("detector_confidence must be between 0 and 1")
        if not 0.0 <= self.occlusion_ratio <= 1.0:
            raise ValueError("occlusion_ratio must be between 0 and 1")

    def region(self, region: LandmarkRegion) -> tuple[Keypoint2D, ...]:
        return tuple(point for point in self.keypoints if point.region == region)

    def valid_ratio(self, threshold: float = 0.5) -> float:
        if not self.keypoints:
            return 0.0
        valid = sum(point.confidence >= threshold for point in self.keypoints)
        return valid / len(self.keypoints)


class WholeBodyPoseBackend(Protocol):
    """Interface implemented by RTMW/RTMO, MediaPipe, or remote services."""

    backend_name: str
    schema_name: str

    def infer(self, image_bgr: object, timestamp_ms: int) -> Sequence[PersonWholeBodyPose]:
        """Return temporary track-level estimates without resolving identity."""
        ...
