"""Pilar 3 — experience_digest (Ψ Sleep additive consolidation line)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.persistence import JsonFilePersistence, extract_snapshot
from src.simulations.runner import ALL_SIMULATIONS


def test_execute_sleep_populates_experience_digest():
    k = EthicalKernel(variability=False, seed=1)
    scn = ALL_SIMULATIONS[1]()
    k.process(scn.name, scn.place, scn.signals, scn.context, scn.actions)
    assert k.memory.experience_digest == ""
    k.execute_sleep()
    d = k.memory.experience_digest
    assert d
    assert "psi_health=" in d
    assert "context_mix=" in d


def test_snapshot_roundtrip_preserves_experience_digest(tmp_path):
    k1 = EthicalKernel(variability=False, seed=2)
    scn = ALL_SIMULATIONS[2]()
    k1.process(scn.name, scn.place, scn.signals, scn.context, scn.actions)
    k1.execute_sleep()
    digest = k1.memory.experience_digest
    path = tmp_path / "s.json"
    store = JsonFilePersistence(path)
    store.save(extract_snapshot(k1))
    k2 = EthicalKernel(variability=False)
    assert store.load_into_kernel(k2) is True
    assert k2.memory.experience_digest == digest
