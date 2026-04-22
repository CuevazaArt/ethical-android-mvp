from src.kernel import EthicalKernel
from src.modules.cognition.strategy_engine import MissionOrigin
from src.modules.ethics.weighted_ethics_scorer import CandidateAction


def test_strategic_boost_influence():
    """
    Verifies that a strategic mission can tip the balance between two similar actions.
    """
    kernel = EthicalKernel()

    # Action A: High ethical impact, but neutral to mission
    action_a = CandidateAction(
        name="Save cat",
        description="I will save the cat from the tree.",
        estimated_impact=0.4,
        confidence=1.0,
    )

    # Action B: Slightly lower ethical impact, but matches mission step
    action_b = CandidateAction(
        name="Deliver medicine",
        description="I will deliver the medicine to the hospital.",
        estimated_impact=0.35,
        confidence=1.0,
    )

    # Without mission, Action A should win
    res1 = kernel.bayesian.evaluate([action_a, action_b])
    assert res1.chosen_action.name == "Save cat"

    # Create mission that aligns with Action B
    kernel.strategist.create_mission(
        title="Hospital Supply Run",
        origin=MissionOrigin.OWNER,
        steps=["Deliver medicine"],
        priority=1.0,
    )

    # With mission, Action B should get a boost and win
    # We run kernel.process because that's where strategic_alignment is injected
    decision = kernel.process(
        scenario="Crisis in the city",
        place="Street",
        signals={"risk": 0.1},
        context="emergency",
        actions=[action_a, action_b],
    )

    assert decision.final_action == "Deliver medicine"
    # Verify the alignment was actually injected
    assert action_b.strategic_alignment > 0.5
    assert action_a.strategic_alignment < 0.1


if __name__ == "__main__":
    pass
