"""
KERNEL_* environment validation (Issue 7).

We do **not** enumerate all flag Cartesian products. Instead:

- **Nominal profiles** stay in ``runtime_profiles.RUNTIME_PROFILES`` (CI smoke covers each).
- **SUPPORTED_COMBOS** partitions those profile names into ``demo`` / ``production`` / ``lab`` buckets
  for documentation and guardrails.
- **Rule-based checks** flag invalid *relationships* between env vars (e.g. mock court without
  escalation). Default **strict** when unset (see ``kernel_public_env``); **warn** for lab nominal
  profiles merged at startup; set ``KERNEL_ENV_VALIDATION=warn`` to log only.

See ``docs/proposals/README.md``.
"""

from __future__ import annotations

import hashlib
import logging
import os
from typing import Final

from ..runtime_profiles import profile_names
from .kernel_public_env import KernelPublicEnv

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Supported nominal bundles (names must partition ``profile_names()``).
# ---------------------------------------------------------------------------

SUPPORTED_COMBOS: Final[dict[str, frozenset[str]]] = {
    "production": frozenset(
        {
            "baseline",
            "operational_trust",
            "lexical_malabs_only",
        }
    ),
    "demo": frozenset(
        {
            "judicial_demo",
            "hub_dao_demo",
            "nomad_demo",
            "reality_lighthouse_demo",
            "lan_mobile_thin_client",
            "lan_operational",
            "moral_hub_extended",
            "situated_v8_lan_demo",
        }
    ),
    "lab": frozenset(
        {
            "perception_hardening_lab",
            "perception_adv_consensus_lab",
            "phase2_event_bus_lab",
            "untrusted_chat_input",
            "llm_integration_lab",
        }
    ),
}

# Flags scheduled for removal or rename — keep in sync with CHANGELOG / KERNEL_ENV_POLICY.
DEPRECATION_ROADMAP: Final[dict[str, str]] = {
    # Example: "KERNEL_LEGACY_FLAG": "Remove in v0.2.0; use ETHOS_RUNTIME_PROFILE + documented bundle."
}


def all_supported_profile_names() -> frozenset[str]:
    """Union of ``SUPPORTED_COMBOS`` values — must equal ``profile_names()``."""
    out: set[str] = set()
    for names in SUPPORTED_COMBOS.values():
        out |= set(names)
    return frozenset(out)


def default_env_validation_for_profile(profile_name: str) -> str:
    """
    Default ``KERNEL_ENV_VALIDATION`` when merging a nominal profile (unset/empty only).

    **Lab** bundles default to ``warn`` (experimentation); **production** and **demo** default to
    ``strict`` so invalid flag combinations fail fast at chat server startup.
    """
    if profile_name in SUPPORTED_COMBOS["lab"]:
        return "warn"
    return "strict"


def collect_env_violations() -> list[str]:
    """
    Return human-readable constraint violations for the **current** process environment.

    Rules are evaluated on a typed :class:`KernelPublicEnv` snapshot — extend that model when
    adding new cross-flag constraints (Issue 7).
    """
    return KernelPublicEnv.from_environ().consistency_violations()


def env_combo_fingerprint() -> str:
    """
    Stable short hash of sorted ``KERNEL_*`` entries (for logs / support tickets).

    Does not include secrets such as ``KERNEL_CHECKPOINT_FERNET_KEY``.
    """
    skip = frozenset({"KERNEL_CHECKPOINT_FERNET_KEY"})
    pairs: list[tuple[str, str]] = []
    for key in sorted(os.environ):
        if not key.startswith("KERNEL_"):
            continue
        if key in skip:
            pairs.append((key, "<redacted>"))
        else:
            pairs.append((key, os.environ[key]))
    blob = "\n".join(f"{k}={v}" for k, v in pairs).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def _effective_validation_mode(mode: str | None, snap: KernelPublicEnv) -> str:
    """Resolve ``KERNEL_ENV_VALIDATION`` (or test override)."""
    if mode is not None:
        raw = mode.strip().lower()
        if raw in ("warn", "warning"):
            return "warn"
        if raw in ("0", "false", "no", "off"):
            return "off"
        if raw in ("1", "true", "yes", "on", "strict"):
            return "strict"
        if raw == "":
            return snap.env_validation
        logger.warning("unknown KERNEL_ENV_VALIDATION override=%r; defaulting to strict", raw)
        return "strict"
    return snap.env_validation


def validate_kernel_env(*, mode: str | None = None) -> None:
    """
    Validate environment according to ``KERNEL_ENV_VALIDATION``:

    - ``off`` — no-op
    - ``warn`` — log warnings for ``collect_env_violations()`` (no raise)
    - ``strict`` — raise ``ValueError`` if any violation

    **Default when unset:** ``strict`` (see ``KernelPublicEnv.from_environ`` / ``_parse_env_validation_mode``).
    After ``apply_named_runtime_profile_to_environ()``, lab tier names get ``warn`` if validation
    is still unset (see ``default_env_validation_for_profile`` in this module).

    ``mode`` overrides the env when set (for tests). Parsed mode is aligned with
    :class:`KernelPublicEnv` (typed layer).
    """
    snap = KernelPublicEnv.from_environ()
    eff = _effective_validation_mode(mode, snap)

    if eff == "off":
        return

    violations = snap.consistency_violations()
    if not violations:
        return

    msg = "KERNEL_* environment issues:\n  - " + "\n  - ".join(violations)
    if eff == "strict":
        raise ValueError(msg)
    logger.warning("%s", msg)


def validate_supported_combo_partition() -> None:
    """
    Dev / CI helper: ensure ``SUPPORTED_COMBOS`` matches ``runtime_profiles.profile_names()``.

    Raises ``AssertionError`` on mismatch.
    """
    nominal = frozenset(profile_names())
    union = all_supported_profile_names()
    if union != nominal:
        only_nominal = nominal - union
        only_buckets = union - nominal
        raise AssertionError(
            "SUPPORTED_COMBOS partition mismatch: "
            f"only in profiles={sorted(only_nominal)!r} "
            f"only in buckets={sorted(only_buckets)!r}"
        )
