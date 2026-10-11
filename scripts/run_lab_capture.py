"""Adult-only laboratory camera smoke test, with encrypted storage and informed consent."""
from __future__ import annotations

import argparse
import os
from datetime import UTC, datetime
from pathlib import Path

from neurojitsu.agents.orchestrator import ReportOrchestrator
from neurojitsu.analysis.camera_metrics import frames_to_windows
from neurojitsu.capture.source import OpenCVFrameSource
from neurojitsu.privacy.consent import AdultCaptureConsent
from neurojitsu.privacy.redactor import FaceRedactor
from neurojitsu.storage.database import Database
from neurojitsu.vision.mediapipe_pose import MediaPipePoseBackend
from neurojitsu.vision.pipeline import VisionPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Pre-validation adult-only research capture")
    parser.add_argument("--participant-id", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--camera-id", required=True)
    parser.add_argument("--calibration-id", required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--db-path", type=Path, default=Path("data/neurojitsu.db"))
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--max-frames", type=int, default=300)
    parser.add_argument("--adult-consent-confirmed", action="store_true")
    parser.add_argument("--single-adult-verified", action="store_true")
    args = parser.parse_args()
    if not (args.adult_consent_confirmed and args.single_adult_verified):
        parser.error("Recorded adult consent and operator supervision are required")
    if not 3 <= args.max_frames <= 3600:
        parser.error("max-frames must be between 3 and 3600")
    key = os.environ.get("NEUROJITSU_DB_KEY")
    if not key:
        parser.error("NEUROJITSU_DB_KEY required: real data must use SQLCipher")
    consent = AdultCaptureConsent(args.participant_id, True, True, True)
    backend = MediaPipePoseBackend(args.model_path, number_of_poses=1)
    try:
        frames = list(
            VisionPipeline(FaceRedactor(), backend).run(
                OpenCVFrameSource(args.camera_index, maximum_frames=args.max_frames),
                args.session_id, args.participant_id,
                started_at=datetime.now(UTC), adult_consent=consent,
                operator_identity_confirmed=args.single_adult_verified,
            )
        )
    finally:
        backend.close()
    if len(frames) < 3:
        raise RuntimeError("Insufficient frames; nothing stored")
    windows = frames_to_windows(
        frames, args.task_id, args.camera_id, args.calibration_id,
        f"mediapipe:{args.model_path.name}",
    )
    database = Database(args.db_path, key=key)
    database.register_participant(args.participant_id, synthetic=False)
    database.create_session(args.session_id, args.participant_id, frames[0].timestamp)
    database.store_windows(windows)
    report = ReportOrchestrator().run(windows)
    database.store_report(
        args.session_id, args.participant_id,
        report.payload.model_dump_json(indent=2), report.html,
    )
    database.set_session_state(args.session_id, "review", ended_at=datetime.now(UTC))
    print(f"Research capture saved: {args.session_id}; {len(windows)} windows")
    print("No raw video persisted; no diagnostic or clinical claims supported.")


if __name__ == "__main__":
    main()
