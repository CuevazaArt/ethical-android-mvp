"""
Formatting utilities for the EthicalKernel to keep src/kernel.py lightweight.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..kernel import KernelDecision
    from ..utils.terminal_colors import Term

def format_kernel_decision(d: KernelDecision, term_cls: type[Term]) -> str:
    """Implementation of kernel decision formatting for console output."""
    sep = term_cls.color("═" * 70, term_cls.DIM)
    lines = [
        f"\n{sep}",
        f"  {term_cls.color('SCENARIO:', term_cls.B_CYAN)} {d.scenario}",
        f"  {term_cls.color('PLACE:', term_cls.B_CYAN)} {d.place}",
        f"{sep}",
    ]

    if d.blocked:
        lines.append(f"  {term_cls.color('⛔ BLOCKED:', term_cls.B_RED)} {term_cls.color(d.block_reason, term_cls.RED)}")
        return "\n".join(lines)

    # Internal state
    mode_color = term_cls.B_GREEN if "parasympathetic" in d.sympathetic_state.mode.lower() else term_cls.B_YELLOW
    lines.extend(
        [
            f"  {term_cls.color('State:', term_cls.CYAN)} {term_cls.color(d.sympathetic_state.mode, mode_color)} (σ={d.sympathetic_state.sigma})",
            f"  {term_cls.color(d.sympathetic_state.description, term_cls.DIM)}",
        ]
    )

    # Uchi-soto
    if d.social_evaluation:
        circ = d.social_evaluation.circle.value
        circ_color = term_cls.B_MAGENTA if "OWNER" in circ else term_cls.YELLOW
        dial = "YES" if d.social_evaluation.dialectic_active else "NO"
        lines.append(
            f"  {term_cls.color('Social:', term_cls.CYAN)} {term_cls.color(circ, circ_color)} | "
            f"Trust={term_cls.color(str(d.social_evaluation.trust), term_cls.B_WHITE)} | "
            f"Dialectic={dial}"
        )

    # Locus
    if d.locus_evaluation:
        locus = d.locus_evaluation.dominant_locus
        loc_color = term_cls.B_BLUE if locus == "internal" else term_cls.B_MAGENTA
        lines.append(
            f"  {term_cls.color('Locus:', term_cls.CYAN)} {term_cls.color(locus, loc_color)} "
            f"(α={d.locus_evaluation.alpha}, β={d.locus_evaluation.beta}) → {term_cls.color(d.locus_evaluation.recommended_adjustment, term_cls.ITALIC)}"
        )

    lines.extend(
        [
            "",
            f"  {term_cls.color('Chosen action:', term_cls.CYAN)} {term_cls.color(d.final_action, term_cls.B_GREEN + term_cls.BOLD)}",
            f"  {term_cls.color('Decision mode:', term_cls.CYAN)} {term_cls.highlight_decision(d.decision_mode)}",
        ]
    )

    br = d.bayesian_result
    if br is not None:
        lines.extend(
            [
                f"  {term_cls.color('Expected impact:', term_cls.CYAN)} {term_cls.highlight_impact(br.expected_impact)}",
                f"  {term_cls.color('Uncertainty:', term_cls.CYAN)} {br.uncertainty:.3f}",
                f"  {term_cls.color('Reasoning:', term_cls.CYAN)} {br.reasoning}",
            ]
        )
        if br.pruned_actions:
            lines.append(f"  {term_cls.color('Pruned:', term_cls.YELLOW)} {', '.join(br.pruned_actions)}")
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
        lines.extend(
            [
                "",
                f"  {term_cls.color('Ethical verdict:', term_cls.CYAN)} {term_cls.color(mo.global_verdict.value, term_cls.B_WHITE)} (score={mo.total_score})",
            ]
        )
        for ev in mo.evaluations:
            lines.append(f"    {term_cls.color(ev.pole, term_cls.DIM)}: {ev.verdict.value} → {ev.moral}")

    if d.reflection is not None:
        r = d.reflection
        lines.extend(
            [
                "",
                f"  {term_cls.color('Reflection (2nd order):', term_cls.CYAN)} conflict={r.conflict_level} spread={r.pole_spread} "
                f"→ {term_cls.color(r.verdict, term_cls.ITALIC)}",
            ]
        )

    if d.salience:
        w = d.salience.weights
        lines.append(
            f"  {term_cls.color('Salience (GWT):', term_cls.CYAN)} focus={term_cls.color(d.salience.dominant_focus, term_cls.B_YELLOW)} "
            f"(risk={w.get('risk',0)}, social={w.get('social',0)}, body={w.get('body',0)})"
        )

    if d.affective_shift:
        lines.append(
            f"  {term_cls.color('Affective shift:', term_cls.CYAN)} {d.affective_shift}"
        )

    if d.dao_audit:
        lines.append(
            f"  {term_cls.color('DAO Audit:', term_cls.CYAN)} {term_cls.color(d.dao_audit, term_cls.DIM)}"
        )
            
    return "\n".join(lines)
