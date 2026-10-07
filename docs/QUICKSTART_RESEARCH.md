# Quick Research Workflow

## 1. Verify the software

```bash
pip install -e ".[dev,api,dashboard]"
neurojitsu verify
pytest
```

## 2. Run synthetic demonstration

```bash
neurojitsu demo --output outputs/demo
```

Inspect the generated JSON/HTML and confirm that no personal data are required.

## 3. Select one laboratory question

Examples:

- knee-angle agreement during a standardized squat;
- trunk-inclination agreement during a balance task;
- test–retest reliability across two days.

Do not begin with a full BJJ intervention.

## 4. Freeze the protocol

Pre-specify:

- task;
- reference method;
- camera geometry;
- metric;
- invalidation rule;
- statistical analysis.

## 5. Adult validation first

Collect consenting adult data only after local research/ethics requirements are satisfied.

## 6. Add grappling complexity

Only after simple-task validation, study occlusion and two-person interactions.

## 7. Child research last

Use only metrics that survived prior validation and only after formal ethics approval.
