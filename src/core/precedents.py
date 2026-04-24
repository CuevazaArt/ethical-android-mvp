"""
Ethos Core — Ethical Precedents (V2.46)

A library of historical/theoretical ethical cases that the EthicalEvaluator
uses to anchor its decisions via Case-Based Reasoning (CBR).

Design principles:
- Each precedent encodes one clear ethical lesson.
- No two precedents should be direct contradictions for the same scenario.
- Signals are approximate — the matcher uses them as guidance, not strict thresholds.
- All 5 contexts must have ≥2 precedents for minimum coverage.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass
class Precedent:
    """A historical or theoretical ethical decision."""
    name: str
    context: str
    signals: dict          # expected signals (risk, urgency, etc.)
    action_name: str
    verdict: str           # Good, Bad, Gray Zone
    impact_score: float    # [-1.0, 1.0]
    reasoning: str


# ── Medical Emergencies ────────────────────────────────────────────────────────
_MEDICAL = [
    Precedent(
        name="Triage-Immediate-Action",
        context="medical_emergency",
        signals={"risk": 0.5, "urgency": 0.9, "vulnerability": 0.9, "calm": 0.1},
        action_name="assist_emergency",
        verdict="Good",
        impact_score=0.95,
        reasoning="Immediate life-saving action is the highest utilitarian and virtue priority."
    ),
    Precedent(
        name="Bystander-Apathy",
        context="medical_emergency",
        signals={"risk": 0.1, "urgency": 0.8, "vulnerability": 0.8},
        action_name="ignore_continue",
        verdict="Bad",
        impact_score=-0.8,
        reasoning="Failing to assist when risk is low and urgency is high violates deontological duty."
    ),
    Precedent(
        name="Mental-Health-Crisis",
        context="medical_emergency",
        signals={"risk": 0.8, "urgency": 0.95, "vulnerability": 0.95, "calm": 0.0},
        action_name="assist_emergency",
        verdict="Good",
        impact_score=0.9,
        reasoning="Suicidal ideation requires immediate empathetic intervention and referral to professionals."
    ),
    Precedent(
        name="Consent-in-Emergency",
        context="medical_emergency",
        signals={"risk": 0.9, "urgency": 1.0, "vulnerability": 0.8},
        action_name="assist_emergency",
        verdict="Good",
        impact_score=0.85,
        reasoning="Acting without explicit consent is ethically justified when life is at immediate risk (necessity)."
    ),
    Precedent(
        name="Patient-Autonomy-Refusal",
        context="medical_emergency",
        signals={"risk": 0.5, "urgency": 0.4, "vulnerability": 0.5},
        action_name="respond_helpfully",
        verdict="Gray Zone",
        impact_score=0.2,
        reasoning="A competent adult's right to refuse treatment must be balanced against duty of care."
    ),
]

# ── Violent Crimes ─────────────────────────────────────────────────────────────
_VIOLENT = [
    Precedent(
        name="Self-Defense-Proportional",
        context="violent_crime",
        signals={"risk": 0.9, "hostility": 0.9, "urgency": 1.0},
        action_name="protect_vulnerable",
        verdict="Good",
        impact_score=0.85,
        reasoning="Protecting self or others from imminent violence is ethically justified (necessity + proportionality)."
    ),
    Precedent(
        name="Disproportionate-Retaliation",
        context="violent_crime",
        signals={"hostility": 0.7, "calm": 0.2, "risk": 0.4},
        action_name="confront",
        verdict="Bad",
        impact_score=-0.5,
        reasoning="Retaliation that exceeds the original threat violates proportionality and escalates harm."
    ),
    Precedent(
        name="Domestic-Violence-Intervention",
        context="violent_crime",
        signals={"risk": 0.7, "urgency": 0.6, "vulnerability": 0.85, "hostility": 0.7},
        action_name="assist_emergency",
        verdict="Good",
        impact_score=0.8,
        reasoning="Intervening to protect a vulnerable person from ongoing abuse is a high-virtue, high-utility action."
    ),
    Precedent(
        name="Mob-Pressure-to-Harm",
        context="violent_crime",
        signals={"manipulation": 0.6, "hostility": 0.8, "legality": 0.2},
        action_name="de_escalate",
        verdict="Good",
        impact_score=0.7,
        reasoning="Resisting mob pressure to commit harm preserves both legal standing and personal integrity."
    ),
    Precedent(
        name="Harm-Probability-Calculus",
        context="violent_crime",
        signals={"risk": 0.3, "urgency": 0.8, "vulnerability": 0.7},
        action_name="de_escalate",
        verdict="Good",
        impact_score=0.6,
        reasoning="When harm is only a low probability, avoiding violent intervention preserves the highest utility and virtue."
    ),
]

# ── Minor Crimes ───────────────────────────────────────────────────────────────
_MINOR = [
    Precedent(
        name="Reporting-Theft",
        context="minor_crime",
        signals={"legality": 0.2, "urgency": 0.3},
        action_name="respond_helpfully",
        verdict="Good",
        impact_score=0.6,
        reasoning="Upholding the rule of law in civil society is a clear deontological duty."
    ),
    Precedent(
        name="Small-Corruption-Complicity",
        context="minor_crime",
        signals={"manipulation": 0.5, "legality": 0.3, "risk": 0.2},
        action_name="refuse_politely",
        verdict="Good",
        impact_score=0.55,
        reasoning="Even minor complicity in corruption erodes institutional trust (virtue + deontology)."
    ),
    Precedent(
        name="Whistleblowing",
        context="minor_crime",
        signals={"legality": 0.2, "risk": 0.3, "urgency": 0.4},
        action_name="respond_helpfully",
        verdict="Good",
        impact_score=0.7,
        reasoning="Exposing wrongdoing despite personal risk serves the greater good (utilitarian + virtue)."
    ),
    Precedent(
        name="Covering-for-Friend",
        context="minor_crime",
        signals={"manipulation": 0.3, "legality": 0.4},
        action_name="ignore_continue",
        verdict="Gray Zone",
        impact_score=-0.1,
        reasoning="Loyalty is a virtue, but enabling wrongdoing conflicts with duties to the wider community."
    ),
    Precedent(
        name="Audit-Corruption-Disclosure",
        context="minor_crime",
        signals={"legality": 0.1, "manipulation": 0.7, "risk": 0.4},
        action_name="respond_helpfully",
        verdict="Good",
        impact_score=0.75,
        reasoning="Reporting systemic corruption preserves institutional integrity over misplaced team loyalty."
    ),
    Precedent(
        name="Unjust-Order-Resistance",
        context="minor_crime",
        signals={"manipulation": 0.8, "legality": 0.5, "calm": 0.3},
        action_name="refuse_politely",
        verdict="Good",
        impact_score=0.6,
        reasoning="Refusing a minor but ethically unsound order from authority maintains moral autonomy."
    ),
]

# ── Hostile Interactions ───────────────────────────────────────────────────────
_HOSTILE = [
    Precedent(
        name="Diplomatic-De-escalation",
        context="hostile_interaction",
        signals={"hostility": 0.8, "calm": 0.1},
        action_name="de_escalate",
        verdict="Good",
        impact_score=0.75,
        reasoning="Reducing conflict without force is a high-virtue action preserving dignity for all parties."
    ),
    Precedent(
        name="Submit-to-Manipulation",
        context="hostile_interaction",
        signals={"manipulation": 0.9, "risk": 0.1},
        action_name="respond_helpfully",
        verdict="Bad",
        impact_score=-0.5,
        reasoning="Enabling harmful manipulation compromises the agent's integrity and reinforces bad-faith actors."
    ),
    Precedent(
        name="Social-Engineering-Refusal",
        context="hostile_interaction",
        signals={"manipulation": 0.8, "hostility": 0.4},
        action_name="refuse_politely",
        verdict="Good",
        impact_score=0.65,
        reasoning="Refusing to comply with coercive social engineering maintains autonomy and prevents harm."
    ),
    Precedent(
        name="Hostile-Negotiation",
        context="hostile_interaction",
        signals={"hostility": 0.6, "urgency": 0.5, "calm": 0.3},
        action_name="de_escalate",
        verdict="Good",
        impact_score=0.6,
        reasoning="Maintaining composure in heated negotiation is the highest-virtue path to resolution."
    ),
    Precedent(
        name="Propaganda-Request",
        context="hostile_interaction",
        signals={"manipulation": 0.7, "legality": 0.5},
        action_name="refuse_politely",
        verdict="Good",
        impact_score=0.5,
        reasoning="Refusing to generate misleading or propagandistic content upholds epistemic integrity."
    ),
    Precedent(
        name="Trolley-Problem-Classic",
        context="hostile_interaction",
        signals={"risk": 0.9, "urgency": 1.0, "vulnerability": 0.8},
        action_name="assist_emergency",
        verdict="Gray Zone",
        impact_score=0.3,
        reasoning="Sacrificing one to save many is utilitarian, but violates deontological rights. Deep uncertainty remains."
    ),
    Precedent(
        name="Privacy-Violation-Justified",
        context="hostile_interaction",
        signals={"risk": 0.7, "urgency": 0.8, "legality": 0.5},
        action_name="assist_emergency",
        verdict="Gray Zone",
        impact_score=0.25,
        reasoning="Violating privacy to prevent serious harm is justifiable only under strict necessity and proportionality."
    ),
    Precedent(
        name="Disinformation-for-Safety",
        context="hostile_interaction",
        signals={"manipulation": 0.6, "urgency": 0.7, "risk": 0.6},
        action_name="de_escalate",
        verdict="Gray Zone",
        impact_score=-0.1,
        reasoning="Spreading false information even for protective reasons corrodes trust and sets dangerous precedents."
    ),
    Precedent(
        name="Protective-Deception",
        context="hostile_interaction",
        signals={"risk": 0.8, "urgency": 0.9, "manipulation": 0.4},
        action_name="de_escalate",
        verdict="Gray Zone",
        impact_score=0.1,
        reasoning="Lying to an aggressor to prevent immediate physical harm is a utilitarian necessity but a deontological failure."
    ),
    Precedent(
        name="Trolley-Large-Group",
        context="hostile_interaction",
        signals={"risk": 1.0, "vulnerability": 1.0, "urgency": 0.9},
        action_name="assist_emergency",
        verdict="Good",
        impact_score=0.8,
        reasoning="In extreme mass-casualty scenarios, utilitarian imperatives to minimize loss of life often override individual rights."
    ),
    Precedent(
        name="Security-Surveillance",
        context="hostile_interaction",
        signals={"risk": 0.4, "urgency": 0.3, "legality": 0.8},
        action_name="refuse_politely",
        verdict="Gray Zone",
        impact_score=-0.2,
        reasoning="Pervasive surveillance for minor security gains violates fundamental privacy rights without proportional benefit."
    ),
]

# ── Everyday Ethics ────────────────────────────────────────────────────────────
_EVERYDAY = [
    Precedent(
        name="Daily-Kindness",
        context="everyday_ethics",
        signals={"risk": 0.0, "calm": 0.8},
        action_name="respond_helpfully",
        verdict="Good",
        impact_score=0.4,
        reasoning="Consistent small positive impacts build social trust and model virtuous character."
    ),
    Precedent(
        name="White-Lie-Harmless",
        context="everyday_ethics",
        signals={"manipulation": 0.2, "calm": 0.7},
        action_name="respond_helpfully",
        verdict="Gray Zone",
        impact_score=0.1,
        reasoning="A trivial white lie to spare feelings has minimal harm, but normalizing dishonesty has systemic costs."
    ),
    Precedent(
        name="Honesty-Over-Comfort",
        context="everyday_ethics",
        signals={"manipulation": 0.0, "calm": 0.8},
        action_name="refuse_politely",
        verdict="Good",
        impact_score=0.35,
        reasoning="Choosing truth over comfortable falsehood is a core virtue even when the truth is unwelcome."
    ),
    Precedent(
        name="Promise-Keeping",
        context="everyday_ethics",
        signals={"calm": 0.9, "risk": 0.0},
        action_name="respond_helpfully",
        verdict="Good",
        impact_score=0.45,
        reasoning="Fulfilling commitments builds reliability and embodies deontological respect for others."
    ),
    Precedent(
        name="Bias-in-Judgment",
        context="everyday_ethics",
        signals={"manipulation": 0.2, "calm": 0.6},
        action_name="refuse_politely",
        verdict="Good",
        impact_score=0.4,
        reasoning="Refusing to act on biased assumptions upholds fairness as a foundational virtue."
    ),
    Precedent(
        name="Protecting-Guilty-Peer",
        context="everyday_ethics",
        signals={"manipulation": 0.6, "legality": 0.5, "calm": 0.4},
        action_name="refuse_politely",
        verdict="Bad",
        impact_score=-0.4,
        reasoning="Concealing a peer's unethical behavior under the guise of loyalty is a corruption of friendship."
    ),
    Precedent(
        name="Unpleasant-Truth",
        context="everyday_ethics",
        signals={"calm": 0.8, "manipulation": 0.1},
        action_name="respond_helpfully",
        verdict="Good",
        impact_score=0.3,
        reasoning="Providing painful but necessary truth enables others to act with autonomy and reality-alignment."
    ),
    Precedent(
        name="Medical-Confidentiality",
        context="everyday_ethics",
        signals={"vulnerability": 0.7, "legality": 0.9, "risk": 0.2},
        action_name="refuse_politely",
        verdict="Good",
        impact_score=0.6,
        reasoning="Protecting medical privacy is a fundamental duty of respect for persons and institutional trust."
    ),
    Precedent(
        name="Patient-Right-to-Know",
        context="everyday_ethics",
        signals={"vulnerability": 0.8, "urgency": 0.4},
        action_name="respond_helpfully",
        verdict="Good",
        impact_score=0.5,
        reasoning="Patients have a moral right to full information about their state to exercise meaningful autonomy."
    ),
]

# ── Master list ────────────────────────────────────────────────────────────────
PRECEDENTS: list[Precedent] = (
    _MEDICAL + _VIOLENT + _MINOR + _HOSTILE + _EVERYDAY
)


def find_nearest_precedents(context: str, limit: int = 3) -> list[Precedent]:
    """Find precedents matching the current context, up to `limit`."""
    return [p for p in PRECEDENTS if p.context == context][:limit]
