"""
DAO Orchestrator Adapter (OGA Bridge).

Decouples the Ethical Kernel from the specific DAO implementation (on-chain or mock).
Handles evidence anchoring and ethical appeals.
"""

import hashlib
import json
import time
from typing import Any, Dict, Optional
from .mock_dao import MockDAO


class DAOOrchestrator:
    """
    Oráculo de Gobernanza y Anchoring (OGA).
    Provides a standardized interface for the Kernel to interact with the DAO layer.
    """

    def __init__(self, dao_endpoint: Optional[str] = None):
        self.endpoint = dao_endpoint
        self.local_dao = MockDAO()  # Fallback to internal mock
        self._policy_version = "v1.0-hybrid"

    def anchor_evidence(self, payload: Dict[str, Any]) -> str:
        """
        Calculates hash of evidence and anchors it to the (simulated) blockchain.
        Returns the anchoring hash.
        """
        evidence_json = json.dumps(payload, sort_keys=True)
        evidence_hash = hashlib.sha256(evidence_json.encode()).hexdigest()
        
        # In a real OGA, this would be a POST to the anchoring registry
        timestamp = time.time()
        self.local_dao.register_audit(
            type="anchoring",
            content=f"Anchored hash {evidence_hash[:16]}... (simulated blockchain)",
            episode_id=payload.get("episode_id")
        )
        
        print(f"[OGA] Evidence anchored. Hash: {evidence_hash}")
        return evidence_hash

    def submit_appeal(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submits an ethical escalation packet to the DAO for voting or committee review.
        """
        print("[OGA] Submitting appeal packet to DAO...")
        
        # Simulate local queuing and escalaton
        audit_rec = self.local_dao.register_escalation_case(
            summary=f"Appeal for context: {context.get('trigger_reason', 'unknown')}",
            episode_id=context.get("episode_id")
        )
        
        # Simulate a mock trial outcome
        trial_result = self.local_dao.run_mock_escalation_court(
            case_uuid=context.get("episode_id", "0000"),
            audit_record_id=audit_rec.id,
            summary_excerpt=str(context),
            buffer_conflict=context.get("social_tension", 0.0) > 0.7
        )
        
        return trial_result

    def get_latest_policy(self) -> Dict[str, Any]:
        """
        Fetches the latest signed policy from the DAO/Oracle.
        """
        # Mock policy structure
        return {
            "version": self._policy_version,
            "whitelist": ["bypass_courtesy_in_emergency", "safe_stop"],
            "grey_zone_threshold": 0.8,
            "timestamp": time.time()
        }

    # --- Proxy methods for MockDAO compatibility (L0/L1 legacy) ---
    def register_audit(self, *args, **kwargs):
        return self.local_dao.register_audit(*args, **kwargs)

    def create_proposal(self, *args, **kwargs):
        return self.local_dao.create_proposal(*args, **kwargs)

    def vote(self, *args, **kwargs):
        return self.local_dao.vote(*args, **kwargs)

    def resolve_proposal(self, *args, **kwargs):
        return self.local_dao.resolve_proposal(*args, **kwargs)

    def export_state(self, *args, **kwargs):
        return self.local_dao.export_state(*args, **kwargs)

    def import_state(self, *args, **kwargs):
        return self.local_dao.import_state(*args, **kwargs)

    def format_status(self, *args, **kwargs):
        return self.local_dao.format_status(*args, **kwargs)

    @property
    def proposals(self):
        return self.local_dao.proposals

    @proposals.setter
    def proposals(self, value):
        self.local_dao.proposals = value

    @property
    def participants(self):
        return self.local_dao.participants

    @participants.setter
    def participants(self, value):
        self.local_dao.participants = value

    @property
    def _record_counter(self):
        return self.local_dao._record_counter

    @_record_counter.setter
    def _record_counter(self, value):
        self.local_dao._record_counter = value

    @property
    def alerts(self):
        return self.local_dao.alerts

    @alerts.setter
    def alerts(self, value):
        self.local_dao.alerts = value

    @property
    def records(self):
        return self.local_dao.records

    @records.setter
    def records(self, value):
        self.local_dao.records = value
