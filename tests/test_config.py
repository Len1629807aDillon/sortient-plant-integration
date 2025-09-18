"""Tests for configuration loading."""

from pathlib import Path

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
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content)
    config = IntegrationConfig.from_yaml(config_file)
    assert config.plant_id == "demo"
    assert config.robotics.protocol == "ros2"
    assert config.data_ingestion.max_batch_size == 128

