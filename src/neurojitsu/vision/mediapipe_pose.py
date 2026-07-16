"""MediaPipe Tasks pose backend.

The model asset is intentionally external because model files must be versioned,
checksummed, and reviewed independently from application code.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


class MediaPipePoseBackend:
    """Run MediaPipe Pose Landmarker on redacted frames only."""

    def __init__(self, model_path: str | Path, number_of_poses: int = 1) -> None:
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Pose model not found: {model_path}")
        try:
            import mediapipe as mp
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Install the vision extra to use MediaPipe") from exc

        base_options = mp.tasks.BaseOptions(model_asset_path=str(model_path))
        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_poses=number_of_poses,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._mp = mp
        self._landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)

    def infer(self, frame_bgr: np.ndarray, timestamp_ms: int) -> list[tuple[float, float, float, float]]:
        rgb = frame_bgr[:, :, ::-1]
        image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb)
        result = self._landmarker.detect_for_video(image, timestamp_ms)
        if not result.pose_landmarks:
            return []
        first_pose = result.pose_landmarks[0]
        return [
            (float(point.x), float(point.y), float(point.z), float(point.visibility))
            for point in first_pose
        ]

    def close(self) -> None:
        self._landmarker.close()
