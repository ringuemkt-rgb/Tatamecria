"""Frame-source abstractions for webcams, files, and deterministic tests."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np


@dataclass(slots=True)
class CapturedFrame:
    index: int
    timestamp_ms: int
    image_bgr: np.ndarray


class FrameSource(Protocol):
    def frames(self) -> Iterator[CapturedFrame]: ...


class SyntheticFrameSource:
    """Generate plain frames without handling personal data."""

    def __init__(self, count: int = 30, width: int = 640, height: int = 480) -> None:
        self.count = count
        self.width = width
        self.height = height

    def frames(self) -> Iterator[CapturedFrame]:
        for index in range(self.count):
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            x = 50 + (index * 7) % max(1, self.width - 150)
            frame[100:300, x : x + 80] = 180
            yield CapturedFrame(index=index, timestamp_ms=index * 33, image_bgr=frame)


class OpenCVFrameSource:
    """Read a local camera or video while never persisting frames by itself."""

    def __init__(self, source: int | str | Path = 0, maximum_frames: int | None = None) -> None:
        self.source = str(source) if isinstance(source, Path) else source
        self.maximum_frames = maximum_frames

    def frames(self) -> Iterator[CapturedFrame]:
        try:
            import cv2
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Install the vision extra: pip install -e '.[vision]'") from exc

        capture = cv2.VideoCapture(self.source)
        if not capture.isOpened():
            raise RuntimeError(f"Could not open frame source: {self.source}")

        try:
            index = 0
            while self.maximum_frames is None or index < self.maximum_frames:
                ok, frame = capture.read()
                if not ok:
                    break
                timestamp_ms = int(capture.get(cv2.CAP_PROP_POS_MSEC))
                if timestamp_ms <= 0:
                    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
                    timestamp_ms = int(index / fps * 1000)
                yield CapturedFrame(index=index, timestamp_ms=timestamp_ms, image_bgr=frame)
                index += 1
        finally:
            capture.release()
