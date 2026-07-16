from neurojitsu.analysis.technique_phases import (
    PhaseHysteresis,
    PhasePrediction,
    TechniquePhase,
)


def test_phase_requires_confirmations() -> None:
    smoother = PhaseHysteresis(enter_threshold=0.7, confirmations=2)
    prediction = PhasePrediction(0, {TechniquePhase.ENTRY: 0.9})
    first = smoother.update(prediction)
    second = smoother.update(prediction)
    assert first.phase == TechniquePhase.UNCLASSIFIED
    assert not first.changed
    assert second.phase == TechniquePhase.ENTRY
    assert second.changed
