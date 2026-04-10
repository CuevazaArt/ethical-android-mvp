"""Kernel snapshot extract/apply and JSON file persistence (Phase 2)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.kernel import EthicalKernel
from src.persistence import (
    SCHEMA_VERSION,
    JsonFilePersistence,
    SqlitePersistence,
    apply_snapshot,
    extract_snapshot,
)
from src.persistence.json_store import snapshot_from_dict
from src.simulations.runner import ALL_SIMULATIONS


def test_schema_version_constant():
    assert SCHEMA_VERSION == 1


def test_snapshot_from_dict_rejects_bad_version():
    with pytest.raises(ValueError, match="schema_version"):
        snapshot_from_dict({"schema_version": 0})


def test_extract_apply_roundtrip_in_memory():
    k1 = EthicalKernel(variability=False)
    scn = ALL_SIMULATIONS[1]()
    k1.process(scn.name, scn.place, scn.signals, scn.context, scn.actions)

    snap = extract_snapshot(k1)
    assert snap.schema_version == SCHEMA_VERSION
    assert len(snap.episodes) == 1

    k2 = EthicalKernel(variability=False)
    apply_snapshot(k2, snap)

    assert len(k2.memory.episodes) == len(k1.memory.episodes)
    assert k2.memory.episodes[0].id == k1.memory.episodes[0].id
    assert k2.memory.episodes[0].verdict == k1.memory.episodes[0].verdict
    assert k2.memory.identity.state.episode_count == k1.memory.identity.state.episode_count
    assert k2.bayesian.pruning_threshold == k1.bayesian.pruning_threshold
    assert len(k2.dao.records) == len(k1.dao.records)


def test_json_file_roundtrip(tmp_path):
    k1 = EthicalKernel(variability=False)
    scn = ALL_SIMULATIONS[2]()
    k1.process(scn.name, scn.place, scn.signals, scn.context, scn.actions)

    path = tmp_path / "checkpoint.json"
    store = JsonFilePersistence(path)
    store.save(extract_snapshot(k1))
    assert path.is_file()

    k2 = EthicalKernel(variability=False)
    assert store.load_into_kernel(k2) is True
    assert len(k2.memory.episodes) == 1
    assert k2.memory.episodes[0].action_taken == k1.memory.episodes[0].action_taken


def test_load_missing_file(tmp_path):
    store = JsonFilePersistence(tmp_path / "missing.json")
    assert store.load() is None
    k = EthicalKernel(variability=False)
    assert store.load_into_kernel(k) is False
    assert len(k.memory.episodes) == 0


def test_sqlite_roundtrip(tmp_path):
    k1 = EthicalKernel(variability=False)
    scn = ALL_SIMULATIONS[2]()
    k1.process(scn.name, scn.place, scn.signals, scn.context, scn.actions)

    path = tmp_path / "checkpoint.db"
    store = SqlitePersistence(path)
    store.save(extract_snapshot(k1))
    assert path.is_file()

    k2 = EthicalKernel(variability=False)
    assert store.load_into_kernel(k2) is True
    assert len(k2.memory.episodes) == 1
    assert k2.memory.episodes[0].action_taken == k1.memory.episodes[0].action_taken


def test_sqlite_load_missing_file(tmp_path):
    store = SqlitePersistence(tmp_path / "missing.db")
    assert store.load() is None
    k = EthicalKernel(variability=False)
    assert store.load_into_kernel(k) is False


def test_double_roundtrip_stable(tmp_path):
    """Save → load → extract again should match first snapshot (structural)."""
    k1 = EthicalKernel(variability=False)
    scn = ALL_SIMULATIONS[3]()
    k1.process(scn.name, scn.place, scn.signals, scn.context, scn.actions)

    s1 = extract_snapshot(k1)
    store = JsonFilePersistence(tmp_path / "c.json")
    store.save(s1)

    k2 = EthicalKernel(variability=False)
    store.load_into_kernel(k2)
    s2 = extract_snapshot(k2)

    assert s2.narrative_counter == s1.narrative_counter
    assert len(s2.episodes) == len(s1.episodes)
    assert s2.identity_state == s1.identity_state
    assert s2.dao_record_counter == s1.dao_record_counter
