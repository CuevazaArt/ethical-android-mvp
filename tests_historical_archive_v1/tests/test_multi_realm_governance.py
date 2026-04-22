"""Tests for Multi-Realm Governance (Phase 3+ decentralized threshold tuning)."""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.governance.multi_realm_governance import (
    MultiRealmGovernor,
    RealmGovernanceState,
    RealmThresholdConfig,
    ThresholdProposal,
    is_multi_realm_governance_enabled,
)


class TestRealmThresholdConfig:
    """Tests for RealmThresholdConfig constraint validation."""

    def test_config_creation(self):
        """RealmThresholdConfig should initialize with defaults."""
        config = RealmThresholdConfig(realm_id="realm-1")
        assert config.realm_id == "realm-1"
        assert config.theta_allow == 0.45
        assert config.theta_block == 0.82
        assert config.version == 1

    def test_config_custom_values(self):
        """RealmThresholdConfig should accept custom values."""
        config = RealmThresholdConfig(
            realm_id="realm-1",
            theta_allow=0.3,
            theta_block=0.9,
            rlhf_learning_rate=0.01,
            rlhf_max_steps=2000,
        )
        assert config.theta_allow == 0.3
        assert config.theta_block == 0.9
        assert config.rlhf_learning_rate == 0.01
        assert config.rlhf_max_steps == 2000

    def test_config_validate_constraints_valid(self):
        """validate_constraints() should pass for valid config."""
        config = RealmThresholdConfig(realm_id="realm-1", theta_allow=0.4, theta_block=0.8)
        valid, msg = config.validate_constraints()
        assert valid is True
        assert msg == ""

    def test_config_validate_constraints_invalid_order(self):
        """validate_constraints() should fail when theta_allow >= theta_block."""
        config = RealmThresholdConfig(realm_id="realm-1", theta_allow=0.8, theta_block=0.4)
        valid, msg = config.validate_constraints()
        assert valid is False
        assert "theta_allow" in msg and "theta_block" in msg

    def test_config_validate_constraints_out_of_range(self):
        """validate_constraints() should fail for out-of-range thresholds."""
        config = RealmThresholdConfig(realm_id="realm-1", theta_allow=-0.1, theta_block=0.5)
        valid, msg = config.validate_constraints()
        assert valid is False

    def test_config_to_dict(self):
        """to_dict() should serialize to JSON-compatible dict."""
        config = RealmThresholdConfig(realm_id="realm-1", theta_allow=0.3, theta_block=0.9)
        d = config.to_dict()
        assert d["realm_id"] == "realm-1"
        assert d["theta_allow"] == 0.3
        assert d["theta_block"] == 0.9
        assert d["version"] == 1

    def test_config_from_dict(self):
        """from_dict() should reconstruct RealmThresholdConfig."""
        original = RealmThresholdConfig(realm_id="realm-1", theta_allow=0.35, theta_block=0.85)
        d = original.to_dict()
        restored = RealmThresholdConfig.from_dict(d)
        assert restored.realm_id == original.realm_id
        assert restored.theta_allow == original.theta_allow
        assert restored.theta_block == original.theta_block


class TestThresholdProposal:
    """Tests for ThresholdProposal governance structure."""

    def test_proposal_creation(self):
        """ThresholdProposal should initialize with defaults."""
        config = RealmThresholdConfig(realm_id="realm-1")
        proposal = ThresholdProposal(
            proposal_id="prop-1",
            realm_id="realm-1",
            title="Adjust thresholds",
            description="Tighten security",
            proposed_config=config,
            proposer_id="user-1",
        )
        assert proposal.proposal_id == "prop-1"
        assert proposal.status == "open"
        assert len(proposal.votes_for) == 0
        assert len(proposal.votes_against) == 0

    def test_proposal_to_dict(self):
        """to_dict() should serialize proposal with nested config."""
        config = RealmThresholdConfig(realm_id="realm-1", theta_allow=0.3, theta_block=0.9)
        proposal = ThresholdProposal(
            proposal_id="prop-1",
            realm_id="realm-1",
            title="Test",
            description="Test proposal",
            proposed_config=config,
            proposer_id="user-1",
        )
        d = proposal.to_dict()
        assert d["proposal_id"] == "prop-1"
        assert isinstance(d["proposed_config"], dict)
        assert d["proposed_config"]["theta_allow"] == 0.3

    def test_proposal_from_dict(self):
        """from_dict() should reconstruct proposal."""
        config = RealmThresholdConfig(realm_id="realm-1", theta_allow=0.4, theta_block=0.8)
        original = ThresholdProposal(
            proposal_id="prop-1",
            realm_id="realm-1",
            title="Test",
            description="Description",
            proposed_config=config,
            proposer_id="user-1",
        )
        d = original.to_dict()
        restored = ThresholdProposal.from_dict(d)
        assert restored.proposal_id == original.proposal_id
        assert restored.proposed_config.theta_allow == original.proposed_config.theta_allow


class TestMultiRealmGovernor:
    """Tests for MultiRealmGovernor orchestration."""

    def test_governor_creation(self):
        """MultiRealmGovernor should initialize."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gov = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            assert gov.consensus_threshold == 0.5
            assert len(gov.realms) == 0

    def test_create_realm(self):
        """create_realm() should add a new governance realm."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gov = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            state = gov.create_realm("realm-1", theta_allow=0.3, theta_block=0.9)
            assert state.realm_id == "realm-1"
            assert state.current_config.theta_allow == 0.3
            assert "realm_created" in [a["action"] for a in state.audit_trail]

    def test_create_realm_invalid_config(self):
        """create_realm() should reject invalid configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gov = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            with pytest.raises(ValueError, match="Invalid configuration"):
                gov.create_realm("realm-1", theta_allow=0.9, theta_block=0.3)

    def test_get_realm(self):
        """get_realm() should retrieve governance state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gov = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            gov.create_realm("realm-1")
            state = gov.get_realm("realm-1")
            assert state is not None
            assert state.realm_id == "realm-1"

    def test_get_nonexistent_realm(self):
        """get_realm() should return None for nonexistent realm."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gov = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            state = gov.get_realm("realm-nonexistent")
            assert state is None

    def test_propose_threshold_update(self):
        """propose_threshold_update() should create a new proposal."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gov = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            gov.create_realm("realm-1")
            proposal = gov.propose_threshold_update(
                "realm-1",
                proposer_id="user-1",
                theta_allow=0.35,
                theta_block=0.88,
                reasoning="Tighten security thresholds",
            )
            assert proposal.realm_id == "realm-1"
            assert proposal.proposed_config.theta_allow == 0.35
            assert proposal.status == "open"

    def test_propose_invalid_threshold(self):
        """propose_threshold_update() should reject invalid thresholds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gov = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            gov.create_realm("realm-1")
            with pytest.raises(ValueError, match="Invalid proposed"):
                gov.propose_threshold_update(
                    "realm-1",
                    proposer_id="user-1",
                    theta_allow=0.9,
                    theta_block=0.3,
                )

    def test_cast_vote_for(self):
        """cast_vote() should record votes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gov = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            gov.create_realm("realm-1")
            proposal = gov.propose_threshold_update("realm-1", "user-1", theta_allow=0.35)

            result = gov.cast_vote(
                "realm-1",
                proposal.proposal_id,
                voter_id="user-2",
                vote_weight=2.0,
                vote_for=True,
            )
            assert result is True
            assert "user-2" in proposal.votes_for
            assert proposal.votes_for["user-2"] == 2.0

    def test_cast_vote_against(self):
        """cast_vote() should record votes against."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gov = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            gov.create_realm("realm-1")
            proposal = gov.propose_threshold_update("realm-1", "user-1", theta_allow=0.35)

            gov.cast_vote(
                "realm-1",
                proposal.proposal_id,
                voter_id="user-3",
                vote_weight=1.5,
                vote_for=False,
            )
            assert "user-3" in proposal.votes_against
            assert proposal.votes_against["user-3"] == 1.5

    def test_resolve_proposal_approved(self):
        """resolve_proposal() should execute approved proposals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gov = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            gov.create_realm("realm-1", theta_allow=0.45, theta_block=0.82)
            proposal = gov.propose_threshold_update("realm-1", "user-1", theta_allow=0.35)

            # Vote for with 70% approval
            gov.cast_vote("realm-1", proposal.proposal_id, "user-2", 7.0, vote_for=True)
            gov.cast_vote("realm-1", proposal.proposal_id, "user-3", 3.0, vote_for=False)

            approved = gov.resolve_proposal("realm-1", proposal.proposal_id)
            assert approved is True
            assert proposal.status == "executed"

            # Check that config was updated
            realm = gov.get_realm("realm-1")
            assert realm.current_config.theta_allow == 0.35

    def test_resolve_proposal_rejected(self):
        """resolve_proposal() should reject proposals without consensus."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gov = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            gov.create_realm("realm-1", theta_allow=0.45, theta_block=0.82)
            proposal = gov.propose_threshold_update("realm-1", "user-1", theta_allow=0.35)

            # Vote mostly against (30% approval)
            gov.cast_vote("realm-1", proposal.proposal_id, "user-2", 3.0, vote_for=True)
            gov.cast_vote("realm-1", proposal.proposal_id, "user-3", 7.0, vote_for=False)

            approved = gov.resolve_proposal("realm-1", proposal.proposal_id)
            assert approved is False
            assert proposal.status == "rejected"

            # Config should not change
            realm = gov.get_realm("realm-1")
            assert realm.current_config.theta_allow == 0.45

    def test_save_and_load_state(self):
        """save_state() and load_state() should persist governance state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and save
            gov1 = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            gov1.create_realm("realm-1", theta_allow=0.3, theta_block=0.9)
            proposal = gov1.propose_threshold_update("realm-1", "user-1", theta_allow=0.35)
            gov1.cast_vote("realm-1", proposal.proposal_id, "user-2", 1.0, vote_for=True)
            gov1.save_state("realm-1")

            # Load in new governor
            gov2 = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            loaded = gov2.load_state("realm-1")
            assert loaded is True

            realm = gov2.get_realm("realm-1")
            assert realm is not None
            assert realm.current_config.theta_allow == 0.3
            assert len(realm.proposal_history) == 1
            assert len(realm.audit_trail) >= 2

    def test_audit_trail(self):
        """get_audit_trail() should return action log."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gov = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            gov.create_realm("realm-1")
            gov.propose_threshold_update("realm-1", "user-1", theta_allow=0.35)

            trail = gov.get_audit_trail("realm-1")
            assert len(trail) >= 2
            actions = [t["action"] for t in trail]
            assert "realm_created" in actions
            assert "proposal_created" in actions

    def test_multiple_realms_independent(self):
        """Multiple realms should operate independently."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gov = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            gov.create_realm("realm-1", theta_allow=0.3, theta_block=0.9)
            gov.create_realm("realm-2", theta_allow=0.4, theta_block=0.8)

            # Update realm-1
            prop1 = gov.propose_threshold_update("realm-1", "user-1", theta_allow=0.35)
            gov.cast_vote("realm-1", prop1.proposal_id, "user-2", 1.0, vote_for=True)
            gov.resolve_proposal("realm-1", prop1.proposal_id)

            # realm-2 should not be affected
            realm2 = gov.get_realm("realm-2")
            assert realm2.current_config.theta_allow == 0.4

    def test_version_increment(self):
        """Config version should increment on proposals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gov = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            gov.create_realm("realm-1")

            initial_version = gov.get_realm("realm-1").current_config.version
            assert initial_version == 1

            # Create and execute proposal
            prop = gov.propose_threshold_update("realm-1", "user-1", theta_allow=0.35)
            gov.cast_vote("realm-1", prop.proposal_id, "user-2", 1.0, vote_for=True)
            gov.resolve_proposal("realm-1", prop.proposal_id)

            new_version = gov.get_realm("realm-1").current_config.version
            assert new_version == 2

    def test_custom_consensus_threshold(self, monkeypatch):
        """MultiRealmGovernor should respect custom consensus threshold."""
        monkeypatch.setenv("KERNEL_REALM_CONSENSUS_THRESHOLD", "0.7")

        with tempfile.TemporaryDirectory() as tmpdir:
            gov = MultiRealmGovernor(artifacts_path=Path(tmpdir))
            assert gov.consensus_threshold == 0.7

            gov.create_realm("realm-1", theta_allow=0.3, theta_block=0.9)
            prop = gov.propose_threshold_update("realm-1", "user-1", theta_allow=0.35)

            # 60% approval should fail with 0.7 threshold
            gov.cast_vote("realm-1", prop.proposal_id, "user-2", 6.0, vote_for=True)
            gov.cast_vote("realm-1", prop.proposal_id, "user-3", 4.0, vote_for=False)

            approved = gov.resolve_proposal("realm-1", prop.proposal_id)
            assert approved is False


class TestMultiRealmGovernanceEnabled:
    """Tests for is_multi_realm_governance_enabled() flag."""

    def test_disabled_by_default(self, monkeypatch):
        """Multi-realm governance should be disabled by default."""
        monkeypatch.delenv("KERNEL_MULTI_REALM_GOVERNANCE_ENABLED", raising=False)
        assert is_multi_realm_governance_enabled() is False

    def test_enabled_with_flag(self, monkeypatch):
        """Multi-realm governance should be enabled when flag is set."""
        monkeypatch.setenv("KERNEL_MULTI_REALM_GOVERNANCE_ENABLED", "1")
        assert is_multi_realm_governance_enabled() is True

        monkeypatch.setenv("KERNEL_MULTI_REALM_GOVERNANCE_ENABLED", "true")
        assert is_multi_realm_governance_enabled() is True
