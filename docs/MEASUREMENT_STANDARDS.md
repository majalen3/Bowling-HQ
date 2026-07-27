# Measurement Standards

## Pattern Data
- Store source (`PBA`, `USBC`, center, manual`)
- Record units explicitly (`ft`, `ml`)
- Preserve revision date because centers may rename or tweak a pattern

## Ball Data
- Normalize coverstock families
- Preserve original manufacturer naming as a raw field
- Track surface grit as both factory and current values

## Bowler Data
- Store mph and RPM as numeric fields
- Record confidence level for manually entered values
- Keep left/right handedness and lane side because it affects transition interpretation

## Simulation Data
- Persist engine version with every prediction
- Save seed values for Monte Carlo runs
- Record confidence intervals, not just point estimates

