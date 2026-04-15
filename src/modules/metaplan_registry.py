"""
Metaplan registry — long-horizon owner goals (advisory hints for LLM) (v10).

In-RAM master goals for the session; persisted via :class:`~src.persistence.schema.KernelSnapshotV1`
(``metaplan_goals``) since vertical Phase 2.

Optional **drive-intent filtering** (v9.4 / trace): when ``KERNEL_METAPLAN_DRIVE_FILTER=1`` and at
least one goal exists, :class:`~src.modules.drive_arbiter.DriveIntent` entries with no lexical overlap
against goal titles are dropped **only if** some other intent overlaps — otherwise the list is
unchanged (safe fallback). Advisory-only; does not alter MalAbs or scoring.

See docs/proposals/README.md
"""

from __future__ import annotations

import os
import re
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .drive_arbiter import DriveIntent


def metaplan_hints_enabled() -> bool:
    v = os.environ.get("KERNEL_METAPLAN_HINT", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def metaplan_drive_filter_enabled() -> bool:
    """Filter :class:`DriveIntent` lists against registered goals (opt-in; default off)."""
    v = os.environ.get("KERNEL_METAPLAN_DRIVE_FILTER", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def metaplan_drive_extra_intent_enabled() -> bool:
    """Append a low-priority coherence hint when goals exist (opt-in; default off)."""
    v = os.environ.get("KERNEL_METAPLAN_DRIVE_EXTRA", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


_STOP = frozenset(
    {
        "a",
        "an",
        "and",
        "as",
        "at",
        "be",
        "by",
        "for",
        "if",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "so",
        "the",
        "to",
        "with",
    }
)


def _tokens(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", s.lower())) - _STOP


@dataclass
class MasterGoal:
    id: str
    title: str
    priority: float  # [0, 1]


def goal_token_union(goals: list[MasterGoal]) -> set[str]:
    u: set[str] = set()
    for g in goals:
        u |= _tokens(g.title)
    return u


def apply_drive_intent_metaplan_filter(
    intents: list[DriveIntent],
    goals: list[MasterGoal],
    *,
    max_intents: int = 4,
) -> list[DriveIntent]:
    """
    Drop drive intents with **no** token overlap with any ``MasterGoal.title`` when at least one
    intent has overlap; if no intent overlaps, return the original list (fallback).
    """
    if not metaplan_drive_filter_enabled() or not goals:
        return intents[:max_intents]
    gl = goal_token_union(goals)
    if not gl:
        return intents[:max_intents]

    scored: list[tuple] = []
    for di in intents:
        it = _tokens(di.suggest.replace("_", " ") + " " + di.reason)
        rel = (len(it & gl) / max(1, len(it))) if it else 0.0
        scored.append((di, rel))

    if not any(rel > 0 for _, rel in scored):
        return intents[:max_intents]

    kept = [di for di, rel in scored if rel > 0]
    kept.sort(key=lambda x: -x.priority)
    return kept[:max_intents]


def maybe_append_metaplan_drive_extra(
    intents: list[DriveIntent],
    goals: list[MasterGoal],
    *,
    max_intents: int = 4,
) -> list[DriveIntent]:
    """Append a low-priority coherence intent when opted in and there is room."""
    if not metaplan_drive_extra_intent_enabled() or not goals:
        return intents[:max_intents]
    if len(intents) >= max_intents:
        return intents[:max_intents]
    from .drive_arbiter import DriveIntent

    extra = DriveIntent(
        suggest="reflect_metaplan_coherence",
        reason=(
            "Advisory: periodically reconcile drive suggestions with registered master goals; "
            "no effect on kernel policy."
        ),
        priority=0.12,
    )
    merged = list(intents) + [extra]
    return merged[:max_intents]


class MetaplanRegistry:
    """Lightweight goal list; no execution — tone alignment only."""

    def __init__(self, max_goals: int = 16) -> None:
        self._goals: list[MasterGoal] = []
        self._max = max_goals

    def add_goal(self, title: str, priority: float = 0.6) -> MasterGoal:
        if len(self._goals) >= self._max:
            self._goals.pop(0)
        g = MasterGoal(
            id=f"mg_{uuid.uuid4().hex[:10]}",
            title=title.strip()[:500],
            priority=max(0.0, min(1.0, float(priority))),
        )
        self._goals.append(g)
        return g

    def clear(self) -> None:
        self._goals.clear()

    def replace_goals(self, goals: list[MasterGoal]) -> None:
        """Restore from snapshot (checkpoint); caps at ``_max``."""
        self._goals = goals[: self._max]

    def goals(self) -> list[MasterGoal]:
        return list(self._goals)

    def hint_for_communicate(self) -> str:
        if not metaplan_hints_enabled() or not self._goals:
            return ""
        top = sorted(self._goals, key=lambda g: g.priority, reverse=True)[:3]
        titles = "; ".join(g.title for g in top)
        return (
            f"Long-horizon owner goals in scope (advisory, subordinate to kernel ethics): {titles}. "
            f"Favor micro-decisions that remain coherent with these stated priorities when possible."
        )

    def consent_note_drive_filter(self) -> str:
        """Short operator-facing note when drive filtering is enabled (for logs / UX copy)."""
        if not metaplan_drive_filter_enabled():
            return ""
        return (
            "Drive advisory intents may be filtered against registered master goals "
            "(KERNEL_METAPLAN_DRIVE_FILTER); operator opted in — advisory only."
        )
