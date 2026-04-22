"""LAN governance WebSocket batch merge helpers (Bloque 34.2).

Extracted from :mod:`src.chat_server` to shrink the monolith. The WebSocket
URL graph and JSON contracts are unchanged.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.modules.governance.lan_governance_merge_context import (
    EVIDENCE_POSTURE_ADVISORY_AGGREGATE,
    LanMergeContextParsed,
)
from ..runtime.chat_feature_flags import coerce_public_int


def _attach_merge_context_telemetry(
    batch_body: dict[str, Any],
    mctx: LanMergeContextParsed,
) -> None:
    """Attach ``merge_context_warnings`` / ``merge_context_echo`` after a LAN batch apply."""
    if mctx.warnings:
        batch_body["merge_context_warnings"] = list(mctx.warnings)
    echo: dict[str, Any] = {}
    if mctx.frontier_turn is not None:
        echo["frontier_turn"] = mctx.frontier_turn
    if mctx.cross_session_hint is not None:
        echo["cross_session_hint"] = dict(mctx.cross_session_hint)
    if mctx.frontier_witnesses:
        echo["frontier_witness_resolution"] = {
            "witnesses": [dict(w) for w in mctx.frontier_witnesses],
            "advisory_max_observed_turn": mctx.witness_advisory_max_turn,
            "evidence_posture": EVIDENCE_POSTURE_ADVISORY_AGGREGATE,
        }
    if echo:
        batch_body["merge_context_echo"] = echo


def _aggregated_event_conflicts_from_lan_governance(
    lg: Mapping[str, Any],
    *,
    envelope_fingerprint: str,
    envelope_idempotency_token: str,
) -> list[dict[str, Any]]:
    """Collect ``event_conflicts`` from LAN batch sections with hub correlation fields."""
    out: list[dict[str, Any]] = []
    for sec in (
        "integrity_batch",
        "dao_batch",
        "judicial_batch",
        "mock_court_batch",
    ):
        block = lg.get(sec)
        if not isinstance(block, dict):
            continue
        ecs = block.get("event_conflicts")
        if not isinstance(ecs, list) or not ecs:
            continue
        for c in ecs:
            if not isinstance(c, dict):
                continue
            row = dict(c)
            row["source_batch"] = sec
            row["envelope_fingerprint"] = envelope_fingerprint
            row["envelope_idempotency_token"] = envelope_idempotency_token
            out.append(row)
    return out


def _aggregated_frontier_witness_resolutions_from_lan_governance(
    lg: Mapping[str, Any],
    *,
    envelope_fingerprint: str,
    envelope_idempotency_token: str,
) -> list[dict[str, Any]]:
    """Collect ``merge_context_echo.frontier_witness_resolution`` from LAN batch sections."""
    out: list[dict[str, Any]] = []
    for sec in (
        "integrity_batch",
        "dao_batch",
        "judicial_batch",
        "mock_court_batch",
    ):
        block = lg.get(sec)
        if not isinstance(block, dict):
            continue
        echo = block.get("merge_context_echo")
        if not isinstance(echo, dict):
            continue
        fwr = echo.get("frontier_witness_resolution")
        if not isinstance(fwr, dict) or not fwr:
            continue
        out.append(
            {
                "source_batch": sec,
                "envelope_fingerprint": envelope_fingerprint,
                "envelope_idempotency_token": envelope_idempotency_token,
                "frontier_witness_resolution": dict(fwr),
            }
        )
    return out


DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS = 300_000
DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES = 256


def _prune_lan_envelope_replay_cache(
    replay_cache: dict[str, dict[str, Any]],
    *,
    now_ms: int,
    ttl_ms: int,
    max_entries: int,
) -> tuple[int, int]:
    """Evict expired and oldest replay-cache rows (TTL then LRU)."""
    evicted_ttl = 0
    evicted_lru = 0

    expired_tokens: list[str] = []
    for token, entry in replay_cache.items():
        cached_at_ms = (
            coerce_public_int(entry.get("cached_at_ms"), default=now_ms, non_negative=True)
            if isinstance(entry, dict)
            else now_ms
        )
        if now_ms - cached_at_ms >= ttl_ms:
            expired_tokens.append(token)
    for token in expired_tokens:
        if replay_cache.pop(token, None) is not None:
            evicted_ttl += 1

    while len(replay_cache) > max_entries:
        oldest = next(iter(replay_cache))
        replay_cache.pop(oldest, None)
        evicted_lru += 1
    return evicted_ttl, evicted_lru


def _lan_envelope_cache_stats(
    replay_cache: dict[str, dict[str, Any]] | None,
    replay_cache_stats: dict[str, int] | None,
    *,
    ttl_ms: int,
    max_entries: int,
    hit: bool,
) -> dict[str, Any]:
    """Compact replay-cache telemetry for envelope ACK."""
    stats = replay_cache_stats or {}
    return {
        "hit": hit,
        "size": len(replay_cache) if replay_cache is not None else 0,
        "hits_total": int(stats.get("hits", 0)),
        "misses_total": int(stats.get("misses", 0)),
        "evicted_ttl_total": int(stats.get("evicted_ttl", 0)),
        "evicted_lru_total": int(stats.get("evicted_lru", 0)),
        "ttl_ms": ttl_ms,
        "max_entries": max_entries,
    }


def _merge_lan_governance_ws_payloads(*parts: dict[str, Any] | None) -> dict[str, Any]:
    """Shallow-merge ``lan_governance`` sections so multiple LAN handlers can coexist in one response."""
    merged: dict[str, Any] = {}
    for p in parts:
        if not p:
            continue
        lg = p.get("lan_governance")
        if isinstance(lg, dict):
            merged.update(lg)
    return merged


def _reject_reason_lan_coordinator(error_code: object) -> str:
    code = str(error_code or "").strip()
    if code == "unsupported_schema":
        return "unsupported_contract"
    if code == "items_too_many":
        return "batch_apply_failed"
    return "schema_validation_failed"
