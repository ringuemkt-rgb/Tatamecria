# Research Scope

## Core scientific purpose

NeuroJitsu Analytics is a **measurement research platform** for motor-control studies involving standardized movement tasks and adapted BJJ contexts.

The current core is designed to support:

- motor control;
- postural control;
- balance-related movement features;
- movement quality;
- bilateral differences;
- repeated longitudinal measurement;
- validation of low-cost markerless measures.

## Primary layer

The primary software layer contains transparent variables whose formulas can be inspected:

- joint angle;
- range of motion;
- trajectory length;
- normalized jerk proxy;
- bilateral difference;
- trunk inclination;
- data-quality indicators.

These are engineering/research variables until validated for a specific protocol and population.

## Secondary layer

Markerless pose and tracking are acquisition methods, not clinical outcomes. Their outputs must be validated against reference methods for each intended task.

## Research extensions

The repository preserves earlier work that may become useful in later studies:

- HRV/RMSSD;
- technique-phase tagging;
- whole-body keypoints;
- optional narrative agents;
- WiFi-CSI sensing;
- heavier pose/action-recognition backends.

They are not required to run the motor-control core and should not be included in a master's study unless the scientific question and supervision justify them.

## Explicitly out of scope

- autism diagnosis;
- emotion recognition from face/body;
- meltdown prediction;
- autonomous clinical decisions;
- hidden “normality” scoring;
- automated ranking of children;
- treatment prescription by software.

## Dissertation-safe hierarchy

A defensible study should keep:

1. validated standardized motor/clinical outcome as primary;
2. laboratory reference measures as objective research outcomes when available;
3. NeuroJitsu variables as complementary/exploratory until validated.

This hierarchy prevents the software from becoming the scientific claim.
