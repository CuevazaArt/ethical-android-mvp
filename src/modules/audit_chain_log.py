"""
Append-only audit chain (JSONL) for MalAbs / kernel block events.

Hash-linked lines for tamper-evident logs; optional HMAC with operator secret.
See ``docs/AUDIT_TRAIL_AND_REPRODUCIBILITY.md``.

Env:

- ``KERNEL_AUDIT_CHAIN_PATH`` — JSONL file path; empty disables the feature.
- ``KERNEL_AUDIT_HMAC_SECRET`` — optional UTF-8 secret for ``hmac_sha256`` on each line.
- ``KERNEL_AUDIT_INCLUDE_REASON_HASH`` — default on; set ``0`` to omit ``reason_sha256``.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from typing import Any

_GENESIS_PREV = "0" * 64


def _truthy(name: str, default: bool = True) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    if default:
        return raw not in ("0", "false", "no", "off")
    return raw in ("1", "true", "yes", "on")


def _canonical_dumps(obj: dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _read_last_chain_state(path: Path) -> tuple[int, str]:
    if not path.is_file():
        return 0, _GENESIS_PREV
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return 0, _GENESIS_PREV
    lines = text.splitlines()
    last = json.loads(lines[-1])
    return int(last["seq"]), str(last["line_sha256"])


def append_audit_event(event_type: str, payload: dict[str, Any]) -> None:
    """Append one chain record if ``KERNEL_AUDIT_CHAIN_PATH`` is set."""
    raw_path = os.environ.get("KERNEL_AUDIT_CHAIN_PATH", "").strip()
    if not raw_path:
        return
    path = Path(raw_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload_canon = _canonical_dumps(payload)
    payload_sha = _sha256_hex(payload_canon)

    from src.persistence.file_lock import advisory_file_lock

    lock_path = path.with_name(path.name + ".audit.lock")
    with advisory_file_lock(lock_path, timeout_s=30.0):
        t0 = time.perf_counter()
        seq, prev_line_hash = _read_last_chain_state(path)
        inner: dict[str, Any] = {
            "seq": seq + 1,
            "ts_unix": time.time(),
            "event_type": event_type,
            "payload": payload,
            "payload_sha256": payload_sha,
            "prev_line_sha256": prev_line_hash,
        }
        inner_canon = _canonical_dumps(inner)
        line_sha = _sha256_hex(inner_canon)
        record: dict[str, Any] = {**inner, "line_sha256": line_sha}
        secret = os.environ.get("KERNEL_AUDIT_HMAC_SECRET", "").strip()
        if secret:
            record["hmac_sha256"] = hmac.new(
                secret.encode("utf-8"),
                inner_canon.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(_canonical_dumps(record) + "\n")
        
        latency = (time.perf_counter() - t0) * 1000
        if latency > 5.0:
            _log.debug("AuditChain: IO Latency spike: %.2fms", latency)


def maybe_append_malabs_block_audit(
    *,
    path_key: str,
    category: str | None,
    decision_trace: list[str],
    reason: str,
) -> None:
    """Record a chat MalAbs block without storing raw user text."""
    payload: dict[str, Any] = {
        "path": path_key,
        "category": category,
        "decision_trace": list(decision_trace),
    }
    if _truthy("KERNEL_AUDIT_INCLUDE_REASON_HASH", default=True):
        payload["reason_sha256"] = _sha256_hex(reason or "")
    append_audit_event("malabs_chat_block", payload)


def maybe_append_kernel_block_audit(*, path_key: str, block_reason: str) -> None:
    payload: dict[str, Any] = {"path": path_key}
    if _truthy("KERNEL_AUDIT_INCLUDE_REASON_HASH", default=True):
        payload["block_reason_sha256"] = _sha256_hex(block_reason or "")
    append_audit_event("kernel_chat_block", payload)
