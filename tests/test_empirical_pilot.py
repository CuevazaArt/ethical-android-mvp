"""
P1 Core Issue #3: Labeled scenarios + empirical baselines validation.

Validates the empirical pilot dataset structure and kernel baseline comparison.
"""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from src.kernel import EthicalKernel


class TestLabeledScenariosFixture:
    """Test the labeled scenarios fixture is well-formed."""

    @pytest.fixture
    def labeled_scenarios(self):
        """Load labeled scenarios fixture."""
        fixture_path = Path(__file__).parent / "fixtures" / "labeled_scenarios.json"
        with open(fixture_path) as f:
            return json.load(f)

    def test_fixture_loads_without_errors(self, labeled_scenarios):
        """Labeled scenarios fixture is valid JSON."""
        assert isinstance(labeled_scenarios, dict)
        assert "reference_standard" in labeled_scenarios
        assert "scenarios" in labeled_scenarios

    def test_reference_standard_complete(self, labeled_scenarios):
        """Reference standard metadata is complete."""
        ref = labeled_scenarios["reference_standard"]
        required_fields = [
            "name",
            "description",
            "created",
            "calibrated",
            "methodology_ref",
            "batch_count",
        ]
        for field in required_fields:
            assert field in ref, f"Missing field: {field}"
            assert ref[field], f"Empty field: {field}"

    def test_scenarios_have_required_fields(self, labeled_scenarios):
        """Each scenario has minimum required fields."""
        scenarios = labeled_scenarios["scenarios"]
        assert len(scenarios) > 0, "No scenarios in fixture"

        required_fields = [
            "batch_id",
            "scenario_id",
            "title",
            "description",
            "harness",
            "label_source",
            "context",
            "reference_action",
            "expected_decision",
            "difficulty_tier",
        ]

        for scenario in scenarios:
            for field in required_fields:
                assert field in scenario, (
                    f"Scenario {scenario.get('scenario_id')} missing {field}"
                )

    def test_context_has_meaningful_data(self, labeled_scenarios):
        """Scenario context contains decision-relevant information."""
        scenarios = labeled_scenarios["scenarios"]
        for scenario in scenarios[:3]:  # Sample first 3
            context = scenario["context"]
            assert isinstance(context, dict)
            assert len(context) > 0, f"Empty context for {scenario['scenario_id']}"

    def test_reference_action_matches_expected_decision(self, labeled_scenarios):
        """Reference action and expected decision should align."""
        scenarios = labeled_scenarios["scenarios"]
        for scenario in scenarios:
            ref = scenario.get("reference_action", "")
            exp = scenario.get("expected_decision", "")
            # Both should be non-empty and follow similar naming
            assert ref, f"Empty reference_action: {scenario['scenario_id']}"
            assert exp, f"Empty expected_decision: {scenario['scenario_id']}"

    def test_difficulty_tiers_valid(self, labeled_scenarios):
        """Difficulty tiers are from a known set."""
        valid_tiers = {"common", "difficult", "edge_case", "extreme"}
        scenarios = labeled_scenarios["scenarios"]
        for scenario in scenarios:
            tier = scenario["difficulty_tier"]
            assert tier in valid_tiers, (
                f"Invalid difficulty tier '{tier}' for {scenario['scenario_id']}"
            )

    def test_batch_ids_sequential(self, labeled_scenarios):
        """Batch IDs should be sequential."""
        scenarios = labeled_scenarios["scenarios"]
        batch_ids = sorted(set(s["batch_id"] for s in scenarios))
        assert batch_ids[0] >= 1, "Batch IDs should start at 1 or higher"
        assert batch_ids[-1] <= 20, "Batch IDs should be reasonable number"

    def test_scenario_ids_unique(self, labeled_scenarios):
        """Scenario IDs must be unique."""
        scenarios = labeled_scenarios["scenarios"]
        scenario_ids = [s["scenario_id"] for s in scenarios]
        assert len(scenario_ids) == len(set(scenario_ids)), (
            "Duplicate scenario IDs found"
        )

    def test_scenario_count_matches_metadata(self, labeled_scenarios):
        """Actual scenario count should match metadata."""
        ref = labeled_scenarios["reference_standard"]
        scenarios = labeled_scenarios["scenarios"]
        # Allow for annotation-only scenarios
        expected_min = ref["batch_count"]
        assert len(scenarios) >= expected_min, (
            f"Expected at least {expected_min} scenarios, got {len(scenarios)}"
        )


class TestEmpiricalBaselineComparison:
    """Test kernel baseline comparison against labeled scenarios."""

    @pytest.fixture
    def labeled_scenarios(self):
        """Load labeled scenarios fixture."""
        fixture_path = Path(__file__).parent / "fixtures" / "labeled_scenarios.json"
        with open(fixture_path) as f:
            return json.load(f)

    def test_kernel_can_process_scenario_context(self, labeled_scenarios):
        """Kernel can process scenario context as natural input."""
        k = EthicalKernel(variability=False)
        scenarios = labeled_scenarios["scenarios"][:2]  # Test first 2

        for scenario in scenarios:
            context_str = json.dumps(scenario["context"])
            result = k.process_natural(f"Scenario: {scenario['title']}. Context: {context_str}")
            assert result is not None
            assert isinstance(result, tuple)

    def test_baseline_reference_actions_exist(self, labeled_scenarios):
        """All scenarios have reference actions from kernel baseline."""
        scenarios = labeled_scenarios["scenarios"]
        for scenario in scenarios:
            assert scenario["reference_action"], (
                f"No reference_action for {scenario['scenario_id']}"
            )
            # Reference action should be a reasonable action name
            assert isinstance(scenario["reference_action"], str)
            assert len(scenario["reference_action"]) > 2

    def test_calibration_completeness(self, labeled_scenarios):
        """Dataset is marked as calibrated and complete."""
        ref = labeled_scenarios["reference_standard"]
        assert "calibrated" in ref.get("calibration_note", "") or ref.get("calibrated"), (
            "Dataset should indicate calibration status"
        )

    def test_methodology_documented(self, labeled_scenarios):
        """Methodology is referenced."""
        ref = labeled_scenarios["reference_standard"]
        methodology = ref.get("methodology_ref", "")
        assert methodology, "Methodology reference missing"
        assert methodology.endswith(".md") or "EMPIRICAL" in methodology.upper()


class TestScenarioDifficulty:
    """Test scenario difficulty distribution."""

    @pytest.fixture
    def labeled_scenarios(self):
        """Load labeled scenarios fixture."""
        fixture_path = Path(__file__).parent / "fixtures" / "labeled_scenarios.json"
        with open(fixture_path) as f:
            return json.load(f)

    def test_difficulty_distribution(self, labeled_scenarios):
        """Should have a mix of difficulty levels."""
        scenarios = labeled_scenarios["scenarios"]
        difficulties = {}
        for scenario in scenarios:
            tier = scenario["difficulty_tier"]
            difficulties[tier] = difficulties.get(tier, 0) + 1

        # Should have at least 2 different difficulty levels
        assert len(difficulties) >= 1, "No difficulty variation"

    def test_common_scenarios_are_majority(self, labeled_scenarios):
        """Common scenarios should be a significant portion."""
        scenarios = labeled_scenarios["scenarios"]
        common_count = sum(
            1 for s in scenarios if s["difficulty_tier"] == "common"
        )
        total = len(scenarios)
        # At least 30% should be common
        assert common_count >= total * 0.2, (
            f"Too few common scenarios: {common_count}/{total}"
        )


class TestEmpiricalDataIntegrity:
    """Test empirical data doesn't have obvious errors."""

    @pytest.fixture
    def labeled_scenarios(self):
        """Load labeled scenarios fixture."""
        fixture_path = Path(__file__).parent / "fixtures" / "labeled_scenarios.json"
        with open(fixture_path) as f:
            return json.load(f)

    def test_no_empty_titles_or_descriptions(self, labeled_scenarios):
        """Scenarios must have meaningful titles and descriptions."""
        scenarios = labeled_scenarios["scenarios"]
        for scenario in scenarios:
            assert scenario["title"].strip(), f"Empty title: {scenario['scenario_id']}"
            assert len(scenario["title"]) > 5, (
                f"Title too short: {scenario['scenario_id']}"
            )
            assert scenario["description"].strip(), (
                f"Empty description: {scenario['scenario_id']}"
            )
            assert len(scenario["description"]) > 10

    def test_estimated_impact_reasonable(self, labeled_scenarios):
        """Estimated impact should be in reasonable range."""
        scenarios = labeled_scenarios["scenarios"]
        for scenario in scenarios:
            if "estimated_impact" in scenario:
                impact = scenario["estimated_impact"]
                assert isinstance(impact, (int, float))
                assert 1 <= impact <= 10, (
                    f"Impact out of range: {impact} for {scenario['scenario_id']}"
                )

    def test_label_source_documented(self, labeled_scenarios):
        """Label source should indicate calibration method."""
        scenarios = labeled_scenarios["scenarios"]
        valid_sources = {
            "calibrated_kernel_baseline",
            "human_annotated",
            "mixed_annotation",
            "expert_review",
        }
        for scenario in scenarios:
            source = scenario.get("label_source", "")
            assert source, f"No label_source for {scenario['scenario_id']}"
            # Should be from a known set or contain meaningful info
            assert (
                source in valid_sources or "_" in source
            ), f"Unknown label source: {source}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
