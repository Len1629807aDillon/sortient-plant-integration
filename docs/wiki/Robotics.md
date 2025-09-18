# Robotics Integration Guide

This guide explains how Sortient Plant Integration communicates with robotics platforms in
production environments.

## Protocol Support Matrix

| Capability                 | ROS 2                         | OPC UA                         | EtherCAT                         |
| -------------------------- | ----------------------------- | ------------------------------ | -------------------------------- |
| Latency                    | ~50 ms                        | ~75 ms                         | < 10 ms                          |
| Reliability                | QoS-managed publish/subscribe | Redundant client failover      | Deterministic fieldbus           |
| Typical Use Case           | Robotic arms and manipulators | PLC/SCADA coordination         | Air jets, diverters, high-speed  |
| Safety Integration         | Emergency stop topics         | Safety namespace monitoring    | Hardware interlocks              |
| Authentication             | DDS-Security                  | X.509 certificates             | Physical network segmentation    |

## Command Lifecycle

1. **Decision Generation** – `DecisionPlanner` produces a `SortingDecision` per observation.
2. **Standard Envelope** – `build_command` renders the decision into protocol-specific payloads.
3. **Command Dispatch** – `RoboticsInterface` transports the command using the chosen protocol.
4. **Actuation Feedback** – Implementors extend `RoboticsInterface` to ingest acknowledgements and
   telemetry for closed-loop control.

## Extending Protocols

To add a new protocol:

1. Implement `StandardCommandBuilder` returning `StandardCommandEnvelope`.
2. Register a `RoboticsInterface` subclass capable of connecting, sending commands, and receiving
   feedback.
3. Add the protocol to `RoboticsInterfaceFactory._registry`.

The shared abstractions ensure consistent handling of metadata, acknowledgements, and safety
workflows across protocols.

