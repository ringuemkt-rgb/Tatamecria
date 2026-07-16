"""Quality gating for dense whole-body motion estimates."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MotionQualityInput:
    body_valid_ratio: float
    hand_valid_ratio: float
    foot_valid_ratio: float
    detector_confidence: float
    occlusion_ratio: float
    identity_confidence: float
    dropped_frame_ratio: float

    def __post_init__(self) -> None:
        for name, value in vars(self).items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class MotionQualityResult:
    score: float
    usable_for_body_kinematics: bool
    usable_for_fine_hand_analysis: bool
    usable_for_individual_report: bool
    limitations: tuple[str, ...]


def assess_motion_quality(data: MotionQualityInput) -> MotionQualityResult:
    """Compute a conservative quality score and use-specific gates."""

    visibility = (
        0.55 * data.body_valid_ratio
        + 0.20 * data.hand_valid_ratio
        + 0.10 * data.foot_valid_ratio
    )
    reliability = 0.15 * data.detector_confidence
    penalties = 0.45 * data.occlusion_ratio + 0.30 * data.dropped_frame_ratio
    score = max(0.0, min(1.0, visibility + reliability - penalties))

    limitations: list[str] = []
    if data.occlusion_ratio > 0.25:
        limitations.append("high_occlusion")
    if data.dropped_frame_ratio > 0.10:
        limitations.append("dropped_frames")
    if data.body_valid_ratio < 0.70:
        limitations.append("insufficient_body_landmarks")
    if data.hand_valid_ratio < 0.65:
        limitations.append("insufficient_hand_landmarks")
    if data.identity_confidence < 0.80:
        limitations.append("identity_assignment_uncertain")

    body_ok = score >= 0.60 and data.body_valid_ratio >= 0.70 and data.occlusion_ratio <= 0.35
    hand_ok = score >= 0.72 and data.hand_valid_ratio >= 0.75 and data.occlusion_ratio <= 0.20
    report_ok = body_ok and data.identity_confidence >= 0.80
    return MotionQualityResult(score, body_ok, hand_ok, report_ok, tuple(limitations))
