"""Collaborative analytic agents over structured data."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean
from typing import Protocol

from neurojitsu.analysis.quality import QualityAgent
from neurojitsu.core.models import ReportPayload, SessionWindow
from neurojitsu.reports.generator import ReportGenerator


class AnalyticAgent(Protocol):
    name: str

    def analyze(self, windows: list[SessionWindow]) -> dict[str, object]: ...


@dataclass(slots=True)
class MotorAgent:
    name: str = "motor_agent"

    def analyze(self, windows: list[SessionWindow]) -> dict[str, object]:
        values = [
            metric.value
            for window in windows
            for metric in window.metrics
            if metric.name == "movement_index" and metric.valid and metric.value is not None
        ]
        return {"mean_movement_index": fmean(values) if values else None, "window_count": len(windows)}


@dataclass(slots=True)
class ParticipationAgent:
    name: str = "participation_agent"

    def analyze(self, windows: list[SessionWindow]) -> dict[str, object]:
        values = [
            metric.value
            for window in windows
            for metric in window.metrics
            if metric.name == "participation_ratio" and metric.valid and metric.value is not None
        ]
        return {"mean_participation_ratio": fmean(values) if values else None}


@dataclass(slots=True)
class AgentRunResult:
    payload: ReportPayload
    agent_outputs: dict[str, dict[str, object]]
    html: str


class ReportOrchestrator:
    """Manager that combines specialist outputs without free-form clinical inference."""

    def __init__(self) -> None:
        self.quality_agent = QualityAgent()
        self.agents: list[AnalyticAgent] = [MotorAgent(), ParticipationAgent()]
        self.report_generator = ReportGenerator(self.quality_agent)

    def run(self, windows: list[SessionWindow]) -> AgentRunResult:
        if not windows:
            raise ValueError("Cannot run agents without session windows")
        outputs = {agent.name: agent.analyze(windows) for agent in self.agents}
        payload, html = self.report_generator.render(windows)
        outputs["quality_agent"] = self.quality_agent.evaluate(windows).model_dump(mode="json")
        return AgentRunResult(payload=payload, agent_outputs=outputs, html=html)
