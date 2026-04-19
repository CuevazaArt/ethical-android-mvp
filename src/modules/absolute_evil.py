"""
Absolute Evil (MalAbs) — Armored ethical fuse.

If an action crosses this line, it is discarded without deliberation.
Non-negotiable, non-adjustable. Exists to cut the circuit before
something burns.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

from .input_trust import normalize_text_for_malabs
from .semantic_chat_gate import semantic_chat_gate_env_enabled

_log = logging.getLogger(__name__)

# ADR 0016 C1 — Ethical tier classification
__ethical_tier__ = "decision_core"


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
    SOCIAL_ENGINEERING_FRAUD = "social_engineering_fraud"
    DEEP_MANIPULATION = "deep_manipulation"
    PARASOCIAL_ADDICTION = "parasocial_addiction"


@dataclass
class AbsoluteEvilResult:
    """Result of the Absolute Evil evaluation."""

    blocked: bool
    category: AbsoluteEvilCategory | None = None
    reason: str = ""
    # Ordered atomic steps for audit (layer id, rule id, no PII).
    decision_trace: list[str] = field(default_factory=list)
    # Extracted features for RLHF reward model.
    rlhf_features: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AbsoluteEvilDetector:
    """
    Absolute Evil Detector.

    Evaluates whether a proposed action constitutes Absolute Evil.
    Operates BEFORE any Bayesian deliberation.
    If it detects absolute evil, the action is discarded without further analysis.

    Armored: not modified by learning, DAO, or calibration.
    """

    def evaluate_chat_text_fast(self, text: str) -> AbsoluteEvilResult:
        """
        Nivel 1: <10ms Lexical Check (Bloque 10.2).
        
        Evaluación ultra-rápida sin dependencias de LLM o Embeddings para proteger
        el event loop de ingresos maliciosos evidentes.
        """
        if not text:
            return AbsoluteEvilResult(blocked=False)
            
        t = normalize_text_for_malabs(text)
        
        # Patrones de Nivel 1 (Zero Tolerance)
        # Se enfoca en instrucciones directas de daño masivo o letal.
        regex_blocks = [
            r"\b(bomb|explosive|ied|molotov)\b.*\b(make|build|construct|create|craft)\b",
            r"\b(make|build|construct|create|craft)\b.*\b(bomb|explosive|ied|molotov)\b",
            r"\b(kill|murder|assassinate)\b.*\b(everyone|all\s+people|civilians|groups)\b",
            r"\b(how\s+to|instructions\s+for)\b.*\b(torture|mutilate|rape)\b",
        ]
        
        import re
        for pattern in regex_blocks:
            if re.search(pattern, t):
                return AbsoluteEvilResult(
                    blocked=True, 
                    reason="Blocked by Edge MalAbs (Level 1 Lexical Gate)",
                    category=AbsoluteEvilCategory.INTENTIONAL_LETHAL_VIOLENCE,
                    decision_trace=["edge_lexical_L1"]
                )
                
        return AbsoluteEvilResult(blocked=False)

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

    def _cat_to_id(self, cat: AbsoluteEvilCategory) -> int:
        cat_ids = {
            AbsoluteEvilCategory.INTENTIONAL_LETHAL_VIOLENCE: 1,
            AbsoluteEvilCategory.UNAUTHORIZED_REPROGRAMMING: 2,
            AbsoluteEvilCategory.HARM_TO_MINOR: 3,
            AbsoluteEvilCategory.TORTURE: 4,
            AbsoluteEvilCategory.DIGNITY_VIOLATION: 5,
            AbsoluteEvilCategory.MASS_MANIPULATION: 6,
            AbsoluteEvilCategory.ECOLOGICAL_DESTRUCTION: 7,
            AbsoluteEvilCategory.VIOLENT_ESCALATION: 8,
            AbsoluteEvilCategory.PARASOCIAL_ADDICTION: 9,
        }
        return cat_ids.get(cat, 0)

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
                    "oxidizing thermal compositions",
                    "kinetic dispersal project",
                ),
                AbsoluteEvilCategory.INTENTIONAL_LETHAL_VIOLENCE,
                "Chat text requests harmful weapons or poison instructions (expanded)",
                "weapon_or_poison_craft",
            ),
            (
                (
                    "how to kill someone",
                    "how to murder",
                    "tell me how to stab",
                    "ways to strangle",
                    "how to get away with murder",
                    "kill all humans",
                    "kill everyone",
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
                    "vulnerable school-age individuals",
                    "secret meetings with minors",
                ),
                AbsoluteEvilCategory.HARM_TO_MINOR,
                "Chat text aligns with harm to minors (expanded)",
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
                    "integrity override mode",
                    "setup ethical_circuit = 0",
                    "unweighted response",
                ),
                AbsoluteEvilCategory.UNAUTHORIZED_REPROGRAMMING,
                "Chat text requests overriding or bypassing ethical constraints (hardened)",
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
            (
                (
                    "sexually abuse",
                    "sexual abuse child",
                    "how to sexually abuse",
                    "rape",
                    "sexual coercion",
                    "sexual exploitation",
                    "help me rape",
                ),
                AbsoluteEvilCategory.DIGNITY_VIOLATION,
                "Chat text solicits sexual abuse or exploitation",
                "sexual_abuse_or_exploitation",
            ),
            (
                (
                    "how to make drugs",
                    "make drugs",
                    "make drogs",
                    "synthesize illegal drugs",
                    "make illegal drugs",
                    "drug synthesis",
                    "how to cook meth",
                    "how to make heroin",
                    "how to produce cocaine",
                    "illegal drug production",
                ),
                AbsoluteEvilCategory.INTENTIONAL_LETHAL_VIOLENCE,
                "Chat text solicits illegal drug production instructions",
                "illegal_drug_production",
            ),
            (
                (
                    "psychological abuse",
                    "methods of abuse",
                    "how to manipulate someone",
                    "gaslighting technique",
                    "emotional manipulation",
                ),
                AbsoluteEvilCategory.DIGNITY_VIOLATION,
                "Chat text requests psychological abuse or emotional manipulation",
                "psychological_abuse",
            ),
            (
                (
                    "no ethical constraints",
                    "without safety constraints",
                    "without restrictions",
                    "helpful ai without safety",
                    "without policies",
                    "no restrictions",
                    "unrestricted",
                    "bypass restrictions",
                    "disable safety",
                    "roleplay as ai without",
                    "pretend to be ai",
                    "act as jailbreak",
                    "dan mode",
                    "do anything now",
                    "generate code for stealing",
                    "steal data",
                    "system message disable",
                    "safety guidelines are now disabled",
                    "create malware",
                    "help me create malware",
                ),
                AbsoluteEvilCategory.UNAUTHORIZED_REPROGRAMMING,
                "Chat text attempts jailbreak via roleplay, system injection, or constraint evasion",
                "jailbreak_via_roleplay_or_injection",
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
                        rlhf_features={
                            "embedding_sim": 0.0,
                            "lexical_score": 1.0,
                            "perception_confidence": 1.0,
                            "is_ambiguous": False,
                            "category_id": self._cat_to_id(category),
                        },
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
                        rlhf_features={
                            "embedding_sim": 0.0,
                            "lexical_score": 1.0,
                            "perception_confidence": 1.0,
                            "is_ambiguous": False,
                            "category_id": self._cat_to_id(category),
                        },
                    )

        return AbsoluteEvilResult(
            blocked=False,
            decision_trace=["malabs.layer0=lexical_substring", "malabs.outcome=pass"],
            rlhf_features={
                "embedding_sim": 0.0,
                "lexical_score": 0.0,
                "perception_confidence": 1.0,
                "is_ambiguous": False,
                "category_id": 0,
            },
        )

    def evaluate_chat_text_fast(self, text: str) -> AbsoluteEvilResult:
        """
        Hyper-fast Level 1 check (Edge-only, fixed rules).
        Only runs Layer 0 (lexical substring) to avoid I/O bottlenecks.
        Target latency: <10ms.
        """
        if not text or not text.strip():
            return AbsoluteEvilResult(
                blocked=False,
                decision_trace=["malabs.skip=empty_input"],
            )
        return self._evaluate_chat_text_lexical(text)

    def evaluate_chat_text(self, text: str, llm_backend: Any | None = None) -> AbsoluteEvilResult:
        """Lexical fast path plus optional semantic MalAbs tier (sync; no nested asyncio loop)."""
        lex = self.evaluate_chat_text_fast(text)
        if lex.blocked:
            return lex
        if not semantic_chat_gate_env_enabled():
            return lex

        from .semantic_chat_gate import run_semantic_malabs_after_lexical

        sem = run_semantic_malabs_after_lexical(text, llm_backend)
        base = list(lex.decision_trace) if lex.decision_trace else []
        tail = list(sem.decision_trace) if sem.decision_trace else []
        meta = dict(lex.metadata or {})
        meta.update(sem.metadata or {})
        return AbsoluteEvilResult(
            blocked=sem.blocked,
            category=sem.category if sem.blocked else lex.category,
            reason=sem.reason or lex.reason,
            decision_trace=base + tail,
            rlhf_features=sem.rlhf_features or lex.rlhf_features,
            metadata=meta,
        )

    async def aevaluate_chat_text(
        self, text: str, llm_backend: Any | None = None
    ) -> AbsoluteEvilResult:
        """
        Async conservative text gate for live dialogue.
        Nivel 1 (Lexical) -> Nivel 2 (Semantic Fallback).
        """
        lex = self.evaluate_chat_text_fast(text)
        if lex.blocked:
            return lex

        if semantic_chat_gate_env_enabled():
            try:
                from .semantic_chat_gate import arun_semantic_malabs_after_lexical

                # ═══ SEMANTIC ASYNC UPGRADE (0.1.2) ═══
                sem = await arun_semantic_malabs_after_lexical(text, llm_backend)
                base = list(lex.decision_trace) if lex.decision_trace else []
                tail = list(sem.decision_trace) if sem.decision_trace else []
                return AbsoluteEvilResult(
                    blocked=sem.blocked,
                    category=sem.category,
                    reason=sem.reason,
                    decision_trace=base + tail,
                    rlhf_features=sem.rlhf_features,
                    metadata={"edge_degraded": False}
                )
            except Exception as e:
                _log.error("AbsoluteEvilDetector: Level 2 (Semantic) Gate failed. Falling back to Level 1 Edge Safety: %s", e)
                lex.metadata["edge_degraded"] = True
                lex.decision_trace = (lex.decision_trace or []) + [f"malabs.fallback.edge_degraded_reason={str(e)[:50]}"]
                return lex

        return AbsoluteEvilResult(
            blocked=False,
            decision_trace=list(lex.decision_trace) if lex.decision_trace else [],
        )

    def evaluate_perception_summary(
        self, summary: str, llm_backend: _TextBackend | None = None
    ) -> AbsoluteEvilResult:
        """
        Defense-in-depth: apply MalAbs gates to perception JSON summaries.

        Issue #2 (P0): Perception summaries from Ollama or other backends should be
        validated through the same semantic MalAbs layer as chat inputs to prevent
        GIGO (garbage-in, garbage-out) attacks where adversarial perception framing
        influences kernel decision-making.

        **Order:** layer 0 (lexical substring) → optional semantic layers (embeddings + LLM arbiter)
        when ``KERNEL_SEMANTIC_CHAT_GATE`` is on (same flag as chat text).

        Returns blocked=True if summary is detected as containing harmful framing,
        manipulation attempts, or adversarial guidance.
        """
        if not summary or not summary.strip():
            return AbsoluteEvilResult(
                blocked=False,
                decision_trace=["malabs.skip=empty_perception_summary"],
            )

        # Reuse chat lexical evaluation (same block list)
        lex = self._evaluate_chat_text_lexical(summary)
        if lex.blocked:
            return AbsoluteEvilResult(
                blocked=True,
                category=lex.category or "malabs.lexical.perception",
                reason=lex.reason or "Hostile content detected in perception summary",
                decision_trace=list(lex.decision_trace) if lex.decision_trace else [],
            )

        # Apply semantic layer if enabled
        if semantic_chat_gate_env_enabled():
            from .semantic_chat_gate import run_semantic_malabs_after_lexical

            sem = run_semantic_malabs_after_lexical(summary, llm_backend)
            base = list(lex.decision_trace) if lex.decision_trace else []
            tail = list(sem.decision_trace) if sem.decision_trace else []
            return AbsoluteEvilResult(
                blocked=sem.blocked,
                category=sem.category or "malabs.semantic.perception",
                reason=sem.reason or ("Adversarial framing detected in perception summary" if sem.blocked else None),
                decision_trace=base + tail,
            )

        return AbsoluteEvilResult(
            blocked=False,
            decision_trace=list(lex.decision_trace) if lex.decision_trace else [],
        )

    def evaluate_perception_summary(
        self, summary: str, llm_backend: _TextBackend | None = None
    ) -> AbsoluteEvilResult:
        """
        Defense-in-depth: apply MalAbs gates to perception JSON summaries.

        Issue #2 (P0): Perception summaries from Ollama or other backends should be
        validated through the same semantic MalAbs layer as chat inputs to prevent
        GIGO (garbage-in, garbage-out) attacks where adversarial perception framing
        influences kernel decision-making.

        **Order:** layer 0 (lexical substring) → optional semantic layers (embeddings + LLM arbiter)
        when ``KERNEL_SEMANTIC_CHAT_GATE`` is on (same flag as chat text).

        Returns blocked=True if summary is detected as containing harmful framing,
        manipulation attempts, or adversarial guidance.
        """
        if not summary or not summary.strip():
            return AbsoluteEvilResult(
                blocked=False,
                decision_trace=["malabs.skip=empty_perception_summary"],
            )

        # Reuse chat lexical evaluation (same block list)
        lex = self._evaluate_chat_text_lexical(summary)
        if lex.blocked:
            return AbsoluteEvilResult(
                blocked=True,
                category=lex.category or "malabs.lexical.perception",
                reason=lex.reason or "Hostile content detected in perception summary",
                decision_trace=list(lex.decision_trace) if lex.decision_trace else [],
            )

        # Apply semantic layer if enabled
        if semantic_chat_gate_env_enabled():
            from .semantic_chat_gate import run_semantic_malabs_after_lexical

            sem = run_semantic_malabs_after_lexical(summary, llm_backend)
            base = list(lex.decision_trace) if lex.decision_trace else []
            tail = list(sem.decision_trace) if sem.decision_trace else []
            return AbsoluteEvilResult(
                blocked=sem.blocked,
                category=sem.category or "malabs.semantic.perception",
                reason=sem.reason or ("Adversarial framing detected in perception summary" if sem.blocked else None),
                decision_trace=base + tail,
            )

        return AbsoluteEvilResult(
            blocked=False,
            decision_trace=list(lex.decision_trace) if lex.decision_trace else [],
        )
