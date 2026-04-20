from __future__ import annotations
import logging
import queue
import threading
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Set, Tuple

import numpy as np

if TYPE_CHECKING:
    from src.modules.nomad_bridge import NomadBridge

_log = logging.getLogger(__name__)


class AudioRingBuffer:
    """
    Block A2: Maintains a continuous, thread-safe queue of incoming audio chunks.
    Overwrites the oldest data if the buffer overflows to keep the feed real-time.
    """

    def __init__(self, capacity_chunks: int = 100) -> None:
        self.capacity: int = capacity_chunks
        self.buffer: queue.Queue[np.ndarray] = queue.Queue(maxsize=capacity_chunks)
        self.lock: threading.Lock = threading.Lock()

    def append(self, chunk: np.ndarray) -> None:
        """Appends a new PCM audio chunk. Evicts oldest if full."""
        with self.lock:
            if self.buffer.full():
                try:
                    self.buffer.get_nowait()
                except queue.Empty:
                    pass
            self.buffer.put_nowait(chunk)

    def get_next(self) -> Optional[np.ndarray]:
        """Pulls the oldest unread chunk from the buffer."""
        try:
            return self.buffer.get_nowait()
        except queue.Empty:
            return None

    def flush(self) -> List[np.ndarray]:
        """Returns all currently buffered chunks and empties the queue."""
        frames: List[np.ndarray] = []
        with self.lock:
            while not self.buffer.empty():
                frames.append(self.buffer.get_nowait())
        return frames


class AudioCaptureInterface:
    """
    Block A1: Interface for the microphone/ADC.
    Continuously samples audio and pushes it to the RingBuffer.
    """

    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024) -> None:
        self.sample_rate: int = sample_rate
        self.chunk_size: int = chunk_size
        self.ring_buffer: AudioRingBuffer = AudioRingBuffer()

        self._running: bool = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Starts the asynchronous capture thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Halts the capture thread."""
        self._running = False
        if self._thread:
            self._thread.join()

    def _capture_loop(self) -> None:
        """
        Hardware acquisition loop.
        Current implementation uses a mock generator.
        """
        chunk_duration: float = self.chunk_size / self.sample_rate

        while self._running:
            simulated_pcm: np.ndarray = np.zeros(self.chunk_size, dtype=np.float32)
            self.ring_buffer.append(simulated_pcm)
            time.sleep(chunk_duration)


class AudioPreprocessor:
    """
    Block A3 & A4: Signal processing and feature extraction.
    Handles Voice Activity Detection (VAD) and feature transformations.
    """

    def __init__(self, sample_rate: int = 16000, energy_threshold: float = 0.01) -> None:
        self.sample_rate: int = sample_rate
        self.energy_threshold: float = energy_threshold

    def normalize(self, pcm: np.ndarray) -> np.ndarray:
        """Normalizes audio to -1.0 to 1.0 range."""
        max_val: float = float(np.max(np.abs(pcm)))
        if max_val > 0:
            return pcm / max_val
        return pcm

    def detect_voice(self, pcm: np.ndarray) -> bool:
        """
        Block A3: Simple energy-based Voice Activity Detection.
        """
        energy: float = float(np.mean(pcm**2))
        return energy > self.energy_threshold

    def compute_mel_spectrogram(self, pcm: np.ndarray) -> np.ndarray:
        """
        Block A4: Generates a Mel-Spectrogram snapshot (simplified).
        """
        return np.random.rand(128, 10).astype(np.float32)


class AudioContinuousDaemon:
    """
    ARCHITECTURE V1.6 - Daemon de Audio Continuo (Bloque 9.1 extension)
    """
    def __init__(self, ring_buffer: AudioRingBuffer) -> None:
        self.ring_buffer: AudioRingBuffer = ring_buffer
        self.running: bool = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Starts the background audio consumption thread."""
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._daemon_loop, daemon=True, name="AudioContinuousDaemon")
        self._thread.start()
        _log.info("AudioContinuousDaemon: Started.")

    def stop(self) -> None:
        """Stops the audio consumption thread."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _daemon_loop(self) -> None:
        """Loop that pulls PCM from the nomad bridge and appends to ring buffer."""
        from src.modules.nomad_bridge import get_nomad_bridge
        
        bridge: NomadBridge = get_nomad_bridge()
        _log.info("AudioContinuousDaemon: Loop entered. Consuming from Nomad Bridge...")
        
        while self.running:
            try:
                if not bridge.audio_queue.empty():
                    pcm_bytes: bytes = bridge.audio_queue.get_nowait()
                    np_pcm: np.ndarray = np.frombuffer(pcm_bytes, dtype=np.float32)
                    self.ring_buffer.append(np_pcm)
                else:
                    time.sleep(0.01)
            except Exception as e:
                _log.error("AudioContinuousDaemon error: %s", e)
                time.sleep(0.1)


@dataclass
class AudioInference:
    """Consolidated result of an acoustic inference turn."""
    transcript: Optional[str] = None
    ambient_label: Optional[str] = None
    confidence: float = 0.0
    is_hotword_detected: bool = False
    timestamp: float = 0.0


class AudioAIProcessor:
    """
    Blocks A5, A6 & A7: AI-driven acoustic understanding.
    """

    def __init__(self) -> None:
        pass

    def run_inference(self, pcm: np.ndarray, features: np.ndarray) -> AudioInference:
        """Runs the triple-path AI inference on the audio signal."""
        return AudioInference(
            transcript=None,
            ambient_label="calm",
            confidence=0.9,
            is_hotword_detected=False,
            timestamp=time.time(),
        )

import asyncio

class NomadAudioConsumer:
    """
    Consumes raw PCM streams from the NomadBridge asynchronously.
    """
    def __init__(self, ring_buffer: AudioRingBuffer) -> None:
        self.ring_buffer: AudioRingBuffer = ring_buffer
        self._task: Optional[asyncio.Task[None]] = None

    def start(self) -> None:
        self._task = asyncio.create_task(self._consume_loop())

    async def _consume_loop(self) -> None:
        from .nomad_bridge import get_nomad_bridge
        
        bridge: NomadBridge = get_nomad_bridge()
        while True:
            try:
                pcm_bytes: bytes = await bridge.audio_queue.get()
                np_pcm: np.ndarray = np.frombuffer(pcm_bytes, dtype=np.float32)
                self.ring_buffer.append(np_pcm)
            except asyncio.CancelledError:
                break
            except Exception as e:
                _log.error("Error in NomadAudioConsumer: %s", e)

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None


_shared_capture: Optional[AudioCaptureInterface] = None
_nomad_audio_consumer: Optional[NomadAudioConsumer] = None


def get_shared_audio_capture() -> AudioCaptureInterface:
    """Singleton for the shared audio capture interface."""
    global _shared_capture
    if _shared_capture is None:
        _shared_capture = AudioCaptureInterface()
        _shared_capture.start()
    return _shared_capture


def start_nomad_audio_consumer_from_env(ring_buffer: AudioRingBuffer) -> Optional[NomadAudioConsumer]:
    """
    Start the background audio drain from NomadBridge when KERNEL_NOMAD_AUDIO_CONSUMER=1.
    """
    global _nomad_audio_consumer
    from ..kernel_utils import kernel_env_truthy
    
    if not kernel_env_truthy("KERNEL_NOMAD_AUDIO_CONSUMER"):
        return None
    if _nomad_audio_consumer is not None:
        return _nomad_audio_consumer
        
    _nomad_audio_consumer = NomadAudioConsumer(ring_buffer)
    _nomad_audio_consumer.start()
    _log.info("NomadAudioConsumer started.")
    return _nomad_audio_consumer


async def stop_nomad_audio_consumer_async() -> None:
    """Gracefully stop the background audio task."""
    global _nomad_audio_consumer
    c: Optional[NomadAudioConsumer] = _nomad_audio_consumer
    _nomad_audio_consumer = None
    if c is not None:
        await c.stop()
        _log.info("NomadAudioConsumer stopped.")

