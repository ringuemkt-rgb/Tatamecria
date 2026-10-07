# Supervisor Brief

## One-sentence description

NeuroJitsu Analytics is pre-validation research software that converts standardized motor-task data into transparent movement metrics with explicit quality controls, designed to be **validated against laboratory reference methods before applied use**.

## What is ready

- reproducible Python package;
- synthetic data generator;
- tested biomechanical metric functions;
- quality/invalidity metadata;
- privacy-first data path;
- JSON/HTML reporting;
- API/dashboard for demonstration;
- automated CI on Python 3.11/3.12;
- documented staged validation plan.

## What is not ready

- criterion validity against reference kinematics;
- postural-control validity;
- two-person grappling validity;
- child-population reliability;
- clinical interpretation.

## Why a motor-control laboratory matters

The key scientific step is no longer “add more AI.” It is to determine which simple metrics survive comparison with reference methods.

A host laboratory can help define:

1. the right task;
2. the right reference instrument;
3. the correct calibration/synchronization;
4. the correct reliability/agreement statistics;
5. the correct scientific interpretation.

## Potential master's-scale questions

### Option A — technical validation

Can selected markerless joint/trunk metrics achieve acceptable agreement and test–retest reliability during standardized adult motor tasks?

### Option B — postural control

Can selected video-derived features complement established laboratory measures of balance/postural control?

### Option C — grappling feasibility

How do occlusion and two-person interaction affect markerless data completeness and reliability in standardized BJJ positions?

### Option D — applied adapted-BJJ pilot

Only after technical validation and ethics approval: can validated complementary metrics be collected feasibly during an adapted-BJJ intervention?

## Scientific rule

The software must serve the research question. The research question must not exist merely to demonstrate the software.
