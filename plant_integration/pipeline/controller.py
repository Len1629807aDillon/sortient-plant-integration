"""High-level orchestration of the Sortient plant integration pipeline."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Iterator, Optional

import numpy as np
from rich.console import Console
from rich.table import Table

from ..ai.detector import MaterialDetector
from ..config import IntegrationConfig
from ..data.structures import IntegrationEvent, RoboticsCommand
from ..integration.planner import DecisionPlanner
from ..integration.standards import RoboticsStandard
from ..robotics.command_stream import decisions_to_commands
from ..robotics.interfaces import RoboticsInterface, RoboticsInterfaceFactory

console = Console()


@dataclass(slots=True)
class PipelineStatistics:
    """Runtime statistics collected by the integration controller."""

    processed_items: int = 0
    rejected_items: int = 0
    last_updated: Optional[datetime] = None

    def update(self, success: bool) -> None:
        self.processed_items += 1
        if not success:
            self.rejected_items += 1
        self.last_updated = datetime.utcnow()


class IntegrationController:
    """Orchestrates detection, decision-making, and robotics connectivity."""

    def __init__(
        self,
        config: IntegrationConfig,
        detector: MaterialDetector,
        planner: DecisionPlanner,
        robotics_interface: Optional[RoboticsInterface] = None,
    ) -> None:
        self.config = config
        self.detector = detector
        self.planner = planner
        self.robotics_interface = (
            robotics_interface
            or RoboticsInterfaceFactory.create(
                config.robotics.protocol, config.robotics.endpoint, config.robotics.namespace
            )
        )
        self.statistics = PipelineStatistics()

    def startup(self) -> None:
        """Start the controller and establish robotics connectivity."""

        console.rule(f"Starting integration pipeline for plant {self.config.plant_id}")
        self.robotics_interface.connect()

    def shutdown(self) -> None:
        """Shutdown procedure, ensuring robotics interface disconnects cleanly."""

        console.rule("Stopping integration pipeline")
        self.robotics_interface.disconnect()

    def ingest_stream(self) -> Iterator[IntegrationEvent]:
        """Simulate ingestion of material events."""

        interval = self.config.data_ingestion.refresh_interval_ms / 1000.0
        counter = 0
        feature_len = len(self.detector.feature_names)
        while True:
            payload = {
                "observation_id": f"sim-{counter}",
                "feature_vector": [0.1 * ((counter + i) % 10) for i in range(feature_len)],
                "metadata": {
                    "location_coordinates": {"x": 0.5, "y": 1.2, "z": 0.05},
                    "contamination_score": 0.1,
                },
            }
            yield IntegrationEvent(event_type="material_sample", payload=payload)
            counter += 1
            time.sleep(interval)

    def process_event(self, event: IntegrationEvent) -> Optional[RoboticsCommand]:
        """Process a single integration event."""

        if event.event_type != "material_sample":
            console.log(f"[yellow]Skipping unsupported event type {event.event_type}[/yellow]")
            return None
        feature_vector = np.asarray(event.payload["feature_vector"], dtype=float)
        metadata = event.payload["metadata"]
        detection = self.detector.predict(feature_vector, metadata)
        decision = self.planner.plan(detection.observation)
        command = next(
            decisions_to_commands(
                [decision], RoboticsStandard(self.config.robotics.protocol), decision.expected_actuator
            ),
            None,
        )
        if command is None:
            self.statistics.update(success=False)
            return None
        self.robotics_interface.send(command)
        self.statistics.update(success=True)
        return command

    def run(self, events: Iterable[IntegrationEvent], limit: Optional[int] = None) -> None:
        """Process an event stream until exhaustion or limit."""

        processed = 0
        for event in events:
            self.process_event(event)
            processed += 1
            if limit and processed >= limit:
                break
        self.render_statistics()

    def render_statistics(self) -> None:
        """Render runtime statistics in a table."""

        table = Table(title="Integration Pipeline Statistics")
        table.add_column("Metric")
        table.add_column("Value")
        table.add_row("Processed Items", str(self.statistics.processed_items))
        table.add_row("Rejected Items", str(self.statistics.rejected_items))
        table.add_row("Last Updated", str(self.statistics.last_updated))
        console.print(table)

