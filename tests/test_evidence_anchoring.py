"""
Tests for Block 1.2: Encrypted Evidence and Anchoring (REO).
"""

import logging

import pytest

from src.modules.dao_orchestrator import DAOOrchestrator
from src.modules.evidence_safe import EvidenceSafe


def test_evidence_safe_invalid_fernet_key_falls_back_with_warning(caplog: pytest.LogCaptureFixture) -> None:
    """Invalid env-style keys must not crash init; operator sees WARNING (Fase 15 / Boy Scout)."""
    with caplog.at_level(logging.WARNING):
        safe = EvidenceSafe(fernet_key="nope_not_a_fernet_key")
    assert safe._is_transient is True
    assert "transient" in caplog.text.lower() or "invalid" in caplog.text.lower()


def test_evidence_safe_hashing():
    safe = EvidenceSafe()
    payload = {"episode_id": "EP-001", "action": "test", "score": 0.9}
    h1 = safe.hash_payload(payload)

    # Deterministic check (canonical JSON)
    payload_reordered = {"score": 0.9, "episode_id": "EP-001", "action": "test"}
    h2 = safe.hash_payload(payload_reordered)

    assert h1 == h2
    assert len(h1) == 64  # SHA-256


def test_evidence_safe_encryption_decryption():
    # Use a fixed key for reproducible test
    from cryptography.fernet import Fernet

    key = Fernet.generate_key().decode()
    safe = EvidenceSafe(fernet_key=key)

    payload = {"secret": "private data", "id": 123}
    blob = safe.encrypt_payload(payload)

    decrypted = safe.decrypt_payload(blob)
    assert decrypted == payload


def test_dao_orchestrator_anchoring_integration():
    orchestrator = DAOOrchestrator()
    payload = {"episode_id": "EP-INT-001", "data": "audit this"}

    e_hash = orchestrator.anchor_evidence(payload)

    # Verify it was registered in local mock DAO
    audit_records = orchestrator.local_dao.records
    anchoring_record = next(r for r in audit_records if r.type == "anchoring")

    assert e_hash in anchoring_record.content
    assert "Blob size" in anchoring_record.content
