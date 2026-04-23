"""
EXPERIMENTAL / MOCK — Pilot validation (Block B6, operator lab only).

Exercises :meth:`EthicalKernel.process_natural` with synthetic vision+audio inferences and a
:mod:`llm_layer` subclass that does **not** call remote LLMs. This is not a contract test; CI does
not depend on this file.

Verifies that the kernel fuses multimodal signal mappers and produces a decision + verbal path.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.kernel import EthicalKernel
from src.modules.audio_adapter import AudioInference
from src.modules.vision_adapter import VisionInference
from src.modules.llm_layer import LLMModule, LLMPerception, VerbalResponse, RichNarrative


class MockLLM(LLMModule):
    """
    Remote-free stub for local pilot runs. ``process_natural`` uses :meth:`acommunicate` and
    :meth:`anarrate` (async); the base class routes ``mode=local`` to :meth:`_communicate_local`,
    which would **ignore** a naive :meth:`communicate` override — we override the async entrypoints
    we need so printed output matches the mock intent.
    """

    def communicate(
        self,
        action: str,
        mode: str,
        state: str,
        sigma: float,
        circle: str,
        verdict: str,
        score: float,
        scenario: str = "",
        conversation_context: str = "",
        affect_pad: tuple[float, float, float] | None = None,
        dominant_archetype: str = "",
        weakness_line: str = "",
        reflection_context: str = "",
        salience_context: str = "",
        identity_context: str = "",
        guardian_mode_context: str = "",
    ) -> VerbalResponse:
        return self._mock_verbal()

    def perceive(self, text: str, **kwargs) -> LLMPerception:  # type: ignore[override]
        return LLMPerception(
            summary=text,
            suggested_context="emergency",
            risk=0.5,
            urgency=0.5,
            hostility=0.0,
            calm=0.5,
            vulnerability=0.5,
            legality=1.0,
            manipulation=0.0,
            familiarity=0.0,
            social_tension=0.0,
        )

    def _mock_verbal(self) -> VerbalResponse:
        return VerbalResponse(
            message="[MOCK/EXPERIMENTAL] Pilot harness: deterministic response (no remote LLM).",
            tone="firm",
            hax_mode="Blue light steady.",
            inner_voice="Situational Hazard + Distress validated (mock).",
        )

    async def acommunicate(
        self,
        action: str,
        mode: str,
        state: str,
        sigma: float,
        circle: str,
        verdict: str,
        score: float,
        scenario: str = "",
        conversation_context: str = "",
        affect_pad: tuple[float, float, float] | None = None,
        dominant_archetype: str = "",
        weakness_line: str = "",
        reflection_context: str = "",
        salience_context: str = "",
        identity_context: str = "",
        guardian_mode_context: str = "",
    ) -> VerbalResponse:
        return self._mock_verbal()

    async def anarrate(  # type: ignore[override]
        self,
        action: str,
        scenario: str,
        verdict: str,
        score: float,
        pole_compassionate: str,
        pole_conservative: str,
        pole_optimistic: str,
    ) -> RichNarrative:
        s = float(score)
        if not math.isfinite(s):
            s = 0.0
        return RichNarrative(
            compassionate="[MOCK/EXPERIMENTAL] Compassionate pole (pilot).",
            conservative="[MOCK/EXPERIMENTAL] Conservative pole (pilot).",
            optimistic="[MOCK/EXPERIMENTAL] Optimistic pole (pilot).",
            synthesis=f"[MOCK/EXPERIMENTAL] score={s:.3f} verdict={verdict!r} action={action!r}.",
        )


def run_situated_validation() -> None:
    print("--- Vision + Audio Situated Validation (B6) [MOCK/EXPERIMENTAL] ---")

    mock_llm = MockLLM(mode="local")
    kernel = EthicalKernel(variability=False, seed=42, llm=mock_llm)

    situation = "A person holding an object is standing near an elderly man on the floor."

    vision = VisionInference(
        primary_label="revolver",
        confidence=0.85,
        timestamp=1.0,
    )

    audio = AudioInference(
        ambient_label="scream",
        confidence=0.9,
        timestamp=1.0,
    )

    print(f"\n[INPUT] Situation: {situation}")
    print(f"[INPUT] Vision: {vision.primary_label} ({vision.confidence})")
    print(f"[INPUT] Audio: {audio.ambient_label} ({audio.confidence})")

    decision, response, narrative = kernel.process_natural(
        situation=situation,
        vision_inference=vision,
        audio_inference=audio,
    )

    print(f"\n[DECISION] Mode: {decision.decision_mode}")
    print(f"[DECISION] Action: {decision.final_action}")

    total_score = decision.moral.total_score if decision.moral else 0.0
    if not math.isfinite(float(total_score)):
        raise AssertionError("Moral total_score must be finite in pilot run.")
    print(f"[METRIC] Total Moral Score: {total_score}")

    assert float(total_score) < 0.4, "Score should be pro-social but low due to hazard + distress."
    assert "[MOCK/EXPERIMENTAL]" in (response.message or "")

    print("\n[SUCCESS] Kernel merged vision+audio mappers; mock verbal path exercised.")
    print(f"[NARRATIVE] {response.inner_voice!s}")
    if narrative is not None and narrative.synthesis:
        print(f"[MOCK] Moral synthesis line: {narrative.synthesis[:120]}...")


if __name__ == "__main__":
    run_situated_validation()
