"""Pose backend interfaces and a deterministic implementation for tests."""

from __future__ import annotations

from typing import Protocol

import numpy as np


class PoseBackend(Protocol):
    def infer(self, frame_bgr: np.ndarray, timestamp_ms: int) -> list[tuple[float, float, float, float]]:
        """Return x, y, z, confidence landmarks."""
        ...


class SyntheticPoseBackend:
    """Return a stable 33-landmark skeleton for safe end-to-end tests."""

    def infer(self, frame_bgr: np.ndarray, timestamp_ms: int) -> list[tuple[float, float, float, float]]:
        del frame_bgr
        phase = (timestamp_ms % 2000) / 2000.0
        return [
            (
                0.25 + (index % 5) * 0.1,
                0.15 + (index // 5) * 0.08 + phase * 0.01,
                0.0,
                0.95,
            )
            for index in range(33)
        ]
