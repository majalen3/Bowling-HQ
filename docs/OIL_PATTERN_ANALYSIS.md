# Oil Pattern Analysis

## Pattern Variables That Matter Most

| Variable | Why it matters | Stored as |
| --- | --- | --- |
| Length | Delays or accelerates friction access | `length_ft` |
| Volume | Controls total skid and forgiveness | `volume_ml` |
| Asymmetry | Narrows the margin for error | `asymmetry_index` |
| Front oil share | Controls early read | `front_oil_pct` |
| Midlane share | Controls blend vs. cliff | `mid_oil_pct` |
| Backend share | Controls downlane response | `backend_oil_pct` |

## Reading Fresh vs. Transition

### Fresh
- Longer skid
- More hold in the heads
- Lower entry angle for weaker shells

### Transition
- Front breakdown increases friction earlier
- Carrydown pushes oil farther downlane
- Breakpoint moves when breakdown outpaces carrydown

## Difficulty Heuristics

Bowling-HQ rates pattern difficulty on a 1-10 scale using:
- length
- volume
- asymmetry
- backend cleanliness
- front-lane concentration

Suggested interpretation:
- **1-3**: typical house or challenge-friendly
- **4-6**: medium difficulty, benchmark territory
- **7-8**: sport pattern requiring shape discipline
- **9-10**: high-volume or highly asymmetric elite conditions

## Prediction Outputs

Pattern Intelligence should expose:
- predicted breakpoint zone
- estimated launch window
- expected transition rate by frame
- recommended ball shape family
- adjustment trigger thresholds

