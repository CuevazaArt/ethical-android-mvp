"""
KERNEL_* environment validation (Issue 7).

We do **not** enumerate all flag Cartesian products. Instead:

- **Nominal profiles** stay in ``runtime_profiles.RUNTIME_PROFILES`` (CI smoke covers each).
- **SUPPORTED_COMBOS** partitions those profile names into ``demo`` / ``production`` / ``lab`` buckets
  for documentation and guardrails.
- **Rule-based checks** flag invalid *relationships* between env vars (e.g. mock court without
  escalation). Default: **warn**; set ``KERNEL_ENV_VALIDATION=strict`` to raise ``ValueError``.

See ``docs/proposals/KERNEL_ENV_POLICY.md``.
"""

from __future__ import annotations

import hashlib
import logging
import os
from typing import Final

from ..runtime_profiles import profile_names

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
            "phase2_event_bus_lab",
            "untrusted_chat_input",
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


def _truthy(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _falsy_or_unset(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    if not v:
        return True
    return v in ("0", "false", "no", "off")


def collect_env_violations() -> list[str]:
    """
    Return human-readable constraint violations for the **current** process environment.

    These are *consistency* rules, not full simulation of the kernel.
    """
    violations: list[str] = []

    if _truthy("KERNEL_JUDICIAL_MOCK_COURT") and _falsy_or_unset("KERNEL_JUDICIAL_ESCALATION"):
        violations.append(
            "KERNEL_JUDICIAL_MOCK_COURT is enabled but KERNEL_JUDICIAL_ESCALATION is off; "
            "mock court runs only when escalation is enabled (see judicial_escalation.py)."
        )

    if (
        _truthy("KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION")
        and not os.environ.get("KERNEL_LIGHTHOUSE_KB_PATH", "").strip()
    ):
        violations.append(
            "KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1 without KERNEL_LIGHTHOUSE_KB_PATH; "
            "reality verification may no-op (set a fixture path for demos)."
        )

    return violations


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


def validate_kernel_env(*, mode: str | None = None) -> None:
    """
    Validate environment according to ``KERNEL_ENV_VALIDATION``:

    - ``off`` — no-op
    - ``warn`` (default) — log warnings for ``collect_env_violations()``
    - ``strict`` — raise ``ValueError`` if any violation

    ``mode`` overrides the env when set (for tests).
    """
    raw = (
        (mode if mode is not None else os.environ.get("KERNEL_ENV_VALIDATION", "")).strip().lower()
    )
    if raw in ("", "warn", "warning"):
        eff = "warn"
    elif raw in ("0", "false", "no", "off"):
        eff = "off"
    elif raw in ("1", "true", "yes", "on", "strict"):
        eff = "strict"
    else:
        eff = "warn"
        logger.warning("unknown KERNEL_ENV_VALIDATION=%r; defaulting to warn", raw)

    if eff == "off":
        return

    violations = collect_env_violations()
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
