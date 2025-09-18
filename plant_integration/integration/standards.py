"""Standards-compliant command generation for robotics integration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Protocol

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


class StandardCommandBuilder(Protocol):
    """Protocol for building commands in various standards."""

    def build(self, decision: SortingDecision) -> StandardCommandEnvelope:
        ...


@dataclass(slots=True)
class Ros2CommandBuilder:
    """Translate sorting decisions into ROS2 motion planning primitives."""

    topic: str = "/sortient/robotics/trajectory"

    def build(self, decision: SortingDecision) -> StandardCommandEnvelope:
        payload = {
            "topic": self.topic,
            "msg_type": "trajectory_msgs/msg/JointTrajectory",
            "header": {"frame_id": "sortient_world"},
            "points": [
                {
                    "positions": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    "time_from_start": 0.0,
                },
                {
                    "positions": [0.1, 0.3, 0.2, 0.4, 0.1, 0.0],
                    "time_from_start": 0.5,
                },
                {
                    "positions": [0.2, 0.6, 0.4, 0.2, 0.2, 0.1],
                    "time_from_start": 1.0,
                },
            ],
            "metadata": {
                "target_lane": decision.target_lane,
                "priority": decision.priority,
                "decision_confidence": decision.confidence,
                "rationale": decision.rationale,
            },
        }
        return StandardCommandEnvelope(standard=RoboticsStandard.ROS2, payload=payload)


@dataclass(slots=True)
class OpcUaCommandBuilder:
    """Translate sorting decisions into OPC UA method calls."""

    node_id: str = "ns=2;i=10853"

    def build(self, decision: SortingDecision) -> StandardCommandEnvelope:
        payload = {
            "node_id": self.node_id,
            "method": "TriggerSortingSequence",
            "arguments": {
                "lane": decision.target_lane,
                "priority": decision.priority,
                "confidence": decision.confidence,
                "actuator": decision.expected_actuator,
            },
        }
        return StandardCommandEnvelope(standard=RoboticsStandard.OPC_UA, payload=payload)


@dataclass(slots=True)
class EthercatCommandBuilder:
    """Build EtherCAT frame payloads for high-speed actuation."""

    frame_id: int = 0x01

    def build(self, decision: SortingDecision) -> StandardCommandEnvelope:
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
            },
        }
        return StandardCommandEnvelope(standard=RoboticsStandard.ETHERCAT, payload=payload)


def build_command(standard: RoboticsStandard, decision: SortingDecision) -> StandardCommandEnvelope:
    """Factory function returning the correct standard builder."""

    builders: Dict[RoboticsStandard, StandardCommandBuilder] = {
        RoboticsStandard.ROS2: Ros2CommandBuilder(),
        RoboticsStandard.OPC_UA: OpcUaCommandBuilder(),
        RoboticsStandard.ETHERCAT: EthercatCommandBuilder(),
    }
    if standard not in builders:
        raise ValueError(f"Unsupported robotics standard: {standard}")
    return builders[standard].build(decision)


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

