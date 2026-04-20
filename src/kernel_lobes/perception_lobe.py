from __future__ import annotations
import asyncio
import os
import threading
import time
import logging
from typing import Optional, Any, TYPE_CHECKING, Deque
from src.kernel_lobes.models import (
    PerceptionStageResult,
    SensoryEpisode,
    SensorySpike,
    SemanticState,
    LimbicTensionAlert,
    CognitivePulse,
    MotorCommandDispatch,
)
if TYPE_CHECKING:
    from src.nervous_system.corpus_callosum import CorpusCallosum
from src.kernel_utils import perception_parallel_workers
from src.modules.epistemic_dissonance import assess_epistemic_dissonance
from src.modules.light_risk_classifier import (
    light_risk_classifier_enabled,
    light_risk_tier_from_text,
)
from src.modules.multimodal_trust import evaluate_multimodal_trust
from src.modules.perception_confidence import build_perception_confidence_envelope
from src.modules.premise_validation import scan_premises
from src.modules.reality_verification import (
    lighthouse_kb_from_env,
    verify_against_lighthouse,
)
from src.modules.sensor_contracts import merge_sensor_hints_into_signals
from src.modules.somatic_markers import apply_somatic_nudges
from src.modules.temporal_planning import build_temporal_context
from src.modules.vitality import assess_vitality

if TYPE_CHECKING:
    from src.modules.absolute_evil import AbsoluteEvilDetector
    from src.modules.buffer import PreloadedBuffer
    from src.modules.llm_layer import LLMModule
    from src.modules.safety_interlock import SafetyInterlock
    from src.modules.sensor_contracts import SensorSnapshot
    from src.modules.somatic_markers import SomaticMarkerStore
    from src.modules.strategy_engine import ExecutiveStrategist

_log = logging.getLogger(__name__)


def _vision_continuous_daemon_enabled() -> bool:
    """Module 9.1 — default on; set ``KERNEL_VISION_CONTINUOUS_DAEMON=0`` to skip the background thread."""

    v = os.environ.get("KERNEL_VISION_CONTINUOUS_DAEMON", "1").strip().lower()
    return v not in ("0", "false", "off", "no")

# Module-level import so tests can monkeypatch src.kernel_lobes.perception_lobe.scan_premises
from src.modules.premise_validation import scan_premises  # noqa: F401
from src.modules.reality_verification import verify_against_lighthouse  # noqa: F401


class PerceptiveLobe:
    """
    Subsystem for Safety Interlocks, Strategic Ingestion, and Multimodal Perception.
    
    Acts as the 'Left Hemisphere' of the kernel, handling I/O and sensory filtering.
    """
    def __init__(
        self,
        safety_interlock: "SafetyInterlock",
        strategist: "ExecutiveStrategist",
        llm: "LLMModule",
        somatic_store: "SomaticMarkerStore",
        buffer: "PreloadedBuffer",
        absolute_evil: "AbsoluteEvilDetector",
        subjective_clock: Any,  # SubjectiveClock
        thalamus: Any | None = None,
        vision_engine: Any | None = None,
        bus: Optional[CorpusCallosum] = None,
    ):
        self._timeout = self._get_perception_timeout()
        self._llm_endpoint = os.environ.get("KERNEL_PERCEPTION_LLM_ENDPOINT", "http://localhost:11434/api/generate")
        self._process_start_mono = time.monotonic()
        self.safety_interlock = safety_interlock
        self.strategist = strategist
        self.llm = llm
        self.somatic_store = somatic_store
        self.buffer = buffer
        self.absolute_evil = absolute_evil
        self.subjective_clock = subjective_clock
        self.thalamus = thalamus
        self.vision_engine = vision_engine
        self.bus = bus

        # Suspensión asíncrona: El PerceptiveLobe (Córtex Sensorial) actúa como
        # receptor de spikes de alto nivel (texto) y emisor de spikes brutos (sensores).
        if self.bus:
            self.bus.subscribe(SensorySpike, self._on_sensory_spike_received)


        # High-frequency sensory buffer (10 episodes max)
        from collections import deque
        from src.kernel_lobes.models import SensoryEpisode
        self.sensory_buffer: Deque[SensoryEpisode] = deque(maxlen=10)

    def receive_sensory_episode(self, episode: "SensoryEpisode") -> None:
        """Callback for high-frequency background sensors (VisionDaemon)."""
        self.sensory_buffer.append(episode)
        
        # Fase A: Publicar SensorySpike en el bus asíncrono
        if self.bus:
            from src.kernel_lobes.models import SensorySpike
            spike = SensorySpike(
                payload={"origin": episode.origin, "entities": episode.vision_entities, "threat_level": episode.threat_load},
                priority=1,
                origin_lobe="sensory_cortex_raw" # Tag different origin to avoid infinite loop
            )
            asyncio.create_task(self.bus.publish(spike))
            
        if episode.signals.get("is_urgent", 0.0) > 0.8:
            # Emit stress alert via bus if urgent
            if self.bus:
                from src.kernel_lobes.models import LimbicTensionAlert
                alert = LimbicTensionAlert(
                    priority=0, # ALTA PRIORIDAD (Arco Reflejo)
                    tension_load=float(episode.signals.get("threat_level", 0.0)),
                    metadata={"origin": episode.origin, "entities": episode.vision_entities}
                )
                asyncio.create_task(self.bus.publish(alert))

    async def _on_sensory_spike_received(self, spike: SensorySpike) -> None:
        """
        Nervous System Hook: Process a sensory spike asynchronously.
        Only process if it contains text (high-level input).
        """
        if spike.origin_lobe == "sensory_cortex_raw":
            return # Skip our own raw spikes

        text: str = (spike.payload or {}).get("text", "")
        if not text:
            return

        _log.info(f"Córtex Sensorial: Recibido impulso de texto {spike.pulse_id}. Procesando observación...")
        
        # Swarm Rule 3: Latency Telemetry
        t0 = time.perf_counter()
        state = await self.observe(text)
        latency_ms = (time.perf_counter() - t0) * 1000
        
        # Publicar el estado semántico de vuelta al bus para que otros órganos lo vean
        if self.bus:
            _log.info(f"Córtex Sensorial: Observación completa (latencia: {latency_ms:.2f}ms) para {spike.pulse_id}. Notificando sistema cognitivo...")
            pulse = CognitivePulse(
                origin_lobe="sensory_cortex",
                state_ref=state,
                ref_pulse_id=spike.pulse_id # Trace back to original stimulus
            )
            asyncio.create_task(self.bus.publish(pulse))



    @staticmethod
    def _get_perception_timeout() -> float:
        """Timeout for the outer httpx call (KERNEL_CHAT_TURN_TIMEOUT, default 30 s)."""
        timeout_str = os.environ.get("KERNEL_CHAT_TURN_TIMEOUT", "30")
        try:
            v = float(timeout_str)
            return v if v > 0 else 30.0
        except (ValueError, TypeError):
            return 30.0

    @staticmethod
    def _get_limbic_perception_timeout() -> float | None:
        """
        Hard asyncio timeout that caps the full ``run_perception_stage_async`` call
        (LLM + sensor stack).  Prevents limbic latency from stalling Nomad text turns.

        Env: ``KERNEL_LIMBIC_PERCEPTION_TIMEOUT`` seconds (default 12 s).
        Set to 0 to disable.
        """
        raw = os.environ.get("KERNEL_LIMBIC_PERCEPTION_TIMEOUT", "12").strip()
        try:
            v = float(raw)
            import math
            if not math.isfinite(v):
                return 12.0
            return v if v > 0 else None
        except (ValueError, TypeError):
            return 12.0

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
        start_time = time.perf_counter()

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
            latency = int((time.perf_counter() - start_time) * 1000)
            perception = self._parse_llm_response(llm_result, raw_input)
            perception.sensory_latency_lag = latency

            return perception
        except (asyncio.TimeoutError, httpx.TimeoutException, httpx.ReadTimeout):
            latency = int((time.perf_counter() - start_time) * 1000)
            return SemanticState(
                perception_confidence=0.0,
                raw_prompt=raw_input,
                summary="Perception timeout",
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
            latency = int((time.perf_counter() - start_time) * 1000)
            # Graceful degradation: return low-confidence state on any error (e.g. Ollama 404)
            return SemanticState(
                perception_confidence=0.1,
                raw_prompt=raw_input,
                summary="Perception error",
                suggested_context="everyday",
                sensory_latency_lag=latency,
                timeout_trauma=TimeoutTrauma(
                    source_lobe="perceptive",
                    latency_ms=latency,
                    severity=0.5,
                    context=f"Perception processing error: {type(e).__name__} - {str(e)}"
                )
            )
            self.vision_daemon.start()
        else:
            self.vision_daemon = None

    async def aclose(self) -> None:
        """Release resources held by the lobe (no-op; httpx clients are context-managed)."""


    async def execute_stage(self, scenario, place, context, sensor_snapshot, interrupt_event=None) -> dict:
        """
        STAGE 0: Perception, Safety and Strategic Ingestion.
        """
        # 0.0 Somatic Overrides (Vertical Increment)
        if interrupt_event and interrupt_event.is_set():
            return {
                "safety_decision": None,
                "mission_updated": False,
                "somatic_interrupt": True
            }

        sensory_stress = self._calculate_sensory_stress()
        if sensory_stress > 0.7:
            _log.warning(
                "PerceptiveLobe: High sustained sensory stress! (%.2f)",
                sensory_stress,
            )

        if self.thalamus and sensor_snapshot:
            ori = getattr(sensor_snapshot, "orientation", None)
            if ori:
                self.thalamus.ingest_telemetry({"orientation": ori})
            rms = getattr(sensor_snapshot, "rms_audio", None)
            if rms is not None:
                self.thalamus.ingest_audio_signal(float(rms))

        # 0.1 Check Safety
        safety_dec = self.safety_interlock.evaluate(scenario, place, context)
        
        # 0.2 Strategic Ingestion
        if sensor_snapshot:
            if getattr(sensor_snapshot, "external_mission_title", None):
                from src.modules.strategy_engine import MissionOrigin
                self.strategist.create_mission(
                    title=sensor_snapshot.external_mission_title,
                    origin=MissionOrigin.OWNER,
                    steps=sensor_snapshot.external_mission_steps or [],
                    priority=sensor_snapshot.external_mission_priority or 0.6,
                )
            self.strategist.ingest_sensors(sensor_snapshot)

        return {
            "somatic_interrupt": somatic_interrupted,
            "safety_decision": stage.malabs_result,
            "perception": stage.perception,
            "signals": stage.signals,
            "vitality": stage.vitality,
            "multimodal_trust": stage.multimodal_trust,
            "epistemic_dissonance": stage.epistemic_dissonance,
            "perception_confidence": stage.perception_confidence,
            "generative_candidates": stage.perception.generative_candidates if hasattr(stage.perception, "generative_candidates") else [],
        }

    async def run_perception_stage_async(
        self,
        text: str,
        *,
        conversation_context: str = "",
        sensor_snapshot: Optional[object] = None,
        turn_start_mono: float = 0.0,
        precomputed: Optional[tuple] = None,
    ) -> "PerceptionStageResult":
        """
        Unified Tri-Lobe entry point for perception.
        Integrates with sensor stack, multimodal assessment, and limbic profiling.

        A hard asyncio timeout (KERNEL_LIMBIC_PERCEPTION_TIMEOUT, default 12 s) caps
        the entire stage so limbic latency never stalls Nomad text turns.  On timeout
        the stage gracefully degrades: sensor signals are still computed; only the LLM
        observation is replaced by a low-confidence SemanticState.
        """
        lp_timeout = self._get_limbic_perception_timeout()
        try:
            result = await asyncio.wait_for(
                self._run_perception_stage_inner(
                    user_input, conversation_context, sensor_snapshot, turn_start_mono, precomputed
                ),
                timeout=lp_timeout,
            )
        except asyncio.TimeoutError:
            latency_ms = int((time.perf_counter()) * 1000)  # approximate
            import logging as _logging
            _logging.getLogger(__name__).warning(
                "PerceptionLobe: stage timeout after %.1fs (KERNEL_LIMBIC_PERCEPTION_TIMEOUT); "
                "falling back to degraded perception.",
                lp_timeout,
            )
            result = await self._run_perception_stage_degraded(
                user_input, sensor_snapshot, precomputed, latency_ms
            )
        return result

    async def _run_perception_stage_inner(
        self,
        user_input: str,
        conversation_context: str = "",
        sensor_snapshot: Optional[object] = None,
        turn_start_mono: float = 0.0,
        precomputed: Optional[tuple] = None,
    ) -> "PerceptionStageResult":
        """Core perception stage — called by run_perception_stage_async under wait_for."""
        from .models import PerceptionStageResult
        from src.modules.perception_confidence import build_perception_confidence_envelope
        from src.modules.multimodal_trust import evaluate_multimodal_trust
        from src.modules.vitality import assess_vitality
        from src.modules.epistemic_dissonance import assess_epistemic_dissonance
        from src.modules.temporal_planning import build_temporal_context

        if precomputed is None:
            tier, premise, reality = self._preprocess_text_observability(text)
        else:
            tier, premise, reality = precomputed

        bootstrap_support = self._build_support_buffer_snapshot("everyday")
        support_line = self._support_buffer_context_line(bootstrap_support)
        merged_ctx = ((conversation_context or "").strip() + "\n" + support_line).strip()
        
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
            "arousal_band": band, "threat_load": threat, "regulation_gap": reg_gap,
            "planning_bias": "short_horizon_containment" if band == "high" else ("balanced" if band == "medium" else "long_horizon_deliberation"),
            "multimodal_mismatch": mm.state == "contradict" if mm else False,
            "vitality_critical": vitality.is_critical if vitality else False,
            "context": perception.suggested_context if perception else "everyday"
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

    async def _run_perception_stage_degraded(
        self,
        user_input: str,
        sensor_snapshot: Optional[object],
        precomputed: Optional[tuple],
        latency_ms: int,
    ) -> "PerceptionStageResult":
        """
        Fallback perception stage used when KERNEL_LIMBIC_PERCEPTION_TIMEOUT is exceeded.

        Sensor signals are still computed (fast, local).  The LLM observation is
        replaced by a low-confidence SemanticState so the kernel can still respond
        with reduced fidelity rather than hanging the turn.
        """
        from .models import PerceptionStageResult, SemanticState, TimeoutTrauma
        from src.modules.perception_confidence import build_perception_confidence_envelope
        from src.modules.multimodal_trust import evaluate_multimodal_trust
        from src.modules.vitality import assess_vitality
        from src.modules.epistemic_dissonance import assess_epistemic_dissonance

        vitality = assess_vitality(sensor_snapshot)
        multimodal = evaluate_multimodal_trust(sensor_snapshot)
        epistemic = assess_epistemic_dissonance(sensor_snapshot, multimodal=multimodal)

        degraded_perception = SemanticState(
            perception_confidence=0.1,
            raw_prompt=user_input,
            summary="Limbic perception timeout — degraded response",
            suggested_context="everyday",
            sensory_latency_lag=latency_ms,
            timeout_trauma=TimeoutTrauma(
                source_lobe="limbic_perception_stage",
                latency_ms=latency_ms,
                severity=0.5,
                context="KERNEL_LIMBIC_PERCEPTION_TIMEOUT exceeded; graceful degradation active",
            ),
        )

        confidence_envelope = build_perception_confidence_envelope(
            coercion_report=None,
            multimodal_state=multimodal.state if multimodal else None,
            epistemic_active=epistemic.active if epistemic else False,
            vitality_critical=vitality.is_critical if vitality else False,
            thermal_critical=vitality.thermal_critical if vitality else False,
        )

        limbic_profile = self._build_limbic_perception_profile(
            degraded_perception, {}, vitality, multimodal, epistemic, confidence_envelope
        )
        support_buffer = self._build_support_buffer_snapshot("perception_degraded", limbic_profile)

        return PerceptionStageResult(
            tier=precomputed[0] if precomputed else None,
            premise_advisory=precomputed[1] if precomputed else None,
            reality_verification=precomputed[2] if precomputed else None,
            perception=degraded_perception,
            signals={},
            vitality=vitality,
            multimodal_trust=multimodal,
            epistemic_dissonance=epistemic,
            support_buffer=support_buffer,
            limbic_profile=limbic_profile,
            temporal_context=None,
            perception_confidence=confidence_envelope,
        )

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
            generative_candidates=llm_result.get("generative_candidates") if isinstance(llm_result, dict) else [],
            sensory_latency_lag=0  # Will be overwritten by caller
        )

    @staticmethod
    def _extract_confidence(text: str) -> float:
        """Heuristic: extract confidence from LLM response."""
        import math
        text_lower = text.lower()
        conf = 0.5
        if "high confidence" in text_lower or "clearly" in text_lower:
            conf = 0.9
        elif "moderate confidence" in text_lower or "appears" in text_lower:
            conf = 0.6
        elif "low confidence" in text_lower or "unclear" in text_lower:
            conf = 0.3
        
        return max(0.0, min(1.0, conf if math.isfinite(conf) else 0.5))

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

    # ─── Phase 9.2/9.4: Sensory Episode Buffer ───────────────────────────────

    _EPISODE_WINDOW = 10  # rolling window size for stress calculation
    _URGENCY_THRESHOLD = 0.5  # signals["is_urgent"] above this → high urgency
    _STRESS_URGENCY_THRESHOLD = 0.5  # fraction of urgent episodes that triggers high stress

    def absorb_episode(self, episode: "Any") -> None:
        """Absorb a SensoryEpisode into the rolling buffer.

        If the episode is urgent (``is_urgent > _URGENCY_THRESHOLD``), the kernel's
        ``proactive_sensory_event`` is set to signal proactive interrupt handling.
        """
        if not hasattr(self, "_episode_log"):
            from collections import deque
            self._episode_log: "deque" = __import__("collections").deque(
                maxlen=self._EPISODE_WINDOW
            )
        self._episode_log.append(episode)

        urgency = float((episode.signals or {}).get("is_urgent", 0.0))
        if urgency > self._URGENCY_THRESHOLD:
            # Signal the kernel's proactive sensory event if available
            if self.event_bus is not None:
                try:
                    from src.modules.kernel_event_bus import EVENT_SENSORY_STRESS_ALERT
                    self.event_bus.emit(EVENT_SENSORY_STRESS_ALERT, {"urgency": urgency})
                except Exception:
                    pass
            # Also set the kernel event directly via a back-reference if present
            cb = getattr(self, "_proactive_event_setter", None)
            if callable(cb):
                cb()

    def _calculate_sensory_stress(self) -> float:
        """Return a stress score [0, 1.5] based on fraction of urgent episodes in the window."""
        if not hasattr(self, "_episode_log") or not self._episode_log:
            return 0.0
        total = len(self._episode_log)
        urgent = sum(
            1 for ep in self._episode_log
            if float((ep.signals or {}).get("is_urgent", 0.0)) > self._STRESS_URGENCY_THRESHOLD
        )
        return min(1.5, (urgent / total) * 1.5)

    def get_sensory_impulses(self) -> dict:
        """Return connectivity and inertia state from the NomadBridge.

        Returns a dict with keys:
            offline        bool   True when the vessel has been silent > 5 s
            inertia_active bool   True when offline but grace window hasn't expired
            sensory_shutdown bool  True when inertia deadline has passed
        """
        import time as _time
        try:
            from src.modules.nomad_bridge import get_nomad_bridge
            bridge = get_nomad_bridge()
            last_update = getattr(bridge, "_last_sensor_update", _time.time())
            is_healthy = getattr(bridge, "_is_vessel_healthy", False)
        except Exception:
            return {"offline": False, "inertia_active": False}

        stale_secs = _time.time() - last_update
        _STALE_THRESHOLD = 5.0
        offline = stale_secs > _STALE_THRESHOLD or not is_healthy

        if not offline:
            # Clear inertia state when reconnecting
            if hasattr(self, "_shutdown_deadline"):
                del self._shutdown_deadline
            return {"offline": False, "inertia_active": False}

        # Offline path — inertia / graceful shutdown
        _INERTIA_WINDOW = 5.0  # seconds of grace after disconnect
        if not hasattr(self, "_shutdown_deadline"):
            self._shutdown_deadline = _time.time() + _INERTIA_WINDOW

        if _time.time() < self._shutdown_deadline:
            return {"offline": True, "inertia_active": True}

        return {"offline": True, "inertia_active": True, "sensory_shutdown": True}

    @staticmethod
    def _extract_sentiment(text: str) -> float:
        """Heuristic: extract sentiment/emotional tone from LLM response."""
        import math
        text_lower = text.lower()

        # Simple sentiment scoring
        positive_words = ["calm", "safe", "friendly", "happy", "positive"]
        negative_words = ["angry", "distressed", "hostile", "fearful", "negative"]

        positive_count = sum(1 for w in positive_words if w in text_lower)
        negative_count = sum(1 for w in negative_words if w in text_lower)

        sent = 0.5
        if positive_count > negative_count:
            sent = 0.7  # More positive
        elif negative_count > positive_count:
            sent = 0.3  # More negative
        
        return max(0.0, min(1.0, sent if math.isfinite(sent) else 0.5))
