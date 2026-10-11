"""Descriptive image-plane metrics for one standardized, single-person motor task.

Pre-validation research only. Coordinates are not calibrated physical distances.
"""
from __future__ import annotations

from datetime import timedelta
from math import atan2, degrees, hypot, isfinite
from statistics import median

from neurojitsu.core.models import (
    IdentityStatus,
    MetricValue,
    PoseFrame,
    SessionPhase,
    SessionWindow,
)

# MediaPipe Pose landmark indices.
LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
LEFT_HIP, RIGHT_HIP = 23, 24
LEFT_KNEE, RIGHT_KNEE = 25, 26
LEFT_ANKLE, RIGHT_ANKLE = 27, 28


def _point(frame: PoseFrame, index: int) -> tuple[float, float] | None:
    if (
        frame.frame_width is None
        or frame.frame_height is None
        or len(frame.landmarks_xyzc) <= index
    ):
        return None
    x, y, _, confidence = frame.landmarks_xyzc[index]
    if not all(isfinite(n) for n in (x, y, confidence)) or confidence < 0.65:
        return None
    return x * frame.frame_width, y * frame.frame_height


def _midpoint(
    a: tuple[float, float] | None, b: tuple[float, float] | None
) -> tuple[float, float] | None:
    if a is None or b is None:
        return None
    return (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0


def _angle(
    a: tuple[float, float] | None,
    b: tuple[float, float] | None,
    c: tuple[float, float] | None,
) -> float | None:
    if a is None or b is None or c is None:
        return None
    ab = a[0] - b[0], a[1] - b[1]
    cb = c[0] - b[0], c[1] - b[1]
    den = hypot(*ab) * hypot(*cb)
    if den <= 1e-8:
        return None
    from math import acos, pi

    cosine = max(-1.0, min(1.0, (ab[0] * cb[0] + ab[1] * cb[1]) / den))
    return acos(cosine) * 180.0 / pi


def _summarize(
    name: str, values: list[float], unit: str, total_frames: int, identity_ok: bool
) -> MetricValue:
    usable = [v for v in values if isfinite(v)]
    confidence = len(usable) / max(1, total_frames)  # completeness, NOT accuracy
    valid = identity_ok and len(usable) >= 3 and confidence >= 0.70
    reason = None if valid else (
        "operator_identity_not_confirmed" if not identity_ok else "insufficient_valid_frames"
    )
    return MetricValue(
        name=name,
        value=float(median(usable)) if valid else None,
        unit=unit,
        confidence=confidence,
        valid=valid,
        reason_invalid=reason,
    )


def frames_to_windows(
    frames: list[PoseFrame],
    task_id: str,
    camera_id: str,
    calibration_id: str,
    backend_version: str,
    window_frames: int = 90,
) -> list[SessionWindow]:
    """Return time windows; no technique scoring and no diagnosis.

    All frames must belong to one participant/session and be timestamp-ordered.
    Identity must be confirmed by an operator; a pose tracker alone is insufficient.
    """
    if not frames:
        raise ValueError("At least one pose frame is required")
    if window_frames < 3:
        raise ValueError("window_frames must be >= 3")
    if not task_id.strip() or not camera_id.strip() or not calibration_id.strip():
        raise ValueError("task, camera and calibration identifiers are required")
    if not backend_version.strip():
        raise ValueError("backend_version is required")

    first = frames[0]
    if any(
        f.session_id != first.session_id or f.participant_id != first.participant_id
        for f in frames
    ):
        raise ValueError("Mixed participants or sessions are prohibited")
    if any(a.timestamp >= b.timestamp for a, b in zip(frames, frames[1:])):
        raise ValueError("Frame timestamps must be strictly increasing")

    windows: list[SessionWindow] = []
    for offset in range(0, len(frames), window_frames):
        chunk = frames[offset : offset + window_frames]
        identity_ok = all(f.identity_status is IdentityStatus.CONFIRMED for f in chunk)
        identity = IdentityStatus.CONFIRMED if identity_ok else IdentityStatus.UNCERTAIN
        left_angles: list[float] = []
        right_angles: list[float] = []
        trunk_angles: list[float] = []
        pelvis_points: list[tuple[float, float]] = []
        valid_frame_count = 0

        for frame in chunk:
            if len(frame.landmarks_xyzc) < 33:
                continue
            left = _angle(
                _point(frame, LEFT_HIP),
                _point(frame, LEFT_KNEE),
                _point(frame, LEFT_ANKLE),
            )
            right = _angle(
                _point(frame, RIGHT_HIP),
                _point(frame, RIGHT_KNEE),
                _point(frame, RIGHT_ANKLE),
            )
            shoulder = _midpoint(
                _point(frame, LEFT_SHOULDER), _point(frame, RIGHT_SHOULDER)
            )
            pelvis = _midpoint(_point(frame, LEFT_HIP), _point(frame, RIGHT_HIP))
            if left is not None:
                left_angles.append(left)
            if right is not None:
                right_angles.append(right)
            if shoulder is not None and pelvis is not None:
                dx, dy = shoulder[0] - pelvis[0], shoulder[1] - pelvis[1]
                if hypot(dx, dy) > 1e-8:
                    trunk_angles.append(degrees(atan2(abs(dx), abs(dy))))
                if frame.frame_width and frame.frame_height:
                    pelvis_points.append(
                        (pelvis[0] / frame.frame_width, pelvis[1] / frame.frame_height)
                    )
            if left is not None and right is not None:
                valid_frame_count += 1

        metrics = [
            _summarize("left_knee_angle", left_angles, "deg", len(chunk), identity_ok),
            _summarize("right_knee_angle", right_angles, "deg", len(chunk), identity_ok),
            _summarize("trunk_inclination_image", trunk_angles, "deg", len(chunk), identity_ok),
        ]
        # This is cumulative image-normalized displacement, NOT CoP or physical distance.
        path = [
            hypot(b[0] - a[0], b[1] - a[1])
            for a, b in zip(pelvis_points, pelvis_points[1:])
        ]
        path_valid = identity_ok and len(pelvis_points) >= 3 and (
            len(pelvis_points) / len(chunk) >= 0.70
        )
        metrics.append(
            MetricValue(
                name="pelvis_trajectory_image",
                value=sum(path) if path_valid else None,
                unit="normalized_image",
                confidence=len(pelvis_points) / len(chunk),
                valid=path_valid,
                reason_invalid=None if path_valid else (
                    "operator_identity_not_confirmed"
                    if not identity_ok else "insufficient_valid_frames"
                ),
            )
        )
        end = chunk[-1].timestamp + timedelta(milliseconds=1)
        windows.append(
            SessionWindow(
                session_id=first.session_id,
                participant_id=first.participant_id,
                timestamp_start=chunk[0].timestamp,
                timestamp_end=end,
                phase=SessionPhase.TECHNICAL_DRILLS,
                identity_status=identity,
                metrics=metrics,
                metadata={
                    "task_id": task_id,
                    "camera_id": camera_id,
                    "calibration_id": calibration_id,
                    "backend_version": backend_version,
                    "frames": len(chunk),
                    "frames_with_valid_knees": valid_frame_count,
                    "scientific_status": "pre_validation_research_only",
                },
            )
        )
    return windows
