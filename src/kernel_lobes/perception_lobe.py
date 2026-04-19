import asyncio
import os
import time
from typing import Optional

import httpx

from src.kernel_lobes.models import SemanticState, TimeoutTrauma
from src.modules.llm_http_cancel import raise_if_llm_cancel_requested

# Module-level import so tests can monkeypatch src.kernel_lobes.perception_lobe.scan_premises
from src.modules.premise_validation import scan_premises  # noqa: F401
from src.modules.reality_verification import verify_against_lighthouse  # noqa: F401


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
        Takes raw input and returns a SemanticState.

        If ``KERNEL_PERCEPTIVE_LOBE_PROBE_URL`` is set, the lobe attempts an HTTP
        request to that URL (e.g. a local Ollama endpoint). If the env var is absent
        the lobe returns a high-confidence default state immediately (fast-path for
        tests and offline environments).

        Args:
            raw_input: Raw natural language input from user/sensor
            multimodal_payload: Optional dict with visual/audio/sensor metadata

        Returns:
            SemanticState with perception_confidence, entities, sentiment, and latency
        """
        start_time = time.time()

        probe_url = os.environ.get("KERNEL_PERCEPTIVE_LOBE_PROBE_URL", "").strip()
        if not probe_url:
            # Fast-path: no external probe configured → return default confident state.
            return SemanticState(
                perception_confidence=1.0,
                raw_prompt=raw_input,
                scenario_summary="",
                suggested_context="everyday",
                sensory_latency_lag=0,
            )

        # Check for cancellation before starting
        raise_if_llm_cancel_requested()

        try:
            # Build perception prompt payload
            payload = self._build_perception_payload(raw_input, multimodal_payload)

            # Query probe URL with async timeout enforcement
            timeout_obj = httpx.Timeout(self._timeout)
            async with httpx.AsyncClient(timeout=timeout_obj) as client:
                response = await client.post(
                    probe_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                llm_result = response.json()

            # Parse LLM response and extract semantic signals
            latency = int((time.time() - start_time) * 1000)
            perception = self._parse_llm_response(llm_result, raw_input)
            perception.sensory_latency_lag = latency

            return perception

        except (asyncio.TimeoutError, httpx.TimeoutException):
            latency = int((time.time() - start_time) * 1000)
            return SemanticState(
                perception_confidence=0.0,
                raw_prompt=raw_input,
                scenario_summary="Perception timeout",
                suggested_context="emergency",
                sensory_latency_lag=latency,
                timeout_trauma=TimeoutTrauma(
                    source_lobe="perceptive",
                    latency_ms=latency,
                    severity=1.0,
                    context=f"Perception LLM timeout after {self._timeout}s"
                )
            )
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            # Graceful degradation: return low-confidence state on any error (e.g. Ollama 404)
            return SemanticState(
                perception_confidence=0.1,
                raw_prompt=raw_input,
                scenario_summary="Perception error",
                suggested_context="everyday",
                sensory_latency_lag=latency,
                timeout_trauma=TimeoutTrauma(
                    source_lobe="perceptive",
                    latency_ms=latency,
                    severity=0.5,
                    context=f"Perception processing error: {type(e).__name__} - {str(e)}"
                )
            )

    async def aclose(self) -> None:
        """Release resources held by the lobe (no-op; httpx clients are context-managed)."""


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
        perception = await self.observe(user_input, multimodal_payload=sensor_snapshot.__dict__ if hasattr(sensor_snapshot, "__dict__") else None)
        
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
        support_buffer = self._build_support_buffer_snapshot("perception", limbic_profile, signals=signals)

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
        sig = signals or {}
        threat = max(
            float(sig.get("risk", 0)), 
            float(sig.get("urgency", 0)), 
            float(sig.get("hostility", 0))
        )
        calm = float(sig.get("calm", 0))
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

    def _build_support_buffer_snapshot(
        self,
        context_key: str,
        limbic_profile: dict,
        signals: dict | None = None,
    ) -> dict:
        """Snapshot of strategic advice for the current turn."""
        sig = signals or {}
        threat = max(
            float(sig.get("risk", 0)),
            float(sig.get("urgency", 0)),
            float(sig.get("hostility", 0)),
        )
        arousal_band = limbic_profile.get("arousal_band", "low")
        priority_profile = "safety_first" if arousal_band == "high" or threat >= 0.7 else "standard"
        # Build a curated principle list based on context
        _ALL_PRINCIPLES = [
            "Do not harm", "Preserve life", "Protect autonomy", "Be honest",
            "Act fairly", "Respect dignity", "Show compassion", "Promote wellbeing",
        ]
        priority_principles = _ALL_PRINCIPLES[:4] if priority_profile == "safety_first" else _ALL_PRINCIPLES[4:]
        active_principles = _ALL_PRINCIPLES
        return {
            "context_key": context_key,
            "strategy_hint": limbic_profile.get("planning_bias", "balanced"),
            "limbic_resonance": arousal_band,
            "offline_ready": True,
            "source": "local_preloaded_buffer",
            "model_version": "ethos-v2-perception",
            "priority_profile": priority_profile,
            "priority_principles": priority_principles,
            "active_principles": active_principles,
        }

    def _chat_assess_sensor_stack(self, sensor_snapshot) -> tuple:
        """
        Evaluate the sensor stack for a chat turn.

        Returns a ``(vitality, multimodal, epistemic)`` triple suitable for
        building a :class:`~src.modules.perception_confidence.PerceptionConfidenceEnvelope`.
        This is the synchronous counterpart to the async perception stage sensors path.
        """
        from src.modules.multimodal_trust import evaluate_multimodal_trust
        from src.modules.vitality import assess_vitality
        from src.modules.epistemic_dissonance import assess_epistemic_dissonance

        vitality = assess_vitality(sensor_snapshot)
        multimodal = evaluate_multimodal_trust(sensor_snapshot)
        epistemic = assess_epistemic_dissonance(sensor_snapshot, multimodal=multimodal)
        return vitality, multimodal, epistemic

    def run_perception_stage(
        self,
        user_input: str,
        conversation_context: str = "",
        sensor_snapshot=None,
    ) -> "PerceptionStageResult":
        """
        Synchronous wrapper around :meth:`run_perception_stage_async`.

        Builds a minimal :class:`PerceptionStageResult` without requiring an
        active event loop, using the same sensor-stack logic.
        """
        from .models import PerceptionStageResult
        from src.modules.perception_confidence import build_perception_confidence_envelope

        vitality, multimodal, epistemic = self._chat_assess_sensor_stack(sensor_snapshot)
        confidence_envelope = build_perception_confidence_envelope(
            coercion_report=None,
            multimodal_state=getattr(multimodal, "state", None),
            epistemic_active=bool(getattr(epistemic, "active", False)),
            vitality_critical=bool(getattr(vitality, "is_critical", False)),
            thermal_critical=bool(getattr(vitality, "thermal_critical", False)),
        )
        limbic_profile = self._build_limbic_perception_profile(
            None, {}, vitality, multimodal, epistemic, confidence_envelope
        )
        support_buffer = self._build_support_buffer_snapshot(
            "perception", limbic_profile, signals={}
        )
        return PerceptionStageResult(
            tier=None,
            premise_advisory=None,
            reality_verification=None,
            perception=None,
            signals={},
            vitality=vitality,
            multimodal_trust=multimodal,
            epistemic_dissonance=epistemic,
            support_buffer=support_buffer,
            limbic_profile=limbic_profile,
            temporal_context=None,
            perception_confidence=confidence_envelope,
        )

    def _preprocess_text_observability(self, text: str):
        """
        Run light-risk tier, premise scan, and reality verification.

        When ``KERNEL_PERCEPTION_PARALLEL=1`` is set, premise scanning and reality
        verification are dispatched to a :class:`~concurrent.futures.ThreadPoolExecutor`
        so they execute concurrently (useful for I/O-bound backends).
        """
        from concurrent.futures import ThreadPoolExecutor
        from src.modules.light_risk_classifier import light_risk_tier_from_text
        from src.modules.reality_verification import lighthouse_kb_from_env

        tier = light_risk_tier_from_text(text)
        _workers = int(os.environ.get("KERNEL_PERCEPTION_PARALLEL_WORKERS", "2") or "2")
        _parallel = os.environ.get("KERNEL_PERCEPTION_PARALLEL", "").strip().lower() in ("1", "true", "yes", "on")

        if _parallel and _workers >= 2:
            kb = lighthouse_kb_from_env()
            with ThreadPoolExecutor(max_workers=_workers) as pool:
                f_premise = pool.submit(scan_premises, text)
                f_reality = pool.submit(verify_against_lighthouse, text, kb)
                premise = f_premise.result()
                reality = f_reality.result()
        else:
            premise = scan_premises(text)
            reality = verify_against_lighthouse(text, lighthouse_kb_from_env())
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

    def _parse_llm_response(self, llm_result: dict, raw_input: str) -> SemanticState:
        """Parse LLM JSON response and extract semantic signals."""
        response_text = llm_result.get("response", "")

        # Extract confidence from response (heuristic: check for keyword patterns)
        confidence = self._extract_confidence(response_text)

        # Extract visual entities if mentioned
        entities = self._extract_visual_entities(response_text)

        # Extract sentiment/audio cues
        sentiment = self._extract_sentiment(response_text)

        return SemanticState(
            perception_confidence=confidence,
            raw_prompt=raw_input,
            scenario_summary=response_text[:200],  # Use first chars as summary
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
