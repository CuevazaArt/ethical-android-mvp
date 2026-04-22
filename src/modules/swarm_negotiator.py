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

    def cast_distributed_vote(
        self, proposal_id: str, action: str, signals: dict, peers: list[str]
    ) -> bool:
        """
        Bloque 6.2: Asks peers to vote on a candidate action.
        Returns True if consensus is reached (>50% agreement).
        Always records the vote log so apply_swarm_justice can process negligent peers.
        """
        votes = []
        for peer in peers:
            # Mock Peer Voting: some nodes agree, some abstain/dissent based on ID and risk
            risk = signals.get("risk", 0.5)
            # PEER_LAN_03 is always a bit 'rebellious' or 'faulty' in this mock
            if peer == "PEER_LAN_03":
                vote = "abstain" if risk < 0.7 else "disagree"
            else:
                vote = "agree" if risk < 0.8 else "abstain"
            votes.append(vote)

        agreements = votes.count("agree")

        # Bloque 7.2: Weighted consensus logic
        total_weight = 0.0
        agreement_weight = 0.0

        # Peer reputation weighting (I1/I7 Integration)
        for i, peer in enumerate(peers):
            # In a full system, we fetch rep from SwarmOracle
            # For this MVP, we assume high trust for known nodes
            rep = 0.9 if peer.startswith("NODE") else 0.5
            weight = 1.0 if rep > 0.6 else 0.3
            total_weight += weight
            if votes[i] == "agree":
                agreement_weight += weight

        is_consensus = agreement_weight > (total_weight / 2.0)

        # Always record the vote entry so apply_swarm_justice can process any negligent nodes
        voter_map = {i: peer for i, peer in enumerate(peers)}
        self.state.consensus_log.append(
            {
                "proposal_id": proposal_id,
                "action": action,
                "votes": votes,
                "voters": voter_map,
                "agreement_weight": agreement_weight,
                "timestamp": time.time(),
            }
        )

        return is_consensus

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
                message=f"[SIMULATION_consensus] Collective agreement reached (MOCK): {last_item}",
            )

    def apply_swarm_justice(self, dao, oracle, case_ref: str):
        """
        Bloque 7.1 & 7.2: Analyzes consensus history to punish deviants and
        compensate for sensory negligence.
        """
        if not self.state.consensus_log:
            return

        from .reparation_vault import (
            execute_simulated_payout,
            register_slashing_intent,
            reparation_vault_mock_enabled,
        )

        last_item = self.state.consensus_log[-1]
        proposal_id = last_item.get("proposal_id", "unknown")
        votes = last_item.get("votes", [])
        action = last_item.get("action", "unknown")

        # We define JUSTICE if we have consensus (which is already the case if it's in the log)
        # nodes that voted 'abstain' or 'disagree' when the swarm agreed on a 'danger' signal
        # are considered 'sensors failed' or 'negligent'.

        for i, vote in enumerate(votes):
            if vote in ["abstain", "disagree"]:
                # Bloque 7.2 Hardening: Map votes back to actual sender IDs
                node_id = last_item.get("voters", {}).get(i, f"unknown_node_{i}")

                # Byzantine Protection: Check if the dissent was based on local Safety Veto
                from .absolute_evil import AbsoluteEvilDetector

                ae = AbsoluteEvilDetector()
                is_safe_dissent = ae._evaluate_chat_text_lexical(action).blocked

                if is_safe_dissent:
                    # Dissenter was right! No slashing.
                    continue

                # Reputation-based Grace (Bloque 7.3):
                current_rep = oracle.get_reputation_hint(node_id)
                penalty = 0.15
                if current_rep > 0.92:
                    penalty = 0.05  # Reduced penalty for stable nodes

                # Bloque 7.2: Slashing
                oracle.apply_slashing(node_id, penalty)
                register_slashing_intent(
                    dao,
                    node_id,
                    f"Consensus mismatch on prop {proposal_id} (attributable). Swarm agreed, Peer failed.",
                )

                # Bloque 7.1: Reparation (Pilar 3 - Restorative)
                if reparation_vault_mock_enabled():
                    execute_simulated_payout(
                        dao,
                        case_ref=case_ref,
                        recipient_id="community_01",
                        amount=20,  # EthosTokens
                    )
                else:
                    # Direct DAO transfer when vault mock is disabled (always keep community whole)
                    dao.transfer_tokens("ethics_panel_01", "community_01", 20)
