"""v8 perceptual abstraction — presets, fixtures, layer merge (no hardware)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.perceptual_abstraction import (
    SENSOR_PRESETS,
    list_sensor_presets,
    load_sensor_fixture,
    merge_sensor_payload_layers,
    snapshot_from_layers,
)
from src.modules.sensor_contracts import SensorSnapshot, merge_sensor_hints_into_signals


def _fixture(name: str) -> str:
    return os.path.join(os.path.dirname(__file__), "fixtures", "sensor", name)


def test_load_sensor_fixture():
    d = load_sensor_fixture(_fixture("calm_uchi.json"))
    assert d["place_trust"] == 0.93


def test_preset_merge_order_client_wins():
    merged = merge_sensor_payload_layers(
        preset_name="calm_uchi",
        client_dict={"battery_level": 0.1},
    )
    assert merged["place_trust"] == SENSOR_PRESETS["calm_uchi"]["place_trust"]
    assert merged["battery_level"] == 0.1


def test_fixture_then_preset_then_client():
    merged = merge_sensor_payload_layers(
        fixture_path=_fixture("calm_uchi.json"),
        preset_name="low_battery",
        client_dict={"place_trust": 0.5},
    )
    assert merged["place_trust"] == 0.5
    assert merged["battery_level"] == 0.03


def test_snapshot_from_layers_none_when_empty():
    assert snapshot_from_layers() is None


def test_list_sensor_presets_sorted():
    names = list_sensor_presets()
    assert names == tuple(sorted(names))
    assert "hostile_soto" in names


def test_integration_merge_into_signals():
    snap = snapshot_from_layers(preset_name="low_battery")
    assert snap is not None
    base = {"risk": 0.4, "urgency": 0.4, "hostility": 0.0, "calm": 0.6, "vulnerability": 0.0}
    out = merge_sensor_hints_into_signals(base, snap)
    assert out["urgency"] > base["urgency"]
