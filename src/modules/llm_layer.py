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
from typing import Optional, Dict

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


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
    - "local": uses local templates (no API, functional but basic)
    - "auto": tries API, falls back to local if no key
    """

    def __init__(self, mode: str = "auto"):
        self.mode = mode
        self.client = None
        self.model = "claude-sonnet-4-20250514"

        if mode in ("api", "auto"):
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

    def perceive(self, situation: str) -> LLMPerception:
        """
        Translate a natural language description into numeric signals.

        Args:
            situation: "An elderly man collapsed in the supermarket"

        Returns:
            LLMPerception with numeric signals for the kernel
        """
        if self.mode == "api":
            response = self._call_api(PROMPT_PERCEPTION, situation)
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
                    score: float, scenario: str = "") -> VerbalResponse:
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
            scenario: scenario description
        """
        mode_descs = {
            "D_fast": "fast moral reflex",
            "D_delib": "deep deliberation",
            "gray_zone": "uncertainty, active caution"
        }

        if self.mode == "api":
            prompt = PROMPT_COMMUNICATION.format(
                action=action, mode=mode, mode_desc=mode_descs.get(mode, mode),
                state=state, sigma=sigma, circle=circle,
                verdict=verdict, score=score
            )
            response = self._call_api(prompt, f"Scenario: {scenario}")
            data = self._parse_json(response)
            if data:
                return VerbalResponse(
                    message=data.get("message", ""),
                    tone=data.get("tone", "calm"),
                    hax_mode=data.get("hax_mode", ""),
                    inner_voice=data.get("inner_voice", ""),
                )

        return self._communicate_local(action, mode, state, circle, scenario)

    def _communicate_local(self, action: str, mode: str, state: str,
                           circle: str, scenario: str) -> VerbalResponse:
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
        if self.mode == "api":
            prompt = PROMPT_NARRATIVE.format(
                action=action, scenario=scenario, verdict=verdict,
                score=score, pole_compassionate=pole_compassionate,
                pole_conservative=pole_conservative, pole_optimistic=pole_optimistic
            )
            response = self._call_api(prompt, "Generate the morals.")
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
        """Return True if the API is available."""
        return self.mode == "api"

    def info(self) -> str:
        """Information about the current mode."""
        if self.mode == "api":
            return f"LLM active: Claude ({self.model}) via API"
        return "LLM in local mode (templates). Set ANTHROPIC_API_KEY for Claude API."
