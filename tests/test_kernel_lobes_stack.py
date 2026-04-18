"""Tri-lobe stack: limbic trauma weights, sensor adapter seam.

``CorpusCallosumOrchestrator`` was removed as a non-functional stub (CHANGELOG — post-merge
kernel repair). Tri-lobe integration is covered via ``EthicalKernel`` + lobe tests elsewhere.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.kernel_lobes.sensor_adapter import FixedSensorAdapter, StubSensorAdapter
from src.modules.sensor_contracts import SensorSnapshot


def test_limbic_execute_stage_smoke() -> None:
    """``LimbicEthicalLobe`` is wired on the kernel with real Uchi-Soto / sympathetic / locus deps."""
    k = EthicalKernel(variability=False)
    out = k.limbic_lobe.execute_stage(
        "user",
        {"risk": 0.1, "urgency": 0.1, "hostility": 0.1, "calm": 0.5, "trust": 0.5},
        "hello",
        1,
    )
    assert out.social_evaluation is not None
    assert out.internal_state is not None
    assert out.locus_evaluation is not None


def test_stub_sensor_adapter_empty_snapshot() -> None:
    stub = StubSensorAdapter()
    snap = stub.read_snapshot()
    assert isinstance(snap, SensorSnapshot)
    assert snap.is_empty()


def test_fixed_sensor_adapter_replays_snapshot() -> None:
    inner = SensorSnapshot(battery_level=0.42, place_trust=0.9)
    fixed = FixedSensorAdapter(inner)
    assert fixed.read_snapshot() is inner
