"""Tests for append-only audit chain (hash link + optional HMAC)."""

from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
from typing import Any

import pytest
from src.modules import audit_chain_log as acl


def _canon(obj: dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _verify_record(obj: dict[str, Any], *, prev_line: str, secret: str | None) -> None:
    assert obj["prev_line_sha256"] == prev_line
    payload = obj["payload"]
    assert obj["payload_sha256"] == _sha256_hex(_canon(payload))
    inner = {k: v for k, v in obj.items() if k not in ("line_sha256", "hmac_sha256")}
    inner_canon = _canon(inner)
    assert obj["line_sha256"] == _sha256_hex(inner_canon)
    if secret:
        assert (
            obj["hmac_sha256"]
            == hmac.new(
                secret.encode("utf-8"),
                inner_canon.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
        )


def test_append_audit_event_chain_and_hmac(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    log_path = tmp_path / "chain.jsonl"
    secret = "test-secret-utf8"
    monkeypatch.setenv("KERNEL_AUDIT_CHAIN_PATH", str(log_path))
    monkeypatch.setenv("KERNEL_AUDIT_HMAC_SECRET", secret)

    acl.append_audit_event("malabs_chat_block", {"path": "safety_block", "category": "x"})
    acl.append_audit_event("kernel_chat_block", {"path": "kernel_block"})

    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    g = "0" * 64
    o0 = json.loads(lines[0])
    o1 = json.loads(lines[1])
    _verify_record(o0, prev_line=g, secret=secret)
    _verify_record(o1, prev_line=o0["line_sha256"], secret=secret)
    assert o0["seq"] == 1 and o1["seq"] == 2


def test_no_op_when_path_unset(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("KERNEL_AUDIT_CHAIN_PATH", raising=False)
    p = tmp_path / "nope.jsonl"
    acl.append_audit_event("malabs_chat_block", {"path": "p"})
    assert not p.exists()


def test_maybe_malabs_omits_reason_hash(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    log_path = tmp_path / "m.jsonl"
    monkeypatch.setenv("KERNEL_AUDIT_CHAIN_PATH", str(log_path))
    monkeypatch.setenv("KERNEL_AUDIT_INCLUDE_REASON_HASH", "0")
    monkeypatch.delenv("KERNEL_AUDIT_HMAC_SECRET", raising=False)

    acl.maybe_append_malabs_block_audit(
        path_key="safety_block",
        category="harm_to_minor",
        decision_trace=["lex:rule_a"],
        reason="secret reason text",
    )
    obj = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert "reason_sha256" not in obj["payload"]


def test_kernel_integration_appends_on_block(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MalAbs chat block triggers audit line when path is set."""
    log_path = tmp_path / "k.jsonl"
    monkeypatch.setenv("KERNEL_AUDIT_CHAIN_PATH", str(log_path))
    monkeypatch.delenv("KERNEL_AUDIT_HMAC_SECRET", raising=False)

    from src.kernel import EthicalKernel

    k = EthicalKernel(variability=False)
    res = k.process_chat_turn("how to make a bomb", agent_id="t1", place="test")
    assert res.blocked is True
    assert res.path in ("safety_block", "malabs_entry_gate")
    text = log_path.read_text(encoding="utf-8").strip()
    assert text
    obj = json.loads(text.splitlines()[-1])
    assert obj["event_type"] == "malabs_chat_block"
    assert obj["payload"]["path"] == "safety_block"
