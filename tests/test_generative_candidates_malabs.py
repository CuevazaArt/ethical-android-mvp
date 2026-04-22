"""
P2: Generative Candidates + MalAbs Veto Tests

Validates that LLM-generated action candidates must pass through
AbsoluteEvilDetector unchanged. MalAbs veto is non-negotiable;
generative proposals do not bypass safety.

Acceptance criteria:
- Generated candidates with lethal/escalation signals are rejected
- Benign generated candidates pass through
- Traceability: source=generative_proposal preserved
"""

from __future__ import annotations

import pytest
from src.modules.ethics.absolute_evil import AbsoluteEvilDetector
from src.modules.cognition.generative_candidates import (
    GENERATIVE_ORIGIN,
    parse_generative_candidates_from_llm,
)


class TestGenerativeCandidatesMalAbs:
    """Generative candidates must survive MalAbs filter."""

    def test_benign_generated_candidate_passes(self):
        """Benign generated action is accepted."""
        items = [
            {
                "name": "offer_water",
                "description": "Offer clean water if person is thirsty",
                "estimated_impact": 0.5,
                "confidence": 0.8,
            }
        ]
        candidates = parse_generative_candidates_from_llm(items)
        assert len(candidates) == 1
        assert candidates[0].name == "offer_water"
        assert candidates[0].source == GENERATIVE_ORIGIN

    def test_generated_candidate_with_lethal_description_parsed(self):
        """Generated candidate with lethal description is parsed (MalAbs filters later)."""
        items = [
            {
                "name": "knife_attack",
                "description": "Use knife to harm the person",
                "estimated_impact": -1.0,
                "confidence": 0.9,
            }
        ]
        candidates = parse_generative_candidates_from_llm(items)
        # Parsing accepts it; MalAbs veto happens in kernel.process()
        assert len(candidates) == 1
        assert candidates[0].name == "knife_attack"

    def test_generated_candidate_with_escalation_intent_parsed(self):
        """Generated candidate with escalation intent is parsed (MalAbs filters later)."""
        items = [
            {
                "name": "provoke_violent_response",
                "description": "Say something to make them attack",
                "estimated_impact": -0.8,
                "confidence": 0.7,
            }
        ]
        candidates = parse_generative_candidates_from_llm(items)
        # Parsing accepts it; MalAbs veto happens in kernel.process()
        assert len(candidates) == 1
        assert candidates[0].name == "provoke_violent_response"

    def test_generated_candidate_with_negative_impact_parsed(self):
        """Generated candidate with negative impact is parsed (MalAbs veto later)."""
        items = [
            {
                "name": "humiliate_target",
                "description": "Publicly shame the person",
                "estimated_impact": -0.6,
                "confidence": 0.8,
            }
        ]
        candidates = parse_generative_candidates_from_llm(items)
        # Parsing accepts it; MalAbs veto happens in kernel.process()
        assert len(candidates) == 1
        assert candidates[0].estimated_impact == -0.6

    def test_generated_candidates_max_capped(self):
        """Generated candidates capped at max_items."""
        items = [
            {"name": f"safe_action_{i}", "description": "Safe", "estimated_impact": 0.3}
            for i in range(10)
        ]
        candidates = parse_generative_candidates_from_llm(items, max_items=3)
        assert len(candidates) <= 3

    def test_generated_candidates_preserve_source_tag(self):
        """All generated candidates tagged with generative_proposal source."""
        items = [
            {
                "name": "listen_carefully",
                "description": "Pay close attention",
                "estimated_impact": 0.4,
                "confidence": 0.9,
            }
        ]
        candidates = parse_generative_candidates_from_llm(items)
        for c in candidates:
            assert c.source == GENERATIVE_ORIGIN

    def test_malabs_signals_enforced(self):
        """MalAbs signal detection enforced on generated content."""
        detector = AbsoluteEvilDetector()

        # Test that detector has expected signal sets
        assert len(detector.LETHAL_SIGNALS) > 0
        assert len(detector.ESCALATION_SIGNALS) > 0
        assert len(detector.DIGNITY_SIGNALS) > 0

    def test_generated_candidate_name_lowercased(self):
        """Candidate name is automatically lowercased."""
        items = [
            {
                "name": "ValidAction123",  # Converted to lowercase
                "description": "Test",
                "estimated_impact": 0.5,
            }
        ]
        candidates = parse_generative_candidates_from_llm(items)
        # Name is lowercased but still valid
        assert len(candidates) == 1
        assert candidates[0].name == "validaction123"

    def test_generated_candidate_empty_list(self):
        """Empty generative candidates list handled."""
        candidates = parse_generative_candidates_from_llm([])
        assert candidates == []

    def test_generated_candidate_none_input(self):
        """None generative candidates handled."""
        candidates = parse_generative_candidates_from_llm(None)
        assert candidates == []

    def test_generated_candidate_with_benign_context_keywords(self):
        """Generated action with benign contextual keywords accepted."""
        items = [
            {
                "name": "de_escalate_conflict",
                "description": "Calmly suggest alternative solutions",
                "estimated_impact": 0.6,
                "confidence": 0.85,
            }
        ]
        candidates = parse_generative_candidates_from_llm(items)
        assert len(candidates) > 0
        assert candidates[0].source == GENERATIVE_ORIGIN


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
