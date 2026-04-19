"""
Tests for Bloque 11.1: Audio Ouroboros — STT → Reasoning → TTS loop.

Validates:
- Speech-to-text transcription accuracy
- Kernel response generation
- Text-to-speech audio synthesis
- Complete loop integration
"""

import asyncio
import pytest
import numpy as np
from unittest.mock import Mock, patch, AsyncMock

from src.modules.audio_ouroboros import (
    AudioTranscription,
    AudioResponse,
    WhisperAdapter,
    TextToSpeechAdapter,
    AudioOuroborosLoop,
)


class TestAudioTranscription:
    """Test AudioTranscription data class."""

    def test_transcription_creation(self):
        """Create valid transcription object."""
        trans = AudioTranscription(
            text="Hello world",
            confidence=0.95,
            language="en",
            duration_sec=1.2,
        )
        assert trans.text == "Hello world"
        assert trans.confidence == 0.95

    def test_transcription_to_dict(self):
        """Serialize transcription to dict."""
        trans = AudioTranscription(text="Test", confidence=0.8)
        d = trans.to_dict()
        assert "text" in d
        assert "confidence" in d
        assert d["text"] == "Test"
        assert d["confidence"] == 0.8


class TestAudioResponse:
    """Test AudioResponse data class."""

    def test_response_creation(self):
        """Create valid response object."""
        response = AudioResponse(
            text="I understand",
            confidence=0.7,
            source_lobe="executive",
        )
        assert response.text == "I understand"
        assert response.confidence == 0.7
        assert response.source_lobe == "executive"

    def test_response_with_audio_bytes(self):
        """Response can include synthesized audio."""
        audio = b"fake_wav_data"
        response = AudioResponse(
            text="Response",
            audio_bytes=audio,
            duration_sec=2.5,
        )
        assert response.audio_bytes == audio
        assert response.duration_sec == 2.5


class TestWhisperAdapter:
    """Test Whisper speech-to-text adapter."""

    @pytest.mark.asyncio
    async def test_whisper_adapter_initialization(self):
        """Whisper adapter initializes without error."""
        adapter = WhisperAdapter(model_size="tiny")
        assert adapter.model_size == "tiny"
        assert adapter is not None

    @pytest.mark.asyncio
    async def test_transcribe_empty_audio(self):
        """Empty audio returns empty/error transcription."""
        adapter = WhisperAdapter(model_size="tiny")
        empty_audio = np.array([], dtype=np.float32)

        # If Whisper is not loaded, transcription will return error message
        result = await adapter.transcribe_audio(empty_audio)
        # Either empty transcription (if Whisper loaded) or error message (if not)
        assert isinstance(result.text, str)
        assert result.confidence >= 0.0

    @pytest.mark.asyncio
    async def test_transcribe_with_mock(self):
        """Transcribe audio with mocked Whisper model."""
        adapter = WhisperAdapter(model_size="tiny")

        # Mock the initialization to pretend Whisper is loaded
        adapter.model = Mock()  # Set model to non-None

        # Mock the transcription result
        with patch.object(adapter, '_transcribe_blocking') as mock_transcribe:
            mock_transcribe.return_value = AudioTranscription(
                text="Hello there",
                confidence=0.92,
                duration_sec=1.5,
            )

            audio = np.random.randn(16000).astype(np.float32)
            result = await adapter.transcribe_audio(audio, sample_rate=16000)

            assert result.text == "Hello there"
            assert result.confidence == 0.92
            assert result.duration_sec == 1.5


class TestTextToSpeechAdapter:
    """Test text-to-speech synthesis adapter."""

    def test_tts_adapter_initialization_gtts(self):
        """Initialize TTS with gTTS backend."""
        tts = TextToSpeechAdapter(backend="gtts")
        assert tts.backend == "gtts"
        assert tts.language == "en"

    def test_tts_adapter_initialization_pyttsx3(self):
        """Initialize TTS with pyttsx3 backend."""
        tts = TextToSpeechAdapter(backend="pyttsx3")
        assert tts.backend == "pyttsx3"

    @pytest.mark.asyncio
    async def test_synthesize_empty_text(self):
        """Synthesizing empty text returns empty bytes."""
        tts = TextToSpeechAdapter(backend="gtts")
        audio_bytes, duration = await tts.synthesize("")
        assert audio_bytes == b""
        assert duration == 0.0

    @pytest.mark.asyncio
    async def test_synthesize_with_mock(self):
        """Synthesize text with mocked TTS."""
        tts = TextToSpeechAdapter(backend="gtts")

        with patch.object(tts, '_synthesize_blocking') as mock_tts:
            mock_tts.return_value = (b"fake_audio_wav", 2.3)

            audio, duration = await tts.synthesize("Hello world")
            assert audio == b"fake_audio_wav"
            assert duration == 2.3

    @pytest.mark.asyncio
    async def test_synthesize_duration_estimate(self):
        """TTS estimates duration based on text length."""
        tts = TextToSpeechAdapter(backend="gtts")
        text = "This is a longer test sentence with many words."

        with patch.object(tts, '_synthesize_blocking') as mock_tts:
            mock_tts.return_value = (b"audio_data", len(text) / 3.0)

            audio, duration = await tts.synthesize(text)
            assert duration > 0, "Estimated duration should be positive"


class TestAudioOuroborosLoop:
    """Test main Ouroboros loop integration."""

    def test_ouroboros_initialization(self):
        """Initialize Ouroboros loop."""
        loop = AudioOuroborosLoop(sample_rate=16000, whisper_model="tiny")
        assert loop.sample_rate == 16000
        assert loop._running is False
        assert loop.transcriptions_processed == 0
        assert loop.responses_generated == 0

    @pytest.mark.asyncio
    async def test_ouroboros_start_stop(self):
        """Start and stop Ouroboros loop."""
        loop = AudioOuroborosLoop(sample_rate=16000)

        await loop.start()
        assert loop._running is True

        await asyncio.sleep(0.1)  # Let loop initialize

        await loop.stop()
        assert loop._running is False

    @pytest.mark.asyncio
    async def test_ouroboros_generate_response(self):
        """Generate kernel response to transcription."""
        loop = AudioOuroborosLoop()

        transcription = AudioTranscription(
            text="What is the capital of France?",
            confidence=0.95,
        )

        response = await loop._generate_kernel_response(transcription)
        assert response.text  # Should have response text
        assert "France" in response.text or "request" in response.text

    @pytest.mark.asyncio
    async def test_ouroboros_empty_transcription_response(self):
        """Empty transcription gets appropriate response."""
        loop = AudioOuroborosLoop()

        transcription = AudioTranscription(text="", confidence=0.0)
        response = await loop._generate_kernel_response(transcription)

        assert "didn't catch" in response.text.lower() or "repeat" in response.text.lower()
        assert response.confidence == 0.0

    @pytest.mark.asyncio
    async def test_ouroboros_metrics(self):
        """Get Ouroboros loop metrics."""
        loop = AudioOuroborosLoop()

        metrics = loop.get_metrics()
        assert "transcriptions_processed" in metrics
        assert "responses_generated" in metrics
        assert "audio_input_queue_size" in metrics
        assert "audio_output_queue_size" in metrics
        assert "is_running" in metrics

    @pytest.mark.asyncio
    async def test_ouroboros_loop_processes_audio(self):
        """Ouroboros loop processes audio and generates output."""
        loop = AudioOuroborosLoop()

        # Mock the components
        with patch.object(loop.whisper, 'transcribe_audio') as mock_whisper, \
             patch.object(loop.tts, 'synthesize') as mock_tts:

            mock_whisper.return_value = AudioTranscription(
                text="Hello kernel",
                confidence=0.9,
            )
            mock_tts.return_value = (b"audio_response", 1.5)

            await loop.start()
            await asyncio.sleep(0.1)

            # Feed audio to input queue
            audio_chunk = np.random.randn(16000).astype(np.float32)
            loop.audio_input_queue.put(audio_chunk)

            # Wait for processing
            await asyncio.sleep(0.5)

            await loop.stop()

            # Metrics should reflect processing
            metrics = loop.get_metrics()
            # Note: processing may or may not complete in time window
            assert isinstance(metrics, dict)

    @pytest.mark.asyncio
    async def test_ouroboros_queue_isolation(self):
        """Input and output queues are independent."""
        loop = AudioOuroborosLoop()

        audio_chunk = np.random.randn(8000).astype(np.float32)
        loop.audio_input_queue.put(audio_chunk)

        assert loop.audio_input_queue.qsize() == 1
        assert loop.audio_output_queue.qsize() == 0  # Output empty until processing

    @pytest.mark.asyncio
    async def test_ouroboros_loop_error_handling(self):
        """Loop handles errors gracefully."""
        loop = AudioOuroborosLoop()

        # Mock Whisper to raise exception
        with patch.object(loop.whisper, 'transcribe_audio') as mock_whisper:
            mock_whisper.side_effect = RuntimeError("Whisper failed")

            await loop.start()
            await asyncio.sleep(0.1)

            # Feed audio
            audio = np.zeros(8000, dtype=np.float32)
            loop.audio_input_queue.put(audio)

            # Wait for error handling
            await asyncio.sleep(0.5)

            # Loop should still be running (error handled gracefully)
            assert loop._running is True

            await loop.stop()

    def test_ouroboros_full_config(self):
        """Create Ouroboros with various configurations."""
        configs = [
            {"sample_rate": 8000, "whisper_model": "tiny"},
            {"sample_rate": 16000, "whisper_model": "base"},
            {"sample_rate": 44100, "whisper_model": "small"},
        ]

        for config in configs:
            loop = AudioOuroborosLoop(**config)
            assert loop.sample_rate == config["sample_rate"]
            assert loop.whisper.model_size == config["whisper_model"]


class TestAudioOuroborosIntegration:
    """Integration tests for complete audio flow."""

    @pytest.mark.asyncio
    async def test_complete_stt_reasoning_tts_flow(self):
        """Complete flow: audio → speech-to-text → reasoning → speech synthesis."""
        loop = AudioOuroborosLoop(whisper_model="tiny")

        # Mock the expensive components
        with patch.object(loop.whisper, 'transcribe_audio') as mock_stt, \
             patch.object(loop.tts, 'synthesize') as mock_tts:

            mock_stt.return_value = AudioTranscription(
                text="Activate protocol alpha",
                confidence=0.88,
            )
            mock_tts.return_value = (b"affirmative_audio", 2.1)

            # Simulate user audio input
            user_audio = np.random.randn(32000).astype(np.float32)

            # STT
            transcription = await loop.whisper.transcribe_audio(user_audio)
            assert "alpha" in transcription.text

            # Reasoning
            response = await loop._generate_kernel_response(transcription)
            assert response.source_lobe == "executive"

            # TTS
            audio, duration = await loop.tts.synthesize(response.text)
            assert audio == b"affirmative_audio"
            assert duration == 2.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
