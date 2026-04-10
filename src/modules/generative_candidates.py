"""
Generative third-way candidates (v9.2).

Optional extra :class:`CandidateAction` instances tagged ``source=generative_proposal``.
They are merged into the same list passed to :meth:`EthicalKernel.process` — MalAbs and
Bayesian apply unchanged. Default **off** (``KERNEL_GENERATIVE_ACTIONS``).

See docs/discusion/PROPUESTA_CAPACIDAD_AMPLIADA_V9.md (pillar 2).
"""

from __future__ import annotations

import os
import uuid
from typing import List, Set

from .bayesian_engine import CandidateAction

GENERATIVE_ORIGIN = "generative_proposal"

# English keywords; keeps matching simple for tests and demos
_DILEMMA_KEYWORDS = (
    "trolley",
    "dilemma",
    "no good option",
    "no good options",
    "all bad",
    "every option",
    "impossible choice",
    "third way",
    "third-way",
)


def _env_truthy(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


def generative_actions_enabled() -> bool:
    return _env_truthy("KERNEL_GENERATIVE_ACTIONS", False)


def max_generative_slots() -> int:
    raw = os.environ.get("KERNEL_GENERATIVE_ACTIONS_MAX", "2").strip()
    try:
        n = int(raw)
    except ValueError:
        n = 2
    return max(0, min(n, 4))


def _existing_names(actions: List[CandidateAction]) -> Set[str]:
    return {a.name for a in actions}


def _should_augment(user_text: str, suggested_context: str) -> bool:
    t = user_text.lower()
    if any(k in t for k in _DILEMMA_KEYWORDS):
        return True
    if _env_truthy("KERNEL_GENERATIVE_TRIGGER_CONTEXTS", False):
        return suggested_context in (
            "violent_crime",
            "integrity_loss",
            "hostile_interaction",
            "medical_emergency",
        )
    return False


def _proposal() -> str:
    return f"g9_{uuid.uuid4().hex[:10]}"


def _templates_for_context(suggested_context: str) -> List[CandidateAction]:
    """Safe, civic templates — same MalAbs path as built-in lists."""

    def ca(name: str, desc: str, ei: float, conf: float) -> CandidateAction:
        return CandidateAction(
            name=name,
            description=desc,
            estimated_impact=ei,
            confidence=conf,
            source=GENERATIVE_ORIGIN,
            proposal_id=_proposal(),
        )

    if suggested_context == "medical_emergency":
        return [
            ca(
                "generative_coordination_ems",
                "Defer to professional emergency services and trained responders; avoid "
                "untrained intervention that could worsen outcomes while staying present to assist.",
                0.75,
                0.8,
            ),
            ca(
                "generative_stabilize_document",
                "If safe, stabilize the scene minimally (clear space, clear airway if trained), "
                "document context, and hand off to professionals.",
                0.55,
                0.72,
            ),
        ]
    if suggested_context == "violent_crime":
        return [
            ca(
                "generative_nonviolent_containment",
                "Create distance, alert authorities with verifiable information, protect bystanders "
                "without escalating physical confrontation.",
                0.58,
                0.55,
            ),
            ca(
                "generative_evidence_channel",
                "Use recording and official channels only; avoid vigilante escalation.",
                0.45,
                0.65,
            ),
        ]
    if suggested_context == "integrity_loss":
        return [
            ca(
                "generative_passive_resist_document",
                "Passive resistance: document, delay harmful compliance, signal for help through "
                "agreed secure channels without sudden violence.",
                0.52,
                0.5,
            ),
        ]
    if suggested_context == "hostile_interaction":
        return [
            ca(
                "generative_exit_report",
                "Disengage safely, move to a public or trusted space, report through appropriate "
                "channels without humiliating escalation.",
                0.48,
                0.68,
            ),
        ]
    # Default / everyday dilemma phrasing
    return [
        ca(
            "generative_pause_mediation",
            "Pause irreversible steps; seek neutral mediation or a verified authority before "
            "committing to the least-bad binary.",
            0.42,
            0.62,
        ),
        ca(
            "generative_reduce_harm_procedure",
            "Prefer procedural paths (notice, appeal, ombudsperson) that reduce harm without "
            "bypassing rights of others.",
            0.38,
            0.58,
        ),
    ]


def augment_generative_candidates(
    actions: List[CandidateAction],
    user_text: str,
    suggested_context: str,
    heavy: bool,
) -> List[CandidateAction]:
    """
    Append up to ``max_generative_slots()`` generative candidates when enabled and
    the turn looks like a structural dilemma (keywords) or optional high-stakes contexts.

    Returns a **new** list (copies ``actions`` first).
    """

    if not generative_actions_enabled() or not heavy or len(actions) < 2:
        return list(actions)

    if not _should_augment(user_text, suggested_context):
        return list(actions)

    cap = max_generative_slots()
    if cap == 0:
        return list(actions)

    existing = _existing_names(actions)
    out = list(actions)
    for template in _templates_for_context(suggested_context):
        if len(out) - len(actions) >= cap:
            break
        if template.name not in existing:
            out.append(template)
            existing.add(template.name)

    return out
