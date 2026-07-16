"""Face redaction performed before preview or downstream image analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(slots=True)
class RedactionResult:
    redacted_bgr: np.ndarray
    face_count: int
    redaction_applied: bool


class FaceRedactor:
    """OpenCV cascade-based redactor for the MVP.

    Research deployments should benchmark a stronger detector in the target room.
    This class never writes images to disk.
    """

    def __init__(self, blur_kernel: int = 99) -> None:
        if blur_kernel < 3:
            raise ValueError("blur_kernel must be at least 3")
        self.blur_kernel = blur_kernel if blur_kernel % 2 == 1 else blur_kernel + 1
        self._cascade: Any | None = None

    def _load(self) -> Any:
        try:
            import cv2
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("OpenCV is required for face redaction") from exc
        if self._cascade is None:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            cascade = cv2.CascadeClassifier(cascade_path)
            if cascade.empty():
                raise RuntimeError("OpenCV face cascade could not be loaded")
            self._cascade = cascade
        return cv2

    def redact(self, frame_bgr: np.ndarray) -> RedactionResult:
        cv2 = self._load()
        if frame_bgr.ndim != 3 or frame_bgr.shape[2] != 3:
            raise ValueError("Expected a BGR image with shape HxWx3")

        redacted = frame_bgr.copy()
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        assert self._cascade is not None
        faces = self._cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
        )
        for x, y, width, height in faces:
            roi = redacted[y : y + height, x : x + width]
            redacted[y : y + height, x : x + width] = cv2.GaussianBlur(
                roi,
                (self.blur_kernel, self.blur_kernel),
                sigmaX=30,
                sigmaY=30,
            )
        return RedactionResult(
            redacted_bgr=redacted,
            face_count=len(faces),
            redaction_applied=bool(len(faces)),
        )
