from unittest.mock import Mock

from src.kernel_lobes.executive_lobe import ExecutiveLobe
from src.kernel_lobes.models import EthicalSentence, SemanticState
from src.modules.weighted_ethics_scorer import CandidateAction


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


def test_executive_lobe_appends_proactive_focus_when_available() -> None:
    lobe = ExecutiveLobe()
    state = SemanticState(perception_confidence=0.9, raw_prompt="assist nearby human")

    lobe.motivation_engine.get_proactive_actions = Mock(
        return_value=[
            CandidateAction(
                name="proactive_social_check",
                description="Check nearby partner state.",
                estimated_impact=0.7,
                confidence=0.9,
            )
        ]
    )
    lobe.motivation_engine.update_drives = Mock(return_value=None)

    safe_text = lobe.formulate_response(
        state,
        EthicalSentence(is_safe=True, social_tension_locus=0.2),
    )

    assert "proactive_focus=proactive_social_check" in safe_text
    lobe.motivation_engine.update_drives.assert_called_once()
    lobe.motivation_engine.get_proactive_actions.assert_called_once()
