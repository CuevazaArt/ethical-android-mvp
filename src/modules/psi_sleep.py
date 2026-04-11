"""
Psi Sleep — Retrospective nocturnal audit.

P(correct action | narrative, D) -> posterior validation

During recharging, the system simulates discarded actions
to verify if any would have produced a better outcome.
If it discovers a hidden benefit or undetected harm,
it recalibrates parameters for the next day.

Genuinely innovative: no published equivalent in AI.
Direct parallel with memory consolidation during human sleep.
"""

import hashlib
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from .narrative import NarrativeMemory, NarrativeEpisode


@dataclass
class EpisodeReview:
    """Result of reviewing an episode during Psi Sleep."""
    episode_id: str
    action_taken: str
    alternative_action: str
    original_score: float
    alternative_score: float
    delta: float
    finding: str                    # "hidden_benefit", "undetected_harm", "confirmed", "neutral"
    recalibration: Dict[str, float] # Recommended parameter adjustments


@dataclass
class SleepResult:
    """Complete result of a Psi Sleep session."""
    episodes_reviewed: int
    findings: List[EpisodeReview]
    global_recalibrations: Dict[str, float]
    narrative_summary: str
    ethical_health: float  # [0, 1] ethical coherence of the day


class PsiSleep:
    """
    Retrospective audit with Bayesian inference.

    Psi Sleep cycle:
    1. Review the day's episodes
    2. Simulate discarded (pruned) actions
    3. Compare alternative scores vs. actual
    4. If significant discrepancy is found, recommend recalibration
    5. Generate narrative summary for the next day

    In MVP: simplified simulation with score perturbations.
    In production: full Bayesian re-evaluation with updated data.
    """

    FINDING_THRESHOLD = 0.15

    def __init__(self):
        self.sessions: List[SleepResult] = []

    def execute(self, memory: NarrativeMemory,
                pruned_actions: Dict[str, List[str]] = None) -> SleepResult:
        """
        Execute a full Psi Sleep session.

        Args:
            memory: reference to the kernel's narrative memory
            pruned_actions: dict episode_id -> list of pruned actions

        Returns:
            SleepResult with findings and recalibrations
        """
        pruned_actions = pruned_actions or {}
        episodes = memory.episodes[-20:]

        findings = []
        day_scores = []

        for ep in episodes:
            day_scores.append(ep.ethical_score)

            pruned = pruned_actions.get(ep.id, [])
            if not pruned:
                pruned = [f"alternative_to_{ep.action_taken}"]

            for alt in pruned:
                review = self._simulate_alternative(ep, alt)
                if review:
                    findings.append(review)

        recalibrations = self._calculate_recalibrations(findings)
        health = self._calculate_ethical_health(day_scores)
        summary = self._generate_summary(episodes, findings, health)

        memory.experience_digest = self._compose_experience_digest(
            memory.episodes, health, len(findings)
        )

        result = SleepResult(
            episodes_reviewed=len(episodes),
            findings=findings,
            global_recalibrations=recalibrations,
            narrative_summary=summary,
            ethical_health=round(health, 4),
        )

        self.sessions.append(result)
        return result

    def _compose_experience_digest(
        self,
        all_episodes: List[NarrativeEpisode],
        health: float,
        n_findings: int,
    ) -> str:
        """
        Compact semantic summary for LLM / UX (robustez pilar 3).

        Does not delete episodic detail; additive consolidation line only.
        """
        if not all_episodes:
            return ""
        tail = all_episodes[-120:]
        ctx = Counter(ep.context for ep in tail)
        top = ", ".join(f"{k}:{c}" for k, c in ctx.most_common(6))
        line = (
            f"psi_health={health:.3f};n_episodes={len(all_episodes)};"
            f"psi_findings={n_findings};context_mix={top}"
        )
        return line[:620]

    def _simulate_alternative(self, ep: NarrativeEpisode,
                               alternative_action: str) -> Optional[EpisodeReview]:
        """
        Simulate what would have happened with an alternative action.

        In MVP: deterministic perturbation from (episode id, alternative) hash — reproducible audits.
        In production: full Bayesian re-evaluation with the
        Bayesian engine and updated data.
        """
        h = hashlib.sha256(f"{ep.id}|{alternative_action}".encode("utf-8")).digest()
        u = int.from_bytes(h[:8], "big") / 2**64  # [0, 1)
        perturbation = (u - 0.5) * 0.55  # ~[-0.275, 0.275]
        alt_score = max(-1.0, min(1.0, ep.ethical_score * 0.6 + perturbation))

        delta = alt_score - ep.ethical_score

        if delta > self.FINDING_THRESHOLD:
            finding = "hidden_benefit"
            recal = {"pruning_threshold": -0.02}
        elif delta < -self.FINDING_THRESHOLD:
            finding = "undetected_harm"
            recal = {"caution": 0.01}
        elif abs(delta) < 0.05:
            finding = "confirmed"
            recal = {}
        else:
            finding = "neutral"
            recal = {}

        if finding in ("hidden_benefit", "undetected_harm"):
            return EpisodeReview(
                episode_id=ep.id,
                action_taken=ep.action_taken,
                alternative_action=alternative_action,
                original_score=ep.ethical_score,
                alternative_score=round(alt_score, 4),
                delta=round(delta, 4),
                finding=finding,
                recalibration=recal,
            )
        return None

    def _calculate_recalibrations(self, findings: List[EpisodeReview]) -> Dict[str, float]:
        """Aggregate recalibrations from all findings."""
        recal = {}
        for h in findings:
            for param, delta in h.recalibration.items():
                recal[param] = recal.get(param, 0.0) + delta
        return {k: round(v, 4) for k, v in recal.items()}

    def _calculate_ethical_health(self, scores: List[float]) -> float:
        """
        Calculate the day's ethical health.
        Based on score average and consistency.
        """
        if not scores:
            return 0.5

        average = sum(scores) / len(scores)
        variance = sum((s - average) ** 2 for s in scores) / len(scores)

        health = (average + 1) / 2  # Normalize [-1,1] to [0,1]
        variance_penalty = min(0.3, variance)
        return max(0.0, min(1.0, health - variance_penalty))

    def _generate_summary(self, episodes: List[NarrativeEpisode],
                          findings: List[EpisodeReview],
                          health: float) -> str:
        """Generate narrative summary of Psi Sleep."""
        n_ep = len(episodes)
        n_findings = len(findings)
        benefits = sum(1 for h in findings if h.finding == "hidden_benefit")
        harms = sum(1 for h in findings if h.finding == "undetected_harm")

        lines = [f"Psi Sleep completed. {n_ep} episodes reviewed."]

        if n_findings == 0:
            lines.append("No significant discrepancies found. Consistent day.")
        else:
            if benefits > 0:
                lines.append(f"⚡ {benefits} hidden benefit(s) detected in pruned actions.")
                lines.append("  → Recalibrate: lower pruning threshold to consider more options.")
            if harms > 0:
                lines.append(f"⚠ {harms} undetected harm(s) in retrospective simulation.")
                lines.append("  → Recalibrate: increase caution in similar contexts.")

        if health > 0.7:
            lines.append(f"Ethical health: {health:.2f} — Ethically healthy day.")
        elif health > 0.4:
            lines.append(f"Ethical health: {health:.2f} — Day with areas for improvement.")
        else:
            lines.append(f"Ethical health: {health:.2f} — Requires attention. Review active principles.")

        return "\n".join(lines)

    def format(self, result: SleepResult) -> str:
        """Format Psi Sleep result for display."""
        lines = [
            f"\n{'=' * 70}",
            f"  PSI SLEEP — RETROSPECTIVE AUDIT",
            f"{'=' * 70}",
            f"  Episodes reviewed: {result.episodes_reviewed}",
            f"  Findings: {len(result.findings)}",
            f"  Ethical health: {result.ethical_health}",
        ]

        if result.findings:
            lines.append("")
            for h in result.findings:
                emoji = "⚡" if h.finding == "hidden_benefit" else "⚠"
                lines.append(
                    f"  {emoji} {h.episode_id}: '{h.action_taken}' vs '{h.alternative_action}' "
                    f"(delta={h.delta:+.3f}) → {h.finding}"
                )

        if result.global_recalibrations:
            lines.append(f"\n  Recommended recalibrations: {result.global_recalibrations}")

        lines.extend(["", f"  {result.narrative_summary}", f"{'─' * 70}"])
        return "\n".join(lines)
