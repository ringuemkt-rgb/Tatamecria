"""Predictable session state transitions."""

from __future__ import annotations

from enum import StrEnum


class SessionState(StrEnum):
    CREATED = "created"
    READY = "ready"
    CAPTURING = "capturing"
    PAUSED = "paused"
    PROCESSING = "processing"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"


_ALLOWED: dict[SessionState, set[SessionState]] = {
    SessionState.CREATED: {SessionState.READY, SessionState.FAILED},
    SessionState.READY: {SessionState.CAPTURING, SessionState.FAILED},
    SessionState.CAPTURING: {
        SessionState.PAUSED,
        SessionState.PROCESSING,
        SessionState.FAILED,
    },
    SessionState.PAUSED: {
        SessionState.CAPTURING,
        SessionState.PROCESSING,
        SessionState.FAILED,
    },
    SessionState.PROCESSING: {SessionState.REVIEW, SessionState.FAILED},
    SessionState.REVIEW: {SessionState.COMPLETED, SessionState.FAILED},
    SessionState.COMPLETED: set(),
    SessionState.FAILED: set(),
}


class InvalidStateTransition(ValueError):
    """Raised when a workflow attempts an impossible state transition."""


class SessionStateMachine:
    """Small explicit state machine used by API and capture workers."""

    def __init__(self, state: SessionState = SessionState.CREATED) -> None:
        self.state = state

    def transition(self, target: SessionState) -> SessionState:
        if target not in _ALLOWED[self.state]:
            raise InvalidStateTransition(f"Cannot transition from {self.state} to {target}")
        self.state = target
        return self.state
