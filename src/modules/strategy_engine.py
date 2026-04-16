"""
Executive Strategy Engine — Planning and Mission Management.

Transitions from passive goal hints to active mission tracking and tactical selection.
Supports Self-generated missions (identity-driven) and External missions (owner-driven).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class MissionStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUCCESS = "success"
    FAILED = "failed"
    ABANDONED = "abandoned"


class MissionOrigin(Enum):
    SELF = "self"  # Intrinsically motivated (curiosity/identity)
    OWNER = "owner"  # Assigned by Uchi/Operator
    SYSTEM = "system"  # Assigned by DAO/Nucleo


@dataclass
class Mission:
    id: str
    title: str
    origin: MissionOrigin
    status: MissionStatus = MissionStatus.ACTIVE
    steps: list[str] = field(default_factory=list)
    completed_steps: list[str] = field(default_factory=list)
    priority: float = 0.5
    created_at: float = field(default_factory=lambda: 0.0)


class ExecutiveStrategist:
    """
    Mental core for task completion and strategic prioritization.
    """

    def __init__(self, max_missions: int = 5):
        self.missions: dict[str, Mission] = {}
        self.max_missions = max_missions

    def create_mission(
        self,
        title: str,
        origin: MissionOrigin,
        steps: list[str] | None = None,
        priority: float = 0.5,
    ) -> Mission | None:
        if len(self.missions) >= self.max_missions:
            completed = [
                m.id
                for m in self.missions.values()
                if m.status in (MissionStatus.SUCCESS, MissionStatus.FAILED)
            ]
            if completed:
                del self.missions[completed[0]]
            else:
                return None

        m_id = f"msn_{uuid.uuid4().hex[:8]}"
        m = Mission(id=m_id, title=title, origin=origin, steps=steps or [], priority=priority)
        self.missions[m_id] = m
        return m

    def evaluate_strategic_alignment(
        self, action_desc: str, active_mission_id: str = None
    ) -> float:
        """
        Calculates how much an action aligns with current missions.
        """
        if not active_mission_id and not self.missions:
            return 0.0

        target_mission = self.missions.get(active_mission_id) if active_mission_id else None
        if not target_mission:
            active = sorted(
                [m for m in self.missions.values() if m.status == MissionStatus.ACTIVE],
                key=lambda x: -x.priority,
            )
            if not active:
                return 0.0
            target_mission = active[0]

        action_l = action_desc.lower()
        match_score = 0.0

        if any(word in action_l for word in target_mission.title.lower().split() if len(word) > 3):
            match_score += 0.4

        remaining_steps = [
            s for s in target_mission.steps if s not in target_mission.completed_steps
        ]
        if remaining_steps:
            if any(
                word in action_l
                for s in remaining_steps
                for word in s.lower().split()
                if len(word) > 3
            ):
                match_score += 0.6

        return min(1.0, match_score)

    def update_mission_progress(self, mission_id: str, completed_step: str):
        if mission_id in self.missions:
            m = self.missions[mission_id]
            if completed_step in m.steps and completed_step not in m.completed_steps:
                m.completed_steps.append(completed_step)
                if len(m.completed_steps) == len(m.steps):
                    m.status = MissionStatus.SUCCESS
                else:
                    m.status = MissionStatus.ACTIVE

    def active_missions_summary(self) -> str:
        active = [m for m in self.missions.values() if m.status == MissionStatus.ACTIVE]
        if not active:
            return "No active missions."
        summary = "Active Missions: " + " | ".join(
            [f"{m.title} ({len(m.completed_steps)}/{len(m.steps)})" for m in active]
        )
        return summary
