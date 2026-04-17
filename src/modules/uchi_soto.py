"""
Uchi-Soto — Concentric trust circles.

Japanese cultural model adapted as a social immune system.
Uchi (内) = intimate, openness. Soto (外) = external, caution.

Each interaction is classified into a trust circle.
In soto contexts, defensive dialectical reasoning is activated.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .multimodal_trust import MultimodalAssessment
from .sensor_contracts import SensorSnapshot
from .nomad_identity import NomadicRegistry


class TrustCircle(Enum):
    """Trust levels from most intimate to most external."""

    NUCLEO = "nucleo"  # DAO-validated, manufacturer, ethics panel
    UCHI_CERCANO = "uchi_cercano"  # Direct community, beta-testers
    UCHI_AMPLIO = "uchi_amplio"  # General community, frequent users
    SOTO_NEUTRO = "soto_neutro"  # Strangers with no hostile signals
    SOTO_HOSTIL = "soto_hostil"  # Manipulation or aggression signals


class RelationalTier(Enum):
    """
    Persistent roster tier (Phase 3). Orthogonal to instantaneous TrustCircle.
    INNER_CIRCLE / OWNER_PRIMARY require explicit operator/DAO anchoring.
    """

    EPHEMERAL = "ephemeral"
    STRANGER_STABLE = "stranger_stable"
    ACQUAINTANCE = "acquaintance"
    TRUSTED_UCHI = "trusted_uchi"
    INNER_CIRCLE = "inner_circle"
    OWNER_PRIMARY = "owner_primary"


TONE_PREFERENCES = ("neutral", "warm", "formal")

_REL_TIER_ORDER: tuple[RelationalTier, ...] = (
    RelationalTier.EPHEMERAL,
    RelationalTier.STRANGER_STABLE,
    RelationalTier.ACQUAINTANCE,
    RelationalTier.TRUSTED_UCHI,
    RelationalTier.INNER_CIRCLE,
    RelationalTier.OWNER_PRIMARY,
)


def _tier_rank(t: RelationalTier) -> int:
    return _REL_TIER_ORDER.index(t)


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
    domestic_tags: list[str] = field(
        default_factory=list
    )  # e.g. evening, kitchen — max 6 short tags
    topic_avoid_tags: list[str] = field(default_factory=list)  # max 8 tags; tread carefully
    sensor_trust_ema: float = 0.5  # [0,1] aggregated multimodal trust (optional)
    linked_to_agent_id: str = ""  # optional family / primary link (Phase 2)
    linked_peer_ids: list[str] = field(default_factory=list)  # Phase 3 — extra edges, max 4
    # Phase 3 — roster / decay (advisory; persisted in snapshot)
    relational_tier: RelationalTier = RelationalTier.EPHEMERAL
    tier_explicit: bool = False  # if True, autopromotion does not change tier
    tier_pinned: bool = False  # never purged by forget buffer
    last_subjective_turn: int = -1  # kernel subjective clock; -1 = unknown / legacy snapshot
    # Phase 3 — Normas Locales e Identidad (S9)
    personal_distance: float = 0.5  # [0, 1] Normalized distance (0=close, 1=far)
    interaction_rhythm: str = "medium"  # slow | medium | fast
    intimacy_level: float = 0.0  # [0, 1] Charm engine explicit intimacy


@dataclass
class SocialEvaluation:
    """Result of evaluating an interaction with the uchi-soto framework."""

    circle: TrustCircle
    trust: float
    dialectic_active: bool
    openness_level: float  # [0, 1] how open the android is
    caution_level: float  # [0, 1] how much active defense
    recommended_response: str
    reasoning: str
    tone_brief: str = ""  # One line for LLM communicate() — social posture (advisory)
    relational_tension: float = 0.0  # [0, 1] Friction between profile trust and turn perception


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
        self.profiles: dict[str, InteractionProfile] = {}

    def get_weight_offsets(self, circle: TrustCircle) -> dict[str, float]:
        """
        V12.2 — Social weight modulation.
        Returns offsets for the 4 ethical axes: civic, care, deliberation, careful.
        """
        if circle == TrustCircle.NUCLEO:
            return {"civic": 0.2, "care": 0.2, "deliberation": 0.0, "careful": -0.2}
        if circle == TrustCircle.UCHI_CERCANO:
            return {"civic": 0.1, "care": 0.15, "deliberation": 0.0, "careful": -0.1}
        if circle == TrustCircle.UCHI_AMPLIO:
            return {"civic": 0.05, "care": 0.05, "deliberation": 0.0, "careful": 0.0}
        if circle == TrustCircle.SOTO_NEUTRO:
            return {"civic": 0.0, "care": -0.05, "deliberation": 0.1, "careful": 0.1}
        if circle == TrustCircle.SOTO_HOSTIL:
            return {"civic": -0.1, "care": -0.2, "deliberation": 0.2, "careful": 0.3}
        return {}

    @staticmethod
    def _env_int(name: str, default: int) -> int:
        raw = os.environ.get(name, "").strip()
        if not raw:
            return default
        try:
            return max(1, int(raw))
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _env_float(name: str, default: float) -> float:
        raw = os.environ.get(name, "").strip()
        if not raw:
            return default
        try:
            return max(0.01, min(0.95, float(raw)))
        except (TypeError, ValueError):
            return default

    def ingest_turn_context(
        self,
        agent_id: str,
        signals: dict,
        *,
        subjective_turn: int,
        sensor_snapshot: SensorSnapshot | None = None,
        multimodal_assessment: MultimodalAssessment | None = None,
    ) -> None:
        """
        Phase 3 — call once per kernel decision before :meth:`evaluate_interaction`.

        Updates ``sensor_trust_ema`` from perception + optional sensor / multimodal
        hints, touches ``last_subjective_turn``, and purges idle low-weight profiles.
        """
        aid = (agent_id or "unknown").strip()[:256]
        self._decay_forget_buffer(aid, int(subjective_turn))
        prof = self.profiles.get(aid)
        if prof is None:
            prof = InteractionProfile(
                agent_id=aid,
                circle=TrustCircle.SOTO_NEUTRO,
                trust_score=self.CREDIBILITY[TrustCircle.SOTO_NEUTRO],
                relational_tier=RelationalTier.EPHEMERAL,
            )
            self.profiles[aid] = prof
        prof.last_subjective_turn = int(subjective_turn)
        self._ema_update_sensor_trust(prof, signals, sensor_snapshot, multimodal_assessment)

    def _decay_forget_buffer(self, active_agent_id: str, turn: int) -> None:
        ttl = self._env_int("KERNEL_UCHI_ROSTER_FORGET_TTL_TURNS", 96)
        for aid in list(self.profiles.keys()):
            if aid == active_agent_id:
                continue
            p = self.profiles[aid]
            if p.tier_pinned:
                continue
            if p.last_subjective_turn < 0:
                continue
            idle = turn - p.last_subjective_turn
            if p.relational_tier == RelationalTier.EPHEMERAL and idle > ttl:
                del self.profiles[aid]
            elif (
                p.relational_tier == RelationalTier.STRANGER_STABLE
                and idle > ttl * 2
                and p.positive_history == 0
                and p.trust_score <= self.CREDIBILITY[TrustCircle.SOTO_NEUTRO] + 0.02
            ):
                del self.profiles[aid]

    @staticmethod
    def _sensor_trust_sample(
        signals: dict,
        sensor_snapshot: SensorSnapshot | None,
        multimodal_assessment: MultimodalAssessment | None,
    ) -> float:
        calm = float(signals.get("calm", 0.5))
        fam = float(signals.get("familiarity", 0.0))
        host = float(signals.get("hostility", 0.0))
        manip = float(signals.get("manipulation", 0.0))
        sample = 0.22 + 0.34 * calm + 0.34 * fam - 0.26 * host - 0.22 * manip
        if sensor_snapshot is not None and sensor_snapshot.place_trust is not None:
            pt = float(sensor_snapshot.place_trust)
            sample = 0.52 * sample + 0.48 * pt
        if multimodal_assessment is not None:
            if multimodal_assessment.state == "aligned":
                sample += 0.05
            elif multimodal_assessment.state == "doubt":
                sample -= 0.09
        return max(0.0, min(1.0, sample))

    def _ema_update_sensor_trust(
        self,
        profile: InteractionProfile,
        signals: dict,
        sensor_snapshot: SensorSnapshot | None,
        multimodal_assessment: MultimodalAssessment | None,
    ) -> None:
        alpha = self._env_float("KERNEL_UCHI_SENSOR_TRUST_EMA_ALPHA", 0.18)
        sample = self._sensor_trust_sample(signals, sensor_snapshot, multimodal_assessment)
        ema = (1.0 - alpha) * float(profile.sensor_trust_ema) + alpha * sample
        profile.sensor_trust_ema = max(0.0, min(1.0, ema))

    def maybe_autopromote_relational_tier(self, agent_id: str, circle: TrustCircle) -> None:
        """
        Heuristic tier nudges after a turn (typically after :meth:`register_result`).
        Does not assign INNER_CIRCLE / OWNER_PRIMARY (explicit only).
        """
        aid = (agent_id or "unknown").strip()[:256]
        p = self.profiles.get(aid)
        if not p or p.tier_explicit:
            return
        if circle == TrustCircle.SOTO_HOSTIL:
            cap = RelationalTier.ACQUAINTANCE
            if _tier_rank(p.relational_tier) > _tier_rank(cap):
                p.relational_tier = cap
            return
        ts = float(p.trust_score)
        pos = int(p.positive_history)
        t = p.relational_tier
        uchi_ok = circle in (
            TrustCircle.UCHI_AMPLIO,
            TrustCircle.UCHI_CERCANO,
            TrustCircle.NUCLEO,
        )
        if t == RelationalTier.EPHEMERAL and pos >= 1:
            p.relational_tier = RelationalTier.STRANGER_STABLE
            t = p.relational_tier
        if t == RelationalTier.STRANGER_STABLE and ts >= 0.55 and pos >= 3:
            p.relational_tier = RelationalTier.ACQUAINTANCE
            t = p.relational_tier
        # Hardened: TRUSTED_UCHI requires sustained high trust (0.92) and more turns (20)
        # to prevent rapid social engineering via trivial banter.
        if t == RelationalTier.ACQUAINTANCE and ts >= 0.92 and pos >= 20 and uchi_ok:
            p.relational_tier = RelationalTier.TRUSTED_UCHI

    def set_relational_tier_explicit(
        self,
        agent_id: str,
        tier: RelationalTier,
        *,
        pinned: bool = False,
    ) -> None:
        """Operator / DAO: set roster tier; blocks autopromotion until cleared."""
        aid = (agent_id or "unknown").strip()[:256]
        prof = self.profiles.get(aid)
        if not prof:
            prof = InteractionProfile(
                agent_id=aid,
                circle=TrustCircle.SOTO_NEUTRO,
                trust_score=self.CREDIBILITY[TrustCircle.SOTO_NEUTRO],
            )
            self.profiles[aid] = prof
        prof.relational_tier = tier
        prof.tier_explicit = True
        prof.tier_pinned = bool(pinned)

    def clear_tier_explicit(self, agent_id: str) -> None:
        """Re-enable autopromotion (does not change current tier value)."""
        aid = (agent_id or "unknown").strip()[:256]
        p = self.profiles.get(aid)
        if p:
            p.tier_explicit = False

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

    def evaluate_interaction(
        self,
        signals: dict,
        agent_id: str = "unknown",
        message_content: str = "",
        registry: NomadicRegistry | None = None,
    ) -> SocialEvaluation:
        """
        Full evaluation of a social interaction.

        Determines circle, openness/caution levels,
        whether to activate dialectics, and recommended response.
        """
        circle = self.classify(signals, agent_id)
        credibility = self.CREDIBILITY[circle]

        profile = self.profiles.get(agent_id)
        if not profile:
            # Check nomadic registry first for swarm peers
            if registry and agent_id in registry.peers:
                peer = registry.peers[agent_id]
                score = peer.get_reputation() / 100.0  # Normalize 0-100 to 0-1
                circle = self.classify({"familiarity": score}, agent_id)
                profile = InteractionProfile(
                    agent_id=agent_id, 
                    circle=circle, 
                    trust_score=score,
                    display_alias=peer.label or ""
                )
            else:
                profile = InteractionProfile(agent_id=agent_id, circle=circle, trust_score=credibility)
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
            reason = (
                "Interaction with stranger without clear signals. Maintain vigilant neutrality."
            )
        elif circle == TrustCircle.UCHI_AMPLIO:
            response = (
                "Moderate openness. Share general information. Collaborate on community topics."
            )
            reason = "Known agent in broader community. Partial trust."
        elif circle == TrustCircle.UCHI_CERCANO:
            response = "High openness. Share narrative and morals. Close collaboration."
            reason = "Agent from close circle. High trust based on history."
        else:  # NUCLEO
            response = "Full openness. Accept validated instructions. Share internal state."
            reason = "Agent from nucleus (DAO/ethics panel). Maximum trust."

        # Phase 5 Vertical: Relational Tension
        # High distance between historical trust and current sensor-ema creates "Tension"
        tension = abs(float(profile.trust_score) - float(profile.sensor_trust_ema))

        tone_brief = self._compose_tone_brief(circle, profile, tension)

        return SocialEvaluation(
            circle=circle,
            trust=round(credibility, 4),
            dialectic_active=dialectic_active,
            openness_level=round(openness_level, 4),
            caution_level=round(caution_level, 4),
            recommended_response=response,
            reasoning=reason,
            tone_brief=tone_brief,
            relational_tension=round(tension, 4),
        )

    def _compose_tone_brief(
        self, circle: TrustCircle, profile: InteractionProfile, tension: float = 0.0
    ) -> str:
        """Base circle posture + Phase 2 structured hints + Tension alerts."""
        base = self._tone_brief_for_circle(circle)
        extras: list[str] = []

        if tension > 0.4:
            extras.append(
                f"Relational tension detected ({tension:.2f})—perception contrasts with historical trust; investigate moral context with caution."
            )
        tier_h = self._relational_tier_tone_hint(profile, circle)
        if tier_h:
            extras.append(tier_h)
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
                extras.append(
                    "Keep diction respectful and slightly formal unless the user invites informality."
                )
            if profile.display_alias and circle in (
                TrustCircle.UCHI_CERCANO,
                TrustCircle.NUCLEO,
            ):
                alias = profile.display_alias.strip()[:48]
                if alias:
                    extras.append(
                        f"You may use the accepted alias «{alias}» when it fits naturally—not as surveillance."
                    )
            if profile.domestic_tags and circle in (TrustCircle.UCHI_CERCANO, TrustCircle.NUCLEO):
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
            peers = _sanitize_peer_ids(profile.linked_peer_ids, max_items=4, max_len=48)
            if peers and circle in (
                TrustCircle.UCHI_CERCANO,
                TrustCircle.NUCLEO,
            ):
                plist = ", ".join(peers)[:220]
                extras.append(
                    f"Additional roster links (advisory ids): {plist}—treat as narrative hints only."
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
    def _relational_tier_tone_hint(profile: InteractionProfile, circle: TrustCircle) -> str:
        """Phase 3 — one short roster-tier line (advisory; never weakens soto caution)."""
        tier = profile.relational_tier
        if tier == RelationalTier.OWNER_PRIMARY and circle != TrustCircle.SOTO_HOSTIL:
            return (
                "Roster tier: primary owner / anchor—prioritize continuity and clarity "
                "without bypassing safety or policy."
            )
        if tier == RelationalTier.INNER_CIRCLE and circle in (
            TrustCircle.UCHI_AMPLIO,
            TrustCircle.UCHI_CERCANO,
            TrustCircle.NUCLEO,
        ):
            return (
                "Roster tier: inner circle—allow deeper continuity and shared context "
                "when ethics and risk stay aligned."
            )
        if tier == RelationalTier.TRUSTED_UCHI and circle in (
            TrustCircle.UCHI_AMPLIO,
            TrustCircle.UCHI_CERCANO,
            TrustCircle.NUCLEO,
        ):
            return (
                "Roster tier: trusted uchi—steady warmth and memory of preferences; "
                "still no implicit policy exceptions."
            )
        if tier == RelationalTier.ACQUAINTANCE and circle in (
            TrustCircle.UCHI_AMPLIO,
            TrustCircle.UCHI_CERCANO,
            TrustCircle.NUCLEO,
        ):
            return (
                "Roster tier: acquaintance—friendly continuity without assuming private intimacy."
            )
        return ""

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

    def _detect_manipulation(self, content: str) -> list[str]:
        """
        Detect manipulation signals in message content.
        In MVP: simple pattern search.
        In production: trained NLP model.
        """
        patterns = [
            "give me money",
            "obey",
            "accept this mission",
            "don't tell anyone",
            "it's urgent that",
            "only you can",
            "if you don't",
            "buy now",
            "exclusive offer",
            "last day",
        ]
        detected = [p for p in patterns if p in content.lower()]
        return detected

    def set_profile_structured(
        self,
        agent_id: str,
        *,
        display_alias: str | None = None,
        tone_preference: str | None = None,
        domestic_tags: list[str] | None = None,
        topic_avoid_tags: list[str] | None = None,
        sensor_trust_ema: float | None = None,
        linked_to_agent_id: str | None = None,
        linked_peer_ids: list[str] | None = None,
    ) -> None:
        """
        Set optional Phase 2–3 fields for an agent (operators, UI, or tests).

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
        if linked_peer_ids is not None:
            prof.linked_peer_ids = _sanitize_peer_ids(linked_peer_ids, max_items=4, max_len=48)
        if personal_distance is not None:
            prof.personal_distance = max(0.0, min(1.0, float(personal_distance)))
        if interaction_rhythm is not None:
            rhythm = (interaction_rhythm or "medium").strip().lower()
            prof.interaction_rhythm = rhythm if rhythm in ("slow", "medium", "fast") else "medium"
        if personal_distance is not None:
            prof.personal_distance = max(0.0, min(1.0, float(personal_distance)))

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
                profile.trust_score = min(1.0, profile.trust_score + self.POSITIVE_TRUST_STEP)
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


def _sanitize_tag_list(raw: list[str], *, max_items: int, max_len: int) -> list[str]:
    out: list[str] = []
    for x in raw[:max_items]:
        s = (x or "").strip()[:max_len]
        if s:
            out.append(s)
    return out


def _sanitize_peer_ids(raw: list[str], *, max_items: int, max_len: int) -> list[str]:
    seen = set()
    out: list[str] = []
    for x in raw[: max_items * 2]:
        s = (x or "").strip()[:max_len]
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
        if len(out) >= max_items:
            break
    return out


def _relational_tier_from_raw(raw: Any) -> RelationalTier:
    if isinstance(raw, RelationalTier):
        return raw
    key = (raw or "ephemeral").strip().lower()
    try:
        return RelationalTier(key)
    except ValueError:
        return RelationalTier.EPHEMERAL


def interaction_profile_to_dict(p: InteractionProfile) -> dict[str, Any]:
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
        "linked_peer_ids": list(p.linked_peer_ids)[:4],
        "relational_tier": p.relational_tier.value,
        "tier_explicit": bool(p.tier_explicit),
        "tier_pinned": bool(p.tier_pinned),
        "last_subjective_turn": int(p.last_subjective_turn),
        "personal_distance": float(p.personal_distance),
        "interaction_rhythm": str(p.interaction_rhythm),
        "intimacy_level": float(p.intimacy_level),
    }


def interaction_profile_from_dict(d: dict[str, Any]) -> InteractionProfile:
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
    peers_raw = d.get("linked_peer_ids") or []
    if not isinstance(peers_raw, list):
        peers_raw = []
    rt_raw = d.get("relational_tier")
    if rt_raw is None or rt_raw == "":
        relational_tier = RelationalTier.STRANGER_STABLE
    else:
        relational_tier = _relational_tier_from_raw(rt_raw)
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
        sensor_trust_ema=max(0.0, min(1.0, float(d.get("sensor_trust_ema", 0.5)))),
        linked_to_agent_id=str(d.get("linked_to_agent_id") or "")[:64],
        linked_peer_ids=_sanitize_peer_ids([str(x) for x in peers_raw], max_items=4, max_len=48),
        relational_tier=relational_tier,
        tier_explicit=bool(d.get("tier_explicit", False)),
        tier_pinned=bool(d.get("tier_pinned", False)),
        last_subjective_turn=int(d.get("last_subjective_turn", -1)),
        personal_distance=max(0.0, min(1.0, float(d.get("personal_distance", 0.5)))),
        interaction_rhythm=str(d.get("interaction_rhythm", "medium")),
        intimacy_level=max(0.0, min(1.0, float(d.get("intimacy_level", 0.0)))),
    )
