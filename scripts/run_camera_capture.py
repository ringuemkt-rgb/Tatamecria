"""Local camera smoke test. No image files are written."""

from __future__ import annotations

import os
from itertools import islice

from neurojitsu.capture.source import OpenCVFrameSource
from neurojitsu.privacy.redactor import FaceRedactor
from neurojitsu.vision.mediapipe_pose import MediaPipePoseBackend
from neurojitsu.vision.pipeline import VisionPipeline


def main() -> None:
    model_path = os.environ.get("NEUROJITSU_POSE_MODEL_PATH")
    if not model_path:
        raise RuntimeError("Set NEUROJITSU_POSE_MODEL_PATH to an official .task model")
    pipeline = VisionPipeline(FaceRedactor(), MediaPipePoseBackend(model_path))
    source = OpenCVFrameSource(0, maximum_frames=300)
    for pose_frame in islice(pipeline.run(source, "NJ-CAMERA-SMOKE", "A001"), 300):
        print(
            pose_frame.frame_index,
            round(pose_frame.valid_landmark_ratio, 3),
            len(pose_frame.landmarks_xyzc),
        )


if __name__ == "__main__":
    main()
