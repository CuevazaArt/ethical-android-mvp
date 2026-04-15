"""
Deprecation warnings for scheduled removal of environment flags (ADR 0016 — B2).

This module emits Python DeprecationWarning for any KERNEL_* or OLLAMA_* variables
that are scheduled for removal or replacement. See DEPRECATION_ROADMAP in env_policy.py
for the full removal timeline.

Usage:
  check_deprecated_flags()  # Call once at kernel startup to emit warnings for active flags

Non-goal: this is NOT a hard block. Deprecated flags continue to work during the
transition window; warnings allow operators time to migrate to recommended alternatives.

Timeline:
  - When deprecated: warning emitted if flag is set
  - After 1-2 minor releases (typically ≤3 months): flag removed from code
  - Removal documented in CHANGELOG.md with migration path

Related:
  - docs/proposals/KERNEL_ENV_POLICY.md
  - docs/proposals/PROPOSAL_ADDRESSING_CORE_WEAKNESSES.md (Bayesian naming)
  - docs/proposals/PROPOSAL_CONSOLIDATION_PRE_DAO.md (Axis B2)
"""

from __future__ import annotations

import os
import warnings
from typing import Final

# Map of deprecated variable names → (removal_version, suggested_replacement).
# Should be kept in sync with DEPRECATION_ROADMAP in env_policy.py.
DEPRECATED_FLAGS: Final[dict[str, tuple[str, str]]] = {
    # Bayesian naming / replaced by feedback mixture tier
    "KERNEL_BAYESIAN_FEEDBACK": (
        "v0.2.0",
        "Use KERNEL_FEEDBACK_* suite (KERNEL_FEEDBACK_PATH, KERNEL_FEEDBACK_UPDATE_STRENGTH) instead.",
    ),
    "KERNEL_BAYESIAN_LEGACY_AFFINE_VALUATIONS": (
        "v0.2.0",
        "Legacy affine valuations replaced by feedback mixture posterior; remove or ignore.",
    ),
    "KERNEL_BAYESIAN_MAX_DRIFT": (
        "v0.2.0",
        "Replaced by KERNEL_FEEDBACK_MAX_DRIFT and KERNEL_FEEDBACK_POSTERIOR_CHECK.",
    ),
    "KERNEL_BAYESIAN_CONTEXT_LEVEL": (
        "v0.2.0",
        "Use KERNEL_BAYESIAN_CONTEXT_LEVEL3 for per-context posteriors (ADR 0013).",
    ),
    "KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS": (
        "v0.2.0",
        "Empirical weight calibration now via feedback posterior; see KERNEL_FEEDBACK_UPDATE_STRENGTH.",
    ),
    # Narrative-tier only (don't affect final_action); marked for optional removal
    "KERNEL_SOMATIC_MARKERS": (
        "v0.3.0",
        "Narrative-tier only (no causal effect on final_action); consider removing or moving to narrative-only profile.",
    ),
    "KERNEL_GRAY_ZONE_DIPLOMACY": (
        "v0.3.0",
        "Narrative-tier tone hint; doesn't affect decision core. Keep if UX values diplomatic framing; else remove.",
    ),
    "KERNEL_POLES_PRE_ARGMAX": (
        "v0.2.0",
        "Experimental narrative pole modulation; conflicts with mixture scorer argmax. Consolidate into KERNEL_NARRATIVE_* family.",
    ),
    "KERNEL_CONTEXT_RICHNESS_PRE_ARGMAX": (
        "v0.2.0",
        "Narrative-only; doesn't affect ethical choice. Merge into KERNEL_NARRATIVE_IDENTITY_POLICY or remove.",
    ),
    # Mock/lab-only flags (not for production)
    "KERNEL_DEMOCRATIC_BUFFER_MOCK": (
        "v0.2.0",
        "Mock governance for lab only. Use real KERNEL_MORAL_HUB_* if deploying DAO; else remove.",
    ),
    "KERNEL_ETHOS_PAYROLL_MOCK": (
        "v0.3.0",
        "Mock ledger (lab only). Not production governance. Remove or move to test harness.",
    ),
    "KERNEL_REPARATION_VAULT_MOCK": (
        "v0.3.0",
        "Mock vault (lab only). Not production justice. Remove or use real vault implementation.",
    ),
    "KERNEL_JUDICIAL_MOCK_COURT": (
        "v0.2.0",
        "Mock court; use KERNEL_MORAL_HUB_DAO_VOTE for real governance. Lab-only flag; remove in production.",
    ),
    # Redundant or overlapping flags
    "KERNEL_PERCEPTION_PARALLEL": (
        "v0.2.0",
        "Overlaps with KERNEL_PERCEPTION_PARALLEL_WORKERS. Use *_WORKERS directly; remove boolean.",
    ),
    "KERNEL_TEMPORAL_DAO_SYNC": (
        "v0.3.0",
        "Overlaps with KERNEL_TEMPORAL_LAN_SYNC. Consolidate into single temporal sync policy.",
    ),
    "KERNEL_SWARM_STUB": (
        "v0.2.0",
        "Peer-stub digest (lab only). Not for production multi-agent. Remove or implement full swarm.",
    ),
    "KERNEL_NOMAD_SIMULATION": (
        "v0.3.0",
        "Simulation mode; not for production. Use real KERNEL_NOMADIC_ED25519_PRIVATE_KEY instead.",
    ),
    # Advanced/experimental Bayesian flags with low coverage
    "KERNEL_HIERARCHICAL_FEEDBACK": (
        "v0.2.0",
        "Experimental hierarchical updater (advanced Bayesian). Use simpler KERNEL_FEEDBACK_* unless specifically calibrated.",
    ),
    "KERNEL_HIERARCHICAL_MIN_LOCAL": (
        "v0.2.0",
        "Accompanies KERNEL_HIERARCHICAL_FEEDBACK. Consider both deprecated.",
    ),
    "KERNEL_HIERARCHICAL_TAU_MAX": (
        "v0.2.0",
        "Hierarchical timing parameter. Remove with KERNEL_HIERARCHICAL_FEEDBACK.",
    ),
    # Unused or undocumented
    "KERNEL_ETHICAL_GENOME_ENFORCE": (
        "v0.2.0",
        "Genetic algorithm mode (unused). Not implemented in scorer. Remove.",
    ),
    "KERNEL_ETHICAL_GENOME_MAX_DRIFT": (
        "v0.2.0",
        "Companion to KERNEL_ETHICAL_GENOME_ENFORCE (unused). Remove.",
    ),
    "KERNEL_STRATEGIC_BOOST_FACTOR": (
        "v0.2.0",
        "Undocumented strategic factor (no tests). Remove or document usage before deploying.",
    ),
    "KERNEL_PSI_SLEEP_UPDATE_MIXTURE": (
        "v0.3.0",
        "Experimental Psi Sleep mixture update (low coverage). Use standard KERNEL_FEEDBACK_* instead.",
    ),
    # Old perception flags replaced by backend policy
    "KERNEL_PERCEPTION_CIRCUIT": (
        "v0.2.0",
        "Replaced by KERNEL_PERCEPTION_BACKEND_POLICY (template_local / fast_fail / session_banner).",
    ),
    "KERNEL_PERCEPTION_PARSE_FAIL_LOCAL": (
        "v0.2.0",
        "Merged into KERNEL_PERCEPTION_BACKEND_POLICY. Use policy names directly.",
    ),
    "KERNEL_CROSS_CHECK_HIGH_MAX_CALM": (
        "v0.2.0",
        "Lab-only cross-check thresholds. Consolidate or remove.",
    ),
    "KERNEL_CROSS_CHECK_HIGH_MIN_RISK": (
        "v0.2.0",
        "Lab-only cross-check thresholds. Consolidate or remove.",
    ),
    "KERNEL_CROSS_CHECK_MED_MAX_CALM": (
        "v0.2.0",
        "Lab-only cross-check thresholds. Consolidate or remove.",
    ),
    "KERNEL_CROSS_CHECK_MED_MIN_RISK": (
        "v0.2.0",
        "Lab-only cross-check thresholds. Consolidate or remove.",
    ),
    # Old LLM naming before unification
    "KERNEL_LLM_MONOLOGUE": (
        "v0.2.0",
        "Replaced by KERNEL_LLM_TP_MONOLOGUE_POLICY and KERNEL_CHAT_EXPOSE_MONOLOGUE. Use policy instead.",
    ),
    "KERNEL_LLM_MONOLOGUE_BACKEND_POLICY": (
        "v0.2.0",
        "Merged into KERNEL_KERNEL_VERBAL_LLM_BACKEND_POLICY. Use new name.",
    ),
}


def check_deprecated_flags() -> None:
    """
    Scan environment and emit DeprecationWarning for any set deprecated flags.

    Call once at kernel startup (e.g., in __init__).
    This is **not** a hard block; flags continue to work during transition window.
    """
    for flag_name, (removal_version, suggestion) in DEPRECATED_FLAGS.items():
        if os.environ.get(flag_name):
            warning_msg = (
                f"{flag_name} is deprecated and scheduled for removal in {removal_version}. "
                f"Suggestion: {suggestion}"
            )
            warnings.warn(warning_msg, DeprecationWarning, stacklevel=2)


def is_deprecated(flag_name: str) -> bool:
    """Check if a flag is in the deprecation roadmap."""
    return flag_name in DEPRECATED_FLAGS


def get_deprecation_info(flag_name: str) -> tuple[str, str] | None:
    """Get removal version and suggestion for a deprecated flag, or None."""
    return DEPRECATED_FLAGS.get(flag_name)
