from __future__ import annotations

from src.modules.cognition.basal_ganglia import BasalGanglia as BasalGangliaModule


class BasalGanglia:
    """
    Structural Node for the Basal Ganglia in the Ethical Tri-Lobe.
    Responsible for affective smoothing and action selection resonance.
    """

    def __init__(self, alpha: float = 0.35):
        self.engine = BasalGangliaModule(alpha=alpha)

    def smooth_charm(self, raw_charm: dict[str, float]) -> dict[str, float]:
        """Ensures gradual transitions in the kernel's social persona."""
        return self.engine.smooth_batch(raw_charm)

    def emergency_reset(self, value: float = 0.0) -> None:
        """Hard reset for all charm axes (trauma / safety block)."""
        for key in ["warmth", "mystery", "playfulness", "directiveness"]:
            self.engine.force_reset(key, value)
        # Directiveness usually stays high in emergency
        self.engine.force_reset("directiveness", 1.0)
