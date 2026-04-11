"""
Mock DAO — Simulated ethical governance.

Simulates the behavior of the Ethical Oracle DAO without real blockchain.
Includes: quadratic voting, vectorial reputation, simulated smart contracts,
and Solidarity Alert Protocol.

**In-process only:** state is not distributed consensus; audit lines are for
traceability demos — see ``docs/GOVERNANCE_MOCKDAO_AND_L0.md``.

In production: replaced by smart contracts on testnet/mainnet.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import hashlib
import math


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
        return (self.experience_reputation,
                self.empathy_reputation,
                self.consistency_reputation)

    @property
    def total_reputation(self) -> float:
        return (self.experience_reputation * 0.4 +
                self.empathy_reputation * 0.35 +
                self.consistency_reputation * 0.25)


@dataclass
class Proposal:
    """A proposal submitted for voting in the DAO."""
    id: str
    title: str
    description: str
    type: str  # "ethics", "calibration", "new_value", "audit"
    votes_for: Dict[str, int] = field(default_factory=dict)
    votes_against: Dict[str, int] = field(default_factory=dict)
    status: str = "open"  # "open", "approved", "rejected"
    timestamp: str = ""


@dataclass
class AuditRecord:
    """Audit record in the DAO."""
    id: str
    type: str  # "decision", "alert", "calibration", "incident"
    content: str
    timestamp: str
    episode_id: Optional[str] = None


@dataclass
class SolidarityAlert:
    """Alert from the Solidarity Alert Protocol."""
    type: str
    location: str
    radius_meters: int
    message: str
    timestamp: str
    recipients: List[str]


class MockDAO:
    """
    Simulated Ethical Oracle DAO.

    Simulated smart contracts:
    - EthicsContract: emergency brakes
    - ConsensusContract: quadratic voting
    - ValuesProposalContract: new value proposals
    - AuditContract: audit registry
    - SolidarityAlertContract: community alerts

    Quadratic voting: the cost of n votes is n².
    Vectorial reputation: [experience, empathy, consistency].
    """

    def __init__(self):
        self.participants: Dict[str, Participant] = {}
        self.proposals: List[Proposal] = []
        self.records: List[AuditRecord] = []
        self.alerts: List[SolidarityAlert] = []
        self._proposal_counter = 0
        self._record_counter = 0

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
        Simulates the EthicsContract: verifies if an action passes the ethical filter.
        In production: smart contract with formal logic.
        """
        self.register_audit("decision", f"EthicsContract: '{action}' in context '{context}' → approved")
        return {"approved": True, "reason": "No ethical objections registered in DAO."}

    # --- ConsensusContract: Quadratic Voting ---
    def create_proposal(self, title: str, description: str,
                        type: str = "ethics") -> Proposal:
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

    def vote(self, proposal_id: str, participant_id: str,
             n_votes: int, in_favor: bool) -> dict:
        """
        Quadratic voting: cost of n votes = n².

        Args:
            proposal_id: ID of the proposal
            participant_id: who is voting
            n_votes: how many votes to cast (cost = n²)
            in_favor: True = for, False = against
        """
        prop = next((p for p in self.proposals if p.id == proposal_id), None)
        if not prop or prop.status != "open":
            return {"success": False, "reason": "Proposal not found or closed."}

        part = self.participants.get(participant_id)
        if not part:
            return {"success": False, "reason": "Participant not registered."}

        cost = n_votes ** 2
        if cost > part.available_tokens:
            max_votes = int(math.sqrt(part.available_tokens))
            return {"success": False,
                    "reason": f"Insufficient tokens. Cost: {cost}, available: {part.available_tokens}. "
                              f"Maximum possible votes: {max_votes}."}

        part.available_tokens -= cost

        weight = n_votes * part.total_reputation
        if in_favor:
            prop.votes_for[participant_id] = weight
        else:
            prop.votes_against[participant_id] = weight

        return {
            "success": True,
            "votes_cast": n_votes,
            "token_cost": cost,
            "effective_weight": round(weight, 4),
            "remaining_tokens": part.available_tokens,
        }

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
    def register_audit(self, type: str, content: str,
                       episode_id: str = None) -> AuditRecord:
        """Register an event in the audit ledger."""
        self._record_counter += 1
        rec = AuditRecord(
            id=f"AUD-{self._record_counter:04d}",
            type=type,
            content=content,
            timestamp=datetime.now().isoformat(),
            episode_id=episode_id,
        )
        self.records.append(rec)
        return rec

    def register_escalation_case(self, summary: str,
                                 episode_id: Optional[str] = None) -> AuditRecord:
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
    ) -> Dict[str, Any]:
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

        out: Dict[str, Any] = {
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
    def emit_solidarity_alert(self, type: str, location: str,
                               radius: int = 500,
                               message: str = "") -> SolidarityAlert:
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
    def get_records(self, type: str = None, limit: int = 10) -> List[AuditRecord]:
        """Get filtered audit records."""
        recs = self.records if not type else [r for r in self.records if r.type == type]
        return recs[-limit:]

    def export_state(self) -> Dict[str, Any]:
        """V12.3 — serialize proposals + participants for kernel checkpoint (off-chain)."""
        return {
            "proposal_counter": self._proposal_counter,
            "participants": [
                asdict(p) for p in sorted(self.participants.values(), key=lambda x: x.id)
            ],
            "proposals": [asdict(p) for p in self.proposals],
        }

    def import_state(self, data: Optional[Dict[str, Any]]) -> None:
        """Restore proposals + participants from :meth:`export_state`."""
        if not data:
            return
        self._proposal_counter = max(0, int(data.get("proposal_counter", 0)))
        participants_raw: List[Dict[str, Any]] = list(data.get("participants") or [])
        proposals_raw: List[Dict[str, Any]] = list(data.get("proposals") or [])
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

    def format_status(self) -> str:
        """Format current DAO status for display."""
        lines = [
            f"\n{'=' * 70}",
            f"  ETHICAL ORACLE DAO — STATUS",
            f"{'=' * 70}",
            f"  Participants: {len(self.participants)}",
            f"  Total proposals: {len(self.proposals)}",
            f"  Audit records: {len(self.records)}",
            f"  Solidarity alerts: {len(self.alerts)}",
        ]

        open_proposals = [p for p in self.proposals if p.status == "open"]
        if open_proposals:
            lines.append(f"\n  Open proposals:")
            for p in open_proposals:
                lines.append(f"    {p.id}: {p.title}")

        latest = self.get_records(limit=5)
        if latest:
            lines.append(f"\n  Latest records:")
            for r in latest:
                lines.append(f"    [{r.type}] {r.content[:60]}")

        lines.append(f"{'─' * 70}")
        return "\n".join(lines)
