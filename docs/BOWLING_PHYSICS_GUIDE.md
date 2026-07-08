# Bowling Physics Guide

This guide defines the baseline physics model for Bowling-HQ's bowling expert agent. It is intentionally practical: every concept maps to a feature, a field in the data model, or a prediction output.

## Core State Variables

### Lane and Oil
- **Pattern length (ft)** drives when friction becomes available.
- **Oil volume (ml)** changes skid distance and hold area.
- **Asymmetry index (0-1)** describes how narrow the playable zone is.
- **Front / midlane / backend oil share** controls where the lane reads.
- **Lane surface** modifies effective friction (`wood > hybrid > synthetic`).

### Ball
- **Coverstock family** controls baseline friction.
- **Surface grit** controls how early the ball reads the lane.
- **RG** influences rev timing and length.
- **Differential / mass bias** shape total flare and motion shape.

### Bowler
- **Speed (mph)**, **rev rate (RPM)**, **axis rotation**, and **axis tilt** drive motion shape.
- **Consistency** widens or narrows the confidence interval.

## Ball Motion Model

Bowling-HQ models the ball in three phases:
1. **Skid** - oil dominated, speed retained
2. **Hook** - friction increases, axis migrates
3. **Roll** - forward roll dominates into the pins

The initial engine predicts:
- skid distance
- hook distance
- roll distance
- breakpoint board
- entry angle
- strike probability
- confidence

## Physics Rules Used in v1

- More oil and more speed increase skid length.
- Rougher surfaces and stronger covers reduce skid length.
- Lower RG and higher differential increase total motion potential.
- Entry angles near ~6° improve carry probability.
- Higher front-lane breakdown moves the breakpoint inward; carrydown delays backend response.

## Where the Model Evolves Next

The current engine is heuristic and designed to be calibrated later with:
- measured lane tapes and pattern files
- tracked ball motion data
- release metrics from video
- pin carry outcome history

See also:
- [Oil Pattern Analysis](OIL_PATTERN_ANALYSIS.md)
- [Ball Reaction Guide](BALL_REACTION_GUIDE.md)
- [Biomechanics Analysis](BIOMECHANICS_ANALYSIS.md)
- [Physics Integration Specs](PHYSICS_INTEGRATION_SPECS.md)

