"""Transparent biomechanical metrics derived from validated trajectories."""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, degrees

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class MetricEstimate:
    name: str
    value: float | None
    unit: str
    confidence: float
    valid: bool
    reason_invalid: str | None = None


def _as_point(point: FloatArray | list[float] | tuple[float, ...]) -> FloatArray:
    array = np.asarray(point, dtype=np.float64)
    if array.ndim != 1 or array.size not in {2, 3}:
        raise ValueError("point must contain two or three coordinates")
    return array


def joint_angle(
    proximal: FloatArray | list[float] | tuple[float, ...],
    vertex: FloatArray | list[float] | tuple[float, ...],
    distal: FloatArray | list[float] | tuple[float, ...],
    confidence: float = 1.0,
) -> MetricEstimate:
    """Compute the internal angle formed by three points."""

    a = _as_point(proximal) - _as_point(vertex)
    b = _as_point(distal) - _as_point(vertex)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-12:
        return MetricEstimate("joint_angle", None, "deg", 0.0, False, "degenerate vectors")
    cosine = float(np.clip(np.dot(a, b) / denom, -1.0, 1.0))
    return MetricEstimate("joint_angle", degrees(acos(cosine)), "deg", confidence, True)


def range_of_motion(values: FloatArray | list[float], confidence: float = 1.0) -> MetricEstimate:
    """Return max-min after removing non-finite samples."""

    array = np.asarray(values, dtype=np.float64)
    finite = array[np.isfinite(array)]
    if finite.size < 2:
        return MetricEstimate("range_of_motion", None, "deg", 0.0, False, "insufficient samples")
    return MetricEstimate(
        "range_of_motion", float(np.max(finite) - np.min(finite)), "deg", confidence, True
    )


def path_length(points: FloatArray | list[list[float]], confidence: float = 1.0) -> MetricEstimate:
    """Compute cumulative Euclidean trajectory length."""

    array = np.asarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[0] < 2:
        return MetricEstimate("path_length", None, "coordinate", 0.0, False, "insufficient samples")
    if not np.all(np.isfinite(array)):
        return MetricEstimate("path_length", None, "coordinate", 0.0, False, "non-finite samples")
    value = float(np.linalg.norm(np.diff(array, axis=0), axis=1).sum())
    return MetricEstimate("path_length", value, "coordinate", confidence, True)


def normalized_jerk(
    positions: FloatArray | list[list[float]], sample_rate_hz: float, confidence: float = 1.0
) -> MetricEstimate:
    """Dimensionless jerk proxy for movement smoothness.

    Lower values indicate smoother trajectories. This is an engineering metric,
    not a clinical diagnosis.
    """

    array = np.asarray(positions, dtype=np.float64)
    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive")
    if array.ndim != 2 or array.shape[0] < 5 or not np.all(np.isfinite(array)):
        return MetricEstimate("normalized_jerk", None, "a.u.", 0.0, False, "insufficient trajectory")
    dt = 1.0 / sample_rate_hz
    velocity = np.gradient(array, dt, axis=0)
    acceleration = np.gradient(velocity, dt, axis=0)
    jerk = np.gradient(acceleration, dt, axis=0)
    duration = (array.shape[0] - 1) * dt
    amplitude = float(np.linalg.norm(array[-1] - array[0]))
    if amplitude <= 1e-9:
        return MetricEstimate("normalized_jerk", None, "a.u.", 0.0, False, "near-zero displacement")
    integral = float(np.trapezoid(np.sum(jerk**2, axis=1), dx=dt))
    value = integral * duration**5 / amplitude**2
    return MetricEstimate("normalized_jerk", value, "a.u.", confidence, True)


def bilateral_difference(
    left: FloatArray | list[float], right: FloatArray | list[float], confidence: float = 1.0
) -> MetricEstimate:
    """Mean absolute bilateral difference normalized by pooled magnitude."""

    left_arr = np.asarray(left, dtype=np.float64)
    right_arr = np.asarray(right, dtype=np.float64)
    if left_arr.shape != right_arr.shape or left_arr.size == 0:
        return MetricEstimate("bilateral_difference", None, "%", 0.0, False, "shape mismatch")
    mask = np.isfinite(left_arr) & np.isfinite(right_arr)
    if mask.sum() < 2:
        return MetricEstimate("bilateral_difference", None, "%", 0.0, False, "insufficient paired samples")
    numerator = float(np.mean(np.abs(left_arr[mask] - right_arr[mask])))
    denominator = float(np.mean((np.abs(left_arr[mask]) + np.abs(right_arr[mask])) / 2.0))
    if denominator <= 1e-12:
        return MetricEstimate("bilateral_difference", 0.0, "%", confidence, True)
    return MetricEstimate("bilateral_difference", 100.0 * numerator / denominator, "%", confidence, True)


def trunk_inclination(
    shoulder_midpoint: FloatArray | list[float] | tuple[float, ...],
    hip_midpoint: FloatArray | list[float] | tuple[float, ...],
    confidence: float = 1.0,
) -> MetricEstimate:
    """Angle of the trunk axis relative to the image or world vertical."""

    shoulder = _as_point(shoulder_midpoint)
    hip = _as_point(hip_midpoint)
    axis = shoulder - hip
    vertical = np.zeros_like(axis)
    vertical[1] = -1.0
    denom = float(np.linalg.norm(axis))
    if denom <= 1e-12:
        return MetricEstimate("trunk_inclination", None, "deg", 0.0, False, "degenerate trunk axis")
    cosine = float(np.clip(np.dot(axis, vertical) / denom, -1.0, 1.0))
    return MetricEstimate("trunk_inclination", degrees(acos(cosine)), "deg", confidence, True)
