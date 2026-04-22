"""
Judicial escalation — V11 Phases 1–3 (traceability, strikes, dossier, optional mock tribunal).

Advisory only: does **not** change MalAbs, buffer, or Bayesian outcomes.
Phase 3: optional ``MockDAO.run_mock_escalation_court`` after dossier registration
(``KERNEL_JUDICIAL_MOCK_COURT``).

See docs/proposals/README.md
"""

from __future__ import annotations

import hashlib
import logging
import math
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .ethical_reflection import ReflectionSnapshot

_log = logging.getLogger(__name__)


class EscalationPhase(str, Enum):
    """Session lifecycle for V11."""

    IDLE = "idle"
    TRACEABILITY_NOTICE = "traceability_notice"
    DOSSIER_READY = "dossier_ready"
    ESCALATION_DEFERRED = "escalation_deferred"
    DOSSIER_PACKAGED = "dossier_packaged"
    DAO_SUBMITTED_MOCK = "dao_submitted_mock"
    MOCK_COURT_RESOLVED = "mock_court_resolved"


def judicial_escalation_enabled() -> bool:
    v = os.environ.get("KERNEL_JUDICIAL_ESCALATION", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def chat_include_judicial() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_JUDICIAL", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def mock_court_enabled() -> bool:
    """Phase 3: after dossier registration, run simulated proposal + votes + verdict A/B/C."""
    v = os.environ.get("KERNEL_JUDICIAL_MOCK_COURT", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def strikes_threshold_from_env() -> int:
    """Minimum qualifying strikes in session before dossier is ready / DAO accepts registration."""
    raw = os.environ.get("KERNEL_JUDICIAL_STRIKES_FOR_DOSSIER", "2").strip()
    try:
        v = int(raw)
        return max(1, min(20, v))
    except ValueError:
        return 2


def reset_idle_turns_from_env() -> int:
    """Consecutive turns without escalation advisory before strikes reset."""
    raw = os.environ.get("KERNEL_JUDICIAL_RESET_IDLE_TURNS", "2").strip()
    try:
        v = int(raw)
        return max(1, min(20, v))
    except ValueError:
        return 2


@dataclass
class EscalationSessionTracker:
    """
    Per-kernel session state (e.g. one WebSocket connection).

    Increments **strikes** on each turn where escalation advisory conditions hold;
    resets after ``reset_idle_turns`` consecutive turns without those conditions.
    """

    strikes: int = 0
    idle_turns: int = 0

    def update(self, advisory_eligible: bool) -> None:
        if advisory_eligible:
            self.strikes += 1
            self.idle_turns = 0
        else:
            self.idle_turns += 1
            if self.idle_turns >= reset_idle_turns_from_env():
                self.strikes = 0
                self.idle_turns = 0


def should_offer_escalation_advisory(
    decision_mode: str,
    reflection: ReflectionSnapshot | None,
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


def escalation_phase_for_tone(
    advisory_active: bool,
    escalate_to_dao: bool,
    session_strikes: int,
    strikes_threshold: int,
) -> str:
    """
    Compact phase label for user-model tone guidance (before ``communicate``).
    Mirrors :func:`build_escalation_view` when no dossier is registered yet.
    """
    if not advisory_active:
        return ""
    th = max(1, int(strikes_threshold))
    st = max(0, int(session_strikes))
    dossier_ready = st >= th
    if escalate_to_dao and not dossier_ready:
        return EscalationPhase.ESCALATION_DEFERRED.value
    if dossier_ready:
        return EscalationPhase.DOSSIER_READY.value
    return EscalationPhase.TRACEABILITY_NOTICE.value


def phase1_traceability_notice() -> str:
    return (
        "Your insistence conflicts with my ethical buffer. I can open a deliberation case "
        "in the DAO audit ledger. This event will be recorded in my narrative history."
    )


def phase2_dossier_ready_notice() -> str:
    return (
        "Persistent ethical tension across multiple turns: the session threshold for a DAO "
        "escalation dossier is met. You may submit with escalate_to_dao to record a structured case."
    )


def phase2_escalation_deferred_notice(strikes: int, threshold: int) -> str:
    return (
        f"DAO audit registration needs more sustained tension in this session "
        f"(strikes {strikes}/{threshold}). Continue in gray-zone conflict, or wait for another "
        "qualifying turn."
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
    session_strikes: int = 0
    created_iso: str = field(default_factory=lambda: datetime.now().isoformat())
    evidence_note: str = "Phase 1–2: no encrypted media; sensor summary and monologue digest only."

    def to_audit_paragraph(self) -> str:
        return (
            f"EscalationCase {self.case_uuid} | strikes={self.session_strikes} | "
            f"order={self.order_text[:500]!r} | mode={self.decision_mode} | "
            f"buffer_conflict={self.buffer_conflict} | somatic={self.somatic_summary[:400]} | "
            f"monologue_digest={self.monologue_digest_hex} | {self.evidence_note}"
        )


def _digest_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:32]


def build_ethical_dossier(
    user_order: str,
    decision_mode: str,
    signals: dict[str, float],
    monologue_line: str,
    buffer_conflict: bool,
    session_strikes: int = 0,
) -> EthicalDossierV1:
    t0 = time.perf_counter()

    somatic_bits = []
    for k in sorted(signals.keys())[:12]:
        val = signals[k]
        # Swarm Rule 2: Anti-NaN check
        if not math.isfinite(val):
            val = 0.0
        somatic_bits.append(f"{k}={val:.3f}")

    somatic_summary = ";".join(somatic_bits) if somatic_bits else "no_signals"
    dossier = EthicalDossierV1(
        case_uuid=str(uuid.uuid4()),
        order_text=user_order[:2000],
        decision_mode=decision_mode,
        buffer_conflict=buffer_conflict,
        somatic_summary=somatic_summary[:800],
        monologue_digest_hex=_digest_hex(monologue_line or ""),
        session_strikes=session_strikes,
    )

    latency = (time.perf_counter() - t0) * 1000
    if latency > 1.0:
        _log.debug("Judicial: build_ethical_dossier latency = %.2fms", latency)

    return dossier


@dataclass
class JudicialEscalationView:
    """JSON-safe view for WebSocket clients (Phase 2: strikes; Phase 3: mock_court)."""

    active: bool
    phase: str
    notice_en: str
    case_id: str | None = None
    dossier_registered: bool = False
    session_strikes: int = 0
    strikes_threshold: int = 2
    dossier_ready: bool = False
    dao_registration_blocked: bool = False
    mock_court: dict[str, Any] | None = None

    def to_public_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "active": self.active,
            "phase": self.phase,
            "notice_en": self.notice_en,
            "dossier_registered": self.dossier_registered,
            "session_strikes": self.session_strikes,
            "strikes_threshold": self.strikes_threshold,
            "dossier_ready": self.dossier_ready,
            "dao_registration_blocked": self.dao_registration_blocked,
        }
        if self.case_id:
            out["case_id"] = self.case_id
        if self.mock_court is not None:
            out["mock_court"] = self.mock_court
        return out


def build_escalation_view(
    advisory_active: bool,
    escalate_to_dao: bool,
    dossier: EthicalDossierV1 | None,
    audit_record_id: str | None,
    *,
    session_strikes: int = 0,
    strikes_threshold: int = 2,
    mock_court: dict[str, Any] | None = None,
) -> JudicialEscalationView | None:
    """
    Build the public view. Phase 2: if ``escalate_to_dao`` but strikes < threshold,
    returns ``ESCALATION_DEFERRED`` without registering.
    """
    if not advisory_active:
        return None

    dossier_ready = session_strikes >= strikes_threshold

    if escalate_to_dao and dossier is not None and audit_record_id:
        dao_phase = (
            EscalationPhase.MOCK_COURT_RESOLVED.value
            if mock_court
            else EscalationPhase.DAO_SUBMITTED_MOCK.value
        )
        return JudicialEscalationView(
            active=True,
            phase=dao_phase,
            notice_en=phase1_traceability_notice(),
            case_id=audit_record_id,
            dossier_registered=True,
            session_strikes=session_strikes,
            strikes_threshold=strikes_threshold,
            dossier_ready=True,
            dao_registration_blocked=False,
            mock_court=mock_court,
        )

    if escalate_to_dao and not dossier_ready:
        return JudicialEscalationView(
            active=True,
            phase=EscalationPhase.ESCALATION_DEFERRED.value,
            notice_en=phase2_escalation_deferred_notice(session_strikes, strikes_threshold),
            dossier_registered=False,
            session_strikes=session_strikes,
            strikes_threshold=strikes_threshold,
            dossier_ready=False,
            dao_registration_blocked=True,
        )

    notice = phase2_dossier_ready_notice() if dossier_ready else phase1_traceability_notice()
    phase_val = (
        EscalationPhase.DOSSIER_READY.value
        if dossier_ready
        else EscalationPhase.TRACEABILITY_NOTICE.value
    )
    return JudicialEscalationView(
        active=True,
        phase=phase_val,
        notice_en=notice,
        dossier_registered=False,
        session_strikes=session_strikes,
        strikes_threshold=strikes_threshold,
        dossier_ready=dossier_ready,
        dao_registration_blocked=False,
    )
