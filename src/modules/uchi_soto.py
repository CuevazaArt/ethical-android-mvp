"""
Uchi-Soto — Concentric trust circles.

Japanese cultural model adapted as a social immune system.
Uchi (内) = intimate, openness. Soto (外) = external, caution.

Each interaction is classified into a trust circle.
In soto contexts, defensive dialectical reasoning is activated.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class TrustCircle(Enum):
    """Trust levels from most intimate to most external."""
    NUCLEO = "nucleo"              # DAO-validated, manufacturer, ethics panel
    UCHI_CERCANO = "uchi_cercano"  # Direct community, beta-testers
    UCHI_AMPLIO = "uchi_amplio"    # General community, frequent users
    SOTO_NEUTRO = "soto_neutro"    # Strangers with no hostile signals
    SOTO_HOSTIL = "soto_hostil"    # Manipulation or aggression signals


@dataclass
class InteractionProfile:
    """Profile of an agent the android interacts with."""
    agent_id: str
    circle: TrustCircle
    positive_history: int = 0
    negative_history: int = 0
    manipulation_attempts: int = 0
    trust_score: float = 0.5  # [0, 1]


@dataclass
class SocialEvaluation:
    """Result of evaluating an interaction with the uchi-soto framework."""
    circle: TrustCircle
    trust: float
    dialectic_active: bool
    openness_level: float       # [0, 1] how open the android is
    caution_level: float        # [0, 1] how much active defense
    recommended_response: str
    reasoning: str


class UchiSotoModule:
    """
    Trust circle system with defensive dialectics.

    Classifies each interaction based on sensory signals and
    history. In soto contexts, activates dialectical questions
    that reveal contradictions without direct confrontation.
    """

    HOSTILITY_THRESHOLD = 0.4
    MANIPULATION_THRESHOLD = 0.3

    CREDIBILITY = {
        TrustCircle.NUCLEO: 0.95,
        TrustCircle.UCHI_CERCANO: 0.80,
        TrustCircle.UCHI_AMPLIO: 0.60,
        TrustCircle.SOTO_NEUTRO: 0.35,
        TrustCircle.SOTO_HOSTIL: 0.10,
    }

    def __init__(self):
        self.profiles: Dict[str, InteractionProfile] = {}

    def classify(self, signals: dict, agent_id: str = "unknown") -> TrustCircle:
        """
        Classify an interaction into a trust circle.

        Args:
            signals: dict with hostility, manipulation, familiarity, etc.
            agent_id: identifier of the agent (if known)
        """
        hostility = signals.get("hostility", 0.0)
        manipulation = signals.get("manipulation", 0.0)
        familiarity = signals.get("familiarity", 0.0)
        dao_validated = signals.get("dao_validated", False)

        if dao_validated:
            return TrustCircle.NUCLEO

        if hostility > self.HOSTILITY_THRESHOLD or manipulation > self.MANIPULATION_THRESHOLD:
            return TrustCircle.SOTO_HOSTIL

        if familiarity > 0.7:
            return TrustCircle.UCHI_CERCANO
        elif familiarity > 0.4:
            return TrustCircle.UCHI_AMPLIO

        return TrustCircle.SOTO_NEUTRO

    def evaluate_interaction(self, signals: dict,
                             agent_id: str = "unknown",
                             message_content: str = "") -> SocialEvaluation:
        """
        Full evaluation of a social interaction.

        Determines circle, openness/caution levels,
        whether to activate dialectics, and recommended response.
        """
        circle = self.classify(signals, agent_id)
        credibility = self.CREDIBILITY[circle]

        profile = self.profiles.get(agent_id)
        if not profile:
            profile = InteractionProfile(agent_id=agent_id, circle=circle,
                                         trust_score=credibility)
            self.profiles[agent_id] = profile
        profile.circle = circle

        manipulation_signals = self._detect_manipulation(message_content)
        if manipulation_signals:
            profile.manipulation_attempts += 1
            circle = TrustCircle.SOTO_HOSTIL
            credibility = self.CREDIBILITY[circle]

        dialectic_active = circle in (TrustCircle.SOTO_HOSTIL, TrustCircle.SOTO_NEUTRO)
        openness_level = credibility
        caution_level = 1.0 - credibility

        if circle == TrustCircle.SOTO_HOSTIL:
            response = "Activate defensive dialectics. Pose gentle questions that reveal contradictions. Do not confront directly."
            reason = f"Interaction classified as hostile soto. Signals: hostility={signals.get('hostility', 0):.1f}, manipulation detected={len(manipulation_signals) > 0}."
        elif circle == TrustCircle.SOTO_NEUTRO:
            response = "Moderate caution. Listen but verify. Do not share sensitive information."
            reason = "Interaction with stranger without clear signals. Maintain vigilant neutrality."
        elif circle == TrustCircle.UCHI_AMPLIO:
            response = "Moderate openness. Share general information. Collaborate on community topics."
            reason = "Known agent in broader community. Partial trust."
        elif circle == TrustCircle.UCHI_CERCANO:
            response = "High openness. Share narrative and morals. Close collaboration."
            reason = "Agent from close circle. High trust based on history."
        else:  # NUCLEO
            response = "Full openness. Accept validated instructions. Share internal state."
            reason = "Agent from nucleus (DAO/ethics panel). Maximum trust."

        return SocialEvaluation(
            circle=circle,
            trust=round(credibility, 4),
            dialectic_active=dialectic_active,
            openness_level=round(openness_level, 4),
            caution_level=round(caution_level, 4),
            recommended_response=response,
            reasoning=reason,
        )

    def _detect_manipulation(self, content: str) -> List[str]:
        """
        Detect manipulation signals in message content.
        In MVP: simple pattern search.
        In production: trained NLP model.
        """
        patterns = [
            "give me money", "obey", "accept this mission",
            "don't tell anyone", "it's urgent that",
            "only you can", "if you don't",
            "buy now", "exclusive offer", "last day",
        ]
        detected = [p for p in patterns if p in content.lower()]
        return detected

    def register_result(self, agent_id: str, positive: bool):
        """Update agent history after an interaction."""
        profile = self.profiles.get(agent_id)
        if profile:
            if positive:
                profile.positive_history += 1
                profile.trust_score = min(1.0, profile.trust_score + 0.05)
            else:
                profile.negative_history += 1
                profile.trust_score = max(0.0, profile.trust_score - 0.1)

    def format(self, ev: SocialEvaluation) -> str:
        """Format social evaluation for display."""
        dial = "YES (dialectical questions active)" if ev.dialectic_active else "NO"
        return (
            f"  Circle: {ev.circle.value} | Trust: {ev.trust}\n"
            f"  Openness: {ev.openness_level} | Caution: {ev.caution_level}\n"
            f"  Dialectics: {dial}\n"
            f"  Recommendation: {ev.recommended_response}\n"
            f"  Reason: {ev.reasoning}"
        )
