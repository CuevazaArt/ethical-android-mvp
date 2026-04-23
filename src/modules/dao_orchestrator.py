"""
DAO Orchestrator Adapter (OGA Bridge).

Decouples the Ethical Kernel from the specific DAO implementation (on-chain or mock).
Handles evidence anchoring and ethical appeals.
"""

import logging
import time
import sqlite3
import json
from typing import Any

from .evidence_safe import EvidenceSafe
from .mock_dao import MockDAO
from ..utils.db_locks import sqlite_safe_write

_log = logging.getLogger(__name__)


class DAOOrchestrator:
    """
    Oráculo de Gobernanza y Anchoring (OGA).
    Provides a standardized interface for the Kernel to interact with the DAO layer.
    """

    def __init__(self, dao_endpoint: str | None = None, db_path: str = "audit_trail.db"):
        self.endpoint = dao_endpoint
        self.db_path = db_path
        self.local_dao = MockDAO()  # Fallback to internal mock
        self.safe = EvidenceSafe()  # Handles hashing and encryption for Block 1.2
        self._policy_version = "v1.0-hybrid"
        self._init_db()

    def _init_db(self):
        """Initializes the persistent audit ledger."""
        with sqlite_safe_write(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    content TEXT,
                    episode_id TEXT,
                    timestamp REAL
                )
            ''')

    def anchor_evidence(self, payload: dict[str, Any]) -> str:
        """
        Calculates hash of evidence, encrypts it, and anchors it to the (simulated) blockchain.
        Returns the anchoring hash.
        """
        packet = self.safe.prepare_anchoring_packet(payload)
        evidence_hash = packet["evidence_hash"]

        # Persistent recording
        with sqlite_safe_write(self.db_path) as conn:
            conn.execute(
                "INSERT INTO audit_logs (type, content, episode_id, timestamp) VALUES (?, ?, ?, ?)",
                ("anchoring", f"Anchored Hash {evidence_hash}", payload.get("episode_id"), time.time())
            )

        _log.info("Evidence anchored securely. Hash: %s", evidence_hash)
        return evidence_hash

    def register_complex_audit(self, event_type: str, details: dict[str, Any], episode_id: str | None = None):
        """
        Bloque 1.1: Persists structured audit events from high-level frameworks (Claude RLHF/Audit).
        """
        details_json = json.dumps(details)
        with sqlite_safe_write(self.db_path) as conn:
            conn.execute(
                "INSERT INTO audit_logs (type, content, episode_id, timestamp) VALUES (?, ?, ?, ?)",
                (event_type, details_json, episode_id, time.time())
            )
        _log.debug("Complex audit registered: %s", event_type)

    def issue_restorative_reparation(self, case_id: str, recipient: str, amount: float) -> str:
        """
        Bloque 7.1: Simulates an EthosToken transfer from the kernel treasury to 
        compensate for an ethical failure. Persistent version.
        """
        txn_hash = f"0x_reparation_{int(time.time())}_{case_id[:4]}"
        msg = f"Restorative reparation of {amount} EthosTokens issued to {recipient} for case {case_id}."
        
        # Persistent recording (SQLite)
        with sqlite_safe_write(self.db_path) as conn:
            conn.execute(
                "INSERT INTO audit_logs (type, content, episode_id, timestamp) VALUES (?, ?, ?, ?)",
                ("reparation_payout", msg, case_id, time.time())
            )
        
        # Legacy/MockDAO internal recording
        self.local_dao.register_audit(
            type="reparation_payout",
            content=msg,
            episode_id=case_id,
        )
        
        _log.info(msg)
        return txn_hash

    def submit_appeal(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Submits an ethical escalation packet to the DAO for voting or committee review.
        """
        _log.info("Submitting appeal packet to DAO…")

        # Simulate local queuing and escalaton
        audit_rec = self.local_dao.register_escalation_case(
            summary=f"Appeal for context: {context.get('trigger_reason', 'unknown')}",
            episode_id=context.get("episode_id"),
        )

        # Simulate a mock trial outcome
        trial_result = self.local_dao.run_mock_escalation_court(
            case_uuid=context.get("episode_id", "0000"),
            audit_record_id=audit_rec.id,
            summary_excerpt=str(context),
            buffer_conflict=context.get("social_tension", 0.0) > 0.7,
        )

        return trial_result

    def get_latest_policy(self) -> dict[str, Any]:
        """
        Fetches the latest signed policy from the DAO/Oracle.
        """
        # Mock policy structure
        return {
            "version": self._policy_version,
            "whitelist": ["bypass_courtesy_in_emergency", "safe_stop"],
            "grey_zone_threshold": 0.8,
            "timestamp": time.time(),
        }

    # --- Proxy methods for MockDAO compatibility (L0/L1 legacy) ---
    def transfer_tokens(self, *args, **kwargs):
        return self.local_dao.transfer_tokens(*args, **kwargs)

    def register_audit(self, *args, **kwargs):
        return self.local_dao.register_audit(*args, **kwargs)

    async def aregister_audit(self, *args, **kwargs):
        """Async version of register_audit (Phase 9.3)."""
        import asyncio
        return await asyncio.to_thread(self.local_dao.register_audit, *args, **kwargs)

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

    def emit_solidarity_alert(self, *args, **kwargs):
        return self.local_dao.emit_solidarity_alert(*args, **kwargs)

    def get_records(self, *args, **kwargs):
        return self.local_dao.get_records(*args, **kwargs)

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
