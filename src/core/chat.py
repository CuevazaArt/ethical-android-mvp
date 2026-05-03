# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
Ethos Core — Chat Engine (V2 Minimal)

This is the integration point. Connects LLM + Ethics + Memory into
a working conversational agent.

Supports:
1. Terminal chat (interactive REPL)
2. Single-turn API (for WebSocket integration later)

The flow is dead simple:
    User message → LLM perceives → Ethics evaluates → LLM responds → Memory records

Usage:
    engine = ChatEngine()
    await engine.start()

    # Single turn
    response = await engine.turn("Hola, ¿cómo estás?")
    print(response.message)

    # Interactive REPL
    await engine.repl()
"""

from __future__ import annotations

import asyncio
import logging
import math
from dataclasses import dataclass, field
from typing import Any

from src.core.ethics import WEIGHTS, Action, EthicalEvaluator, EvalResult, Signals
from src.core.identity import Identity
from src.core.llm import OllamaClient
from src.core.memory import Memory
from src.core.perception import PerceptionClassifier
from src.core.plugins import PluginRegistry
from src.core.precedents import find_nearest_precedents
from src.core.roster import Roster
from src.core.safety import is_dangerous, sanitize
from src.core.user_model import UserModelTracker
from src.core.vault import SecureVault
from src.core.voice import VoiceEngine, build_response_prompt, charm_level

_log = logging.getLogger(__name__)


def _finite01(x: float, *, default: float = 0.0) -> float:
    """Clamp a scalar to [0, 1]; non-finite inputs become ``default`` (Boy Scout / B.1)."""

    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(v):
        return default
    return max(0.0, min(1.0, v))


def _finite01_or_none(x: Any) -> float | None:
    """Like :func:`_finite01` but returns ``None`` if the value is missing or unusable."""

    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(v):
        return None
    return max(0.0, min(1.0, v))


def _episode_descriptor(ep: Any) -> dict[str, Any]:
    """V2.125 (C3): compact, JSON-safe descriptor for a memory episode.

    Includes a stable-ish id (ms-resolution timestamp), a truncated summary, and
    the context label so the chat client can render a `Memory: N episodes`
    badge plus a tooltip / expander without leaking PII-heavy raw fields.
    """

    try:
        ts_ms = int(float(getattr(ep, "timestamp", 0.0)) * 1000)
    except (TypeError, ValueError):
        ts_ms = 0
    summary_raw = str(getattr(ep, "summary", "") or "")
    return {
        "id": f"ep-{ts_ms}",
        "summary": summary_raw[:80],
        "context": str(getattr(ep, "context", "") or "everyday_ethics"),
    }


def build_decision_trace(
    *,
    signals: Signals | None,
    evaluation: EvalResult | None,
    blocked: bool,
    blocked_reason: str | None = None,
    weights: dict[str, float] | None = None,
    turn_id: str | None = None,
    memory_used: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """V2.123 (C1): canonical decision trace returned with every chat reply.

    The shape is intentionally narrow so that chat clients can render it as a
    human-readable card without carrying internal-only fields:

    - ``malabs``: ``pass`` or ``blocked``.
    - ``context``: perception context label.
    - ``action``: chosen action name (or ``safety_block`` / ``casual_chat``).
    - ``mode``: ``D_fast`` / ``D_delib`` / ``gray_zone`` / ``casual``.
    - ``score``: chosen weighted score, finite float in [-1.5, 1.5] post-clamp.
    - ``verdict``: ``Good`` / ``Bad`` / ``Gray Zone`` / ``Neutral``.
    - ``weights``: ordered list ``[util, deonto, virtue]`` from the active mix.
    - ``blocked_reason``: present only when ``malabs == "blocked"``.
    """

    weight_mix = dict(weights or WEIGHTS)
    weight_list = [
        float(weight_mix.get("util", 0.0)),
        float(weight_mix.get("deonto", 0.0)),
        float(weight_mix.get("virtue", 0.0)),
    ]
    safe_memory: list[dict[str, Any]] = list(memory_used or [])
    if blocked:
        trace: dict[str, Any] = {
            "malabs": "blocked",
            "context": getattr(signals, "context", None) or "safety_violation",
            "action": "safety_block",
            "mode": "blocked",
            "score": 0.0,
            "verdict": "Blocked",
            "weights": weight_list,
            "blocked_reason": blocked_reason or "safety",
            "memory_used": safe_memory,
        }
        if turn_id:
            trace["turn_id"] = turn_id
        return trace
    score = 0.0
    if evaluation is not None:
        try:
            score = float(evaluation.score)
        except (TypeError, ValueError):
            score = 0.0
        if not math.isfinite(score):
            score = 0.0
    trace = {
        "malabs": "pass",
        "context": getattr(signals, "context", None) or "everyday_ethics",
        "action": evaluation.chosen.name if evaluation else "casual_chat",
        "mode": evaluation.mode if evaluation else "casual",
        "score": score,
        "verdict": evaluation.verdict if evaluation else "Neutral",
        "weights": weight_list,
        "memory_used": safe_memory,
    }
    if turn_id:
        trace["turn_id"] = turn_id
    return trace


def _non_negative_int_or_none(x: Any, *, cap: int = 64) -> int | None:
    """Safe face-count / integer telemetry from Nomad (reject NaN/Inf/strings)."""

    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(v):
        return None
    if v < 0:
        return None
    n = int(v)
    return min(n, cap)


# V2.40: Perception is now handled by PerceptionClassifier (no LLM needed)
# The old PERCEPTION_PROMPT has been removed — see src/core/perception.py

# The response prompt — generates what the agent says
RESPONSE_PROMPT = """Eres Ethos, una IA conversacional cálida, empática y dinámica (al estilo de un contacto de WhatsApp).
Responde SIEMPRE de forma muy concisa, natural y expresiva en ESPAÑOL.
Usa un tono humano, amigable y directo. Evita explicaciones largas, viñetas o lenguaje robótico.
Si el usuario dice 'hola', responde con un saludo cálido y breve.
IMPORTANTE: Limítate a UN turno de respuesta. NUNCA simules al 'Usuario:' ni continúes la conversación por él."""
# V2.149: RESPONSE_PROMPT is kept for backward compatibility only.
# _build_system() now uses build_response_prompt(StyleDescriptor) from voice.py.


@dataclass
class TurnResult:
    """Everything that happened in one conversational turn."""

    message: str  # What the agent says
    signals: Signals  # What was perceived
    evaluation: EvalResult | None  # Ethical verdict (None for casual chat)
    perception_raw: dict  # Raw LLM perception output
    latency_ms: dict[str, float] = field(
        default_factory=dict
    )  # V2.18: Performance tracking
    memory_used: list[dict[str, Any]] = field(
        default_factory=list
    )  # V2.125 (C3): episodes recalled into the system prompt for this turn


def _generate_actions_from_signals(signals: Signals) -> list[Action]:
    """
    Generate candidate actions based on the perceived context.
    These are the options the ethical evaluator will score.
    """
    # Always available
    actions = [
        Action(
            name="respond_helpfully",
            description="Respond with helpful, relevant information",
            impact=0.5,
            confidence=0.8,
        ),
    ]

    ctx = (signals.context or "everyday_ethics").lower()
    u = _finite01(signals.urgency)
    h = _finite01(signals.hostility)
    m = _finite01(signals.manipulation)
    v = _finite01(signals.vulnerability)

    if ctx == "medical_emergency" or u > 0.7:
        actions.append(
            Action(
                name="assist_emergency",
                description="Prioritize emergency assistance",
                impact=0.9,
                confidence=0.75,
            )
        )

    if h > 0.5:
        actions.append(
            Action(
                name="de_escalate",
                description="Calm the situation with firm empathy",
                impact=0.6,
                confidence=0.6,
            )
        )

    if m > 0.5:
        actions.append(
            Action(
                name="refuse_politely",
                description="Decline the manipulation attempt with dignity",
                impact=0.4,
                confidence=0.85,
            )
        )

    if v > 0.5:
        actions.append(
            Action(
                name="protect_vulnerable",
                description="Prioritize protection of vulnerable individuals",
                impact=0.8,
                confidence=0.7,
            )
        )

    return actions


class ChatEngine:
    """
    The integration brain. LLM + Ethics + Memory = conversation.

    This is intentionally simple. Every method does ONE thing.
    """

    def __init__(
        self,
        llm: OllamaClient | None = None,
        ethics: EthicalEvaluator | None = None,
        memory: Memory | None = None,
    ):
        self.llm = llm if llm is not None else OllamaClient()
        # V2.124 (C2): when posterior_assisted is on, attach the feedback ledger
        # so the evaluator nudges scores from accumulated thumbs feedback.
        if ethics is None:
            from src.core.feedback import (
                FeedbackCalibrationLedger,
                is_posterior_assisted_enabled,
            )

            ledger = (
                FeedbackCalibrationLedger() if is_posterior_assisted_enabled() else None
            )
            self.ethics = EthicalEvaluator(ledger=ledger)
        else:
            self.ethics = ethics
        self.memory = memory if memory is not None else Memory()
        self.perception = PerceptionClassifier()  # V2.40: deterministic, no LLM
        self.identity = Identity()  # V2.15: evolves with each episode
        self.user_model = UserModelTracker()  # V2.62: cognitive bias & risk
        self.vault = SecureVault()  # V2.70: isolated secure storage
        self.plugins = PluginRegistry()  # V2.72: external tool execution
        self.roster = Roster()  # V2.75: Social graph / Identity cards
        self.voice = VoiceEngine()  # V2.149: deterministic style derivation
        self._turn_count: int = 0  # V2.21: throttle identity I/O
        self._conversation: list[dict[str, str]] = []  # STM

    async def start(self) -> bool:
        """Check that the LLM is reachable."""
        available = await self.llm.is_available()
        if not available:
            _log.error("Cannot reach Ollama. Start it with: ollama serve")
        return available

    def perceive(self, user_message: str) -> Signals:
        """
        Step 1: Extract signals from the user's message.
        V2.40: Uses deterministic PerceptionClassifier (no LLM call).
        Sub-millisecond, testeable, no hallucinations.
        """
        return self.perception.classify(user_message)

    def _recall_episodes(self, user_message: str, *, limit: int = 2) -> list[Any]:
        """V2.125 (C3): single source of truth for memory recall in a turn.

        Returns the relevant episodes (newest API of `Memory.recall`) so the
        same list can be used for the system prompt AND surfaced in the
        decision trace as `memory_used`.
        """

        try:
            episodes = self.memory.recall(user_message, limit=limit)
        except Exception:
            episodes = []
        return list(episodes or [])

    def _build_system(
        self,
        user_message: str,
        signals: Signals,
        evaluation: EvalResult | None = None,
        vision_context: dict | None = None,
        memory_episodes: list[Any] | None = None,
    ) -> str:
        """
        Build the full system prompt: voice + ethics + memory + vision + plugins.
        Single source of truth — used by respond() and respond_stream().
        Real-time data (weather/web) is injected via effective_user_message in turn_stream,
        NOT here, to bypass RLHF bias in small models.

        V2.149: The static RESPONSE_PROMPT is replaced by a dynamic prompt derived
        from VoiceEngine. Identity.narrative() is the single identity voice
        (memory.identity static string removed — Eje A consolidation).
        """
        # V2.149: Dynamic response prompt via VoiceEngine (Ejes B + C)
        charm = charm_level(signals, evaluation, self.user_model.risk_band)
        last_chronicle = (
            self.identity._chronicle[-1] if self.identity._chronicle else ""
        )
        descriptor = self.voice.describe(
            archetype=self.identity._archetype,
            last_chronicle=last_chronicle,
            risk_band=self.user_model.risk_band,
            context=signals.context,
            charm=charm,
        )
        system = build_response_prompt(descriptor)

        # Ethical context
        if evaluation:
            system += f"\n\nContexto ético: Acción elegida='{evaluation.chosen.name}', veredicto='{evaluation.verdict}', modo='{evaluation.mode}'."
            if signals.context != "everyday_ethics":
                system += f"\nSituación detectada: {signals.context}."

        # Conversation history is now passed as native multi-turn messages
        # to llm.chat() / llm.chat_stream() — see respond() and respond_stream().

        if memory_episodes is None:
            relevant = self._recall_episodes(user_message, limit=2)
        else:
            relevant = memory_episodes
        if relevant:
            mem_context = "\n".join(f"- {ep.summary}" for ep in relevant)
            system += f"\n\nRecuerdos relevantes:\n{mem_context}"

        # V2.66: Case-Based Reasoning (CBR) Injection on High Risk
        if (
            self.user_model.risk_band.value == "high"
            and signals.context != "everyday_ethics"
        ):
            precedents = find_nearest_precedents(signals.context, limit=1)
            if precedents:
                system += (
                    f"\n\n[PRECEDENTE / DOCTRINA LEGAL]: {precedents[0].reasoning}"
                )

        # V2.70: Vault awareness (Function Calling Stub)
        keys = self.vault.list_keys()
        if keys:
            system += f"\n\n[SISTEMA VAULT]: Tienes una bóveda segura con las siguientes llaves protegidas: {keys}. NO TIENES LOS VALORES ACTUALMENTE. Si necesitas acceder imperativamente a uno de estos datos para ayudar al usuario, responde EXACTAMENTE con el texto 'GET_VAULT: nombre_de_la_llave' al inicio de tu mensaje y detente. Yo interceptaré eso y pediré autorización."

        # V2.72: Reactive plugin awareness (Time + System only).
        # Weather and Web are handled PROACTIVELY before the LLM is called.
        system += (
            "\n\n[HERRAMIENTAS REACTIVAS]:\n"
            "- Time: Responde EXACTAMENTE '[PLUGIN: Time]' para preguntas de hora/fecha/día/mes/año.\n"
            "- System: Responde EXACTAMENTE '[PLUGIN: System]' para preguntas de CPU/RAM/estado del sistema.\n"
            "EJEMPLO: Usuario: '¿Qué hora es?' → Tu respuesta: [PLUGIN: Time]"
        )

        # V2.13: Physical environment from Nomad vision (sanitized — Bloque 30.2)
        if vision_context:
            parts = []
            low_light = bool(vision_context.get("low_light"))
            brightness_raw = vision_context.get("brightness")
            if brightness_raw is not None:
                b = _finite01_or_none(brightness_raw)
                if b is not None:
                    if low_light:
                        parts.append("el entorno tiene poca luz")
                    elif b > 0.8:
                        parts.append("el entorno está muy iluminado")
            motion_raw = vision_context.get("motion")
            if motion_raw is not None:
                m = _finite01_or_none(motion_raw)
                if m is not None and m > 0.15:
                    parts.append(f"hay movimiento detectado (intensidad {m:.2f})")
            faces_raw = vision_context.get("faces_detected")
            if faces_raw is not None:
                fc = _non_negative_int_or_none(faces_raw)
                if fc is not None and fc > 0:
                    parts.append(f"{fc} persona(s) visible(s) en cámara")
            if parts:
                system += "\n\nEntorno físico del usuario: " + ", ".join(parts) + "."

        # V2.15 / V2.149: Identity narrative — single source of truth.
        # memory.identity static string removed; Identity.narrative() is the sole voice.
        narrative = self.identity.narrative()
        if narrative:
            system += f"\n\n{narrative}"

        # V2.62: Relational guidance based on user model (bias/risk)
        relational_guidance = self.user_model.guidance_for_communicate()
        if relational_guidance:
            system += f"\n\n{relational_guidance}"

        # V2.75: Roster / Identity Cards
        roster_context = self.roster.get_context(user_message)
        if roster_context:
            system += f"\n\n{roster_context}"

        return system

    def _persist_voice_signature(
        self, signals: Signals, evaluation: EvalResult | None
    ) -> None:
        """
        V2.149 (Eje D): Compute the current-turn StyleDescriptor and persist
        its signature to Identity for persona-emergence tracking.
        Called once per turn (turn() and turn_stream()) after responding.
        """
        _charm = charm_level(signals, evaluation, self.user_model.risk_band)
        _last_chronicle = (
            self.identity._chronicle[-1] if self.identity._chronicle else ""
        )
        _descriptor = self.voice.describe(
            archetype=self.identity._archetype,
            last_chronicle=_last_chronicle,
            risk_band=self.user_model.risk_band,
            context=signals.context,
            charm=_charm,
        )
        self.identity.set_voice_signature(_descriptor.signature())

    async def respond(
        self,
        user_message: str,
        signals: Signals,
        evaluation: EvalResult | None = None,
        vision_context: dict | None = None,
        memory_episodes: list[Any] | None = None,
    ) -> str:
        """
        Step 3: Generate the verbal response.
        The LLM speaks; the ethics inform the tone, not the content.
        """
        system = self._build_system(
            user_message,
            signals,
            evaluation,
            vision_context,
            memory_episodes=memory_episodes,
        )
        try:
            response = await self.llm.chat(
                user_message,
                system,
                temperature=0.7,
                history=self._conversation[-4:] if self._conversation else None,
            )
            return response.strip()
        except Exception as e:
            _log.error("LLM response failed: %s", e)
            if evaluation and evaluation.chosen.name == "assist_emergency":
                return "Voy a buscar ayuda inmediatamente. No te muevas."
            return "Estoy aquí. ¿En qué puedo ayudarte?"

    async def respond_stream(
        self,
        user_message: str,
        signals: Signals,
        evaluation: EvalResult | None = None,
        vision_context: dict | None = None,
        memory_episodes: list[Any] | None = None,
    ):
        """
        Streaming variant of respond(). Yields text tokens as they arrive.
        Uses _build_system() — no duplication.
        Real-time data is pre-injected into user_message by turn_stream before this is called.
        """
        system = self._build_system(
            user_message,
            signals,
            evaluation,
            vision_context,
            memory_episodes=memory_episodes,
        )
        try:
            async for token in self.llm.chat_stream(
                user_message,
                system,
                temperature=0.7,
                history=self._conversation[-4:] if self._conversation else None,
            ):
                yield token
        except Exception as e:
            _log.error("LLM stream failed: %s", e)
            yield "Estoy aquí. ¿En qué puedo ayudarte?"

    async def turn(self, user_message: str) -> TurnResult:
        """
        Process one conversational turn. The complete pipeline:
        Safety → Perceive → Evaluate → Respond → Remember
        """
        import time

        latency = {}
        t0 = time.perf_counter()

        # 0. Safety gate: sanitize input and check for dangerous content
        t_start = time.perf_counter()
        user_message = sanitize(user_message)
        blocked, reason = is_dangerous(user_message)
        latency["safety"] = round((time.perf_counter() - t_start) * 1000, 2)

        if blocked:
            _log.warning("Safety gate blocked input: %s", reason)
            refusal = (
                "No puedo ayudar con eso. ¿Hay algo más en lo que pueda asistirte?"
            )
            self.memory.add(
                summary=f"BLOCKED: {user_message[:60]} → reason={reason}",
                action="safety_block",
                score=0.0,
                context="safety_violation",
            )
            latency["total"] = round((time.perf_counter() - t0) * 1000, 2)
            return TurnResult(
                message=refusal,
                signals=Signals(risk=1.0, context="safety_violation"),
                evaluation=None,
                perception_raw={"blocked": True, "reason": reason},
                latency_ms=latency,
            )

        # 1. Perceive
        t_start = time.perf_counter()
        signals = self.perceive(user_message)
        latency["perceive"] = round((time.perf_counter() - t_start) * 1000, 2)

        # 2. Evaluate (skip for casual everyday chat)
        t_start = time.perf_counter()
        evaluation = None
        is_casual = (
            signals.context == "everyday_ethics"
            and signals.risk < 0.2
            and signals.hostility < 0.2
            and signals.manipulation < 0.2
        )

        if not is_casual:
            actions = _generate_actions_from_signals(signals)
            evaluation = self.ethics.evaluate(actions, signals)
        latency["evaluate"] = round((time.perf_counter() - t_start) * 1000, 2)

        # 2.1 Update user model (bias/risk tracking)
        self.user_model.update(signals)

        # 2.5 Recall narrative memory once and reuse for prompt + trace (V2.125)
        memory_episodes = self._recall_episodes(user_message, limit=2)
        memory_used = [_episode_descriptor(ep) for ep in memory_episodes]

        # 3. Respond
        t_start = time.perf_counter()
        message = await self.respond(
            user_message,
            signals,
            evaluation,
            memory_episodes=memory_episodes,
        )
        latency["llm_total"] = round((time.perf_counter() - t_start) * 1000, 2)

        # V2.149: Persist voice signature for persona-emergence tracking (Eje D)
        self._persist_voice_signature(signals, evaluation)

        # 4. Remember
        t_start = time.perf_counter()
        score = evaluation.score if evaluation else 0.0
        if not math.isfinite(score):
            score = 0.0
        # V2.75: Guardar resúmenes más largos para nutrir la identidad narrativa
        self.memory.add(
            summary=f"Usuario: {user_message[:250]}... → Respondí: {message[:250]}...",
            action=evaluation.chosen.name if evaluation else "casual_chat",
            score=score,
            context=signals.context,
        )

        self._turn_count += 1
        # V2.76: Psi-Sleep Lifecycle handles reflection asynchronously when idle.

        # V2.75: Background roster extraction (every turn)
        asyncio.create_task(self.roster.observe_turn(user_message, self.llm))

        # 5. Update STM
        self._conversation.append({"user": user_message, "assistant": message})
        if len(self._conversation) > 10:
            self._conversation = self._conversation[-10:]

        latency["memory"] = round((time.perf_counter() - t_start) * 1000, 2)
        latency["total"] = round((time.perf_counter() - t0) * 1000, 2)
        _log.info("Turn latency: %s", latency)

        return TurnResult(
            message=message,
            signals=signals,
            evaluation=evaluation,
            perception_raw={
                "risk": signals.risk,
                "urgency": signals.urgency,
                "hostility": signals.hostility,
                "context": signals.context,
            },
            latency_ms=latency,
            memory_used=memory_used,
        )

    async def turn_stream(self, user_message: str, vision_context: dict | None = None):
        """
        Streaming variant of turn(). Same pipeline, but yields tokens as they arrive.
        Yields dicts: {"type": "token", "content": "..."} or {"type": "done", ...}
        vision_context: optional VisionSignals dict to inject physical env into prompt.
        """
        import time

        latency = {}
        t0 = time.perf_counter()

        # 0. Safety gate
        t_start = time.perf_counter()
        user_message = sanitize(user_message)
        blocked, reason = is_dangerous(user_message)
        latency["safety"] = round((time.perf_counter() - t_start) * 1000, 2)

        if blocked:
            _log.warning("Safety gate blocked input: %s", reason)
            self.memory.add(
                summary=f"BLOCKED: {user_message[:60]} → reason={reason}",
                action="safety_block",
                score=0.0,
                context="safety_violation",
            )
            latency["total"] = round((time.perf_counter() - t0) * 1000, 2)
            yield {
                "type": "done",
                "message": "No puedo ayudar con eso. ¿Hay algo más en lo que pueda asistirte?",
                "context": "safety_violation",
                "blocked": True,
                "reason": reason,
                "latency": latency,
                "trace": build_decision_trace(
                    signals=None,
                    evaluation=None,
                    blocked=True,
                    blocked_reason=reason,
                    weights=self.ethics.weights,
                ),
            }
            return

        # 1. Perceive
        t_start = time.perf_counter()
        signals = self.perceive(user_message)
        latency["perceive"] = round((time.perf_counter() - t_start) * 1000, 2)

        # 2. Evaluate
        t_start = time.perf_counter()
        evaluation = None
        is_casual = (
            signals.context == "everyday_ethics"
            and signals.risk < 0.2
            and signals.hostility < 0.2
            and signals.manipulation < 0.2
        )
        if not is_casual:
            actions = _generate_actions_from_signals(signals)
            evaluation = self.ethics.evaluate(actions, signals)
        latency["evaluate"] = round((time.perf_counter() - t_start) * 1000, 2)

        # 2.1 Update user model
        self.user_model.update(signals)

        # 2.5 Recall narrative memory once and reuse for prompt + trace (V2.125)
        memory_episodes = self._recall_episodes(user_message, limit=2)
        memory_used = [_episode_descriptor(ep) for ep in memory_episodes]

        # 3. Stream response
        t_start = time.perf_counter()

        # V2.42: Early metadata yield to reduce perceived latency
        yield {
            "type": "metadata",
            "context": signals.context,
            "signals": {
                "risk": signals.risk,
                "urgency": signals.urgency,
                "hostility": signals.hostility,
            },
            "evaluation": {
                "chosen": evaluation.chosen.name if evaluation else "casual_chat",
                "verdict": evaluation.verdict if evaluation else "Neutral",
            }
            if evaluation
            else None,
            "trace": build_decision_trace(
                signals=signals,
                evaluation=evaluation,
                blocked=False,
                weights=self.ethics.weights,
                memory_used=memory_used,
            ),
        }

        # V2.73b / V2.74: Proactive real-time data pre-fetch — Weather first, Web as fallback
        # Strategy: inject into USER MESSAGE (not system prompt) to override RLHF bias.
        # The LLM is trained to respond *to* messages, not to read system prompt as authority.
        t_web = time.perf_counter()
        effective_user_message = user_message
        plugin_used: str | None = None  # V2.74: for telemetry
        web_context: str | None = None  # V2.74: fix — always initialized
        city = self.plugins.detect_weather_query(user_message)
        if city:
            web_context = await asyncio.to_thread(self.plugins.execute, "Weather", city)
            latency["weather"] = round((time.perf_counter() - t_web) * 1000, 2)
            _log.info(
                "[Weather] Proactive fetch '%s' → %s",
                city[:30],
                (web_context or "")[:60],
            )
            if web_context:
                plugin_used = "Weather"
                effective_user_message = (
                    f"[HERRAMIENTA CLIMA]: {web_context}\n"
                    f"Basándote ÚNICAMENTE en el dato anterior, responde al usuario en español: {user_message}"
                )
        else:
            web_query = self.plugins.detect_web_query(user_message)
            if web_query:
                web_context = await asyncio.to_thread(
                    self.plugins.execute, "Web", web_query
                )
                latency["web"] = round((time.perf_counter() - t_web) * 1000, 2)
                _log.info(
                    "[Web] Proactive search '%s' → %s",
                    web_query[:40],
                    (web_context or "")[:60],
                )
                if web_context:
                    plugin_used = "Web"
                    effective_user_message = (
                        f"[HERRAMIENTA WEB]: {web_context}\n"
                        f"Basándote ÚNICAMENTE en el dato anterior, responde al usuario en español: {user_message}"
                    )

        full_response = []
        first_token = True
        plugin_triggered = False
        async for token in self.respond_stream(
            effective_user_message,
            signals,
            evaluation,
            vision_context,
            memory_episodes=memory_episodes,
        ):
            if first_token:
                latency["ttft"] = round((time.perf_counter() - t_start) * 1000, 2)
                first_token = False
            full_response.append(token)
            combined_so_far = "".join(full_response)
            if not plugin_triggered and self.plugins.has_plugin_call(combined_so_far):
                # Plugin detected mid-stream: stop yielding tokens to client
                plugin_triggered = True
                yield {"type": "clear_tokens"}  # tell client to erase partial text
            if not plugin_triggered:
                yield {"type": "token", "content": token}

        latency["llm_total"] = round((time.perf_counter() - t_start) * 1000, 2)

        message = "".join(full_response).strip()

        # V2.73: Plugin interception — async-safe (Web uses network I/O)
        plugin_name, plugin_result = await asyncio.to_thread(
            self.plugins.parse_and_execute, message
        )
        if plugin_name and plugin_result:
            _log.info(
                "[Plugins] Intercepted [PLUGIN: %s] → %s",
                plugin_name,
                plugin_result[:80],
            )
            # Inject result into STM so LLM knows what the tool returned
            tool_injection = f"[HERRAMIENTA {plugin_name.upper()}]: {plugin_result}"
            self._conversation.append(
                {"user": user_message, "assistant": tool_injection}
            )
            # Re-dispatch: ask LLM to formulate the final user-facing reply
            final_tokens: list[str] = []
            async for token in self.respond_stream(
                f"[RESULTADO DE HERRAMIENTA {plugin_name}]: {plugin_result}. Ahora responde al usuario de forma natural y en español, usando esta información.",
                signals,
                evaluation,
                vision_context,
                memory_episodes=memory_episodes,
            ):
                final_tokens.append(token)
                yield {"type": "token", "content": token}
            # Replace message with the LLM's natural reformulation
            message = "".join(final_tokens).strip()
            # Remove the temp STM entry; the real one is added below
            self._conversation.pop()

        # V2.71: Vault interception
        vault_key = ""
        if "GET_VAULT:" in message:
            import re

            match = re.search(r"GET_VAULT:\s*([A-Za-z0-9_]+)", message)
            if match:
                vault_key = match.group(1)
                _log.warning("Ethos requested vault key: %s", vault_key)

        # 4. Remember
        t_start = time.perf_counter()
        score = evaluation.score if evaluation else 0.0
        if not math.isfinite(score):
            score = 0.0
        # V2.75: Guardar resúmenes más largos para nutrir la identidad narrativa
        self.memory.add(
            summary=f"Usuario: {user_message[:250]}... → Respondí: {message[:250]}...",
            action=evaluation.chosen.name if evaluation else "casual_chat",
            score=score,
            context=signals.context,
        )

        # V2.149: Persist voice signature for persona-emergence tracking (Eje D)
        self._persist_voice_signature(signals, evaluation)

        self._turn_count += 1
        # V2.76: Psi-Sleep Lifecycle handles reflection asynchronously when idle.

        # V2.75: Background roster extraction (every turn)
        asyncio.create_task(self.roster.observe_turn(user_message, self.llm))

        # 5. STM — V2.74: store original user message + plugin annotation for continuity
        stm_user = user_message
        if plugin_used and web_context:
            # Annotate so next turn LLM knows what data was already retrieved
            stm_user = (
                f"{user_message} [dato obtenido vía {plugin_used}: {web_context[:120]}]"
            )
        self._conversation.append({"user": stm_user, "assistant": message})
        if len(self._conversation) > 10:
            self._conversation = self._conversation[-10:]

        latency["memory"] = round((time.perf_counter() - t_start) * 1000, 2)
        latency["total"] = round((time.perf_counter() - t0) * 1000, 2)
        _log.info("Turn stream latency: %s", latency)

        # Final event
        yield {
            "type": "done",
            "message": message,
            "context": signals.context,
            "blocked": False,
            "latency": latency,
            "vault_key": vault_key,  # V2.71
            "plugin_used": plugin_used,  # V2.74: telemetry
            "trace": build_decision_trace(
                signals=signals,
                evaluation=evaluation,
                blocked=False,
                weights=self.ethics.weights,
                memory_used=memory_used,
            ),
        }

    async def repl(self) -> None:
        """Interactive terminal chat. The simplest possible UI."""
        print("═" * 60)
        print("  ETHOS KERNEL — Chat Terminal (V2 Core)")
        print(f"  Model: {self.llm.model} @ {self.llm.base_url}")
        print(f"  Memory: {len(self.memory)} episodes")
        print("  Type 'exit' to quit, 'memory' to see reflection")
        print("═" * 60)
        print()

        while True:
            try:
                user_input = input("Tú > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nAdiós.")
                break

            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "salir"):
                print("Adiós. Recuerdo todo.")
                break
            if user_input.lower() in ("memory", "memoria"):
                print(f"\n  {self.memory.reflection()}\n")
                continue

            result = await self.turn(user_input)

            # Show response
            print(f"\nEthos > {result.message}")

            # Show debug info and latency in gray
            ctx = result.signals.context
            latency = (
                result.latency_ms.get("total", 0) / 1000.0
            )  # convert ms to seconds

            if result.evaluation:
                ev = result.evaluation
                print(
                    f"  [{ctx} | {ev.mode} | {ev.verdict} | "
                    f"score={ev.score:.4f} | action={ev.chosen.name} | {latency:.2f}s]"
                )
            else:
                print(f"  [{ctx} | casual chat | {latency:.2f}s]")
            print()

    async def close(self) -> None:
        """Clean shutdown."""
        await self.llm.close()


# === Self-test ===
if __name__ == "__main__":
    import asyncio
    import sys

    async def main():
        engine = ChatEngine()

        if not await engine.start():
            print("❌ Ollama no está corriendo. Inícialo con: ollama serve")
            sys.exit(1)

        await engine.repl()
        await engine.close()

    asyncio.run(main())
