"""FastAPI surface for local research workflows."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from neurojitsu.core.models import FeedbackRecord
from neurojitsu.settings import load_settings
from neurojitsu.storage.database import Database

settings = load_settings()
database = Database(
    settings.db_path,
    key=settings.db_key,
    allow_unencrypted_synthetic_only=settings.allow_unencrypted_synthetic_only,
)

app = FastAPI(
    title="NeuroJitsu Analytics API",
    version="0.1.0",
    description="Local-only research API. Not a diagnostic medical device.",
)


class PauseRequest(BaseModel):
    participant_id: str
    reason: str = "voluntary_sensory_pause"


class FeedbackRequest(BaseModel):
    participant_id: str
    engagement: str
    sensory_overload: str
    notes: str | None = None


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "database_encrypted": database.encrypted,
        "mode": settings.runtime.get("mode", "unknown"),
        "time": datetime.now(UTC).isoformat(),
    }


@app.get("/sessions")
def list_sessions() -> list[dict[str, object]]:
    return database.list_sessions()


@app.post("/sessions/{session_id}/pause")
def record_pause(session_id: str, request: PauseRequest) -> dict[str, str]:
    sessions = {row["session_id"]: row for row in database.list_sessions()}
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    database.audit(
        "researcher",
        "sensory_pause.record",
        "session",
        session_id,
        {"participant_id": request.participant_id, "reason": request.reason},
    )
    return {"status": "recorded", "session_id": session_id}


@app.post("/sessions/{session_id}/feedback")
def store_feedback(session_id: str, request: FeedbackRequest) -> dict[str, str]:
    try:
        feedback = FeedbackRecord(
            session_id=session_id,
            participant_id=request.participant_id,
            engagement=request.engagement,
            sensory_overload=request.sensory_overload,
            recorded_at=datetime.now(UTC),
            notes=request.notes,
        )
        database.store_feedback(feedback)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "stored", "session_id": session_id}


@app.get("/reports/{session_id}")
def get_report(session_id: str) -> dict[str, object]:
    report = database.get_report(session_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return {str(key): value for key, value in report.items()}
