"""Abstractions for connecting to industrial robotics systems."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, Optional

from rich.console import Console

from ..data.structures import RoboticsCommand

console = Console()


@dataclass(slots=True)
class ConnectionState:
    """Represents the state of a robotics connection."""

    connected: bool
    last_heartbeat: Optional[datetime]
    metadata: Dict[str, str]


class RoboticsInterface(ABC):
    """Abstract interface for robotics backends."""

    def __init__(self, endpoint: str, namespace: str) -> None:
        self.endpoint = endpoint
        self.namespace = namespace
        self._state = ConnectionState(connected=False, last_heartbeat=None, metadata={})

    @abstractmethod
    def connect(self) -> None:
        ...

    @abstractmethod
    def disconnect(self) -> None:
        ...

    @abstractmethod
    def send(self, command: RoboticsCommand) -> None:
        ...

    @abstractmethod
    def send_batch(self, commands: Iterable[RoboticsCommand]) -> None:
        ...

    def heartbeat(self) -> None:
        """Update connection heartbeat."""

        self._state.last_heartbeat = datetime.utcnow()

    @property
    def state(self) -> ConnectionState:
        """Retrieve connection state."""

        return self._state


class MockRos2Interface(RoboticsInterface):
    """Mock implementation that mimics ROS2 messaging semantics."""

    def connect(self) -> None:
        console.log(f"[bold green]ROS2 interface connected to {self.endpoint}[/bold green]")
        self._state.connected = True
        self.heartbeat()

    def disconnect(self) -> None:
        console.log("[yellow]ROS2 interface disconnected[/yellow]")
        self._state.connected = False

    def send(self, command: RoboticsCommand) -> None:
        console.log(
            "[cyan]ROS2 publish[/cyan]",
            json.dumps({
                "namespace": self.namespace,
                "endpoint": self.endpoint,
                "command": command.__dict__,
            }, default=str),
        )
        self.heartbeat()

    def send_batch(self, commands: Iterable[RoboticsCommand]) -> None:
        for command in commands:
            self.send(command)


class MockOpcUaInterface(RoboticsInterface):
    """Mock interface simulating OPC UA method invocations."""

    def connect(self) -> None:
        console.log(f"[bold green]OPC UA session established with {self.endpoint}[/bold green]")
        self._state.connected = True
        self.heartbeat()

    def disconnect(self) -> None:
        console.log("[yellow]OPC UA session closed[/yellow]")
        self._state.connected = False

    def send(self, command: RoboticsCommand) -> None:
        console.log(
            "[magenta]OPC UA call[/magenta]",
            json.dumps({
                "namespace": self.namespace,
                "endpoint": self.endpoint,
                "command": command.__dict__,
            }, default=str),
        )
        self.heartbeat()

    def send_batch(self, commands: Iterable[RoboticsCommand]) -> None:
        for command in commands:
            self.send(command)


class RoboticsInterfaceFactory:
    """Factory creating robotics interfaces based on protocol string."""

    _registry = {
        "ros2": MockRos2Interface,
        "opc_ua": MockOpcUaInterface,
    }

    @classmethod
    def create(cls, protocol: str, endpoint: str, namespace: str) -> RoboticsInterface:
        try:
            impl = cls._registry[protocol]
        except KeyError as exc:
            raise ValueError(f"Unsupported robotics protocol: {protocol}") from exc
        return impl(endpoint=endpoint, namespace=namespace)

