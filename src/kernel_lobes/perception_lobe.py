from __future__ import annotations

import asyncio
import logging
import math
import os
import threading
import time
import urllib.error
import urllib.request
from typing import TYPE_CHECKING, Any, Optional

from src.kernel_lobes.models import SemanticState, TimeoutTrauma

if TYPE_CHECKING:
    from src.modules.sensor_contracts import SensorSnapshot
    from src.modules.safety_interlock import SafetyInterlock
    from src.modules.strategy_engine import ExecutiveStrategist

_log = logging.getLogger(__name__)


class PerceptiveLobe:
    """
    Subsystem for Safety Interlocks, Strategic Ingestion, and Multimodal Perception.

    Acts as the 'Left Hemisphere' of the kernel, handling I/O and sensory filtering.
    """

    def __init__(
        self,
        safety_interlock: Optional["SafetyInterlock"] = None,
        strategist: Optional["ExecutiveStrategist"] = None,
        llm_backend: Optional[Any] = None,
    ) -> None:
        if safety_interlock is None:
            from src.modules.safety_interlock import SafetyInterlock

            safety_interlock = SafetyInterlock()
        if strategist is None:
            from src.modules.strategy_engine import ExecutiveStrategist

            strategist = ExecutiveStrategist()
        self.safety_interlock = safety_interlock
        self.strategist = strategist
        self.llm_backend = llm_backend  # For semantic perception if needed

    def execute_stage(
        self,
        scenario: str,
        place: str,
        context: str,
        sensor_snapshot: Optional[SensorSnapshot] = None,
        interrupt_event: Optional[threading.Event] = None,
    ) -> dict[str, Any]:
        """
        STAGE 0: Perception, Safety and Strategic Ingestion.
        """
        # 0.0 Somatic Overrides (Vertical Increment)
        if interrupt_event and interrupt_event.is_set():
            # In production, we would fetch details from CerebellumNode
            return {
                "safety_decision": None,  # Will be handled by state change
                "mission_updated": False,
                "somatic_interrupt": True,
            }

        # 0.1 Check Safety
        safety_dec = self.safety_interlock.evaluate(scenario, place, context)

        # 0.2 Strategic Ingestion
        if sensor_snapshot:
            # Mission updates
            if sensor_snapshot.external_mission_title:
                from src.modules.strategy_engine import MissionOrigin

                self.strategist.create_mission(
                    title=sensor_snapshot.external_mission_title,
                    origin=MissionOrigin.OWNER,
                    steps=sensor_snapshot.external_mission_steps or [],
                    priority=sensor_snapshot.external_mission_priority or 0.6,
                )
            # Generic sensor ingestion for heuristic updates
            self.strategist.ingest_sensors(sensor_snapshot)

        return {
            "safety_decision": safety_dec,
            "mission_updated": bool(
                sensor_snapshot and getattr(sensor_snapshot, "external_mission_title", None)
            ),
        }

    def _probe_sync(self, url: str, timeout_s: float) -> None:
        urllib.request.urlopen(url, timeout=timeout_s)  # noqa: S310 — lab-only optional probe

    async def aclose(self) -> None:
        """
        Best-effort teardown (``CorpusCallosumOrchestrator`` / tests).

        No persistent async HTTP client in this lobe today; reserved for future probes.
        """
        return

    async def observe(self, raw_input: str, multimodal_payload: Any = None) -> SemanticState:
        """Optional ``KERNEL_PERCEPTIVE_LOBE_PROBE_URL`` connectivity check (stack tests)."""
        url = os.environ.get("KERNEL_PERCEPTIVE_LOBE_PROBE_URL", "").strip()
        if url:
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(self._probe_sync, url, 0.25),
                    timeout=0.4,
                )
            except (OSError, urllib.error.URLError, TimeoutError, asyncio.TimeoutError) as exc:
                _log.debug("perceptive probe failed: %s", exc)
                return SemanticState(
                    perception_confidence=0.35,
                    raw_prompt=raw_input,
                    timeout_trauma=TimeoutTrauma(
                        source_lobe="perceptive",
                        latency_ms=50,
                        severity=0.8,
                        context="probe failed",
                    ),
                )
        return await self.observe_async(raw_input, multimodal_payload)

    async def observe_async(
        self,
        raw_input: str,
        conversation_context: Optional[Any] = None,
        sensor_snapshot: Optional[SensorSnapshot] = None,
    ) -> SemanticState:
        """
        Full asynchronous perception cycle.
        Vertical growth: Includes sensor fusion into the prompt context.

        **MOCK / EXPERIMENTAL:** When ``llm_backend`` is not wired, returns a synthetic
        :class:`SemanticState` (stack demos / tests). A real LLM path would call the
        backend here without changing MalAbs or safety ordering elsewhere.
        """
        start_time = time.time()

        elapsed_ms = (time.time() - start_time) * 1000.0
        if not math.isfinite(elapsed_ms) or elapsed_ms < 0.0:
            latency = 0
        else:
            latency = int(min(2_147_483_647, elapsed_ms))

        return SemanticState(
            perception_confidence=1.0,
            raw_prompt=raw_input,
            sensory_latency_lag=latency,
            visual_entities=getattr(sensor_snapshot, "detections", []),
            audio_sentiment=0.5,
        )
