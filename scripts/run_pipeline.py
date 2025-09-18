"""Command-line entry point to run the Sortient plant integration pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import numpy as np
import typer
from rich.console import Console

from plant_integration.ai.detector import MaterialDetector
from plant_integration.config import IntegrationConfig
from plant_integration.data.structures import MaterialClass
from plant_integration.integration.planner import DecisionPlanner, LaneConfiguration
from plant_integration.pipeline.controller import IntegrationController
from plant_integration.simulation.facility import ConveyorSegment, FacilitySimulator

app = typer.Typer(help="Run the Sortient integration pipeline with simulated inputs.")
console = Console()


def _load_detector(model_path: Path) -> MaterialDetector:
    if model_path.exists():
        return MaterialDetector.load(model_path)
    console.log("[yellow]Model not found, training synthetic detector[/yellow]")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)
    samples = rng.normal(loc=0.5, scale=0.2, size=(500, 6))
    labels = rng.choice(["plastic", "glass", "metal", "paper"], size=500)
    detector = MaterialDetector.from_training_data(samples, labels.tolist())
    detector.save(model_path)
    return detector


@app.command()
def run(
    config_path: Path = typer.Argument(..., exists=True, help="Path to integration config YAML"),
    model_path: Path = typer.Option(Path("artifacts/model.npz"), help="Path to the detector model"),
    iterations: Optional[int] = typer.Option(None, help="Number of events to process"),
) -> None:
    """Run the integration pipeline."""

    config = IntegrationConfig.from_yaml(config_path)
    detector = _load_detector(model_path)
    lanes = [
        LaneConfiguration(
            lane_id="lane_a",
            supported_materials=["plastic", "paper"],
            capacity_per_minute=1800,
            contamination_tolerance=0.12,
        ),
        LaneConfiguration(
            lane_id="lane_b",
            supported_materials=["glass", "metal"],
            capacity_per_minute=1400,
            contamination_tolerance=0.08,
        ),
        LaneConfiguration(
            lane_id="lane_c",
            supported_materials=["organic"],
            capacity_per_minute=800,
            contamination_tolerance=0.25,
        ),
    ]
    planner = DecisionPlanner(lanes)
    controller = IntegrationController(config=config, detector=detector, planner=planner)
    controller.startup()
    try:
        events = controller.ingest_stream()
        controller.run(events, limit=iterations)
    finally:
        controller.shutdown()
    if config.digital_twin.enabled:
        _run_digital_twin_simulation(config)


@app.command()
def describe_config(config_path: Path) -> None:
    """Pretty-print integration configuration."""

    config = IntegrationConfig.from_yaml(config_path)
    console.print_json(data=json.loads(json.dumps(config.to_dict())))


def _default_segments() -> list[ConveyorSegment]:
    return [
        ConveyorSegment(
            segment_id="intake",
            length_m=6.0,
            speed_mps=1.3,
            capacity_items=220,
            connected_to=["pre_sort"],
        ),
        ConveyorSegment(
            segment_id="pre_sort",
            length_m=4.5,
            speed_mps=1.1,
            capacity_items=180,
            connected_to=["optical", "bypass"],
        ),
        ConveyorSegment(
            segment_id="optical",
            length_m=3.0,
            speed_mps=0.9,
            capacity_items=140,
            connected_to=["plastic_output"],
        ),
        ConveyorSegment(
            segment_id="bypass",
            length_m=2.5,
            speed_mps=0.7,
            capacity_items=90,
            connected_to=["residue"],
        ),
        ConveyorSegment(
            segment_id="plastic_output",
            length_m=2.8,
            speed_mps=0.85,
            capacity_items=110,
            connected_to=[],
        ),
        ConveyorSegment(
            segment_id="residue",
            length_m=2.0,
            speed_mps=0.6,
            capacity_items=80,
            connected_to=[],
        ),
    ]


def _run_digital_twin_simulation(config: IntegrationConfig) -> None:
    console.rule("Digital Twin Simulation")
    simulator = FacilitySimulator(
        _default_segments(), energy_coefficient=config.digital_twin.energy_coefficient_kw_per_item
    )
    report = simulator.simulate(
        initial_loads={"intake": 200},
        material=MaterialClass.PLASTIC,
        steps=5,
        export_path=config.digital_twin.export_path,
    )
    console.log(
        "[green]Simulation complete[/green]",
        {
            "average_energy_kw": round(report.average_energy_kw, 3),
            "average_recovery_rate": round(report.average_recovery_rate, 3),
        },
    )


@app.command()
def simulate(
    steps: int = typer.Option(5, help="Number of simulation steps"),
    material: MaterialClass = typer.Option(MaterialClass.PLASTIC, help="Material class to simulate"),
    export_path: Path = typer.Option(Path("artifacts/manual_simulation.json"), help="Where to export the report"),
) -> None:
    """Run the digital twin simulator without starting the full pipeline."""

    simulator = FacilitySimulator(_default_segments())
    report = simulator.simulate(
        initial_loads={"intake": 180}, material=material, steps=steps, export_path=export_path
    )
    console.log(
        "[blue]Simulation summary[/blue]",
        {
            "average_energy_kw": round(report.average_energy_kw, 3),
            "average_recovery_rate": round(report.average_recovery_rate, 3),
        },
    )


if __name__ == "__main__":
    app()

