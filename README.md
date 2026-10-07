# NeuroJitsu Analytics

> **Research software — pre-validation. Not a medical device.**

NeuroJitsu Analytics is an open, local-first research platform for **motor-control and movement analysis in adapted Brazilian Jiu-Jitsu (BJJ) studies**. Its current purpose is to convert standardized motor-task recordings into transparent, auditable movement metrics while preserving data quality, privacy and human scientific oversight.

The project is designed to support research in **motor control, postural control, balance, biomechanics, motor learning and adapted physical activity**. It does **not** diagnose autism, infer emotion, predict crises, or make autonomous clinical decisions.

## Research focus

The academic core is intentionally narrow:

```text
standardized motor task
        ↓
video / pose landmarks
        ↓
quality gates
        ↓
transparent kinematic metrics
        ↓
comparison with reference laboratory measures
        ↓
longitudinal research use
```

Primary research questions include:

1. Are low-cost markerless metrics sufficiently reliable and valid for standardized motor tasks?
2. How robust are those metrics to camera position, occlusion and repeated measurement?
3. Can validated metrics complement conventional motor-control and postural-control outcomes in adapted BJJ research?
4. After technical validation and ethics approval, can the platform be used safely in studies involving autistic children?

## What is implemented

### Research core

- deterministic session/state contracts with Pydantic;
- synthetic reproducible datasets;
- joint angle;
- range of motion;
- trajectory length;
- jerk-based movement smoothness;
- bilateral difference;
- trunk inclination;
- explicit metric confidence, validity and invalidation reason;
- quality gates for missing frames, occlusion and landmark quality;
- local report generation (JSON + HTML);
- auditable storage and integrity checks;
- privacy-first capture path;
- local FastAPI API and Streamlit dashboard;
- CI for Python 3.11/3.12, Ruff, mypy, pytest, CLI verification and synthetic end-to-end smoke test.

### Markerless vision

- optional MediaPipe pose backend;
- Supervision adapters for detections, keypoints, zones and tracking metadata;
- single-participant workflows;
- experimental multi-person/grappling workflows with explicit uncertainty handling.

### Research extensions retained from earlier development

These modules are preserved because they may support future studies, but they are **not part of the current academic core**:

- HRV/RMSSD research utilities;
- temporal technique-phase models;
- whole-body hands/feet contracts;
- optional local narrative agents;
- experimental WiFi-CSI adapter;
- research hooks for heavier pose/action-recognition stacks.

See [RESEARCH_SCOPE.md](docs/RESEARCH_SCOPE.md) and [EXPERIMENTAL_EXTENSIONS.md](docs/EXPERIMENTAL_EXTENSIONS.md).

## Why this can be useful to a motor-neuroscience laboratory

The software is most useful when paired with laboratory reference methods rather than presented as a replacement for them.

A laboratory can use NeuroJitsu to test questions such as:

- agreement between markerless video angles and reference kinematics;
- agreement between video-derived postural features and force/pressure-platform measures;
- test–retest reliability;
- sensitivity to camera geometry and occlusion;
- validity of low-cost longitudinal monitoring;
- feasibility of movement analysis in grappling-specific tasks.

A potential alignment with the **Laboratory of Motor Neurosciences (NEMO/UEL)** is documented in [NEMO_RESEARCH_ALIGNMENT.md](docs/NEMO_RESEARCH_ALIGNMENT.md). That document describes scientific fit only and does **not** imply institutional affiliation, endorsement or supervision.

For a one-page academic summary, see [SUPERVISOR_BRIEF.md](docs/SUPERVISOR_BRIEF.md).

## Current scientific status

| Layer | Status |
|---|---|
| Software unit tests | Implemented |
| Synthetic end-to-end demo | Implemented |
| Transparent motor metrics | Implemented |
| Quality/invalidity metadata | Implemented |
| Local privacy-first pipeline | Implemented |
| Markerless pose integration | Experimental |
| Multi-person grappling analysis | Experimental |
| Criterion validity vs laboratory reference | **Not yet established** |
| Reliability in autistic children | **Not yet established** |
| Clinical validity | **Not established** |
| Diagnostic use | **Out of scope** |

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev,api,dashboard]"

neurojitsu verify
neurojitsu demo --output outputs/demo
```

Generated demonstration artifacts:

```text
outputs/demo/NJ-DEMO-001.json
outputs/demo/NJ-DEMO-001.html
outputs/demo/NJ-DEMO-001-agents.json
```

### Run API and dashboard

```bash
uvicorn neurojitsu.api.main:app --reload
streamlit run src/neurojitsu/dashboard/app.py
```

### Optional laboratory/vision dependencies

```bash
pip install -e ".[vision]"
pip install -e ".[tracking]"
pip install -e ".[physiology]"
```

## Test suite

```bash
pytest
ruff check src tests
mypy src/neurojitsu
neurojitsu verify
neurojitsu demo --output outputs/demo
```

The default research QA path does not require a camera, GPU, participant data or external model weights.

## Research documentation

Recommended reading order:

1. [Supervisor brief](docs/SUPERVISOR_BRIEF.md)
2. [Research scope](docs/RESEARCH_SCOPE.md)
3. [Research use cases](docs/RESEARCH_USE_CASES.md)
4. [Architecture](docs/ARCHITECTURE.md)
5. [Measurement dictionary](docs/MEASUREMENT_DICTIONARY.md)
6. [Laboratory validation protocol](docs/LAB_VALIDATION_PROTOCOL.md)
7. [Validation plan](docs/VALIDATION_PLAN.md)
8. [Known limitations](docs/KNOWN_LIMITATIONS.md)
9. [Reproducibility](docs/REPRODUCIBILITY.md)
10. [Ethics and safety](docs/ETHICS_AND_SAFETY.md)
11. [Data governance](docs/DATA_GOVERNANCE.md)
12. [Experimental extensions](docs/EXPERIMENTAL_EXTENSIONS.md)
13. [Development history](docs/DEVELOPMENT_HISTORY.md)
14. [Potential NEMO/UEL research alignment](docs/NEMO_RESEARCH_ALIGNMENT.md)
15. [Portuguese overview](docs/README_pt-BR.md)

## Ethical boundaries

NeuroJitsu must not be used to:

- diagnose autism or any health condition;
- infer emotion from faces;
- predict meltdowns or distress episodes;
- rank children by a hidden “normality” score;
- replace a clinician, researcher or coach;
- collect identifiable child data before ethics approval and institutional data-governance review.

The system is a **measurement research tool**, not an autonomous evaluator.

## Data protection

- raw video persistence is disabled by default;
- real-participant storage requires encrypted storage;
- identity mapping is separated from research data;
- direct facial recognition is prohibited;
- every research deployment must define consent/assent, retention, access and deletion rules before data collection.

## Repository history

This academic release consolidates the NeuroJitsu work previously developed inside the `Tatamecria` repository and narrows the public-facing scientific focus to motor-control research. Earlier experimental modules are retained but clearly labeled.

## Citation

See [CITATION.cff](CITATION.cff).

## License

MIT for original source code. External model weights, datasets and dependencies retain their own licenses.
