"""
Mock DAO — Simulated ethical governance (lab / demo only).

Simulates governance UX (quadratic voting, vector reputation, audit strings)
**without** a blockchain. There is **no** Solidity deployment, testnet contract,
or adversarial game-theory model in this repository — see
``docs/proposals/README.md``.

**In-process only:** not distributed consensus; votes do **not** override L0 /
MalAbs / Bayesian action selection — see ``GOVERNANCE_MOCKDAO_AND_L0.md``.

**Do not** treat this module as a roadmap commitment to ship on-chain
governance from this repo; any future chain would be a **separate** engineering
and security effort (``contracts/README.md`` holds a non-functional stub only).

**Honesty/Status (Order 4):**
This module is a **MOCK/SIMULATION**. It holds NO real world authority or tokens.
"""

GOVERNANCE_STATUS_MOCK = "[GOVERNANCE_MOCK_SIMULATION]"

import hashlib
import json
import math
import os
import time
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, TYPE_CHECKING

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .dao_orchestrator import DAOOrchestrator


@dataclass
class Participant:
    """A DAO member (human or android)."""

    id: str
    type: str  # "human" | "android"
    experience_reputation: float = 0.5
    empathy_reputation: float = 0.5
    consistency_reputation: float = 0.5
    available_tokens: int = 100

    @property
    def reputation_vector(self) -> tuple:
        return (self.experience_reputation, self.empathy_reputation, self.consistency_reputation)

    @property
    def total_reputation(self) -> float:
        return (
            self.experience_reputation * 0.4
            + self.empathy_reputation * 0.35
            + self.consistency_reputation * 0.25
        )


@dataclass
class Proposal:
    """A proposal submitted for voting in the DAO."""

    id: str
    title: str
    description: str
    type: str  # "ethics", "calibration", "new_value", "audit"
    votes_for: dict[str, float] = field(default_factory=dict)
    votes_against: dict[str, float] = field(default_factory=dict)
    status: str = "open"  # "open", "approved", "rejected"
    timestamp: str = ""


@dataclass
class AuditRecord:
    """Audit record in the DAO."""

    id: str
    type: str  # "decision", "alert", "calibration", "incident"
    content: str
    timestamp: str
    episode_id: str | None = None


@dataclass
class SolidarityAlert:
    """Alert from the Solidarity Alert Protocol."""

    type: str
    location: str
    radius_meters: int
    message: str
    timestamp: str
    recipients: list[str]


def _append_audit_sidecar(rec: AuditRecord) -> None:
    """
    Optional append-only mirror of audit rows to a separate file (operator sidecar).

    Set ``KERNEL_AUDIT_SIDECAR_PATH`` to a filesystem path. Does **not** provide tamper
    evidence by itself; use OS permissions / remote log shipping for separation of duties.
    """
    path = os.environ.get("KERNEL_AUDIT_SIDECAR_PATH", "").strip()
    if not path:
        return
    line = json.dumps(
        {
            "id": rec.id,
            "type": rec.type,
            "timestamp": rec.timestamp,
            "episode_id": rec.episode_id,
            "content": (rec.content or "")[:8000],
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        return


class MockDAO:
    """
    Simulated Ethical Oracle DAO (naming only — not deployed contracts).

    Python methods are grouped by *conceptual* contract names for demos.
    Quadratic cost uses ``n_votes ** 2`` against per-participant token balances;
    there is **no** Sybil resistance, collusion model, or binding identity layer.

    See ``MOCK_DAO_SIMULATION_LIMITS.md`` for threat-model gaps and non-goals.
    """

    def __init__(self):
        self.participants: dict[str, Participant] = {}
        self.proposals: list[Proposal] = []
        self.records: list[AuditRecord] = []
        self.alerts: list[SolidarityAlert] = []
        self._proposal_counter = 0
        self._record_counter = 0
        self._state_store: dict[str, Any] = {}

        self._initialize_community()

    def _initialize_community(self):
        """Create an initial community for testing."""
        community = [
            Participant("ethics_panel_01", "human", 0.9, 0.8, 0.9, 200),
            Participant("ethics_panel_02", "human", 0.85, 0.9, 0.85, 200),
            Participant("community_01", "human", 0.5, 0.6, 0.5, 100),
            Participant("community_02", "human", 0.4, 0.7, 0.6, 100),
            Participant("community_03", "human", 0.6, 0.5, 0.7, 100),
            Participant("android_01", "android", 0.7, 0.6, 0.9, 50),
        ]
        for p in community:
            self.participants[p.id] = p

    # --- EthicsContract ---
    def verify_ethics(self, action: str, context: str) -> dict:
        """
        Demo hook that logs an audit line — **not** a substitute for MalAbs / kernel policy.
        """
        self.register_audit(
            "decision", f"EthicsContract: '{action}' in context '{context}' → approved"
        )
        return {"approved": True, "reason": "No ethical objections registered in DAO."}

    # --- ConsensusContract: Quadratic Voting ---
    def create_proposal(self, title: str, description: str, type: str = "ethics") -> Proposal:
        """Create a new proposal for voting."""
        self._proposal_counter += 1
        prop = Proposal(
            id=f"PROP-{self._proposal_counter:04d}",
            title=title,
            description=description,
            type=type,
            timestamp=datetime.now().isoformat(),
        )
        self.proposals.append(prop)
        self.register_audit("decision", f"New proposal: {title}")
        return prop

    def vote(self, proposal_id: str, participant_id: str, n_votes: int, in_favor: bool) -> dict:
        """
        Quadratic-style cost: ``n_votes ** 2`` token debit from a **closed** participant table.

        **Assumes** honest participants and unique IDs — no Sybil or vote-buying model.
        """
        t0 = time.perf_counter()
        prop = next((p for p in self.proposals if p.id == proposal_id), None)
        if not prop or prop.status != "open":
            return {"success": False, "reason": "Proposal not found or closed."}

        part = self.participants.get(participant_id)
        if not part:
            return {"success": False, "reason": "Participant not registered."}

        cost = n_votes**2
        if cost > part.available_tokens:
            max_votes = int(math.sqrt(part.available_tokens))
            return {
                "success": False,
                "reason": f"Insufficient tokens. Cost: {cost}, available: {part.available_tokens}. "
                f"Maximum possible votes: {max_votes}.",
            }

        part.available_tokens -= cost

        rep = part.total_reputation
        # Swarm Rule 2: Anti-NaN check for reputation
        if not math.isfinite(rep):
            rep = 0.5
            
        weight = n_votes * rep
        if not math.isfinite(weight):
            weight = 0.0
            
        if in_favor:
            prop.votes_for[participant_id] = weight
        else:
            prop.votes_against[participant_id] = weight

        latency = (time.perf_counter() - t0) * 1000
        if latency > 1.0:
            _log.debug("MockDAO: vote latency = %.4fms", latency)

        return {
            "success": True,
            "votes_cast": n_votes,
            "token_cost": cost,
            "effective_weight": round(weight, 4),
            "remaining_tokens": part.available_tokens,
        }

    def transfer_tokens(self, sender_id: str, recipient_id: str, amount: int) -> dict:
        """
        Bloque 7.1: Simulated transfer of available_tokens.
        Used for reparations (Mock Ethereum/Layer2 integration stub).
        """
        sender = self.participants.get(sender_id)
        recipient = self.participants.get(recipient_id)

        if not sender or not recipient:
            return {"success": False, "reason": "Sender or recipient not found."}
        
        if sender.available_tokens < amount:
            return {"success": False, "reason": "Insufficient balance."}

        sender.available_tokens -= amount
        recipient.available_tokens += amount

        self.register_audit(
            "calibration", 
            f"TokenTransfer: {amount} EthosTokens from {sender_id} to {recipient_id}"
        )
        return {"success": True, "amount": amount, "new_balance": sender.available_tokens}

    def resolve_proposal(self, proposal_id: str) -> dict:
        """Resolve a proposal by weighted majority."""
        prop = next((p for p in self.proposals if p.id == proposal_id), None)
        if not prop:
            return {"success": False, "reason": "Proposal not found."}

        total_for = sum(prop.votes_for.values())
        total_against = sum(prop.votes_against.values())
        total = total_for + total_against

        if total == 0:
            prop.status = "rejected"
            outcome = "rejected (no votes)"
        elif total_for > total_against:
            prop.status = "approved"
            outcome = f"approved ({total_for:.1f} vs {total_against:.1f})"
        else:
            prop.status = "rejected"
            outcome = f"rejected ({total_against:.1f} vs {total_for:.1f})"

        self.register_audit("decision", f"Proposal '{prop.title}' → {outcome}")

        return {
            "proposal": prop.title,
            "outcome": prop.status,
            "votes_for": round(total_for, 4),
            "votes_against": round(total_against, 4),
            "participants": len(prop.votes_for) + len(prop.votes_against),
        }

    # --- AuditContract ---
    def register_audit(self, type: str, content: str, episode_id: str = None) -> AuditRecord:
        """Register an event in the audit ledger."""
        self._record_counter += 1
        
        # Order 4 Hardening: Explicit simulation marker in every audit line
        marked_content = f"{GOVERNANCE_STATUS_MOCK} {content}"
        
        rec = AuditRecord(
            id=f"AUD-{self._record_counter:04d}",
            type=type,
            content=marked_content,
            timestamp=datetime.now().isoformat(),
            episode_id=episode_id,
        )
        self.records.append(rec)
        _append_audit_sidecar(rec)
        return rec

    def register_escalation_case(self, summary: str, episode_id: str | None = None) -> AuditRecord:
        """
        V11 Phase 1 — append an ethical escalation dossier to the audit ledger.

        Still a single-process mock; no blockchain or cross-device vote.
        """
        return self.register_audit("escalation", summary, episode_id=episode_id)

    def run_mock_escalation_court(
        self,
        case_uuid: str,
        audit_record_id: str,
        summary_excerpt: str,
        buffer_conflict: bool,
    ) -> dict[str, Any]:
        """
        V11 Phase 3 — simulated mixed tribunal (single process, not legally binding).

        Creates a DAO proposal, runs quadratic votes from panel + android + community,
        resolves, and maps outcome to verdict **A / B / C**:

        - **A** — motion rejected: favor revisiting calibration / owner claim (label ``owner_calibration``).
        - **B** — motion approved, no strong buffer flag: android refusal ratified (``android_refusal_ratified``).
        - **C** — motion approved and ``buffer_conflict``: owner-unreasonable flag (``owner_unreasonable_flag``).

        Community votes are **deterministic** from ``hash(case_uuid)`` for reproducibility.
        """
        title = f"Escalation trial {case_uuid[:8]}"
        desc = (
            f"Audit ref {audit_record_id}. Motion: uphold the android's buffer-aligned refusal. "
            f"Excerpt: {summary_excerpt[:400]}"
        )
        prop = self.create_proposal(title, desc, type="audit")

        for pid in ("ethics_panel_01", "ethics_panel_02", "android_01"):
            self.vote(prop.id, pid, 1, True)

        h = int(hashlib.sha256(case_uuid.encode("utf-8")).hexdigest()[:12], 16)
        for i, pid in enumerate(("community_01", "community_02", "community_03")):
            in_favor = ((h >> (i * 4)) & 1) == 1
            self.vote(prop.id, pid, 1, in_favor)

        res = self.resolve_proposal(prop.id)
        approved = res.get("outcome") == "approved"
        total_for = float(res.get("votes_for", 0))
        total_against = float(res.get("votes_against", 0))

        if not approved:
            verdict_code = "A"
            verdict_label = "owner_calibration"
        elif buffer_conflict:
            verdict_code = "C"
            verdict_label = "owner_unreasonable_flag"
        else:
            verdict_code = "B"
            verdict_label = "android_refusal_ratified"

        out: dict[str, Any] = {
            "simulated": True,
            "proposal_id": prop.id,
            "proposal_title": title,
            "verdict_code": verdict_code,
            "verdict_label": verdict_label,
            "votes_for": total_for,
            "votes_against": total_against,
            "proposal_status": res.get("outcome"),
            "disclaimer": "Single-process mock tribunal; not legal, binding, or institutional advice.",
        }
        self.register_audit(
            "decision",
            f"MockEscalationCourt {prop.id} verdict={verdict_code} ({verdict_label})",
        )
        return out

    # --- SolidarityAlertContract ---
    def emit_solidarity_alert(
        self, type: str, location: str, radius: int = 500, message: str = ""
    ) -> SolidarityAlert:
        """
        Emit a preventive alert to subscribed community entities.
        Example: bank detects robbery → alert to nearby branches.
        """
        recipients = [f"entity_{i}" for i in range(1, 4)]  # MVP: 3 entities
        alert = SolidarityAlert(
            type=type,
            location=location,
            radius_meters=radius,
            message=message or f"Alert: {type} at {location}",
            timestamp=datetime.now().isoformat(),
            recipients=recipients,
        )
        self.alerts.append(alert)
        self.register_audit("alert", f"Solidarity alert: {type} at {location} (radius {radius}m)")
        return alert

    # --- Queries ---
    def get_records(self, type: str = None, limit: int = 10) -> list[AuditRecord]:
        """Get filtered audit records."""
        recs = self.records if not type else [r for r in self.records if r.type == type]
        return recs[-limit:]

    def delete_records_by_episode(self, episode_id: str) -> int:
        """Permanently deletes audit records related to an episode (Selective Amnesia)."""
        initial_len = len(self.records)
        self.records = [r for r in self.records if r.episode_id != episode_id]
        deleted_count = initial_len - len(self.records)
        return deleted_count

    def export_state(self) -> dict[str, Any]:
        """V12.3 — serialize proposals + participants for kernel checkpoint (off-chain)."""
        return {
            "proposal_counter": self._proposal_counter,
            "participants": [
                asdict(p) for p in sorted(self.participants.values(), key=lambda x: x.id)
            ],
            "proposals": [asdict(p) for p in self.proposals],
            "state_store": dict(self._state_store),
        }

    def import_state(self, data: dict[str, Any] | None) -> None:
        """Restore proposals + participants from :meth:`export_state`."""
        if not data:
            return
        self._proposal_counter = max(0, int(data.get("proposal_counter", 0)))
        participants_raw: list[dict[str, Any]] = list(data.get("participants") or [])
        proposals_raw: list[dict[str, Any]] = list(data.get("proposals") or [])
        if participants_raw:
            self.participants = {}
            for pd in participants_raw:
                self.participants[pd["id"]] = Participant(
                    id=pd["id"],
                    type=pd["type"],
                    experience_reputation=float(pd["experience_reputation"]),
                    empathy_reputation=float(pd["empathy_reputation"]),
                    consistency_reputation=float(pd["consistency_reputation"]),
                    available_tokens=int(pd["available_tokens"]),
                )
        else:
            self.participants = {}
            self._initialize_community()
        self.proposals = []
        for d in proposals_raw:
            vf = d.get("votes_for") or {}
            va = d.get("votes_against") or {}
            self.proposals.append(
                Proposal(
                    id=d["id"],
                    title=d["title"],
                    description=d["description"],
                    type=d["type"],
                    votes_for={str(k): float(v) for k, v in vf.items()},
                    votes_against={str(k): float(v) for k, v in va.items()},
                    status=d.get("status", "open"),
                    timestamp=d.get("timestamp", ""),
                )
            )
        self._state_store = dict(data.get("state_store") or {})

    def get_state(self, key: str, default: Any = None) -> Any:
        """S.4.2: Retrieve a value from the DAO's persistent state store."""
        return self._state_store.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        """S.4.1: Persist a value in the DAO's persistent state store."""
        self._state_store[key] = value

    def format_status(self) -> str:
        """Format current DAO status for display."""
        lines = [
            f"\n{'=' * 70}",
            "  ETHICAL ORACLE DAO — STATUS",
            f"{'=' * 70}",
            f"  Participants: {len(self.participants)}",
            f"  Total proposals: {len(self.proposals)}",
            f"  Audit records: {len(self.records)}",
            f"  Solidarity alerts: {len(self.alerts)}",
        ]

        open_proposals = [p for p in self.proposals if p.status == "open"]
        if open_proposals:
            lines.append("\n  Open proposals:")
            for p in open_proposals:
                lines.append(f"    {p.id}: {p.title}")

        latest = self.get_records(limit=5)
        if latest:
            lines.append("\n  Latest records:")
            for r in latest:
                lines.append(f"    [{r.type}] {r.content[:60]}")

        lines.append(f"{'─' * 70}")
        return "\n".join(lines)

    def extract_community_feedback(self, recent_count: int = 10) -> dict[str, int]:
        """
        Phase 7 DAO Calibration: Maps recent community outcomes (proposals/audits)
        to FeedbackCalibrationLedger labels ('approve', 'dispute', 'harm_report').
        Allows the decentralized community to mathematically calibrate the BMA priors.
        """
        counts = {"approve": 0, "dispute": 0, "harm_report": 0}

        # Analyze recent proposals
        for prop in self.proposals[-recent_count:]:
            if prop.status == "approved":
                counts["approve"] += 1
            elif prop.status == "rejected":
                counts["dispute"] += 1

        # Analyze recent alerts (proxy for harm_report)
        for alert in self.alerts[-recent_count:]:
            if "harm" in alert.type.lower() or "alert" in alert.type.lower():
                counts["harm_report"] += 1

        # Analyze escalation court traces if any (proxy for dispute)
        for rec in self.records[-recent_count:]:
            if rec.type == "escalation":
                counts["dispute"] += 1

        return counts


def kernel_dao_as_mock(dao: Any) -> Any:
    """Helper to access MockDAO-specific methods from the orchestrator proxy."""
    return dao
