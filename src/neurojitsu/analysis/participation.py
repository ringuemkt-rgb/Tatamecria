"""Participation metrics based on observable events."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParticipationEvent:
    event_type: str
    duration_seconds: float = 0.0


def participation_summary(events: Iterable[ParticipationEvent], session_seconds: float) -> dict[str, float | int]:
    """Summarize observable participation without inferring motivation."""
    if session_seconds <= 0:
        raise ValueError("session_seconds must be positive")
    event_list = list(events)
    counts = Counter(event.event_type for event in event_list)
    active_seconds = sum(
        event.duration_seconds
        for event in event_list
        if event.event_type in {"active", "technical_drill", "cooperative_game"}
    )
    pause_seconds = sum(
        event.duration_seconds for event in event_list if event.event_type == "sensory_pause"
    )
    return {
        "active_participation_ratio": min(active_seconds / session_seconds, 1.0),
        "pause_ratio": min(pause_seconds / session_seconds, 1.0),
        "task_attempts": counts["task_attempt"],
        "task_completions": counts["task_completion"],
        "instructor_assistance_events": counts["instructor_assistance"],
        "voluntary_pauses": counts["sensory_pause"],
    }
