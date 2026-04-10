"""
Moral Infrastructure Hub — V12 Phase 1 (read-only constitution export + audit hooks).

Does **not** replace ``PreloadedBuffer`` or MalAbs. Provides:
- JSON snapshot of Level-0 (immutable) principles for transparency APIs
- Optional DAO audit lines for R&D transparency protocol and mock community proposals
- Stubs for EthosPayroll narrative (audit-only)

See docs/discusion/PROPUESTA_ESTADO_ETOSOCIAL_V12.md
"""

from __future__ import annotations

import os
from enum import IntEnum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

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


def constitution_snapshot(buffer: "PreloadedBuffer") -> Dict[str, Any]:
    """
    Read-only export of Level-0 principles (current ``PreloadedBuffer``).
    Democratic evolution of content is **not** implemented; this documents the live constitution.
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
    return {
        "version": "v12-phase1-snapshot",
        "levels": {
            "0": {
                "name": "hard_core",
                "label": "Universal principles (immutable in MVP)",
                "quorum_note": "Production DemocraticBuffer would require supermajority vote to change L0",
                "principles": principles,
            },
            "1": {
                "name": "coexistence",
                "label": "Norms of coexistence (future community / culture)",
                "principles": [],
            },
            "2": {
                "name": "owner_directive",
                "label": "Owner preferences bounded by L0/L1 (future)",
                "principles": [],
            },
        },
        "disclaimer": "L0 reflects code in buffer.py; L1/L2 are placeholders until governance exists.",
    }


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
) -> Optional[Any]:
    """
    Simulated path: institution/human proposes an ethical article for future buffer layers.

    Creates a DAO proposal (does not mutate ``PreloadedBuffer``).
    """
    if not democratic_buffer_mock_enabled():
        return None
    if target_level not in (0, 1, 2):
        target_level = 1
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
