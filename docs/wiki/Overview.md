# Sortient Plant Integration Overview

The Sortient Plant Integration project provides a full-stack blueprint for deploying AI-assisted
recycling operations. It showcases how detection, decisioning, robotics, and analytics
infrastructure can be combined to reach industry-leading performance.

## Architecture

1. **Material Detection** – AI models ingest multi-spectrum sensor data and produce structured
   observations.
2. **Decision Planning** – Lane selection and actuator coordination maximise recovery and throughput
   while accounting for contamination tolerance and utilisation trends.
3. **Robotics Interface** – Commands are formatted according to ROS 2, OPC UA, EtherCAT, Modbus TCP,
   and Fanuc PCDK standards and can be extended for additional protocols.
4. **Digital Twin** – Conveyor-level simulation estimates performance, energy use, and recovery,
   exporting JSON snapshots for downstream analysis.
5. **Analytics** – Metrics and dashboards provide operational visibility, including OEE breakdowns,
   throughput trends, and predictive maintenance insights.

The integration controller orchestrates these layers and enables configuration-driven deployments.

## Design Principles

- **Openness** – Built to integrate with existing plants and third-party solutions.
- **Reliability** – Emphasis on deterministic pipelines and fail-safe robotics integration.
- **Extensibility** – Modular architecture supporting new sensors, actuators, analytics engines, and
  robotics standards through runtime registration.
- **Observability** – Rich telemetry surfaces actionable insights for operations teams, and the CLI
  exposes simulation and diagnostics commands for rapid iteration.

## Configuration-driven deployment

The YAML configuration schema captures ingestion cadences, robotics safety envelopes, QoS settings,
analytics toggles, and digital twin preferences. Validation ensures that safety-related constraints
are respected before the integration pipeline boots.

## Tooling highlights

- `scripts/run_pipeline.py run` executes the full AI-to-robotics pipeline using sample data.
- `scripts/run_pipeline.py simulate` drives the digital twin independently to validate plant
  layouts.
- Mock robotics interfaces expose diagnostics hooks so integrators can verify messaging semantics
  without physical hardware.

