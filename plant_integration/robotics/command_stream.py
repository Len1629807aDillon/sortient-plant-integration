"""Command stream utilities bridging AI decisions and robotics commands."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Iterator

from ..data.structures import RoboticsCommand, SortingDecision
from ..integration.standards import RoboticsStandard, StandardCommandEnvelope, build_command


def decisions_to_commands(
    decisions: Iterable[SortingDecision],
    standard: RoboticsStandard,
    actuator_id: str,
) -> Iterator[RoboticsCommand]:
    """Convert sorting decisions to robotics commands."""

    for decision in decisions:
        envelope: StandardCommandEnvelope = build_command(standard, decision)
        command = RoboticsCommand(
            actuator_id=actuator_id,
            command_type=f"{envelope.standard.value}_dispatch",
            parameters={"payload": envelope.payload},
            issued_at=datetime.utcnow(),
            correlation_id=decision.observation_id,
        )
        yield command

