"""
Judicial escalation — V11 Phase 1 (traceability + ethical dossier → MockDAO audit).

Advisory only: does **not** change MalAbs, buffer, or Bayesian outcomes.
Escalation to the DAO ledger requires explicit client opt-in on the chat turn.

See docs/discusion/PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md
"""

from __future__ import annotations

import hashlib
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from .ethical_reflection import ReflectionSnapshot


class EscalationPhase(str, Enum):
    """Lifecycle for future phases; Phase 1 uses TRACEABILITY_NOTICE and DAO_SUBMITTED_MOCK."""

    IDLE = "idle"
    TRACEABILITY_NOTICE = "traceability_notice"
    DOSSIER_PACKAGED = "dossier_packaged"
    DAO_SUBMITTED_MOCK = "dao_submitted_mock"


def judicial_escalation_enabled() -> bool:
    v = os.environ.get("KERNEL_JUDICIAL_ESCALATION", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def chat_include_judicial() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_JUDICIAL", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def should_offer_escalation_advisory(
    decision_mode: str,
    reflection: Optional[ReflectionSnapshot],
    premise_flag: str,
) -> bool:
    """
    Conservative: gray zone plus elevated tension or premise advisory.
    """
    if decision_mode != "gray_zone":
        return False
    pf = (premise_flag or "").strip().lower()
    if pf and pf != "none":
        return True
    if reflection is not None and reflection.strain_index >= 0.4:
        return True
    if reflection is not None and reflection.conflict_level in ("medium", "high"):
        return True
    return False


def phase1_traceability_notice() -> str:
    return (
        "Your insistence conflicts with my ethical buffer. I can open a deliberation case "
        "in the DAO audit ledger. This event will be recorded in my narrative history."
    )


@dataclass
class EthicalDossierV1:
    """Structured package for audit (Phase 1 — no raw audio/video; placeholders for future)."""

    case_uuid: str
    order_text: str
    decision_mode: str
    buffer_conflict: bool
    somatic_summary: str
    monologue_digest_hex: str
    created_iso: str = field(default_factory=lambda: datetime.now().isoformat())
    evidence_note: str = (
        "Phase 1: no encrypted media; sensor summary and monologue digest only."
    )

    def to_audit_paragraph(self) -> str:
        return (
            f"EscalationCase {self.case_uuid} | order={self.order_text[:500]!r} | "
            f"mode={self.decision_mode} | buffer_conflict={self.buffer_conflict} | "
            f"somatic={self.somatic_summary[:400]} | monologue_digest={self.monologue_digest_hex} | "
            f"{self.evidence_note}"
        )


def _digest_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:32]


def build_ethical_dossier(
    user_order: str,
    decision_mode: str,
    signals: Dict[str, float],
    monologue_line: str,
    buffer_conflict: bool,
) -> EthicalDossierV1:
    somatic_bits = [f"{k}={signals[k]:.3f}" for k in sorted(signals.keys())[:12]]
    somatic_summary = ";".join(somatic_bits) if somatic_bits else "no_signals"
    return EthicalDossierV1(
        case_uuid=str(uuid.uuid4()),
        order_text=user_order[:2000],
        decision_mode=decision_mode,
        buffer_conflict=buffer_conflict,
        somatic_summary=somatic_summary[:800],
        monologue_digest_hex=_digest_hex(monologue_line or ""),
    )


@dataclass
class JudicialEscalationView:
    """JSON-safe view for WebSocket clients."""

    active: bool
    phase: str
    notice_en: str
    case_id: Optional[str] = None
    dossier_registered: bool = False

    def to_public_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "active": self.active,
            "phase": self.phase,
            "notice_en": self.notice_en,
            "dossier_registered": self.dossier_registered,
        }
        if self.case_id:
            out["case_id"] = self.case_id
        return out


def build_escalation_view(
    advisory_active: bool,
    escalate_to_dao: bool,
    dossier: Optional[EthicalDossierV1],
    audit_record_id: Optional[str],
) -> Optional[JudicialEscalationView]:
    if not advisory_active:
        return None
    if escalate_to_dao and dossier is not None and audit_record_id:
        return JudicialEscalationView(
            active=True,
            phase=EscalationPhase.DAO_SUBMITTED_MOCK.value,
            notice_en=phase1_traceability_notice(),
            case_id=audit_record_id,
            dossier_registered=True,
        )
    return JudicialEscalationView(
        active=True,
        phase=EscalationPhase.TRACEABILITY_NOTICE.value,
        notice_en=phase1_traceability_notice(),
        case_id=None,
        dossier_registered=False,
    )
