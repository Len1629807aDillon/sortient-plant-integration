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
4. Call `simulate_step` to compute the next state.

Outputs include the new load distribution, energy consumption (kW), and recovery rate for the
material class.

## Extending the Digital Twin

- Integrate empirical energy coefficients per segment.
- Model maintenance downtimes by disabling nodes or edges.
- Integrate with reinforcement learning agents to optimise routing.

