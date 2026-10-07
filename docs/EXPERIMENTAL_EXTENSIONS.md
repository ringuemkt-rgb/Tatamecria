# Experimental Extensions

Earlier NeuroJitsu development explored several modules beyond the current motor-control core. They are retained for reproducibility and future research, but are explicitly **non-core**.

## HRV / physiology

Location: `src/neurojitsu/physiology/`

Current capability:

- basic RR-derived HRV utilities;
- quality-aware processing path;
- optional NeuroKit2 dependency.

Academic status:

- useful only with a validated acquisition protocol and reference device;
- not required for the current motor-control focus.

## Technique-phase analysis

Locations:

- `src/neurojitsu/analysis/technique_phases.py`
- `src/neurojitsu/analysis/phase_tagger.py`

Current capability:

- deterministic phase ontology;
- temporal stabilization logic.

Academic status:

- potentially useful for future movement-sequence studies;
- technique recognition itself is not validated.

## Whole-body / multi-person vision

Locations:

- `src/neurojitsu/vision/wholebody.py`
- `src/neurojitsu/vision/supervision_runtime.py`

Current capability:

- whole-body contracts;
- detection/keypoint adapters;
- tracking metadata;
- zone events.

Academic status:

- technically promising for grappling;
- severe occlusion and identity uncertainty remain open research problems.

## Local narrative agents

Location: `src/neurojitsu/agents/`

Purpose:

- generate optional human-readable drafts from structured results.

Rule:

- agents do not create measurements;
- agents do not receive authority to diagnose or recommend treatment;
- deterministic reports remain available without them.

## WiFi-CSI

Location: `src/neurojitsu/wifi/`

Status:

- experimental adapter retained from earlier research exploration;
- not part of the master's-scale motor-control plan;
- should remain disabled unless a future protocol specifically justifies it.

## Heavy pose/action-recognition stacks

Configuration and documentation reference potential external stacks such as heavier pose and temporal skeleton models.

Status:

- research options only;
- not default dependencies;
- not required for the current validation path;
- external licenses and weights must be reviewed independently.
