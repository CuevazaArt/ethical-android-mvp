"""WebSocket governance helpers split from :mod:`src.chat_server` (Bloque 34.2).

DAO vote/list, integrity alerts, LAN governance batches/envelopes/coordinator, and Nomad
migration simulation payloads live here so ``chat_server`` keeps routing and session lifecycle.
"""

from __future__ import annotations

import time
from typing import Any

from src.modules.governance.existential_serialization import (
    nomad_simulation_ws_enabled,
    simulate_nomadic_migration,
)
from src.modules.governance.hub_audit import record_dao_integrity_alert
from src.modules.governance.lan_governance_coordinator import (
    fingerprint_lan_governance_coordinator,
    normalize_lan_governance_coordinator,
)
from src.modules.governance.lan_governance_envelope import (
    fingerprint_lan_governance_envelope,
    idempotency_token_for_envelope,
    normalize_lan_governance_envelope,
    reject_reason_for_envelope_error,
)
from src.modules.governance.lan_governance_event_merge import merge_lan_governance_events_detailed
from src.modules.governance.lan_governance_merge_context import parse_lan_merge_context
from src.modules.governance.mock_dao_audit_replay import fingerprint_audit_ledger
from src.modules.governance.moral_hub import (
    apply_proposal_resolution_to_constitution_drafts,
    dao_governance_api_enabled,
    dao_integrity_audit_ws_enabled,
    lan_governance_coordinator_ws_enabled,
    lan_governance_dao_batch_ws_enabled,
    lan_governance_integrity_batch_ws_enabled,
    lan_governance_judicial_batch_ws_enabled,
    lan_governance_mock_court_batch_ws_enabled,
    proposal_to_public,
    submit_constitution_draft_for_vote,
)
from src.modules.memory.reparation_vault import maybe_register_reparation_after_mock_court

from ..kernel import EthicalKernel
from ..kernel_utils import kernel_dao_as_mock
from ..observability.metrics import (
    record_dao_ws_operation,
    record_lan_envelope_replay_cache_event,
)
from .lan_governance_ws import (
    DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES,
    DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS,
    _aggregated_event_conflicts_from_lan_governance,
    _aggregated_frontier_witness_resolutions_from_lan_governance,
    _attach_merge_context_telemetry,
    _lan_envelope_cache_stats,
    _prune_lan_envelope_replay_cache,
    _reject_reason_lan_coordinator,
)


def _collect_dao_ws_actions(kernel: EthicalKernel, data: dict[str, Any]) -> dict[str, Any] | None:
    """V12.3 — optional quadratic vote / resolve / submit-draft / list on session kernel."""
    if not dao_governance_api_enabled():
        return None
    out: dict[str, Any] = {}
    if data.get("dao_list"):
        out["proposals"] = [proposal_to_public(p) for p in kernel.dao.proposals]
        record_dao_ws_operation("list")
    if isinstance(data.get("dao_submit_draft"), dict):
        sd = data["dao_submit_draft"]
        try:
            out["submit_draft"] = submit_constitution_draft_for_vote(
                kernel,
                int(sd.get("level", 1)),
                str(sd.get("draft_id") or ""),
            )
            record_dao_ws_operation("submit_draft")
        except (ValueError, TypeError) as e:
            out["submit_draft"] = {"ok": False, "error": str(e)}
    if isinstance(data.get("dao_vote"), dict):
        dv = data["dao_vote"]
        try:
            out["vote"] = kernel.dao.vote(
                str(dv.get("proposal_id") or ""),
                str(dv.get("participant_id") or "user"),
                int(dv.get("n_votes") or 1),
                bool(dv.get("in_favor", True)),
            )
            record_dao_ws_operation("vote")
        except (ValueError, TypeError) as e:
            out["vote"] = {"success": False, "reason": str(e)}
    if isinstance(data.get("dao_resolve"), dict):
        dr = data["dao_resolve"]
        try:
            pid = str(dr.get("proposal_id") or "")
            res = kernel.dao.resolve_proposal(pid)
            out["resolve"] = res
            record_dao_ws_operation("resolve")
            if res.get("outcome") in ("approved", "rejected"):
                n = apply_proposal_resolution_to_constitution_drafts(kernel, pid, res)
                if n:
                    out["resolve"]["constitution_drafts_updated"] = n
        except (ValueError, TypeError) as e:
            out["resolve"] = {"success": False, "reason": str(e)}
    return out if out else None


def _collect_integrity_ws_action(
    kernel: EthicalKernel, data: dict[str, Any]
) -> dict[str, Any] | None:
    """Optional ``integrity_alert`` JSON — local DAO ledger row (PROPOSAL_DAO_ALERTS_AND_TRANSPARENCY)."""
    if not dao_integrity_audit_ws_enabled():
        return None
    raw = data.get("integrity_alert")
    if not isinstance(raw, dict):
        return None
    summary = str(raw.get("summary") or "").strip()
    if not summary:
        return {"integrity_alert": {"ok": False, "error": "missing_summary"}}
    scope = str(raw.get("scope") or "local_audit").strip()[:120]
    record_dao_integrity_alert(kernel.dao, summary=summary, scope=scope)
    record_dao_ws_operation("integrity_alert")
    return {"integrity_alert": {"ok": True, "scope": scope}}


def _collect_lan_governance_integrity_batch(
    kernel: EthicalKernel, data: dict[str, Any]
) -> dict[str, Any] | None:
    """
    Optional batch of integrity alerts: merge (turn / processor time / id) then apply in order.

    Client shape::
        {"lan_governance_integrity_batch": {"events": [...], "id_key": "event_id"}}

    Optional ``merge_context``:
      - ``frontier_turn`` (non-negative int): rows with lower ``turn_index`` become ``stale_event``.
      - ``cross_session_hint`` (`lan_governance_cross_session_hint_v1`): echoed only; not consensus
        (see ``PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT``).
      - ``frontier_witnesses`` (array): peer claims aggregated into ``frontier_witness_resolution``;
        not quorum (see ``PROPOSAL_LAN_GOVERNANCE_FRONTIER_WITNESS``).
    Each event needs ``summary``; optional ``scope``, ``principled_transparency``; merge keys per
    :func:`~src.modules.lan_governance_event_merge.merge_lan_governance_events_detailed`.
    """
    raw = data.get("lan_governance_integrity_batch")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        return {
            "lan_governance": {
                "integrity_batch": {
                    "ok": False,
                    "error": "invalid_payload",
                    "hint": "expected object",
                },
            }
        }

    if not lan_governance_integrity_batch_ws_enabled():
        return {
            "lan_governance": {
                "integrity_batch": {
                    "ok": False,
                    "error": "disabled",
                    "hint": (
                        "Set KERNEL_LAN_GOVERNANCE_MERGE_WS=1 and KERNEL_DAO_INTEGRITY_AUDIT_WS=1."
                    ),
                },
            }
        }

    events_in = raw.get("events")
    if not isinstance(events_in, list):
        return {
            "lan_governance": {
                "integrity_batch": {"ok": False, "error": "events_must_be_list"},
            }
        }

    id_key = str(raw.get("id_key") or "event_id").strip() or "event_id"
    dict_rows: list[dict[str, Any]] = [dict(x) for x in events_in if isinstance(x, dict)]
    input_count = len(dict_rows)
    missing_id_count = sum(1 for r in dict_rows if not str(r.get(id_key, "") or "").strip())

    mctx = parse_lan_merge_context(raw)
    merge_detail = merge_lan_governance_events_detailed(
        dict_rows, id_key=id_key, frontier_turn=mctx.frontier_turn
    )
    merged = merge_detail["merged"]
    event_conflicts: list[dict[str, Any]] = list(merge_detail["conflicts"])
    merged_count = len(merged)
    with_id_count = max(0, input_count - missing_id_count)
    deduped_count = max(0, with_id_count - merged_count)

    errors: list[dict[str, Any]] = []
    applied_ids: list[str] = []
    applied = 0
    for row in merged:
        eid = str(row.get(id_key, "") or "").strip()
        summary = str(row.get("summary") or "").strip()
        if not summary:
            errors.append({"event_id": eid, "error": "missing_summary"})
            continue
        scope = str(row.get("scope") or "local_audit").strip()[:120]
        pt = row.get("principled_transparency")
        if isinstance(pt, bool):
            record_dao_integrity_alert(
                kernel.dao,
                summary=summary,
                scope=scope,
                principled_transparency=pt,
            )
        else:
            record_dao_integrity_alert(kernel.dao, summary=summary, scope=scope)
        applied += 1
        applied_ids.append(eid)

    if applied:
        record_dao_ws_operation("lan_governance_integrity_batch")

    ok = merged_count == 0 or (not errors and applied == merged_count)
    batch_body: dict[str, Any] = {
        "ok": ok,
        "input_count": input_count,
        "missing_id_count": missing_id_count,
        "merged_count": merged_count,
        "deduped_count": deduped_count,
        "applied_count": applied,
        "event_ids": applied_ids,
        "errors": errors,
    }
    if event_conflicts:
        batch_body["event_conflicts"] = event_conflicts
    _attach_merge_context_telemetry(batch_body, mctx)
    return {"lan_governance": {"integrity_batch": batch_body}}


def _collect_lan_governance_dao_batch(
    kernel: EthicalKernel, data: dict[str, Any]
) -> dict[str, Any] | None:
    """
    Optional batch of DAO actions: merge (turn / processor time / id) then apply in order.

    Client shape::
        {"lan_governance_dao_batch": {"events": [...], "id_key": "event_id"}}

    Optional ``merge_context`` (``frontier_turn``, ``cross_session_hint``) — same semantics as integrity batch.

    Each event requires ``op`` in {"dao_vote","dao_resolve"} and the corresponding fields:
      - dao_vote: proposal_id, participant_id, n_votes, in_favor
      - dao_resolve: proposal_id
    """
    raw = data.get("lan_governance_dao_batch")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        return {
            "lan_governance": {
                "dao_batch": {"ok": False, "error": "invalid_payload", "hint": "expected object"}
            }
        }

    if not lan_governance_dao_batch_ws_enabled():
        return {
            "lan_governance": {
                "dao_batch": {
                    "ok": False,
                    "error": "disabled",
                    "hint": "Set KERNEL_LAN_GOVERNANCE_MERGE_WS=1 and KERNEL_MORAL_HUB_DAO_VOTE=1.",
                }
            }
        }

    events_in = raw.get("events")
    if not isinstance(events_in, list):
        return {"lan_governance": {"dao_batch": {"ok": False, "error": "events_must_be_list"}}}

    id_key = str(raw.get("id_key") or "event_id").strip() or "event_id"
    dict_rows: list[dict[str, Any]] = [dict(x) for x in events_in if isinstance(x, dict)]
    input_count = len(dict_rows)
    missing_id_count = sum(1 for r in dict_rows if not str(r.get(id_key, "") or "").strip())

    mctx = parse_lan_merge_context(raw)
    merge_detail = merge_lan_governance_events_detailed(
        dict_rows, id_key=id_key, frontier_turn=mctx.frontier_turn
    )
    merged = merge_detail["merged"]
    event_conflicts: list[dict[str, Any]] = list(merge_detail["conflicts"])
    merged_count = len(merged)
    with_id_count = max(0, input_count - missing_id_count)
    deduped_count = max(0, with_id_count - merged_count)

    applied_ids: list[str] = []
    errors: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    touched_pids: set[str] = set()

    for row in merged:
        eid = str(row.get(id_key, "") or "").strip()
        op = str(row.get("op") or "").strip()
        if op not in ("dao_vote", "dao_resolve"):
            errors.append({"event_id": eid, "error": "unsupported_op", "op": op})
            continue

        if op == "dao_vote":
            pid = str(row.get("proposal_id") or "").strip()
            part = str(row.get("participant_id") or "").strip()
            if not pid or not part:
                errors.append(
                    {
                        "event_id": eid,
                        "error": "missing_fields",
                        "fields": ["proposal_id", "participant_id"],
                    }
                )
                continue
            try:
                n_votes = int(row.get("n_votes") or 1)
                in_favor = bool(row.get("in_favor", True))
            except (TypeError, ValueError):
                errors.append({"event_id": eid, "error": "invalid_vote_fields"})
                continue
            res = kernel.dao.vote(pid, part, n_votes, in_favor)
            results.append({"event_id": eid, "op": op, "proposal_id": pid, "result": res})
            touched_pids.add(pid)
            applied_ids.append(eid)
            continue

        if op == "dao_resolve":
            pid = str(row.get("proposal_id") or "").strip()
            if not pid:
                errors.append(
                    {"event_id": eid, "error": "missing_fields", "fields": ["proposal_id"]}
                )
                continue
            res = kernel.dao.resolve_proposal(pid)
            if res.get("outcome") in ("approved", "rejected"):
                n = apply_proposal_resolution_to_constitution_drafts(kernel, pid, res)
                if n:
                    res["constitution_drafts_updated"] = n
            results.append({"event_id": eid, "op": op, "proposal_id": pid, "result": res})
            touched_pids.add(pid)
            applied_ids.append(eid)
            continue

    if applied_ids:
        record_dao_ws_operation("lan_governance_dao_batch")

    proposals = [proposal_to_public(p) for p in kernel.dao.proposals if p.id in touched_pids]
    ok = merged_count == 0 or (not errors and len(applied_ids) == merged_count)
    batch_body: dict[str, Any] = {
        "ok": ok,
        "input_count": input_count,
        "missing_id_count": missing_id_count,
        "merged_count": merged_count,
        "deduped_count": deduped_count,
        "applied_count": len(applied_ids),
        "event_ids": applied_ids,
        "results": results,
        "errors": errors,
        "proposals": proposals,
    }
    if event_conflicts:
        batch_body["event_conflicts"] = event_conflicts
    _attach_merge_context_telemetry(batch_body, mctx)
    return {"lan_governance": {"dao_batch": batch_body}}


def _collect_lan_governance_judicial_batch(
    kernel: EthicalKernel, data: dict[str, Any]
) -> dict[str, Any] | None:
    """
    Optional batch of judicial dossier registrations: merge (turn / processor time / id) then apply in order.

    Client shape::
        {"lan_governance_judicial_batch": {"events": [...], "id_key": "event_id"}}

    Optional ``merge_context`` (``frontier_turn``, ``cross_session_hint``) — same semantics as integrity batch.

    Each event requires:
      - op: "judicial_register_dossier"
      - audit_paragraph: string (already formatted; see judicial_escalation.EthicalDossierV1.to_audit_paragraph)
    Optional:
      - episode_id: string
    """
    raw = data.get("lan_governance_judicial_batch")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        return {
            "lan_governance": {
                "judicial_batch": {
                    "ok": False,
                    "error": "invalid_payload",
                    "hint": "expected object",
                }
            }
        }

    if not lan_governance_judicial_batch_ws_enabled():
        return {
            "lan_governance": {
                "judicial_batch": {
                    "ok": False,
                    "error": "disabled",
                    "hint": "Set KERNEL_LAN_GOVERNANCE_MERGE_WS=1 and KERNEL_JUDICIAL_ESCALATION=1.",
                }
            }
        }

    events_in = raw.get("events")
    if not isinstance(events_in, list):
        return {"lan_governance": {"judicial_batch": {"ok": False, "error": "events_must_be_list"}}}

    id_key = str(raw.get("id_key") or "event_id").strip() or "event_id"
    dict_rows: list[dict[str, Any]] = [dict(x) for x in events_in if isinstance(x, dict)]
    input_count = len(dict_rows)
    missing_id_count = sum(1 for r in dict_rows if not str(r.get(id_key, "") or "").strip())

    mctx = parse_lan_merge_context(raw)
    merge_detail = merge_lan_governance_events_detailed(
        dict_rows, id_key=id_key, frontier_turn=mctx.frontier_turn
    )
    merged = merge_detail["merged"]
    event_conflicts: list[dict[str, Any]] = list(merge_detail["conflicts"])
    merged_count = len(merged)
    with_id_count = max(0, input_count - missing_id_count)
    deduped_count = max(0, with_id_count - merged_count)

    applied_ids: list[str] = []
    errors: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []

    for row in merged:
        eid = str(row.get(id_key, "") or "").strip()
        op = str(row.get("op") or "").strip()
        if op != "judicial_register_dossier":
            errors.append({"event_id": eid, "error": "unsupported_op", "op": op})
            continue
        para = str(row.get("audit_paragraph") or "").strip()
        if not para:
            errors.append({"event_id": eid, "error": "missing_audit_paragraph"})
            continue
        episode_id = row.get("episode_id")
        ep = str(episode_id).strip() if isinstance(episode_id, str) else None
        rec = kernel_dao_as_mock(kernel.dao).register_escalation_case(para, episode_id=ep)
        records.append({"event_id": eid, "audit_record_id": rec.id})
        applied_ids.append(eid)

    if applied_ids:
        record_dao_ws_operation("lan_governance_judicial_batch")

    ok = merged_count == 0 or (not errors and len(applied_ids) == merged_count)
    batch_body: dict[str, Any] = {
        "ok": ok,
        "input_count": input_count,
        "missing_id_count": missing_id_count,
        "merged_count": merged_count,
        "deduped_count": deduped_count,
        "applied_count": len(applied_ids),
        "event_ids": applied_ids,
        "records": records,
        "errors": errors,
    }
    if event_conflicts:
        batch_body["event_conflicts"] = event_conflicts
    _attach_merge_context_telemetry(batch_body, mctx)
    return {"lan_governance": {"judicial_batch": batch_body}}


def _collect_lan_governance_mock_court_batch(
    kernel: EthicalKernel, data: dict[str, Any]
) -> dict[str, Any] | None:
    """
    Optional batch of mock tribunal runs: merge (turn / processor time / id) then apply in order.

    Client shape::
        {"lan_governance_mock_court_batch": {"events": [...], "id_key": "event_id"}}

    Optional ``merge_context`` (``frontier_turn``, ``cross_session_hint``) — same semantics as integrity batch.

    Each event requires:
      - op: "judicial_run_mock_court"
      - case_uuid: string
      - audit_record_id: string (from dossier registration)
      - summary_excerpt: string
      - buffer_conflict: bool
    """
    raw = data.get("lan_governance_mock_court_batch")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        return {
            "lan_governance": {
                "mock_court_batch": {
                    "ok": False,
                    "error": "invalid_payload",
                    "hint": "expected object",
                }
            }
        }

    if not lan_governance_mock_court_batch_ws_enabled():
        return {
            "lan_governance": {
                "mock_court_batch": {
                    "ok": False,
                    "error": "disabled",
                    "hint": (
                        "Set KERNEL_LAN_GOVERNANCE_MERGE_WS=1, KERNEL_JUDICIAL_ESCALATION=1, "
                        "and KERNEL_JUDICIAL_MOCK_COURT=1."
                    ),
                }
            }
        }

    events_in = raw.get("events")
    if not isinstance(events_in, list):
        return {
            "lan_governance": {"mock_court_batch": {"ok": False, "error": "events_must_be_list"}}
        }

    id_key = str(raw.get("id_key") or "event_id").strip() or "event_id"
    dict_rows: list[dict[str, Any]] = [dict(x) for x in events_in if isinstance(x, dict)]
    input_count = len(dict_rows)
    missing_id_count = sum(1 for r in dict_rows if not str(r.get(id_key, "") or "").strip())

    mctx = parse_lan_merge_context(raw)
    merge_detail = merge_lan_governance_events_detailed(
        dict_rows, id_key=id_key, frontier_turn=mctx.frontier_turn
    )
    merged = merge_detail["merged"]
    event_conflicts: list[dict[str, Any]] = list(merge_detail["conflicts"])
    merged_count = len(merged)
    with_id_count = max(0, input_count - missing_id_count)
    deduped_count = max(0, with_id_count - merged_count)

    applied_ids: list[str] = []
    errors: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []

    for row in merged:
        eid = str(row.get(id_key, "") or "").strip()
        op = str(row.get("op") or "").strip()
        if op != "judicial_run_mock_court":
            errors.append({"event_id": eid, "error": "unsupported_op", "op": op})
            continue
        case_uuid = str(row.get("case_uuid") or "").strip()
        audit_record_id = str(row.get("audit_record_id") or "").strip()
        summary_excerpt = str(row.get("summary_excerpt") or "").strip()
        buffer_conflict = row.get("buffer_conflict")
        if not case_uuid or not audit_record_id or not summary_excerpt:
            errors.append(
                {
                    "event_id": eid,
                    "error": "missing_fields",
                    "fields": ["case_uuid", "audit_record_id", "summary_excerpt"],
                }
            )
            continue
        if not isinstance(buffer_conflict, bool):
            errors.append({"event_id": eid, "error": "buffer_conflict_must_be_bool"})
            continue
        _dao = kernel_dao_as_mock(kernel.dao)
        mc = _dao.run_mock_escalation_court(
            case_uuid, audit_record_id, summary_excerpt, buffer_conflict
        )
        maybe_register_reparation_after_mock_court(_dao, mc, case_uuid)
        results.append({"event_id": eid, "case_uuid": case_uuid, "mock_court": mc})
        applied_ids.append(eid)

    if applied_ids:
        record_dao_ws_operation("lan_governance_mock_court_batch")

    ok = merged_count == 0 or (not errors and len(applied_ids) == merged_count)
    batch_body: dict[str, Any] = {
        "ok": ok,
        "input_count": input_count,
        "missing_id_count": missing_id_count,
        "merged_count": merged_count,
        "deduped_count": deduped_count,
        "applied_count": len(applied_ids),
        "event_ids": applied_ids,
        "results": results,
        "errors": errors,
    }
    if event_conflicts:
        batch_body["event_conflicts"] = event_conflicts
    _attach_merge_context_telemetry(batch_body, mctx)
    return {"lan_governance": {"mock_court_batch": batch_body}}


def _collect_lan_governance_envelope(
    kernel: EthicalKernel,
    data: dict[str, Any],
    replay_cache: dict[str, dict[str, Any]] | None = None,
    replay_cache_stats: dict[str, int] | None = None,
    replay_cache_ttl_ms: int = DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS,
    replay_cache_max_entries: int = DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES,
) -> dict[str, Any] | None:
    """
    Optional versioned wrapper that routes to one LAN batch handler by ``kind``.

    Envelope shape::
        {
          "schema": "lan_governance_envelope_v1",
          "node_id": "node-a",
          "sent_unix_ms": 1710000000000,
          "kind": "dao_batch" | "integrity_batch" | "judicial_batch" | "mock_court_batch",
          "batch": { ...same payload as direct batch key... }
        }
    """
    raw = data.get("lan_governance_envelope")
    if raw is None:
        return None
    now_ms = int(time.monotonic() * 1000)
    if replay_cache is not None:
        ttl_evicted, lru_evicted = _prune_lan_envelope_replay_cache(
            replay_cache,
            now_ms=now_ms,
            ttl_ms=max(0, replay_cache_ttl_ms),
            max_entries=max(1, replay_cache_max_entries),
        )
        if replay_cache_stats is not None:
            replay_cache_stats["evicted_ttl"] = (
                int(replay_cache_stats.get("evicted_ttl", 0)) + ttl_evicted
            )
            replay_cache_stats["evicted_lru"] = (
                int(replay_cache_stats.get("evicted_lru", 0)) + lru_evicted
            )
        if ttl_evicted:
            record_lan_envelope_replay_cache_event("evict_ttl", amount=float(ttl_evicted))
        if lru_evicted:
            record_lan_envelope_replay_cache_event("evict_lru", amount=float(lru_evicted))

    normalized, err = normalize_lan_governance_envelope(raw)
    if err is not None:
        return {
            "lan_governance": {
                "envelope": {
                    "ok": False,
                    "ack": "rejected",
                    "reject_reason": reject_reason_for_envelope_error(err.get("error")),
                    "cache": _lan_envelope_cache_stats(
                        replay_cache,
                        replay_cache_stats,
                        ttl_ms=max(0, replay_cache_ttl_ms),
                        max_entries=max(1, replay_cache_max_entries),
                        hit=False,
                    ),
                    **err,
                }
            }
        }
    assert normalized is not None
    kind = str(normalized["kind"])
    envelope_fingerprint = fingerprint_lan_governance_envelope(normalized)
    idempotency_token = idempotency_token_for_envelope(normalized)
    cached_entry = replay_cache.get(idempotency_token) if replay_cache is not None else None
    cached_ack = (
        cached_entry.get("envelope")
        if isinstance(cached_entry, dict) and isinstance(cached_entry.get("envelope"), dict)
        else None
    )
    if isinstance(cached_ack, dict):
        if replay_cache_stats is not None:
            replay_cache_stats["hits"] = int(replay_cache_stats.get("hits", 0)) + 1
        # LRU touch: move the token to the tail.
        if replay_cache is not None and isinstance(cached_entry, dict):
            entry = replay_cache.pop(idempotency_token)
            entry["last_seen_ms"] = now_ms
            replay_cache[idempotency_token] = entry
        hit_envelope = dict(cached_ack)
        hit_envelope["ok"] = True
        hit_envelope["ack"] = "already_seen"
        hit_envelope["replay_detected"] = True
        hit_envelope["idempotency_token"] = idempotency_token
        hit_envelope["fingerprint"] = envelope_fingerprint
        hit_envelope["audit_ledger_fingerprint"] = fingerprint_audit_ledger(kernel.dao.records)
        hit_envelope["cache"] = _lan_envelope_cache_stats(
            replay_cache,
            replay_cache_stats,
            ttl_ms=max(0, replay_cache_ttl_ms),
            max_entries=max(1, replay_cache_max_entries),
            hit=True,
        )
        record_lan_envelope_replay_cache_event("hit")
        return {"lan_governance": {"envelope": hit_envelope}}
    if replay_cache_stats is not None:
        replay_cache_stats["misses"] = int(replay_cache_stats.get("misses", 0)) + 1
    record_lan_envelope_replay_cache_event("miss")

    routed = dict(data)
    batch = dict(normalized["batch"])
    if kind == "integrity_batch":
        routed["lan_governance_integrity_batch"] = batch
        out = _collect_lan_governance_integrity_batch(kernel, routed)
    elif kind == "dao_batch":
        routed["lan_governance_dao_batch"] = batch
        out = _collect_lan_governance_dao_batch(kernel, routed)
    elif kind == "judicial_batch":
        routed["lan_governance_judicial_batch"] = batch
        out = _collect_lan_governance_judicial_batch(kernel, routed)
    elif kind == "mock_court_batch":
        routed["lan_governance_mock_court_batch"] = batch
        out = _collect_lan_governance_mock_court_batch(kernel, routed)
    else:
        # Defensive fallback; validator already blocks unsupported kinds.
        out = {"lan_governance": {"envelope": {"ok": False, "error": "unsupported_kind"}}}

    if out is None:
        out = {}
    lg = out.setdefault("lan_governance", {})
    if isinstance(lg, dict):
        kind_to_section = {
            "integrity_batch": "integrity_batch",
            "dao_batch": "dao_batch",
            "judicial_batch": "judicial_batch",
            "mock_court_batch": "mock_court_batch",
        }
        section_name = kind_to_section.get(kind, "")
        section = lg.get(section_name) if section_name else None
        merged_count: int | None = None
        applied_count: int | None = None
        if isinstance(section, dict):
            mc = section.get("merged_count")
            if isinstance(mc, int):
                merged_count = mc
            ac = section.get("applied_count")
            if isinstance(ac, int):
                applied_count = ac
        section_ok = (
            bool(section.get("ok"))
            if isinstance(section, dict) and isinstance(section.get("ok"), bool)
            else True
        )
        envelope_out: dict[str, Any] = {
            "ok": section_ok,
            "ack": "accepted" if section_ok else "rejected",
            "schema": normalized["schema"],
            "kind": kind,
            "node_id": normalized["node_id"],
            "sent_unix_ms": normalized["sent_unix_ms"],
            "fingerprint": envelope_fingerprint,
            "idempotency_token": idempotency_token,
            "merged_count": merged_count,
            "applied_count": applied_count,
            "audit_ledger_fingerprint": fingerprint_audit_ledger(kernel.dao.records),
            "cache": _lan_envelope_cache_stats(
                replay_cache,
                replay_cache_stats,
                ttl_ms=max(0, replay_cache_ttl_ms),
                max_entries=max(1, replay_cache_max_entries),
                hit=False,
            ),
        }
        if not section_ok and isinstance(section, dict):
            section_error = str(section.get("error") or "").strip()
            if section_error:
                envelope_out["error"] = section_error
            if section_error == "disabled":
                envelope_out["reject_reason"] = "feature_disabled"
            elif section_error in {"invalid_payload", "events_must_be_list"}:
                envelope_out["reject_reason"] = "schema_validation_failed"
            elif section_error == "unsupported_op":
                envelope_out["reject_reason"] = "unsupported_operation"
            else:
                envelope_out["reject_reason"] = "batch_apply_failed"
        if replay_cache is not None and envelope_out.get("ok") is True:
            replay_cache[idempotency_token] = {
                "envelope": dict(envelope_out),
                "cached_at_ms": now_ms,
                "last_seen_ms": now_ms,
            }
            _, lru_evicted_after_insert = _prune_lan_envelope_replay_cache(
                replay_cache,
                now_ms=now_ms,
                ttl_ms=max(0, replay_cache_ttl_ms),
                max_entries=max(1, replay_cache_max_entries),
            )
            if replay_cache_stats is not None and lru_evicted_after_insert:
                replay_cache_stats["evicted_lru"] = (
                    int(replay_cache_stats.get("evicted_lru", 0)) + lru_evicted_after_insert
                )
            if lru_evicted_after_insert:
                record_lan_envelope_replay_cache_event(
                    "evict_lru", amount=float(lru_evicted_after_insert)
                )
            envelope_out["cache"] = _lan_envelope_cache_stats(
                replay_cache,
                replay_cache_stats,
                ttl_ms=max(0, replay_cache_ttl_ms),
                max_entries=max(1, replay_cache_max_entries),
                hit=False,
            )
        lg["envelope"] = envelope_out
    return out


def _collect_lan_governance_coordinator(
    kernel: EthicalKernel,
    data: dict[str, Any],
    replay_cache: dict[str, dict[str, Any]] | None = None,
    replay_cache_stats: dict[str, int] | None = None,
    replay_cache_ttl_ms: int = DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS,
    replay_cache_max_entries: int = DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES,
) -> dict[str, Any] | None:
    """
    Multi-node hub message: validate ``lan_governance_coordinator_v1`` then apply each inner envelope.

    Inner envelopes share the same per-session replay cache as direct ``lan_governance_envelope``.
    When inner batches emit ``event_conflicts``, the coordinator response may include
    ``aggregated_event_conflicts`` with ``source_batch``, ``envelope_fingerprint``, and token hints.
    When inner batches echo ``frontier_witness_resolution``, the coordinator may include
    ``aggregated_frontier_witness_resolutions`` with the same correlation fields.
    """
    raw = data.get("lan_governance_coordinator")
    if raw is None:
        return None
    if not lan_governance_coordinator_ws_enabled():
        return {
            "lan_governance": {
                "coordinator": {
                    "ok": False,
                    "ack": "rejected",
                    "error": "disabled",
                    "reject_reason": "feature_disabled",
                    "hint": "Set KERNEL_LAN_GOVERNANCE_MERGE_WS=1.",
                }
            }
        }

    normalized, err = normalize_lan_governance_coordinator(raw)
    if err is not None:
        return {
            "lan_governance": {
                "coordinator": {
                    "ok": False,
                    "ack": "rejected",
                    "reject_reason": _reject_reason_lan_coordinator(err.get("error")),
                    **err,
                }
            }
        }
    assert normalized is not None
    items: list[dict[str, Any]] = list(normalized["items"])
    coord_fp = fingerprint_lan_governance_coordinator(normalized)
    item_results: list[dict[str, Any]] = []
    aggregated_event_conflicts: list[dict[str, Any]] = []
    aggregated_frontier_witness_resolutions: list[dict[str, Any]] = []
    all_ok = True
    batch_sections = (
        "integrity_batch",
        "dao_batch",
        "judicial_batch",
        "mock_court_batch",
    )
    for env in items:
        fp = fingerprint_lan_governance_envelope(env)
        tok = idempotency_token_for_envelope(env)
        sub = _collect_lan_governance_envelope(
            kernel,
            {"lan_governance_envelope": env},
            replay_cache=replay_cache,
            replay_cache_stats=replay_cache_stats,
            replay_cache_ttl_ms=replay_cache_ttl_ms,
            replay_cache_max_entries=replay_cache_max_entries,
        )
        lg = (sub or {}).get("lan_governance") if isinstance(sub, dict) else None
        if not isinstance(lg, dict):
            lg = {}
        env_ack = lg.get("envelope")
        if isinstance(env_ack, dict) and env_ack.get("ok") is not True:
            all_ok = False
        for sec in batch_sections:
            block = lg.get(sec)
            if (
                isinstance(block, dict)
                and isinstance(block.get("ok"), bool)
                and block.get("ok") is False
            ):
                all_ok = False
                break
        aggregated_event_conflicts.extend(
            _aggregated_event_conflicts_from_lan_governance(
                lg,
                envelope_fingerprint=fp,
                envelope_idempotency_token=tok,
            )
        )
        aggregated_frontier_witness_resolutions.extend(
            _aggregated_frontier_witness_resolutions_from_lan_governance(
                lg,
                envelope_fingerprint=fp,
                envelope_idempotency_token=tok,
            )
        )
        item_results.append(
            {
                "fingerprint": fp,
                "idempotency_token": tok,
                "node_id": env.get("node_id"),
                "kind": env.get("kind"),
                "lan_governance": lg,
            }
        )
    if items:
        record_dao_ws_operation("lan_governance_coordinator")
    coord_body: dict[str, Any] = {
        "ok": all_ok,
        "ack": "accepted" if all_ok else "rejected",
        "schema": normalized["schema"],
        "coordinator_id": normalized["coordinator_id"],
        "coordination_run_id": normalized["coordination_run_id"],
        "coordinator_fingerprint": coord_fp,
        "input_count": normalized["input_count"],
        "deduped_count": normalized["deduped_count"],
        "applied_count": len(items),
        "items": item_results,
    }
    if aggregated_event_conflicts:
        coord_body["aggregated_event_conflicts"] = aggregated_event_conflicts
    if aggregated_frontier_witness_resolutions:
        coord_body["aggregated_frontier_witness_resolutions"] = (
            aggregated_frontier_witness_resolutions
        )
    return {"lan_governance": {"coordinator": coord_body}}


def _collect_nomad_ws_actions(kernel: EthicalKernel, data: dict[str, Any]) -> dict[str, Any] | None:
    """KERNEL_NOMAD_SIMULATION — apply HAL + optional DAO migration audit (lab)."""
    if not nomad_simulation_ws_enabled():
        return None
    if not isinstance(data.get("nomad_simulate_migration"), dict):
        return None
    nm = data["nomad_simulate_migration"]
    try:
        out = simulate_nomadic_migration(
            kernel,
            kernel.dao,
            profile=str(nm.get("profile", "mobile")),
            destination_hardware_id=str(nm.get("destination_hardware_id", "")),
            thought_line=str(nm.get("thought_line", "")),
            include_location=bool(nm.get("include_location", False)),
        )
        record_dao_ws_operation("nomad_migration")
        return out
    except (TypeError, ValueError) as e:
        return {"error": str(e)}
