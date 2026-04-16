"""Temporal planning context: processor/wall/battery/ETA/sync advisory snapshot."""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.sensor_contracts import SensorSnapshot
from src.modules.temporal_planning import build_temporal_context
from src.modules.vitality import VitalityAssessment, critical_temperature_threshold


def test_temporal_context_transport_keyword_eta_and_sync_fields():
    start = time.monotonic()
    turn = start
    tc = build_temporal_context(
        turn_index=3,
        process_start_mono=start,
        turn_start_mono=turn,
        subjective_elapsed_s=12.3,
        context="everyday_ethics",
        text="I need transport options for a long trip.",
        vitality=VitalityAssessment(
            0.8, 0.05, False, None, critical_temperature_threshold(), False
        ),
        sensor_snapshot=SensorSnapshot(place_trust=0.9),
    )
    out = tc.to_public_dict()
    assert out["sync_schema"] == "temporal_sync_v1"
    assert out["turn_index"] == 3
    assert out["eta_source"] == "keyword:transport"
    assert out["eta_seconds"] >= 1800.0
    assert out["local_network_sync_ready"] is True
    assert out["dao_sync_ready"] is True


def test_temporal_context_low_place_trust_disables_lan_sync(monkeypatch):
    monkeypatch.setenv("KERNEL_TEMPORAL_LAN_SYNC", "1")
    tc = build_temporal_context(
        turn_index=1,
        process_start_mono=time.monotonic(),
        turn_start_mono=time.monotonic(),
        subjective_elapsed_s=1.0,
        context="hostile_interaction",
        text="hello",
        vitality=VitalityAssessment(
            None, 0.05, False, None, critical_temperature_threshold(), False
        ),
        sensor_snapshot=SensorSnapshot(place_trust=0.1),
    )
    assert tc.local_network_sync_ready is False
