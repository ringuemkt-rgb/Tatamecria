# Reproducibility

## Default reproducible mode

Use `synthetic` mode for software verification.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,api,dashboard]"
neurojitsu verify
neurojitsu demo --output outputs/demo
pytest
ruff check src tests
mypy src/neurojitsu
```

## Record for every experiment

- Git commit SHA;
- Python version;
- operating system;
- dependency lock/snapshot;
- configuration files;
- model/backend version;
- model checksum;
- random seed;
- camera/device metadata;
- analysis script version.

## Data policy

Public examples should use synthetic or fully de-identified demonstration data.

Real-participant data must not be committed to Git.

## Model weights

Do not redistribute external model weights unless their license explicitly allows it. Store approved model locations/checksums in the research environment rather than committing large binaries.

## Research outputs

A publication-ready workflow should export:

- analysis configuration;
- data dictionary;
- exclusion log;
- metric validity report;
- environment snapshot;
- analysis script;
- anonymized/synthetic reproducibility example where lawful and ethical.
