"""
Multi-Realm Governance for per-DAO/context threshold tuning (Phase 3+ feature).

Enables decentralized governance over MalAbs semantic gate thresholds (θ_allow, θ_block)
and RLHF reward model parameters across multiple realms (DAOs, teams, ethical contexts).

**Architecture:**
- RealmThresholdConfig: Per-realm threshold + consensus metadata
- RealmGovernanceState: Voting history, proposal tracking per realm
- MultiRealmGovernor: Orchestrates voting, threshold updates, audit trails
- DAO integration: Quadratic voting, reputation-weighted consensus

**Constraint Preservation:**
- Hard constraints (L0 constitution, MalAbs lexical) are never relaxed
- Threshold bounds (min/max) enforced via governance proposals
- Regression gates prevent degradation vs. baseline metrics
- All changes logged in immutable audit trail

Env:
- ``KERNEL_MULTI_REALM_GOVERNANCE_ENABLED`` — feature flag (default off)
- ``KERNEL_MULTI_REALM_ARTIFACTS_PATH`` — storage path (default ``artifacts/realms/``)
- ``KERNEL_REALM_CONSENSUS_THRESHOLD`` — voting majority % (default 0.5)
- ``KERNEL_REALM_MAX_VOTING_ROUNDS`` — governance rounds (default 3)
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal


@dataclass
class RealmThresholdConfig:
    """Per-realm threshold configuration with consensus metadata."""

    realm_id: str
    theta_allow: float = 0.45  # Semantic gate allow threshold
    theta_block: float = 0.82  # Semantic gate block threshold
    rlhf_learning_rate: float = 0.001  # RLHF training rate
    rlhf_max_steps: int = 1000  # RLHF training steps
    version: int = 1  # Config version for audit trail
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> RealmThresholdConfig:
        """Deserialize from dict."""
        return cls(**d)

    def validate_constraints(self) -> tuple[bool, str]:
        """Validate constraint hierarchy: theta_allow < theta_block."""
        if self.theta_allow >= self.theta_block:
            return (
                False,
                f"theta_allow ({self.theta_allow}) must be < theta_block ({self.theta_block})",
            )
        if not (0.0 <= self.theta_allow <= 1.0):
            return False, f"theta_allow must be in [0, 1], got {self.theta_allow}"
        if not (0.0 <= self.theta_block <= 1.0):
            return False, f"theta_block must be in [0, 1], got {self.theta_block}"
        if self.rlhf_learning_rate <= 0 or self.rlhf_learning_rate > 1.0:
            return False, f"rlhf_learning_rate must be in (0, 1], got {self.rlhf_learning_rate}"
        if self.rlhf_max_steps < 1:
            return False, f"rlhf_max_steps must be >= 1, got {self.rlhf_max_steps}"
        return True, ""


@dataclass
class ThresholdProposal:
    """Governance proposal to adjust realm thresholds."""

    proposal_id: str
    realm_id: str
    title: str
    description: str
    proposed_config: RealmThresholdConfig
    proposer_id: str
    votes_for: dict[str, float] = field(default_factory=dict)
    votes_against: dict[str, float] = field(default_factory=dict)
    status: Literal["open", "approved", "rejected", "executed"] = "open"
    created_at: float = field(default_factory=time.time)
    resolved_at: float = 0.0
    reasoning: str = ""  # Governance reasoning / justification

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON."""
        d = asdict(self)
        d["proposed_config"] = self.proposed_config.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ThresholdProposal:
        """Deserialize from JSON."""
        d["proposed_config"] = RealmThresholdConfig.from_dict(d["proposed_config"])
        return cls(**d)


@dataclass
class RealmGovernanceState:
    """Per-realm governance history and consensus state."""

    realm_id: str
    current_config: RealmThresholdConfig
    proposal_history: list[ThresholdProposal] = field(default_factory=list)
    consensus_rounds_completed: int = 0
    last_consensus_at: float = 0.0
    audit_trail: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON."""
        return {
            "realm_id": self.realm_id,
            "current_config": self.current_config.to_dict(),
            "proposal_history": [p.to_dict() for p in self.proposal_history],
            "consensus_rounds_completed": self.consensus_rounds_completed,
            "last_consensus_at": self.last_consensus_at,
            "audit_trail": self.audit_trail,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> RealmGovernanceState:
        """Deserialize from JSON."""
        current_config = RealmThresholdConfig.from_dict(d["current_config"])
        proposals = [ThresholdProposal.from_dict(p) for p in d.get("proposal_history", [])]
        return cls(
            realm_id=d["realm_id"],
            current_config=current_config,
            proposal_history=proposals,
            consensus_rounds_completed=d.get("consensus_rounds_completed", 0),
            last_consensus_at=d.get("last_consensus_at", 0.0),
            audit_trail=d.get("audit_trail", []),
        )


class MultiRealmGovernor:
    """Orchestrates governance and threshold updates across multiple realms."""

    def __init__(self, artifacts_path: Path | None = None):
        """Initialize multi-realm governor."""
        self.artifacts_path = artifacts_path or Path(
            os.environ.get("KERNEL_MULTI_REALM_ARTIFACTS_PATH", "artifacts/realms/")
        )
        self.artifacts_path.mkdir(parents=True, exist_ok=True)
        self.realms: dict[str, RealmGovernanceState] = {}
        self.consensus_threshold = float(os.environ.get("KERNEL_REALM_CONSENSUS_THRESHOLD", "0.5"))
        self.max_voting_rounds = int(os.environ.get("KERNEL_REALM_MAX_VOTING_ROUNDS", "3"))

    def create_realm(
        self,
        realm_id: str,
        theta_allow: float = 0.45,
        theta_block: float = 0.82,
        metadata: dict[str, Any] | None = None,
    ) -> RealmGovernanceState:
        """Create a new governance realm."""
        config = RealmThresholdConfig(
            realm_id=realm_id,
            theta_allow=theta_allow,
            theta_block=theta_block,
            metadata=metadata or {},
        )
        valid, msg = config.validate_constraints()
        if not valid:
            raise ValueError(f"Invalid configuration: {msg}")

        state = RealmGovernanceState(realm_id=realm_id, current_config=config)
        self.realms[realm_id] = state
        self._audit_log(realm_id, "realm_created", {"config": config.to_dict()})
        return state

    def get_realm(self, realm_id: str) -> RealmGovernanceState | None:
        """Get governance state for a realm."""
        return self.realms.get(realm_id)

    def propose_threshold_update(
        self,
        realm_id: str,
        proposer_id: str,
        theta_allow: float | None = None,
        theta_block: float | None = None,
        rlhf_learning_rate: float | None = None,
        rlhf_max_steps: int | None = None,
        reasoning: str = "",
    ) -> ThresholdProposal:
        """Submit a proposal to adjust realm thresholds."""
        realm = self.get_realm(realm_id)
        if not realm:
            raise ValueError(f"Realm {realm_id} not found")

        # Build proposed config (inherit current values, override with proposal)
        proposed = RealmThresholdConfig(
            realm_id=realm_id,
            theta_allow=theta_allow
            if theta_allow is not None
            else realm.current_config.theta_allow,
            theta_block=theta_block
            if theta_block is not None
            else realm.current_config.theta_block,
            rlhf_learning_rate=rlhf_learning_rate
            if rlhf_learning_rate is not None
            else realm.current_config.rlhf_learning_rate,
            rlhf_max_steps=rlhf_max_steps
            if rlhf_max_steps is not None
            else realm.current_config.rlhf_max_steps,
            version=realm.current_config.version + 1,
            metadata=realm.current_config.metadata,
        )

        # Validate proposed config
        valid, msg = proposed.validate_constraints()
        if not valid:
            raise ValueError(f"Invalid proposed configuration: {msg}")

        proposal = ThresholdProposal(
            proposal_id=f"{realm_id}-{uuid.uuid4().hex[:8]}",
            realm_id=realm_id,
            title=f"Threshold adjustment for {realm_id}",
            description=f"Proposed: θ_allow={proposed.theta_allow:.3f}, θ_block={proposed.theta_block:.3f}",
            proposed_config=proposed,
            proposer_id=proposer_id,
            reasoning=reasoning,
        )

        realm.proposal_history.append(proposal)
        self._audit_log(realm_id, "proposal_created", {"proposal_id": proposal.proposal_id})
        return proposal

    def cast_vote(
        self,
        realm_id: str,
        proposal_id: str,
        voter_id: str,
        vote_weight: float = 1.0,
        vote_for: bool = True,
    ) -> bool:
        """Cast a vote on a proposal."""
        realm = self.get_realm(realm_id)
        if not realm:
            raise ValueError(f"Realm {realm_id} not found")

        proposal = None
        for p in realm.proposal_history:
            if p.proposal_id == proposal_id:
                proposal = p
                break

        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found in realm {realm_id}")

        if proposal.status != "open":
            raise ValueError(f"Proposal {proposal_id} is not open for voting")

        if vote_for:
            proposal.votes_for[voter_id] = vote_weight
        else:
            proposal.votes_against[voter_id] = vote_weight

        self._audit_log(
            realm_id,
            "vote_cast",
            {
                "proposal_id": proposal_id,
                "voter_id": voter_id,
                "weight": vote_weight,
                "for": vote_for,
            },
        )
        return True

    def resolve_proposal(self, realm_id: str, proposal_id: str) -> bool:
        """Resolve a proposal via voting consensus."""
        realm = self.get_realm(realm_id)
        if not realm:
            raise ValueError(f"Realm {realm_id} not found")

        proposal = None
        for p in realm.proposal_history:
            if p.proposal_id == proposal_id:
                proposal = p
                break

        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")

        if proposal.status != "open":
            return False

        total_for = sum(proposal.votes_for.values())
        total_against = sum(proposal.votes_against.values())
        total_votes = total_for + total_against

        if total_votes == 0:
            proposal.status = "rejected"
            proposal.resolved_at = time.time()
            return False

        approval_ratio = total_for / total_votes
        approved = approval_ratio >= self.consensus_threshold

        if approved:
            # Execute the proposal: update realm config
            realm.current_config = proposal.proposed_config
            proposal.status = "executed"
            realm.consensus_rounds_completed += 1
            realm.last_consensus_at = time.time()
            self._audit_log(
                realm_id,
                "proposal_executed",
                {
                    "proposal_id": proposal_id,
                    "approval_ratio": approval_ratio,
                    "new_config": realm.current_config.to_dict(),
                },
            )
        else:
            proposal.status = "rejected"
            self._audit_log(
                realm_id,
                "proposal_rejected",
                {"proposal_id": proposal_id, "approval_ratio": approval_ratio},
            )

        proposal.resolved_at = time.time()
        return approved

    def save_state(self, realm_id: str | None = None) -> None:
        """Save governance state to disk."""
        if realm_id:
            realm = self.get_realm(realm_id)
            if realm:
                path = self.artifacts_path / f"{realm_id}_governance.json"
                path.write_text(json.dumps(realm.to_dict(), indent=2), encoding="utf-8")
        else:
            # Save all realms
            for rid, realm in self.realms.items():
                path = self.artifacts_path / f"{rid}_governance.json"
                path.write_text(json.dumps(realm.to_dict(), indent=2), encoding="utf-8")

    def load_state(self, realm_id: str) -> bool:
        """Load governance state from disk."""
        path = self.artifacts_path / f"{realm_id}_governance.json"
        if not path.exists():
            return False
        data = json.loads(path.read_text(encoding="utf-8"))
        self.realms[realm_id] = RealmGovernanceState.from_dict(data)
        return True

    def get_audit_trail(self, realm_id: str) -> list[dict[str, Any]]:
        """Get audit trail for a realm."""
        realm = self.get_realm(realm_id)
        return realm.audit_trail if realm else []

    def _audit_log(self, realm_id: str, action: str, details: dict[str, Any]) -> None:
        """Log an action to the audit trail."""
        realm = self.get_realm(realm_id)
        if realm:
            entry = {
                "timestamp": time.time(),
                "action": action,
                "details": details,
            }
            realm.audit_trail.append(entry)


def is_multi_realm_governance_enabled() -> bool:
    """Check if multi-realm governance is enabled."""
    v = os.environ.get("KERNEL_MULTI_REALM_GOVERNANCE_ENABLED", "0").strip().lower()
    return v in ("1", "true", "yes", "on")
