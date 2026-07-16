"""Deterministic report generation from validated structured metrics."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from statistics import fmean

from jinja2 import Environment, StrictUndefined

from neurojitsu.analysis.quality import QualityAgent
from neurojitsu.core.models import ReportPayload, SessionWindow

_TEMPLATE = """
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Relatório NeuroJitsu — {{ report.session_id }}</title>
<style>
body { font-family: Arial, sans-serif; margin: 2rem; line-height: 1.45; color: #e8e8e8; background: #111; }
h1, h2 { color: #fff; }
.card { background: #1d1d1d; border: 1px solid #333; padding: 1rem; margin: 1rem 0; border-radius: 8px; }
table { width: 100%; border-collapse: collapse; }
th, td { border: 1px solid #444; padding: .6rem; text-align: left; }
.notice { border-left: 5px solid #d9a441; padding-left: 1rem; }
</style>
</head>
<body>
<h1>Relatório Individual NeuroJitsu</h1>
<div class="card">
<p><strong>Participante:</strong> {{ report.participant_id }}</p>
<p><strong>Sessão:</strong> {{ report.session_id }}</p>
<p><strong>Qualidade geral:</strong> {{ report.quality.overall.value }}</p>
<p><strong>Janelas válidas:</strong> {{ '%.1f'|format(report.quality.valid_window_ratio * 100) }}%</p>
<p><strong>Confiança média:</strong> {{ '%.2f'|format(report.quality.mean_confidence) }}</p>
</div>
<h2>Métricas por fase</h2>
<table>
<tr><th>Fase</th><th>Participação</th><th>Movimento</th><th>Simetria</th><th>RMSSD</th></tr>
{% for phase, values in report.phase_metrics.items() %}
<tr>
<td>{{ phase }}</td>
<td>{{ values.participation_ratio }}</td>
<td>{{ values.movement_index }}</td>
<td>{{ values.symmetry_difference_percent }}</td>
<td>{{ values.rmssd_ms }}</td>
</tr>
{% endfor %}
</table>
<h2>Observações objetivas</h2>
<ul>{% for item in report.observations %}<li>{{ item }}</li>{% endfor %}</ul>
<h2>Limitações</h2>
<ul>{% for item in report.limitations %}<li>{{ item }}</li>{% endfor %}</ul>
<p class="notice"><strong>Revisão obrigatória:</strong> este documento descreve dados da sessão. Não é diagnóstico, não substitui avaliação profissional e deve ser revisado antes de qualquer uso clínico ou científico.</p>
</body>
</html>
"""


def _mean_metric(windows: list[SessionWindow], name: str) -> float | None:
    values = [
        metric.value
        for window in windows
        for metric in window.metrics
        if metric.name == name and metric.valid and metric.value is not None
    ]
    return float(fmean(values)) if values else None


class ReportGenerator:
    """Build JSON and HTML reports without allowing an LLM to invent measurements."""

    def __init__(self, quality_agent: QualityAgent | None = None) -> None:
        self.quality_agent = quality_agent or QualityAgent()
        self.environment = Environment(undefined=StrictUndefined, autoescape=True)
        self.template = self.environment.from_string(_TEMPLATE)

    def build_payload(self, windows: list[SessionWindow]) -> ReportPayload:
        quality = self.quality_agent.evaluate(windows)
        by_phase: dict[str, list[SessionWindow]] = {}
        for window in windows:
            by_phase.setdefault(window.phase.value, []).append(window)

        phase_metrics: dict[str, dict[str, float | int | str | None]] = {
            phase: {
                "participation_ratio": _mean_metric(group, "participation_ratio"),
                "movement_index": _mean_metric(group, "movement_index"),
                "symmetry_difference_percent": _mean_metric(group, "symmetry_difference_percent"),
                "rmssd_ms": _mean_metric(group, "rmssd_ms"),
            }
            for phase, group in by_phase.items()
        }
        observations = [
            f"Foram analisadas {len(windows)} janelas temporais estruturadas.",
            "As métricas foram agregadas apenas quando marcadas como válidas.",
            "A comparação principal deve ser longitudinal, usando a linha de base do próprio participante.",
        ]
        limitations = list(quality.limitations)
        if not limitations:
            limitations.append("Os valores ainda dependem de validação no ambiente e tarefa específicos.")
        first = windows[0]
        return ReportPayload(
            session_id=first.session_id,
            participant_id=first.participant_id,
            generated_at=datetime.now(UTC),
            quality=quality,
            phase_metrics=phase_metrics,
            observations=observations,
            limitations=limitations,
        )

    def render(self, windows: list[SessionWindow]) -> tuple[ReportPayload, str]:
        payload = self.build_payload(windows)
        return payload, self.template.render(report=payload)

    def write(self, windows: list[SessionWindow], output_directory: str | Path) -> tuple[Path, Path]:
        output = Path(output_directory)
        output.mkdir(parents=True, exist_ok=True)
        payload, html = self.render(windows)
        json_path = output / f"{payload.session_id}.json"
        html_path = output / f"{payload.session_id}.html"
        json_path.write_text(payload.model_dump_json(indent=2), encoding="utf-8")
        html_path.write_text(html, encoding="utf-8")
        return json_path, html_path
