# Measurement Dictionary

All values below are **research variables**. They are not clinical diagnoses.

| Metric | Unit | Interpretation | Main limitations |
|---|---:|---|---|
| Joint angle | degrees | Internal angle from three points | 2D projection, pose error, camera geometry |
| Range of motion | degrees | Max–min angle over valid samples | Depends on valid angle trajectory |
| Path length | coordinate units | Cumulative landmark trajectory | Scale/camera calibration required for physical units |
| Normalized jerk | arbitrary/dimensionless proxy | Lower may represent smoother trajectory | Sensitive to noise, filtering and sampling |
| Bilateral difference | % | Relative left–right difference | Not equivalent to pathological asymmetry |
| Trunk inclination | degrees | Trunk axis vs image/world vertical | Requires valid shoulder/hip points and calibrated orientation |

## Quality metadata

Every `MetricEstimate` includes:

- `value`;
- `unit`;
- `confidence`;
- `valid`;
- `reason_invalid`.

A missing value is preferable to a false precise value.

## Recommended validation metadata

Each laboratory record should also preserve:

- task ID;
- camera ID;
- camera position/calibration version;
- pose-backend version;
- model checksum when applicable;
- sample rate;
- participant pseudonym;
- session/day;
- operator;
- preprocessing version;
- invalid-window reason.

## Do not infer

A metric must not be converted automatically into:

- “good/bad movement”;
- autism severity;
- distress;
- emotion;
- injury risk;
- clinical normality.

Those interpretations require separate validated evidence.
