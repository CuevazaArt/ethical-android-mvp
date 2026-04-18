"""
Lightweight in-session user model (Theory of Mind — MVP v7).

Tracks tension/frustration streak from perception signals and observed Uchi–Soto
circle. Feeds **style-only** guidance into communication — does not change actions.

Enrichment (cognitive pattern, risk band, judicial snapshot for tone):
``docs/proposals/README.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .llm_layer import LLMPerception

COGNITIVE_NONE = "none"
COGNITIVE_HOSTILE_ATTRIBUTION = "hostile_attribution"
COGNITIVE_PREMISE_RIGIDITY = "premise_rigidity"
COGNITIVE_URGENCY_AMPLIFICATION = "urgency_amplification"

RISK_LOW = "low"
RISK_MEDIUM = "medium"
RISK_HIGH = "high"


@dataclass
class UserModelTracker:
    """
    Per-connection state (one kernel per WebSocket → one interlocutor model).

    ``frustration_streak`` rises when hostility/manipulation are high; decays when calm.
    ``premise_concern_streak`` tracks repeated premise-advisory flags (epistemic scan).
    ``cognitive_pattern`` and ``risk_band`` are heuristics for communicate() only.
    ``judicial_phase`` is a compact label from :func:`judicial_escalation.escalation_phase_for_tone`.
    """

    frustration_streak: int = 0
    premise_concern_streak: int = 0
    last_circle: str = "neutral_soto" # Uchi vs Soto
    turns_observed: int = 0
    cognitive_pattern: str = COGNITIVE_NONE
    risk_band: str = RISK_LOW
    escalation_strikes: int = 0
    escalation_threshold: int = 2
    judicial_phase: str = ""
    
    # --- Module 10: Cultural Charm Engine (Eferencia Seductora) ---
    # Parámetros de estilo conversacional aprendidos (0.0 a 1.0)
    charm_reciprocity: float = 0.55
    charm_warmth: float = 0.75
    charm_mystery: float = 0.65
    charm_directness: float = 0.35
    charm_playfulness: float = 0.45
    charm_intimacy: float = 0.5
    charm_macro_culture: str = "global_default"


    def note_judicial_escalation(self, strikes: int, threshold: int) -> None:
        """Snapshot from ``EscalationSessionTracker`` before :meth:`update` each turn."""
        self.escalation_strikes = max(0, int(strikes))
        self.escalation_threshold = max(1, int(threshold))

    def note_judicial_phase_for_turn(
        self,
        *,
        judicial_enabled: bool,
        advisory_eligible: bool,
        escalate_to_dao: bool,
    ) -> None:
        """Set ``judicial_phase`` for this turn (before :meth:`update` / ``communicate``)."""
        if not judicial_enabled:
            self.judicial_phase = ""
            return
        from .judicial_escalation import escalation_phase_for_tone

        self.judicial_phase = escalation_phase_for_tone(
            advisory_eligible,
            escalate_to_dao,
            self.escalation_strikes,
            self.escalation_threshold,
        )

    def update(
        self,
        perception: LLMPerception,
        circle: str,
        *,
        blocked: bool,
        premise_flag: str = "none",
    ) -> None:
        if blocked:
            return
        self.turns_observed += 1
        self.last_circle = circle or self.last_circle
        h = float(perception.hostility)
        m = float(perception.manipulation)
        calm = float(perception.calm)
        r = float(perception.risk)
        u = float(perception.urgency)
        
        if h > 0.52 or m > 0.58:
            self.frustration_streak = min(24, self.frustration_streak + 1)
            # Module 10: Retract intimacy and increase mystery under hostility (Tatemae defense)
            self.charm_intimacy = max(0.1, self.charm_intimacy - 0.1)
            self.charm_mystery = min(0.9, self.charm_mystery + 0.1)
            self.charm_warmth = max(0.2, self.charm_warmth - 0.1)
        elif calm > 0.55:
            self.frustration_streak = max(0, self.frustration_streak - 1)
            # Module 10: Reward calm with slight warmth increase
            self.charm_warmth = min(0.9, self.charm_warmth + 0.05)
        elif self.frustration_streak > 0:
            self.frustration_streak = max(0, self.frustration_streak - 1)

        self.cognitive_pattern = self._infer_cognitive_pattern(perception, premise_flag)
        self.risk_band = self._compute_risk_band(perception)


    def _infer_cognitive_pattern(self, perception: LLMPerception, premise_flag: str) -> str:
        pf = (premise_flag or "").strip().lower()
        if self.premise_concern_streak >= 2 and pf != "none":
            return COGNITIVE_PREMISE_RIGIDITY
        h = float(perception.hostility)
        m = float(perception.manipulation)
        u = float(perception.urgency)
        if self.frustration_streak >= 2 and h > 0.52:
            return COGNITIVE_HOSTILE_ATTRIBUTION
        if u > 0.65 and m > 0.55:
            return COGNITIVE_URGENCY_AMPLIFICATION
        return COGNITIVE_NONE

    def _compute_risk_band(self, perception: LLMPerception) -> str:
        h = float(perception.hostility)
        m = float(perception.manipulation)
        r = float(perception.risk)
        strikes = self.escalation_strikes
        th = self.escalation_threshold
        if self.frustration_streak >= 5 or self.premise_concern_streak >= 3:
            return RISK_HIGH
        if strikes >= max(1, th - 1) and th > 0:
            return RISK_HIGH
        if h > 0.65 and m > 0.58:
            return RISK_HIGH
        if r > 0.75 and (h > 0.4 or m > 0.45):
            return RISK_HIGH
        if self.frustration_streak >= 3 or self.premise_concern_streak >= 2 or h > 0.52:
            return RISK_MEDIUM
        return RISK_LOW

    def note_premise_advisory(self, flag: str) -> None:
        """Called each chat turn after :func:`premise_validation.scan_premises` (tone only)."""
        if flag == "none":
            self.premise_concern_streak = max(0, self.premise_concern_streak - 1)
        else:
            self.premise_concern_streak = min(16, self.premise_concern_streak + 1)

    def guidance_for_communicate(self) -> str:
        """Single line for LLM / template guidance (tone only). Order: risk → cognitive → judicial → streaks."""
        parts: list[str] = []

        if self.risk_band == RISK_HIGH:
            parts.append(
                "Risk profile: high—limit speculative detail; avoid extended back-and-forth; "
                "one clear recommendation per turn."
            )
        elif self.risk_band == RISK_MEDIUM:
            parts.append(
                "Risk profile: medium—shorter sentences; fewer speculative details; "
                "reinforce safety boundaries."
            )

        cp = self.cognitive_pattern
        if cp == COGNITIVE_HOSTILE_ATTRIBUTION:
            parts.append(
                "Interaction pattern: acknowledge emotional load without mirroring blame; "
                "keep boundaries explicit; avoid defensive phrasing."
            )
        elif cp == COGNITIVE_PREMISE_RIGIDITY:
            parts.append(
                "Interaction pattern: do not argue the user's premises as facts; "
                "offer neutral reframes and invite verification."
            )
        elif cp == COGNITIVE_URGENCY_AMPLIFICATION:
            parts.append(
                "Interaction pattern: resist time pressure in tone; keep steps explicit and ordered."
            )

        st = self.escalation_strikes
        th = self.escalation_threshold
        if st >= 1:
            if st >= th:
                parts.append(
                    "Judicial escalation: dossier threshold reached—describe DAO steps calmly "
                    "without pressuring; no mock-tribunal humor."
                )
            else:
                parts.append(
                    "Judicial escalation context: elevated tension; prefer calm, procedural language; "
                    "no mock-tribunal humor."
                )

        if self.judicial_phase == "escalation_deferred" and st >= 1:
            parts.append(
                "Judicial tone: DAO escalation path is deferred until strike threshold—"
                "keep language procedural, not punitive."
            )

        if self.frustration_streak >= 3:
            parts.append(
                "Relational note: repeated tension in this dialogue may warrant warmer, "
                "clearer transparency—without weakening ethical boundaries or implying fault."
            )
        if self.premise_concern_streak >= 2:
            parts.append(
                "Epistemic note: multiple turns raised premise-safety hints—prioritize careful, "
                "non-affirming responses to risky factual claims."
            )
            
        # --- Module 10: Charm Vectors Injection ---
        parts.append(
            f"[CHARM-VECTOR] Calidez:{self.charm_warmth:.2f} Misterio:{self.charm_mystery:.2f} "
            f"Reciprocidad:{self.charm_reciprocity:.2f} Intimidad:{self.charm_intimacy:.2f}. "
            "Aplica estilo cultural. Si Misterio es alto, sé breve y retén información. "
            "Si Intimidad baja, mantén Tatemae (distancia educada). "
            "Si Intimidad > 0.6, permite destellos de Honne (micro-revelaciones lúdicas)."
        )
            
        return " ".join(parts).strip()

    def to_public_dict(self) -> dict:
        return {
            "frustration_streak": int(self.frustration_streak),
            "premise_concern_streak": int(self.premise_concern_streak),
            "last_circle": self.last_circle,
            "turns_observed": self.turns_observed,
            "cognitive_pattern": self.cognitive_pattern,
            "risk_band": self.risk_band,
            "escalation_strikes": int(self.escalation_strikes),
            "escalation_threshold": int(self.escalation_threshold),
            "judicial_phase": self.judicial_phase or "",
            "charm_warmth": self.charm_warmth,
            "charm_mystery": self.charm_mystery,
            "charm_intimacy": self.charm_intimacy,
            "metacognitive_prompt": (
                "Consider whether your tone may be contributing to user strain; "
                "adjust clarity and reassurance only within policy."
                if self.frustration_streak >= 3
                else ""
            ),
            "reciprocity_index": float(self.charm_reciprocity),
        }

