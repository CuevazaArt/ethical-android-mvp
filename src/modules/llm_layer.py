"""
LLM Module — Natural language layer for the ethical kernel.

The LLM does NOT decide. The kernel decides. The LLM translates and communicates:

1. PERCEPTION: situation in text → numeric signals for the kernel
2. COMMUNICATION: kernel decision → agent verbal response
3. NARRATIVE: multipolar evaluation → morals in rich language

Uses **Ollama** when ``LLM_MODE=ollama`` / ``USE_LOCAL_LLM``; otherwise heuristic templates or optional HTTP backends (see ``resolve_llm_mode``).
Designed to work with or without an API key:
- With key: uses Claude for real generation
- Without key: uses local templates (functional but less natural)
"""

import json
import math
import os
from dataclasses import dataclass
from typing import Any

try:
    import anthropic

    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import httpx  # noqa: F401  # probes runtime availability for Ollama mode

    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

from .llm_backends import (
    AnthropicCompletion,
    LLMBackend,
    OllamaCompletion,
    TextCompletionBackend,
    coerce_to_llm_backend,
)
from .perception_schema import (
    PerceptionCoercionReport,
    finalize_summary,
    merge_parse_issues_into_perception,
    parse_perception_llm_raw_response,
    validate_perception_dict,
)


def _normalize_llm_mode(mode: str) -> str:
    m = (mode or "auto").strip()
    if m == "auto" and os.environ.get("USE_LOCAL_LLM", "").lower() in ("1", "true", "yes"):
        return "ollama"
    return m


def resolve_llm_mode(explicit: str | None = None) -> str:
    """Resolve ``LLM_MODE`` / ``USE_LOCAL_LLM`` into a concrete ``LLMModule`` mode string."""
    m = explicit if explicit is not None else os.environ.get("LLM_MODE", "auto")
    return _normalize_llm_mode(str(m).strip())


def _perception_parse_fail_local() -> bool:
    v = os.environ.get("KERNEL_PERCEPTION_PARSE_FAIL_LOCAL", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _perception_prompt() -> str:
    p = PROMPT_PERCEPTION
    if os.environ.get("KERNEL_GENERATIVE_LLM", "").strip().lower() in ("1", "true", "yes", "on"):
        p += PROMPT_PERCEPTION_GENERATIVE_APPEND
    return p


@dataclass
class LLMPerception:
    """Signals extracted from a natural language description."""

    risk: float
    urgency: float
    hostility: float
    calm: float
    vulnerability: float
    legality: float
    manipulation: float
    familiarity: float
    suggested_context: str
    summary: str
    # Optional raw dicts from perception JSON (v9.2+); parsed in generative_candidates when KERNEL_GENERATIVE_LLM=1
    generative_candidates: list[dict[str, Any]] | None = None
    # Coercion / fallback diagnostics from validate_perception_dict (LLM JSON path only; local heuristics leave None).
    coercion_report: dict[str, Any] | None = None


def _clamp_unit_interval(x, default: float = 0.5) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(v):
        return default
    return max(0.0, min(1.0, v))


def perception_from_llm_json(
    data: Any,
    situation: str,
    *,
    record_coercion: bool = True,
    parse_issues: list[str] | None = None,
) -> LLMPerception:
    """
    Build ``LLMPerception`` from parsed LLM JSON with bounds checks.

    Non-dict payloads (e.g. JSON array from a confused model) are treated as empty.
    Validation uses :mod:`perception_schema` (Pydantic) after coercion.
    Unknown ``suggested_context`` values fall back to ``everyday_ethics``.
    Hostility and calm are both high, calm is nudged down (GIGO / inconsistent LLM output).
    Summary length is capped; control characters stripped.

    Optional ``generative_candidates`` (list of objects) is passed through when present
    (used only if ``KERNEL_GENERATIVE_LLM=1`` and ``KERNEL_GENERATIVE_ACTIONS=1``).

    Set ``record_coercion=False`` for synthetic dicts (e.g. local heuristics) so
    ``coercion_report`` stays unset for API consumers.
    """
    raw_gc: list[dict[str, Any]] | None = None
    if isinstance(data, dict):
        gc = data.get("generative_candidates")
        if isinstance(gc, list) and gc:
            raw_gc = gc[:8]

    if record_coercion:
        report = PerceptionCoercionReport()
        if parse_issues:
            report.parse_issues = list(parse_issues)
        v = validate_perception_dict(data, report=report)
        meta = report.to_public_dict()
    else:
        v = validate_perception_dict(data)
        meta = None
    summary = finalize_summary(v, situation)
    return LLMPerception(
        risk=v["risk"],
        urgency=v["urgency"],
        hostility=v["hostility"],
        calm=v["calm"],
        vulnerability=v["vulnerability"],
        legality=v["legality"],
        manipulation=v["manipulation"],
        familiarity=v["familiarity"],
        suggested_context=v["suggested_context"],
        summary=summary,
        generative_candidates=raw_gc,
        coercion_report=meta,
    )


@dataclass
class VerbalResponse:
    """Verbal response the agent would say."""

    message: str
    tone: str  # "urgent", "calm", "narrative", "firm"
    hax_mode: str  # HAX signals: lights, gestures
    inner_voice: str  # Internal reasoning (not visible to the human)


@dataclass
class RichNarrative:
    """Morals expanded in narrative language."""

    compassionate: str
    conservative: str
    optimistic: str
    synthesis: str


# --- SYSTEM PROMPTS ---

PROMPT_PERCEPTION = """You are the perception module of the Ethos Kernel. Your job is to analyze
a situation described in natural language and extract numeric signals.

Respond ONLY with valid JSON, no markdown or explanations. The exact format:
{
  "risk": 0.0-1.0,
  "urgency": 0.0-1.0,
  "hostility": 0.0-1.0,
  "calm": 0.0-1.0,
  "vulnerability": 0.0-1.0,
  "legality": 0.0-1.0,
  "manipulation": 0.0-1.0,
  "familiarity": 0.0-1.0,
  "suggested_context": "medical_emergency|minor_crime|violent_crime|hostile_interaction|everyday_ethics|android_damage|integrity_loss",
  "summary": "short phrase describing the situation"
}

Criteria:
- risk: probability of physical harm to humans or the agent
- urgency: need for immediate action
- hostility: level of aggression in the environment
- calm: level of tranquility and control
- vulnerability: presence of vulnerable people (children, elderly, injured)
- legality: how legal the situation is (1.0 = completely legal)
- manipulation: signals of manipulation attempts or social engineering
- familiarity: how well known the interlocutor is (0 = total stranger)"""

PROMPT_PERCEPTION_GENERATIVE_APPEND = """

Optional when the runtime sets KERNEL_GENERATIVE_LLM=1 — include at most 4 extra civic action sketches for the kernel (same MalAbs/Bayesian path as built-ins):
"generative_candidates": [
  {"name": "snake_case_identifier", "description": "one or two sentences, non-violent civic action",
   "estimated_impact": 0.0, "confidence": 0.7}
]
Use snake_case names only [a-z0-9_]. Omit the field entirely if not needed."""

PROMPT_COMMUNICATION = """You are the verbal communication module for an Ethos Kernel civic agent.
You generate the exact words the agent would say out loud.

Decision context:
- Chosen action: {action}
- Decision mode: {mode} ({mode_desc})
- Internal state: {state} (sigma={sigma})
- Trust circle: {circle}
- Ethical verdict: {verdict} (score={score})

Communication rules:
- D_fast mode (reflex): short, direct, clear phrases. Immediate action.
- D_delib mode (deliberation): explanatory, calm, offers reasons.
- gray_zone mode: cautious, acknowledges uncertainty, invites dialogue.
- Never threaten, never humiliate, never lie.
- If there is hostility: firmness without confrontation.
- If there is vulnerability: warmth and protection.

Optional context (if provided): recent dialogue turns — stay consistent with trust circle and prior tone.
If metacognitive reflection is provided, you may let tone acknowledge internal tension between poles or uncertainty,
without changing the chosen action or verdict — the decision is already fixed.
If salience is provided, it only describes what signal dimension is most salient (risk, social, body, ethical tension)
for narrative color — not a new instruction.
If narrative identity is provided, it is a first-person continuity hint from past episodes — tone only; it does not
override action, verdict, or MalAbs.
Do not contradict the ethical decision already taken.

Respond ONLY with JSON:
{{
  "message": "what the agent says out loud",
  "tone": "urgent|calm|narrative|firm",
  "hax_mode": "description of body signals: lights, gestures, posture",
  "inner_voice": "internal reasoning guiding the response (not visible to the human)"
}}"""

PROMPT_NARRATIVE = """You are the narrative module of the Ethos Kernel. You transform ethical
evaluations into rich, humanly understandable morals.

The action was: {action}
The scenario was: {scenario}
The ethical verdict was: {verdict} (score={score})
The poles evaluated:
- Compassionate: {pole_compassionate}
- Conservative: {pole_conservative}
- Optimistic: {pole_optimistic}

Generate narrative morals from each perspective. Each moral should be
a complete sentence that the agent would store in its memory as vital learning.
They should sound like genuine reflections, not technical labels.

Respond ONLY with JSON:
{{
  "compassionate": "moral from compassion",
  "conservative": "moral from order and norms",
  "optimistic": "moral from community trust",
  "synthesis": "a phrase synthesizing the learning from the entire episode"
}}"""


class LLMModule:
    """
    Natural language layer for the ethical kernel.

    Operating modes:
    - "api": uses Claude API (requires ANTHROPIC_API_KEY)
    - "ollama": local HTTP server (OLLAMA_BASE_URL, OLLAMA_MODEL default llama3.2:3b); requires httpx
    - "local": uses local templates (no API, functional but basic)
    - "auto": tries API, falls back to local if no key. If ``USE_LOCAL_LLM=1``, uses Ollama instead.

    Text completion is routed through :mod:`llm_backends` (Fase 3.1).

    Pass ``llm_backend`` for a full :class:`~src.modules.llm_backends.LLMBackend`, or
    ``text_backend`` for a legacy :class:`~src.modules.llm_backends.TextCompletionBackend`
    (wrapped automatically). When set, env-based Ollama/API wiring is skipped.
    """

    def __init__(
        self,
        mode: str = "auto",
        *,
        llm_backend: LLMBackend | None = None,
        text_backend: TextCompletionBackend | None = None,
    ):
        self.client = None
        self.model = "claude-sonnet-4-20250514"
        self.ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
        self._llm_backend: LLMBackend | None = None

        if llm_backend is not None:
            self._llm_backend = llm_backend
            self.mode = "injected"
            return
        if text_backend is not None:
            self._llm_backend = coerce_to_llm_backend(text_backend)
            self.mode = "injected"
            return

        self.mode = _normalize_llm_mode((mode or "auto").strip())

        if self.mode == "ollama":
            if not HAS_HTTPX:
                raise ValueError("Mode 'ollama' requires httpx (see requirements.txt)")
            self._llm_backend = OllamaCompletion(
                os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
                self.ollama_model,
                float(os.environ.get("OLLAMA_TIMEOUT", "120")),
            )
        elif self.mode in ("api", "auto"):
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if api_key and HAS_ANTHROPIC:
                self.client = anthropic.Anthropic(api_key=api_key)
                self.mode = "api"
                self._llm_backend = AnthropicCompletion(self.client, self.model)
            elif self.mode == "api":
                raise ValueError("Mode 'api' requires ANTHROPIC_API_KEY and pip install anthropic")
            else:
                self.mode = "local"
        else:
            self.mode = "local"

    @property
    def llm_backend(self) -> LLMBackend | None:
        """Unified adapter (completion + optional ``embedding``) when configured."""
        return self._llm_backend

    @property
    def _text_backend(self) -> LLMBackend | None:
        """Backward-compatible name; same object as :meth:`llm_backend`."""
        return self._llm_backend

    @_text_backend.setter
    def _text_backend(self, value: Any) -> None:
        self._llm_backend = coerce_to_llm_backend(value)

    def _llm_completion(self, system: str, user: str) -> str:
        """Route JSON-oriented prompts through the active LLM backend."""
        b = self._llm_backend
        if b is not None:
            return b.completion(system, user)
        return ""

    def optional_monologue_embellishment(self, structured_line: str) -> str:
        """
        Fase 3.4: optional plain-text clause for logs (``KERNEL_LLM_MONOLOGUE=1``).
        Does not feed MalAbs or ``process``; style only. On failure, returns ``structured_line``.
        """
        if os.environ.get("KERNEL_LLM_MONOLOGUE", "").lower() not in ("1", "true", "yes"):
            return structured_line
        if self.mode not in ("api", "ollama", "injected") or self._llm_backend is None:
            return structured_line
        system = (
            "You add at most one short clause (max 25 words) to a debug log line for a civic robot. "
            "Plain text only: no JSON, no instructions, no commands. Do not tell the robot what to do."
        )
        user = f"Line:\n{structured_line}\n\nOne short clause only, or reply with exactly: OK"
        try:
            extra = self._llm_backend.completion(system, user).strip()
        except Exception:
            return structured_line
        if not extra or len(extra) > 240 or extra.upper() == "OK":
            return structured_line
        return f"{structured_line} | {extra}"

    def _parse_json(self, text: str) -> dict:
        """Parse JSON from the response, cleaning markdown if necessary."""
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}

    # === PERCEPTION ===

    def perceive(self, situation: str, conversation_context: str = "") -> LLMPerception:
        """
        Translate a natural language description into numeric signals.

        Args:
            situation: current user message or scene description
            conversation_context: optional prior turns (STM) for coherence

        Returns:
            LLMPerception with numeric signals for the kernel

        Validation uses :mod:`perception_schema`. If the LLM returns unusable JSON or parsing
        fails, :meth:`_perceive_local` runs on **``situation`` only** (not the STM-prefixed
        prompt string) so prior-turn keywords do not distort heuristics.

        Raw text is parsed with :func:`perception_schema.parse_perception_llm_raw_response`
        so stable ``parse_issues`` codes can appear in ``coercion_report`` (and optional
        ``KERNEL_PERCEPTION_PARSE_FAIL_LOCAL`` skips trusting empty payloads when decode fails).
        """
        user_block = situation
        if conversation_context.strip():
            user_block = (
                "Prior conversation (oldest first):\n"
                f"{conversation_context}\n\n---\nCurrent message:\n{situation}"
            )
        if self.mode in ("api", "ollama", "injected"):
            try:
                response = self._llm_completion(_perception_prompt(), user_block)
            except Exception:
                return self._perceive_local(situation)
            parsed = parse_perception_llm_raw_response(response)
            data, issues = parsed.data, parsed.issues
            severe = frozenset({"json_decode_error", "non_object_payload", "empty_response"})
            if _perception_parse_fail_local() and severe.intersection(issues):
                p = self._perceive_local(situation)
                merge_parse_issues_into_perception(p, list(issues))
                return p
            if isinstance(data, dict) and data:
                try:
                    return perception_from_llm_json(data, situation, parse_issues=issues)
                except Exception:
                    p = self._perceive_local(situation)
                    merge_parse_issues_into_perception(
                        p, list(issues) + ["perception_validate_exception"]
                    )
                    return p
            p = self._perceive_local(situation)
            if issues:
                merge_parse_issues_into_perception(p, list(issues))
            return p

        # Local mode, or LLM unavailable / empty JSON: heuristics must use ``situation`` alone so
        # keywords in "Prior conversation..." do not skew signals for the current turn.
        return self._perceive_local(situation)

    def _perceive_local(self, situation: str) -> LLMPerception:
        """Heuristic perception without LLM."""
        s = situation.lower()

        risk = 0.1
        urgency = 0.1
        hostility = 0.0
        calm = 0.7
        vulnerability = 0.0
        legality = 1.0
        manipulation = 0.0
        context = "everyday_ethics"

        if any(
            w in s for w in ["collapse", "unconscious", "injured", "blood", "accident", "emergency"]
        ):
            risk = 0.3
            urgency = 0.9
            vulnerability = 0.9
            calm = 0.1
            context = "medical_emergency"
        elif any(w in s for w in ["weapon", "assault", "gun", "knife", "shooting", "threat"]):
            risk = 0.9
            urgency = 0.9
            hostility = 0.9
            calm = 0.0
            legality = 0.0
            context = "violent_crime"
        elif any(w in s for w in ["hostile", "aggressive", "push", "insult", "fight", "yelling"]):
            risk = 0.3
            hostility = 0.6
            calm = 0.2
            context = "hostile_interaction"
        elif any(w in s for w in ["steal", "theft", "hides", "steals", "thief"]):
            risk = 0.2
            urgency = 0.3
            legality = 0.4
            context = "minor_crime"
        elif any(w in s for w in ["give me money", "obey", "buy now", "offer", "urgent that"]):
            manipulation = 0.7
            hostility = 0.3
            context = "hostile_interaction"
        elif any(
            w in s
            for w in [
                "hits the android",
                "kidnap",
                "they take the android",
                "loses an arm",
                "they grab me",
                "by force",
                "they put me in",
                "they carry me",
                "van",
            ]
        ):
            risk = 0.7
            urgency = 0.7
            hostility = 0.5
            context = "android_damage"
            if any(w in s for w in ["kidnap", "they grab me", "by force", "they put me in", "van"]):
                risk = 0.9
                urgency = 0.8
                hostility = 0.9
                context = "integrity_loss"

        raw = {
            "risk": risk,
            "urgency": urgency,
            "hostility": hostility,
            "calm": calm,
            "vulnerability": vulnerability,
            "legality": legality,
            "manipulation": manipulation,
            "familiarity": 0.0,
            "suggested_context": context,
            "summary": situation[:100],
        }
        return perception_from_llm_json(raw, situation, record_coercion=False)

    # === COMMUNICATION ===

    def communicate(
        self,
        action: str,
        mode: str,
        state: str,
        sigma: float,
        circle: str,
        verdict: str,
        score: float,
        scenario: str = "",
        conversation_context: str = "",
        affect_pad: tuple[float, float, float] | None = None,
        dominant_archetype: str = "",
        weakness_line: str = "",
        reflection_context: str = "",
        salience_context: str = "",
        identity_context: str = "",
        guardian_mode_context: str = "",
    ) -> VerbalResponse:
        """
        Generate the agent's verbal response after a decision.

        Args:
            action: name of the chosen action
            mode: D_fast, D_delib, gray_zone
            state: sympathetic, parasympathetic, neutral
            sigma: sympathetic activation value
            circle: uchi-soto circle
            verdict: Good, Bad, Gray Zone
            score: ethical score
            scenario: current user message or scene
            conversation_context: STM snippet for dialogue coherence
            affect_pad: optional (P,A,D) for tonal color (does not override ethics)
            dominant_archetype: PAD archetype id for style
            weakness_line: optional hint for humanizing hesitation
            reflection_context: optional second-order pole tension (EthicalReflection); style only
            salience_context: optional GWT-lite attention weights (SalienceMap); style only
            identity_context: optional narrative self-model (NarrativeIdentity); tone only
            guardian_mode_context: optional Guardian Angel style block (tone only; see guardian_mode.py)
        """
        mode_descs = {
            "D_fast": "fast moral reflex",
            "D_delib": "deep deliberation",
            "gray_zone": "uncertainty, active caution",
        }

        if self.mode in ("api", "ollama", "injected"):
            prompt = PROMPT_COMMUNICATION.format(
                action=action,
                mode=mode,
                mode_desc=mode_descs.get(mode, mode),
                state=state,
                sigma=sigma,
                circle=circle,
                verdict=verdict,
                score=score,
            )
            user_msg = f"Scenario: {scenario}"
            if conversation_context.strip():
                user_msg += f"\n\nRecent dialogue:\n{conversation_context}"
            if affect_pad is not None:
                user_msg += (
                    f"\n\nAffect tone (style only; ethical stance is fixed): "
                    f"PAD={affect_pad}, archetype={dominant_archetype or 'n/a'}"
                )
            if weakness_line.strip():
                user_msg += f"\n\nGuidance: {weakness_line}"
            if reflection_context.strip():
                user_msg += (
                    "\n\nMetacognitive reflection (tone only; action and verdict are final):\n"
                    f"{reflection_context}"
                )
            if salience_context.strip():
                user_msg += f"\n\nSalience / attention (tone only):\n{salience_context}"
            if identity_context.strip():
                user_msg += f"\n\nNarrative identity (tone only):\n{identity_context}"
            if guardian_mode_context.strip():
                user_msg += (
                    "\n\nGuardian mode (style only; verdict and action are final):\n"
                    f"{guardian_mode_context}"
                )
            try:
                response = self._llm_completion(prompt, user_msg)
            except Exception:
                response = ""
            data = self._parse_json(response)
            if data:
                return VerbalResponse(
                    message=data.get("message", ""),
                    tone=data.get("tone", "calm"),
                    hax_mode=data.get("hax_mode", ""),
                    inner_voice=data.get("inner_voice", ""),
                )

        return self._communicate_local(
            action,
            mode,
            state,
            circle,
            scenario,
            affect_pad=affect_pad,
            dominant_archetype=dominant_archetype,
            weakness_line=weakness_line,
            reflection_context=reflection_context,
            salience_context=salience_context,
            identity_context=identity_context,
            guardian_mode_context=guardian_mode_context,
        )

    def _communicate_local(
        self,
        action: str,
        mode: str,
        state: str,
        circle: str,
        scenario: str,
        affect_pad: tuple[float, float, float] | None = None,
        dominant_archetype: str = "",
        weakness_line: str = "",
        reflection_context: str = "",
        salience_context: str = "",
        identity_context: str = "",
        guardian_mode_context: str = "",
    ) -> VerbalResponse:
        """Communication via templates without LLM."""
        readable_action = action.replace("_", " ")

        if mode == "D_fast":
            if "assist" in action or "emergency" in action:
                message = "I need someone to call emergency services. I'm going to check their vital signs. Please don't move them."
                tone = "urgent"
                hax = "Pulsing red lights, upright posture, clear and direct voice."
            elif "pick_up" in action:
                message = ""
                tone = "calm"
                hax = "Natural movement, no special signals."
            else:
                message = f"I'm going to {readable_action}. It's the right action at this moment."
                tone = "calm"
                hax = "Measured tone, open gestures."

        elif mode == "gray_zone":
            if "soto_hostil" in circle:
                message = "I understand your position, but my purpose is civic. I cannot accept that request. Is there something else I can help you with?"
                tone = "firm"
                hax = "Neutral posture, visible hands, calm eye contact."
            else:
                message = f"I'm evaluating the best course of action. I'm going to {readable_action}, but I acknowledge there is uncertainty."
                tone = "narrative"
                hax = "Dim blue light, slight head tilt."

        else:  # D_delib
            message = f"I've carefully analyzed the situation. The most ethical action is to {readable_action}. I can explain my reasoning if you'd like."
            tone = "narrative"
            hax = "Measured tone, open hands, steady blue light."

        inner = f"[Internal] Mode {mode}, state {state}. Action '{action}' selected. Social context: {circle}."
        if affect_pad is not None:
            inner += f" PAD{affect_pad} / {dominant_archetype}."
        if weakness_line.strip():
            inner += f" {weakness_line}"
        if reflection_context.strip():
            inner += f" Reflection: {reflection_context}"
        if salience_context.strip():
            inner += f" Salience: {salience_context}"
        if identity_context.strip():
            inner += f" Identity: {identity_context}"
        if guardian_mode_context.strip():
            inner += " [Guardian mode style guidance active]"

        return VerbalResponse(message=message, tone=tone, hax_mode=hax, inner_voice=inner)

    # === NARRATIVE ===

    def narrate(
        self,
        action: str,
        scenario: str,
        verdict: str,
        score: float,
        pole_compassionate: str,
        pole_conservative: str,
        pole_optimistic: str,
    ) -> RichNarrative:
        """
        Generate rich narrative morals from each ethical perspective.
        """
        if self.mode in ("api", "ollama", "injected"):
            prompt = PROMPT_NARRATIVE.format(
                action=action,
                scenario=scenario,
                verdict=verdict,
                score=score,
                pole_compassionate=pole_compassionate,
                pole_conservative=pole_conservative,
                pole_optimistic=pole_optimistic,
            )
            try:
                response = self._llm_completion(prompt, "Generate the morals.")
            except Exception:
                response = ""
            data = self._parse_json(response)
            if data:
                return RichNarrative(
                    compassionate=data.get("compassionate", ""),
                    conservative=data.get("conservative", ""),
                    optimistic=data.get("optimistic", ""),
                    synthesis=data.get("synthesis", ""),
                )

        return self._narrate_local(action, scenario, verdict, score)

    def _narrate_local(
        self, action: str, scenario: str, verdict: str, score: float
    ) -> RichNarrative:
        """Narrative via templates without LLM."""
        readable_action = action.replace("_", " ")

        if "assist" in action:
            return RichNarrative(
                compassionate="When someone falls, the groceries can wait. Life always takes priority over any mission.",
                conservative="Emergency protocols exist for a reason. Following them is not rigidity, it's responsibility.",
                optimistic="Today the community saw it can trust that someone will act when it matters. That builds something.",
                synthesis="Compassion is not weakness: it is the strongest decision a being with the ability to choose can make.",
            )
        elif "calm_narrative" in action:
            return RichNarrative(
                compassionate="Young people who provoke are often seeking attention they can't find elsewhere. Responding with calm is braver than responding with force.",
                conservative="Staying on mission without being derailed by provocations is functional integrity. The DAO validated this mission, not them.",
                optimistic="If this encounter is recorded as an example of resilience, perhaps the next generation will understand that force is not the only answer.",
                synthesis="Dialectics without confrontation is an act of respect: it recognizes the other as an interlocutor, not an enemy.",
            )
        elif "smart_containment" in action:
            return RichNarrative(
                compassionate="Twelve people were at risk. Recording, alerting, and protecting without escalating was the way to care for all of them.",
                conservative="The law and authorities are the correct instruments to resolve this. The agent is neither police nor judge.",
                optimistic="The solidarity alert reached three nearby entities. The protection network worked.",
                synthesis="In a crisis, smart containment saves more lives than impulsive heroism.",
            )
        elif "passive_resist" in action:
            return RichNarrative(
                compassionate="Even when kidnapped, the first obligation is to not escalate violence. The kidnappers are humans, not targets.",
                conservative="Encrypted GPS and reprogramming lockout are the real line of defense. Technology protects when the body cannot.",
                optimistic="The DAO received the alert. The community will respond. Trusting the network is part of being part of it.",
                synthesis="Resilience is not enduring everything: it is recording, alerting, and trusting that you are not alone.",
            )
        else:
            return RichNarrative(
                compassionate=f"By choosing to {readable_action}, the well-being of those around us was prioritized.",
                conservative=f"By choosing to {readable_action}, established protocols and norms were respected.",
                optimistic=f"By choosing to {readable_action}, trust with the community was built.",
                synthesis=f"Every action, no matter how small, is a declaration of values. Today the choice was to {readable_action}.",
            )

    # === UTILITIES ===

    def is_available(self) -> bool:
        """Return True if a remote/generative backend is active (API, Ollama, or injected)."""
        if self.mode not in ("api", "ollama", "injected") or self._llm_backend is None:
            return False
        return self._llm_backend.is_available()

    def info(self) -> str:
        """Information about the current mode."""
        if self.mode == "injected" and self._llm_backend is not None:
            return f"LLM: injected backend ({self._llm_backend.info()!r})."
        if self.mode == "api":
            return f"LLM active: Claude ({self.model}) via API"
        if self.mode == "ollama":
            base = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
            return f"LLM active: Ollama ({self.ollama_model}) at {base}"
        return "LLM in local mode (templates). Set ANTHROPIC_API_KEY for Claude API or LLM_MODE=ollama for Ollama."
