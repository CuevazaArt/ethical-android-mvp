"""
Operator-facing view of KERNEL_* surface (Issue: configuration monolith / fatigue).

Groups keys by documented **families**, scores alignment with **nominal runtime profiles**,
and flags **experimental** combinations when many flags are set without ``ETHOS_RUNTIME_PROFILE``.

Does not replace ``validate_kernel_env()`` — use together: policy rules + this inventory.
See ``docs/proposals/README.md`` and ``docs/proposals/README.md``.
"""

from __future__ import annotations

import os
from typing import Any, Final

from ..runtime_profiles import RUNTIME_PROFILES, describe_profiles, profile_names
from .env_policy import collect_env_violations

# First matching rule wins (keep more specific prefixes before general ones).
_FAMILY_RULES: Final[tuple[tuple[str, tuple[str, ...]], ...]] = (
    ("Validation & policy", ("KERNEL_ENV_VALIDATION",)),
    (
        "Cybersecurity",
        ("KERNEL_CYBERSECURITY_", "KERNEL_SECURE_BOOT", "KERNEL_SELECTIVE_AMNESIA"),
    ),
    (
        "Chat JSON / UX",
        ("KERNEL_CHAT_INCLUDE_", "KERNEL_CHAT_EXPOSE_", "KERNEL_CHAT_EXPERIENCE_DIGEST"),
    ),
    ("Chat async / pool", ("KERNEL_CHAT_TURN_TIMEOUT", "KERNEL_CHAT_THREADPOOL_WORKERS")),
    ("Chat server bind", ("CHAT_HOST", "CHAT_PORT")),
    ("Runtime profile", ("ETHOS_RUNTIME_PROFILE",)),
    ("Persistence / checkpoints", ("KERNEL_CHECKPOINT_", "KERNEL_CONDUCT_GUIDE_")),
    ("Lighthouse / reality", ("KERNEL_LIGHTHOUSE_", "KERNEL_CHAT_INCLUDE_REALITY_")),
    ("Guardian", ("KERNEL_GUARDIAN_", "KERNEL_CHAT_INCLUDE_GUARDIAN")),
    (
        "Perception / sensors",
        (
            "KERNEL_SENSOR_",
            "KERNEL_MULTIMODAL_",
            "KERNEL_VITALITY_",
            "KERNEL_PERCEPTION_",
            "KERNEL_LIGHT_RISK_",
            "KERNEL_CROSS_CHECK_",
            "KERNEL_CHAT_INCLUDE_LIGHT_RISK",
        ),
    ),
    ("MalAbs lexical", ("KERNEL_MALABS_",)),
    ("MalAbs semantic / embed", ("KERNEL_SEMANTIC_",)),
    (
        "Governance / hub / judicial",
        (
            "KERNEL_MORAL_HUB_",
            "KERNEL_DEONTIC_",
            "KERNEL_JUDICIAL_",
            "KERNEL_DAO_",
            "KERNEL_LOCAL_SOVEREIGNTY",
        ),
    ),
    ("Nomad / identity", ("KERNEL_NOMAD_", "KERNEL_CHAT_INCLUDE_NOMAD_")),
    ("Metaplan / drives", ("KERNEL_METAPLAN_",)),
    ("Observability", ("KERNEL_METRICS", "KERNEL_LOG_", "KERNEL_API_DOCS")),
    ("Event bus (lab)", ("KERNEL_EVENT_BUS",)),
    ("Swarm (lab stub)", ("KERNEL_SWARM_STUB",)),
    (
        "Poles / mixture / temporal",
        (
            "KERNEL_POLE_",
            "KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS",
            "KERNEL_TEMPORAL_HORIZON_",
            "KERNEL_FEEDBACK_CALIBRATION",
            "KERNEL_PSI_SLEEP_",
        ),
    ),
    (
        "LLM / variability / generative",
        (
            "KERNEL_VARIABILITY",
            "KERNEL_GENERATIVE_",
            "KERNEL_VERBAL_",
            "KERNEL_LLM_TP_",
            "KERNEL_LLM_VERBAL_FAMILY_",
            "KERNEL_LLM_MONOLOGUE_BACKEND_",
            "KERNEL_LLM_MONOLOGUE",
            "LLM_MODE",
        ),
    ),
    ("Ethos runtime", ("ETHOS_",)),
)

_EXPERIMENTAL_MANY_KERNEL_KEYS: Final[int] = 10
_EXPERIMENTAL_MEDIUM_KERNEL_KEYS: Final[int] = 5


def classify_env_key(key: str) -> str:
    """Assign a human family label for operator grouping."""
    for label, prefixes in _FAMILY_RULES:
        for p in prefixes:
            if key == p or key.startswith(p):
                return label
    if key.startswith("KERNEL_"):
        return "Other KERNEL_*"
    return "Other"


def _truthy_nonempty(val: str | None) -> bool:
    return bool(val and str(val).strip())


def collect_kernel_environ_snapshot() -> dict[str, str]:
    """Non-secret KERNEL_* and related operator keys (sorted). Values as in ``os.environ``."""
    out: dict[str, str] = {}
    for k in sorted(os.environ):
        if k.startswith("KERNEL_"):
            out[k] = os.environ[k]
        elif k in ("CHAT_HOST", "CHAT_PORT", "ETHOS_RUNTIME_PROFILE", "LLM_MODE"):
            out[k] = os.environ[k]
    return out


def profile_alignment_scores() -> list[dict[str, Any]]:
    """
    For each nominal profile, fraction of **explicitly set** bundle keys that match the bundle.

    Unset variables are neutral (they would be filled by ``ETHOS_RUNTIME_PROFILE`` merge at
    startup). This avoids ranking huge bundles as “closest” when the operator has not set any
    ``KERNEL_*`` yet.
    """
    rows: list[dict[str, Any]] = []
    for name in profile_names():
        bundle = RUNTIME_PROFILES[name]
        if not bundle:
            rows.append(
                {
                    "profile": name,
                    "bundle_keys": 0,
                    "aligned": 0,
                    "explicit_in_bundle": 0,
                    "score": 0.0,
                    "mismatches": [],
                    "mismatches_truncated": False,
                }
            )
            continue
        mismatches: list[str] = []
        aligned = 0
        explicit = 0
        for k, intended in bundle.items():
            cur = os.environ.get(k)
            if not _truthy_nonempty(cur):
                continue
            explicit += 1
            eff = str(cur).strip()
            want = str(intended).strip()
            if eff == want:
                aligned += 1
            else:
                mismatches.append(f"{k}={eff!r} (profile wants {want!r})")
        total = len(bundle)
        score = (aligned / total) if total else 0.0
        rows.append(
            {
                "profile": name,
                "bundle_keys": total,
                "aligned": aligned,
                "explicit_in_bundle": explicit,
                "score": score,
                "mismatches": mismatches[:12],
                "mismatches_truncated": len(mismatches) > 12,
            }
        )
    # Prefer higher score, then more explicit keys matched, larger bundle, stable name.
    rows.sort(
        key=lambda r: (
            -float(r["score"]),
            -int(r["aligned"]),
            -int(r["bundle_keys"]),
            str(r["profile"]),
        )
    )
    return rows


def experimental_risk_level() -> dict[str, Any]:
    """
    Heuristic: many non-default KERNEL_* toggles without a named profile → higher emergent risk.

    Not a security guarantee — encourages ``ETHOS_RUNTIME_PROFILE`` + documented bundles.
    """
    snap = collect_kernel_environ_snapshot()
    kernel_only = {k: v for k, v in snap.items() if k.startswith("KERNEL_") and _truthy_nonempty(v)}
    n = len(kernel_only)
    profile = os.environ.get("ETHOS_RUNTIME_PROFILE", "").strip()
    if profile:
        level = "low"
        detail = f"ETHOS_RUNTIME_PROFILE={profile!r} is set — prefer documented bundles; explicit env still overrides."
    elif n >= _EXPERIMENTAL_MANY_KERNEL_KEYS:
        level = "high"
        detail = (
            f"{n} KERNEL_* variables are set without ETHOS_RUNTIME_PROFILE — "
            "combinatorial surface is large; prefer a nominal profile from runtime_profiles.py "
            "unless you are debugging a specific flag."
        )
    elif n >= _EXPERIMENTAL_MEDIUM_KERNEL_KEYS:
        level = "medium"
        detail = (
            f"{n} KERNEL_* variables set without ETHOS_RUNTIME_PROFILE — "
            "document your combo or switch to a named profile for CI-tested viability."
        )
    else:
        level = "low"
        detail = "Few KERNEL_* overrides or profile is set — typical for baseline/minimal setups."

    return {
        "level": level,
        "kernel_non_empty_count": n,
        "ethos_runtime_profile": profile or None,
        "detail": detail,
    }


def build_operator_config_report() -> dict[str, Any]:
    """Single JSON-serializable report for CLI and tooling."""
    snap = collect_kernel_environ_snapshot()
    by_family: dict[str, list[tuple[str, str]]] = {}
    for k, v in snap.items():
        fam = classify_env_key(k)
        by_family.setdefault(fam, []).append((k, v))
    for fam in by_family:
        by_family[fam].sort(key=lambda t: t[0])

    violations = collect_env_violations()
    risk = experimental_risk_level()
    profiles_ranked = profile_alignment_scores()
    best = profiles_ranked[0] if profiles_ranked else None
    # Avoid implying a "closest" nominal profile when nothing is explicitly configured.
    closest: dict[str, Any] | None = None
    if (
        risk["kernel_non_empty_count"] > 0
        and best
        and best["bundle_keys"] > 0
        and best.get("explicit_in_bundle", 0) > 0
    ):
        closest = {
            "profile": best["profile"],
            "score": best["score"],
            "aligned": best["aligned"],
            "bundle_keys": best["bundle_keys"],
            "explicit_in_bundle": best.get("explicit_in_bundle", 0),
        }

    return {
        "environ_key_count": len(snap),
        "by_family": {
            k: [{"key": a, "value": b} for a, b in v] for k, v in sorted(by_family.items())
        },
        "policy_violations": violations,
        "experimental_risk": risk,
        "profile_alignment": profiles_ranked,
        "closest_profile_hint": closest,
        "profile_descriptions": dict(describe_profiles()),
    }
