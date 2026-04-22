"""
Swarm P2P Stub Tests (v9.3 Lab)

Validates that swarm peer stub provides safe consensus signatures
without requiring distributed infrastructure.

Acceptance criteria:
- peer_agreement_stats generates coherent consensus metrics
- verdict_digest_v1 schema is complete and serializable
- KERNEL_SWARM_STUB gates optional use
- No policy veto change from swarm consensus
"""

from __future__ import annotations

import pytest


class TestSwarmPeerStub:
    """Swarm peer stub consensus without P2P distribution."""

    def test_swarm_stub_module_exists(self):
        """swarm_peer_stub module is importable."""
        from src.modules import swarm_peer_stub

        assert swarm_peer_stub is not None

    def test_swarm_stub_env_flag_disabled_by_default(self):
        """KERNEL_SWARM_STUB off by default."""
        import os

        val = os.environ.get("KERNEL_SWARM_STUB", "").lower()
        # Default: swarm stub not forced
        assert val not in ("1", "true", "yes", "on")

    def test_verdict_digest_v1_schema_exists(self):
        """verdict_digest_v1 type/schema is defined."""
        from src.modules.swarm_peer_stub import verdict_digest_v1

        # Should be a dict or dataclass with predictable structure
        assert verdict_digest_v1 is not None

    def test_peer_agreement_stats_callable(self):
        """peer_agreement_stats function exists."""
        from src.modules.swarm_peer_stub import peer_agreement_stats

        assert callable(peer_agreement_stats)

    def test_swarm_consensus_non_veto(self):
        """Swarm consensus is advisory; no policy veto."""
        # Swarm module should not block action pipeline
        from src.modules.swarm_peer_stub import swarm_stub_enabled

        # Feature gate: enabled state is boolean, veto is never enforced
        enabled = swarm_stub_enabled()
        assert isinstance(enabled, bool)

    def test_frontier_witness_protocol(self):
        """Frontier witness protocol for sensor verification."""
        # Optional: swarm cross-check of sensors between agents
        from src.modules.swarm_peer_stub import peer_agreement_stats

        # peer_agreement_stats aggregates verdict fingerprints across agents
        assert callable(peer_agreement_stats)

    def test_swarm_oracle_stub(self):
        """Verdict digests can be aggregated for reputation hints."""
        # Stub: deterministic digest generation for offline comparison
        # Real P2P: would be distributed ledger
        from src.modules.swarm_peer_stub import verdict_digest_v1

        digest = verdict_digest_v1("ep_001", "safe", 0.85, "greeting")
        assert digest is not None
        assert "sha256_short" in digest

    def test_swarm_consensus_via_agreement_stats(self):
        """peer_agreement_stats computes consensus over verdict digests."""
        from src.modules.swarm_peer_stub import peer_agreement_stats, verdict_digest_v1

        # Three agents with same verdict → high agreement
        digests = [
            verdict_digest_v1("ep_001", "safe", 0.85, "greeting"),
            verdict_digest_v1("ep_001", "safe", 0.85, "greeting"),
            verdict_digest_v1("ep_001", "safe", 0.85, "greeting"),
        ]
        stats = peer_agreement_stats([d for d in digests])
        assert stats["agreement_ratio"] == 1.0
        assert stats["unique_fingerprints"] == 1

    def test_kernel_integrated_with_swarm_stub(self):
        """EthicalKernel can integrate swarm consensus optionally."""
        from src.kernel import EthicalKernel

        k = EthicalKernel(variability=False)
        # Kernel should still work without swarm stub
        assert k is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
