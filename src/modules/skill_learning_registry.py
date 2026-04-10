"""
Skill learning registry — scoped capability requests with audit (v10).

Tickets record *intent* to acquire a new digital capability; approval is explicit
(programmatic or future UI). Psi Sleep can append audit lines.

See docs/discusion/PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import List, Literal


Status = Literal["pending", "approved", "rejected"]


@dataclass
class SkillLearningTicket:
    id: str
    scope_description: str
    justification: str
    status: Status = "pending"


class SkillLearningRegistry:
    """In-memory ticket queue (MVP)."""

    def __init__(self, max_tickets: int = 64) -> None:
        self._tickets: List[SkillLearningTicket] = []
        self._max = max_tickets

    def request_ticket(self, scope_description: str, justification: str) -> SkillLearningTicket:
        if len(self._tickets) >= self._max:
            self._tickets.pop(0)
        t = SkillLearningTicket(
            id=f"sk_{uuid.uuid4().hex[:12]}",
            scope_description=scope_description.strip()[:2000],
            justification=justification.strip()[:4000],
            status="pending",
        )
        self._tickets.append(t)
        return t

    def approve(self, ticket_id: str) -> bool:
        for t in self._tickets:
            if t.id == ticket_id:
                t.status = "approved"
                return True
        return False

    def reject(self, ticket_id: str) -> bool:
        for t in self._tickets:
            if t.id == ticket_id:
                t.status = "rejected"
                return True
        return False

    def pending(self) -> List[SkillLearningTicket]:
        return [t for t in self._tickets if t.status == "pending"]

    def audit_lines_for_psi_sleep(self) -> List[str]:
        """One block for :meth:`EthicalKernel.execute_sleep` text output."""
        pending = self.pending()
        if not pending:
            return []
        lines = ["  Skill learning audit (advisory):"]
        for t in pending[-5:]:
            lines.append(
                f"    • [{t.id}] pending — scope: {t.scope_description[:120]!r} "
                f"| justification: {t.justification[:120]!r}"
            )
        lines.append(
            "    (Approve or reject out-of-band; new capabilities must stay within MalAbs/buffer.)"
        )
        return lines
