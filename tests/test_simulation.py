"""Tests for the facility simulator."""

from pathlib import Path

from plant_integration.data.structures import MaterialClass
from plant_integration.simulation.facility import (
    ConveyorSegment,
    FacilitySimulator,
)


def _segments() -> list[ConveyorSegment]:
    return [
        ConveyorSegment(
            segment_id="infeed",
            length_m=5.0,
            speed_mps=1.2,
            capacity_items=200,
            connected_to=["sorter"],
        ),
        ConveyorSegment(
            segment_id="sorter",
            length_m=4.0,
            speed_mps=1.0,
            capacity_items=150,
            connected_to=["output_a", "output_b"],
        ),
        ConveyorSegment(
            segment_id="output_a",
            length_m=3.0,
            speed_mps=0.8,
            capacity_items=120,
            connected_to=[],
        ),
        ConveyorSegment(
            segment_id="output_b",
            length_m=3.5,
            speed_mps=0.9,
            capacity_items=110,
            connected_to=[],
        ),
    ]


def test_simulation_report_export(tmp_path: Path) -> None:
    simulator = FacilitySimulator(_segments(), energy_coefficient=0.04)
    report_path = tmp_path / "report.json"
    report = simulator.simulate({"infeed": 180}, MaterialClass.PLASTIC, steps=3, export_path=report_path)
    assert report.average_energy_kw > 0
    assert report_path.exists()


def test_simulation_throughput_stats() -> None:
    simulator = FacilitySimulator(_segments())
    report = simulator.simulate({"infeed": 200}, MaterialClass.METAL, steps=2)
    assert "infeed" in report.throughput_per_segment
    assert report.throughput_per_segment["infeed"] >= 0
