"""Sensor adapter seam (SP-P1-01): vendor-agnostic SensorSnapshot read."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.modules.sensor_contracts import SensorSnapshot


class SensorAdapter(ABC):
    """Minimal interface for pre-perception sensor fusion (no transport coupling)."""

    @abstractmethod
    def read_snapshot(self) -> SensorSnapshot:
        """Return current multimodal hints; empty snapshot when unavailable."""


class StubSensorAdapter(SensorAdapter):
    """Deterministic CI double: no sensor signal."""

    def read_snapshot(self) -> SensorSnapshot:
        return SensorSnapshot()


class FixedSensorAdapter(SensorAdapter):
    """Test double with a fixed snapshot."""

    def __init__(self, snapshot: SensorSnapshot) -> None:
        self._snapshot = snapshot

    def read_snapshot(self) -> SensorSnapshot:
        return self._snapshot
