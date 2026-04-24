import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.internal_monologue import compose_monologue_line


def _decision(blocked: bool = False):
    return SimpleNamespace(
        blocked=blocked,
        absolute_evil=SimpleNamespace(blocked=blocked),
        scenario="scenario",
        final_action="communicate",
        decision_mode="D_fast",
        sympathetic_state=SimpleNamespace(mode="regulated", sigma=0.2),
        social_evaluation=SimpleNamespace(circle=SimpleNamespace(value="neutral_soto")),
        moral=SimpleNamespace(global_verdict=SimpleNamespace(value="gray_zone"), total_score=0.1),
        reflection=None,
        salience=None,
        affect=None,
    )


def test_build_safe_monologue_emits_only_on_safe_path():
    line = compose_monologue_line(_decision(blocked=False), episode_id="ep-1")
    assert line


def test_build_safe_monologue_blocks_when_not_safe():
    line = compose_monologue_line(_decision(blocked=True), episode_id="ep-1")
    assert "[MONO] blocked=1" in line
