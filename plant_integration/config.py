"""Configuration utilities for the Sortient plant integration stack."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass(slots=True)
class DataIngestionConfig:
    """Configuration for material flow ingestion."""

    source: str
    refresh_interval_ms: int = 100
    max_batch_size: int = 1024
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class RoboticsInterfaceConfig:
    """Configuration for robotics connectivity."""

    protocol: str
    endpoint: str
    namespace: str = "sortient"
    max_queue_size: int = 5000
    safety_stop_topic: Optional[str] = None
    allowed_joint_ranges: Dict[str, List[float]] = field(default_factory=dict)


@dataclass(slots=True)
class IntegrationConfig:
    """Top-level configuration for the integration controller."""

    plant_id: str
    data_ingestion: DataIngestionConfig
    robotics: RoboticsInterfaceConfig
    enable_predictive_maintenance: bool = True
    enable_closed_loop_control: bool = True
    enable_realtime_dashboard: bool = True
    materials_catalog: Optional[Path] = None

    @classmethod
    def from_yaml(cls, path: Path) -> "IntegrationConfig":
        """Load an :class:`IntegrationConfig` instance from a YAML file."""

        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        data_ingestion = DataIngestionConfig(**data["data_ingestion"])
        robotics = RoboticsInterfaceConfig(**data["robotics"])
        return cls(
            plant_id=data["plant_id"],
            data_ingestion=data_ingestion,
            robotics=robotics,
            enable_predictive_maintenance=data.get("enable_predictive_maintenance", True),
            enable_closed_loop_control=data.get("enable_closed_loop_control", True),
            enable_realtime_dashboard=data.get("enable_realtime_dashboard", True),
            materials_catalog=Path(data["materials_catalog"]) if data.get("materials_catalog") else None,
        )

    def to_dict(self) -> Dict[str, object]:
        """Serialize the configuration into a JSON-compatible dictionary."""

        return {
            "plant_id": self.plant_id,
            "data_ingestion": self.data_ingestion.__dict__,
            "robotics": self.robotics.__dict__,
            "enable_predictive_maintenance": self.enable_predictive_maintenance,
            "enable_closed_loop_control": self.enable_closed_loop_control,
            "enable_realtime_dashboard": self.enable_realtime_dashboard,
            "materials_catalog": str(self.materials_catalog) if self.materials_catalog else None,
        }

