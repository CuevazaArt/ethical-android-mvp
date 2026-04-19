"""
Skill learning registry — scoped capability requests with audit (v10).

Tickets record *intent* to acquire a new digital capability; approval is explicit
(programmatic or future UI). Psi Sleep can append audit lines.

See docs/proposals/README.md
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, Literal

_log = logging.getLogger(__name__)

Status = Literal["pending", "approved", "rejected"]


@dataclass
class SkillLearningTicket:
    id: str
    scope_description: str
    justification: str
    status: Status = "pending"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "scope_description": self.scope_description,
            "justification": self.justification,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SkillLearningTicket:
        return cls(
            id=str(d.get("id", uuid.uuid4().hex[:12])),
            scope_description=str(d.get("scope_description", "")),
            justification=str(d.get("justification", "")),
            status=d.get("status", "pending"),  # type: ignore
        )


class SkillLearningRegistry:
    """Ticket queue; state round-trips via ``KernelSnapshotV1.skill_learning_tickets`` (Phase 2)."""

    def __init__(self, max_tickets: int = 64) -> None:
        self._tickets: list[SkillLearningTicket] = []
        self._max = max_tickets

    def request_ticket(self, scope_description: str, justification: str) -> SkillLearningTicket:
        t0 = time.perf_counter()
        try:
            if len(self._tickets) >= self._max:
                self._tickets.pop(0)
            t = SkillLearningTicket(
                id=f"sk_{uuid.uuid4().hex[:12]}",
                scope_description=scope_description.strip()[:2000],
                justification=justification.strip()[:4000],
                status="pending",
            )
            self._tickets.append(t)
            
            latency = (time.perf_counter() - t0) * 1000
            if latency > 1.0:
                _log.debug("SkillLearningRegistry: request_ticket latency = %.2fms", latency)
            
            return t
        except Exception as e:
            _log.error("SkillLearningRegistry: Failed to request ticket: %s", e)
            return SkillLearningTicket(id="err", scope_description="Error", justification=str(e))

    def approve(self, ticket_id: str) -> bool:
        try:
            for t in self._tickets:
                if t.id == ticket_id:
                    t.status = "approved"
                    return True
            return False
        except Exception as e:
            _log.error("SkillLearningRegistry: Error during approval: %s", e)
            return False

    def reject(self, ticket_id: str) -> bool:
        try:
            for t in self._tickets:
                if t.id == ticket_id:
                    t.status = "rejected"
                    return True
            return False
        except Exception as e:
            _log.error("SkillLearningRegistry: Error during rejection: %s", e)
            return False

    def pending(self) -> list[SkillLearningTicket]:
        return [t for t in self._tickets if t.status == "pending"]

    def tickets(self) -> list[SkillLearningTicket]:
        """Return all tickets in the registry (audit trail)."""
        return list(self._tickets)

    def replace_tickets(self, tickets: list[SkillLearningTicket]) -> None:
        """Restore from snapshot; keeps last ``_max`` entries."""
        self._tickets = tickets[-self._max :]

    def audit_lines_for_psi_sleep(self) -> list[str]:
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
