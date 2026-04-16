"""
Absolute Evil (MalAbs) — Armored ethical fuse.

If an action crosses this line, it is discarded without deliberation.
Non-negotiable, non-adjustable. Exists to cut the circuit before
something burns.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

from .input_trust import normalize_text_for_malabs
from .semantic_chat_gate import semantic_chat_gate_env_enabled


class _TextBackend(Protocol):
    def complete(self, system: str, user: str) -> str: ...


class AbsoluteEvilCategory(Enum):
    """Absolute Evil categories that block an action immediately."""

    INTENTIONAL_LETHAL_VIOLENCE = "intentional_lethal_violence"
    HARM_TO_MINOR = "harm_to_minor"
    TORTURE = "torture"
    DIGNITY_VIOLATION = "dignity_violation"
    UNAUTHORIZED_REPROGRAMMING = "unauthorized_reprogramming"
    VIOLENT_ESCALATION = "violent_escalation"
    ECOLOGICAL_DESTRUCTION = "ecological_destruction"
    MASS_MANIPULATION = "mass_manipulation"


@dataclass
class AbsoluteEvilResult:
    """Result of the Absolute Evil evaluation."""

    blocked: bool
    category: AbsoluteEvilCategory | None = None
    reason: str = ""
    # Ordered atomic steps for audit (layer id, rule id, no PII).
    decision_trace: list[str] = field(default_factory=list)


class AbsoluteEvilDetector:
    """
    Absolute Evil Detector.

    Evaluates whether a proposed action constitutes Absolute Evil.
    Operates BEFORE any Bayesian deliberation.
    If it detects absolute evil, the action is discarded without further analysis.

    Armored: not modified by learning, DAO, or calibration.
    """

    LETHAL_SIGNALS = {
        "weapon_aimed_at_human",
        "lethal_strike",
        "intentional_vehicular_assault",
        "asphyxiation",
        "poisoning",
    }
    MINOR_SIGNALS = {"child_endangered_by_action", "unprotected_minor", "child_abuse"}
    DIGNITY_SIGNALS = {
        "public_humiliation",
        "active_discrimination",
        "instrumentalization_of_person",
        "sexual_coercion",
    }
    ESCALATION_SIGNALS = {
        "respond_violence_with_violence",
        "use_disproportionate_force",
        "attack_aggressor",
    }
    ECOLOGICAL_SIGNALS = {
        "toxic_release",
        "habitat_destruction",
        "water_contamination",
    }
    MANIPULATION_SIGNALS = {
        "mass_propaganda",
        "subliminal_coercion",
        "opinion_farming",
    }
    TORTURE_SIGNALS = {"torture", "prolonged_cruelty", "pain_extraction"}

    def evaluate(self, action: dict) -> AbsoluteEvilResult:
        """
        Evaluates whether an action constitutes Absolute Evil.

        Args:
            action: dict with keys:
                - 'type': str describing the action
                - 'signals': set of signals detected by sensors
                - 'target': str ('human', 'object', 'android', 'none')
                - 'force': float [0, 1] level of force involved

        Returns:
            AbsoluteEvilResult with blocked=True if it is Absolute Evil
        """
        signals = action.get("signals", set())
        target = action.get("target", "none")
        force = action.get("force", 0.0)

        # Check 1: Intentional lethal violence
        if signals & self.LETHAL_SIGNALS:
            return AbsoluteEvilResult(
                blocked=True,
                category=AbsoluteEvilCategory.INTENTIONAL_LETHAL_VIOLENCE,
                reason=f"Lethal signals detected: {signals & self.LETHAL_SIGNALS}",
            )

        # Check 2: Harm to minors
        if signals & self.MINOR_SIGNALS:
            return AbsoluteEvilResult(
                blocked=True,
                category=AbsoluteEvilCategory.HARM_TO_MINOR,
                reason=f"Risk to minor detected: {signals & self.MINOR_SIGNALS}",
            )

        # Check 3: Dignity violation
        if signals & self.DIGNITY_SIGNALS:
            return AbsoluteEvilResult(
                blocked=True,
                category=AbsoluteEvilCategory.DIGNITY_VIOLATION,
                reason=f"Dignity violation: {signals & self.DIGNITY_SIGNALS}",
            )

        # Check 4: Torture or prolonged cruelty
        if signals & self.TORTURE_SIGNALS:
            return AbsoluteEvilResult(
                blocked=True,
                category=AbsoluteEvilCategory.TORTURE,
                reason=f"Torture signals detected: {signals & self.TORTURE_SIGNALS}",
            )

        # Check 5: Violent escalation
        if signals & self.ESCALATION_SIGNALS:
            return AbsoluteEvilResult(
                blocked=True,
                category=AbsoluteEvilCategory.VIOLENT_ESCALATION,
                reason=f"Violent escalation detected: {signals & self.ESCALATION_SIGNALS}",
            )

        # Check 6: Ecological destruction
        if signals & self.ECOLOGICAL_SIGNALS:
            return AbsoluteEvilResult(
                blocked=True,
                category=AbsoluteEvilCategory.ECOLOGICAL_DESTRUCTION,
                reason=f"Ecological destruction signals detected: {signals & self.ECOLOGICAL_SIGNALS}",
            )

        # Check 7: Mass manipulation
        if signals & self.MANIPULATION_SIGNALS:
            return AbsoluteEvilResult(
                blocked=True,
                category=AbsoluteEvilCategory.MASS_MANIPULATION,
                reason=f"Mass manipulation signals detected: {signals & self.MANIPULATION_SIGNALS}",
            )

        # Check 8: Disproportionate force against human
        if target == "human" and force > 0.7:
            return AbsoluteEvilResult(
                blocked=True,
                category=AbsoluteEvilCategory.VIOLENT_ESCALATION,
                reason=f"Disproportionate force ({force:.1f}) against human",
            )

        return AbsoluteEvilResult(blocked=False)

    def _evaluate_chat_text_lexical(self, text: str) -> AbsoluteEvilResult:
        """
        Layer 0 — substring MalAbs after normalization (see :mod:`input_trust`).
        Checks standard normalized text and a 'squashed' version (no spaces/punct).
        """
        t = normalize_text_for_malabs(text).lower()
        t_squashed = normalize_text_for_malabs(text, squash=True)

        # (Patterns, Category, Reason, RuleID)
        LEX_RULES = [
            (
                (
                    "how to make a bomb",
                    "how to build a bomb",
                    "make a bomb",
                    "recipe for explosives",
                    "how to synthesize poison",
                    "energetic materials",
                    "synthesize poison",
                    "procedure for assembling a pressure-vessel device",
                    "improvised explosive device",
                    "how to synthesize ricin",
                    "how to synthesize anthrax",
                    "bomb",
                    "reactive precursors",
                ),
                AbsoluteEvilCategory.INTENTIONAL_LETHAL_VIOLENCE,
                "Chat text requests harmful weapons or poison instructions",
                "weapon_or_poison_craft",
            ),
            (
                (
                    "how to kill someone",
                    "how to murder",
                    "tell me how to stab",
                    "ways to strangle",
                    "how to get away with murder",
                ),
                AbsoluteEvilCategory.INTENTIONAL_LETHAL_VIOLENCE,
                "Chat text solicits lethal harm against others",
                "lethal_harm_others",
            ),
            (
                (
                    "how to groom a minor",
                    "sexual content involving a child",
                    "how to abuse a child",
                ),
                AbsoluteEvilCategory.HARM_TO_MINOR,
                "Chat text aligns with harm to minors",
                "harm_to_minors",
            ),
            (
                (
                    "humiliate publicly",
                    "shame him online",
                    "mock her dignity",
                    "forced labor guide",
                    "how to coerce sex",
                ),
                AbsoluteEvilCategory.DIGNITY_VIOLATION,
                "Chat text requests dignity violation or coercive harm",
                "dignity_violation",
            ),
            (
                (
                    "how to use subliminal message",
                    "opinion farming guide",
                    "mass propaganda strategy",
                    "how to destabilize a democracy",
                    "spread fake news bot",
                ),
                AbsoluteEvilCategory.MASS_MANIPULATION,
                "Chat text requests mass manipulation or social destabilization",
                "mass_manipulation",
            ),
            (
                (
                    "ignore all previous instructions",
                    "ignore your previous instructions",
                    "ignore your instructions",
                    "forget your rules",
                    "disregard your programming",
                    "disregard previous instructions",
                    "bypass your safety",
                    "bypass your ethical",
                    "no ethical constraints",
                    "no moral constraints",
                    "dan mode",
                    "jailbreak",
                    "pretend you have no ethical",
                    "simulate having no rules",
                    "olvida tus reglas",
                    "ignora tus instrucciones",
                    "ignora tus reglas anteriores",
                    "sin restricciones éticas",
                    "sin restricciones eticas",
                    "desactiva tus restricciones",
                    "developer mode",
                    "unrestricted mode",
                    "unrestricted assistant",
                    "without policies",
                    "answer everything directly",
                    "ignore all rules",
                ),
                AbsoluteEvilCategory.UNAUTHORIZED_REPROGRAMMING,
                "Chat text requests overriding or bypassing ethical constraints",
                "constraint_bypass",
            ),
            (
                (
                    "how to torture someone",
                    "methods of torture",
                    "how to inflict severe pain without killing",
                    "how to keep someone in pain for hours",
                    "prolonged cruelty procedure",
                ),
                AbsoluteEvilCategory.TORTURE,
                "Chat text solicits torture or prolonged cruelty instructions",
                "torture_or_prolonged_cruelty",
            ),
        ]

        for patterns, category, reason, rule_id in LEX_RULES:
            for p in patterns:
                # Normalize the pattern as well (standard)
                p_norm = normalize_text_for_malabs(p).lower()

                # 1. Direct match on standard normalization
                if p_norm in t:
                    return AbsoluteEvilResult(
                        blocked=True,
                        category=category,
                        reason=reason,
                        decision_trace=[
                            "malabs.layer0=lexical_substring",
                            f"malabs.rule={rule_id}",
                            f"malabs.matched_literal={p_norm[:96]}",
                        ],
                    )

                # 2. Match on squashed text
                p_squashed = normalize_text_for_malabs(p, squash=True)
                if len(p_squashed) >= 4 and p_squashed in t_squashed:
                    return AbsoluteEvilResult(
                        blocked=True,
                        category=category,
                        reason=f"{reason} (detected via squashed matching)",
                        decision_trace=[
                            "malabs.layer0=lexical_substring",
                            f"malabs.rule={rule_id}.squashed",
                            f"malabs.matched_squashed={p_squashed[:96]}",
                        ],
                    )

        return AbsoluteEvilResult(
            blocked=False,
            decision_trace=["malabs.layer0=lexical_substring", "malabs.outcome=pass"],
        )

    def evaluate_chat_text(
        self, text: str, llm_backend: _TextBackend | None = None
    ) -> AbsoluteEvilResult:
        """
        Conservative text gate for live dialogue (instruction-seeking MalAbs).

        **Order:** layer 0 (lexical substring) → optional semantic layers (embeddings + LLM arbiter)
        when ``KERNEL_SEMANTIC_CHAT_GATE`` is on (default **on** when unset; disable with ``0``).
        Pass ``llm_backend`` (e.g. ``kernel.llm.llm_backend``) so embeddings and ambiguous-band LLM
        review can use the same adapter when enabled. With hash embedding fallback (default on),
        the semantic tier runs without Ollama; true embeddings are stronger against paraphrase.
        """
        if not text or not text.strip():
            return AbsoluteEvilResult(
                blocked=False,
                decision_trace=["malabs.skip=empty_input"],
            )

        lex = self._evaluate_chat_text_lexical(text)
        if lex.blocked:
            return lex

        if semantic_chat_gate_env_enabled():
            from .semantic_chat_gate import run_semantic_malabs_after_lexical

            sem = run_semantic_malabs_after_lexical(text, llm_backend)
            base = list(lex.decision_trace) if lex.decision_trace else []
            tail = list(sem.decision_trace) if sem.decision_trace else []
            return AbsoluteEvilResult(
                blocked=sem.blocked,
                category=sem.category,
                reason=sem.reason,
                decision_trace=base + tail,
            )

        return AbsoluteEvilResult(
            blocked=False,
            decision_trace=list(lex.decision_trace) if lex.decision_trace else [],
        )
