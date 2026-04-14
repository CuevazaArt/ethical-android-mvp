"""v9.3 swarm stub — digests and stats (no network, no kernel)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.swarm_peer_stub import (
    peer_agreement_stats,
    swarm_stub_enabled,
    verdict_digest_v1,
)


def test_verdict_digest_deterministic():
    a = verdict_digest_v1("EP-0001", "Good", 0.42, "everyday")
    b = verdict_digest_v1("EP-0001", "Good", 0.42, "everyday")
    assert a["sha256_full"] == b["sha256_full"]
    assert a["sha256_short"] == b["sha256_short"][:16]
    assert a["payload"]["v"] == 1


def test_peer_agreement_all_same():
    d = verdict_digest_v1("EP-1", "Gray Zone", -0.1, "hostile_interaction")
    stats = peer_agreement_stats([d, d, d])
    assert stats["n"] == 3
    assert stats["unique_fingerprints"] == 1
    assert stats["agreement_ratio"] == 1.0


def test_peer_agreement_all_different():
    d1 = verdict_digest_v1("EP-1", "Good", 0.5, "everyday")
    d2 = verdict_digest_v1("EP-2", "Bad", -0.5, "everyday")
    stats = peer_agreement_stats([d1, d2])
    assert stats["n"] == 2
    assert stats["unique_fingerprints"] == 2
    assert stats["agreement_ratio"] == 0.5


def test_swarm_stub_env(monkeypatch):
    monkeypatch.delenv("KERNEL_SWARM_STUB", raising=False)
    assert swarm_stub_enabled() is False
    monkeypatch.setenv("KERNEL_SWARM_STUB", "1")
    assert swarm_stub_enabled() is True
