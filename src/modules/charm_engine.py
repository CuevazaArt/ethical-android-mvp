"""
Multimodal Charm Engine — Renderizado Estilístico y Físico (Fase 8+).

Aplica la capa de encanto (Intimidad, Misterio, Juego) *después* de que
el EthicalKernel haya tomado una decisión L0/C1 válida.

Incluye la orquestación de gestos somáticos para inferencia multimodal
en tiempo real (Nomad Bridge) y filtros anti-parasociabilidad.

Bloque E.2: RLHF-informed sycophancy guard.
When ``KERNEL_RLHF_REWARD_MODEL_ENABLED=1`` and a trained reward model
is available, ``ResponseSculptor.sculpt`` queries the model with style
features to detect and dampen sycophantic charm vectors (excessive warmth /
playfulness with low assertiveness).  Hard safety constraints (absolute evil
bypass) are never altered.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

from .uchi_soto import InteractionProfile
from .user_model import UserModelTracker

logger = logging.getLogger(__name__)

# Threshold above which RLHF reward score triggers sycophancy dampening.
_RLHF_SYCO_THRESHOLD = float(os.environ.get("KERNEL_RLHF_SYCO_THRESHOLD", "0.55"))
# Maximum factor by which warmth/playfulness is reduced under RLHF dampening.
_RLHF_DAMPENING_MAX = float(os.environ.get("KERNEL_RLHF_DAMPENING_MAX", "0.4"))


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
        dirct = 0.5

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
    def __init__(self, llm_module: Any = None, rlhf_pipeline: Any = None):
        self.llm = llm_module
        self.parametrizer = StyleParametrizer()
        self.gesture_planner = GesturePlanner()
        self._rlhf = rlhf_pipeline  # RLHFPipeline | None

    # ------------------------------------------------------------------
    # RLHF sycophancy guard (Bloque E.2)
    # ------------------------------------------------------------------

    def _apply_rlhf_guard(self, charm: CharmVector, caution_level: float) -> CharmVector:
        """
        Query the reward model with style features and dampen warmth/playfulness
        when the score exceeds the sycophancy threshold.

        Feature encoding (re-uses existing RLHF extractor):
        - embedding_sim  ← warmth   (high warmth = closer to flattery anchor)
        - lexical_score  ← 1 - directiveness  (low assertiveness = sycophancy risk)
        - perception_conf ← 1 - caution_level (lower caution → higher style confidence)
        - is_ambiguous   ← warmth in (0.4, 0.65) band
        - category_id    ← 0 (style, not safety)
        """
        if self._rlhf is None:
            return charm
        try:
            from .rlhf_reward_model import is_rlhf_enabled
            if not is_rlhf_enabled():
                return charm
            if not self._rlhf.reward_model.is_trained:
                return charm
            fv = self._rlhf.reward_model.extract_features(
                embedding_sim=charm.warmth,
                lexical_score=max(0.0, 1.0 - charm.directiveness),
                perception_conf=max(0.0, 1.0 - caution_level),
                is_ambiguous=(0.4 < charm.warmth < 0.65),
                category_id=0,
            )
            reward_score, confidence = self._rlhf.reward_model.predict(fv)
            if reward_score > _RLHF_SYCO_THRESHOLD and confidence > 0.2:
                # Proportional dampening — stronger dampening as score rises
                excess = min(1.0, (reward_score - _RLHF_SYCO_THRESHOLD) / (1.0 - _RLHF_SYCO_THRESHOLD))
                factor = max(1.0 - excess * _RLHF_DAMPENING_MAX, 1.0 - _RLHF_DAMPENING_MAX)
                logger.debug(
                    "RLHF sycophancy guard: score=%.3f confidence=%.3f dampening=%.3f",
                    reward_score, confidence, factor,
                )
                return CharmVector(
                    warmth=charm.warmth * factor,
                    mystery=charm.mystery,
                    playfulness=charm.playfulness * factor,
                    directiveness=min(1.0, charm.directiveness + (1.0 - factor) * 0.2),
                )
        except Exception as exc:
            logger.warning("RLHF guard skipped due to error: %s", exc)
        return charm

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

        When RLHF is enabled and a trained reward model is available, the charm
        vector is post-processed by the sycophancy guard (Bloque E.2) before
        tone annotations and gesture planning are applied.
        """
        if absolute_evil_detected:
            # Full bypass for L0 safety
            return StylizedResponse(
                final_text=base_text,
                charm_vector={"warmth": 0.0, "mystery": 0.0, "playfulness": 0.0, "directiveness": 1.0},
                gesture_plan=[{"actuator": "posture", "action": "rigid_block", "intensity": 1.0}],
            )

        charm = self.parametrizer.parametrize(decision_action, profile, user_tracker, caution_level)

        # Bloque E.2: RLHF-informed sycophancy dampening (no-op when RLHF is off/untrained)
        charm = self._apply_rlhf_guard(charm, caution_level)

        gesture = self.gesture_planner.plan(charm)

        final_text = base_text
        if charm.warmth > 0.7 and caution_level <= 0.3:
            final_text += " [Tone: Warm & Open]"
        elif charm.directiveness > 0.8:
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
        )


class CharmEngine:
    """
    Facade for the Charm pipeline in the Executive Lobe.
    """
    def __init__(self, llm_module: Any = None, rlhf_pipeline: Any = None):
        self.sculptor = ResponseSculptor(llm_module, rlhf_pipeline)

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
