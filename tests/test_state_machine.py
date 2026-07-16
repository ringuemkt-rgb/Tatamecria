import pytest

from neurojitsu.core.state_machine import (
    InvalidStateTransition,
    SessionState,
    SessionStateMachine,
)


def test_valid_session_lifecycle() -> None:
    machine = SessionStateMachine()
    for target in [
        SessionState.READY,
        SessionState.CAPTURING,
        SessionState.PROCESSING,
        SessionState.REVIEW,
        SessionState.COMPLETED,
    ]:
        machine.transition(target)
    assert machine.state is SessionState.COMPLETED


def test_pause_can_resume_capture() -> None:
    machine = SessionStateMachine(SessionState.CAPTURING)
    machine.transition(SessionState.PAUSED)
    machine.transition(SessionState.CAPTURING)
    assert machine.state is SessionState.CAPTURING


def test_completed_session_cannot_restart() -> None:
    machine = SessionStateMachine(SessionState.COMPLETED)
    with pytest.raises(InvalidStateTransition):
        machine.transition(SessionState.CAPTURING)
