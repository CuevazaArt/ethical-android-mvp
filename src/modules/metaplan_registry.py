"""
Metaplan registry — long-horizon owner goals (advisory hints for LLM) (v10).

In-RAM master goals for the session; checkpoint persistence is future work.

See docs/discusion/PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from typing import List


def metaplan_hints_enabled() -> bool:
    v = os.environ.get("KERNEL_METAPLAN_HINT", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


@dataclass
class MasterGoal:
    id: str
    title: str
    priority: float  # [0, 1]


class MetaplanRegistry:
    """Lightweight goal list; no execution — tone alignment only."""

    def __init__(self, max_goals: int = 16) -> None:
        self._goals: List[MasterGoal] = []
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

    def goals(self) -> List[MasterGoal]:
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
