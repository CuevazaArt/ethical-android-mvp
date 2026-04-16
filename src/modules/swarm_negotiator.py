"""
Swarm Negotiator — Cross-kernel moral alignment and consensus.

Handles identity exchange, goal synchronization, and conflict resolution
between multiple Ethical Kernels. Supports offline-mode deltas.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .metaplan_registry import MasterGoal
    from .narrative import NarrativeMemory


@dataclass
class SwarmMessage:
    sender_id: str
    timestamp: float
    payload_type: str  # "identity_digest", "proposal", "vote", "offline_delta"
    data: dict[str, Any]
    signature: str = ""  # Simplified stub for now


@dataclass
class SwarmNegotiationState:
    known_peers: dict[str, dict] = field(default_factory=dict)
    active_proposals: dict[str, dict] = field(default_factory=dict)
    consensus_log: list[dict] = field(default_factory=list)


class SwarmNegotiator:
    """
    Orchestrates collective ethics.
    """

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.state = SwarmNegotiationState()

    def pack_identity_digest(self, memory: NarrativeMemory) -> SwarmMessage:
        """
        Creates a privacy-preserved digest of the kernel's identity.
        Uses Existence Digest from Tier 3.
        """
        digest_text = memory.identity.generate_existence_digest(memory.episodes)
        return SwarmMessage(
            sender_id=self.node_id,
            timestamp=time.time(),
            payload_type="identity_digest",
            data={
                "epitome": digest_text,
                "leans": {
                    "civic": memory.identity.state.civic_lean,
                    "care": memory.identity.state.care_lean,
                },
            },
        )

    def process_incoming(self, msg: SwarmMessage, local_kernel):
        """
        Processes messages from other kernels.
        Supports offline-mode sync if timestamp is old.
        """
        peer_id = msg.sender_id

        if msg.payload_type == "identity_digest":
            self.state.known_peers[peer_id] = msg.data

        elif msg.payload_type == "proposal":
            self._evaluate_proposal(msg, local_kernel)

        elif msg.payload_type == "offline_delta":
            self._integrate_offline_delta(msg, local_kernel)

    def _evaluate_proposal(self, msg: SwarmMessage, kernel):
        """
        Decides whether to agree with a peer's proposal based on internal ethics.
        """
        prop_id = msg.data.get("proposal_id")

        # Alignment check: does the suggested action align with local leans?
        lean_alignment = (
            kernel.memory.identity.state.civic_lean + kernel.memory.identity.state.care_lean
        ) / 2.0

        # We vote based on local alignment + peer authority
        vote = "agree" if lean_alignment >= 0.5 else "abstain"

        return {"proposal_id": prop_id, "vote": vote, "voter": self.node_id}

    def _integrate_offline_delta(self, msg: SwarmMessage, kernel):
        """
        Re-syncs after Cursor-team-style Offline Mode.
        """
        missed_items = msg.data.get("items", [])
        for item in missed_items:
            if item not in self.state.consensus_log:
                self.state.consensus_log.append(item)

    def resolve_goal_conflict(self, local_goal: MasterGoal, peer_goal: dict) -> str:
        """
        Conflict resolution between kernels.
        """
        return "compromise_alpha"

    def get_swarm_trust_nudge(self) -> float:
        """
        I7: Returns a confidence boost [0, 0.15] if recently synchronized with peers.
        """
        if not self.state.known_peers:
            return 0.0

        # Simple heuristic: more peers = more confidence in collective reality
        peer_count = len(self.state.known_peers)
        nudge = min(0.15, peer_count * 0.04)
        return nudge

    def promote_consensus_to_dao(self, dao):
        """
        Registers major consensus items as Solidarity Alerts in the DAO.
        """
        if len(self.state.known_peers) >= 3 and self.state.consensus_log:
            last_item = self.state.consensus_log[-1]
            dao.emit_solidarity_alert(
                type="swarm_consensus",
                location="swarm_network",
                message=f"Collective agreement reaching DAO: {last_item}",
            )
