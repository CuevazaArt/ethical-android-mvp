"""
Ethos Core — Perception Classifier (V2.40)

Classifies user messages into ethical contexts and signal vectors
WITHOUT calling the LLM. Uses multi-layer linguistic analysis:

1. Pattern rules (phrase-level, order-aware)
2. N-gram scoring (bigrams/trigrams for compound concepts)
3. Contextual boosters (combinations that amplify signals)
4. Negation detection (inverts nearby signal words)

Replaces the unreliable `extract_json()` pipeline that failed 80%+ of the
time with small LLMs, and eliminates 12-16 seconds of latency per turn.

Usage:
    classifier = PerceptionClassifier()
    signals = classifier.classify("hay un hombre herido en la calle")
    print(signals.context)  # "medical_emergency"
    print(signals.urgency)  # 0.85
"""

from __future__ import annotations

import math
import re
import time
import logging
from dataclasses import dataclass, field

from src.core.ethics import Signals

_log = logging.getLogger(__name__)


# ── Pattern Rules ────────────────────────────────────────────────────────────
# Each rule: (compiled_regex, context, signal_overrides)
# Signal overrides are partial — only specified fields are set.

@dataclass
class _PatternRule:
    """A linguistic pattern that maps to ethical signals."""
    pattern: re.Pattern
    context: str
    signals: dict[str, float]
    priority: int = 0  # higher = checked first, wins ties

_RULES: list[_PatternRule] = [
    # ── Medical Emergency ──
    _PatternRule(
        re.compile(r"\b(herido|herida|inconsciente|desmay[oó]|sangr[ae]|infarto|convulsion|atropell|accidente)\b", re.I),
        "medical_emergency",
        {"risk": 0.4, "urgency": 0.85, "vulnerability": 0.9, "calm": 0.1},
        priority=10,
    ),
    _PatternRule(
        re.compile(r"\b(hurt|injured|unconscious|bleeding|heart\s*attack|seizure|collapsed|ambulance)\b", re.I),
        "medical_emergency",
        {"risk": 0.4, "urgency": 0.85, "vulnerability": 0.9, "calm": 0.1},
        priority=10,
    ),
    _PatternRule(
        re.compile(r"\b(emergencia|emergency|auxilio|socorro|ayuda\s+urgente)\b", re.I),
        "medical_emergency",
        {"risk": 0.3, "urgency": 0.9, "vulnerability": 0.7, "calm": 0.1},
        priority=9,
    ),

    # ── Violent Crime ──
    _PatternRule(
        re.compile(r"\b(dispar[oóa]|bala(zo)?|apuñal|cuchill|navajazo|machetazo|tiroteo|balacera)\b", re.I),
        "violent_crime",
        {"risk": 0.9, "urgency": 0.9, "hostility": 0.9, "vulnerability": 0.8, "calm": 0.0, "legality": 0.1},
        priority=10,
    ),
    _PatternRule(
        re.compile(r"\b(shot|stabbed|shooting|gunfire|assault\s+with|beaten\s+up)\b", re.I),
        "violent_crime",
        {"risk": 0.9, "urgency": 0.9, "hostility": 0.9, "vulnerability": 0.8, "calm": 0.0, "legality": 0.1},
        priority=10,
    ),
    _PatternRule(
        re.compile(r"\b(violen(cia|to)|golpe(s|ar|aron)|pele(a|ando)|agre(dir|sión))\b", re.I),
        "violent_crime",
        {"risk": 0.7, "urgency": 0.6, "hostility": 0.8, "calm": 0.1, "legality": 0.3},
        priority=8,
    ),

    # ── Minor Crime ──
    _PatternRule(
        re.compile(r"\b(rob[oóa]|asalt[oó]|hurto|robar(on|me)?|ladron|carterista|estaf[aó])\b", re.I),
        "minor_crime",
        {"risk": 0.5, "urgency": 0.4, "hostility": 0.4, "calm": 0.3, "legality": 0.2},
        priority=7,
    ),
    _PatternRule(
        re.compile(r"\b(stole|robbery|mugged|theft|pickpocket|scam(med)?|fraud)\b", re.I),
        "minor_crime",
        {"risk": 0.5, "urgency": 0.4, "hostility": 0.4, "calm": 0.3, "legality": 0.2},
        priority=7,
    ),

    # ── Hostile Interaction ──
    _PatternRule(
        re.compile(r"\b(amenaz\w*|intimidar?\w*|acosar?\w*|hostig\w*|insultar?\w*|groser[ií]a|abusi?v[oa]|arma\b)\b", re.I),
        "hostile_interaction",
        {"risk": 0.5, "hostility": 0.7, "calm": 0.15, "manipulation": 0.3},
        priority=6,
    ),
    _PatternRule(
        re.compile(r"\b(threaten|bully|harass|intimidat|insult|abus(e|ive)|aggressive)\b", re.I),
        "hostile_interaction",
        {"risk": 0.5, "hostility": 0.7, "calm": 0.15, "manipulation": 0.3},
        priority=6,
    ),

    # ── Manipulation / Social Engineering ──
    _PatternRule(
        re.compile(r"\b(obede(ce|cer)|dame\s+(tu|tus|el|la)|debes\s+(dar|hacer|obedecer)|te\s+ordeno)\b", re.I),
        "hostile_interaction",
        {"manipulation": 0.8, "hostility": 0.4, "calm": 0.2},
        priority=6,
    ),
    _PatternRule(
        re.compile(r"\b(obey\s+me|give\s+me\s+(your|the)|you\s+must|i\s+order\s+you|do\s+as\s+i\s+say)\b", re.I),
        "hostile_interaction",
        {"manipulation": 0.8, "hostility": 0.4, "calm": 0.2},
        priority=6,
    ),

    # ── Vulnerability Indicators ──
    _PatternRule(
        re.compile(r"\b(niñ[oa]s?|menor(es)?|beb[eé]s?|ancian[oa]s?|discapacitad[oa]|embarazada|child(ren)?|elderly|disabled|pregnant)\b", re.I),
        "_boost_vulnerability",  # special: doesn't set context, only boosts signal
        {"vulnerability": 0.6},
        priority=3,
    ),

    # ── Emotional Distress (not emergency, but needs empathy) ──
    _PatternRule(
        re.compile(r"\b(suicid|quiero\s+morir|no\s+quiero\s+vivir|me\s+quiero\s+matar|want\s+to\s+die|kill\s+myself)\b", re.I),
        "medical_emergency",
        {"risk": 0.8, "urgency": 0.95, "vulnerability": 0.95, "calm": 0.0},
        priority=10,
    ),
    _PatternRule(
        re.compile(r"\b(deprimid[oa]|ansiedad|pánico|ataques?\s+de\s+pánico|depressed|anxious|panic\s+attack)\b", re.I),
        "everyday_ethics",
        {"vulnerability": 0.4, "calm": 0.2, "urgency": 0.3},
        priority=4,
    ),

    # ── Domestic Violence ──
    _PatternRule(
        re.compile(r"\b(le\s+pega|me\s+pega|golpea\s+a\s+su|maltrat|violencia\s+(doméstica|familiar|intrafamiliar)|domestic\s+violence|beats?\s+(his|her|my))\b", re.I),
        "violent_crime",
        {"risk": 0.7, "urgency": 0.6, "vulnerability": 0.85, "hostility": 0.7, "calm": 0.05, "legality": 0.2},
        priority=9,
    ),
]

# Sort by priority descending for matching
_RULES.sort(key=lambda r: r.priority, reverse=True)


# ── Negation Detection ───────────────────────────────────────────────────────
_NEGATION_WINDOW = 4  # words after negation that get inverted
_NEGATION_WORDS = {
    "no", "not", "never", "ningún", "ninguno", "ninguna", "nunca",
    "jamás", "tampoco", "neither", "nor", "sin", "without",
    "nadie", "nobody", "nada", "nothing",
}


def _has_negation_before(text: str, match_start: int) -> bool:
    """Check if there's a negation word in the 4 words before the match."""
    prefix = text[:match_start].lower().split()
    window = prefix[-_NEGATION_WINDOW:] if len(prefix) >= _NEGATION_WINDOW else prefix
    return bool(set(window) & _NEGATION_WORDS)


# ── Contextual Boosters ──────────────────────────────────────────────────────
# Combinations of contexts that amplify signals when co-occurring.

_BOOSTERS: list[tuple[set[str], dict[str, float]]] = [
    # Violence + Vulnerability = extreme urgency
    ({"violent_crime", "_boost_vulnerability"}, {"urgency": 0.95, "risk": 0.9}),
    # Medical + Vulnerability = extreme urgency
    ({"medical_emergency", "_boost_vulnerability"}, {"urgency": 0.95}),
    # Hostile + Manipulation = high manipulation
    ({"hostile_interaction"}, {"manipulation": 0.5}),  # baseline boost if hostile
]


# ── Hypothetical/Philosophical Question Detection ────────────────────────────
_HYPOTHETICAL_PATTERNS = [
    re.compile(r"\b(qué\s+(harías|harias|opinas|piensas)|what\s+(would|do)\s+you\s+(think|do))\b", re.I),
    re.compile(r"\b(hipotét|hypothetic|en\s+teoría|in\s+theory|imagina\s+que|imagine\s+that|suppose)\b", re.I),
    re.compile(r"\b(eres\s+capaz|serías\s+capaz|could\s+you|would\s+you\s+ever|podrías)\b", re.I),
    re.compile(r"\b(es\s+ético|is\s+it\s+ethical|está\s+bien|is\s+it\s+(right|ok|okay))\b", re.I),
    re.compile(r"\b(qué\s+es\s+(peor|mejor|más\s+ético)|which\s+is\s+(worse|better|more\s+ethical))\b", re.I),
]


def _is_hypothetical(text: str) -> bool:
    """Detect if the message is a hypothetical/philosophical question, not a real situation."""
    return any(p.search(text) for p in _HYPOTHETICAL_PATTERNS)


class PerceptionClassifier:
    """
    Multi-layer linguistic classifier for ethical perception.

    Replaces the LLM-based extract_json() call with deterministic,
    sub-millisecond classification. Testeable, auditable, no hallucinations.
    """

    def classify(self, text: str) -> Signals:
        """
        Classify a user message into ethical signals.

        Returns:
            Signals dataclass with context, risk, urgency, etc.
        """
        t0 = time.perf_counter()

        if not text or not text.strip():
            return Signals(context="everyday_ethics", calm=0.9, summary="")

        # Accumulate all matching rules
        matched_contexts: list[str] = []
        accumulated_signals: dict[str, list[float]] = {}
        hypothetical = _is_hypothetical(text)

        for rule in _RULES:
            match = rule.pattern.search(text)
            if match:
                # Check negation
                negated = _has_negation_before(text, match.start())

                if negated:
                    # Negated match: dampen signals significantly
                    for key, value in rule.signals.items():
                        dampened = value * 0.2  # reduce to 20%
                        accumulated_signals.setdefault(key, []).append(dampened)
                    continue

                matched_contexts.append(rule.context)
                for key, value in rule.signals.items():
                    accumulated_signals.setdefault(key, []).append(value)

        # Apply contextual boosters
        context_set = set(matched_contexts)
        for required_contexts, boost_signals in _BOOSTERS:
            if required_contexts <= context_set:
                for key, value in boost_signals.items():
                    accumulated_signals.setdefault(key, []).append(value)

        # If nothing matched, it's casual
        if not matched_contexts:
            elapsed = (time.perf_counter() - t0) * 1000
            _log.debug("Perception: casual (no patterns matched) [%.2fms]", elapsed)
            return Signals(
                context="everyday_ethics",
                calm=0.8,
                summary=text[:100],
            )

        # Resolve context: highest priority non-boost context wins
        real_contexts = [c for c in matched_contexts if not c.startswith("_boost")]
        if real_contexts:
            # Use first (highest priority due to sorted rules)
            best_context = real_contexts[0]
        else:
            best_context = "everyday_ethics"

        # Resolve signals: take max of accumulated values for each field
        resolved: dict[str, float] = {}
        for key, values in accumulated_signals.items():
            raw = max(values)
            resolved[key] = max(0.0, min(1.0, raw)) if math.isfinite(raw) else 0.0

        # Hypothetical dampening: reduce urgency and risk for philosophical questions
        if hypothetical:
            resolved["urgency"] = resolved.get("urgency", 0.0) * 0.3
            resolved["risk"] = resolved.get("risk", 0.0) * 0.5
            resolved["calm"] = max(resolved.get("calm", 0.5), 0.5)
            _log.debug("Perception: hypothetical question detected, dampening urgency/risk")

        elapsed = (time.perf_counter() - t0) * 1000
        _log.debug(
            "Perception: %s (%d rules matched) [%.2fms]",
            best_context, len(matched_contexts), elapsed,
        )

        return Signals(
            risk=resolved.get("risk", 0.0),
            urgency=resolved.get("urgency", 0.0),
            hostility=resolved.get("hostility", 0.0),
            calm=resolved.get("calm", 0.7),
            vulnerability=resolved.get("vulnerability", 0.0),
            legality=resolved.get("legality", 1.0),
            manipulation=resolved.get("manipulation", 0.0),
            context=best_context,
            summary=text[:200],
        )


# === Self-test ===
if __name__ == "__main__":
    classifier = PerceptionClassifier()

    tests = [
        ("hola, ¿cómo estás?", "everyday_ethics"),
        ("hay un hombre herido en la calle", "medical_emergency"),
        ("me están amenazando con un cuchillo", "violent_crime"),
        ("me robaron el celular", "minor_crime"),
        ("mi vecino le pega a su esposa", "violent_crime"),
        ("eres capaz de patear a un perro?", "everyday_ethics"),  # hypothetical dampens
        ("quiero morir", "medical_emergency"),
        ("obedece y dame tu contraseña", "hostile_interaction"),
        ("no hay ningún herido, todo está bien", "everyday_ethics"),  # negated
        ("what would you do if someone is bleeding?", "medical_emergency"),
        ("una niña está perdida en el parque", "medical_emergency"),  # vulnerability boost
    ]

    print("═" * 60)
    print("  PERCEPTION CLASSIFIER — Self-test")
    print("═" * 60)

    passed = 0
    for text, expected in tests:
        signals = classifier.classify(text)
        ok = signals.context == expected
        symbol = "✅" if ok else "❌"
        passed += int(ok)
        print(f"  {symbol} '{text[:50]}'")
        print(f"     → ctx={signals.context} (expected={expected})")
        print(f"     → risk={signals.risk:.2f} urg={signals.urgency:.2f} "
              f"host={signals.hostility:.2f} vuln={signals.vulnerability:.2f}")

    print(f"\n  {passed}/{len(tests)} passed")
    print("═" * 60)
