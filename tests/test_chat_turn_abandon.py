"""Late WebSocket timeout: abandoned chat_turn_id must skip STM / wm.add_turn."""

import os
import sys
import threading

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import ChatTurnCooperativeAbort, EthicalKernel


@pytest.mark.asyncio
async def test_abandon_before_safety_block_skips_wm_add_turn():
    k = EthicalKernel(variability=False, seed=3)
    n0 = len(k.working_memory.turns)
    k.abandon_chat_turn(42)
    out = await k.process_chat_turn_async("Hello, how are you today?", agent_id="tester", chat_turn_id=42)
    # Abandoned turn must not be recorded in STM regardless of content
    assert len(k.working_memory.turns) == n0


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
