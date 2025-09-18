"""Tests for analytics helpers."""

from plant_integration.analytics.metrics import (
    OeeBreakdown,
    ThroughputWindow,
    compute_oee_breakdown,
    recommend_maintenance,
    throughput_trend,
)


def test_throughput_trend_positive() -> None:
    window = ThroughputWindow(timestamps=[0, 1, 2], counts=[100, 120, 150])
    trend = throughput_trend(window)
    assert trend > 0


def test_oee_breakdown_contains_components() -> None:
    breakdown = compute_oee_breakdown(0.9, 0.95, 0.97)
    assert isinstance(breakdown, OeeBreakdown)
    assert round(breakdown.oee, 3) == round(0.9 * 0.95 * 0.97, 3)


def test_recommend_maintenance_filters_threshold() -> None:
    telemetry = {"actuator_1": 8.0, "actuator_2": 2.0}
    recommendations = recommend_maintenance(telemetry, threshold=0.3)
    assert any(rec.component_id == "actuator_1" for rec in recommendations)
    assert all(rec.failure_probability >= 0.3 for rec in recommendations)
