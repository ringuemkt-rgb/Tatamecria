from neurojitsu.reports.generator import ReportGenerator
from neurojitsu.synthetic.generator import dataframe_to_windows, generate_session_dataframe


def test_report_contains_review_warning(tmp_path) -> None:
    windows = dataframe_to_windows(generate_session_dataframe(windows_per_phase=1))
    json_path, html_path = ReportGenerator().write(windows, tmp_path)
    assert json_path.exists()
    assert html_path.exists()
    assert "Revisão obrigatória" in html_path.read_text(encoding="utf-8")


def test_report_has_all_phases() -> None:
    windows = dataframe_to_windows(generate_session_dataframe(windows_per_phase=1))
    payload = ReportGenerator().build_payload(windows)
    assert set(payload.phase_metrics) == {
        "warm_up",
        "technical_drills",
        "cooperative_games",
        "cool_down",
    }
