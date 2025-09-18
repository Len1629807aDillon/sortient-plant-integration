"""Tests for robotics command generation."""

from datetime import datetime, timezone

from plant_integration.data.structures import RoboticsCommand, SortingDecision
from plant_integration.integration.standards import (
    CommandContext,
    RoboticsStandard,
    build_command,
    format_command_for_transport,
)
from plant_integration.robotics.command_stream import decisions_to_commands


def _decision() -> SortingDecision:
    return SortingDecision(
        observation_id="obs-1",
        target_lane="lane_a",
        priority=5,
        confidence=0.9,
        expected_actuator="actuator_lane_a",
        rationale="test",
    )


def _context() -> CommandContext:
    return CommandContext(
        plant_id="demo",
        sequence_id="seq-1",
        safety_metadata={"handshake_required": True, "max_payload_kg": 20},
        telemetry_overrides={"ack_timeout_s": 1.0},
    )


def test_build_ros2_command() -> None:
    decision = _decision()
    envelope = build_command(RoboticsStandard.ROS2, decision, context=_context())
    assert envelope.standard == RoboticsStandard.ROS2
    assert envelope.payload["metadata"]["target_lane"] == "lane_a"
    assert envelope.diagnostics["sequence_id"] == "seq-1"


def test_modbus_command_metadata() -> None:
    decision = _decision()
    envelope = build_command(RoboticsStandard.MODBUS_TCP, decision, context=_context())
    assert envelope.payload["metadata"]["plant"] == "demo"


def test_format_command() -> None:
    command = RoboticsCommand(
        actuator_id="a1",
        command_type="ros2_dispatch",
        parameters={"payload": {"topic": "test"}},
        issued_at=datetime.now(timezone.utc),
    )
    message = format_command_for_transport(command)
    assert message["actuator_id"] == "a1"
    assert message["parameters"]["payload"]["topic"] == "test"


def test_decisions_to_commands_carries_context() -> None:
    decision = _decision()
    commands = list(
        decisions_to_commands(
            [decision], RoboticsStandard.MODBUS_TCP, "actuator_lane_a", _context()
        )
    )
    assert len(commands) == 1
    payload = commands[0].parameters["payload"]
    assert payload["metadata"]["plant"] == "demo"

