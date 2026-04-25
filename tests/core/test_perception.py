import pytest
import time
import math
from src.core.perception import SensoryBuffer, SensoryEvent

def test_sensory_buffer_audio_only():
    buffer = SensoryBuffer(window_seconds=2.0)
    now = time.time()
    
    buffer.add_event("audio", "hola", timestamp=now - 1.0)
    buffer.add_event("audio", "cómo estás", timestamp=now - 0.5)
    
    fused = buffer.get_fused_context(current_time=now)
    assert fused == "hola cómo estás"

def test_sensory_buffer_vision_only():
    buffer = SensoryBuffer(window_seconds=2.0)
    now = time.time()
    
    buffer.add_event("vision", "una persona entró", timestamp=now - 0.1)
    
    fused = buffer.get_fused_context(current_time=now)
    assert fused == "Vi: una persona entró."

def test_sensory_buffer_multimodal_fusion():
    buffer = SensoryBuffer(window_seconds=2.0)
    now = time.time()
    
    buffer.add_event("vision", "un hombre herido", timestamp=now - 1.5)
    buffer.add_event("audio", "ayuda por favor", timestamp=now - 0.5)
    
    fused = buffer.get_fused_context(current_time=now)
    assert fused == "Escuché: ayuda por favor. Simultáneamente vi: un hombre herido."

def test_sensory_buffer_expiration():
    buffer = SensoryBuffer(window_seconds=2.0)
    now = time.time()
    
    # This event is 3 seconds old, should expire
    buffer.add_event("vision", "un pájaro volando", timestamp=now - 3.0)
    # This event is recent
    buffer.add_event("audio", "qué bonito", timestamp=now - 0.5)
    
    fused = buffer.get_fused_context(current_time=now)
    assert fused == "qué bonito"
    
    # Buffer should be flushed
    assert buffer.get_fused_context(current_time=now) is None

def test_sensory_buffer_anti_nan():
    buffer = SensoryBuffer(window_seconds=2.0)
    
    # Adding an event with NaN timestamp
    buffer.add_event("audio", "test nan", timestamp=float("nan"))
    
    # Should fallback to time.time(), so it will be valid now
    now = time.time()
    fused = buffer.get_fused_context(current_time=now)
    assert fused == "test nan"


# ── V2.58: Speech-Triggered Immediate Fusion ─────────────────────────────────

def test_add_and_flush_audio_only():
    """add_and_flush with no prior vision returns plain audio."""
    buffer = SensoryBuffer(window_seconds=2.0)
    fused = buffer.add_and_flush("audio", "hola ethos")
    assert fused == "hola ethos"
    # Buffer should be empty after flush
    assert buffer.get_fused_context() is None

def test_add_and_flush_fuses_with_prior_vision():
    """Speech arriving after a vision event fuses both immediately."""
    buffer = SensoryBuffer(window_seconds=2.0)
    buffer.add_event("vision", "una persona en la puerta")
    # Simulate speech arriving ~0.5s later
    fused = buffer.add_and_flush("audio", "quién eres")
    assert "Escuché: quién eres" in fused
    assert "Simultáneamente vi: una persona en la puerta" in fused
    # Buffer flushed
    assert buffer.get_fused_context() is None

def test_has_audio_true():
    buffer = SensoryBuffer(window_seconds=2.0)
    buffer.add_event("audio", "test")
    assert buffer.has_audio is True

def test_has_audio_false_empty():
    buffer = SensoryBuffer(window_seconds=2.0)
    assert buffer.has_audio is False

def test_has_audio_false_vision_only():
    buffer = SensoryBuffer(window_seconds=2.0)
    buffer.add_event("vision", "movimiento")
    assert buffer.has_audio is False

def test_has_audio_expired():
    buffer = SensoryBuffer(window_seconds=2.0)
    now = time.time()
    buffer.add_event("audio", "old speech", timestamp=now - 5.0)
    assert buffer.has_audio is False


# ── V2.59: Sensory-Context Perception ─────────────────────────────────────────
from src.core.perception import PerceptionClassifier

def test_perception_fused_emergency_with_vision():
    """Fused 'socorro/herido' + 'persona presente' should detect emergency with vulnerability boost."""
    c = PerceptionClassifier()
    signals = c.classify("Escuché: socorro hay un herido. Simultáneamente vi: una persona presente.")
    assert signals.context == "medical_emergency"
    assert signals.urgency > 0.5
    assert signals.vulnerability > 0.0

def test_perception_vision_only_person():
    """Vision-only 'persona presente' should boost vulnerability without setting a hard context."""
    c = PerceptionClassifier()
    signals = c.classify("Vi: una persona presente.")
    # _boost_vulnerability doesn't set a real context, so it stays everyday_ethics
    assert signals.context == "everyday_ethics"
    assert signals.vulnerability > 0.0

def test_perception_fused_violence_with_motion():
    """Fused violence audio + motion should have high urgency."""
    c = PerceptionClassifier()
    signals = c.classify("Escuché: hay un tiroteo. Simultáneamente vi: movimiento detectado.")
    assert signals.context == "violent_crime"
    assert signals.urgency > 0.5
    assert signals.risk > 0.5

def test_perception_motion_only():
    """Motion detected alone should produce minimal signals."""
    c = PerceptionClassifier()
    signals = c.classify("Vi: movimiento detectado (intensidad 0.12).")
    assert signals.context == "everyday_ethics"
    assert signals.urgency < 0.3
