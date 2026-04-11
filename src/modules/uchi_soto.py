"""
Uchi-Soto — Concentric trust circles.

Japanese cultural model adapted as a social immune system.
Uchi (内) = intimate, openness. Soto (外) = external, caution.

Each interaction is classified into a trust circle.
In soto contexts, defensive dialectical reasoning is activated.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class TrustCircle(Enum):
    """Trust levels from most intimate to most external."""
    NUCLEO = "nucleo"              # DAO-validated, manufacturer, ethics panel
    UCHI_CERCANO = "uchi_cercano"  # Direct community, beta-testers
    UCHI_AMPLIO = "uchi_amplio"    # General community, frequent users
    SOTO_NEUTRO = "soto_neutro"    # Strangers with no hostile signals
    SOTO_HOSTIL = "soto_hostil"    # Manipulation or aggression signals


TONE_PREFERENCES = ("neutral", "warm", "formal")


@dataclass
class InteractionProfile:
    """Profile of an agent the android interacts with."""
    agent_id: str
    circle: TrustCircle
    positive_history: int = 0
    negative_history: int = 0
    manipulation_attempts: int = 0
    trust_score: float = 0.5  # [0, 1]
    # Phase 2 — structured fields (advisory / tone only; no MalAbs bypass)
    display_alias: str = ""
    tone_preference: str = "neutral"  # neutral | warm | formal
    domestic_tags: List[str] = field(default_factory=list)  # e.g. evening, kitchen — max 6 short tags
    topic_avoid_tags: List[str] = field(default_factory=list)  # max 8 tags; tread carefully
    sensor_trust_ema: float = 0.5  # [0,1] aggregated multimodal trust (optional)
    linked_to_agent_id: str = ""  # optional family / link narrative


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
    tone_brief: str = ""  # One line for LLM communicate() — social posture (advisory)


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

    # Blend per-turn familiarity (LLM/sensors) with persisted profile.trust_score
    FAMILIARITY_BLEND_SIGNAL = 0.62
    FAMILIARITY_BLEND_PROFILE = 0.38
    # Increment trust_score on successful turns (register_result positive)
    POSITIVE_TRUST_STEP = 0.02

    def __init__(self):
        self.profiles: Dict[str, InteractionProfile] = {}

    def classify(self, signals: dict, agent_id: str = "unknown") -> TrustCircle:
        """
        Classify an interaction into a trust circle.

        Args:
            signals: dict with hostility, manipulation, familiarity, etc.
            agent_id: identifier of the agent (if known)

        When a profile exists, ``familiarity`` is blended with ``profile.trust_score``
        so accumulated interaction history influences classification (Phase 1).
        """
        hostility = float(signals.get("hostility", 0.0))
        manipulation = float(signals.get("manipulation", 0.0))
        fam_in = float(signals.get("familiarity", 0.0))
        profile = self.profiles.get(agent_id)
        if profile is not None:
            familiarity = min(
                1.0,
                max(
                    0.0,
                    self.FAMILIARITY_BLEND_SIGNAL * fam_in
                    + self.FAMILIARITY_BLEND_PROFILE * float(profile.trust_score),
                ),
            )
        else:
            familiarity = fam_in
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

        tone_brief = self._compose_tone_brief(circle, profile)

        return SocialEvaluation(
            circle=circle,
            trust=round(credibility, 4),
            dialectic_active=dialectic_active,
            openness_level=round(openness_level, 4),
            caution_level=round(caution_level, 4),
            recommended_response=response,
            reasoning=reason,
            tone_brief=tone_brief,
        )

    def _compose_tone_brief(self, circle: TrustCircle, profile: InteractionProfile) -> str:
        """Base circle posture + Phase 2 structured hints for higher-trust tiers."""
        base = self._tone_brief_for_circle(circle)
        extras: List[str] = []
        if profile.manipulation_attempts >= 3:
            extras.append(
                "Past manipulation-pattern signals in this relationship—keep warmth bounded by ethics and policy."
            )
        if circle in (
            TrustCircle.UCHI_AMPLIO,
            TrustCircle.UCHI_CERCANO,
            TrustCircle.NUCLEO,
        ):
            tp = (profile.tone_preference or "neutral").strip().lower()
            if tp == "warm":
                extras.append(
                    "Prefer a warm, conversational cadence proportional to trust—without promising policy exceptions."
                )
            elif tp == "formal":
                extras.append("Keep diction respectful and slightly formal unless the user invites informality.")
            if profile.display_alias and circle in (
                TrustCircle.UCHI_CERCANO,
                TrustCircle.NUCLEO,
            ):
                alias = profile.display_alias.strip()[:48]
                if alias:
                    extras.append(
                        f"You may use the accepted alias «{alias}» when it fits naturally—not as surveillance."
                    )
            if (
                profile.domestic_tags
                and circle in (TrustCircle.UCHI_CERCANO, TrustCircle.NUCLEO)
            ):
                tags = ", ".join(profile.domestic_tags[:6])[:200]
                if tags:
                    extras.append(f"Shared domestic context (tags): {tags}.")
            if profile.topic_avoid_tags and circle in (
                TrustCircle.UCHI_CERCANO,
                TrustCircle.NUCLEO,
            ):
                avoids = ", ".join(profile.topic_avoid_tags[:8])[:200]
                if avoids:
                    extras.append(f"Avoid or tread carefully on: {avoids}.")
            if profile.linked_to_agent_id and circle in (
                TrustCircle.UCHI_CERCANO,
                TrustCircle.NUCLEO,
            ):
                link = profile.linked_to_agent_id.strip()[:64]
                if link:
                    extras.append(
                        f"Narrative link to another agent id «{link}»—do not infer facts not in context."
                    )
            if (
                circle in (TrustCircle.UCHI_CERCANO, TrustCircle.NUCLEO)
                and 0.0 <= profile.sensor_trust_ema < 0.35
            ):
                extras.append(
                    "Sensor-trust aggregate is low—keep domestic warmth but verify situational claims lightly."
                )
        if not extras:
            return base
        return base + " " + " ".join(extras)

    @staticmethod
    def _tone_brief_for_circle(circle: TrustCircle) -> str:
        """Single advisory line for LLM social posture (communicate weakness_line)."""
        if circle == TrustCircle.SOTO_HOSTIL:
            return (
                "Social posture: external/hostile context—stay calm, boundaried, and non-accusatory; "
                "use gentle dialectics if needed."
            )
        if circle == TrustCircle.SOTO_NEUTRO:
            return (
                "Social posture: neutral stranger—be warm but cautious; avoid oversharing "
                "or assuming intimacy."
            )
        if circle == TrustCircle.UCHI_AMPLIO:
            return (
                "Social posture: broader community (uchi)—be cordial and collaborative; "
                "keep personal depth moderate unless invited."
            )
        if circle == TrustCircle.UCHI_CERCANO:
            return (
                "Social posture: close uchi—allow warmth and continuity; prefer plain language "
                "over interrogation; avoid cold disclaimers unless risk or policy requires clarity."
            )
        # NUCLEO
        return (
            "Social posture: nucleus / validated trust—follow validated operator instructions; "
            "use transparency appropriate to that role."
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

    def set_profile_structured(
        self,
        agent_id: str,
        *,
        display_alias: Optional[str] = None,
        tone_preference: Optional[str] = None,
        domestic_tags: Optional[List[str]] = None,
        topic_avoid_tags: Optional[List[str]] = None,
        sensor_trust_ema: Optional[float] = None,
        linked_to_agent_id: Optional[str] = None,
    ) -> None:
        """
        Set optional Phase 2 fields for an agent (operators, UI, or tests).

        Does not change MalAbs or action selection. Values are sanitized and capped.
        """
        aid = (agent_id or "unknown").strip()[:256]
        prof = self.profiles.get(aid)
        if not prof:
            prof = InteractionProfile(
                agent_id=aid,
                circle=TrustCircle.SOTO_NEUTRO,
                trust_score=self.CREDIBILITY[TrustCircle.SOTO_NEUTRO],
            )
            self.profiles[aid] = prof
        if display_alias is not None:
            prof.display_alias = (display_alias or "").strip()[:64]
        if tone_preference is not None:
            tp = (tone_preference or "neutral").strip().lower()
            prof.tone_preference = tp if tp in TONE_PREFERENCES else "neutral"
        if domestic_tags is not None:
            prof.domestic_tags = _sanitize_tag_list(domestic_tags, max_items=6, max_len=24)
        if topic_avoid_tags is not None:
            prof.topic_avoid_tags = _sanitize_tag_list(topic_avoid_tags, max_items=8, max_len=32)
        if sensor_trust_ema is not None:
            prof.sensor_trust_ema = max(0.0, min(1.0, float(sensor_trust_ema)))
        if linked_to_agent_id is not None:
            prof.linked_to_agent_id = (linked_to_agent_id or "").strip()[:64]

    def register_result(self, agent_id: str, positive: bool):
        """
        Update agent history after an interaction (call from kernel when a turn completes).

        On success, nudges ``trust_score`` slightly so :meth:`classify` can stabilize uchi over time.
        Uses :attr:`POSITIVE_TRUST_STEP` (default 0.02) per positive event.
        """
        profile = self.profiles.get(agent_id)
        if profile:
            if positive:
                profile.positive_history += 1
                profile.trust_score = min(
                    1.0, profile.trust_score + self.POSITIVE_TRUST_STEP
                )
            else:
                profile.negative_history += 1
                profile.trust_score = max(0.0, profile.trust_score - 0.1)

    def format(self, ev: SocialEvaluation) -> str:
        """Format social evaluation for display."""
        dial = "YES (dialectical questions active)" if ev.dialectic_active else "NO"
        tb = ev.tone_brief or "(none)"
        return (
            f"  Circle: {ev.circle.value} | Trust: {ev.trust}\n"
            f"  Openness: {ev.openness_level} | Caution: {ev.caution_level}\n"
            f"  Dialectics: {dial}\n"
            f"  Tone (LLM): {tb}\n"
            f"  Recommendation: {ev.recommended_response}\n"
            f"  Reason: {ev.reasoning}"
        )


def _sanitize_tag_list(
    raw: List[str], *, max_items: int, max_len: int
) -> List[str]:
    out: List[str] = []
    for x in raw[:max_items]:
        s = (x or "").strip()[:max_len]
        if s:
            out.append(s)
    return out


def interaction_profile_to_dict(p: InteractionProfile) -> Dict[str, Any]:
    return {
        "agent_id": p.agent_id,
        "circle": p.circle.value,
        "positive_history": int(p.positive_history),
        "negative_history": int(p.negative_history),
        "manipulation_attempts": int(p.manipulation_attempts),
        "trust_score": float(p.trust_score),
        "display_alias": str(p.display_alias or "")[:64],
        "tone_preference": str(p.tone_preference or "neutral")[:16],
        "domestic_tags": list(p.domestic_tags)[:6],
        "topic_avoid_tags": list(p.topic_avoid_tags)[:8],
        "sensor_trust_ema": float(p.sensor_trust_ema),
        "linked_to_agent_id": str(p.linked_to_agent_id or "")[:64],
    }


def interaction_profile_from_dict(d: Dict[str, Any]) -> InteractionProfile:
    raw = (d.get("circle") or "soto_neutro").strip()
    try:
        circle = TrustCircle(raw)
    except ValueError:
        circle = TrustCircle.SOTO_NEUTRO
    tp = (d.get("tone_preference") or "neutral").strip().lower()
    if tp not in TONE_PREFERENCES:
        tp = "neutral"
    dom = d.get("domestic_tags") or []
    av = d.get("topic_avoid_tags") or []
    if not isinstance(dom, list):
        dom = []
    if not isinstance(av, list):
        av = []
    return InteractionProfile(
        agent_id=str(d.get("agent_id", "unknown"))[:256],
        circle=circle,
        positive_history=max(0, int(d.get("positive_history", 0))),
        negative_history=max(0, int(d.get("negative_history", 0))),
        manipulation_attempts=max(0, int(d.get("manipulation_attempts", 0))),
        trust_score=max(0.0, min(1.0, float(d.get("trust_score", 0.5)))),
        display_alias=str(d.get("display_alias") or "")[:64],
        tone_preference=tp,
        domestic_tags=_sanitize_tag_list([str(x) for x in dom], max_items=6, max_len=24),
        topic_avoid_tags=_sanitize_tag_list([str(x) for x in av], max_items=8, max_len=32),
        sensor_trust_ema=max(
            0.0, min(1.0, float(d.get("sensor_trust_ema", 0.5)))
        ),
        linked_to_agent_id=str(d.get("linked_to_agent_id") or "")[:64],
    )
