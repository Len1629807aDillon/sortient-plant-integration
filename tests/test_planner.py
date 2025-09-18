"""Tests for decision planner."""

from datetime import datetime, timezone

from plant_integration.data.structures import MaterialClass, MaterialObservation
from plant_integration.integration.planner import DecisionPlanner, LaneConfiguration


def test_planner_selects_supported_lane() -> None:
    lanes = [
        LaneConfiguration(lane_id="lane_a", supported_materials=["plastic"], capacity_per_minute=1000),
        LaneConfiguration(lane_id="lane_b", supported_materials=["glass"], capacity_per_minute=900),
    ]
    planner = DecisionPlanner(lanes)
    observation = MaterialObservation(
        observation_id="obs-1",
        timestamp=datetime.now(timezone.utc),
        material_class=MaterialClass.PLASTIC,
        confidence=0.95,
        contamination_score=0.05,
        location_coordinates={"x": 0.0, "y": 0.0, "z": 0.0},
    )
    decision = planner.plan(observation)
    assert decision.target_lane == "lane_a"
    assert decision.priority >= 1

