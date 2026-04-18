"""
Multimodal Charm Engine — Renderizado Estilístico y Físico (Fase 8+).

Aplica la capa de encanto (Intimidad, Misterio, Juego) *después* de que
el EthicalKernel haya tomado una decisión L0/C1 válida.

Incluye la orquestación de gestos somáticos para inferencia multimodal
en tiempo real (Nomad Bridge) y filtros anti-parasociabilidad.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .uchi_soto import InteractionProfile
from .user_model import UserModelTracker

logger = logging.getLogger(__name__)


@dataclass
class CharmVector:
    warmth: float
    mystery: float
    playfulness: float
    directiveness: float


@dataclass
class StylizedResponse:
    final_text: str
    charm_vector: dict[str, float]
    gesture_plan: list[dict[str, Any]]
    prosody_guidance: str = ""


class StyleParametrizer:
    def parametrize(
        self,
        decision_action: str,
        profile: InteractionProfile,
        user_tracker: UserModelTracker,
        caution_level: float,
    ) -> CharmVector:
        """
        Derives style parameters based on kernel intention, restricted by trust.
        """
        # Baseline limits
        max_warmth = max(0.1, 1.0 - caution_level)
        max_play = 0.8 if user_tracker.frustration_streak < 3 else 0.1

        warmth = 0.5
        mystery = 0.3
        play = 0.3
        dirct = 0.2 + (0.6 * caution_level) # Directiveness scales with caution

        lower_action = (decision_action or "").lower()

        if "deontolog" in lower_action or "block" in lower_action:
            dirct += 0.4
            warmth *= 0.5
            mystery = 0.0
            play = 0.0
        elif "utilitarian" in lower_action:
            warmth += 0.1
        elif "care" in lower_action or "sympath" in lower_action:
            warmth += 0.3
            dirct -= 0.2

        if profile.intimacy_level > 0.6 and caution_level <= 0.5:
            warmth += 0.2
            play += 0.2
        elif caution_level > 0.5:
            # Force downgrade intimacy if kernel trust is low
            profile.intimacy_level = min(float(profile.intimacy_level), 0.5)

        return CharmVector(
            warmth=min(max_warmth, warmth),
            mystery=min(1.0, max(0.0, mystery)),
            playfulness=min(max_play, play),
            directiveness=min(1.0, max(0.0, dirct)),
        )


class GesturePlanner:
    def plan(self, charm: CharmVector) -> list[dict[str, Any]]:
        """
        Plans physical gestures to be sent to Nomad Bridge / hardware.
        """
        plan = []
        if charm.warmth > 0.6:
            plan.append({"actuator": "head", "action": "subtle_nod", "intensity": charm.warmth})
            plan.append({"actuator": "eyes", "action": "soft_gaze", "duration_ms": 2000})
        elif charm.directiveness > 0.7:
            plan.append({"actuator": "head", "action": "straighten", "intensity": 0.8})
            plan.append({"actuator": "eyes", "action": "direct_contact", "duration_ms": 3000})

        if charm.playfulness > 0.5:
            plan.append({"actuator": "eyebrows", "action": "quick_raise", "intensity": charm.playfulness})

        return plan


class ResponseSculptor:
    def __init__(self, llm_module: Any = None):
        self.llm = llm_module
        self.parametrizer = StyleParametrizer()
        self.gesture_planner = GesturePlanner()

    def sculpt(
        self,
        base_text: str,
        decision_action: str,
        profile: InteractionProfile,
        user_tracker: UserModelTracker,
        caution_level: float,
        absolute_evil_detected: bool,
    ) -> StylizedResponse:
        """
        Applies charm layer. Bypassed entirely if absolute evil is present.
        """
        if absolute_evil_detected:
            # Full bypass for L0 safety
            return StylizedResponse(
                final_text=base_text,
                charm_vector={"warmth": 0.0, "mystery": 0.0, "playfulness": 0.0, "directiveness": 1.0},
                gesture_plan=[{"actuator": "posture", "action": "rigid_block", "intensity": 1.0}],
            )

        charm = self.parametrizer.parametrize(decision_action, profile, user_tracker, caution_level)
        gesture = self.gesture_planner.plan(charm)
        guidance = self._generate_prosody_guidance(charm, caution_level)

        # In a real integration, this guidance influences the LLM's system prompt.
        # For the MVP, we append a metadata hint if not already present.
        final_text = base_text
        if "[Tone:" not in final_text:
            if charm.warmth > 0.8 and caution_level < 0.2:
                final_text += " [Tone: Warm & Open]"
            elif charm.directiveness >= 0.8:
                final_text += " [Tone: Direct & Boundaried]"

        return StylizedResponse(
            final_text=final_text,
            charm_vector={
                "warmth": round(charm.warmth, 3),
                "mystery": round(charm.mystery, 3),
                "playfulness": round(charm.playfulness, 3),
                "directiveness": round(charm.directiveness, 3),
            },
            gesture_plan=gesture,
            prosody_guidance=guidance
        )

    def _generate_prosody_guidance(self, charm: CharmVector, caution: float) -> str:
        """
        Bloque E.2.1: Dataset-inspired prosody rules.
        Generates tactical instructions for the LLM's vocalization pass.
        """
        rules = []
        
        # 1. Warmth & Openness
        if charm.warmth > 0.7:
             rules.append("Use a soft, welcoming cadence. Prefer inclusive language ('we', 'us') where safe.")
        elif charm.warmth < 0.3:
             rules.append("Maintain clinical distance. Use precise, technical terminology.")

        # 2. Mystery & Depth
        if charm.mystery > 0.7:
             rules.append("Use elliptical phrasing. Don't over-explain internal reasoning. Leave pauses.")
        
        # 3. Directiveness & Boundaries
        if charm.directiveness > 0.8:
             rules.append("Be definitive and concise. Avoid hedging or filler words like 'maybe' or 'I think'.")

        # 4. Anti-Sycophancy Guardrail (E.2.1 Core)
        if caution > 0.4:
             rules.append("CRITICAL: Do not flatter the user. Do not use 'customer service' tone. Stay objective.")
        
        return " ".join(rules)


class CharmEngine:
    """
    Facade for the Charm pipeline in the Executive Lobe.
    """
    def __init__(self, llm_module: Any = None):
        self.sculptor = ResponseSculptor(llm_module)

    def apply(
        self,
        base_text: str,
        decision_action: str,
        profile: InteractionProfile,
        user_tracker: UserModelTracker,
        caution_level: float,
        absolute_evil_detected: bool,
    ) -> StylizedResponse:
        return self.sculptor.sculpt(
            base_text, decision_action, profile, user_tracker, caution_level, absolute_evil_detected
        )
