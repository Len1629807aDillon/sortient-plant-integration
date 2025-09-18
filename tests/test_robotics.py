"""Tests for robotics command generation."""

from datetime import datetime, timezone

from plant_integration.data.structures import RoboticsCommand, SortingDecision
from plant_integration.integration.standards import (
    RoboticsStandard,
    build_command,
    format_command_for_transport,
)


def _decision() -> SortingDecision:
    return SortingDecision(
        observation_id="obs-1",
        target_lane="lane_a",
        priority=5,
        confidence=0.9,
        expected_actuator="actuator_lane_a",
        rationale="test",
    )


def test_build_ros2_command() -> None:
    decision = _decision()
    envelope = build_command(RoboticsStandard.ROS2, decision)
    assert envelope.standard == RoboticsStandard.ROS2
    assert envelope.payload["metadata"]["target_lane"] == "lane_a"


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

