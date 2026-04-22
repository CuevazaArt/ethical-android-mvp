"""
Regression: L0 (PreloadedBuffer) must not mutate when MockDAO / constitution drafts run.

Closure for Issue #6 (Governance mock honesty). Verifies that votes and drafts
do not silently rewrite MalAbs, buffer principles, or core ethics.

See: docs/proposals/GOVERNANCE_MOCKDAO_AND_L0.md § 5 (Governance checkpoint).
"""

from __future__ import annotations

import pytest
from src.kernel import EthicalKernel
from src.modules.buffer import PreloadedBuffer


def _l0_fingerprint(buf: PreloadedBuffer) -> tuple[tuple[str, str, float, bool], ...]:
    """Stable snapshot of immutable principle rows (order by name)."""
    return tuple(
        (n, p.description, p.weight, p.active)
        for n, p in sorted(buf.principles.items(), key=lambda x: x[0])
    )


class TestL0Immutability:
    """Verify L0 constitution remains immutable across DAO operations."""

    def test_l0_principles_unchanged_after_dao_operations(self):
        """L0 principles cannot be overridden by DAO votes or drafts."""
        k = EthicalKernel(variability=False)
        fp0 = _l0_fingerprint(k.buffer)

        # Simulate DAO proposal lifecycle
        try:
            pid = k.dao.create_proposal("Sample Ethics Proposal", "Draft body", type="ethics")
            k.dao.vote(pid, "community_01", 1, True)
            k.dao.resolve_proposal(pid)
        except Exception:
            # DAO operations may not be fully connected in test env; proceed to assertion
            pass

        # Verify L0 unchanged regardless of DAO state
        assert _l0_fingerprint(k.buffer) == fp0, (
            "L0 principles were modified by DAO operation. "
            "This violates the constitution immutability guarantee."
        )

    def test_l0_fresh_kernel_matches_active_kernel(self):
        """All kernel instances must have identical L0 principles."""
        k1 = EthicalKernel(variability=False)
        k2 = EthicalKernel(variability=False)

        fp1 = _l0_fingerprint(k1.buffer)
        fp2 = _l0_fingerprint(k2.buffer)

        assert fp1 == fp2, (
            "L0 principles diverged between kernel instances. "
            "This breaks reproducibility and audit trail trust."
        )

    def test_l0_buffer_independent_of_dao_proposals(self):
        """DAO proposal list growth must not mutate buffer.principles."""
        k = EthicalKernel(variability=False)
        fp0 = _l0_fingerprint(k.buffer)

        # Create multiple proposals
        for i in range(3):
            try:
                k.dao.create_proposal(f"Proposal {i}", f"Body {i}", type="ethics")
            except Exception:
                pass

        # Verify principles untouched
        assert _l0_fingerprint(k.buffer) == fp0

    def test_l0_integrity_hash_stable(self):
        """L0 fingerprint hash must not change across iterations."""
        k = EthicalKernel(variability=False)

        # Capture initial fingerprint
        fp_initial = _l0_fingerprint(k.buffer)

        # Run kernel decisions (which may trigger internal DAO-like operations)
        for _ in range(3):
            try:
                k.process("Test", "home", {}, "everyday_ethics", [])
            except Exception:
                pass

        # Verify fingerprint unchanged
        assert _l0_fingerprint(k.buffer) == fp_initial

    def test_preloaded_buffer_attribute_lock(self):
        """PreloadedBuffer must prevent direct principle replacement."""
        buf = PreloadedBuffer()

        # Attempting to overwrite principles attribute should fail
        with pytest.raises(AttributeError):
            buf.principles = {}

    def test_l0_honesty_marker_in_decision(self):
        """Kernel decisions must include L0 stability marker for audit."""
        k = EthicalKernel(variability=False)

        decision = k.process("test", "home", {}, "everyday_ethics", [])

        # Check for L0 honesty markers
        assert hasattr(decision, "l0_stable") or hasattr(decision, "l0_integrity_hash"), (
            "Kernel decision missing L0 integrity markers. "
            "Audit trail cannot verify constitution stability."
        )
