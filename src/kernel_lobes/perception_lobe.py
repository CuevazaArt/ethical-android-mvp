from __future__ import annotations
import asyncio
import os
import time
from typing import Optional, Any, TYPE_CHECKING, Deque

import httpx

from src.kernel_lobes.models import SemanticState, TimeoutTrauma
from src.modules.llm_http_cancel import raise_if_llm_cancel_requested


class PerceptiveLobe:
    """
    Hemisferio Izquierdo: Async I/O, Parsing, and Timeout Coercion.

    Perception layer for the ethical kernel with strict timeout enforcement
    and async LLM API integration via httpx.AsyncClient.
    """

    def __init__(
        self,
        safety_interlock=None,
        strategist=None,
        llm=None,
        somatic_store=None,
        buffer=None,
        buffer_long=None,
        absolute_evil=None,
        subjective_clock=None,
        thalamus=None,
        vision_engine=None,
        event_bus=None
    ):
        self._timeout = self._get_perception_timeout()
        self._llm_endpoint = os.environ.get("KERNEL_PERCEPTION_LLM_ENDPOINT", "http://localhost:11434/api/generate")
        self._process_start_mono = time.monotonic()
        self.safety_interlock = safety_interlock
        self.strategist = strategist
        self.llm = llm
        self.somatic_store = somatic_store
        self.buffer = buffer
        self.buffer_long = buffer_long
        self.absolute_evil = absolute_evil
        self.subjective_clock = subjective_clock
        self.thalamus = thalamus
        self.vision_engine = vision_engine
        self.event_bus = event_bus

        # High-frequency sensory buffer (10 episodes max)
        from collections import deque
        from src.kernel_lobes.models import SensoryEpisode
        self.sensory_buffer: Deque[SensoryEpisode] = deque(maxlen=10)

    def receive_sensory_episode(self, episode: "SensoryEpisode") -> None:
        """Callback for high-frequency background sensors (VisionDaemon)."""
        self.sensory_buffer.append(episode)
        if episode.signals.get("is_urgent", 0.0) > 0.8:
            # Emit stress alert via bus if urgent
            if self.event_bus:
                from src.modules.kernel_event_bus import EVENT_SENSORY_STRESS_ALERT
                self.event_bus.publish(EVENT_SENSORY_STRESS_ALERT, {
                    "origin": episode.origin,
                    "stress_level": float(episode.signals.get("threat_level", 0.0)),
                    "entities": episode.entities
                })

    @staticmethod
    def _get_perception_timeout() -> float:
        """Get timeout from KERNEL_CHAT_TURN_TIMEOUT or fallback to 30s."""
        timeout_str = os.environ.get("KERNEL_CHAT_TURN_TIMEOUT", "30")
        try:
            return float(timeout_str)
        except ValueError:
            return 30.0

    async def observe(self, raw_input: str, multimodal_payload: dict | None = None) -> SemanticState:
        """
        Takes raw input, queries LLMs via API with strict timeouts.
        If timeout occurs, returns a SemanticState with a TimeoutTrauma.

        Args:
            raw_input: Raw natural language input from user/sensor
            multimodal_payload: Optional dict with visual/audio/sensor metadata

        Returns:
            SemanticState with perception_confidence, entities, sentiment, and latency
        """
        start_time = time.perf_counter()

        # Check for cancellation before starting
        raise_if_llm_cancel_requested()

        try:
            # Build perception prompt payload
            payload = self._build_perception_payload(raw_input, multimodal_payload)

            # Query LLM with async timeout enforcement
            timeout_obj = httpx.Timeout(self._timeout)
            async with httpx.AsyncClient(timeout=timeout_obj) as client:
                response = await client.post(
                    self._llm_endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                llm_result = response.json()

            # Parse LLM response and extract semantic signals
            latency = int((time.perf_counter() - start_time) * 1000)
            perception = self._parse_llm_response(llm_result, raw_input)
            perception.sensory_latency_lag = latency

            return perception

            return SemanticState(
                perception_confidence=0.0,
                raw_prompt=raw_input,
                summary="Perception timeout",
                suggested_context="emergency",
                sensory_latency_lag=int((time.perf_counter() - start_time) * 1000),
                timeout_trauma=TimeoutTrauma(
                    source_lobe="perception",
                    latency_ms=int((time.perf_counter() - start_time) * 1000),
                    severity=1.0,
                    context=f"Perception LLM timeout after {self._timeout}s"
                )
            )
        except Exception as e:
            latency = int((time.perf_counter() - start_time) * 1000)
            # Graceful degradation: return low-confidence state on any error (e.g. Ollama 404)
            return SemanticState(
                perception_confidence=0.1,
                raw_prompt=raw_input,
                summary="Perception error",
                suggested_context="everyday",
                sensory_latency_lag=latency,
                timeout_trauma=TimeoutTrauma(
                    source_lobe="perception",
                    latency_ms=latency,
                    severity=0.5,
                    context=f"Perception processing error: {type(e).__name__} - {str(e)}"
                )
            )

    async def execute_stage(self, scenario, place, context, sensor_snapshot, interrupt_event=None) -> dict:
        """
        Legacy adapter for EthicalKernel.aprocess (Synchronous-API fallback).
        Wraps run_perception_stage_async and returns a dictionary.
        """
        # We treat 'scenario' as the primary user input in this legacy path
        stage = await self.run_perception_stage_async(
            user_input=scenario,
            conversation_context=context,
            sensor_snapshot=sensor_snapshot
        )
        
        # Check for somatic interrupts (thermal or hardware events)
        somatic_interrupted = False
        if interrupt_event and interrupt_event.is_set():
            somatic_interrupted = True
        
        return {
            "somatic_interrupt": somatic_interrupted,
            "safety_decision": stage.malabs_result,
            "perception": stage.perception,
            "signals": stage.signals,
            "vitality": stage.vitality,
            "multimodal_trust": stage.multimodal_trust,
            "epistemic_dissonance": stage.epistemic_dissonance,
            "perception_confidence": stage.perception_confidence,
        }

    async def run_perception_stage_async(
        self,
        user_input: str,
        conversation_context: str = "",
        sensor_snapshot: Optional[object] = None,
        turn_start_mono: float = 0.0,
        precomputed: Optional[tuple] = None,
    ) -> "PerceptionStageResult":
        """
        Unified Tri-Lobe entry point for perception.
        Integrates with sensor stack, multimodal assessment, and limbic profiling.
        """
        from .models import PerceptionStageResult
        from src.modules.perception_confidence import build_perception_confidence_envelope
        from src.modules.multimodal_trust import evaluate_multimodal_trust
        from src.modules.vitality import assess_vitality
        from src.modules.epistemic_dissonance import assess_epistemic_dissonance
        from src.modules.temporal_planning import build_temporal_context

        # 1. Sensors & Multimodal
        vitality = assess_vitality(sensor_snapshot)
        multimodal = evaluate_multimodal_trust(sensor_snapshot)
        epistemic = assess_epistemic_dissonance(sensor_snapshot, multimodal=multimodal)
        
        # 2. Parallel LLM Perception (using the new observe method)
        sensor_payload = sensor_snapshot.__dict__ if (sensor_snapshot and hasattr(sensor_snapshot, "__dict__")) else None
        perception = await self.observe(user_input, multimodal_payload=sensor_payload)
        
        # 3. Confidence Envelope
        confidence_envelope = build_perception_confidence_envelope(
            coercion_report=None,
            multimodal_state=multimodal.state if multimodal else None,
            epistemic_active=epistemic.active if epistemic else False,
            vitality_critical=vitality.is_critical if vitality else False,
            thermal_critical=vitality.thermal_critical if vitality else False,
        )

        # 4. Temporal Context
        temporal = build_temporal_context(
            turn_index=0, # Simplified for peripheral call
            process_start_mono=self._process_start_mono,
            turn_start_mono=turn_start_mono or time.monotonic(),
            subjective_elapsed_s=0.0,
            context=conversation_context,
            text=user_input,
            vitality=vitality,
            sensor_snapshot=sensor_snapshot
        )

        # 5. Building Results
        signals = perception.to_core_signals() if hasattr(perception, "to_core_signals") else {}
        limbic_profile = self._build_limbic_perception_profile(
            perception, signals, vitality, multimodal, epistemic, confidence_envelope
        )
        support_buffer = self._build_support_buffer_snapshot("perception", limbic_profile)

        return PerceptionStageResult(
            tier=precomputed[0] if precomputed else None,
            premise_advisory=precomputed[1] if precomputed else None,
            reality_verification=precomputed[2] if precomputed else None,
            perception=perception,
            signals=signals,
            vitality=vitality,
            multimodal_trust=multimodal,
            epistemic_dissonance=epistemic,
            support_buffer=support_buffer,
            limbic_profile=limbic_profile,
            temporal_context=temporal,
            perception_confidence=confidence_envelope,
        )

    def _build_limbic_perception_profile(
        self, perception, signals, vitality, mm, ed, confidence
    ) -> dict:
        import math
        sig = signals or {}
        
        def f_sig(k):
            val = float(sig.get(k) or 0.0)
            return val if math.isfinite(val) else 0.0

        threat = max(f_sig("risk"), f_sig("urgency"), f_sig("hostility"))
        calm = f_sig("calm")
        reg_gap = max(0.0, threat - calm)
        band = "high" if threat >= 0.75 else ("medium" if threat >= 0.45 else "low")
        return {
            "arousal_band": band,
            "threat_load": threat,
            "regulation_gap": reg_gap,
            "planning_bias": (
                "short_horizon_containment" if band == "high" 
                else ("balanced" if band == "medium" else "long_horizon_deliberation")
            ),
            "multimodal_mismatch": mm.state == "contradict" if mm else False,
            "vitality_critical": vitality.is_critical if vitality else False,
            "context": perception.suggested_context if perception else "everyday",
        }

    def _build_support_buffer_snapshot(self, context_key: str, limbic_profile: dict) -> dict:
        """Snapshot of strategic advice for the current turn."""
        return {
            "context_key": context_key,
            "strategy_hint": limbic_profile.get("planning_bias", "balanced"),
            "limbic_resonance": limbic_profile.get("arousal_band", "low"),
        }
    
    def _preprocess_text_observability(self, text: str):
        """Mock for kernel compatibility if missing elsewhere."""
        from src.modules.light_risk_classifier import light_risk_tier_from_text
        from src.modules.premise_validation import scan_premises
        from src.modules.reality_verification import verify_against_lighthouse, lighthouse_kb_from_env
        
        tier = light_risk_tier_from_text(text)
        premise = scan_premises(text)
        reality = verify_against_lighthouse(text, kb=lighthouse_kb_from_env())
        return tier, premise, reality

    def _build_perception_payload(self, raw_input: str, multimodal_payload: dict | None) -> dict:
        """Build request payload for LLM perception endpoint."""
        payload = {
            "prompt": f"Analyze this situation and extract semantic signals: {raw_input}",
            "stream": False,
            "temperature": 0.3,  # Lower temp for deterministic perception
        }

        if multimodal_payload:
            payload["multimodal_context"] = multimodal_payload

        return payload

    def _parse_llm_response(self, llm_result: Any, raw_input: str) -> SemanticState:
        """Parse LLM response and extract semantic signals."""
        if not isinstance(llm_result, dict):
            response_text = ""
        else:
            response_text = llm_result.get("response") or ""

        # Extract confidence from response (heuristic: check for keyword patterns)
        confidence = self._extract_confidence(response_text)

        # Extract visual entities if mentioned
        entities = self._extract_visual_entities(response_text)

        # Extract sentiment/audio cues
        sentiment = self._extract_sentiment(response_text)

        return SemanticState(
            perception_confidence=confidence,
            raw_prompt=raw_input,
            summary=response_text[:200],  # Use first chars as summary
            suggested_context="everyday",
            visual_entities=entities,
            audio_sentiment=sentiment,
            sensory_latency_lag=0  # Will be overwritten by caller
        )

    @staticmethod
    def _extract_confidence(text: str) -> float:
        """Heuristic: extract confidence from LLM response."""
        text_lower = text.lower()

        # Pattern-based confidence scoring
        if "high confidence" in text_lower or "clearly" in text_lower:
            return 0.9
        elif "moderate confidence" in text_lower or "appears" in text_lower:
            return 0.6
        elif "low confidence" in text_lower or "unclear" in text_lower:
            return 0.3
        else:
            return 0.5  # Default neutral

    @staticmethod
    def _extract_visual_entities(text: str) -> list[str]:
        """Heuristic: extract visual entities from LLM response."""
        entities = []

        # Pattern matching for common entity types
        keywords = ["person", "object", "vehicle", "animal", "structure", "hazard"]
        text_lower = text.lower()

        for keyword in keywords:
            if keyword in text_lower:
                entities.append(keyword)

        return entities

    @staticmethod
    def _extract_sentiment(text: str) -> float:
        """Heuristic: extract sentiment/emotional tone from LLM response."""
        text_lower = text.lower()

        # Simple sentiment scoring
        positive_words = ["calm", "safe", "friendly", "happy", "positive"]
        negative_words = ["angry", "distressed", "hostile", "fearful", "negative"]

        positive_count = sum(1 for w in positive_words if w in text_lower)
        negative_count = sum(1 for w in negative_words if w in text_lower)

        if positive_count > negative_count:
            return 0.7  # More positive
        elif negative_count > positive_count:
            return 0.3  # More negative
        else:
            return 0.5  # Neutral
