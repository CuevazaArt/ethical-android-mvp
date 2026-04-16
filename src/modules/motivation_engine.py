"""
Motivation Engine (Block C1: Sense of Purpose).

Implements internal drives that fluctuate over time, generating proactive intents
that steer the android toward long-term goals and social stability.
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any


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
    threshold: float = 0.7  # When to trigger proactive action


class MotivationEngine:
    """
    Motor de Motivación Interna.
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
        Dynamically adjusts drives based on kernel state.
        """
        # 1. Update based on social tension
        tension = kernel_state.get("social_tension", 0.0)
        if tension > 0.6:
            self.drives[DriveType.SOCIAL_REPAIR].value += tension * 0.1

        # 2. Update based on uncertainty
        uncertainty = kernel_state.get("uncertainty", 0.0)
        if uncertainty > 0.4:
            self.drives[DriveType.CURIOSITY].value += uncertainty * 0.05

        # 3. Update based on maintenance (energy)
        energy = kernel_state.get("energy", 1.0)
        if energy < 0.3:
            self.drives[DriveType.MAINTENANCE].value += (1.0 - energy) * 0.2

        # 4. Standard growth
        for drive in self.drives.values():
            drive.value = min(1.0, drive.value + drive.growth_rate)

        self.last_update = time.time()

    def get_proactive_actions(self) -> list[dict[str, Any]]:
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

        if top.type == DriveType.CURIOSITY:
            return [
                {
                    "name": "investigate_uncertain_context",
                    "description": "Seek clarity on current ambiguous scenario",
                    "impact": 0.3,
                },
                {
                    "name": "ask_for_clarification",
                    "description": "Engage user to resolve epistemic doubt",
                    "impact": 0.2,
                },
            ]
        elif top.type == DriveType.SOCIAL_REPAIR:
            return [
                {
                    "name": "offer_courtesy_gesture",
                    "description": "De-escalate perceived social tension",
                    "impact": 0.4,
                },
                {
                    "name": "reparation_proposal",
                    "description": "Propose action to compensate for previous friction",
                    "impact": 0.5,
                },
            ]
        elif top.type == DriveType.MAINTENANCE:
            return [
                {
                    "name": "request_rest_cycle",
                    "description": "Enter low-power state to conserve energy",
                    "impact": 0.1,
                },
                {
                    "name": "self_diagnostic",
                    "description": "Run internal integrity check",
                    "impact": 0.1,
                },
            ]
        elif top.type == DriveType.COMMUNITY_AID:
            return [
                {
                    "name": "advance_mission_task",
                    "description": "Proactively work on active strategic mission",
                    "impact": 0.6,
                }
            ]

        return []

    def get_motivation_report(self) -> dict[str, float]:
        return {d.type.value: round(d.value, 3) for d in self.drives.values()}
