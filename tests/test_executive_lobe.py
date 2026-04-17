from src.kernel_lobes.executive_lobe import ExecutiveLobe
from src.kernel_lobes.models import EthicalSentence, SemanticState


def test_executive_lobe_emits_monologue_only_when_safe() -> None:
    lobe = ExecutiveLobe()
    state = SemanticState(perception_confidence=0.9, raw_prompt="assist nearby human")

    safe_text = lobe.formulate_response(
        state,
        EthicalSentence(is_safe=True, social_tension_locus=0.2),
    )
    blocked_text = lobe.formulate_response(
        state,
        EthicalSentence(is_safe=False, social_tension_locus=0.9, veto_reason="unsafe maneuver"),
    )

    assert "Response generated for intent" in safe_text
    assert "[MONO]" in safe_text
    assert blocked_text.startswith("Veto Triggered:")
    assert "[MONO]" not in blocked_text
