"""Fully synthetic demonstration: descriptive repeated camera-derived metrics."""
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from html import escape
from math import sin
from pathlib import Path

from neurojitsu.agents.orchestrator import ReportOrchestrator
from neurojitsu.analysis.camera_metrics import frames_to_windows
from neurojitsu.analysis.longitudinal import longitudinal_summary
from neurojitsu.core.models import IdentityStatus, PoseFrame
from neurojitsu.storage.database import Database


def synthetic_frames(session_id: str, week: int) -> list[PoseFrame]:
    start = datetime(2026, 10, 1, tzinfo=UTC) + timedelta(weeks=week)
    frames: list[PoseFrame] = []
    for index in range(90):
        lean = 0.075 - week * 0.003 + sin(index / 11.0) * 0.004
        pts = [(0.5, 0.5, 0.0, 0.98) for _ in range(33)]
        pts[11], pts[12] = (0.43 + lean, 0.29, 0, 0.98), (0.57 + lean, 0.29, 0, 0.98)
        pts[23], pts[24] = (0.44, 0.54, 0, 0.98), (0.56, 0.54, 0, 0.98)
        pts[25], pts[26] = (0.44, 0.72, 0, 0.98), (0.56, 0.72, 0, 0.98)
        pts[27], pts[28] = (0.43, 0.91, 0, 0.98), (0.57, 0.91, 0, 0.98)
        frames.append(
            PoseFrame(
                session_id=session_id, participant_id="A001",
                timestamp=start + timedelta(milliseconds=index * 33),
                frame_index=index, frame_width=640, frame_height=480,
                landmarks_xyzc=pts, valid_landmark_ratio=1.0,
                tracking_confidence=0.98, identity_status=IdentityStatus.CONFIRMED,
            )
        )
    return frames


def run_demo(output: Path) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    db = Database(output / "lab_demo.sqlite3")
    db.register_participant("A001", synthetic=True)
    for week in (0, 4, 8, 12):
        sid = f"NJ-ADULT-SYNTH-W{week:02d}"
        frames = synthetic_frames(sid, week)
        windows = frames_to_windows(
            frames, "standing-task", "synthetic-camera",
            "synthetic-fixed-calibration-v1", "synthetic-pose-v1",
        )
        db.create_session(sid, "A001", frames[0].timestamp)
        db.store_windows(windows)
        report = ReportOrchestrator().run(windows)
        db.store_report(sid, "A001", report.payload.model_dump_json(indent=2), report.html)
        db.set_session_state(sid, "review", ended_at=frames[-1].timestamp)
    summary = longitudinal_summary(db, "A001", "standing-task", "trunk_inclination_image")
    (output / "lab_longitudinal.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    rows = "".join(
        "<tr><td>{}</td><td>{:.2f}</td><td>{}</td></tr>".format(
            escape(str(r["session_id"])),
            r["value"] if r["value"] is not None else float("nan"),
            escape(str(r["delta_from_baseline"])),
        )
        for r in summary["sessions"]
    )
    html = (
        "<!doctype html><html lang='pt-BR'><meta charset='utf-8'>"
        "<title>NeuroJitsu — demonstração sintética</title>"
        "<style>body{font:16px system-ui;max-width:900px;margin:3rem auto;"
        "line-height:1.5}td,th{padding:.6rem;border:1px solid #888}"
        "table{border-collapse:collapse}</style>"
        "<h1>NeuroJitsu: laboratório — dados sintéticos</h1>"
        "<p><strong>NÃO são dados de crianças nem evidência clínica.</strong></p>"
        "<p>Quatro sessões artificiais; valores meramente descritivos.</p>"
        "<table><tr><th>Sessão</th><th>Ângulo do tronco (graus)"
        "</th><th>Diferença frente à primeira sessão</th></tr>"
        + rows + "</table><p>Não mede centro de pressão ou aprendizagem motora.</p></html>"
    )
    (output / "lab_longitudinal.html").write_text(html, encoding="utf-8")
    return summary


if __name__ == "__main__":
    result = run_demo(Path("outputs/lab-demo"))
    print("Synthetic laboratory demo: " + str(len(result["sessions"])) + " sessions")
