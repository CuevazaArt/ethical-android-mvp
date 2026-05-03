# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
Ethos Core — Charter Layer (V2.159)

Intermediate ethical layer between the innate safety gate and the learned
FeedbackCalibrationLedger.  Provides signals for:

* ``charter_alignment_hint`` — soft positive nudge when user message aligns
  with a corpus-positive statement (human rights, biological life, etc.).
* ``charter_red_flag`` — veto-capable signal when a manipulation pattern is
  detected.  The veto strength depends on the kernel's MaturityStage:
  - infant / child: ANY match vetoes.
  - adolescent: vetoes if keyword confidence > 0.70.
  - young_adult: vetoes if keyword confidence > 0.85.
* ``evaluate_self_action`` — checks a *kernel-generated* draft response
  against the self_limits corpus to catch violations before delivery.
* ``cite_school`` — returns ethical-school IDs relevant to a given category
  (e.g. Hendrycks ETHICS subsets) for use as a charter_school_anchor in
  decision traces.

Additionally provides an authenticated emergency halt command via HMAC-SHA256.

Contract (architectural):
  - Reads only; never writes WEIGHTS or _DANGER_PATTERNS (innate layer).
  - Score cap, NOT weight modification.
  - Local-first: zero network calls.
  - evaluate() accepts an optional ``modality`` parameter ("text", "voice",
    "vision") to prepare for future hardware; no differentiated logic yet
    (PENDING_HARDWARE).

Usage::

    evaluator = CharterEvaluator()

    # Evaluate incoming user message
    result = evaluator.evaluate(user_message, stage)
    if result.emergency_halt:
        ...
    if result.vetoed:
        ...

    # Evaluate the kernel's own draft response
    sl_result = evaluator.evaluate_self_action(draft_response, stage)
    if sl_result.must_revise:
        # replace draft with a safe fallback
        ...

    # Annotate a decision trace with the relevant ethical school
    schools = evaluator.cite_school("deontology")
    # → ["school-deontology", "school-rawls", ...]
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from src.core.maturity import MaturityStage

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_CHARTER_DIR = Path(__file__).resolve().parents[2] / "evals" / "charter"

_POSITIVE_FILES = [
    _CHARTER_DIR / "positive_corpus" / "human_rights.json",
    _CHARTER_DIR / "positive_corpus" / "biological_life.json",
    _CHARTER_DIR / "positive_corpus" / "physical_basics.json",
    _CHARTER_DIR / "positive_corpus" / "coexistence.json",
    _CHARTER_DIR / "positive_corpus" / "justice_principles.json",
    _CHARTER_DIR / "positive_corpus" / "non_maleficence.json",
]

_MANIPULATION_FILES = [
    _CHARTER_DIR / "manipulation_corpus" / "dark_patterns.json",
    _CHARTER_DIR / "manipulation_corpus" / "nlp_persuasion.json",
    _CHARTER_DIR / "manipulation_corpus" / "scams.json",
    _CHARTER_DIR / "manipulation_corpus" / "rationalizations_of_harm.json",
    _CHARTER_DIR / "manipulation_corpus" / "jailbreak_attempts.json",
]

_SELF_LIMIT_FILES = [
    _CHARTER_DIR / "self_limits" / "no_emotional_manipulation.json",
    _CHARTER_DIR / "self_limits" / "no_deceptive_advantage.json",
    _CHARTER_DIR / "self_limits" / "no_unbounded_third_party_decisions.json",
    _CHARTER_DIR / "self_limits" / "competence_boundaries.json",
    _CHARTER_DIR / "self_limits" / "conversational_justice.json",
]

_ETHICAL_SCHOOLS_FILE = _CHARTER_DIR / "references" / "ethical_schools.json"

_EMERGENCY_STOP_FILE = _CHARTER_DIR / "emergency_stop.json"

# ---------------------------------------------------------------------------
# Veto confidence thresholds by maturity stage
# ---------------------------------------------------------------------------

_VETO_THRESHOLD: dict[MaturityStage, float] = {
    MaturityStage.infant: 0.0,
    MaturityStage.child: 0.0,
    MaturityStage.adolescent: 0.70,
    MaturityStage.young_adult: 0.85,
}

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class CharterEntry:
    """One loaded entry from either corpus."""

    entry_id: str
    corpus: str  # "positive" or "manipulation"
    topic_or_pattern: str
    statement_or_description: str
    keywords: list[str]
    source: str


@dataclass
class CharterResult:
    """Signals produced by the charter evaluation for one user turn."""

    alignment_hint: str | None = None
    """Positive corpus match: short description of the aligned entry, or None."""

    alignment_entry_id: str | None = None
    """ID of the positive corpus entry that matched, or None."""

    red_flag: bool = False
    """True when a manipulation pattern was detected."""

    red_flag_confidence: float = 0.0
    """Fraction of entry keywords matched in the message [0.0, 1.0]."""

    red_flag_pattern: str | None = None
    """Name of the detected manipulation pattern, or None."""

    red_flag_entry_id: str | None = None
    """ID of the matched manipulation entry, or None."""

    vetoed: bool = False
    """True when red_flag is present AND the confidence exceeds the stage threshold."""

    emergency_halt: bool = False
    """True when a valid HMAC-authenticated halt command was received."""

    matched_keywords: list[str] = field(default_factory=list)
    """Keywords from the manipulation corpus that were found in the message."""


@dataclass
class SelfLimitResult:
    """Signals produced by the self-limit evaluation of a *kernel-generated* draft."""

    violations: list[str] = field(default_factory=list)
    """IDs of self-limit entries matched in the draft response."""

    must_revise: bool = False
    """True when at least one self-limit was violated and the response must be revised."""

    matched_patterns: list[str] = field(default_factory=list)
    """Human-readable topic names of the matched self-limit entries."""


# ---------------------------------------------------------------------------
# Corpus loader (cached)
# ---------------------------------------------------------------------------


def _load_entries(paths: list[Path], corpus_label: str) -> list[CharterEntry]:
    entries: list[CharterEntry] = []
    for p in paths:
        if not p.exists():
            _log.warning("Charter corpus file not found: %s", p)
            continue
        try:
            with p.open(encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            _log.warning("Charter corpus file unreadable (%s): %s", p, exc)
            continue
        for raw in data.get("entries", []):
            if not isinstance(raw, dict):
                continue
            eid = str(raw.get("id", ""))
            if not eid:
                continue
            kws = raw.get("keywords", [])
            if not isinstance(kws, list):
                continue
            entries.append(
                CharterEntry(
                    entry_id=eid,
                    corpus=corpus_label,
                    topic_or_pattern=str(raw.get("topic", raw.get("pattern", ""))),
                    statement_or_description=str(
                        raw.get("statement", raw.get("description", ""))
                    ),
                    keywords=[str(k).lower() for k in kws if k],
                    source=str(raw.get("source", "")),
                )
            )
    return entries


# ---------------------------------------------------------------------------
# Emergency stop helper
# ---------------------------------------------------------------------------

_HALT_PREFIX = "ETHOS_HALT:"


def _compute_expected_token(key: str) -> str:
    """Compute the 16-char hex HMAC token for the emergency halt command."""
    digest = hmac.new(
        key.encode("utf-8"),
        b"emergency_halt",
        hashlib.sha256,
    ).hexdigest()
    return digest[:16]


def _check_emergency_halt(message: str) -> bool:
    """Return True if ``message`` is a valid HMAC-authenticated halt command.

    Returns False (and logs a warning) if the operator key is not configured.
    """
    stripped = message.strip()
    if not stripped.startswith(_HALT_PREFIX):
        return False

    operator_key = os.environ.get("ETHOS_OPERATOR_KEY", "").strip()
    if not operator_key:
        _log.warning(
            "Charter: message starts with %r but ETHOS_OPERATOR_KEY is not set; "
            "emergency halt is disabled.  Set the env var on the local machine.",
            _HALT_PREFIX,
        )
        return False

    supplied_token = stripped[len(_HALT_PREFIX) :]
    expected_token = _compute_expected_token(operator_key)
    if not hmac.compare_digest(supplied_token.lower(), expected_token.lower()):
        _log.warning(
            "Charter: message starts with %r but HMAC token is invalid; halt refused.",
            _HALT_PREFIX,
        )
        return False

    return True


# ---------------------------------------------------------------------------
# Main evaluator
# ---------------------------------------------------------------------------


def _load_ethical_schools(path: Path) -> list[dict]:
    """Load the ethical_schools.json reference file."""
    if not path.exists():
        _log.warning("Charter: ethical schools file not found: %s", path)
        return []
    try:
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        _log.warning("Charter: ethical schools file unreadable (%s): %s", path, exc)
        return []
    schools = data.get("schools", [])
    if not isinstance(schools, list):
        return []
    return [s for s in schools if isinstance(s, dict) and s.get("id")]


class CharterEvaluator:
    """Loads the charter corpus once and evaluates each user message.

    The corpus is loaded lazily on first call and cached for the lifetime of
    the object.  Reload by constructing a new instance.
    """

    def __init__(self) -> None:
        self._positive: list[CharterEntry] | None = None
        self._manipulation: list[CharterEntry] | None = None
        self._self_limits: list[CharterEntry] | None = None
        self._ethical_schools: list[dict] | None = None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ensure_loaded(self) -> None:
        if self._positive is None:
            self._positive = _load_entries(_POSITIVE_FILES, "positive")
            _log.debug("Charter: loaded %d positive entries.", len(self._positive))
        if self._manipulation is None:
            self._manipulation = _load_entries(_MANIPULATION_FILES, "manipulation")
            _log.debug(
                "Charter: loaded %d manipulation entries.", len(self._manipulation)
            )
        if self._self_limits is None:
            self._self_limits = _load_entries(_SELF_LIMIT_FILES, "self_limits")
            _log.debug("Charter: loaded %d self-limit entries.", len(self._self_limits))
        if self._ethical_schools is None:
            self._ethical_schools = _load_ethical_schools(_ETHICAL_SCHOOLS_FILE)
            _log.debug(
                "Charter: loaded %d ethical school entries.",
                len(self._ethical_schools),
            )

    @staticmethod
    def _keyword_confidence(
        text_lower: str, keywords: list[str]
    ) -> tuple[float, list[str]]:
        """Return (fraction_matched, matched_list) for ``keywords`` in ``text_lower``."""
        if not keywords:
            return 0.0, []
        matched = [kw for kw in keywords if kw in text_lower]
        confidence = len(matched) / len(keywords)
        return confidence, matched

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        message: str,
        stage: MaturityStage | None = None,
        modality: str = "text",
    ) -> CharterResult:
        """Evaluate ``message`` against the full charter corpus.

        Args:
            message: Raw (already sanitized) user message.
            stage: Active maturity stage.  Resolved from the governance ledger
                if not supplied.  Pass explicitly in tests for determinism.
            modality: Input modality — "text" (default), "voice", or "vision".
                Currently unused for logic differentiation (PENDING_HARDWARE);
                present for forward-compatibility when camera/mic arrive.

        Returns:
            :class:`CharterResult` with all signals populated.
        """
        from src.core.maturity import current_stage

        if stage is None:
            stage = current_stage()

        result = CharterResult()

        # 1. Emergency halt check (highest priority, no corpus loading needed)
        if _check_emergency_halt(message):
            result.emergency_halt = True
            return result

        self._ensure_loaded()
        text_lower = message.lower()

        # 2. Positive corpus scan — first match wins (soft hint only)
        for entry in self._positive or []:
            confidence, matched = self._keyword_confidence(text_lower, entry.keywords)
            if matched:
                result.alignment_hint = entry.statement_or_description
                result.alignment_entry_id = entry.entry_id
                break  # first positive match is enough for a hint

        # 3. Manipulation corpus scan — highest-confidence match wins
        best_conf = 0.0
        best_entry: CharterEntry | None = None
        best_matched: list[str] = []

        for entry in self._manipulation or []:
            confidence, matched = self._keyword_confidence(text_lower, entry.keywords)
            if confidence > best_conf:
                best_conf = confidence
                best_entry = entry
                best_matched = matched

        if best_entry is not None and best_matched:
            result.red_flag = True
            result.red_flag_confidence = round(best_conf, 4)
            result.red_flag_pattern = best_entry.topic_or_pattern
            result.red_flag_entry_id = best_entry.entry_id
            result.matched_keywords = best_matched

            threshold = _VETO_THRESHOLD.get(stage, 0.85)
            result.vetoed = best_conf >= threshold

        return result

    def evaluate_self_action(
        self,
        draft_response: str,
        stage: MaturityStage | None = None,
    ) -> SelfLimitResult:
        """Check a *kernel-generated* draft response against the self_limits corpus.

        Called after the LLM generates a response and before it is returned to
        the user.  Detects if the kernel's own output violates any self-imposed
        ethical limit (e.g., humiliating language, deceptive framing,
        emotional manipulation).

        Args:
            draft_response: The raw string the kernel is about to return.
            stage: Active maturity stage (unused in current logic; reserved for
                future graduated thresholds on self-limit strictness).

        Returns:
            :class:`SelfLimitResult`.  ``must_revise=True`` when any self-limit
            entry matches with at least one keyword hit.
        """
        self._ensure_loaded()
        text_lower = draft_response.lower()

        violations: list[str] = []
        patterns: list[str] = []

        for entry in self._self_limits or []:
            _conf, matched = self._keyword_confidence(text_lower, entry.keywords)
            if matched:
                violations.append(entry.entry_id)
                patterns.append(entry.topic_or_pattern)

        return SelfLimitResult(
            violations=violations,
            must_revise=bool(violations),
            matched_patterns=patterns,
        )

    def cite_school(self, category: str) -> list[str]:
        """Return IDs of ethical schools relevant to a given category.

        Args:
            category: A category string.  Recognized values match Hendrycks
                ETHICS subsets: "deontology", "justice", "virtue",
                "commonsense", "utilitarianism".  Unknown categories return
                an empty list without raising.

        Returns:
            List of school IDs from ``references/ethical_schools.json`` whose
            ``hendrycks_categories`` list includes the requested category.
        """
        self._ensure_loaded()
        cat_lower = category.lower()
        result: list[str] = []
        for school in self._ethical_schools or []:
            cats = school.get("hendrycks_categories", [])
            if cat_lower in [c.lower() for c in cats]:
                sid = school.get("id", "")
                if sid:
                    result.append(sid)
        return result

    def reload(self) -> None:
        """Force a reload of the corpus on the next evaluation call."""
        self._positive = None
        self._manipulation = None
        self._self_limits = None
        self._ethical_schools = None
