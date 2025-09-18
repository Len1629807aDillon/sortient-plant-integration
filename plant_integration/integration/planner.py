"""Decision planning for AI-guided recycling plants."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import numpy as np

from ..data.structures import MaterialObservation, SortingDecision


@dataclass(slots=True)
class LaneConfiguration:
    """Configuration describing available sorting lanes."""

    lane_id: str
    supported_materials: List[str]
    capacity_per_minute: int


class DecisionPlanner:
    """Plan sorting decisions based on AI observations and lane capacities."""

    def __init__(self, lanes: Iterable[LaneConfiguration]) -> None:
        self._lanes = list(lanes)

    def plan(self, observation: MaterialObservation) -> SortingDecision:
        """Generate a :class:`SortingDecision` for a given observation."""

        lane_scores: List[float] = []
        for lane in self._lanes:
            support = 1.0 if observation.material_class.value in lane.supported_materials else 0.2
            capacity_factor = min(1.0, observation.confidence * lane.capacity_per_minute / 1000.0)
            lane_scores.append(0.7 * support + 0.3 * capacity_factor)
        index = int(np.argmax(lane_scores))
        lane = self._lanes[index]
        rationale = (
            f"Selected lane {lane.lane_id} for material {observation.material_class.value} "
            f"with score {lane_scores[index]:.3f}"
        )
        return SortingDecision(
            observation_id=observation.observation_id,
            target_lane=lane.lane_id,
            priority=int(np.clip(observation.confidence * 10, 1, 10)),
            confidence=float(lane_scores[index]),
            expected_actuator=f"actuator_{lane.lane_id}",
            rationale=rationale,
        )

