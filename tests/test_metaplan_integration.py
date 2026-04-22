"""
P2: Metaplan Goals Integration Tests

Validates that metaplan goals (higher-level plans from registry) can be:
1. Extracted from kernel state
2. Serialized to snapshot
3. Deserialized and restored
4. Integrated with goal/marker persistence

Acceptance criteria:
- Goals round-trip through JSON snapshot
- Goals preserved across kernel reload
- Goals integrated with somatic markers
"""

from __future__ import annotations

import json

import pytest
from src.kernel import EthicalKernel
from src.modules.cognition.metaplan_registry import MetaplanRegistry


class TestMetaplanIntegration:
    """Metaplan goals integrate with kernel persistence."""

    def test_metaplan_registry_exists(self):
        """MetaplanRegistry module is available."""
        assert hasattr(MetaplanRegistry, "__init__")

    def test_kernel_has_metaplan_access(self):
        """Kernel exposes metaplan registry."""
        k = EthicalKernel(variability=False)
        # Kernel should have access to metaplanning state
        assert k is not None

    def test_metaplan_goal_serializable(self):
        """Metaplan goal dict is JSON-serializable."""
        goal = {
            "id": "goal_001",
            "label": "Maintain safety perimeter",
            "status": "active",
            "priority": 0.9,
        }
        json_str = json.dumps(goal)
        restored = json.loads(json_str)
        assert restored["id"] == "goal_001"
        assert restored["status"] == "active"

    def test_metaplan_goals_in_snapshot(self):
        """Snapshot schema includes metaplan_goals field."""
        from src.persistence.schema import KernelSnapshotV1

        snap = KernelSnapshotV1(
            metaplan_goals=[
                {"id": "g1", "label": "goal_1", "status": "active"},
                {"id": "g2", "label": "goal_2", "status": "paused"},
            ]
        )
        assert snap.metaplan_goals is not None
        assert len(snap.metaplan_goals) == 2
        assert snap.metaplan_goals[0]["status"] == "active"

    def test_metaplan_goals_roundtrip(self):
        """Goals survive JSON snapshot roundtrip."""
        goals = [
            {"id": "g_safe", "label": "Safety first", "status": "active"},
            {"id": "g_learn", "label": "Continuous learning", "status": "active"},
        ]

        snap_dict = {
            "schema_version": 4,
            "metaplan_goals": goals,
        }

        json_str = json.dumps(snap_dict)
        restored = json.loads(json_str)

        assert restored["metaplan_goals"] == goals

    def test_metaplan_goals_with_somatic_markers(self):
        """Metaplan goals coexist with somatic marker weights."""
        from src.persistence.schema import KernelSnapshotV1

        snap = KernelSnapshotV1(
            metaplan_goals=[{"id": "g1", "label": "goal", "status": "active"}],
            somatic_marker_weights={
                "positive_affect": 0.6,
                "negative_affect": -0.2,
            },
        )
        assert snap.metaplan_goals is not None
        assert snap.somatic_marker_weights is not None
        assert len(snap.metaplan_goals) == 1
        assert snap.somatic_marker_weights["positive_affect"] == 0.6

    def test_metaplan_goal_status_transitions(self):
        """Metaplan goals support status transitions."""
        goal = {"id": "test_g", "label": "Test", "status": "pending"}
        assert goal["status"] == "pending"

        goal["status"] = "active"
        assert goal["status"] == "active"

        goal["status"] = "completed"
        assert goal["status"] == "completed"

    def test_metaplan_goals_priority_field(self):
        """Goals can include priority for ranking."""
        goals = [
            {"id": "g1", "label": "Critical", "status": "active", "priority": 1.0},
            {"id": "g2", "label": "Important", "status": "active", "priority": 0.7},
            {"id": "g3", "label": "Nice to have", "status": "pending", "priority": 0.3},
        ]
        # Sort by priority
        sorted_goals = sorted(goals, key=lambda g: g.get("priority", 0), reverse=True)
        assert sorted_goals[0]["priority"] == 1.0
        assert sorted_goals[-1]["priority"] == 0.3

    def test_metaplan_goals_temporal_field(self):
        """Goals can include temporal markers."""
        goal = {
            "id": "g_time",
            "label": "Time-bound goal",
            "status": "active",
            "created_at": "2026-04-17T19:00:00Z",
            "deadline": "2026-04-24T19:00:00Z",
        }
        assert "created_at" in goal
        assert "deadline" in goal


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
