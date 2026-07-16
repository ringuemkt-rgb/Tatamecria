"""Quality gates that prevent low-confidence data entering reports as fact."""

from __future__ import annotations

from statistics import fmean

from neurojitsu.core.models import DataUsability, IdentityStatus, QualitySummary, SessionWindow


class QualityAgent:
    """Assess data completeness and confidence using explicit thresholds."""

    def __init__(
        self,
        minimum_confidence: float = 0.65,
        maximum_missing_ratio: float = 0.20,
        maximum_identity_uncertain_seconds: float = 30.0,
    ) -> None:
        self.minimum_confidence = minimum_confidence
        self.maximum_missing_ratio = maximum_missing_ratio
        self.maximum_identity_uncertain_seconds = maximum_identity_uncertain_seconds

    def evaluate(self, windows: list[SessionWindow]) -> QualitySummary:
        if not windows:
            raise ValueError("At least one window is required")

        valid_flags: list[bool] = []
        confidence_values: list[float] = []
        identity_uncertain_seconds = 0.0
        limitations: list[str] = []

        for window in windows:
            duration = (window.timestamp_end - window.timestamp_start).total_seconds()
            if window.identity_status is IdentityStatus.UNCERTAIN:
                identity_uncertain_seconds += duration
            for metric in window.metrics:
                valid_flags.append(metric.valid)
                confidence_values.append(metric.confidence)

        valid_ratio = sum(valid_flags) / len(valid_flags) if valid_flags else 0.0
        mean_confidence = fmean(confidence_values) if confidence_values else 0.0
        missing_ratio = 1.0 - valid_ratio

        if mean_confidence < self.minimum_confidence:
            limitations.append("Mean metric confidence was below the configured threshold.")
        if missing_ratio > self.maximum_missing_ratio:
            limitations.append("The proportion of invalid or missing metrics was too high.")
        if identity_uncertain_seconds > self.maximum_identity_uncertain_seconds:
            limitations.append("Participant identity was uncertain for an excessive duration.")

        if limitations:
            overall = DataUsability.INVALID if len(limitations) >= 2 else DataUsability.EXPLORATORY
        else:
            overall = DataUsability.VALID

        first = windows[0]
        return QualitySummary(
            session_id=first.session_id,
            participant_id=first.participant_id,
            overall=overall,
            valid_window_ratio=valid_ratio,
            mean_confidence=mean_confidence,
            identity_uncertain_seconds=identity_uncertain_seconds,
            limitations=limitations,
        )
