"""Standards-compliant command generation for robotics integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, Optional, Protocol

from ..data.structures import RoboticsCommand, SortingDecision


class RoboticsStandard(str, Enum):
    """Industry standards used for robotic control."""

    ROS2 = "ros2"
    OPC_UA = "opc_ua"
    MODBUS_TCP = "modbus_tcp"
    ETHERCAT = "ethercat"
    FANUC_PCDK = "fanuc_pcdk"


@dataclass(slots=True)
class StandardCommandEnvelope:
    """Container describing a robotics command compatible with a standard."""

    standard: RoboticsStandard
    payload: Dict[str, object]
    diagnostics: Dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class CommandContext:
    """Metadata injected into command builders (e.g., safety and plant info)."""

    plant_id: str
    sequence_id: Optional[str] = None
    safety_metadata: Dict[str, object] = field(default_factory=dict)
    telemetry_overrides: Dict[str, object] = field(default_factory=dict)


class StandardCommandBuilder(Protocol):
    """Protocol for building commands in various standards."""

    def build(
        self, decision: SortingDecision, context: Optional[CommandContext] = None
    ) -> StandardCommandEnvelope:
        ...


@dataclass(slots=True)
class Ros2CommandBuilder:
    """Translate sorting decisions into ROS 2 motion planning primitives."""

    topic: str = "/sortient/robotics/trajectory"

    def build(
        self, decision: SortingDecision, context: Optional[CommandContext] = None
    ) -> StandardCommandEnvelope:
        context = context or CommandContext(plant_id="unknown")
        payload = {
            "topic": self.topic,
            "msg_type": "trajectory_msgs/msg/JointTrajectory",
            "header": {
                "frame_id": "sortient_world",
                "stamp": context.telemetry_overrides.get("ros_timestamp"),
            },
            "goal_tolerance": context.telemetry_overrides.get(
                "goal_tolerance", {"position": 0.002, "velocity": 0.01}
            ),
            "points": [
                {
                    "positions": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    "velocities": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    "accelerations": [0.0] * 6,
                    "time_from_start": 0.0,
                },
                {
                    "positions": [0.1, 0.3, 0.2, 0.4, 0.1, 0.0],
                    "velocities": [0.2, 0.5, 0.3, 0.4, 0.2, 0.1],
                    "accelerations": [0.05] * 6,
                    "time_from_start": 0.5,
                },
                {
                    "positions": [0.2, 0.6, 0.4, 0.2, 0.2, 0.1],
                    "velocities": [0.15, 0.35, 0.28, 0.18, 0.15, 0.1],
                    "accelerations": [0.03] * 6,
                    "time_from_start": 1.0,
                },
            ],
            "metadata": {
                "target_lane": decision.target_lane,
                "priority": decision.priority,
                "decision_confidence": decision.confidence,
                "rationale": decision.rationale,
                "plant_id": context.plant_id,
            },
        }
        diagnostics = {
            "safety": context.safety_metadata,
            "sequence_id": context.sequence_id,
        }
        return StandardCommandEnvelope(
            standard=RoboticsStandard.ROS2, payload=payload, diagnostics=diagnostics
        )


@dataclass(slots=True)
class OpcUaCommandBuilder:
    """Translate sorting decisions into OPC UA method calls."""

    node_id: str = "ns=2;i=10853"

    def build(
        self, decision: SortingDecision, context: Optional[CommandContext] = None
    ) -> StandardCommandEnvelope:
        context = context or CommandContext(plant_id="unknown")
        payload = {
            "node_id": self.node_id,
            "method": "TriggerSortingSequence",
            "arguments": {
                "lane": decision.target_lane,
                "priority": decision.priority,
                "confidence": decision.confidence,
                "actuator": decision.expected_actuator,
                "plant": context.plant_id,
                "sequence": context.sequence_id,
            },
            "input_signature": ["String", "UInt16", "Double", "String", "String", "String"],
        }
        diagnostics = {
            "requires_handshake": context.safety_metadata.get("handshake_required", True),
            "expected_ack_timeout": context.telemetry_overrides.get("ack_timeout_s"),
        }
        return StandardCommandEnvelope(
            standard=RoboticsStandard.OPC_UA, payload=payload, diagnostics=diagnostics
        )


@dataclass(slots=True)
class EthercatCommandBuilder:
    """Build EtherCAT frame payloads for high-speed actuation."""

    frame_id: int = 0x01

    def build(
        self, decision: SortingDecision, context: Optional[CommandContext] = None
    ) -> StandardCommandEnvelope:
        context = context or CommandContext(plant_id="unknown")
        payload = {
            "frame_id": self.frame_id,
            "payload_bytes": [
                len(decision.target_lane),
                decision.priority,
                int(decision.confidence * 1000),
            ],
            "metadata": {
                "actuator": decision.expected_actuator,
                "rationale": decision.rationale,
                "plant": context.plant_id,
            },
        }
        diagnostics = {
            "jitter_budget_ms": context.telemetry_overrides.get("jitter_budget_ms", 5),
        }
        return StandardCommandEnvelope(
            standard=RoboticsStandard.ETHERCAT, payload=payload, diagnostics=diagnostics
        )


@dataclass(slots=True)
class ModbusTcpCommandBuilder:
    """Compose Modbus TCP payloads for PLC controlled diverters."""

    unit_id: int = 1

    def build(
        self, decision: SortingDecision, context: Optional[CommandContext] = None
    ) -> StandardCommandEnvelope:
        context = context or CommandContext(plant_id="unknown")
        register_base = 40000
        payload = {
            "unit_id": self.unit_id,
            "function_code": 16,
            "address": register_base + int(decision.priority * 10),
            "values": [
                len(decision.target_lane),
                int(decision.confidence * 10000),
                hash(decision.observation_id) % 65535,
            ],
            "metadata": {"target_lane": decision.target_lane, "plant": context.plant_id},
        }
        diagnostics = {"register_count": len(payload["values"])}
        return StandardCommandEnvelope(
            standard=RoboticsStandard.MODBUS_TCP, payload=payload, diagnostics=diagnostics
        )


@dataclass(slots=True)
class FanucPcdkCommandBuilder:
    """Compose Fanuc PCDK motion program calls for articulated arms."""

    program: str = "SORTIENT_PICK"

    def build(
        self, decision: SortingDecision, context: Optional[CommandContext] = None
    ) -> StandardCommandEnvelope:
        context = context or CommandContext(plant_id="unknown")
        payload = {
            "program": self.program,
            "arguments": [
                decision.target_lane,
                decision.priority,
                round(decision.confidence, 3),
                decision.expected_actuator,
            ],
            "comment": f"auto-sort {decision.observation_id} for {context.plant_id}",
        }
        diagnostics = {"pcdk_version": context.telemetry_overrides.get("pcdk_version", "1.0")}
        return StandardCommandEnvelope(
            standard=RoboticsStandard.FANUC_PCDK, payload=payload, diagnostics=diagnostics
        )


_BUILDER_REGISTRY: Dict[RoboticsStandard, StandardCommandBuilder] = {
    RoboticsStandard.ROS2: Ros2CommandBuilder(),
    RoboticsStandard.OPC_UA: OpcUaCommandBuilder(),
    RoboticsStandard.ETHERCAT: EthercatCommandBuilder(),
    RoboticsStandard.MODBUS_TCP: ModbusTcpCommandBuilder(),
    RoboticsStandard.FANUC_PCDK: FanucPcdkCommandBuilder(),
}


def register_builder(standard: RoboticsStandard, builder: StandardCommandBuilder) -> None:
    """Register or override a command builder for a robotics standard."""

    _BUILDER_REGISTRY[standard] = builder


def build_command(
    standard: RoboticsStandard,
    decision: SortingDecision,
    context: Optional[CommandContext] = None,
) -> StandardCommandEnvelope:
    """Factory function returning the correct standard builder."""

    try:
        builder = _BUILDER_REGISTRY[standard]
    except KeyError as exc:
        raise ValueError(f"Unsupported robotics standard: {standard}") from exc
    return builder.build(decision, context=context)


def get_available_standards() -> Iterable[RoboticsStandard]:
    """Expose registered standards for discovery tooling."""

    return list(_BUILDER_REGISTRY.keys())


def format_command_for_transport(command: RoboticsCommand) -> Dict[str, object]:
    """Prepare a robotics command for message bus delivery."""

    return {
        "actuator_id": command.actuator_id,
        "command_type": command.command_type,
        "parameters": command.parameters,
        "issued_at": command.issued_at.isoformat(),
        "requires_ack": command.requires_ack,
        "correlation_id": command.correlation_id,
    }

