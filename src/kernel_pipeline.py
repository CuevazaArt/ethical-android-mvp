"""
Pipeline helpers extracted from :class:`~src.kernel.EthicalKernel`.

Currently implements :func:`run_sleep_cycle` (Psi Sleep + DAO feedback + forgiveness +
immortality backup). Further ``process()`` step extraction can extend this module
without growing ``kernel.py``.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .kernel import EthicalKernel


def run_sleep_cycle(kernel: EthicalKernel) -> str:
    """Body of ``EthicalKernel.execute_sleep`` — retrospective audit, forgiveness, backup."""
    from .kernel import kernel_dao_as_mock, kernel_mixture_scorer
    from .modules.cognition.feedback_calibration_ledger import apply_psi_sleep_feedback_to_engine
    from .modules.governance.identity_integrity import pruning_recalibration_allowed

    parts: list[str] = []

    result = kernel.sleep.execute(kernel.memory, kernel._pruned_actions)
    max_drift = float(os.environ.get("KERNEL_ETHICAL_GENOME_MAX_DRIFT", "0.15"))
    enforce_genome = os.environ.get("KERNEL_ETHICAL_GENOME_ENFORCE", "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )
    for param, delta in result.global_recalibrations.items():
        if param == "pruning_threshold":
            if enforce_genome and not pruning_recalibration_allowed(
                kernel._bayesian_genome_threshold,
                kernel.bayesian.pruning_threshold,
                float(delta),
                max_drift,
            ):
                parts.append(
                    "\n  Identity integrity: pruning recalibration skipped (genome drift cap)."
                )
                continue
            kernel.bayesian.pruning_threshold = max(0.1, kernel.bayesian.pruning_threshold + delta)
        elif param == "caution":
            kernel.locus.beta = min(kernel.locus.BETA_MAX, kernel.locus.beta + delta)
    parts.append(kernel.sleep.format(result))

    if hasattr(kernel, "dao") and kernel.dao is not None:
        dao_feedback = kernel_dao_as_mock(kernel.dao).extract_community_feedback(recent_count=10)
        for label, count in dao_feedback.items():
            for _ in range(count):
                kernel.feedback_ledger.record("DAO_community_consensus", label)

    fb_line = apply_psi_sleep_feedback_to_engine(
        kernel_mixture_scorer(kernel.bayesian),
        kernel.feedback_ledger,
        genome_weights=kernel._bayesian_genome_weights,
        max_drift=max_drift,
    )
    if fb_line:
        parts.append(fb_line)

    forgiveness_result = kernel.forgiveness.forgiveness_cycle()
    parts.append(f"\n{kernel.forgiveness.format(forgiveness_result)}")

    load = kernel.weakness.emotional_load()
    parts.append(f"\n  \U0001f300 Weakness emotional load: {load:.3f}")

    _ = kernel.immortality.backup(kernel)
    parts.append(f"\n{kernel.immortality.format_status()}")

    intents = kernel.drive_arbiter.evaluate(kernel)
    if intents:
        drive_lines = ["\n  Drive intents (advisory):"]
        for di in intents:
            drive_lines.append(f"    \u2022 {di.suggest} (p={di.priority:.2f}) \u2014 {di.reason}")
        parts.append("\n".join(drive_lines))

    sl_lines = kernel.skill_learning.audit_lines_for_psi_sleep()
    if sl_lines:
        parts.append("\n" + "\n".join(sl_lines))

    return "\n".join(parts)
