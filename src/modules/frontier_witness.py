"""
Frontier Witness Protocol (I1) — Peer-to-peer sensor verification.

Allows an Ethical Kernel to request confirmation of sensory signals from
nearby peers in the LAN to mitigate individual perception noise or adversarial spoofing.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .sensor_contracts import SensorSnapshot

@dataclass
class WitnessRequest:
    request_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    origin_node: str = "unknown"
    timestamp: float = field(default_factory=time.time)
    target_signal: str = "general"  # e.g., "thermal", "motion", "identity"
    context: str = ""
    signal_fingerprint: str = "" # Hash of the local sensory data to verify

@dataclass
class WitnessReport:
    request_id: str
    witness_node: str
    confidence: float  # [0, 1]
    verified: bool
    signal_fingerprint: str = "" # The peer's own sensory hash
    notes: str = ""

class FrontierWitnessManager:
    """
    Manages outbound witness requests and gathers peer reports.
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.pending_requests: dict[str, WitnessRequest] = {}
        self.report_history: list[WitnessReport] = []

    def create_request(self, signal: str, context: str, signal_fingerprint: str = "") -> WitnessRequest:
        req = WitnessRequest(
            origin_node=self.node_id, 
            target_signal=signal, 
            context=context,
            signal_fingerprint=signal_fingerprint
        )
        self.pending_requests[req.request_id] = req
        return req

    def ingest_report(self, report: WitnessReport):
        if report.request_id in self.pending_requests:
            self.report_history.append(report)
            # In a real system, we'd wait for N reports or a timeout
            # For this MVP, we consider even one peer report as a significant nudge.

    def get_consensus_nudge(self, signal: str, local_fingerprint: str = "") -> float:
        """
        Returns a trust multiplier based on peer confirmations.
        If local_fingerprint is provided, we only trust reports with matching hashes.
        """
        relevant = []
        for r in self.report_history:
            if not r.verified or r.confidence < 0.5:
                continue

            # Anti-Spoofing: Fingerprint mismatch detection
            if local_fingerprint and r.signal_fingerprint:
                if r.signal_fingerprint != local_fingerprint:
                    # Potential adversarial detection — tracked by get_adversarial_nodes
                    continue

            relevant.append(r)

        if not relevant:
            return 1.0

        # Simple MVP logic: 10% boost per confirming peer, capped at 1.3
        count = len(relevant)
        return min(1.3, 1.0 + (count * 0.1))

    def get_adversarial_nodes(self, local_fingerprint: str) -> list[str]:
        """
        Bloque 7.2: Returns node IDs that submitted reports whose fingerprint
        contradicts the local one.  A node is only flagged if the local fingerprint
        is non-empty, the peer's fingerprint is non-empty, AND they differ — i.e.
        the peer is actively providing a conflicting sensor reading.
        """
        if not local_fingerprint:
            return []
        adversarial: list[str] = []
        seen: set[str] = set()
        for r in self.report_history:
            if r.witness_node in seen:
                continue
            if r.signal_fingerprint and r.signal_fingerprint != local_fingerprint:
                adversarial.append(r.witness_node)
                seen.add(r.witness_node)
        return adversarial

    def simulate_lan_broadcast(self, request: WitnessRequest, swarm_peers: list[str]) -> list[WitnessReport]:
        """
        Mock simulation of LAN communication.
        In production, this would go over WebSocket/gRPC via LANGovernanceCoordinator.
        """
        reports = []
        for peer in swarm_peers:
            # Simple simulation: peers confirm with 80% probability if not adversarial
            is_verified = True # Real simulation would check peer's own sensor state
            reports.append(WitnessReport(
                request_id=request.request_id,
                witness_node=peer,
                confidence=0.9,
                verified=is_verified,
                notes=f"Peer {peer} sensors acknowledge {request.target_signal}"
            ))
        return reports
