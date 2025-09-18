"""Digital twin simulation for AI-enabled recycling plants."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

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


class FacilitySimulator:
    """Creates a directed graph of facility segments and simulates material flow."""

    def __init__(self, segments: Iterable[ConveyorSegment]) -> None:
        self.graph = nx.DiGraph()
        for segment in segments:
            self.graph.add_node(
                segment.segment_id,
                length_m=segment.length_m,
                speed_mps=segment.speed_mps,
                capacity_items=segment.capacity_items,
            )
            for target in segment.connected_to:
                self.graph.add_edge(segment.segment_id, target)

    def simulate_step(self, loads: Dict[str, int], material: MaterialClass) -> FacilityState:
        """Simulate a single time step of material flow."""

        new_loads: Dict[str, int] = {}
        for node in self.graph.nodes:
            current_load = loads.get(node, 0)
            capacity = self.graph.nodes[node]["capacity_items"]
            throughput = min(current_load, capacity)
            neighbors = list(self.graph.successors(node))
            if not neighbors:
                new_loads[node] = throughput
                continue
            distribution = np.random.dirichlet(np.ones(len(neighbors)))
            for neighbor, ratio in zip(neighbors, distribution):
                amount = int(throughput * ratio)
                new_loads[neighbor] = new_loads.get(neighbor, 0) + amount
        energy = self._compute_energy(new_loads)
        recovery = self._estimate_recovery(material)
        return FacilityState(loads=new_loads, energy_consumption_kw=energy, recovery_rate=recovery)

    def _compute_energy(self, loads: Dict[str, int]) -> float:
        energy = 0.0
        for node, load in loads.items():
            length = self.graph.nodes[node]["length_m"]
            speed = self.graph.nodes[node]["speed_mps"]
            energy += 0.05 * load * length * speed
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

