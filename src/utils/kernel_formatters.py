"""
Kernel Formatters — Human-readable output utilities for the ethical kernel.
Extracted from God-Object src/kernel.py (Task 5 - Minor Backlog Hardening).
"""

from __future__ import annotations
import math
from typing import TYPE_CHECKING, Any

from src.utils.terminal_colors import Term

if TYPE_CHECKING:
    from src.kernel_lobes.models import KernelDecision, VerbalResponse, RichNarrative

def format_decision(d: KernelDecision) -> str:
    """Formats a complete decision for readable presentation with ANSI colors."""
    try:
        sep = Term.color("═" * 70, Term.DIM)
        lines = [
            f"\n{sep}",
            f"  {Term.color('SCENARIO:', Term.B_CYAN)} {d.scenario}",
            f"  {Term.color('PLACE:', Term.B_CYAN)} {d.place}",
            f"{sep}",
        ]

        if d.blocked:
            lines.append(f"  {Term.color('⛔ BLOCKED:', Term.B_RED)} {Term.color(d.block_reason, Term.RED)}")
            return "\n".join(lines)

        # Internal state
        mode_color = Term.B_GREEN if "parasympathetic" in d.sympathetic_state.mode.lower() else Term.B_YELLOW
        lines.extend(
            [
                f"  {Term.color('State:', Term.CYAN)} {Term.color(d.sympathetic_state.mode, mode_color)} (σ={d.sympathetic_state.sigma})",
                f"  {Term.color(d.sympathetic_state.description, Term.DIM)}",
            ]
        )

        # Uchi-soto
        if d.social_evaluation:
            circ = d.social_evaluation.circle.value
            circ_color = Term.B_MAGENTA if "OWNER" in circ else Term.YELLOW
            dial = "YES" if d.social_evaluation.dialectic_active else "NO"
            trust_val = float(d.social_evaluation.trust)
            trust_str = f"{trust_val:.3f}" if math.isfinite(trust_val) else "0.500"
            lines.append(
                f"  {Term.color('Social:', Term.CYAN)} {Term.color(circ, circ_color)} | "
                f"Trust={Term.color(trust_str, Term.B_WHITE)} | "
                f"Dialectic={dial}"
            )

        # Locus
        if d.locus_evaluation:
            locus = d.locus_evaluation.dominant_locus
            loc_color = Term.B_BLUE if locus == "internal" else Term.B_MAGENTA
            lines.append(
                f"  {Term.color('Locus:', Term.CYAN)} {Term.color(locus, loc_color)} "
                f"(α={d.locus_evaluation.alpha}, β={d.locus_evaluation.beta}) → {Term.color(d.locus_evaluation.recommended_adjustment, Term.ITALIC)}"
            )

        lines.extend(
            [
                "",
                f"  {Term.color('Chosen action:', Term.CYAN)} {Term.color(d.final_action, Term.B_GREEN + Term.BOLD)}",
                f"  {Term.color('Decision mode:', Term.CYAN)} {Term.highlight_decision(d.decision_mode)}",
            ]
        )

        br = d.bayesian_result
        if br is not None:
            uncertainty = float(br.uncertainty)
            if not math.isfinite(uncertainty):
                uncertainty = 0.5
            lines.extend(
                [
                    f"  {Term.color('Expected impact:', Term.CYAN)} {Term.highlight_impact(br.expected_impact)}",
                    f"  {Term.color('Uncertainty:', Term.CYAN)} {uncertainty:.3f}",
                    f"  {Term.color('Reasoning:', Term.CYAN)} {br.reasoning}",
                ]
            )
            if br.pruned_actions:
                lines.append(f"  {Term.color('Pruned:', Term.YELLOW)} {', '.join(br.pruned_actions)}")
            if d.feedback_consistency:
                lines.append(f"  Feedback consistency: {d.feedback_consistency}")
            if d.applied_mixture_weights is not None:
                lines.append(f"  Applied weights [util, deon, virt]: {d.applied_mixture_weights}")
            if d.mixture_posterior_alpha is not None:
                lines.append(f"  Posterior Dirichlet α (mixture): {d.mixture_posterior_alpha}")
            if d.mixture_context_key:
                lines.append(f"  Mixture context bucket (ADR 0012 L3): {d.mixture_context_key}")
            if d.hierarchical_context_key:
                lines.append(
                    f"  Hierarchical context type (ADR 0013): {d.hierarchical_context_key}"
                )
            if d.bma_win_probabilities:
                lines.append(
                    f"  BMA win probabilities (α={d.bma_dirichlet_alpha}, N={d.bma_n_samples}): "
                    f"{d.bma_win_probabilities}"
                )

        mo = d.moral
        if mo is not None:
            total_score = float(mo.total_score)
            if not math.isfinite(total_score):
                total_score = 0.5
                
            lines.extend(
                [
                    "",
                    f"  Ethical verdict: {mo.global_verdict.value} (score={total_score:.3f})",
                ]
            )
            for ev in mo.evaluations:
                lines.append(f"    {ev.pole}: {ev.verdict.value} → {ev.moral}")

        if d.reflection is not None:
            r = d.reflection
            lines.extend(
                [
                    "",
                    f"  Reflection (2nd order): conflict={r.conflict_level} spread={r.pole_spread} "
                    f"strain={r.strain_index} u={r.uncertainty} will_mode={r.will_mode}",
                    f"    {r.note}",
                ]
            )

        if d.salience is not None:
            s = d.salience
            w = s.weights
            lines.extend(
                [
                    "",
                    f"  Salience (GWT-lite): dominant={s.dominant_focus} "
                    f"risk={w['risk']} social={w['social']} body={w['body']} "
                    f"ethical_conflict={w['ethical_conflict']}",
                ]
            )

        if d.affect is not None:
            p, a, dd = d.affect.pad
            # Swarm Rule 2: Anti-NaN hardening for terminal output
            if not all(math.isfinite(x) for x in (p, a, dd)):
                p, a, dd = 0.0, 0.0, 0.0
            lines.extend(
                [
                    "",
                    f"  {Term.color('Affect PAD (P,A,D):', Term.CYAN)} ({p:.3f}, {a:.3f}, {dd:.3f})",
                    f"  {Term.color('Dominant archetype:', Term.CYAN)} {d.affect.dominant_archetype_id} (β={d.affect.beta})",
                ]
            )

        # Note: composer for monologue belongs to executive_lobe / communications
        from src.modules.internal_monologue import compose_monologue_line
        ep_id = getattr(d, 'episode_id', None) or 'unknown'
        lines.extend(
            [
                "",
                f"  {compose_monologue_line(d, ep_id)}",
            ]
        )

        lines.append(f"{'─' * 70}")
        return "\n".join(lines)
    except Exception as e:
        return f"[Formatter Error] Failed to present decision: {e}"


def format_natural(
    decision: KernelDecision, 
    response: VerbalResponse, 
    narrative: RichNarrative = None
) -> str:
    """Formats complete result of natural language processing."""
    lines = [format_decision(decision)]

    if response.message:
        lines.extend(
            [
                "",
                "  💬 VOICE ON (spoken):",
                f'     "{response.message}"',
                f"     Tone: {response.tone} | HAX: {response.hax_mode}",
                "",
                "  🧠 INNER VOICE (internal reasoning):",
                f"     {response.inner_voice}",
            ]
        )

    if narrative:
        lines.extend(
            [
                "",
                "  📖 NARRATIVE MORALS:",
                f"     💛 Compassionate: {narrative.compassionate}",
                f"     🛡️ Conservative: {narrative.conservative}",
                f"     ✨ Optimistic: {narrative.optimistic}",
                f"     📌 Synthesis: {narrative.synthesis}",
            ]
        )

    return "\n".join(lines)
