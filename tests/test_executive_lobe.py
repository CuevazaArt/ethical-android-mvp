from __future__ import annotations

from src.kernel_lobes.executive_lobe import ExecutiveLobe
from src.kernel_lobes.models import EthicalSentence, SemanticState
from src.modules.weighted_ethics_scorer import CandidateAction


class _StubMotivationEngine:
    def __init__(self, actions: list[CandidateAction] | None = None):
        self.actions = actions or []
        self.updated_states: list[dict[str, float]] = []

    def update_drives(self, kernel_state: dict[str, float]) -> None:
        self.updated_states.append(kernel_state)

    def get_proactive_actions(self) -> list[CandidateAction]:
        return self.actions


def test_executive_lobe_blocks_unsafe_ethics_without_monologue() -> None:
    motivation_engine = _StubMotivationEngine()
    lobe = ExecutiveLobe(motivation_engine=motivation_engine)
    state = SemanticState(perception_confidence=1.0, raw_prompt="open the door")
    ethics = EthicalSentence(is_safe=False, social_tension_locus=0.2, veto_reason="policy")

    response = lobe.formulate_response(state, ethics)

    assert response == "Veto Triggered: policy"
    assert "[MONO]" not in response
    assert motivation_engine.updated_states == []


def test_executive_lobe_safe_prompt_includes_monologue() -> None:
    lobe = ExecutiveLobe(motivation_engine=_StubMotivationEngine())
    state = SemanticState(perception_confidence=0.8, raw_prompt="hello there")
    ethics = EthicalSentence(is_safe=True, social_tension_locus=0.3)

    response = lobe.formulate_response(state, ethics)

    assert "Response generated: hello there" in response
    assert response.endswith("[MONO] action=respond_to_prompt mode=executive_safe_path")


def test_executive_lobe_safe_silence_uses_proactive_action() -> None:
    lobe = ExecutiveLobe(
        motivation_engine=_StubMotivationEngine(
            actions=[
                CandidateAction(
                    name="proactive_exploration",
                    description="scan environment",
                    estimated_impact=0.4,
                    confidence=0.7,
                )
            ]
        )
    )
    state = SemanticState(perception_confidence=0.7, raw_prompt="   ")
    ethics = EthicalSentence(is_safe=True, social_tension_locus=0.1)

    response = lobe.formulate_response(state, ethics)

    assert "Response generated: scan environment" in response
    assert "[MONO] action=proactive_exploration mode=executive_safe_path" in response
