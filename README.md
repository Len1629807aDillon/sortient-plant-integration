# Sortient Plant Integration

Sortient Plant Integration is an open-source, production-grade toolkit that connects advanced
recycling AI with industrial robotics. The project demonstrates how the Sortient technology stack
can be integrated with modern material recovery facilities, enabling real-time decision making,
robotic execution, and facility-wide analytics.

## Key Capabilities

- **AI Material Detection** – High-performance detection pipeline with confidence tracking and
  contamination analysis.
- **Decision Planning** – Adaptive lane assignment using throughput-aware heuristics.
- **Robotics Integration** – Standards-compliant command generation for ROS 2, OPC UA, and EtherCAT
  robotic systems.
- **Digital Twin Simulation** – Graph-based plant simulator to evaluate conveyor layouts and energy
  consumption.
- **Analytics** – Accuracy, throughput, and recovery metrics for operational intelligence.
- **CLI Tooling** – Typer-based CLI to run integration demos, inspect configuration, and orchestrate
  pipelines end-to-end.

## Project Structure

```text
plant_integration/
├── ai/                  # Detection pipelines and AI artifacts
├── analytics/           # Metrics and analytical utilities
├── config.py            # Typed configuration definitions
├── data/                # Shared data structures
├── integration/         # Decision planning and robotics standards
├── pipeline/            # Integration controller orchestrating the stack
├── robotics/            # Robotics connectivity abstractions
├── simulation/          # Digital twin simulation utilities
└── utils/               # Shared utilities (logging, helpers)
```

## Getting Started

### Prerequisites

- Python 3.10+
- Optional: ROS 2, OPC UA server, or EtherCAT stack if connecting to live equipment

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Running the Demo Pipeline

1. Prepare the configuration file (a sample is provided under `examples/sample_config.yaml`).
2. Execute the CLI:

   ```bash
   python scripts/run_pipeline.py run examples/sample_config.yaml --iterations 10
   ```

   The command will train a synthetic detector (if not already available), stream simulated events,
   and publish commands to the mock robotics interfaces.

### Inspecting Configuration

```bash
python scripts/run_pipeline.py describe-config examples/sample_config.yaml
```

## Robotics Integration

Sortient Plant Integration emphasizes compatibility with industry-standard communication layers.
The project includes command builders for:

| Standard    | Use Case                                | Example Payload                                         |
| ----------- | ---------------------------------------- | -------------------------------------------------------- |
| ROS 2       | High-speed robotic manipulators          | `trajectory_msgs/msg/JointTrajectory` with rich metadata |
| OPC UA      | Interoperable PLC and SCADA systems      | Method calls invoking `TriggerSortingSequence`           |
| EtherCAT    | Deterministic high-speed actuator control| Compact frame payloads for air jets or mechanical gates  |

Integrators can extend `StandardCommandBuilder` to support additional protocols (e.g., Modbus TCP,
Fanuc PCDK) while leveraging the shared `RoboticsCommand` abstraction. The `RoboticsInterface`
classes provide a clear contract for exchanging commands with field devices and can be adapted to
use ROS 2 publishers, OPC UA clients, or EtherCAT masters.

## Digital Twin Simulation

The `FacilitySimulator` enables planners to model complex conveyor networks as directed graphs. By
combining segment capacities, velocities, and energy consumption coefficients, the simulator
produces:

- Load distribution per segment
- Estimated energy draw per time step
- Recovery rate predictions per material class

These insights accelerate commissioning by validating that the robotic cell can achieve target
throughput and purity before physical deployment.

## Analytics and Monitoring

The analytics module provides tooling for:

- Confusion matrix analysis across material classes
- Throughput calculations over sliding windows
- Overall Equipment Effectiveness (OEE)
- Predictive maintenance recommendations

Results are surfaced through Rich tables and can be exported to monitoring stacks such as Prometheus
or Grafana.

## Configuration Schema

`IntegrationConfig` defines the parameters required to orchestrate the plant:

- **Plant metadata** – Unique plant identifier and optional materials catalog
- **Data ingestion** – Source, refresh cadence, and batching strategy
- **Robotics** – Protocol, endpoint, namespaces, and safety parameters
- **Feature toggles** – Predictive maintenance, closed-loop control, real-time dashboards

The schema is extensible and designed for infrastructure-as-code workflows.

## Roadmap

- Real ROS 2 bridge leveraging `rclpy`
- OPC UA client integration using `asyncua`
- Edge deployment toolkit with containerized microservices
- Reinforcement learning planners for dynamic lane optimization
- Advanced predictive maintenance models using survival analysis

## Contributing

Contributions from the community are welcome. Suggested areas include:

- Additional robotics protocol adaptors
- Higher fidelity simulators with physics-based modelling
- Visualization dashboards built on Plotly Dash or Streamlit
- Integration with MES/SCADA systems

Before submitting a pull request, please run:

```bash
ruff check .
pytest
```

## License

Sortient Plant Integration is released under the [MIT License](LICENSE).

