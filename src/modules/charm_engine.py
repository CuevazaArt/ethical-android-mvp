"""
Multimodal Charm Engine — style / somatic layer after a valid L0/L1 decision.

Applies affect (intimacy, mystery, play) *after* the EthicalKernel decision.
Coordinates gesture hints for Nomad / hardware and optional **basal-ganglia EMA**
smoothing on warmth/mystery (MER Block 10.3).

**Env (optional):** ``KERNEL_BASAL_GANGLIA_SMOOTHING=1`` — run :class:`basal_ganglia.BasalGanglia`
on ``CharmVector`` warmth/mystery to reduce sociopathic parametric jumps (default off).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

from src.modules.llm_layer import LLMModule

from .uchi_soto import InteractionProfile
from .user_model import UserModelTracker

logger = logging.getLogger(__name__)

_basal_ganglia_singleton: Any = None


def _basal_ganglia_smoothing_enabled() -> bool:
    v = os.environ.get("KERNEL_BASAL_GANGLIA_SMOOTHING", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def _get_basal_ganglia() -> Any:
    global _basal_ganglia_singleton
    if _basal_ganglia_singleton is None:
        from .basal_ganglia import BasalGanglia

        _basal_ganglia_singleton = BasalGanglia()
    return _basal_ganglia_singleton


def clear_charm_engine_basal_singleton_for_tests() -> None:
    """Reset process-local basal filter (tests only)."""
    global _basal_ganglia_singleton
    _basal_ganglia_singleton = None


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
    haptic_plan: list[dict[str, Any]]  # Phase 10.2


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
            plan.append(
                {"actuator": "eyebrows", "action": "quick_raise", "intensity": charm.playfulness}
            )

        return plan


class HapticPlanner:
    """Phase 10.2: Plans vibrations for the Nomad Vessel PWA."""

    def plan(self, charm: CharmVector, caution: float) -> list[dict[str, Any]]:
        plan = []
        if caution > 0.8:
            plan.append({"type": "vibrate", "pattern": [50, 100, 50], "label": "alert_caution"})
        elif charm.warmth > 0.7:
            plan.append({"type": "vibrate", "pattern": [10], "label": "gentle_pulse"})
        elif charm.playfulness > 0.6:
            plan.append({"type": "vibrate", "pattern": [30, 30], "label": "playful_double"})
        return plan


class ResponseSculptor:
    def __init__(self, llm_module: LLMModule | None = None):
        self.llm = llm_module
        self.parametrizer = StyleParametrizer()
        self.gesture_planner = GesturePlanner()
        self.haptic_planner = HapticPlanner()

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
        t0 = time.perf_counter()
        if absolute_evil_detected:
            # Full bypass for L0 safety
            return StylizedResponse(
                final_text=base_text,
                charm_vector={
                    "warmth": 0.0,
                    "mystery": 0.0,
                    "playfulness": 0.0,
                    "directiveness": 1.0,
                },
                gesture_plan=[{"actuator": "posture", "action": "rigid_block", "intensity": 1.0}],
                haptic_plan=[
                    {"type": "vibrate", "pattern": [500], "label": "absolute_evil_warning"}
                ],
            )

        charm = self.parametrizer.parametrize(decision_action, profile, user_tracker, caution_level)
        if _basal_ganglia_smoothing_enabled():
            r = _get_basal_ganglia().smooth(
                target_warmth=charm.warmth,
                target_mystery=charm.mystery,
            )
            charm = CharmVector(
                warmth=float(r["warmth"]),
                mystery=float(r["mystery"]),
                playfulness=charm.playfulness,
                directiveness=charm.directiveness,
            )
        gesture = self.gesture_planner.plan(charm)
        haptic = self.haptic_planner.plan(charm, caution_level)

        # En integración real, esto encadena un call al LLM (con override_template).
        # Para el stub arquitectónico, agregamos el metadata de intención.
        final_text = base_text
        if charm.warmth > 0.7 and caution_level <= 0.3:
            final_text += " [Tone: Warm & Open]"
        elif charm.directiveness > 0.8:
            final_text += " [Tone: Direct & Boundaried]"

        res = StylizedResponse(
            final_text=final_text,
            charm_vector={
                "warmth": round(charm.warmth, 3),
                "mystery": round(charm.mystery, 3),
                "playfulness": round(charm.playfulness, 3),
                "directiveness": round(charm.directiveness, 3),
            },
            gesture_plan=gesture,
            haptic_plan=haptic,
        )

        latency = (time.perf_counter() - t0) * 1000
        if latency > 2.0:
            logger.debug("CharmEngine: sculpt latency = %.2fms", latency)

        return res


class CharmEngine:
    """
    Facade for the Charm pipeline in the Executive Lobe.
    """

    def __init__(self, llm_module: LLMModule | None = None):
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
