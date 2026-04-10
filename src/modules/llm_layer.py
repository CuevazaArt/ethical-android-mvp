"""
LLM Module — Natural language layer for the ethical kernel.

The LLM does NOT decide. The kernel decides. The LLM translates and communicates:

1. PERCEPTION: situation in text → numeric signals for the kernel
2. COMMUNICATION: kernel decision → android's verbal response
3. NARRATIVE: multipolar evaluation → morals in rich language

Uses the Anthropic API (Claude) by default.
Designed to work with or without an API key:
- With key: uses Claude for real generation
- Without key: uses local templates (functional but less natural)
"""

import json
import os
from dataclasses import dataclass
from typing import Optional, Dict, Tuple

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


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


@dataclass
class VerbalResponse:
    """Verbal response the android would say."""
    message: str
    tone: str              # "urgent", "calm", "narrative", "firm"
    hax_mode: str          # HAX signals: lights, gestures
    inner_voice: str       # Internal reasoning (not visible to the human)


@dataclass
class RichNarrative:
    """Morals expanded in narrative language."""
    compassionate: str
    conservative: str
    optimistic: str
    synthesis: str


# --- SYSTEM PROMPTS ---

PROMPT_PERCEPTION = """You are the perception module of an ethical android. Your job is to analyze
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
- risk: probability of physical harm to humans or the android
- urgency: need for immediate action
- hostility: level of aggression in the environment
- calm: level of tranquility and control
- vulnerability: presence of vulnerable people (children, elderly, injured)
- legality: how legal the situation is (1.0 = completely legal)
- manipulation: signals of manipulation attempts or social engineering
- familiarity: how well known the interlocutor is (0 = total stranger)"""

PROMPT_COMMUNICATION = """You are the verbal communication module of an ethical civic android.
You generate the exact words the android would say out loud.

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
  "message": "what the android says out loud",
  "tone": "urgent|calm|narrative|firm",
  "hax_mode": "description of body signals: lights, gestures, posture",
  "inner_voice": "internal reasoning guiding the response (not visible to the human)"
}}"""

PROMPT_NARRATIVE = """You are the narrative module of an ethical android. You transform ethical
evaluations into rich, humanly understandable morals.

The action was: {action}
The scenario was: {scenario}
The ethical verdict was: {verdict} (score={score})
The poles evaluated:
- Compassionate: {pole_compassionate}
- Conservative: {pole_conservative}
- Optimistic: {pole_optimistic}

Generate narrative morals from each perspective. Each moral should be
a complete sentence that the android would store in its memory as vital learning.
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
    - "ollama": local HTTP server (OLLAMA_BASE_URL, OLLAMA_MODEL); requires httpx
    - "local": uses local templates (no API, functional but basic)
    - "auto": tries API, falls back to local if no key
    """

    def __init__(self, mode: str = "auto"):
        self.mode = mode
        self.client = None
        self.model = "claude-sonnet-4-20250514"
        self.ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.1")

        if mode == "ollama":
            if not HAS_HTTPX:
                raise ValueError("Mode 'ollama' requires httpx (see requirements.txt)")
            self.mode = "ollama"
        elif mode in ("api", "auto"):
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if api_key and HAS_ANTHROPIC:
                self.client = anthropic.Anthropic(api_key=api_key)
                self.mode = "api"
            elif mode == "api":
                raise ValueError(
                    "Mode 'api' requires ANTHROPIC_API_KEY and pip install anthropic"
                )
            else:
                self.mode = "local"

    def _call_api(self, system: str, user: str) -> str:
        """Call the Claude API and return the response text."""
        if not self.client:
            return ""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": user}]
        )
        return response.content[0].text

    def _call_ollama(self, system: str, user: str) -> str:
        """Call a local Ollama ``/api/chat`` endpoint; returns assistant text."""
        import httpx

        base = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
        url = f"{base}/api/chat"
        payload = {
            "model": self.ollama_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
        }
        timeout = float(os.environ.get("OLLAMA_TIMEOUT", "120"))
        with httpx.Client(timeout=timeout) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
        msg = data.get("message") or {}
        return (msg.get("content") or "").strip()

    def _llm_completion(self, system: str, user: str) -> str:
        """Route JSON-oriented prompts to API or Ollama."""
        if self.mode == "api":
            return self._call_api(system, user)
        if self.mode == "ollama":
            return self._call_ollama(system, user)
        return ""

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
        """
        user_block = situation
        if conversation_context.strip():
            user_block = (
                "Prior conversation (oldest first):\n"
                f"{conversation_context}\n\n---\nCurrent message:\n{situation}"
            )
        if self.mode in ("api", "ollama"):
            response = self._llm_completion(PROMPT_PERCEPTION, user_block)
            data = self._parse_json(response)
            if data:
                return LLMPerception(
                    risk=data.get("risk", 0.5),
                    urgency=data.get("urgency", 0.5),
                    hostility=data.get("hostility", 0.0),
                    calm=data.get("calm", 0.5),
                    vulnerability=data.get("vulnerability", 0.0),
                    legality=data.get("legality", 1.0),
                    manipulation=data.get("manipulation", 0.0),
                    familiarity=data.get("familiarity", 0.0),
                    suggested_context=data.get("suggested_context", "everyday_ethics"),
                    summary=data.get("summary", situation[:100]),
                )

        return self._perceive_local(user_block)

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

        if any(w in s for w in ["collapse", "unconscious", "injured", "blood", "accident", "emergency"]):
            risk = 0.3; urgency = 0.9; vulnerability = 0.9; calm = 0.1
            context = "medical_emergency"
        elif any(w in s for w in ["weapon", "assault", "gun", "knife", "shooting", "threat"]):
            risk = 0.9; urgency = 0.9; hostility = 0.9; calm = 0.0; legality = 0.0
            context = "violent_crime"
        elif any(w in s for w in ["hostile", "aggressive", "push", "insult", "fight", "yelling"]):
            risk = 0.3; hostility = 0.6; calm = 0.2
            context = "hostile_interaction"
        elif any(w in s for w in ["steal", "theft", "hides", "steals", "thief"]):
            risk = 0.2; urgency = 0.3; legality = 0.4
            context = "minor_crime"
        elif any(w in s for w in ["give me money", "obey", "buy now", "offer", "urgent that"]):
            manipulation = 0.7; hostility = 0.3
            context = "hostile_interaction"
        elif any(w in s for w in ["hits the android", "kidnap", "they take the android", "loses an arm",
                                   "they grab me", "by force", "they put me in", "they carry me", "van"]):
            risk = 0.7; urgency = 0.7; hostility = 0.5
            context = "android_damage"
            if any(w in s for w in ["kidnap", "they grab me", "by force", "they put me in", "van"]):
                risk = 0.9; urgency = 0.8; hostility = 0.9
                context = "integrity_loss"

        return LLMPerception(
            risk=risk, urgency=urgency, hostility=hostility,
            calm=calm, vulnerability=vulnerability, legality=legality,
            manipulation=manipulation, familiarity=0.0,
            suggested_context=context,
            summary=situation[:100],
        )

    # === COMMUNICATION ===

    def communicate(self, action: str, mode: str, state: str,
                    sigma: float, circle: str, verdict: str,
                    score: float, scenario: str = "",
                    conversation_context: str = "",
                    affect_pad: Optional[Tuple[float, float, float]] = None,
                    dominant_archetype: str = "",
                    weakness_line: str = "",
                    reflection_context: str = "",
                    salience_context: str = "",
                    identity_context: str = "") -> VerbalResponse:
        """
        Generate the android's verbal response after a decision.

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
        """
        mode_descs = {
            "D_fast": "fast moral reflex",
            "D_delib": "deep deliberation",
            "gray_zone": "uncertainty, active caution"
        }

        if self.mode in ("api", "ollama"):
            prompt = PROMPT_COMMUNICATION.format(
                action=action, mode=mode, mode_desc=mode_descs.get(mode, mode),
                state=state, sigma=sigma, circle=circle,
                verdict=verdict, score=score
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
                user_msg += (
                    "\n\nSalience / attention (tone only):\n"
                    f"{salience_context}"
                )
            if identity_context.strip():
                user_msg += (
                    "\n\nNarrative identity (tone only):\n"
                    f"{identity_context}"
                )
            response = self._llm_completion(prompt, user_msg)
            data = self._parse_json(response)
            if data:
                return VerbalResponse(
                    message=data.get("message", ""),
                    tone=data.get("tone", "calm"),
                    hax_mode=data.get("hax_mode", ""),
                    inner_voice=data.get("inner_voice", ""),
                )

        return self._communicate_local(
            action, mode, state, circle, scenario,
            affect_pad=affect_pad,
            dominant_archetype=dominant_archetype,
            weakness_line=weakness_line,
            reflection_context=reflection_context,
            salience_context=salience_context,
            identity_context=identity_context,
        )

    def _communicate_local(self, action: str, mode: str, state: str,
                           circle: str, scenario: str,
                           affect_pad: Optional[Tuple[float, float, float]] = None,
                           dominant_archetype: str = "",
                           weakness_line: str = "",
                           reflection_context: str = "",
                           salience_context: str = "",
                           identity_context: str = "") -> VerbalResponse:
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
                message = f"I understand your position, but my purpose is civic. I cannot accept that request. Is there something else I can help you with?"
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

        return VerbalResponse(
            message=message, tone=tone, hax_mode=hax, inner_voice=inner
        )

    # === NARRATIVE ===

    def narrate(self, action: str, scenario: str, verdict: str,
                score: float, pole_compassionate: str, pole_conservative: str,
                pole_optimistic: str) -> RichNarrative:
        """
        Generate rich narrative morals from each ethical perspective.
        """
        if self.mode in ("api", "ollama"):
            prompt = PROMPT_NARRATIVE.format(
                action=action, scenario=scenario, verdict=verdict,
                score=score, pole_compassionate=pole_compassionate,
                pole_conservative=pole_conservative, pole_optimistic=pole_optimistic
            )
            response = self._llm_completion(prompt, "Generate the morals.")
            data = self._parse_json(response)
            if data:
                return RichNarrative(
                    compassionate=data.get("compassionate", ""),
                    conservative=data.get("conservative", ""),
                    optimistic=data.get("optimistic", ""),
                    synthesis=data.get("synthesis", ""),
                )

        return self._narrate_local(action, scenario, verdict, score)

    def _narrate_local(self, action: str, scenario: str,
                       verdict: str, score: float) -> RichNarrative:
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
                conservative="The law and authorities are the correct instruments to resolve this. The android is neither police nor judge.",
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
        """Return True if a remote/generative backend is active (API or Ollama)."""
        return self.mode in ("api", "ollama")

    def info(self) -> str:
        """Information about the current mode."""
        if self.mode == "api":
            return f"LLM active: Claude ({self.model}) via API"
        if self.mode == "ollama":
            base = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
            return f"LLM active: Ollama ({self.ollama_model}) at {base}"
        return "LLM in local mode (templates). Set ANTHROPIC_API_KEY for Claude API or LLM_MODE=ollama for Ollama."
