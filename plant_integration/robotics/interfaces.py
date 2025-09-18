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
    protocol: str
    latency_ms: float = 0.0
    dropped_messages: int = 0
    handshake_complete: bool = False


class RoboticsInterface(ABC):
    """Abstract interface for robotics backends."""

    def __init__(self, endpoint: str, namespace: str) -> None:
        self.endpoint = endpoint
        self.namespace = namespace
        self._state = ConnectionState(
            connected=False,
            last_heartbeat=None,
            metadata={},
            protocol=self.__class__.__name__,
        )

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

    def publish_diagnostics(self) -> None:
        """Emit human-readable diagnostics for the interface."""

        console.log(
            "[blue]robotics diagnostics[/blue]",
            {
                "endpoint": self.endpoint,
                "namespace": self.namespace,
                "protocol": self._state.protocol,
                "handshake_complete": self._state.handshake_complete,
                "latency_ms": round(self._state.latency_ms, 3),
                "dropped_messages": self._state.dropped_messages,
            },
        )

    @property
    def state(self) -> ConnectionState:
        """Retrieve connection state."""

        return self._state


class MockRos2Interface(RoboticsInterface):
    """Mock implementation that mimics ROS 2 messaging semantics."""

    def connect(self) -> None:
        console.log(f"[bold green]ROS2 interface connected to {self.endpoint}[/bold green]")
        self._state.connected = True
        self._state.handshake_complete = True
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
        self._state.latency_ms = 8.5
        self.heartbeat()

    def send_batch(self, commands: Iterable[RoboticsCommand]) -> None:
        for command in commands:
            self.send(command)


class MockOpcUaInterface(RoboticsInterface):
    """Mock interface simulating OPC UA method invocations."""

    def connect(self) -> None:
        console.log(f"[bold green]OPC UA session established with {self.endpoint}[/bold green]")
        self._state.connected = True
        self._state.handshake_complete = True
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
        self._state.latency_ms = 14.2
        self.heartbeat()

    def send_batch(self, commands: Iterable[RoboticsCommand]) -> None:
        for command in commands:
            self.send(command)


class MockEthercatInterface(RoboticsInterface):
    """Mock EtherCAT master that logs deterministic frame payloads."""

    def connect(self) -> None:
        console.log(
            f"[bold green]EtherCAT master online at {self.endpoint}[/bold green]"
        )
        self._state.connected = True
        self._state.handshake_complete = True
        self.heartbeat()

    def disconnect(self) -> None:
        console.log("[yellow]EtherCAT master offline[/yellow]")
        self._state.connected = False

    def send(self, command: RoboticsCommand) -> None:
        console.log(
            "[blue]EtherCAT frame[/blue]",
            json.dumps(
                {
                    "endpoint": self.endpoint,
                    "command": command.parameters,
                    "issued_at": command.issued_at.isoformat(),
                }
            ),
        )
        self._state.latency_ms = 3.1
        self.heartbeat()

    def send_batch(self, commands: Iterable[RoboticsCommand]) -> None:
        for command in commands:
            self.send(command)


class MockModbusTcpInterface(RoboticsInterface):
    """Mock Modbus TCP interface to emulate PLC register writes."""

    def connect(self) -> None:
        console.log(f"[bold green]Modbus TCP connected to {self.endpoint}[/bold green]")
        self._state.connected = True
        self._state.handshake_complete = True
        self.heartbeat()

    def disconnect(self) -> None:
        console.log("[yellow]Modbus TCP connection closed[/yellow]")
        self._state.connected = False

    def send(self, command: RoboticsCommand) -> None:
        console.log(
            "[green]Modbus write[/green]",
            json.dumps(
                {
                    "endpoint": self.endpoint,
                    "parameters": command.parameters,
                    "actuator": command.actuator_id,
                }
            ),
        )
        self._state.latency_ms = 6.8
        self.heartbeat()

    def send_batch(self, commands: Iterable[RoboticsCommand]) -> None:
        for command in commands:
            self.send(command)


class MockFanucPcdkInterface(RoboticsInterface):
    """Mock Fanuc PCDK client emitting motion program calls."""

    def connect(self) -> None:
        console.log(
            f"[bold green]Fanuc PCDK session created for {self.endpoint}[/bold green]"
        )
        self._state.connected = True
        self._state.handshake_complete = True
        self.heartbeat()

    def disconnect(self) -> None:
        console.log("[yellow]Fanuc PCDK session terminated[/yellow]")
        self._state.connected = False

    def send(self, command: RoboticsCommand) -> None:
        console.log(
            "[purple]Fanuc program call[/purple]",
            json.dumps(
                {
                    "endpoint": self.endpoint,
                    "program": command.parameters.get("payload", {}).get("program"),
                    "arguments": command.parameters.get("payload", {}).get("arguments"),
                }
            ),
        )
        self._state.latency_ms = 22.5
        self.heartbeat()

    def send_batch(self, commands: Iterable[RoboticsCommand]) -> None:
        for command in commands:
            self.send(command)


class RoboticsInterfaceFactory:
    """Factory creating robotics interfaces based on protocol string."""

    _registry = {
        "ros2": MockRos2Interface,
        "opc_ua": MockOpcUaInterface,
        "ethercat": MockEthercatInterface,
        "modbus_tcp": MockModbusTcpInterface,
        "fanuc_pcdk": MockFanucPcdkInterface,
    }

    @classmethod
    def create(cls, protocol: str, endpoint: str, namespace: str) -> RoboticsInterface:
        try:
            impl = cls._registry[protocol]
        except KeyError as exc:
            raise ValueError(f"Unsupported robotics protocol: {protocol}") from exc
        return impl(endpoint=endpoint, namespace=namespace)

