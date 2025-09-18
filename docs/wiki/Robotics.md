# Robotics Integration Guide

This guide explains how Sortient Plant Integration communicates with robotics platforms in
production environments and how to extend the stack for new protocols.

## Protocol support matrix

| Capability                 | ROS 2                         | OPC UA                         | EtherCAT                     | Modbus TCP                      | Fanuc PCDK                   |
| -------------------------- | ----------------------------- | ------------------------------ | ---------------------------- | -------------------------------- | ---------------------------- |
| Latency                    | ~50 ms                        | ~75 ms                         | < 10 ms                      | ~20 ms                          | ~120 ms                     |
| Reliability                | QoS-managed publish/subscribe | Redundant client failover      | Deterministic fieldbus       | PLC register acknowledgements    | Vendor runtime APIs         |
| Typical Use Case           | Robotic arms and manipulators | PLC/SCADA coordination         | Air jets, diverters, high-speed | Diverter gates and compactors    | Articulated picking arms    |
| Safety Integration         | Emergency stop topics         | Safety namespace monitoring    | Hardware interlocks          | Safety relays                   | Dual-check safety routines  |
| Authentication             | DDS-Security                  | X.509 certificates             | Physical network segmentation | Plant network ACLs               | Controller credentials      |

## Command lifecycle

1. **Decision generation** – `DecisionPlanner` produces a `SortingDecision` per observation.
2. **Standard envelope** – `build_command` renders the decision into protocol-specific payloads. The
   `CommandContext` carries plant identifiers, handshake metadata, latency budgets, and safety
   envelopes so every payload is fully annotated.
3. **Command dispatch** – `RoboticsInterface` transports the command using the chosen protocol and
   tracks handshake status, latency, and dropped messages for diagnostics.
4. **Actuation feedback** – Implementors extend `RoboticsInterface` to ingest acknowledgements and
   telemetry for closed-loop control or quality assurance loops.

## Diagnostics and safety

- Connection state exposes heartbeat timestamps, whether a handshake completed, observed latency, and
  dropped message counts.
- `publish_diagnostics()` prints a compact snapshot of the current robotics connection for operations
  teams.
- Safety envelopes can be defined in configuration to enforce emergency stop topics, payload limits,
  and keep-out zones.

## Extending protocols

To add a new protocol:

1. Implement `StandardCommandBuilder` returning `StandardCommandEnvelope`. Builders receive a
   `CommandContext` so they can enrich payloads with plant IDs, sequence numbers, and QoS hints.
2. Register a `RoboticsInterface` subclass capable of connecting, sending commands, and receiving
   feedback. The base class already exposes heartbeat tracking and diagnostic helpers.
3. Add the protocol to `RoboticsInterfaceFactory._registry` (or call `register_builder`) so the
   integration controller can instantiate it from configuration.

The shared abstractions ensure consistent handling of metadata, acknowledgements, diagnostics, and
safety workflows across protocols. Integrators can begin with the mock interfaces supplied in the
repository and gradually swap them out for field-tested drivers.
