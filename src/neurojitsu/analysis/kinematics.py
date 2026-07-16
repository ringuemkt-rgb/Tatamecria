"""Transparent kinematic calculations from landmark coordinates."""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

Point2D = tuple[float, float]


def joint_angle(a: Point2D, b: Point2D, c: Point2D) -> float | None:
    """Return angle ABC in degrees, or ``None`` for degenerate vectors."""
    vector_ba = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    vector_bc = np.asarray(c, dtype=float) - np.asarray(b, dtype=float)
    denominator = np.linalg.norm(vector_ba) * np.linalg.norm(vector_bc)
    if denominator <= 1e-12:
        return None
    cosine = float(np.clip(np.dot(vector_ba, vector_bc) / denominator, -1.0, 1.0))
    return math.degrees(math.acos(cosine))


def symmetry_difference_percent(left: float, right: float) -> float | None:
    """Return absolute bilateral difference relative to their mean."""
    denominator = (abs(left) + abs(right)) / 2.0
    if denominator <= 1e-12:
        return None
    return abs(left - right) / denominator * 100.0


def path_length(points: Sequence[Point2D]) -> float:
    """Calculate normalized trajectory length."""
    if len(points) < 2:
        return 0.0
    array = np.asarray(points, dtype=float)
    return float(np.linalg.norm(np.diff(array, axis=0), axis=1).sum())


def normalized_jerk(positions: Sequence[Point2D], sampling_hz: float) -> float | None:
    """Calculate a dimensionless jerk proxy for exploratory movement fluency.

    The result must be validated for each task before clinical interpretation.
    """
    if sampling_hz <= 0:
        raise ValueError("sampling_hz must be positive")
    if len(positions) < 5:
        return None
    xy = np.asarray(positions, dtype=float)
    velocity = np.gradient(xy, axis=0) * sampling_hz
    acceleration = np.gradient(velocity, axis=0) * sampling_hz
    jerk = np.gradient(acceleration, axis=0) * sampling_hz
    duration = (len(xy) - 1) / sampling_hz
    distance = np.linalg.norm(xy[-1] - xy[0])
    if duration <= 0 or distance <= 1e-12:
        return None
    integrated_squared_jerk = np.sum(np.linalg.norm(jerk, axis=1) ** 2) / sampling_hz
    return float(integrated_squared_jerk * duration**5 / distance**2)
