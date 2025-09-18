"""Decision planning for AI-guided recycling plants."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

import numpy as np

from ..data.structures import MaterialObservation, SortingDecision


@dataclass(slots=True)
class LaneConfiguration:
    """Configuration describing available sorting lanes."""

    lane_id: str
    supported_materials: List[str]
    capacity_per_minute: int
    contamination_tolerance: float = 0.1


@dataclass(slots=True)
class PlannerTelemetry:
    """Aggregated telemetry about planner decisions."""

    lane_utilization: Dict[str, float] = field(default_factory=dict)
    contamination_routes: Dict[str, float] = field(default_factory=dict)


class DecisionPlanner:
    """Plan sorting decisions based on AI observations and lane capacities."""

    def __init__(self, lanes: Iterable[LaneConfiguration]) -> None:
        self._lanes = list(lanes)
        self._telemetry = PlannerTelemetry(
            lane_utilization={lane.lane_id: 0.0 for lane in self._lanes},
            contamination_routes={lane.lane_id: lane.contamination_tolerance for lane in self._lanes},
        )

    def plan(self, observation: MaterialObservation) -> SortingDecision:
        """Generate a :class:`SortingDecision` for a given observation."""

        lane_scores: List[float] = []
        for lane in self._lanes:
            support = 1.0 if observation.material_class.value in lane.supported_materials else 0.2
            capacity_factor = min(1.0, observation.confidence * lane.capacity_per_minute / 1000.0)
            utilization_penalty = 1.0 - min(1.0, self._telemetry.lane_utilization[lane.lane_id])
            contamination_penalty = 1.0
            if observation.contamination_score > lane.contamination_tolerance:
                contamination_penalty = 0.5
            score = (0.6 * support) + (0.25 * capacity_factor) + (0.15 * utilization_penalty)
            score *= contamination_penalty
            lane_scores.append(score)
        index = int(np.argmax(lane_scores))
        lane = self._lanes[index]
        rationale = (
            f"Selected lane {lane.lane_id} for material {observation.material_class.value} "
            f"with score {lane_scores[index]:.3f}"
        )
        decision = SortingDecision(
            observation_id=observation.observation_id,
            target_lane=lane.lane_id,
            priority=int(np.clip(observation.confidence * 10, 1, 10)),
            confidence=float(lane_scores[index]),
            expected_actuator=f"actuator_{lane.lane_id}",
            rationale=rationale,
        )
        self._update_telemetry(decision, observation)
        return decision

    def reconfigure_lane(self, lane_id: str, capacity_per_minute: int) -> None:
        """Dynamically adjust lane capacity during runtime."""

        for lane in self._lanes:
            if lane.lane_id == lane_id:
                lane.capacity_per_minute = capacity_per_minute
                break
        self._telemetry.lane_utilization.setdefault(lane_id, 0.0)

    def telemetry(self) -> PlannerTelemetry:
        """Expose telemetry data for monitoring layers."""

        return self._telemetry

    def _update_telemetry(self, decision: SortingDecision, observation: MaterialObservation) -> None:
        utilization = self._telemetry.lane_utilization.get(decision.target_lane, 0.0)
        updated = 0.8 * utilization + 0.2 * observation.confidence
        self._telemetry.lane_utilization[decision.target_lane] = min(updated, 1.0)
        self._telemetry.contamination_routes[decision.target_lane] = observation.contamination_score

