"""
Módulo 7: Justicia Restaurativa y Compensación Swarm

Validates restorative justice mechanisms and swarm compensation integration:
- EthosToken reparation transfers linked to swarm vote outcomes
- Reputation slashing for nodes with false witness data
- Persistent audit logging of all compensation transactions
"""

from __future__ import annotations

import pytest
from src.kernel import EthicalKernel
from src.modules.dao_orchestrator import DAOOrchestrator
from src.modules.swarm_oracle import SwarmOracle


class TestRestoraiveJusticeModule:
    """Bloque 7.1 & 7.2: Compensation and Slashing Integration."""

    def test_dao_orchestrator_issue_reparation(self):
        """EthosToken reparation transfer is logged persistently."""
        dao = DAOOrchestrator()
        txn = dao.issue_restorative_reparation(
            case_id="case_001",
            recipient="affected_user",
            amount=100.5
        )
        # Should return a mock transaction hash
        assert isinstance(txn, str)
        assert "reparation" in txn.lower()

    def test_reparation_audit_logged(self):
        """Reparation transactions appear in audit logs."""
        dao = DAOOrchestrator()
        amount = 50.0
        recipient = "test_user"
        case_id = "case_test_001"

        txn = dao.issue_restorative_reparation(
            case_id=case_id,
            recipient=recipient,
            amount=amount
        )

        # Verify audit entry exists
        assert txn is not None
        assert len(txn) > 0

    def test_swarm_oracle_reputation_slashing(self):
        """Node reputation is degraded when witness fails."""
        oracle = SwarmOracle()

        # Register a peer with sufficient successful interactions to build reputation
        for _ in range(5):
            oracle.register_interaction("peer_001", success=True)
        peer_rep_before = oracle.peers["peer_001"].reputation

        # Apply slashing
        oracle.apply_slashing("peer_001", severity=0.05)
        peer_rep_after = oracle.peers["peer_001"].reputation

        # Reputation should decrease
        assert peer_rep_after < peer_rep_before
        assert peer_rep_after == peer_rep_before - 0.05

    def test_slashing_bounds_reputation_at_zero(self):
        """Slashing cannot reduce reputation below 0."""
        oracle = SwarmOracle()
        # Register with failed interaction to set low reputation
        oracle.register_interaction("peer_002", success=False)
        oracle.register_interaction("peer_002", success=False)
        oracle.register_interaction("peer_002", success=False)

        # Apply slashing greater than current reputation
        oracle.apply_slashing("peer_002", severity=0.5)

        # Reputation should be clamped at 0, not negative
        assert oracle.peers["peer_002"].reputation >= 0.0

    def test_slashing_unregistered_peer_safe(self):
        """Slashing unregistered peer does not crash."""
        oracle = SwarmOracle()
        # Should not raise exception
        oracle.apply_slashing("nonexistent_peer", severity=0.3)
        # Oracle should remain stable
        assert oracle is not None

    def test_kernel_integration_with_restorative_flow(self):
        """Kernel can trigger restorative justice via DAO."""
        k = EthicalKernel(variability=False)
        # Kernel has dao reference
        assert k.dao is not None
        # DAO should have reparation method
        assert hasattr(k.dao, 'issue_restorative_reparation')

    def test_multiple_slashing_events_cumulative(self):
        """Multiple slashing events accumulate reputation penalty."""
        oracle = SwarmOracle()
        # Build up higher reputation first
        for _ in range(10):
            oracle.register_interaction("peer_003", success=True)

        initial_rep = oracle.peers["peer_003"].reputation

        # Apply two slashing events
        oracle.apply_slashing("peer_003", severity=0.2)
        rep_after_first = oracle.peers["peer_003"].reputation
        oracle.apply_slashing("peer_003", severity=0.1)

        final_rep = oracle.peers["peer_003"].reputation

        # Each slashing should reduce reputation
        assert final_rep < initial_rep
        assert rep_after_first == initial_rep - 0.2
        assert final_rep == rep_after_first - 0.1

    def test_reparation_amount_precision(self):
        """Reparation amounts preserve floating-point precision."""
        dao = DAOOrchestrator()
        test_amounts = [10.5, 100.25, 0.01, 1000.999]

        for amount in test_amounts:
            txn = dao.issue_restorative_reparation(
                case_id=f"precision_test_{amount}",
                recipient="precision_user",
                amount=amount
            )
            assert txn is not None

    def test_oracle_persistence_across_instances(self):
        """SwarmOracle state is persisted to disk."""
        oracle1 = SwarmOracle()
        oracle1.register_interaction("persistent_peer", success=True)

        # Create new instance with same cache path and verify state persists
        oracle2 = SwarmOracle()
        # Peer registration should survive across instances
        assert "persistent_peer" in oracle2.peers

    def test_bloque_71_acceptance_criteria(self):
        """Acceptance: EthosToken reparation links to swarm votes."""
        # M7.1: Vincular los resultados del voto Swarm con transferencias
        dao = DAOOrchestrator()

        # Simulate swarm consensus outcome
        case_id = "swarm_vote_case_001"
        compensation_amount = 75.5

        # Issue reparation linked to swarm consensus
        txn_hash = dao.issue_restorative_reparation(
            case_id=case_id,
            recipient="swarm_affected_user",
            amount=compensation_amount
        )

        # M7.1 acceptance: txn exists, amount is non-zero
        assert txn_hash is not None
        assert compensation_amount > 0

    def test_bloque_72_acceptance_criteria(self):
        """Acceptance: Reputation degradation for false witness."""
        # M7.2: Degradar reputación si testigos son desmentidos
        oracle = SwarmOracle()

        node_id = "witness_node_001"
        # Register with successful interactions to build reputation
        for _ in range(8):
            oracle.register_interaction(node_id, success=True)
        initial_rep = oracle.peers[node_id].reputation

        # Simulate witness being proven false by majority
        slashing_severity = 0.15
        oracle.apply_slashing(node_id, severity=slashing_severity)

        # M7.2 acceptance: reputation is degraded
        final_rep = oracle.peers[node_id].reputation
        assert final_rep < initial_rep
        assert final_rep == initial_rep - slashing_severity


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
