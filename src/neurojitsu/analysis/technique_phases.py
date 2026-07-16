"""Temporal phase smoothing for BJJ technique analysis."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TechniquePhase(StrEnum):
    SETUP = "setup"
    ENTRY = "entry"
    CONTROL = "control"
    TRANSITION = "transition"
    COMPLETION = "completion"
    RECOVERY = "recovery"
    UNCLASSIFIED = "unclassified"


@dataclass(frozen=True, slots=True)
class PhasePrediction:
    timestamp_ms: int
    probabilities: dict[TechniquePhase, float]

    def best(self) -> tuple[TechniquePhase, float]:
        if not self.probabilities:
            return TechniquePhase.UNCLASSIFIED, 0.0
        phase, confidence = max(self.probabilities.items(), key=lambda item: item[1])
        return phase, confidence


@dataclass(frozen=True, slots=True)
class StablePhase:
    phase: TechniquePhase
    confidence: float
    changed: bool


class PhaseHysteresis:
    """Require repeated evidence before changing the displayed phase."""

    def __init__(self, enter_threshold: float = 0.70, confirmations: int = 3) -> None:
        if not 0.0 < enter_threshold <= 1.0:
            raise ValueError("enter_threshold must be in (0, 1]")
        if confirmations < 1:
            raise ValueError("confirmations must be positive")
        self.enter_threshold = enter_threshold
        self.confirmations = confirmations
        self.current = TechniquePhase.UNCLASSIFIED
        self._candidate = TechniquePhase.UNCLASSIFIED
        self._candidate_count = 0

    def update(self, prediction: PhasePrediction) -> StablePhase:
        phase, confidence = prediction.best()
        if confidence < self.enter_threshold:
            self._candidate = TechniquePhase.UNCLASSIFIED
            self._candidate_count = 0
            return StablePhase(self.current, confidence, False)
        if phase == self.current:
            self._candidate = TechniquePhase.UNCLASSIFIED
            self._candidate_count = 0
            return StablePhase(self.current, confidence, False)
        if phase != self._candidate:
            self._candidate = phase
            self._candidate_count = 1
        else:
            self._candidate_count += 1
        if self._candidate_count < self.confirmations:
            return StablePhase(self.current, confidence, False)
        self.current = phase
        self._candidate = TechniquePhase.UNCLASSIFIED
        self._candidate_count = 0
        return StablePhase(self.current, confidence, True)
