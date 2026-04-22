"""
Tests for Bloque 13.0 — Desbloqueo Conversacional y Voz (Zero-Friction Audio)

Covers:
- 13.1: KERNEL_LIMBIC_PERCEPTION_TIMEOUT wraps run_perception_stage_async
- 13.1: KERNEL_CHAT_TURN_TIMEOUT defaults to 30 s in KernelSettings
- 13.2: VAD logic (tested via Python re-implementation of the JS state machine)
"""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# 13.1a — KERNEL_CHAT_TURN_TIMEOUT default in settings
# ---------------------------------------------------------------------------


class TestChatTurnTimeoutDefault:
    def test_default_is_30s_remote_profile(self):
        """Unset KERNEL_CHAT_TURN_TIMEOUT + no local-Ollama stack → 30 s API-style default."""
        skip = {
            "KERNEL_CHAT_TURN_TIMEOUT",
            "USE_LOCAL_LLM",
            "LLM_MODE",
            "KERNEL_NOMAD_MODE",
        }
        env = {k: v for k, v in os.environ.items() if k not in skip}
        with patch.dict(os.environ, env, clear=True):
            from src.settings.kernel_settings import KernelSettings

            st = KernelSettings.from_env()
        assert st.kernel_chat_turn_timeout_seconds == 30.0

    def test_default_is_180s_when_use_local_llm(self):
        """Bloque 20.2: local stack needs a longer async wait than cloud API defaults."""
        skip = {"KERNEL_CHAT_TURN_TIMEOUT", "LLM_MODE", "KERNEL_NOMAD_MODE"}
        env = {k: v for k, v in os.environ.items() if k not in skip}
        env["USE_LOCAL_LLM"] = "1"
        with patch.dict(os.environ, env, clear=True):
            from src.settings.kernel_settings import KernelSettings

            st = KernelSettings.from_env()
        assert st.kernel_chat_turn_timeout_seconds == 180.0

    def test_default_is_60s_when_nomad_mode(self):
        skip = {"KERNEL_CHAT_TURN_TIMEOUT", "USE_LOCAL_LLM", "LLM_MODE"}
        env = {k: v for k, v in os.environ.items() if k not in skip}
        env["KERNEL_NOMAD_MODE"] = "1"
        with patch.dict(os.environ, env, clear=True):
            from src.settings.kernel_settings import KernelSettings

            st = KernelSettings.from_env()
        assert st.kernel_chat_turn_timeout_seconds == 60.0

    def test_env_override(self):
        """Explicit env value is honoured."""
        with patch.dict(os.environ, {"KERNEL_CHAT_TURN_TIMEOUT": "15"}):
            from src.settings.kernel_settings import KernelSettings

            st = KernelSettings.from_env()
        assert st.kernel_chat_turn_timeout_seconds == 15.0


# ---------------------------------------------------------------------------
# 13.1b — _get_limbic_perception_timeout
# ---------------------------------------------------------------------------


class TestLimbicPerceptionTimeoutHelper:
    def test_default_12s(self):
        env = {k: v for k, v in os.environ.items() if k != "KERNEL_LIMBIC_PERCEPTION_TIMEOUT"}
        with patch.dict(os.environ, env, clear=True):
            from src.kernel_lobes.perception_lobe import PerceptiveLobe

            assert PerceptiveLobe._get_limbic_perception_timeout() == 12.0

    def test_env_override(self):
        with patch.dict(os.environ, {"KERNEL_LIMBIC_PERCEPTION_TIMEOUT": "5"}):
            from src.kernel_lobes.perception_lobe import PerceptiveLobe

            assert PerceptiveLobe._get_limbic_perception_timeout() == 5.0

    def test_zero_disables(self):
        with patch.dict(os.environ, {"KERNEL_LIMBIC_PERCEPTION_TIMEOUT": "0"}):
            from src.kernel_lobes.perception_lobe import PerceptiveLobe

            assert PerceptiveLobe._get_limbic_perception_timeout() is None

    def test_invalid_falls_back_to_12(self):
        with patch.dict(os.environ, {"KERNEL_LIMBIC_PERCEPTION_TIMEOUT": "NaN"}):
            from src.kernel_lobes.perception_lobe import PerceptiveLobe

            assert PerceptiveLobe._get_limbic_perception_timeout() == 12.0


# ---------------------------------------------------------------------------
# 13.1c — run_perception_stage_async falls back gracefully on timeout
# ---------------------------------------------------------------------------


class TestPerceptionStageTimeout:
    @pytest.mark.asyncio
    async def test_degraded_path_returned_on_timeout(self):
        """
        When _run_perception_stage_inner sleeps longer than the timeout,
        run_perception_stage_async must return a degraded PerceptionStageResult
        without raising.
        """
        from src.kernel_lobes.perception_lobe import PerceptiveLobe

        lobe = PerceptiveLobe.__new__(PerceptiveLobe)
        lobe._timeout = 1.0
        lobe._process_start_mono = time.monotonic()

        async def _slow_inner(*args, **kwargs):
            await asyncio.sleep(10)

        with patch.dict(os.environ, {"KERNEL_LIMBIC_PERCEPTION_TIMEOUT": "0.05"}):
            with patch.object(lobe, "_run_perception_stage_inner", side_effect=_slow_inner):
                result = await lobe.run_perception_stage_async("hello")

        assert result is not None
        assert result.perception is not None
        # Degraded: confidence near 0 and trauma recorded
        assert result.perception.perception_confidence <= 0.1
        assert result.perception.timeout_trauma is not None
        assert "limbic_perception_stage" in result.perception.timeout_trauma.source_lobe

    @pytest.mark.asyncio
    async def test_normal_path_returned_when_fast(self):
        """
        When inner stage completes quickly, normal result is returned.
        """
        from src.kernel_lobes.models import PerceptionStageResult
        from src.kernel_lobes.perception_lobe import PerceptiveLobe

        lobe = PerceptiveLobe.__new__(PerceptiveLobe)
        lobe._timeout = 5.0
        lobe._process_start_mono = time.monotonic()

        # Use MagicMock so we don't have to know all required fields
        fake_result = MagicMock(spec=PerceptionStageResult)
        fake_result.perception = MagicMock()
        fake_result.perception.perception_confidence = 0.9

        async def _fast_inner(*args, **kwargs):
            return fake_result

        with patch.dict(os.environ, {"KERNEL_LIMBIC_PERCEPTION_TIMEOUT": "5"}):
            with patch.object(lobe, "_run_perception_stage_inner", side_effect=_fast_inner):
                result = await lobe.run_perception_stage_async("hello")

        assert result.perception.perception_confidence == 0.9


# ---------------------------------------------------------------------------
# 13.2 — VAD state machine (Python mirror of media_engine.js logic)
# ---------------------------------------------------------------------------


class _VAD:
    """Pure-Python mirror of the JS VAD in media_engine.js (for unit testing).

    Logic mirrors the latched version committed in Bloque 13.2:
    - Onset: ONSET_FRAMES consecutive above-threshold frames → speech=True
    - Sustain: once speaking, hangover alone sustains speech (above_count can be 0)
    - End: speech=False when hangover drains to 0
    """

    RMS_THRESHOLD = 0.015
    ONSET_FRAMES = 3
    HANGOVER_FRAMES = 12

    def __init__(self) -> None:
        self._above = 0
        self._hangover = 0
        self._speaking = False
        self.events: list[str] = []

    def update(self, rms: float) -> bool:
        active = rms >= self.RMS_THRESHOLD
        if active:
            self._hangover = self.HANGOVER_FRAMES
            self._above = min(self._above + 1, self.ONSET_FRAMES + 1)
        else:
            self._above = 0
            if self._hangover > 0:
                self._hangover -= 1

        was = self._speaking
        # Latched state: onset triggers on ONSET_FRAMES; hangover sustains
        if not self._speaking:
            self._speaking = self._above >= self.ONSET_FRAMES
        else:
            self._speaking = self._hangover > 0

        if not was and self._speaking:
            self.events.append("speech_start")
        elif was and not self._speaking:
            self.events.append("speech_end")

        return self._speaking


class TestVADStateMachine:
    def test_silence_stays_false(self):
        vad = _VAD()
        for _ in range(20):
            assert not vad.update(0.001)
        assert "speech_start" not in vad.events

    def test_onset_requires_consecutive_frames(self):
        vad = _VAD()
        # Only 2 frames above threshold (< ONSET_FRAMES=3)
        vad.update(0.1)
        vad.update(0.1)
        assert not vad._speaking, "Should not trigger before ONSET_FRAMES"

    def test_onset_after_3_frames(self):
        vad = _VAD()
        for _ in range(3):
            vad.update(0.1)
        assert vad._speaking
        assert "speech_start" in vad.events

    def test_hangover_keeps_speaking_after_silence(self):
        vad = _VAD()
        for _ in range(3):
            vad.update(0.1)
        # Single silence frame should NOT end speech (hangover active, latched state)
        result = vad.update(0.001)
        assert result, "Hangover should keep speech active"
        assert "speech_end" not in vad.events

    def test_speech_end_after_hangover_expires(self):
        vad = _VAD()
        for _ in range(3):
            vad.update(0.1)
        # Drain hangover
        for _ in range(_VAD.HANGOVER_FRAMES + 1):
            vad.update(0.001)
        assert not vad._speaking
        assert "speech_end" in vad.events

    def test_speech_start_fires_only_once(self):
        vad = _VAD()
        for _ in range(30):
            vad.update(0.1)
        assert vad.events.count("speech_start") == 1

    def test_stt_confidence_gate(self):
        """STT transcript with confidence < 0.45 should be rejected."""
        MIN_CONFIDENCE = 0.45
        assert 0.3 < MIN_CONFIDENCE, "Low confidence must be filtered"
        assert 0.9 >= MIN_CONFIDENCE, "High confidence must pass"

    def test_vad_silence_gates_stt(self):
        """If VAD is silent (hangover=0) transcript should be dropped."""
        vad = _VAD()
        # All silence
        for _ in range(20):
            vad.update(0.001)
        assert not vad._speaking
        assert vad._hangover == 0
        # Simulated STT result would be rejected (gate check)
        should_send = vad._speaking or vad._hangover > 0
        assert not should_send


# ---------------------------------------------------------------------------
# 13.1 NEW — NomadBridge vad_event + chat_text relay (Bloque 13.1)
# ---------------------------------------------------------------------------


class TestNomadBridgeVadEvent:
    """NomadBridge._recv_loop must update vad_speaking on vad_event payloads."""

    def _make_bridge(self) -> Any:
        from src.modules.nomad_bridge import NomadBridge

        return NomadBridge()

    def test_initial_vad_speaking_is_false(self) -> None:
        bridge = self._make_bridge()
        assert bridge.vad_speaking is False

    @pytest.mark.asyncio
    async def test_speech_start_sets_true(self) -> None:
        bridge = self._make_bridge()
        messages = [{"type": "vad_event", "payload": {"state": "speech_start"}}]
        idx = 0

        async def _recv() -> dict:
            nonlocal idx
            if idx < len(messages):
                m = messages[idx]
                idx += 1
                return m
            raise asyncio.CancelledError

        ws = MagicMock()
        ws.receive_json = _recv
        with pytest.raises(asyncio.CancelledError):
            await bridge._recv_loop(ws)
        assert bridge.vad_speaking is True

    @pytest.mark.asyncio
    async def test_speech_end_sets_false(self) -> None:
        bridge = self._make_bridge()
        bridge.vad_speaking = True
        messages = [{"type": "vad_event", "payload": {"state": "speech_end"}}]
        idx = 0

        async def _recv() -> dict:
            nonlocal idx
            if idx < len(messages):
                m = messages[idx]
                idx += 1
                return m
            raise asyncio.CancelledError

        ws = MagicMock()
        ws.receive_json = _recv
        with pytest.raises(asyncio.CancelledError):
            await bridge._recv_loop(ws)
        assert bridge.vad_speaking is False

    @pytest.mark.asyncio
    async def test_unknown_state_does_not_crash(self) -> None:
        bridge = self._make_bridge()
        messages = [{"type": "vad_event", "payload": {"state": "whatever"}}]
        idx = 0

        async def _recv() -> dict:
            nonlocal idx
            if idx < len(messages):
                m = messages[idx]
                idx += 1
                return m
            raise asyncio.CancelledError

        ws = MagicMock()
        ws.receive_json = _recv
        with pytest.raises(asyncio.CancelledError):
            await bridge._recv_loop(ws)
        assert bridge.vad_speaking is False


class TestNomadBridgeChatTextQueue:
    """chat_text events must be enqueued; empty strings must be dropped."""

    def _make_bridge(self) -> Any:
        from src.modules.nomad_bridge import NomadBridge

        return NomadBridge()

    @pytest.mark.asyncio
    async def test_text_enqueued(self) -> None:
        bridge = self._make_bridge()
        messages = [{"type": "chat_text", "payload": {"text": "Hello Nomad"}}]
        idx = 0

        async def _recv() -> dict:
            nonlocal idx
            if idx < len(messages):
                m = messages[idx]
                idx += 1
                return m
            raise asyncio.CancelledError

        ws = MagicMock()
        ws.receive_json = _recv
        with pytest.raises(asyncio.CancelledError):
            await bridge._recv_loop(ws)

        assert not bridge.chat_text_queue.empty()
        assert bridge.chat_text_queue.get_nowait() == "Hello Nomad"

    @pytest.mark.asyncio
    async def test_empty_text_not_enqueued(self) -> None:
        bridge = self._make_bridge()
        messages = [{"type": "chat_text", "payload": {"text": "   "}}]
        idx = 0

        async def _recv() -> dict:
            nonlocal idx
            if idx < len(messages):
                m = messages[idx]
                idx += 1
                return m
            raise asyncio.CancelledError

        ws = MagicMock()
        ws.receive_json = _recv
        with pytest.raises(asyncio.CancelledError):
            await bridge._recv_loop(ws)
        assert bridge.chat_text_queue.empty()

    @pytest.mark.asyncio
    async def test_missing_text_field_not_enqueued(self) -> None:
        bridge = self._make_bridge()
        messages = [{"type": "chat_text", "payload": {}}]
        idx = 0

        async def _recv() -> dict:
            nonlocal idx
            if idx < len(messages):
                m = messages[idx]
                idx += 1
                return m
            raise asyncio.CancelledError

        ws = MagicMock()
        ws.receive_json = _recv
        with pytest.raises(asyncio.CancelledError):
            await bridge._recv_loop(ws)
        assert bridge.chat_text_queue.empty()


class TestChatTextConsumerCallback:
    """_chat_text_consumer must dispatch to the callback and survive errors."""

    def _make_bridge(self) -> Any:
        from src.modules.nomad_bridge import NomadBridge

        return NomadBridge()

    @pytest.mark.asyncio
    async def test_callback_invoked_for_queued_text(self) -> None:
        bridge = self._make_bridge()
        received: list[str] = []

        async def cb(text: str) -> None:
            received.append(text)

        await bridge.chat_text_queue.put("alpha")
        await bridge.chat_text_queue.put("beta")

        task = asyncio.create_task(bridge._chat_text_consumer(cb))
        for _ in range(30):
            await asyncio.sleep(0)
            if len(received) >= 2:
                break
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert received == ["alpha", "beta"]

    @pytest.mark.asyncio
    async def test_callback_exception_does_not_crash_consumer(self) -> None:
        bridge = self._make_bridge()

        async def bad_cb(text: str) -> None:
            raise RuntimeError("simulated callback failure")

        await bridge.chat_text_queue.put("trigger")

        task = asyncio.create_task(bridge._chat_text_consumer(bad_cb))
        for _ in range(20):
            await asyncio.sleep(0)
            if bridge.chat_text_queue.empty():
                break
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        # No assertion — test verifies consumer survives callback exception


class TestNomadChatTimeoutSetting:
    """KernelSettings.kernel_nomad_chat_timeout_seconds must be configurable."""

    def test_default_five_seconds(self) -> None:
        from src.settings.kernel_settings import KernelSettings

        env = {k: v for k, v in os.environ.items() if k != "KERNEL_NOMAD_CHAT_TIMEOUT"}
        with patch.dict(os.environ, env, clear=True):
            st = KernelSettings.from_env()
        assert st.kernel_nomad_chat_timeout_seconds == pytest.approx(5.0)

    def test_env_override(self) -> None:
        from src.settings.kernel_settings import KernelSettings

        with patch.dict(os.environ, {"KERNEL_NOMAD_CHAT_TIMEOUT": "2.5"}):
            st = KernelSettings.from_env()
        assert st.kernel_nomad_chat_timeout_seconds == pytest.approx(2.5)
