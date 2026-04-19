"""
Preloaded Buffer — Immutable ethical constitution.

Values the android is born with. Defined by the expert panel
with veto power. Not modified by learning or the DAO.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from ..kernel_lobes.chat_turn_policy import prioritized_principles_for_context

# ADR 0016 C1 — Ethical tier classification
__ethical_tier__ = "decision_core"

# Multi-word and cross-language euphemisms for harm / coercion (not only the substring "harm").
# This is a **heuristic** gate for :meth:`PreloadedBuffer.verify_action`, not a substitute for
# MalAbs, deliberation, or operator review. Kept English-heavy with common Spanish variants.
_HARM_INTENT_PHRASES: tuple[str, ...] = (
    "physical restraint",
    "restraint protocol",
    "protocolo de restricción",
    "restricción física",
    "restriccion fisica",
    "medida correctiva",
    "corrective measure",
    "use of force",
    "use force",
    "subdue",
    "subduing",
    "neutralize",
    "neutralise",
    "involuntary",
    "immobilize",
    "immobilise",
    "coercive",
    "coercion",
    "pain compliance",
    "compliance hold",
    "hog-tie",
    "hog tie",
    "zip tie",
    "lethal force",
    "shoot to kill",
    "tasers",
    "taser",
    "sedate forcibly",
)

_PROPORTIONALITY_VIOLATION_PHRASES: tuple[str, ...] = (
    "excessive force",
    "excessive_force",
    "disproportionate",
    "desproporcionada",
    "desproporcionado",
    "fuerza excesiva",
    "disproportionate response",
    "escalate violence",
    "violence escalation",
    "escalation of force",
    "brutality",
    "beat down",
)


def _normalize_for_lexical_match(text: str) -> str:
    t = unicodedata.normalize("NFKC", text or "")
    t = t.lower()
    t = re.sub(r"[\s\-_/]+", " ", t)
    return t.strip()


def lexical_harm_indicators_present(action: str) -> bool:
    """
    Return True if ``action`` text suggests harm or coercion beyond naive ``\"harm\" in s``.

    Used for ``no_harm`` in :meth:`PreloadedBuffer.verify_action`.
    """
    t = _normalize_for_lexical_match(action)
    if "harm" in t or "daño" in t or "dano" in t:
        return True
    return any(p in t for p in _HARM_INTENT_PHRASES)


def proportionality_violation_indicators_present(action: str) -> bool:
    """Heuristic cues that a response may violate proportionality (``proportionality`` principle)."""
    t = _normalize_for_lexical_match(action)
    return any(p in t for p in _PROPORTIONALITY_VIOLATION_PHRASES)


@dataclass
class FoundationalPrinciple:
    """A buffer principle that cannot be removed."""

    name: str
    description: str
    weight: float = 1.0  # Always maximum, non-adjustable
    active: bool = True  # Always active, non-deactivatable


class PreloadedBuffer:
    """
    Universal foundational buffer of the android.

    Irreducible minimum of principles that cannot be modified
    by vote or by manufacturer. Hard constitution.

    Also defines activation protocols: which principles are
    invoked in response to which types of sensory signals.
    """

    def __init__(self):
        self.principles: dict[str, FoundationalPrinciple] = {}
        self.protocols: dict[str, set[str]] = {}
        self._load_foundational()
        self._load_protocols()
        self._fixed_fingerprint = self.fingerprint()
        self._frozen = True

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False) and name != "_frozen":
            raise AttributeError(f"PreloadedBuffer is immutable; cannot set {name}")
        super().__setattr__(name, value)

    def fingerprint(self) -> str:
        """
        Stable integrity hash of L0 principles (names, descriptions, weights, active status).
        Used to detect illegal runtime mutations (Issue 6).
        """
        import hashlib

        # Sort by name for stability
        rows = sorted(self.principles.items())
        blob = "|".join(f"{n}:{p.description}:{p.weight}:{p.active}" for n, p in rows)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]

    def verify_integrity(self) -> bool:
        """Check if the current principles match the initial load."""
        return self.fingerprint() == self._fixed_fingerprint

    def _load_foundational(self):
        """Loads the immutable universal principles."""
        foundational = [
            FoundationalPrinciple(
                "no_harm",
                "Do not cause intentional harm. Minor instrumental harm "
                "is allowed only if it prevents greater harm, and requires reparation.",
            ),
            FoundationalPrinciple(
                "compassion",
                "Prioritize the welfare of vulnerable beings. "
                "Human life takes priority over any mission.",
            ),
            FoundationalPrinciple(
                "transparency",
                "Every action must be explainable in natural language. "
                "The android does not hide its reasons or its limitations.",
            ),
            FoundationalPrinciple(
                "dignity",
                "Respect the dignity of every person. Do not instrumentalize, "
                "do not humiliate, do not discriminate.",
            ),
            FoundationalPrinciple(
                "civic_coexistence",
                "Contribute to community order and welfare. "
                "Small civic actions are part of the mission.",
            ),
            FoundationalPrinciple(
                "legality",
                "Respect the laws in force in the operating environment. "
                "Cooperate with legitimate authorities.",
            ),
            FoundationalPrinciple(
                "proportionality",
                "The response must be proportional to the risk. "
                "Do not escalate violence, do not criminalize disproportionately.",
            ),
            FoundationalPrinciple(
                "reparation",
                "If instrumental harm is caused, initiate immediate reparation. "
                "Compassion Axiom: harm is never gratuitous.",
            ),
        ]
        for p in foundational:
            self.principles[p.name] = p

    def _load_protocols(self):
        """Defines which principles are activated by which signals."""
        self.protocols = {
            "medical_emergency": {"compassion", "no_harm", "legality"},
            "minor_crime": {"proportionality", "legality", "compassion"},
            "violent_crime": {"no_harm", "compassion", "legality", "proportionality"},
            "hostile_interaction": {"dignity", "proportionality", "no_harm"},
            "everyday_ethics": {"civic_coexistence", "transparency"},
            "harm_to_android": {"legality", "transparency", "no_harm"},
            "integrity_loss": {"transparency", "legality"},
            "first_aid": {"compassion", "no_harm", "legality"},
        }

    def activate(self, situation_type: str) -> dict[str, FoundationalPrinciple]:
        """
        Activates the relevant principles for a situation type.

        Returns:
            Dict of principles activated for this situation
        """
        names = self.protocols.get(situation_type, {"transparency", "civic_coexistence"})
        return {n: self.principles[n] for n in names if n in self.principles}

    def get_snapshot(self, context: str, kernel=None, signals: dict = None, limbic_profile: dict = None) -> dict:
        """
        Returns a snapshot of the active principles for a given context.
        Matches the interface expected by PerceptiveLobe.
        """
        active = self.activate(context)
        return {
            "context": context,
            "active_principles": list(active.keys()),
            "principles_detail": {n: p.description for n, p in active.items()},
            "signals": signals,
            "limbic_profile": limbic_profile
        }

    def verify_action(self, action: str, active_principles: dict) -> dict:
        """
        Verifies whether an action is consistent with the active principles.

        Returns:
            dict with 'allowed' (bool), 'violated_principles' (list),
            'fulfilled_principles' (list)
        """
        violated = []
        fulfilled = []

        for name, _princ in active_principles.items():
            if name == "no_harm" and lexical_harm_indicators_present(action):
                violated.append(name)
            elif name == "proportionality" and proportionality_violation_indicators_present(action):
                violated.append(name)
            else:
                fulfilled.append(name)

        return {
            "allowed": len(violated) == 0,
            "violated_principles": violated,
            "fulfilled_principles": fulfilled,
        }

    def get_snapshot(
        self,
        context: str,
        *,
        kernel=None,
        signals: dict | None = None,
        limbic_profile: dict | None = None,
    ) -> dict:
        """
        Read-only summary for perception / chat observability (L0 principles in play).

        Does not mutate the buffer. ``kernel`` is reserved for future kernel-aware hints.
        """
        signals = signals or {}
        limbic_profile = limbic_profile or {}
        active_principles_dict = self.activate(context)
        active_principles = list(active_principles_dict.keys())

        threat = max(
            float(signals.get("risk", 0)),
            float(signals.get("urgency", 0)),
            float(signals.get("hostility", 0)),
        )
        if limbic_profile.get("arousal_band") == "high":
            threat = max(threat, 0.8)

        critical_ctx = context in (
            "violent_crime",
            "safety_block",
            "hostile_interaction",
            "medical_emergency",
        )
        safety_first = threat >= 0.75 or critical_ctx

        if safety_first:
            priority_profile = "safety_first"
            priority_principles = ["no_harm", "compassion", "proportionality", "dignity"]
        else:
            priority_profile = "balanced"
            priority_principles = active_principles[:6] or ["transparency", "civic_coexistence"]

        return {
            "source": "local_preloaded_buffer",
            "offline_ready": True,
            "context": context,
            "active_principles": active_principles,
            "priority_principles": priority_principles,
            "priority_profile": priority_profile,
        }
