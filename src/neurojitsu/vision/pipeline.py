"""Privacy-first frame pipeline."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

from neurojitsu.capture.source import FrameSource, SyntheticFrameSource
from neurojitsu.core.models import IdentityStatus, PoseFrame
from neurojitsu.privacy.consent import AdultCaptureConsent, AdultConsentGuard
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
        adult_consent: AdultCaptureConsent | None = None,
        operator_identity_confirmed: bool = False,
    ) -> Iterator[PoseFrame]:
        if not isinstance(source, SyntheticFrameSource):
            if adult_consent is None:
                raise PermissionError("Real capture requires documented adult research consent")
            AdultConsentGuard.require_capture_permission(adult_consent, participant_id)
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
                frame_width=int(captured.image_bgr.shape[1]),
                frame_height=int(captured.image_bgr.shape[0]),
                landmarks_xyzc=landmarks,
                valid_landmark_ratio=valid_ratio,
                tracking_confidence=valid_ratio,
                identity_status=(
                    IdentityStatus.CONFIRMED
                    if (isinstance(source, SyntheticFrameSource) or operator_identity_confirmed)
                    and valid_ratio >= 0.70
                    else IdentityStatus.UNCERTAIN
                ),
            )
