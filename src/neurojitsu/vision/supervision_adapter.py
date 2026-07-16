"""Optional conversion helpers for Roboflow Supervision."""

from __future__ import annotations

from typing import Any

import numpy as np


def keypoints_to_supervision(
    landmarks: list[tuple[float, float, float, float]],
    frame_width: int,
    frame_height: int,
) -> Any:
    """Convert normalized landmarks to ``sv.KeyPoints`` when Supervision is installed."""
    try:
        import supervision as sv
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Install the vision extra to use Supervision") from exc

    if not landmarks:
        return sv.KeyPoints.empty()

    xy = np.array([[[x * frame_width, y * frame_height] for x, y, _, _ in landmarks]])
    confidence = np.array([[confidence for _, _, _, confidence in landmarks]])
    return sv.KeyPoints(xy=xy, confidence=confidence)


def create_polygon_zone(points: list[tuple[int, int]]) -> Any:
    """Create a Supervision polygon zone for tatame or pause areas."""
    try:
        import supervision as sv
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install the vision extra to use Supervision") from exc
    polygon = np.asarray(points, dtype=np.int64)
    if polygon.shape[0] < 3:
        raise ValueError("A polygon zone requires at least three points")
    return sv.PolygonZone(polygon=polygon)
