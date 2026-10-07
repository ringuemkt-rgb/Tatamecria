# Validation Plan

NeuroJitsu is deliberately labeled **pre-validation**. Software correctness does not equal biomechanical or clinical validity.

## Phase 0 — Synthetic software verification

Objectives:

- verify deterministic metric calculations;
- verify validity flags and failure reasons;
- verify database transactions and audit trail;
- verify report reproducibility;
- run without camera, GPU or participant data.

Acceptance evidence:

- passing unit tests;
- passing static checks;
- reproducible demo artifacts from a fixed seed.

## Phase 1 — Single-adult bench validation

Population: consenting healthy adults.

Tasks: simple standardized movements selected with the host laboratory.

Compare:

- video-derived joint angles vs manual/reference kinematics;
- repeated trials across camera distances and angles;
- different lighting conditions;
- day-to-day test–retest reliability.

Candidate analyses:

- ICC with confidence intervals;
- Bland–Altman bias and limits of agreement;
- MAE/RMSE where appropriate;
- SEM and MDC where appropriate;
- missing/invalid-window rate.

Thresholds must be pre-specified with the supervising laboratory/statistician.

## Phase 2 — Postural-control validation

Use tasks for which a reference laboratory can provide force/pressure-platform or validated postural-control outcomes.

Research questions:

- which video features correlate with reference balance variables?
- which are reliable across repeated sessions?
- which should be discarded because of poor agreement?

No video metric should be promoted to a clinical endpoint solely because it correlates once with a reference measure.

## Phase 3 — Two-adult grappling feasibility

Objectives:

- quantify occlusion;
- quantify track/identity uncertainty;
- test basic standing and ground positions;
- compare single- vs multi-camera completeness;
- define invalidation rules for unusable windows.

This phase is technical feasibility, not clinical validation.

## Phase 4 — Prospective adult research use

Only metrics that passed previous validation remain eligible.

Objectives:

- longitudinal repeatability;
- sensitivity to known task changes;
- protocol adherence;
- data completeness.

## Phase 5 — Child study after ethics approval

Requirements:

- approved research protocol;
- guardian consent and child assent when applicable;
- approved retention/deletion plan;
- age-appropriate procedures;
- independent professional oversight;
- no automated clinical alerts;
- no diagnostic or emotion inference.

Primary clinical/motor outcomes should remain validated standardized instruments. NeuroJitsu metrics remain complementary until criterion validity and reliability are established in the target population.
