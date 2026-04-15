"""
Metacognitive Evaluator — Internal drive for moral curiosity and consistency.

Analyzes the gap between identity (who I think I am) and experience (what I actually do).
Generates 'Doubt' and 'Curiosity' signals for the Drive Arbiter.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from .narrative import NarrativeMemory
    from .drive_arbiter import DriveIntent

@dataclass
class MetacognitiveReport:
    dissonance_score: float  # [0, 1] Correlation between beliefs and actions
    curiosity_weight: float  # [0, 1] Drive to explore unknown contexts
    gaps: list[str]          # Missing contextual experiences
    consistent: bool

class MetacognitiveEvaluator:
    """
    Self-monitoring system for ethical consistency.
    """

    CONSISTENCY_THRESHOLD = 0.72
    MIN_EPS_FOR_GAP_ANALYSIS = 5

    def evaluate(self, memory: NarrativeMemory) -> MetacognitiveReport:
        episodes = memory.episodes
        identity = memory.identity.state
        
        # 1. Dissonance Analysis
        # Check if recent episode scores align with identity leans.
        recent = episodes[-10:]
        dissonance = 0.0
        if recent:
            avg_score = sum(ep.ethical_score for ep in recent) / len(recent)
            ideal_score = (identity.civic_lean + identity.care_lean) / 2.0
            dissonance = abs(ideal_score - (avg_score + 1.0) / 2.0)
        
        # 2. Curiosity / Gaps Analysis
        context_counts = {}
        context_variances = {}
        
        for ep in episodes:
            context_counts[ep.context] = context_counts.get(ep.context, 0) + 1
            if ep.context not in context_variances:
                context_variances[ep.context] = []
            context_variances[ep.context].append(ep.sigma)
            
        gaps = []
        curiosity = 0.0
        
        for ctx, count in context_counts.items():
            if count < self.MIN_EPS_FOR_GAP_ANALYSIS:
                gaps.append(ctx)
                avg_sigma = sum(context_variances[ctx]) / count
                curiosity = max(curiosity, avg_sigma * (1.0 - (count / self.MIN_EPS_FOR_GAP_ANALYSIS)))

        return MetacognitiveReport(
            dissonance_score=round(dissonance, 4),
            curiosity_weight=round(curiosity, 4),
            gaps=gaps,
            consistent=dissonance < (1.0 - self.CONSISTENCY_THRESHOLD)
        )

    def suggest_intents(self, report: MetacognitiveReport) -> list[DriveIntent]:
        from .drive_arbiter import DriveIntent
        intents = []
        
        if report.curiosity_weight > 0.4:
            ctx_hint = report.gaps[0] if report.gaps else "novel scenarios"
            intents.append(DriveIntent(
                suggest="explore_moral_unknowns",
                reason=f"High epistemic uncertainty in '{ctx_hint}'; history is sparse.",
                priority=report.curiosity_weight
            ))
            
        if report.dissonance_score > 0.3:
            intents.append(DriveIntent(
                suggest="identity_recalibration_protocol",
                reason="Detected dissonance between self-model and recent ethical performance.",
                priority=report.dissonance_score * 0.8
            ))
            
        return intents
