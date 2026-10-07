# Known Limitations

## Scientific

- No criterion validity against laboratory reference equipment has yet been established.
- No target-population reliability has yet been established.
- No clinical validity has been established.
- Software test coverage does not imply scientific validity.

## Markerless vision

- 2D measurements are affected by perspective and camera geometry.
- Grappling creates severe self- and partner-occlusion.
- Pose backends may swap people or landmarks.
- Clothing, lighting and floor interaction can reduce landmark quality.
- Multi-person ground grappling is an especially difficult pose-estimation problem.

## Metrics

- Jerk-based smoothness is sensitive to noise and filtering.
- Bilateral difference is descriptive and not synonymous with pathology.
- Trunk inclination depends on valid shoulder/hip landmarks.
- Path length requires calibration before physical-distance interpretation.

## Generalizability

Adult validation cannot be assumed to generalize to children.
A metric validated in one task cannot automatically be assumed valid in another task.
A metric validated in one camera setup cannot automatically be assumed valid in another setup.

## Research operations

Any study involving minors or identifiable health data requires institutional ethics and data-governance approval before collection.
