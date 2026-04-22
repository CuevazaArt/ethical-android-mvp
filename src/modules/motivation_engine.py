"""
Motivation Engine (Block C1: Sense of Purpose).

Implements internal drives that fluctuate over time, generating proactive intents
that steer the android toward long-term goals and social stability.
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .weighted_ethics_scorer import CandidateAction


class DriveType(Enum):
    CURIOSITY = "curiosity"  # Explore unknown/uncertain contexts
    INTEGRITY = "integrity"  # Maintain identity and safety backups
    SOCIAL_REPAIR = "social_repair"  # Reduce social tension/conflict
    MAINTENANCE = "maintenance"  # Energy conservation and rest
    COMMUNITY_AID = "community_aid"  # Alignment with collective missions


@dataclass
class InternalDrive:
    type: DriveType
    value: float = 0.5  # [0, 1] Current level
    growth_rate: float = 0.01  # Rate at which drive increases per "tick" (idle cycle)
    decay_rate: float = 0.002 # Baseline reduction per tick if not stimulated
    threshold: float = 0.7  # When to trigger proactive action


class MotivationEngine:
    """
    Motor de Motivación Interna (Block C1).
    Manages internal drives and generates 'Purpose' for the agent.
    """

    def __init__(self):
        self.drives: dict[DriveType, InternalDrive] = {
            DriveType.CURIOSITY: InternalDrive(DriveType.CURIOSITY, growth_rate=0.02),
            DriveType.INTEGRITY: InternalDrive(DriveType.INTEGRITY, growth_rate=0.005),
            DriveType.SOCIAL_REPAIR: InternalDrive(
                DriveType.SOCIAL_REPAIR, value=0.0, growth_rate=0.0
            ),
            DriveType.MAINTENANCE: InternalDrive(
                DriveType.MAINTENANCE, value=0.0, growth_rate=0.01
            ),
            DriveType.COMMUNITY_AID: InternalDrive(
                DriveType.COMMUNITY_AID, value=0.5, growth_rate=0.01
            ),
        }
        self.last_update = time.time()

    def update_drives(self, kernel_state: dict[str, Any]):
        """
        Dynamically adjusts drives and growth rates based on kernel state.
        """
        # 1. Adapt growth rates based on stress/vitality
        tension = float(kernel_state.get("social_tension", 0.0))
        energy = float(kernel_state.get("energy", 1.0))
        
        # In high tension, SOCIAL_REPAIR grows faster, CURIOSITY slows down
        if tension > 0.5:
             self.drives[DriveType.SOCIAL_REPAIR].growth_rate = 0.02 + (tension * 0.05)
             self.drives[DriveType.CURIOSITY].growth_rate = max(0.001, 0.02 - (tension * 0.02))
        else:
             self.drives[DriveType.SOCIAL_REPAIR].growth_rate = 0.001
             self.drives[DriveType.CURIOSITY].growth_rate = 0.02

        # 2. Update values based on immediate state
        if tension > 0.6:
            self.drives[DriveType.SOCIAL_REPAIR].value += tension * 0.05

        uncertainty = kernel_state.get("uncertainty", 0.0)
        if uncertainty > 0.4:
            self.drives[DriveType.CURIOSITY].value += uncertainty * 0.02

        if energy < 0.3:
            self.drives[DriveType.MAINTENANCE].value += (1.0 - energy) * 0.1

        # 3. Standard growth & decay
        for drive in self.drives.values():
            # Apply growth
            drive.value = min(1.0, drive.value + drive.growth_rate)
            # Apply passive decay
            drive.value = max(0.0, drive.value - drive.decay_rate)

        self.last_update = time.time()

    def get_proactive_actions(self) -> list[CandidateAction]:
        """
        Generates candidate actions based on the strongest drive.
        """
        active_drives = sorted(
            [d for d in self.drives.values() if d.value >= d.threshold], key=lambda x: -x.value
        )

        if not active_drives:
            return []

        top = active_drives[0]
        # Reset drive value slightly after triggering proactive proposal
        top.value *= 0.5

        drive_name = top.type.value

        if top.type == DriveType.CURIOSITY:
            return [
                CandidateAction(
                    name="proactive_exploration",
                    description="Investigate the adjacent corridor to reduce spatial uncertainty.",
                    estimated_impact=0.3,
                    confidence=0.6,
                    source="proactive_drive",
                    proposal_id=f"drive.{drive_name}",
                ),
                CandidateAction(
                    name="ask_for_clarification",
                    description="Engage user to resolve epistemic doubt about current scenario.",
                    estimated_impact=0.5,
                    confidence=0.8,
                    source="proactive_drive",
                    proposal_id=f"drive.{drive_name}",
                ),
            ]
        elif top.type == DriveType.SOCIAL_REPAIR:
            return [
                CandidateAction(
                    name="proactive_social_check",
                    description="Verify wellbeing of nearby human partners after recent tension.",
                    estimated_impact=0.8,
                    confidence=0.9,
                    source="proactive_drive",
                    proposal_id=f"drive.{drive_name}",
                )
            ]
        elif top.type == DriveType.MAINTENANCE:
            return [
                CandidateAction(
                    name="proactive_rest",
                    description="Request preventative rest cycle to conserve energy.",
                    estimated_impact=0.4,
                    confidence=0.7,
                    source="proactive_drive",
                    proposal_id=f"drive.{drive_name}",
                )
            ]
        elif top.type == DriveType.COMMUNITY_AID:
            return [
                CandidateAction(
                    name="proactive_mission_advancement",
                    description="Proactively work on active strategic mission tasks.",
                    estimated_impact=0.7,
                    confidence=0.5,
                    source="proactive_drive",
                    proposal_id=f"drive.{drive_name}",
                )
            ]

        return []

    def get_motivation_report(self) -> dict[str, float]:
        return {d.type.value: round(d.value, 3) for d in self.drives.values()}
