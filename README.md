# Sortient Plant Integration

Sortient Plant Integration is a production-grade, open-source reference stack that demonstrates how
to blend computer vision, decision intelligence, and robotics control inside a modern recycling
facility. The project is designed so that newcomers can understand the big picture while systems
integrators can dive straight into robotics protocols, digital twin modelling, and analytics tools.

## Why this project matters

Recycling plants are complex cyber-physical systems. Waste streams arrive continuously, materials
must be identified in milliseconds, and robots need to move safely alongside humans. Sortient Plant
Integration shows how to stitch these layers together:

- **Understandable for everyone** – The repository includes guided documentation, an approachable
  command-line interface, and a walk-through configuration so stakeholders can see the technology
  flow without deep technical knowledge.
- **Robotics-native** – Command builders cover ROS 2, OPC UA, EtherCAT, Modbus TCP, and Fanuc PCDK.
  Commands carry safety metadata, sequence identifiers, and quality-of-service hints so that they
  can slot directly into industrial controllers.
- **Digital twin ready** – A graph-based facility simulator models conveyor networks, predicts
  recovery rates, and exports energy/throughput reports that can be reviewed before hardware is
  deployed.
- **Analytics aware** – Accuracy breakdowns, throughput trends, OEE calculators, and predictive
  maintenance helpers make it easy to evaluate operational performance.

## Quick tour for non-specialists

1. **AI identifies materials** – A detector ingests sensor features and decides whether an item is
   plastic, glass, metal, paper, organic material, or other supported classes.
2. **The planner picks a lane** – Lane capacities, contamination tolerance, and current utilisation
   are weighed to choose where the material should go.
3. **Robotics commands are generated** – Standards-compliant payloads are produced for the protocol
   defined in the configuration (e.g., ROS 2 trajectories or Modbus register writes).
4. **Digital twin validates the flow** – Optional simulations stress-test conveyor layouts and
   estimate energy consumption before physical commissioning.
5. **Analytics close the loop** – Sliding-window throughput, OEE, and maintenance insights can be
   surfaced to dashboards or exported to monitoring systems.

The `examples/sample_config.yaml` file wires these components together so you can run a full demo in
minutes.

## Project structure

```text
plant_integration/
├── ai/                  # Detection pipelines and AI model utilities
├── analytics/           # Metrics, OEE, and maintenance analysis helpers
├── config.py            # Typed configuration schema with validation
├── data/                # Shared domain models (observations, decisions, commands)
├── integration/         # Decision planner and robotics standards registry
├── pipeline/            # Orchestrator that links detection, planning, and robotics
├── robotics/            # Interface abstractions for ROS 2, OPC UA, EtherCAT, etc.
├── simulation/          # Digital twin facility simulator and reporting utilities
└── utils/               # Shared helpers (e.g., logging)
```

## Getting started

### Prerequisites

- Python 3.10+
- Optional: access to ROS 2, OPC UA, EtherCAT, or PLC hardware if you want to replace the mock
  interfaces with live equipment.

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Run the end-to-end demo

```bash
python scripts/run_pipeline.py run examples/sample_config.yaml --iterations 25
```

This command trains a synthetic detector (if no model exists), streams simulated material events,
produces robotics commands with rich safety metadata, and logs digital twin results when the
configuration enables simulations.

### Explore the configuration

```bash
python scripts/run_pipeline.py describe-config examples/sample_config.yaml
```

The configuration schema captures plant metadata, ingestion cadence, robotics protocol details,
quality-of-service settings, and safety envelopes. Nested sections cover analytics toggles and
whether the digital twin should export simulation reports.

> **Path resolution tip:** Any relative paths supplied (e.g., `materials_catalog` or
> `digital_twin.export_path`) are resolved from the directory that contains the configuration file.
> This keeps configs portable across environments and avoids surprises when running the CLI from
> different working directories.

### Run the digital twin on its own

```bash
python scripts/run_pipeline.py simulate --steps 8 --material plastic
```

The standalone simulator uses a sample conveyor network to estimate throughput and energy draw. The
result is stored as structured JSON so it can be visualised or imported into MES/SCADA dashboards.

## Robotics integration highlights

- **Command context awareness** – Each robotics command is created with sequence IDs, handshake
  requirements, latency budgets, and plant identifiers. Integrators can register additional
  standards by extending the `StandardCommandBuilder` protocol.
- **Protocol coverage** – Builders for ROS 2, OPC UA, EtherCAT, Modbus TCP, and Fanuc PCDK translate
  AI decisions into protocol-native payloads. The mock interfaces included in the repository mimic
  publishers, method calls, and frame dispatch so the entire flow can be inspected without hardware.
- **Safety-first design** – Connection states track handshake completion, heartbeat timing, and
  dropped message counts. Diagnostics can be emitted on demand to confirm connectivity and
  performance envelopes.

## Digital twin simulation

The `FacilitySimulator` represents a plant as a directed graph. Each step of the simulation updates
segment loads, estimates energy usage with configurable coefficients, and predicts recovery rates per
material class. Multi-step runs produce:

- Per-step snapshots with load, energy, and recovery metrics
- Average energy draw and recovery rate
- Throughput estimates for every conveyor segment
- Optional JSON exports for archival or dashboarding

These features help commissioning teams validate throughput and purity targets before making changes
on the shop floor.

## Analytics and monitoring

The analytics module provides:

- Confusion matrices and accuracy breakdowns by material class
- Sliding-window throughput calculations and trend indicators
- Overall Equipment Effectiveness (OEE) breakdowns
- Predictive maintenance recommendations derived from vibration telemetry
- Moving-average utilities for forecasting pipelines

Outputs can be transformed into Rich tables, shipped to observability platforms, or embedded in
reports for stakeholders.

## Documentation and wiki

Extended documentation lives in `docs/wiki/` and covers architecture, robotics integration,
analytics practices, and simulation guidance. These guides are written so that both researchers and
industrial engineers can navigate the project quickly.

## Contributing

Contributions are welcome. High-impact areas include adding new robotics protocol adapters,
extending the digital twin with richer physics, integrating live ROS 2/OPC UA clients, and building
visual dashboards. Before submitting a pull request, please run:

```bash
pytest
```

The Sortient team is excited to collaborate with the community to push recycling technology forward.

## License

Sortient Plant Integration is released under the [MIT License](LICENSE).
