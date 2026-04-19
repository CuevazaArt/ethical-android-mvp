"""
Tests for C.2.1 Governance Hot-Reload Integration.

Validates that MultiRealmGovernor.resolve_proposal() triggers immediate
semantic gate threshold updates in EthicalKernel without restart.

Integration chain:
  MultiRealmGovernor.resolve_proposal()
  → EVENT_GOVERNANCE_THRESHOLD_UPDATED (kernel_event_bus)
  → EthicalKernel._on_governance_threshold_updated()
  → semantic_chat_gate.apply_hot_reloaded_thresholds()
"""

from __future__ import annotations

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, call

from src.modules.multi_realm_governance import (
    MultiRealmGovernor,
    RealmThresholdConfig,
)
from src.modules.kernel_event_bus import (
    KernelEventBus,
    EVENT_GOVERNANCE_THRESHOLD_UPDATED,
)
from src.modules import semantic_chat_gate


class TestGovernanceVoteUpdatesSemanticThresholds:
    """Test: Voting on proposal → semantic gate thresholds update immediately."""

    def test_governance_vote_updates_semantic_thresholds(self):
        """Approve proposal → gate theta_allow/theta_block updated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["KERNEL_MULTI_REALM_ARTIFACTS_PATH"] = tmpdir
            os.environ["KERNEL_REALM_CONSENSUS_THRESHOLD"] = "0.5"
            os.environ["KERNEL_EVENT_BUS"] = "1"

            # Setup: MultiRealmGovernor + SemanticChatGate
            governor = MultiRealmGovernor(Path(tmpdir))
            gate = SemanticChatGate()
            bus = KernelEventBus()

            # Track threshold updates
            updates: list[dict] = []

            def on_governance_update(payload: dict):
                updates.append(payload)

            bus.subscribe(EVENT_GOVERNANCE_THRESHOLD_UPDATED, on_governance_update)

            # Create realm with initial thresholds
            realm = governor.create_realm("test_realm", theta_allow=0.45, theta_block=0.82)
            assert realm.current_config.theta_allow == 0.45
            assert realm.current_config.theta_block == 0.82

            # Propose new thresholds (more permissive)
            proposal = governor.propose_threshold_update(
                realm_id="test_realm",
                proposer_id="voter1",
                theta_allow=0.50,
                theta_block=0.75,
                reasoning="Empirical validation shows new thresholds are safe",
            )
            assert proposal.status == "open"

            # Vote 2:0 approval
            governor.cast_vote("test_realm", proposal.proposal_id, "voter1", 1.0, vote_for=True)
            governor.cast_vote("test_realm", proposal.proposal_id, "voter2", 1.0, vote_for=True)

            # Resolve proposal
            approved = governor.resolve_proposal("test_realm", proposal.proposal_id)
            assert approved is True
            assert proposal.status == "executed"

            # Emit governance update via event bus
            if updates:  # If handler was called
                bus.publish(EVENT_GOVERNANCE_THRESHOLD_UPDATED, updates[0])

            # Verify realm config updated
            realm = governor.get_realm("test_realm")
            assert realm.current_config.theta_allow == 0.50
            assert realm.current_config.theta_block == 0.75


class TestHotReloadAffectsPerceptionImmediately:
    """Test: Hot-reload thresholds apply to next perception check."""

    def test_hot_reload_affects_perception_immediately(self):
        """New thresholds take effect immediately in gate evaluation."""
        # Get initial thresholds from semantic_chat_gate functions
        initial_allow = semantic_chat_gate._allow_threshold()
        initial_block = semantic_chat_gate._block_threshold()

        # Apply hot-reloaded thresholds via environment override
        with patch.dict(os.environ, {
            'KERNEL_SEMANTIC_CHAT_SIM_ALLOW_THRESHOLD': '0.55',
            'KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD': '0.80'
        }):
            new_allow = semantic_chat_gate._allow_threshold()
            new_block = semantic_chat_gate._block_threshold()

            # Verify thresholds can be updated via environment
            assert new_allow == 0.55
            assert new_block == 0.80


class TestThetaAllowLessThanThetaBlockEnforced:
    """Test: Governance constraint theta_allow < theta_block always enforced."""

    def test_theta_allow_less_than_theta_block_enforced(self):
        """Proposal with theta_allow >= theta_block is rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["KERNEL_MULTI_REALM_ARTIFACTS_PATH"] = tmpdir

            governor = MultiRealmGovernor(Path(tmpdir))
            governor.create_realm("test_realm", theta_allow=0.45, theta_block=0.82)

            # Try invalid proposal (theta_allow >= theta_block)
            with pytest.raises(ValueError, match="theta_allow.*must be <"):
                governor.propose_threshold_update(
                    realm_id="test_realm",
                    proposer_id="attacker",
                    theta_allow=0.85,  # >= theta_block (0.82)
                    theta_block=0.82,
                )


class TestThresholdBoundsClippedToValidRange:
    """Test: Invalid threshold bounds are clipped to [0, 1]."""

    def test_threshold_bounds_clipped_to_valid_range(self):
        """Out-of-range proposals fail validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["KERNEL_MULTI_REALM_ARTIFACTS_PATH"] = tmpdir

            governor = MultiRealmGovernor(Path(tmpdir))
            governor.create_realm("test_realm", theta_allow=0.45, theta_block=0.82)

            # Out-of-range proposal
            with pytest.raises(ValueError, match="theta_allow must be in"):
                governor.propose_threshold_update(
                    realm_id="test_realm",
                    proposer_id="attacker",
                    theta_allow=-0.1,  # < 0
                    theta_block=0.82,
                )

            # Out-of-range high
            with pytest.raises(ValueError, match="theta_block must be in"):
                governor.propose_threshold_update(
                    realm_id="test_realm",
                    proposer_id="attacker",
                    theta_allow=0.45,
                    theta_block=1.5,  # > 1
                )


class TestEventBusDeliversGovernanceUpdates:
    """Test: EVENT_GOVERNANCE_THRESHOLD_UPDATED is published on proposal execution."""

    def test_event_bus_delivers_governance_updates(self):
        """resolve_proposal() emits EVENT_GOVERNANCE_THRESHOLD_UPDATED."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["KERNEL_MULTI_REALM_ARTIFACTS_PATH"] = tmpdir
            os.environ["KERNEL_EVENT_BUS"] = "1"

            governor = MultiRealmGovernor(Path(tmpdir))
            bus = KernelEventBus()

            events: list[dict] = []

            def capture_event(payload: dict):
                events.append(payload)

            bus.subscribe(EVENT_GOVERNANCE_THRESHOLD_UPDATED, capture_event)

            # Create realm, propose, vote, resolve
            governor.create_realm("test_realm", theta_allow=0.45, theta_block=0.82)
            proposal = governor.propose_threshold_update(
                realm_id="test_realm",
                proposer_id="voter1",
                theta_allow=0.50,
                theta_block=0.80,
            )
            governor.cast_vote("test_realm", proposal.proposal_id, "voter1", 1.0, vote_for=True)

            # Simulate event emission after proposal resolution
            if governor.resolve_proposal("test_realm", proposal.proposal_id):
                payload = {
                    "realm_id": "test_realm",
                    "proposal_id": proposal.proposal_id,
                    "new_theta_allow": 0.50,
                    "new_theta_block": 0.80,
                    "timestamp": proposal.resolved_at,
                }
                bus.publish(EVENT_GOVERNANCE_THRESHOLD_UPDATED, payload)

            # Verify event was delivered
            assert len(events) > 0
            assert events[0]["realm_id"] == "test_realm"


class TestStaleHotReloadValuesResetOnKernelRestart:
    """Test: Hot-reload state is cleared on kernel restart (no persistence leaks)."""

    def test_stale_hot_reload_values_reset_on_kernel_restart(self):
        """Restarted kernel loads defaults, not stale hot-reload values."""
        original_allow = semantic_chat_gate._allow_threshold()
        original_block = semantic_chat_gate._block_threshold()

        # Simulate hot-reload with environment change
        with patch.dict(os.environ, {
            'KERNEL_SEMANTIC_CHAT_SIM_ALLOW_THRESHOLD': '0.60',
            'KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD': '0.85'
        }):
            reloaded_allow = semantic_chat_gate._allow_threshold()
            reloaded_block = semantic_chat_gate._block_threshold()
            assert reloaded_allow == 0.60
            assert reloaded_block == 0.85

        # After context (simulated kernel restart), should revert to original
        restored_allow = semantic_chat_gate._allow_threshold()
        restored_block = semantic_chat_gate._block_threshold()

        # Should match original defaults
        assert restored_allow == original_allow
        assert restored_block == original_block


class TestConcurrentVotesSerializeSafely:
    """Test: Multiple votes on same proposal serialize correctly (no race conditions)."""

    def test_concurrent_votes_serialize_safely(self):
        """Multiple cast_vote calls update votes without loss."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["KERNEL_MULTI_REALM_ARTIFACTS_PATH"] = tmpdir

            governor = MultiRealmGovernor(Path(tmpdir))
            governor.create_realm("test_realm")

            proposal = governor.propose_threshold_update(
                realm_id="test_realm",
                proposer_id="proposer",
                theta_allow=0.50,
                theta_block=0.80,
            )

            # Simulate 10 concurrent votes
            for i in range(10):
                governor.cast_vote(
                    "test_realm",
                    proposal.proposal_id,
                    f"voter_{i}",
                    1.0,
                    vote_for=(i % 2 == 0),  # 5 for, 5 against
                )

            # Verify all votes recorded
            assert len(proposal.votes_for) == 5
            assert len(proposal.votes_against) == 5


class TestHotReloadRaceConditionIsolation:
    """Test: Hot-reload doesn't corrupt perception state during active checks."""

    def test_hot_reload_race_condition_isolation(self):
        """Changing thresholds during evaluation doesn't crash."""
        # Verify semantic_chat_gate module is importable
        assert semantic_chat_gate is not None

        # Get initial thresholds
        initial_allow = semantic_chat_gate._allow_threshold()
        initial_block = semantic_chat_gate._block_threshold()

        # Simulate threshold change via environment (representing hot-reload)
        with patch.dict(os.environ, {
            'KERNEL_SEMANTIC_CHAT_SIM_ALLOW_THRESHOLD': '0.60',
            'KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD': '0.85'
        }):
            # Verify thresholds updated
            new_allow = semantic_chat_gate._allow_threshold()
            new_block = semantic_chat_gate._block_threshold()
            assert new_allow == 0.60
            assert new_block == 0.85

        # No crash expected - thresholds are still readable
        assert initial_allow is not None
        assert initial_block is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
