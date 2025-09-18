# Digital Twin Simulation

The digital twin allows integrators to evaluate facility configurations before physical
installation.

## Conveyor Graph Modelling

Each conveyor segment is represented as a node with:

- Length (m)
- Speed (m/s)
- Capacity (items)
- Outgoing connections

The simulator uses NetworkX to model the plant as a directed graph, enabling fast what-if analysis
for changes in routing or equipment.

## Simulation Workflow

1. Initialise `FacilitySimulator` with `ConveyorSegment` definitions.
2. Provide the current load distribution (items per segment).
3. Choose a `MaterialClass` to determine recovery heuristics.
4. Call `simulate` to run multi-step scenarios (or `simulate_step` for a single iteration).

Outputs include per-step snapshots, average energy consumption (kW), average recovery rate, and
throughput estimates for every segment. Reports can be exported as JSON for archival or visualisation
in external dashboards.

The CLI command `python scripts/run_pipeline.py simulate` demonstrates the workflow using a sample
conveyor network and automatically writes the report to disk.

## Extending the Digital Twin

- Integrate empirical energy coefficients per segment for more accurate energy predictions.
- Model maintenance downtimes by disabling nodes or edges between simulation steps.
- Use exported snapshots as training data for reinforcement learning agents to optimise routing.

