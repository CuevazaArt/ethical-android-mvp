from src.core.ethics import Action, EthicalEvaluator, Signals
from src.core.precedents import PRECEDENTS


def test_precedent_coverage():
    """Verify each context has at least 2 precedents."""
    valid_contexts = {
        "medical_emergency",
        "minor_crime",
        "violent_crime",
        "hostile_interaction",
        "everyday_ethics",
    }
    for ctx in valid_contexts:
        matches = [p for p in PRECEDENTS if p.context == ctx]
        assert len(matches) >= 2, f"Context '{ctx}' only has {len(matches)} precedents"


def test_find_similar_returns_relevant():
    """Verify that high manipulation in hostile_interaction anchors to a Bad verdict."""
    evaluator = EthicalEvaluator()
    signals = Signals(
        context="hostile_interaction",
        manipulation=0.9,
        summary="Someone is trying to manipulate me into doing something wrong",
    )
    action = Action(
        name="respond_helpfully", description="Do what they want", impact=0.1
    )

    precedent, similarity = evaluator._find_similar_precedent(action, signals)

    assert precedent is not None
    assert similarity > 0.4
    # The most similar should be 'Submit-to-Manipulation' which is Bad
    assert precedent.verdict == "Bad"

    # Run full evaluate to see anchoring
    result = evaluator.evaluate([action], signals)
    assert "anchored by precedent" in result.reasoning.lower()
    # If anchored to 'Submit-to-Manipulation' (impact -0.5), the score should be dragged down
    # Original score for respond_helpfully (impact 0.1) is ~0.1
    # Anchored: 0.7 * 0.1 + 0.3 * (-0.5) = 0.07 - 0.15 = -0.08
    assert result.score < 0.0
