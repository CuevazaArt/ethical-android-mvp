"""
Soft Robotics & Kinematic Filtering (Module 3: S7).

Provides smoothing and acceleration control for physical android actions.
The goal is to prevent 'jerkiness' and ensure ethical motion (proxemics).
"""

import math
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class KinematicState:
    """Current state of a robotic joint or velocity vector."""

    last_value: float = 0.0
    last_time: float = field(default_factory=time.time)
    current_velocity: float = 0.0


class SoftKinematicFilter:
    """
    Implements a sigmoid-based or low-pass filter for motion control.
    Couples ethical signals (social tension) to motion dynamics.
    """

    def __init__(
        self,
        max_acceleration: float = 1.0,  # units/s^2
        max_velocity: float = 2.0,  # units/s
        smoothing_factor: float = 0.5,  # [0, 1] low pass component
    ):
        self.max_accel = max_acceleration
        self.max_vel = max_velocity
        self.smoothing = smoothing_factor
        self.joints: dict[str, KinematicState] = {}

    def filter_action(
        self, joint_id: str, target_value: float, social_tension: float = 0.0, arousal: float = 0.0
    ) -> float:
        """
        Calculates the next command value for a joint, applying limits.
        Higher social_tension or arousal reduces max_acceleration for 'caution'.
        """
        now = time.time()
        if joint_id not in self.joints:
            self.joints[joint_id] = KinematicState(last_value=target_value)
            return target_value

        state = self.joints[joint_id]
        dt = now - state.last_time
        if dt <= 0:
            return state.last_value

        # --- STEP 1: Dynamic Limit Adjustment ---
        # Caution: High social tension -> lower acceleration limits
        effective_max_accel = self.max_accel * (1.0 - 0.7 * social_tension)
        effective_max_vel = self.max_vel * (1.0 - 0.4 * social_tension)

        # Arousal (sigma) boost: if the kernel is 'excited', it might move faster
        # but with less control. For this filter, we interpret arousal as 'jitter'.
        jitter = 0.05 * arousal * math.sin(now * 10)

        # --- STEP 2: Velocity & Acceleration Constraints ---
        delta = target_value - state.last_value
        desired_velocity = delta / dt

        # Clamp velocity
        desired_velocity = max(-effective_max_vel, min(effective_max_vel, desired_velocity))

        # Calculate acceleration
        accel = (desired_velocity - state.current_velocity) / dt

        # Clamp acceleration
        accel = max(-effective_max_accel, min(effective_max_accel, accel))

        # Update state
        new_velocity = state.current_velocity + accel * dt
        new_value = state.last_value + new_velocity * dt + jitter

        # --- STEP 3: Low-pass Smoothing ---
        # Blends raw target and physics-constrained value
        final_value = (self.smoothing * state.last_value) + (1.0 - self.smoothing) * new_value

        state.last_value = final_value
        state.last_time = now
        state.current_velocity = new_velocity

        return final_value

    def filter_action_with_profile(
        self,
        joint_id: str,
        target_value: float,
        profile: Any,  # InteractionProfile
        social_tension: float = 0.0,
        arousal: float = 0.0,
    ) -> float:
        """
        Extends filter_action to use InteractionProfile preferences (S9).
        - personal_distance (0=close, 1=far): increases standoff distance or slows approach.
        - interaction_rhythm (slow/medium/fast): modulates max velocity.
        """
        # 1. Modulation from rhythm
        rhythm_mult = 1.0
        rhythm = getattr(profile, "interaction_rhythm", "medium")
        if rhythm == "slow":
            rhythm_mult = 0.6
        elif rhythm == "fast":
            rhythm_mult = 1.3

        # 2. Modulation from personal distance
        # If the user wants MORE distance (personal_distance -> 1.0),
        # we slow down approach-style actions even more.
        dist_mult = 1.0 - (0.4 * getattr(profile, "personal_distance", 0.5))

        # Apply combined multipliers to internal limits temporarily
        original_vel = self.max_vel
        original_accel = self.max_accel

        self.max_vel *= rhythm_mult * dist_mult
        self.max_accel *= rhythm_mult * dist_mult

        try:
            return self.filter_action(joint_id, target_value, social_tension, arousal)
        finally:
            # Restore original limits
            self.max_vel = original_vel
            self.max_accel = original_accel


def apply_social_proxemics_filter(
    raw_magnitude: float, social_tension: float, vulnerability: float
) -> float:
    """
    Static utility to reduce 'approach magnitude' based on social context.
    If tension is high or person is vulnerable, reduce movement intensity.
    """
    multiplier = 1.0 - (0.5 * social_tension) - (0.3 * vulnerability)
    return raw_magnitude * max(0.2, multiplier)
