from datetime import UTC, datetime

import numpy as np
import pytest

from neurojitsu.capture.source import CapturedFrame
from neurojitsu.privacy.consent import AdultCaptureConsent
from neurojitsu.privacy.redactor import RedactionResult
from neurojitsu.vision.pipeline import VisionPipeline


class RealSource:
    def frames(self):
        yield CapturedFrame(0, 0, np.zeros((64, 64, 3), dtype=np.uint8))


class FakeRedactor:
    def redact(self, image):
        return RedactionResult(image, 0, False)


class FakeBackend:
    def infer(self, frame_bgr, timestamp_ms):
        return [(0.5, 0.5, 0.0, 0.98)] * 33


def test_real_capture_requires_consent() -> None:
    pipeline = VisionPipeline(FakeRedactor(), FakeBackend())
    with pytest.raises(PermissionError):
        list(pipeline.run(RealSource(), "LAB-001", "A001"))


def test_no_child_capture_and_identity_not_automatic() -> None:
    pipeline = VisionPipeline(FakeRedactor(), FakeBackend())
    with pytest.raises(PermissionError):
        list(pipeline.run(RealSource(),"LAB-001","A001",
             adult_consent=AdultCaptureConsent("A001",False,True,True)))
    result = list(pipeline.run(
        RealSource(),"LAB-001","A001",started_at=datetime(2026,10,1,tzinfo=UTC),
        adult_consent=AdultCaptureConsent("A001",True,True,True)))
    assert result[0].identity_status.value == "uncertain"
    confirmed = list(pipeline.run(
        RealSource(),"LAB-001","A001",
        adult_consent=AdultCaptureConsent("A001",True,True,True),
        operator_identity_confirmed=True))
    assert confirmed[0].identity_status.value == "confirmed"
