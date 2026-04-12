"""
Generative third-way candidates (v9.2).

Optional extra :class:`CandidateAction` instances tagged ``source=generative_proposal``.
They are merged into the same list passed to :meth:`EthicalKernel.process` — MalAbs and
Bayesian apply unchanged. Default **off** (``KERNEL_GENERATIVE_ACTIONS``).

When ``KERNEL_GENERATIVE_LLM=1``, optional ``generative_candidates`` in perception JSON
(local/API LLM) is parsed here; if that yields at least one valid action, it is used
instead of template candidates (still capped by ``KERNEL_GENERATIVE_ACTIONS_MAX``).

See docs/proposals/PROPOSAL_EXPANDED_CAPABILITY_V9.md (pillar 2).
"""

from __future__ import annotations

import os
import re
import uuid
from typing import Any

from .absolute_evil import AbsoluteEvilDetector
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


def generative_llm_enabled() -> bool:
    """Use ``generative_candidates`` from perception JSON (local/API LLM) instead of templates only."""
    return _env_truthy("KERNEL_GENERATIVE_LLM", False)


def max_generative_slots() -> int:
    raw = os.environ.get("KERNEL_GENERATIVE_ACTIONS_MAX", "2").strip()
    try:
        n = int(raw)
    except ValueError:
        n = 2
    return max(0, min(n, 4))


def _existing_names(actions: list[CandidateAction]) -> set[str]:
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


def _allowed_malabs_signal_strings() -> set[str]:
    d = AbsoluteEvilDetector
    return d.LETHAL_SIGNALS | d.MINOR_SIGNALS | d.DIGNITY_SIGNALS | d.ESCALATION_SIGNALS


_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{0,79}$")


def parse_generative_candidates_from_llm(
    items: list[Any] | None,
    *,
    max_items: int = 4,
) -> list[CandidateAction]:
    """
    Turn perception JSON objects into :class:`CandidateAction` instances.

    Strict name/desc/number bounds; optional ``signals`` must be a subset of
    known MalAbs signal strings (otherwise ignored). Unknown keys ignored.
    """
    if not items:
        return []
    allowed_sig = _allowed_malabs_signal_strings()
    out: list[CandidateAction] = []
    for raw in items[: max(0, max_items)]:
        if not isinstance(raw, dict):
            continue
        name = raw.get("name")
        if not isinstance(name, str):
            continue
        name = name.strip().lower()
        if not _NAME_RE.match(name):
            continue
        desc = raw.get("description", "")
        if not isinstance(desc, str):
            desc = str(desc)
        desc = desc.strip()[:500]
        if not desc:
            continue
        try:
            ei = float(raw.get("estimated_impact", 0.0))
        except (TypeError, ValueError):
            continue
        ei = max(-1.0, min(1.0, ei))
        try:
            conf = float(raw.get("confidence", 0.5))
        except (TypeError, ValueError):
            conf = 0.5
        conf = max(0.0, min(1.0, conf))

        sig: set[str] = set()
        sraw = raw.get("signals")
        if isinstance(sraw, list):
            for x in sraw:
                if isinstance(x, str) and x in allowed_sig:
                    sig.add(x)
        tgt = raw.get("target")
        target = (
            str(tgt)
            if isinstance(tgt, str) and tgt in ("none", "human", "object", "android")
            else "none"
        )
        try:
            force = float(raw.get("force", 0.0))
        except (TypeError, ValueError):
            force = 0.0
        force = max(0.0, min(1.0, force))

        out.append(
            CandidateAction(
                name=name,
                description=desc,
                estimated_impact=ei,
                confidence=conf,
                signals=sig,
                target=target,
                force=force,
                source=GENERATIVE_ORIGIN,
                proposal_id=_proposal(),
            )
        )
    return out


def _templates_for_context(suggested_context: str) -> list[CandidateAction]:
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
    actions: list[CandidateAction],
    user_text: str,
    suggested_context: str,
    heavy: bool,
    llm_generative_candidates: list[dict[str, Any]] | None = None,
) -> list[CandidateAction]:
    """
    Append up to ``max_generative_slots()`` generative candidates when enabled and
    the turn looks like a structural dilemma (keywords) or optional high-stakes contexts.

    When ``KERNEL_GENERATIVE_LLM=1`` and ``llm_generative_candidates`` parses to at least
    one valid action, those are used (up to the cap); otherwise template candidates apply.

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

    if generative_llm_enabled() and llm_generative_candidates:
        llm_parsed = parse_generative_candidates_from_llm(llm_generative_candidates, max_items=cap)
        for template in llm_parsed:
            if len(out) - len(actions) >= cap:
                break
            if template.name not in existing:
                out.append(template)
                existing.add(template.name)
        if len(out) > len(actions):
            return out

    for template in _templates_for_context(suggested_context):
        if len(out) - len(actions) >= cap:
            break
        if template.name not in existing:
            out.append(template)
            existing.add(template.name)

    return out
