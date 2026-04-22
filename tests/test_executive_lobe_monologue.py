import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel_lobes.executive_lobe import ExecutiveLobe
from src.modules.ethics.absolute_evil import AbsoluteEvilDetector


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
    lobe = ExecutiveLobe(absolute_evil=AbsoluteEvilDetector())
    line = lobe.build_safe_monologue(
        _decision(blocked=False),
        episode_id="ep-1",
        is_safe=True,
        expose_monologue=True,
        embellish=None,
    )
    assert line


def test_build_safe_monologue_blocks_when_not_safe():
    lobe = ExecutiveLobe(absolute_evil=AbsoluteEvilDetector())
    line = lobe.build_safe_monologue(
        _decision(blocked=True),
        episode_id="ep-1",
        is_safe=False,
        expose_monologue=True,
        embellish=None,
    )
    assert line == ""
