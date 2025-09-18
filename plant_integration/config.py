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
class RoboticsSafetyConfig:
    """Safety envelope for robotics communication and execution."""

    handshake_required: bool = True
    handshake_timeout_s: float = 2.0
    emergency_stop_topic: Optional[str] = None
    max_payload_kg: float = 25.0
    keepout_zones: List[Dict[str, float]] = field(default_factory=list)
    allowed_joint_ranges: Dict[str, List[float]] = field(default_factory=dict)


@dataclass(slots=True)
class RoboticsQoSConfig:
    """Quality-of-service settings for outbound robotics commands."""

    max_queue_size: int = 5000
    heartbeat_interval_s: float = 0.5
    ack_timeout_s: float = 1.5
    retry_attempts: int = 3
    jitter_tolerance_ms: int = 20


@dataclass(slots=True)
class RoboticsInterfaceConfig:
    """Configuration for robotics connectivity."""

    protocol: str
    endpoint: str
    namespace: str = "sortient"
    qos: RoboticsQoSConfig = field(default_factory=RoboticsQoSConfig)
    safety: RoboticsSafetyConfig = field(default_factory=RoboticsSafetyConfig)


@dataclass(slots=True)
class DigitalTwinConfig:
    """Configuration for facility digital twin simulations."""

    enabled: bool = False
    default_speed_mps: float = 1.5
    energy_coefficient_kw_per_item: float = 0.05
    export_path: Optional[Path] = None


@dataclass(slots=True)
class AnalyticsConfig:
    """Configuration toggles for analytics subsystems."""

    enable_oee_tracking: bool = True
    enable_predictive_maintenance: bool = True
    enable_prometheus_export: bool = False
    sliding_window_minutes: int = 10


@dataclass(slots=True)
class IntegrationConfig:
    """Top-level configuration for the integration controller."""

    plant_id: str
    data_ingestion: DataIngestionConfig
    robotics: RoboticsInterfaceConfig
    analytics: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    digital_twin: DigitalTwinConfig = field(default_factory=DigitalTwinConfig)
    materials_catalog: Optional[Path] = None

    @classmethod
    def from_yaml(cls, path: Path) -> "IntegrationConfig":
        """Load an :class:`IntegrationConfig` instance from a YAML file."""

        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)

        base_dir = path.parent

        data_ingestion = DataIngestionConfig(**data["data_ingestion"])

        safety_data = data.get("robotics", {}).get("safety", {})
        qos_data = data.get("robotics", {}).get("qos", {})
        robotics = RoboticsInterfaceConfig(
            protocol=data["robotics"]["protocol"],
            endpoint=data["robotics"]["endpoint"],
            namespace=data["robotics"].get("namespace", "sortient"),
            qos=RoboticsQoSConfig(**qos_data) if qos_data else RoboticsQoSConfig(),
            safety=RoboticsSafetyConfig(**safety_data) if safety_data else RoboticsSafetyConfig(),
        )

        analytics_data = data.get("analytics", {})
        analytics = AnalyticsConfig(**analytics_data) if analytics_data else AnalyticsConfig()

        twin_data = data.get("digital_twin", {})
        export_path = twin_data.get("export_path")
        if export_path:
            export_path = Path(export_path)
            if not export_path.is_absolute():
                export_path = (base_dir / export_path).resolve()
        digital_twin = (
            DigitalTwinConfig(
                enabled=twin_data.get("enabled", False),
                default_speed_mps=twin_data.get("default_speed_mps", 1.5),
                energy_coefficient_kw_per_item=twin_data.get("energy_coefficient_kw_per_item", 0.05),
                export_path=export_path,
            )
            if twin_data
            else DigitalTwinConfig()
        )

        catalog_path = data.get("materials_catalog")
        if catalog_path:
            catalog_path = Path(catalog_path)
            if not catalog_path.is_absolute():
                catalog_path = (base_dir / catalog_path).resolve()

        config = cls(
            plant_id=data["plant_id"],
            data_ingestion=data_ingestion,
            robotics=robotics,
            analytics=analytics,
            digital_twin=digital_twin,
            materials_catalog=catalog_path,
        )
        config.validate()
        return config

    def validate(self) -> None:
        """Perform defensive validation of the configuration envelope."""

        if self.robotics.safety.handshake_required and self.robotics.safety.handshake_timeout_s <= 0:
            raise ValueError("Handshake timeout must be positive when handshake is required")
        if self.robotics.qos.max_queue_size <= 0:
            raise ValueError("Robotics QoS queue size must be positive")
        if self.analytics.sliding_window_minutes <= 0:
            raise ValueError("Analytics sliding window must be positive")
        if self.digital_twin.default_speed_mps <= 0:
            raise ValueError("Digital twin conveyor speed must be positive")
        if self.digital_twin.energy_coefficient_kw_per_item <= 0:
            raise ValueError("Digital twin energy coefficient must be positive")
        if self.materials_catalog and not self.materials_catalog.exists():
            raise FileNotFoundError(
                f"Materials catalog {self.materials_catalog} does not exist"
            )

    def to_dict(self) -> Dict[str, object]:
        """Serialize the configuration into a JSON-compatible dictionary."""

        return {
            "plant_id": self.plant_id,
            "data_ingestion": self.data_ingestion.__dict__,
            "robotics": {
                "protocol": self.robotics.protocol,
                "endpoint": self.robotics.endpoint,
                "namespace": self.robotics.namespace,
                "qos": self.robotics.qos.__dict__,
                "safety": self.robotics.safety.__dict__,
            },
            "analytics": self.analytics.__dict__,
            "digital_twin": {
                "enabled": self.digital_twin.enabled,
                "default_speed_mps": self.digital_twin.default_speed_mps,
                "energy_coefficient_kw_per_item": self.digital_twin.energy_coefficient_kw_per_item,
                "export_path": str(self.digital_twin.export_path) if self.digital_twin.export_path else None,
            },
            "materials_catalog": str(self.materials_catalog) if self.materials_catalog else None,
        }

