import asyncio
import logging
from typing import Any

_log = logging.getLogger(__name__)


class ReactionTable:
    """
    Manages pending stimuli-to-reaction futures for the distributed nervous system.
    Part of the 'Obliteración del Monolito' (Tarea 19.3).
    """

    def __init__(self):
        self._pending: dict[str, asyncio.Future] = {}

    def register(self, pulse_id: str) -> asyncio.Future:
        """Create a future for a specific sensory stimulus."""
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._pending[pulse_id] = future
        return future

    def resolve(self, ref_id: str, result: Any) -> bool:
        """Resolve a future with the resulting motor command."""
        if ref_id in self._pending:
            future = self._pending[ref_id]
            if not future.done():
                future.set_result(result)
                return True
        return False

    def clear(self, pulse_id: str):
        """Remove a pulse from the table (cleanup)."""
        self._pending.pop(pulse_id, None)

    def __len__(self):
        return len(self._pending)
