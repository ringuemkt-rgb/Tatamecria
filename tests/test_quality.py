from neurojitsu.analysis.quality import QualityAgent
from neurojitsu.core.models import DataUsability
from neurojitsu.synthetic.generator import dataframe_to_windows, generate_session_dataframe


def test_synthetic_session_is_valid() -> None:
    windows = dataframe_to_windows(generate_session_dataframe(windows_per_phase=2))
    result = QualityAgent().evaluate(windows)
    assert result.overall is DataUsability.VALID
    assert result.valid_window_ratio == 1.0


def test_empty_windows_are_rejected() -> None:
    try:
        QualityAgent().evaluate([])
    except ValueError as exc:
        assert "At least one" in str(exc)
    else:
        raise AssertionError("Expected an error")
