"""
Bloque B.5 — Nomad + Thalamus path without unittest mocks (V13 tri-lobe).

Replaces legacy PerceptiveLobe MagicMock setup with a real CorpusCallosum gateway.
"""

from __future__ import annotations

import asyncio
import time
from types import SimpleNamespace

import pytest
from src.kernel_lobes.models import RawSensoryPulse, SensorySpike
from src.kernel_lobes.perception_lobe import PerceptiveLobe
from src.kernel_lobes.thalamus_lobe import ThalamusLobe
from src.modules.perception.nomad_bridge import get_nomad_bridge
from src.nervous_system.corpus_callosum import CorpusCallosum


@pytest.mark.asyncio
async def test_text_pulse_promoted_via_thalamus_gateway() -> None:
    """Explicit chat text must promote to SensorySpike (survival path for Nomad typed input)."""

    bus = CorpusCallosum()
    bus.start()
    try:
        ThalamusLobe(bus)
        spikes: list[SensorySpike] = []

        async def _collect(sp: SensorySpike) -> None:
            spikes.append(sp)

        bus.subscribe(SensorySpike, _collect)

        pulse = RawSensoryPulse(
            payload={
                "text": "field ping",
                "agent_id": "nomad",
                "vision": {"human_presence": 0.0, "lip_movement": 0.0},
                "audio": {"vad_confidence": 0.0},
            },
            origin_lobe="nomad_test",
        )
        await bus.publish(pulse)
        await asyncio.sleep(0.15)
        assert len(spikes) >= 1
        assert spikes[-1].payload.get("text") == "field ping"
    finally:
        await bus.stop()


def test_nomad_bridge_health_is_readable_without_mock() -> None:
    """Global NomadBridge exposes queue stats for observability (no MagicMock)."""

    nb = get_nomad_bridge()
    try:
        stats = nb.public_queue_stats()
        assert str(stats.get("schema", "")).startswith("nomad_bridge_queue_stats_v")
        nb._last_sensor_update = time.time()
        nb._is_vessel_healthy = True
        assert isinstance(nb.public_queue_stats().get("vessel_healthy"), bool)
    finally:
        nb._last_sensor_update = time.time()
        nb._is_vessel_healthy = True


def test_perceptive_somatic_inertia_without_thalamus_mock() -> None:
    """PerceptiveLobe inertia uses real NomadBridge + ``is_vessel_online`` (no unittest mocks)."""

    bridge = get_nomad_bridge()
    try:
        bridge._last_sensor_update = time.time()
        bridge._is_vessel_healthy = True

        dummy = SimpleNamespace()
        clock = SimpleNamespace(turn_index=1)
        lobe = PerceptiveLobe(
            safety_interlock=dummy,
            strategist=dummy,
            llm=dummy,
            somatic_store=dummy,
            buffer=dummy,
            absolute_evil=dummy,
            subjective_clock=clock,
            bus=None,
        )

        assert lobe.get_sensory_impulses()["offline"] is False

        bridge._last_sensor_update = time.time() - 10.0
        ghost = lobe.get_sensory_impulses()
        assert ghost["offline"] is True
        assert ghost["inertia_active"] is True
        assert "sensory_shutdown" not in ghost

        lobe._nomad_inertia_deadline = time.time() - 1.0
        shutdown = lobe.get_sensory_impulses()
        assert shutdown.get("sensory_shutdown") is True
        assert shutdown["offline"] is True
    finally:
        bridge._last_sensor_update = time.time()
        bridge._is_vessel_healthy = True
