"""Snapshot apply rejects non-finite episode and Bayesian floats."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.persistence import SCHEMA_VERSION, extract_snapshot, snapshot_from_dict
from src.persistence.kernel_io import apply_snapshot, episode_from_dict


def test_episode_from_dict_rejects_nan_sigma():
    d = {
        "id": "1",
        "timestamp": "t",
        "place": "p",
        "event_description": "e",
        "body_state": {"energy": 1.0, "active_nodes": 8, "sensors_ok": True, "description": ""},
        "action_taken": "a",
        "morals": {},
        "verdict": "Good",
        "ethical_score": 0.5,
        "decision_mode": "D_fast",
        "sigma": float("nan"),
        "context": "everyday",
    }
    with pytest.raises(ValueError, match="finite"):
        episode_from_dict(d)


def test_apply_snapshot_rejects_nonfinite_bayesian_weight():
    k = EthicalKernel(variability=False)
    snap = extract_snapshot(k)
    snap.bayesian_hypothesis_weights = [0.4, float("inf"), 0.25]
    with pytest.raises(ValueError, match="finite"):
        apply_snapshot(k, snap)


def test_snapshot_roundtrip_still_validates_schema():
    raw = {"schema_version": SCHEMA_VERSION}
    snap = snapshot_from_dict(raw)
    k2 = EthicalKernel(variability=False)
    apply_snapshot(k2, snap)
