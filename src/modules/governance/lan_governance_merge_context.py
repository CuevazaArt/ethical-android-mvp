"""
Optional ``merge_context`` on LAN batch payloads: local frontier + cross-session hint (Phase 2).

``frontier_turn`` affects merge (``stale_event`` below frontier).

``cross_session_hint`` is **validated for shape only** and echoed back for operator / hub logs.
The kernel does **not** treat it as replicated consensus or quorum enforcement — see
``docs/proposals/PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md``.

``frontier_witnesses`` is a list of peer **claims** (observed max turn per session id). The kernel
aggregates them deterministically (dedupe by claimant, max turn, sort) and echoes
``frontier_witness_resolution`` with ``evidence_posture=advisory_aggregate_not_quorum`` — see
``docs/proposals/PROPOSAL_LAN_GOVERNANCE_FRONTIER_WITNESS.md``.
"""
# Status: SCAFFOLD


from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

LAN_GOVERNANCE_CROSS_SESSION_HINT_SCHEMA_V1 = "lan_governance_cross_session_hint_v1"
LAN_GOVERNANCE_FRONTIER_WITNESS_SCHEMA_V1 = "lan_governance_frontier_witness_v1"
MAX_CROSS_SESSION_PARTICIPANTS = 32
MAX_CROSS_SESSION_STRING = 200
MAX_FRONTIER_WITNESSES = 16
EVIDENCE_POSTURE_ADVISORY_AGGREGATE = "advisory_aggregate_not_quorum"


def _coerce_non_negative_int(value: object) -> int:
    if value is None:
        return 0
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return max(0, value)
    if isinstance(value, float):
        return max(0, int(value)) if math.isfinite(value) else 0
    if isinstance(value, str):
        try:
            s = value.strip()
            return max(0, int(s, 10)) if s else 0
        except ValueError:
            return 0
    return 0


def normalize_cross_session_hint(raw: object) -> tuple[dict[str, Any] | None, str | None]:
    """
    Validate ``merge_context.cross_session_hint``.

    Returns ``(normalized, error_code)``; error codes are short machine strings.
    """
    if not isinstance(raw, Mapping):
        return None, "expected_object"

    schema = str(raw.get("schema") or "").strip()
    if schema != LAN_GOVERNANCE_CROSS_SESSION_HINT_SCHEMA_V1:
        return None, "unsupported_schema"

    claimant = str(raw.get("claimant_session_id") or "").strip()
    if not claimant:
        return None, "missing_claimant_session_id"

    out: dict[str, Any] = {
        "schema": LAN_GOVERNANCE_CROSS_SESSION_HINT_SCHEMA_V1,
        "claimant_session_id": claimant[:MAX_CROSS_SESSION_STRING],
    }

    qr = raw.get("quorum_ref")
    if qr is not None:
        qs = str(qr).strip()
        if qs:
            out["quorum_ref"] = qs[:MAX_CROSS_SESSION_STRING]

    if "claimed_frontier_turn" in raw:
        out["claimed_frontier_turn"] = _coerce_non_negative_int(raw.get("claimed_frontier_turn"))

    parts = raw.get("participant_sessions")
    if parts is not None:
        if not isinstance(parts, list):
            return None, "participant_sessions_not_list"
        if len(parts) > MAX_CROSS_SESSION_PARTICIPANTS:
            return None, "participant_sessions_too_many"
        norm_parts: list[str] = []
        for p in parts:
            ps = str(p).strip() if p is not None else ""
            if not ps:
                return None, "participant_sessions_empty_entry"
            norm_parts.append(ps[:MAX_CROSS_SESSION_STRING])
        out["participant_sessions"] = norm_parts

    return out, None


def normalize_frontier_witness(raw: object) -> tuple[dict[str, Any] | None, str | None]:
    """Validate one ``merge_context.frontier_witnesses[]`` entry."""
    if not isinstance(raw, Mapping):
        return None, "expected_object"

    schema = str(raw.get("schema") or "").strip()
    if schema != LAN_GOVERNANCE_FRONTIER_WITNESS_SCHEMA_V1:
        return None, "unsupported_schema"

    claimant = str(raw.get("claimant_session_id") or "").strip()
    if not claimant:
        return None, "missing_claimant_session_id"

    omt = _coerce_non_negative_int(raw.get("observed_max_turn"))
    return {
        "schema": LAN_GOVERNANCE_FRONTIER_WITNESS_SCHEMA_V1,
        "claimant_session_id": claimant[:MAX_CROSS_SESSION_STRING],
        "observed_max_turn": omt,
    }, None


def aggregate_frontier_witnesses(
    raw_list: object,
    warnings: list[str],
) -> tuple[tuple[dict[str, Any], ...], int | None]:
    """
    Dedupe by ``claimant_session_id`` (keep max ``observed_max_turn``), sort by id, compute advisory max.
    """
    if raw_list is None:
        return (), None
    if not isinstance(raw_list, list):
        warnings.append("frontier_witnesses_not_list")
        return (), None

    items = raw_list
    if len(items) > MAX_FRONTIER_WITNESSES:
        warnings.append(f"frontier_witnesses_truncated:{len(items)}")
        items = items[:MAX_FRONTIER_WITNESSES]

    by_claimant: dict[str, int] = {}
    for idx, item in enumerate(items):
        norm_w, err = normalize_frontier_witness(item)
        if err is not None:
            warnings.append(f"frontier_witness_rejected:{idx}:{err}")
            continue
        assert norm_w is not None
        cid = str(norm_w["claimant_session_id"])
        turn = int(norm_w["observed_max_turn"])
        prev = by_claimant.get(cid, -1)
        if turn > prev:
            by_claimant[cid] = turn

    if not by_claimant:
        return (), None

    rows = tuple(
        {
            "schema": LAN_GOVERNANCE_FRONTIER_WITNESS_SCHEMA_V1,
            "claimant_session_id": cid,
            "observed_max_turn": turn,
        }
        for cid, turn in sorted(by_claimant.items(), key=lambda x: x[0])
    )
    return rows, max(by_claimant.values())


@dataclass(frozen=True)
class LanMergeContextParsed:
    frontier_turn: int | None
    cross_session_hint: dict[str, Any] | None
    frontier_witnesses: tuple[dict[str, Any], ...]
    witness_advisory_max_turn: int | None
    warnings: tuple[str, ...]


def parse_lan_merge_context(batch_obj: Mapping[str, Any]) -> LanMergeContextParsed:
    """
    Read ``merge_context`` from a LAN batch dict (integrity / DAO / judicial / mock_court).

    Invalid ``cross_session_hint`` yields a warning and ``cross_session_hint=None``; merge still runs.
    """
    mc = batch_obj.get("merge_context")
    if not isinstance(mc, dict):
        return LanMergeContextParsed(None, None, (), None, ())

    warnings: list[str] = []
    ft: int | None = None
    if "frontier_turn" in mc:
        ft = _coerce_non_negative_int(mc.get("frontier_turn"))

    hint: dict[str, Any] | None = None
    if "cross_session_hint" in mc:
        h, err = normalize_cross_session_hint(mc.get("cross_session_hint"))
        if err is not None:
            warnings.append(f"cross_session_hint_rejected:{err}")
        else:
            hint = h

    witnesses, adv_max = aggregate_frontier_witnesses(mc.get("frontier_witnesses"), warnings)

    return LanMergeContextParsed(ft, hint, witnesses, adv_max, tuple(warnings))
