# Ball Reaction Guide

## Coverstock Hierarchy

- **Plastic**: spare-first, minimal friction
- **Urethane**: control shape, earlier but smoother motion
- **Reactive**: benchmark motion on medium conditions
- **Hybrid reactive**: blend of midlane read and continuation
- **Pearl reactive**: cleaner through the fronts, stronger backend response
- **Particle / strong solids**: traction on longer or higher-volume patterns

## Core Variables

- **RG**: lower RG revs sooner; higher RG delays migration
- **Differential**: higher values increase flare potential
- **Mass bias**: adds asymmetry and can sharpen response

## Surface Rules

- Lower grit numbers read sooner
- Higher grit or polish stores energy longer
- Surface should be re-measured because wear changes the intended reaction

## Matching Shapes to Conditions

| Condition | Preferred reaction | Common fit |
| --- | --- | --- |
| Light / broken down | control or clean angular | urethane, pearl reactive |
| Medium | benchmark blend | reactive, hybrid reactive |
| Heavy / long | traction and early read | solid reactive, particle |

## Engine Outputs

The v1 backend model scores each ball for:
- fit score (0-100)
- matched shape (`control`, `benchmark`, `traction`)
- predicted trajectory
- projected strike probability

