# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
Ethos Core — Psi-Sleep Lifecycle (Cognitive Consolidation)
V2.76: Async Maintenance Daemon

Runs in the background. When Ethos is idle (no user interaction for X seconds),
it triggers identity reflection, distills the narrative chronicle, and optimizes memory.
This replaces the blocking "every 5 turns" reflection.
"""

from __future__ import annotations

import asyncio
import logging
import time

from src.core.identity import Identity
from src.core.llm import OllamaClient
from src.core.memory import Memory

_log = logging.getLogger(__name__)


class PsiSleepDaemon:
    """
    Background daemon that manages cognitive consolidation during idle periods.
    """

    def __init__(self, idle_threshold_seconds: int = 120):
        self.idle_threshold = idle_threshold_seconds
        self._last_activity = time.time()
        self._running = False
        self._task: asyncio.Task | None = None
        self._memory = Memory()
        self._identity = Identity()
        self._llm = OllamaClient()
        self._unreflected_turns = 0

    def note_activity(self) -> None:
        """Called by ChatEngine on every turn to reset the sleep timer."""
        self._last_activity = time.time()
        self._unreflected_turns += 1

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        _log.info(
            "[Psi-Sleep] Daemon started. Idle threshold: %ds", self.idle_threshold
        )

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        _log.info("[Psi-Sleep] Daemon stopped.")

    async def _loop(self) -> None:
        while self._running:
            await asyncio.sleep(10)
            now = time.time()
            idle_time = now - self._last_activity

            if idle_time >= self.idle_threshold and self._unreflected_turns >= 3:
                _log.info(
                    "[Psi-Sleep] Entering REM sleep (Idle for %.1fs, %d turns).",
                    idle_time,
                    self._unreflected_turns,
                )
                try:
                    # Trigger reflection and memory consolidation
                    await self._identity.reflect(self._memory, self._llm)
                    self._unreflected_turns = 0
                    _log.info("[Psi-Sleep] Waking up. Identity consolidated.")
                except Exception as e:
                    _log.error("[Psi-Sleep] Error during consolidation: %s", e)
