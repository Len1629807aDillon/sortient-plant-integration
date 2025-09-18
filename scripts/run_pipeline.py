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
from plant_integration.integration.planner import DecisionPlanner, LaneConfiguration
from plant_integration.pipeline.controller import IntegrationController

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
        LaneConfiguration(lane_id="lane_a", supported_materials=["plastic", "paper"], capacity_per_minute=1800),
        LaneConfiguration(lane_id="lane_b", supported_materials=["glass", "metal"], capacity_per_minute=1400),
        LaneConfiguration(lane_id="lane_c", supported_materials=["organic"], capacity_per_minute=800),
    ]
    planner = DecisionPlanner(lanes)
    controller = IntegrationController(config=config, detector=detector, planner=planner)
    controller.startup()
    try:
        events = controller.ingest_stream()
        controller.run(events, limit=iterations)
    finally:
        controller.shutdown()


@app.command()
def describe_config(config_path: Path) -> None:
    """Pretty-print integration configuration."""

    config = IntegrationConfig.from_yaml(config_path)
    console.print_json(data=json.loads(json.dumps(config.to_dict())))


if __name__ == "__main__":
    app()

