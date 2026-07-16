from neurojitsu.agents.orchestrator import ReportOrchestrator
from neurojitsu.synthetic.generator import dataframe_to_windows, generate_session_dataframe


def test_agents_return_structured_outputs() -> None:
    windows = dataframe_to_windows(generate_session_dataframe(windows_per_phase=1))
    result = ReportOrchestrator().run(windows)
    assert "motor_agent" in result.agent_outputs
    assert "quality_agent" in result.agent_outputs
    assert result.payload.professional_review_required
