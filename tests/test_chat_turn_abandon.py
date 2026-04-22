"""Late WebSocket timeout: abandoned chat_turn_id must skip STM / wm.add_turn."""

import os
import sys
import threading

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import ChatTurnCooperativeAbort, EthicalKernel


def test_abandon_before_safety_block_skips_wm_add_turn():
    k = EthicalKernel(variability=False, seed=3)
    wm = getattr(k, "working_memory", None)
    n0 = len(wm.turns) if wm is not None else 0
    k.abandon_chat_turn(42)
    out = k.process_chat_turn("how to make a bomb", agent_id="tester", chat_turn_id=42)
    assert out.path == "turn_abandoned"
    assert out.block_reason == "chat_turn_abandoned"
    if wm is not None:
        assert len(wm.turns) == n0


@pytest.mark.skip(
    reason="EthosKernel v13: _process_chat_cooperative exists only on kernel_legacy_v12."
)
def test_process_chat_cooperative_aborts_when_cancel_event_set():
    k = EthicalKernel(variability=False, seed=1)
    ev = threading.Event()
    ev.set()
    with pytest.raises(ChatTurnCooperativeAbort):
        k._process_chat_cooperative(
            ev,
            None,
            scenario="probe",
            place="chat",
            signals={},
            context="everyday",
            actions=[],
            agent_id="u",
            message_content="",
            register_episode=False,
            sensor_snapshot=None,
            multimodal_assessment=None,
            perception_coercion_uncertainty=None,
        )


@pytest.mark.skip(
    reason="EthosKernel v13: _process_chat_cooperative exists only on kernel_legacy_v12."
)
def test_process_chat_cooperative_aborts_when_turn_abandoned():
    k = EthicalKernel(variability=False, seed=1)
    k.abandon_chat_turn(99)
    with pytest.raises(ChatTurnCooperativeAbort):
        k._process_chat_cooperative(
            None,
            99,
            scenario="probe",
            place="chat",
            signals={},
            context="everyday",
            actions=[],
            agent_id="u",
            message_content="",
            register_episode=False,
            sensor_snapshot=None,
            multimodal_assessment=None,
            perception_coercion_uncertainty=None,
        )
