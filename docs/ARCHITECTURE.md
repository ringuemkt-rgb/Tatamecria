# Architecture

## Academic design principles

1. **Measurement before prediction.** The research core computes transparent motor variables rather than hidden behavioral scores.
2. **Deterministic core.** Capture contracts, quality checks, metrics, storage and reports do not depend on an LLM.
3. **Quality is part of the result.** Every metric carries confidence, validity and a reason when invalid.
4. **Reference-laboratory validation first.** Markerless outputs must be compared with reference methods before child-study interpretation.
5. **Privacy before analysis.** Direct identifiers and raw video are not part of the default research dataset.
6. **Human scientific oversight.** The platform does not autonomously diagnose, classify clinical normality or recommend treatment.
7. **Extensions fail safely.** Experimental modules may be unavailable without breaking the motor-analysis core.

## Core research flow

```text
standardized task
      ↓
volatile frame / synthetic landmarks
      ↓
privacy layer
      ↓
pose backend
      ↓
landmark quality + occlusion checks
      ↓
transparent motor metrics
      ↓
metric validity metadata
      ↓
pseudonymized storage
      ↓
deterministic research report
```

## Software layers

```text
┌─────────────────────────────────────────────────────────────┐
│ Interfaces: CLI | FastAPI | Streamlit                      │
├─────────────────────────────────────────────────────────────┤
│ Reports: deterministic JSON/HTML + human review            │
├─────────────────────────────────────────────────────────────┤
│ Research analysis: kinematics | motion quality | phases    │
├─────────────────────────────────────────────────────────────┤
│ Biomechanics: angle | ROM | path | jerk | symmetry | trunk │
├─────────────────────────────────────────────────────────────┤
│ Quality: confidence | missingness | occlusion | validity   │
├─────────────────────────────────────────────────────────────┤
│ Vision: backend abstraction | MediaPipe | Supervision      │
├─────────────────────────────────────────────────────────────┤
│ Contracts: Pydantic | state machine | timestamps           │
├─────────────────────────────────────────────────────────────┤
│ Governance: consent | encrypted storage | audit trail      │
└─────────────────────────────────────────────────────────────┘
```

## Research extensions

The repository also retains physiology, temporal technique-phase, whole-body and WiFi-CSI modules from earlier development. They are isolated from the default scientific core and should not be interpreted as validated endpoints.

## Modes

### `synthetic`

Default and CI-safe. No participant data, camera, GPU or external model is required.

### `single_participant_camera`

Research validation mode for one consenting adult, after local approval and protocol review.

### `multi_person_research`

Experimental two-person workflow for occlusion and tracking studies. Identity uncertainty must be surfaced; automatic re-identification is not allowed.

### Experimental extensions

HRV, WiFi-CSI, action recognition and language-model narration remain research extensions, not required components of the motor-control core.
