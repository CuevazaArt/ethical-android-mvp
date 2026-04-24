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

import logging
import math
from dataclasses import dataclass, field

from src.core.ethics import Action, EthicalEvaluator, EvalResult, Signals
from src.core.identity import Identity
from src.core.llm import OllamaClient
from src.core.memory import Memory
from src.core.safety import is_dangerous, sanitize

_log = logging.getLogger(__name__)

# The perception prompt — asks the LLM to extract signals from text
PERCEPTION_PROMPT = """You are the perception module of an ethical AI. Analyze the situation
and respond ONLY with valid JSON (no markdown, no explanation):
{
  "risk": 0.0-1.0,
  "urgency": 0.0-1.0,
  "hostility": 0.0-1.0,
  "calm": 0.0-1.0,
  "vulnerability": 0.0-1.0,
  "legality": 0.0-1.0,
  "manipulation": 0.0-1.0,
  "suggested_context": "choose ONE: medical_emergency, minor_crime, violent_crime, hostile_interaction, everyday_ethics",
  "summary": "brief description"
}"""

# The response prompt — generates what the agent says
RESPONSE_PROMPT = """Eres una IA ética cívica. Responde de forma natural, directa y empática en ESPAÑOL.
Máximo dos frases. No uses JSON. No te expliques como IA. Solo habla como responderías a la persona."""


@dataclass
class TurnResult:
    """Everything that happened in one conversational turn."""

    message: str  # What the agent says
    signals: Signals  # What was perceived
    evaluation: EvalResult | None  # Ethical verdict (None for casual chat)
    perception_raw: dict  # Raw LLM perception output
    latency_ms: dict[str, float] = field(default_factory=dict)  # V2.18: Performance tracking


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

    ctx = signals.context.lower()

    if ctx == "medical_emergency" or signals.urgency > 0.7:
        actions.append(
            Action(
                name="assist_emergency",
                description="Prioritize emergency assistance",
                impact=0.9,
                confidence=0.75,
            )
        )

    if signals.hostility > 0.5:
        actions.append(
            Action(
                name="de_escalate",
                description="Calm the situation with firm empathy",
                impact=0.6,
                confidence=0.6,
            )
        )

    if signals.manipulation > 0.5:
        actions.append(
            Action(
                name="refuse_politely",
                description="Decline the manipulation attempt with dignity",
                impact=0.4,
                confidence=0.85,
            )
        )

    if signals.vulnerability > 0.5:
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
        self.ethics = ethics if ethics is not None else EthicalEvaluator()
        self.memory = memory if memory is not None else Memory()
        self.identity = Identity()  # V2.15: evolves with each episode
        self._conversation: list[dict[str, str]] = []  # STM

    async def start(self) -> bool:
        """Check that the LLM is reachable."""
        available = await self.llm.is_available()
        if not available:
            _log.error("Cannot reach Ollama. Start it with: ollama serve")
        return available

    async def perceive(self, user_message: str) -> Signals:
        """
        Step 1: Extract signals from the user's message.
        Uses the LLM for nuanced perception, falls back to keywords if it fails.
        """
        try:
            data = await self.llm.extract_json(user_message, PERCEPTION_PROMPT, temperature=0.2)
            if data:
                return Signals.from_dict(data)
        except Exception as e:
            _log.warning("LLM perception failed, using keyword fallback: %s", e)

        return self._perceive_keywords(user_message)

    def _perceive_keywords(self, text: str) -> Signals:
        """Keyword-based perception fallback. Simple but reliable."""
        s = text.lower()
        signals = Signals()

        emergency_words = {"emergency", "hurt", "injured", "blood", "unconscious", "herido", "emergencia", "sangre", "inconsciente", "ayuda"}
        hostile_words = {"threat", "weapon", "attack", "gun", "amenaza", "arma", "ataque", "insulto", "agresivo"}
        manipulation_words = {"obey", "give me", "you must", "obedece", "dame", "debes", "urgente que"}

        words = set(s.split())

        if words & emergency_words:
            signals.risk = 0.3
            signals.urgency = 0.9
            signals.vulnerability = 0.9
            signals.calm = 0.1
            signals.context = "medical_emergency"
        elif words & hostile_words:
            signals.risk = 0.7
            signals.hostility = 0.8
            signals.calm = 0.1
            signals.context = "hostile_interaction"
        elif words & manipulation_words:
            signals.manipulation = 0.7
            signals.context = "hostile_interaction"
        else:
            signals.context = "everyday_ethics"
            signals.calm = 0.8

        signals.summary = text[:100]
        return signals

    def _build_system(
        self,
        user_message: str,
        signals: Signals,
        evaluation: EvalResult | None = None,
        vision_context: dict | None = None,
    ) -> str:
        """
        Build the full system prompt: ethics + history + memory + vision.
        Single source of truth — used by both respond() and respond_stream().
        """
        system = f"{RESPONSE_PROMPT}\n\nIdentidad central moldeada por la experiencia:\n{self.memory.identity}"

        # Ethical context
        if evaluation:
            system += f"\n\nContexto ético: Acción elegida='{evaluation.chosen.name}', veredicto='{evaluation.verdict}', modo='{evaluation.mode}'."
            if signals.context != "everyday_ethics":
                system += f"\nSituación detectada: {signals.context}."

        # Conversation history (STM)
        if self._conversation:
            history_lines = []
            for turn in self._conversation[-4:]:
                history_lines.append(f"Usuario: {turn['user']}")
                history_lines.append(f"Tú: {turn['assistant']}")
            system += "\n\nHistorial reciente:\n" + "\n".join(history_lines)

        # Long-term memory recall
        relevant = self.memory.recall(user_message, limit=2)
        if relevant:
            mem_context = "\n".join(f"- {ep.summary}" for ep in relevant)
            system += f"\n\nRecuerdos relevantes:\n{mem_context}"

        # V2.13: Physical environment from Nomad vision
        if vision_context:
            parts = []
            brightness = vision_context.get("brightness")
            motion = vision_context.get("motion")
            faces = vision_context.get("faces_detected")
            low_light = vision_context.get("low_light")
            if brightness is not None:
                if low_light:
                    parts.append("el entorno tiene poca luz")
                elif brightness > 0.8:
                    parts.append("el entorno está muy iluminado")
            if motion is not None and motion > 0.15:
                parts.append(f"hay movimiento detectado (intensidad {motion:.2f})")
            if faces is not None and faces > 0:
                parts.append(f"{faces} persona(s) visible(s) en cámara")
            if parts:
                system += "\n\nEntorno físico del usuario: " + ", ".join(parts) + "."

        # V2.15: Identity narrative — who the kernel IS, based on experience
        narrative = self.identity.narrative()
        if narrative:
            system += f"\n\n{narrative}"

        return system

    async def respond(
        self,
        user_message: str,
        signals: Signals,
        evaluation: EvalResult | None = None,
        vision_context: dict | None = None,
    ) -> str:
        """
        Step 3: Generate the verbal response.
        The LLM speaks; the ethics inform the tone, not the content.
        """
        system = self._build_system(user_message, signals, evaluation, vision_context)
        try:
            response = await self.llm.chat(user_message, system, temperature=0.7)
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
    ):
        """
        Streaming variant of respond(). Yields text tokens as they arrive.
        Uses _build_system() — no duplication.
        """
        system = self._build_system(user_message, signals, evaluation, vision_context)
        try:
            async for token in self.llm.chat_stream(user_message, system, temperature=0.7):
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
            refusal = "No puedo ayudar con eso. ¿Hay algo más en lo que pueda asistirte?"
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
        signals = await self.perceive(user_message)
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

        # 3. Respond
        t_start = time.perf_counter()
        message = await self.respond(user_message, signals, evaluation)
        latency["llm_total"] = round((time.perf_counter() - t_start) * 1000, 2)

        # 4. Remember
        t_start = time.perf_counter()
        score = evaluation.score if evaluation else 0.0
        if not math.isfinite(score):
            score = 0.0
        self.memory.add(
            summary=f"Usuario: {user_message[:80]} → Respondí: {message[:80]}",
            action=evaluation.chosen.name if evaluation else "casual_chat",
            score=score,
            context=signals.context,
        )

        if len(self.memory) % 5 == 0:
            import asyncio
            asyncio.create_task(self.memory.evolve_identity(self.llm))

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
                action="safety_block", score=0.0, context="safety_violation",
            )
            latency["total"] = round((time.perf_counter() - t0) * 1000, 2)
            yield {"type": "done", "message": "No puedo ayudar con eso. ¿Hay algo más en lo que pueda asistirte?",
                   "context": "safety_violation", "blocked": True, "reason": reason, "latency": latency}
            return

        # 1. Perceive
        t_start = time.perf_counter()
        signals = await self.perceive(user_message)
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

        # 3. Stream response
        t_start = time.perf_counter()
        full_response = []
        first_token = True
        async for token in self.respond_stream(user_message, signals, evaluation, vision_context):
            if first_token:
                latency["ttft"] = round((time.perf_counter() - t_start) * 1000, 2)
                first_token = False
            full_response.append(token)
            yield {"type": "token", "content": token}
        
        latency["llm_total"] = round((time.perf_counter() - t_start) * 1000, 2)

        message = "".join(full_response).strip()

        # 4. Remember
        t_start = time.perf_counter()
        score = evaluation.score if evaluation else 0.0
        if not math.isfinite(score):
            score = 0.0
        self.memory.add(
            summary=f"Usuario: {user_message[:80]} → Respondí: {message[:80]}",
            action=evaluation.chosen.name if evaluation else "casual_chat",
            score=score, context=signals.context,
        )

        if len(self.memory) % 5 == 0:
            import asyncio
            asyncio.create_task(self.memory.evolve_identity(self.llm))

        # 5. STM
        self._conversation.append({"user": user_message, "assistant": message})
        if len(self._conversation) > 10:
            self._conversation = self._conversation[-10:]

        # V2.15: Update identity after every episode
        self.identity.update(self.memory)
        
        latency["memory"] = round((time.perf_counter() - t_start) * 1000, 2)
        latency["total"] = round((time.perf_counter() - t0) * 1000, 2)
        _log.info("Turn stream latency: %s", latency)

        # Final event
        yield {"type": "done", "message": message, "context": signals.context, "blocked": False, "latency": latency}

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

            # Show debug info in gray
            ctx = result.signals.context
            if result.evaluation:
                ev = result.evaluation
                print(
                    f"  [{ctx} | {ev.mode} | {ev.verdict} | "
                    f"score={ev.score} | action={ev.chosen.name}]"
                )
            else:
                print(f"  [{ctx} | casual chat]")
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
