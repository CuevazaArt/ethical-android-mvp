from __future__ import annotations

from dataclasses import dataclass

from src.kernel_lobes.executive_lobe import ExecutiveLobe
from src.kernel_lobes.models import EthicalSentence, SemanticState


@dataclass
class _DummyAction:
    name: str
    description: str


class _StubMotivationEngine:
    def __init__(self, actions: list[_DummyAction] | None = None):
        self.actions = actions or []
        self.updated_states: list[dict[str, float]] = []

    def update_drives(self, kernel_state: dict[str, float]) -> None:
        self.updated_states.append(kernel_state)

    def get_proactive_actions(self) -> list[_DummyAction]:
        return self.actions


def test_executive_lobe_blocks_unsafe_ethics_without_monologue() -> None:
    lobe = ExecutiveLobe(motivation_engine=_StubMotivationEngine())
    state = SemanticState(perception_confidence=1.0, raw_prompt="open the door")
    ethics = EthicalSentence(is_safe=False, social_tension_locus=0.2, veto_reason="policy")

    response = lobe.formulate_response(state, ethics)

    assert response == "Veto Triggered: policy"
    assert "[MONO]" not in response


def test_executive_lobe_safe_prompt_includes_monologue() -> None:
    lobe = ExecutiveLobe(motivation_engine=_StubMotivationEngine())
    state = SemanticState(perception_confidence=0.8, raw_prompt="hello there")
    ethics = EthicalSentence(is_safe=True, social_tension_locus=0.3)

    response = lobe.formulate_response(state, ethics)

    assert "Response generated: hello there" in response
    assert "[MONO] action=respond_to_prompt mode=executive_safe_path" in response


def test_executive_lobe_safe_silence_uses_proactive_action() -> None:
    lobe = ExecutiveLobe(
        motivation_engine=_StubMotivationEngine(
            actions=[_DummyAction(name="proactive_exploration", description="scan environment")]
        )
    )
    state = SemanticState(perception_confidence=0.7, raw_prompt="   ")
    ethics = EthicalSentence(is_safe=True, social_tension_locus=0.1)

    response = lobe.formulate_response(state, ethics)

    assert "Response generated: scan environment" in response
    assert "[MONO] action=proactive_exploration mode=executive_safe_path" in response
