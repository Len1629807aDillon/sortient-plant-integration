"""Data structures describing material flow and system events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class MaterialClass(str, Enum):
    """Enumerate supported material classes."""

    PLASTIC = "plastic"
    GLASS = "glass"
    METAL = "metal"
    PAPER = "paper"
    ORGANIC = "organic"
    E_WASTE = "e_waste"
    TEXTILE = "textile"
    INERT = "inert"


@dataclass(slots=True)
class MaterialObservation:
    """Single material detection record produced by the AI stack."""

    observation_id: str
    timestamp: datetime
    material_class: MaterialClass
    confidence: float
    contamination_score: float
    location_coordinates: Dict[str, float]
    spectral_signature: List[float] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class SortingDecision:
    """Decision describing where a material should be directed."""

    observation_id: str
    target_lane: str
    priority: int
    confidence: float
    expected_actuator: str
    rationale: str


@dataclass(slots=True)
class RoboticsCommand:
    """Instruction for a robotic actuator compatible with industry standards."""

    actuator_id: str
    command_type: str
    parameters: Dict[str, object]
    issued_at: datetime
    correlation_id: Optional[str] = None
    requires_ack: bool = True


@dataclass(slots=True)
class IntegrationEvent:
    """General event propagated through the integration pipeline."""

    event_type: str
    payload: Dict[str, object]
    created_at: datetime = field(default_factory=datetime.utcnow)

