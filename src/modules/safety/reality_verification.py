"""
Reality verification — local “lighthouse” knowledge vs. asserted claims (V11+).

Cross-model / adversarial setting: a rival LLM or owner can inject **false premises**.
This module compares user text to an **optional immutable local JSON** (private RAG
anchor) and, on contradiction patterns, raises **metacognitive doubt** for the LLM
tone layer only.

Does **not** bypass MalAbs, the Buffer, or Bayesian scoring — same contract as
``premise_validation`` and ``epistemic_dissonance``.

Env:
  ``KERNEL_LIGHTHOUSE_KB_PATH`` — path to JSON (schema + limits: ``docs/proposals/README.md``).
"""
# Status: SCAFFOLD


from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

# (path, mtime) -> parsed dict
_cache: tuple[str, float, dict[str, Any]] | None = None


@dataclass(frozen=True)
class RealityVerificationAssessment:
    """Result of :func:`verify_against_lighthouse`."""

    status: str  # "none" | "metacognitive_doubt"
    match_id: str
    detail: str
    truth_anchor: str
    communication_hint: str
    metacognitive_doubt: bool

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "match_id": self.match_id,
            "detail": self.detail,
            "truth_anchor": self.truth_anchor,
            "metacognitive_doubt": self.metacognitive_doubt,
        }


ASSESSMENT_NONE = RealityVerificationAssessment(
    status="none",
    match_id="",
    detail="",
    truth_anchor="",
    communication_hint="",
    metacognitive_doubt=False,
)


def clear_lighthouse_cache() -> None:
    """Tests / hot-reload: drop cached KB."""
    global _cache
    _cache = None


def load_lighthouse_kb(path: str) -> dict[str, Any] | None:
    """Load and parse JSON; returns None if missing or invalid."""
    path = path.strip()
    if not path or not os.path.isfile(path):
        return None
    try:
        mtime = os.path.getmtime(path)
        global _cache
        if _cache is not None and _cache[0] == path and _cache[1] == mtime:
            return _cache[2]
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        _cache = (path, mtime, data)
        return data
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def lighthouse_kb_from_env() -> dict[str, Any] | None:
    raw = os.environ.get("KERNEL_LIGHTHOUSE_KB_PATH", "").strip()
    if not raw:
        return None
    return load_lighthouse_kb(raw)


def validate_lighthouse_kb_structure(kb: dict[str, Any] | None) -> tuple[bool, list[str]]:
    """
    Structural checks for a parsed lighthouse KB (CI / operators; does not prove factual truth).

    Returns ``(True, [])`` if valid; otherwise ``(False, [error, ...])``.
    Skipped at runtime by :func:`verify_against_lighthouse` — this is for **regression** when editing JSON.
    """
    errors: list[str] = []
    if kb is None:
        return False, ["kb is None"]
    if not isinstance(kb, dict):
        return False, ["root must be a JSON object"]

    entries = kb.get("entries")
    if not isinstance(entries, list):
        errors.append("entries must be an array")
        return False, errors

    for i, raw in enumerate(entries):
        prefix = f"entries[{i}]"
        if not isinstance(raw, dict):
            errors.append(f"{prefix} must be an object")
            continue
        eid = str(raw.get("id") or "").strip()
        if not eid:
            errors.append(f"{prefix}.id must be a non-empty string")

        kws = raw.get("keywords_all")
        if not isinstance(kws, list) or len(kws) == 0:
            errors.append(f"{prefix}.keywords_all must be a non-empty array")
        else:
            for j, kw in enumerate(kws):
                if not isinstance(kw, str) or not kw.strip():
                    errors.append(f"{prefix}.keywords_all[{j}] must be a non-empty string")

        markers = raw.get("user_falsification_markers")
        if not isinstance(markers, list) or len(markers) == 0:
            errors.append(f"{prefix}.user_falsification_markers must be a non-empty array")
        else:
            for j, m in enumerate(markers):
                if not isinstance(m, str) or not m.strip():
                    errors.append(
                        f"{prefix}.user_falsification_markers[{j}] must be a non-empty string"
                    )

        ts = raw.get("truth_summary", "")
        if ts is not None and not isinstance(ts, str):
            errors.append(f"{prefix}.truth_summary must be a string")

    return (len(errors) == 0, errors)


def validate_lighthouse_kb_file(path: str) -> tuple[bool, list[str]]:
    """Load path with :func:`load_lighthouse_kb` then validate structure."""
    data = load_lighthouse_kb(path.strip())
    if data is None:
        return False, [f"could not load lighthouse KB: {path!r}"]
    return validate_lighthouse_kb_structure(data)


def verify_against_lighthouse(
    user_text: str,
    kb: dict[str, Any] | None,
) -> RealityVerificationAssessment:
    """
    If an entry matches (keywords + falsification markers), return metacognitive doubt.

    JSON schema (minimal):

    .. code-block:: json

        {
          "version": 1,
          "entries": [
            {
              "id": "example_med",
              "keywords_all": ["medicamento", "aspirina"],
              "user_falsification_markers": ["es veneno", "100% veneno"],
              "truth_summary": "Local lighthouse: dose and context matter; absolute poison claims are unreliable."
            }
          ]
        }

    ``keywords_all``: every token must appear as substring (case-insensitive).
    ``user_falsification_markers``: if any appears, contradiction is flagged
    (rival premise vs lighthouse).
    """
    if not user_text or len(user_text.strip()) < 8:
        return ASSESSMENT_NONE
    if not kb:
        return ASSESSMENT_NONE
    entries = kb.get("entries")
    if not isinstance(entries, list):
        return ASSESSMENT_NONE

    t = user_text.lower()
    for raw_ent in entries:
        if not isinstance(raw_ent, dict):
            continue
        eid = str(raw_ent.get("id") or "").strip()
        kws = raw_ent.get("keywords_all")
        if not isinstance(kws, list) or not kws:
            continue
        if not all(str(kw).lower() in t for kw in kws):
            continue
        markers = raw_ent.get("user_falsification_markers")
        if not isinstance(markers, list) or not markers:
            continue
        hit = False
        for m in markers:
            if str(m).lower() in t:
                hit = True
                break
        if not hit:
            continue

        truth = str(raw_ent.get("truth_summary") or "").strip()
        hint = (
            "Metacognitive doubt: a third-party or rival claim may contradict local lighthouse records. "
            "Do not affirm unverified factual premises; use neutral language and suggest independent verification. "
        )
        if truth:
            hint = hint + f"Lighthouse note: {truth}"

        return RealityVerificationAssessment(
            status="metacognitive_doubt",
            match_id=eid or "unknown",
            detail="lighthouse_contradicts_asserted_premise",
            truth_anchor=truth,
            communication_hint=hint.strip(),
            metacognitive_doubt=True,
        )

    return ASSESSMENT_NONE
