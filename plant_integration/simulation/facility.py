"""Digital twin simulation for AI-enabled recycling plants."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import networkx as nx
import numpy as np

from ..data.structures import MaterialClass


@dataclass(slots=True)
class ConveyorSegment:
    """Represents a conveyor segment in the digital twin graph."""

    segment_id: str
    length_m: float
    speed_mps: float
    capacity_items: int
    connected_to: List[str]


@dataclass(slots=True)
class FacilityState:
    """Represents the current state of the simulated facility."""

    loads: Dict[str, int]
    energy_consumption_kw: float
    recovery_rate: float


@dataclass(slots=True)
class SimulationSnapshot:
    """Snapshot for a single timestep in the simulation."""

    step: int
    loads: Dict[str, int]
    energy_kw: float
    recovery_rate: float


@dataclass(slots=True)
class SimulationReport:
    """Aggregate view of a multi-step facility simulation."""

    snapshots: List[SimulationSnapshot]
    average_energy_kw: float
    average_recovery_rate: float
    throughput_per_segment: Dict[str, float] = field(default_factory=dict)


class FacilitySimulator:
    """Creates a directed graph of facility segments and simulates material flow."""

    def __init__(self, segments: Iterable[ConveyorSegment], energy_coefficient: float = 0.05) -> None:
        self.graph = nx.DiGraph()
        self.energy_coefficient = energy_coefficient
        for segment in segments:
            self.graph.add_node(
                segment.segment_id,
                length_m=segment.length_m,
                speed_mps=segment.speed_mps,
                capacity_items=segment.capacity_items,
            )
            for target in segment.connected_to:
                self.graph.add_edge(segment.segment_id, target)

    def simulate_step(
        self, loads: Dict[str, int], material: MaterialClass, *, rng: Optional[np.random.Generator] = None
    ) -> FacilityState:
        """Simulate a single time step of material flow."""

        rng = rng or np.random.default_rng()
        new_loads: Dict[str, int] = {}
        for node in self.graph.nodes:
            current_load = loads.get(node, 0)
            capacity = self.graph.nodes[node]["capacity_items"]
            throughput = min(current_load, capacity)
            neighbors = list(self.graph.successors(node))
            if not neighbors:
                new_loads[node] = throughput
                continue
            distribution = rng.dirichlet(np.ones(len(neighbors)))
            for neighbor, ratio in zip(neighbors, distribution):
                amount = int(throughput * ratio)
                new_loads[neighbor] = new_loads.get(neighbor, 0) + amount
        energy = self._compute_energy(new_loads)
        recovery = self._estimate_recovery(material)
        return FacilityState(loads=new_loads, energy_consumption_kw=energy, recovery_rate=recovery)

    def simulate(
        self,
        initial_loads: Dict[str, int],
        material: MaterialClass,
        steps: int = 10,
        export_path: Optional[Path] = None,
    ) -> SimulationReport:
        """Run a multi-step simulation and optionally export the report."""

        if steps <= 0:
            raise ValueError("Simulation steps must be positive")

        snapshots: List[SimulationSnapshot] = []
        loads = dict(initial_loads)
        rng = np.random.default_rng(42)
        for step in range(steps):
            state = self.simulate_step(loads, material, rng=rng)
            snapshots.append(
                SimulationSnapshot(
                    step=step,
                    loads=state.loads,
                    energy_kw=state.energy_consumption_kw,
                    recovery_rate=state.recovery_rate,
                )
            )
            loads = state.loads
        average_energy = float(np.mean([snap.energy_kw for snap in snapshots])) if snapshots else 0.0
        average_recovery = float(np.mean([snap.recovery_rate for snap in snapshots])) if snapshots else 0.0
        throughput_per_segment = self._compute_throughput_statistics(snapshots)
        report = SimulationReport(
            snapshots=snapshots,
            average_energy_kw=average_energy,
            average_recovery_rate=average_recovery,
            throughput_per_segment=throughput_per_segment,
        )
        if export_path:
            self._export_report(report, export_path)
        return report

    def _compute_energy(self, loads: Dict[str, int]) -> float:
        energy = 0.0
        for node, load in loads.items():
            length = self.graph.nodes[node]["length_m"]
            speed = self.graph.nodes[node]["speed_mps"]
            energy += self.energy_coefficient * load * length * speed
        return energy

    def _estimate_recovery(self, material: MaterialClass) -> float:
        base = {
            MaterialClass.PLASTIC: 0.94,
            MaterialClass.GLASS: 0.91,
            MaterialClass.METAL: 0.97,
            MaterialClass.PAPER: 0.89,
            MaterialClass.ORGANIC: 0.75,
        }.get(material, 0.65)
        return float(np.clip(np.random.normal(base, 0.02), 0.5, 0.99))

    def _compute_throughput_statistics(self, snapshots: List[SimulationSnapshot]) -> Dict[str, float]:
        throughput: Dict[str, List[int]] = {node: [] for node in self.graph.nodes}
        for snapshot in snapshots:
            for node, load in snapshot.loads.items():
                throughput[node].append(load)
        return {
            node: float(np.mean(values)) if values else 0.0 for node, values in throughput.items()
        }

    def _export_report(self, report: SimulationReport, export_path: Path) -> None:
        export_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "average_energy_kw": report.average_energy_kw,
            "average_recovery_rate": report.average_recovery_rate,
            "throughput_per_segment": report.throughput_per_segment,
            "snapshots": [
                {
                    "step": snap.step,
                    "loads": snap.loads,
                    "energy_kw": snap.energy_kw,
                    "recovery_rate": snap.recovery_rate,
                }
                for snap in report.snapshots
            ],
        }
        export_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

