"""Injection port for checkpoint persistence (JSON file, SQLite, or test doubles)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.kernel import EthicalKernel


class CheckpointPersistencePort(Protocol):
    """Load/save kernel snapshots without tying callers to a concrete store."""

    def load_into_kernel(self, kernel: EthicalKernel) -> bool:
        """Apply stored state to ``kernel``. Return True if a snapshot was applied."""
        ...

    def save_from_kernel(self, kernel: EthicalKernel) -> bool:
        """Persist current ``kernel`` state. Return True on success."""
        ...
