# Data Validation Rules

## Oil Patterns
- `length_ft` must be between 30 and 52
- `volume_ml` must be between 10 and 40
- oil segment percentages must be positive and total to a meaningful whole
- `asymmetry_index` must be between 0 and 1

## Balls
- `rg` must be between 2.40 and 2.80
- `differential` must be between 0.000 and 0.080
- `mass_bias` must be between 0.000 and 0.040
- `surface_grit` must be between 500 and 5000

## Bowlers
- `speed_mph` must be between 10 and 24
- `rev_rate` must be between 100 and 650
- `axis_rotation_deg` must be between 0 and 90
- `consistency` must be between 0 and 1

## Prediction Integrity
- every recommendation must include source inputs
- every score prediction must include a confidence range
- every simulation output must include the engine version and timestamp

