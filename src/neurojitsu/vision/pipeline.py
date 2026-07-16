"""Privacy-first frame pipeline."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

from neurojitsu.capture.source import FrameSource
from neurojitsu.core.models import IdentityStatus, PoseFrame
from neurojitsu.privacy.redactor import FaceRedactor
from neurojitsu.vision.base import PoseBackend


class VisionPipeline:
    """Redact, infer pose, and emit landmark-only records.

    The original frame is never returned or persisted by this class.
    """

    def __init__(self, redactor: FaceRedactor, pose_backend: PoseBackend) -> None:
        self.redactor = redactor
        self.pose_backend = pose_backend

    def run(
        self,
        source: FrameSource,
        session_id: str,
        participant_id: str,
        started_at: datetime | None = None,
    ) -> Iterator[PoseFrame]:
        origin = started_at or datetime.now(UTC)
        for captured in source.frames():
            redacted = self.redactor.redact(captured.image_bgr)
            landmarks = self.pose_backend.infer(redacted.redacted_bgr, captured.timestamp_ms)
            valid_ratio = (
                sum(1 for *_, confidence in landmarks if confidence >= 0.5) / len(landmarks)
                if landmarks
                else 0.0
            )
            yield PoseFrame(
                session_id=session_id,
                participant_id=participant_id,
                timestamp=origin + timedelta(milliseconds=captured.timestamp_ms),
                frame_index=captured.index,
                landmarks_xyzc=landmarks,
                valid_landmark_ratio=valid_ratio,
                tracking_confidence=valid_ratio,
                identity_status=IdentityStatus.CONFIRMED,
            )
