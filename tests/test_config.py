"""Tests for configuration loading."""

from pathlib import Path

import pytest

from plant_integration.config import IntegrationConfig


def test_load_from_yaml(tmp_path: Path) -> None:
    yaml_content = """
plant_id: demo
data_ingestion:
  source: stream
  refresh_interval_ms: 100
  max_batch_size: 128
robotics:
  protocol: ros2
  endpoint: ws://localhost:9090
  namespace: sortient/test
  qos:
    max_queue_size: 3200
    heartbeat_interval_s: 0.4
  safety:
    handshake_required: true
    handshake_timeout_s: 2.2
analytics:
  enable_oee_tracking: false
digital_twin:
  enabled: true
  default_speed_mps: 1.7
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content)
    config = IntegrationConfig.from_yaml(config_file)
    assert config.plant_id == "demo"
    assert config.robotics.protocol == "ros2"
    assert config.data_ingestion.max_batch_size == 128
    assert config.robotics.qos.max_queue_size == 3200
    assert config.analytics.enable_oee_tracking is False
    assert config.digital_twin.enabled is True


def test_materials_catalog_resolves_relative_path(tmp_path: Path) -> None:
    catalog = tmp_path / "materials_catalog.csv"
    catalog.write_text("material,category\nplastic,polymer\n")
    yaml_content = f"""
plant_id: demo
data_ingestion:
  source: stream
  refresh_interval_ms: 100
  max_batch_size: 128
robotics:
  protocol: ros2
  endpoint: ws://localhost:9090
digital_twin:
  enabled: false
materials_catalog: "materials_catalog.csv"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content)
    config = IntegrationConfig.from_yaml(config_file)
    assert config.materials_catalog == catalog


def test_missing_materials_catalog_raises(tmp_path: Path) -> None:
    yaml_content = """
plant_id: demo
data_ingestion:
  source: stream
  refresh_interval_ms: 100
  max_batch_size: 128
robotics:
  protocol: ros2
  endpoint: ws://localhost:9090
digital_twin:
  enabled: false
materials_catalog: "missing.csv"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content)
    with pytest.raises(FileNotFoundError):
        IntegrationConfig.from_yaml(config_file)

