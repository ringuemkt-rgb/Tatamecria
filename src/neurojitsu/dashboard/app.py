"""Neuroinclusive Streamlit dashboard."""

from __future__ import annotations

import json

import streamlit as st

from neurojitsu.analysis.longitudinal import longitudinal_summary
from neurojitsu.settings import load_settings
from neurojitsu.storage.database import Database


def _format(value: object) -> str:
    if value is None:
        return "—"
    return f"{float(str(value)):.2f}"


def _format_ratio(value: object) -> str:
    if value is None:
        return "—"
    return f"{float(str(value)) * 100:.1f}%"


st.set_page_config(
    page_title="NeuroJitsu Analytics",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
.stApp { background: #101010; color: #f2f2f2; }
[data-testid="stMetric"] { background: #1b1b1b; border: 1px solid #343434; padding: 1rem; }
button { min-height: 3rem; }
</style>
""",
    unsafe_allow_html=True,
)

settings = load_settings()
database = Database(
    settings.db_path,
    key=settings.db_key,
    allow_unencrypted_synthetic_only=settings.allow_unencrypted_synthetic_only,
)

st.title("NeuroJitsu Analytics")
st.caption("Fluxo previsível: Sessão → Métricas → Pausa → Relatório → Revisão")

sessions = database.list_sessions()
if not sessions:
    st.info("Nenhuma sessão registrada. Execute `neurojitsu demo --output outputs/demo`.")
    st.stop()

session_ids = [str(item["session_id"]) for item in sessions]
selected = st.selectbox("Sessão", session_ids)
report = database.get_report(selected)

if report is None:
    st.warning("A sessão ainda não possui relatório.")
    st.stop()
assert report is not None

payload = json.loads(str(report["report_json"]))
phase_metrics = payload.get("phase_metrics", {})
phase_names = list(phase_metrics)
latest_phase = phase_names[-1] if phase_names else None
latest = phase_metrics.get(latest_phase, {}) if latest_phase else {}

column1, column2, column3, column4 = st.columns(4)
column1.metric("Simetria (%)", _format(latest.get("symmetry_difference_percent")))
column2.metric("Movimento", _format(latest.get("movement_index")))
column3.metric("RMSSD (ms)", _format(latest.get("rmssd_ms")))
column4.metric("Participação", _format_ratio(latest.get("participation_ratio")))

if st.button("Registrar pausa sensorial", type="primary", use_container_width=True):
    database.audit(
        "researcher",
        "sensory_pause.record",
        "session",
        selected,
        {"source": "dashboard"},
    )
    st.success("Pausa registrada. Os dados anteriores permanecem válidos.")

st.subheader("Qualidade dos dados")
st.json(payload.get("quality", {}), expanded=False)

st.subheader("Métricas por fase")
st.dataframe(
    [dict(phase=phase, **values) for phase, values in phase_metrics.items()],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Limitações")
for limitation in payload.get("limitations", []):
    st.write(f"• {limitation}")

st.warning("Relatório descritivo. Revisão profissional obrigatória antes de uso científico ou clínico.")


st.subheader("Série temporal de uma tarefa padronizada")
windows = database.load_windows(selected)
task_id = str(windows[0].metadata.get("task_id", "")) if windows else ""
if not task_id:
    st.info("Nenhuma tarefa de captura padronizada registrada nesta sessão.")
else:
    choices = sorted({m.name for w in windows for m in w.metrics if m.valid})
    if choices:
        metric_name = st.selectbox("Métrica exploratória", choices)
        summary = longitudinal_summary(
            database, str(windows[0].participant_id), task_id, metric_name
        )
        compatible = [
            {
                "date": str(r["timestamp"])[:10],
                "value": r["value"],
                "session": r["session_id"],
            }
            for r in summary["sessions"]
            if r["comparable_to_baseline"] and r["value"] is not None
        ]
        if len(compatible) > 1:
            st.line_chart(compatible, x="date", y="value")
        st.dataframe(compatible, hide_index=True, use_container_width=True)
        st.caption(summary["notice"])
        st.warning(
            "Variáveis exploratórias pré-validação. Não medem autismo, desenvolvimento "
            "clínico, eficácia de tratamento nem centro de pressão."
        )
    else:
        st.info("Nenhuma métrica válida nesta sessão.")
