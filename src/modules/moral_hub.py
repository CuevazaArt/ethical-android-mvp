"""
Moral Infrastructure Hub — V12 Phase 1 (read-only constitution export + audit hooks).

Does **not** replace ``PreloadedBuffer`` or MalAbs. Provides:
- JSON snapshot of Level-0 (immutable) principles for transparency APIs
- Optional DAO audit lines for R&D transparency protocol and mock community proposals
- Stubs for EthosPayroll narrative (audit-only)

See docs/discusion/PROPUESTA_ESTADO_ETOSOCIAL_V12.md and UNIVERSAL_ETHOS_AND_HUB.md.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from enum import IntEnum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .deontic_gate import validate_draft_or_raise, validate_draft_structure
from .local_sovereignty import evaluate_calibration_update

if TYPE_CHECKING:
    from .buffer import PreloadedBuffer
    from .mock_dao import MockDAO


class ConstitutionLevel(IntEnum):
    """
    L0 hard core (MalAbs + universal principles) — fixed in code today.
    L1 coexistence / culture — future community vote.
    L2 owner preferences — must not violate L0/L1.
    """

    HARD_CORE = 0
    COEXISTENCE = 1
    OWNER_DIRECTIVE = 2


def moral_hub_public_enabled() -> bool:
    """Expose GET /constitution and related when set."""
    v = os.environ.get("KERNEL_MORAL_HUB_PUBLIC", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def democratic_buffer_mock_enabled() -> bool:
    """Allow mock ``create_proposal`` for community articles (dev/demo)."""
    v = os.environ.get("KERNEL_DEMOCRATIC_BUFFER_MOCK", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def transparency_audit_enabled() -> bool:
    """Log R&D / developer transparency events to DAO audit ledger."""
    v = os.environ.get("KERNEL_TRANSPARENCY_AUDIT", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def ethos_payroll_mock_enabled() -> bool:
    """Append conceptual payroll / value-flow lines to audit (mock)."""
    v = os.environ.get("KERNEL_ETHOS_PAYROLL_MOCK", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def constitution_draft_ws_enabled() -> bool:
    """Allow WebSocket JSON ``constitution_draft`` to append L1/L2 drafts (session kernel)."""
    v = os.environ.get("KERNEL_MORAL_HUB_DRAFT_WS", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def chat_include_constitution() -> bool:
    """Include full ``constitution`` object in WebSocket responses (can be large)."""
    v = os.environ.get("KERNEL_CHAT_INCLUDE_CONSTITUTION", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def dao_governance_api_enabled() -> bool:
    """V12.3 — WebSocket ``dao_vote`` / ``dao_resolve`` / ``dao_submit_draft`` / ``dao_list``."""
    v = os.environ.get("KERNEL_MORAL_HUB_DAO_VOTE", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def dao_integrity_audit_ws_enabled() -> bool:
    """WebSocket ``integrity_alert`` — record ``HubAudit:dao_integrity`` on MockDAO (local transparency)."""
    v = os.environ.get("KERNEL_DAO_INTEGRITY_AUDIT_WS", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def proposal_to_public(p: Any) -> Dict[str, Any]:
    """JSON-safe summary of a DAO :class:`~src.modules.mock_dao.Proposal` (quadratic vote totals)."""
    vf = getattr(p, "votes_for", None) or {}
    va = getattr(p, "votes_against", None) or {}
    tw = sum(float(x) for x in vf.values())
    ta = sum(float(x) for x in va.values())
    return {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "type": p.type,
        "status": p.status,
        "timestamp": p.timestamp,
        "weighted_votes_for": round(tw, 4),
        "weighted_votes_against": round(ta, 4),
        "voter_count_for": len(vf),
        "voter_count_against": len(va),
    }


def constitution_snapshot(
    buffer: "PreloadedBuffer",
    kernel: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Read-only export of L0 from ``PreloadedBuffer``; optional L1/L2 **draft** articles from ``kernel``
    (persisted in :class:`KernelSnapshotV1` as of schema v2).
    """
    principles: List[Dict[str, Any]] = []
    for name, p in sorted(buffer.principles.items(), key=lambda x: x[0]):
        principles.append(
            {
                "id": name,
                "level": ConstitutionLevel.HARD_CORE.value,
                "title": name,
                "description": p.description,
                "weight": p.weight,
                "locked": True,
            }
        )
    l1: List[Dict[str, Any]] = []
    l2: List[Dict[str, Any]] = []
    if kernel is not None:
        l1 = list(getattr(kernel, "constitution_l1_drafts", []) or [])
        l2 = list(getattr(kernel, "constitution_l2_drafts", []) or [])
    disc = (
        "L0 reflects code in buffer.py. L1/L2 list draft articles when present (V12.2); "
        "they do not override PreloadedBuffer."
    )
    return {
        "version": "v12-universal-ethos-snapshot",
        "levels": {
            "0": {
                "name": "hard_core",
                "label": "Universal principles (immutable in MVP)",
                "quorum_note": "Production DemocraticBuffer would require supermajority vote to change L0",
                "principles": principles,
            },
            "1": {
                "name": "coexistence",
                "label": "Norms of coexistence (drafts; persisted in kernel snapshot)",
                "principles": l1,
            },
            "2": {
                "name": "owner_directive",
                "label": "Owner preferences (drafts; bounded by L0/L1 in production)",
                "principles": l2,
            },
        },
        "disclaimer": disc,
    }


def add_constitution_draft(
    kernel: Any,
    level: int,
    title: str,
    body: str,
    proposer: str = "user",
) -> Dict[str, Any]:
    """
    Append a draft article to L1 or L2 on the kernel (checkpoint / snapshot persist).

    Does **not** change ``PreloadedBuffer`` or MalAbs.
    """
    if level not in (1, 2):
        raise ValueError("level must be 1 or 2")
    title = (title or "").strip()[:500]
    body = (body or "").strip()[:4000]
    if not title:
        raise ValueError("title required")
    validate_draft_or_raise(title, body, kernel.buffer)
    d: Dict[str, Any] = {
        "id": str(uuid.uuid4()),
        "title": title,
        "body": body,
        "proposer": (proposer or "user")[:200],
        "created": datetime.now().isoformat(),
        "status": "draft",
    }
    if level == 1:
        kernel.constitution_l1_drafts.append(d)
    else:
        kernel.constitution_l2_drafts.append(d)
    return d


def submit_constitution_draft_for_vote(
    kernel: Any,
    level: int,
    draft_id: str,
) -> Dict[str, Any]:
    """
    Create a MockDAO proposal from an L1/L2 constitution draft (off-chain pipeline).

    Does **not** mutate ``PreloadedBuffer``. Idempotent if ``dao_proposal_id`` already set.
    """
    if level not in (1, 2):
        return {"ok": False, "error": "level must be 1 or 2"}
    did = (draft_id or "").strip()
    if not did:
        return {"ok": False, "error": "draft_id required"}
    lst = kernel.constitution_l1_drafts if level == 1 else kernel.constitution_l2_drafts
    draft = next((d for d in lst if d.get("id") == did), None)
    if not draft:
        return {"ok": False, "error": "draft not found"}
    existing = draft.get("dao_proposal_id")
    if existing:
        return {"ok": True, "proposal_id": existing, "already_submitted": True}
    title = str(draft.get("title", ""))
    body = str(draft.get("body", ""))
    ok_struct, schema_errs = validate_draft_structure(title, body)
    if not ok_struct:
        return {"ok": False, "error": "draft_schema: " + ",".join(schema_errs)}
    try:
        validate_draft_or_raise(title, body, kernel.buffer)
    except ValueError as e:
        return {"ok": False, "error": str(e)}
    title_pub = title[:500]
    body_pub = body[:4000]
    prop = kernel.dao.create_proposal(
        title=f"[Constitution L{level}] {title_pub}",
        description=body_pub,
        type="ethics",
    )
    draft["dao_proposal_id"] = prop.id
    draft["status"] = "voting"
    return {"ok": True, "proposal_id": prop.id, "title": prop.title}


def apply_proposal_resolution_to_constitution_drafts(
    kernel: Any,
    proposal_id: str,
    resolve_result: Dict[str, Any],
) -> int:
    """
    After :meth:`MockDAO.resolve_proposal`, set linked L1/L2 draft ``status`` to
    ``approved`` or ``rejected`` when ``dao_proposal_id`` matches.
    """
    pid = (proposal_id or "").strip()
    if not pid:
        return 0
    outcome = resolve_result.get("outcome")
    if outcome not in ("approved", "rejected"):
        return 0
    ts = datetime.now().isoformat()
    n = 0
    for lst in (kernel.constitution_l1_drafts, kernel.constitution_l2_drafts):
        for d in lst:
            if d.get("dao_proposal_id") == pid:
                d["status"] = "approved" if outcome == "approved" else "rejected"
                d["resolved_at"] = ts
                d["resolution_outcome"] = outcome
                n += 1
    return n


def audit_transparency_event(dao: "MockDAO", event: str, detail: str = "") -> None:
    """
    Safe Observation / R&D protocol: each logged access is auditable (single-process mock).

    Pair with documented policy: no secret permanent observation — see V12 doc.
    """
    if not transparency_audit_enabled():
        return
    msg = f"TransparencyAudit event={event}"
    if detail:
        msg += f" | {detail[:500]}"
    dao.register_audit("incident", msg)


def propose_community_article_mock(
    dao: "MockDAO",
    title: str,
    description: str,
    target_level: int,
    kernel: Any = None,
) -> Optional[Any]:
    """
    Simulated path: institution/human proposes an ethical article for future buffer layers.

    Creates a DAO proposal (does not mutate ``PreloadedBuffer``). Runs
    :func:`~local_sovereignty.evaluate_calibration_update` on the payload when
    ``KERNEL_LOCAL_SOVEREIGNTY`` is on (default).
    """
    if not democratic_buffer_mock_enabled():
        return None
    if target_level not in (0, 1, 2):
        target_level = 1
    buf = kernel.buffer if kernel is not None else None
    ev = evaluate_calibration_update(
        {
            "title": (title or "")[:500],
            "description": (description or "")[:2000],
            "target_level": int(target_level),
        },
        buffer=buf,
    )
    if not ev.accept:
        dao.register_audit(
            "incident",
            f"LocalSovereignty: rejected | {ev.reason} | {ev.audit_hint}"[:2000],
        )
        return None
    desc = f"[Level {target_level} target] {description}"
    return dao.create_proposal(
        title=f"[DemocraticBuffer] {title}",
        description=desc[:2000],
        type="ethics",
    )


def ethos_payroll_record_mock(dao: "MockDAO", line: str) -> None:
    """Narrative-only payroll / value-flow audit line for demos."""
    if not ethos_payroll_mock_enabled():
        return
    dao.register_audit("calibration", f"EthosPayroll(mock): {line[:800]}")
