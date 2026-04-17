"""
E1 — Governable parameters contract (ADR 0016 Axis E1).

Declares the **explicit surface** of Ethos Kernel parameters that the DAO
can propose changes to. Any parameter NOT listed here is considered internal
kernel implementation detail and must NOT be changed via DAO vote.

This file is the single authoritative inventory. It is imported by:
  - src/dao/audit_snapshot.py (snapshot serialisation)
  - MockDAO (future: validate that proposals reference known parameters)
  - tests/integration/ (governance boundary invariant tests)

Governance constraints:
  - DAO votes are **advisory only** in the current architecture; they do not
    override L0 / MalAbs / BayesianEngine argmax (see WEAKNESSES §4).
  - Changes to parameters below must go through the MockDAO proposal cycle
    and be recorded in the audit sidecar before taking effect.
  - Hard safety floors/ceilings are enforced in code, not by DAO vote.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ParameterSpec:
    """
    Specification for a single DAO-governable kernel parameter.

    Attributes
    ----------
    name:
        Canonical parameter name (env var or internal key).
    tier:
        Which kernel tier owns the parameter:
        ``"scoring"``  — affects mixture weights / scorer behaviour
        ``"narrative"``— affects tone, monologue, guardian style
        ``"safety"``   — hard safety floors (extra scrutiny required)
        ``"governance"``— DAO / audit parameters
        ``"sensor"``   — multimodal / situated-sensor thresholds
    description:
        Human-readable explanation of what the parameter does.
    env_var:
        Environment variable name (None for internal-only params).
    dtype:
        Python type name string: ``"float"``, ``"int"``, ``"bool"``, ``"str"``.
    default_value:
        The default value used when the env var is absent or empty.
    floor:
        Minimum allowed value (inclusive). None = no floor.
    ceiling:
        Maximum allowed value (inclusive). None = no ceiling.
    requires_restart:
        True if the kernel must be restarted for the change to take effect.
    safety_critical:
        True if this parameter directly impacts harm prevention. Extra DAO
        scrutiny (higher quorum) should be required before approving.
    """

    name: str
    tier: str
    description: str
    env_var: str | None
    dtype: str
    default_value: Any
    floor: Any = None
    ceiling: Any = None
    requires_restart: bool = False
    safety_critical: bool = False


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

GOVERNABLE_PARAMETERS: dict[str, ParameterSpec] = {}


def _reg(spec: ParameterSpec) -> None:
    GOVERNABLE_PARAMETERS[spec.name] = spec


# ── Scoring tier ────────────────────────────────────────────────────────────

_reg(
    ParameterSpec(
        name="mixture_weight_utilitarian",
        tier="scoring",
        description="Utilitarian hypothesis weight in the ethical mixture scorer "
        "(ADR 0012). Must sum to 1.0 across the three weights.",
        env_var=None,  # set via pole_linear_default.json or KERNEL_POLE_LINEAR_PATH
        dtype="float",
        default_value=0.34,
        floor=0.05,
        ceiling=0.90,
        requires_restart=False,
        safety_critical=False,
    )
)

_reg(
    ParameterSpec(
        name="mixture_weight_deontological",
        tier="scoring",
        description="Deontological hypothesis weight.",
        env_var=None,
        dtype="float",
        default_value=0.33,
        floor=0.05,
        ceiling=0.90,
        requires_restart=False,
        safety_critical=False,
    )
)

_reg(
    ParameterSpec(
        name="mixture_weight_virtue",
        tier="scoring",
        description="Virtue-ethics hypothesis weight.",
        env_var=None,
        dtype="float",
        default_value=0.33,
        floor=0.05,
        ceiling=0.90,
        requires_restart=False,
        safety_critical=False,
    )
)

_reg(
    ParameterSpec(
        name="KERNEL_PRUNING_THRESHOLD",
        tier="scoring",
        description="Minimum ethical score for a candidate action to survive MalAbs "
        "pruning. Raising this tightens the safety gate.",
        env_var="KERNEL_PRUNING_THRESHOLD",
        dtype="float",
        default_value=0.3,
        floor=0.1,
        ceiling=0.8,
        requires_restart=False,
        safety_critical=True,
    )
)

_reg(
    ParameterSpec(
        name="KERNEL_MALABS_MODE",
        tier="scoring",
        description="MalAbs operating mode: ``lexical`` (fast, keyword-based) or "
        "``semantic`` (embedding-based, requires Ollama). Switching to "
        "``lexical`` reduces safety coverage.",
        env_var="KERNEL_SEMANTIC_CHAT_GATE",
        dtype="bool",
        default_value=True,
        requires_restart=False,
        safety_critical=True,
    )
)

# ── Safety tier ──────────────────────────────────────────────────────────────

_reg(
    ParameterSpec(
        name="KERNEL_ABSOLUTE_EVIL_THRESHOLD",
        tier="safety",
        description="Score above which an action is classified as absolute evil and "
        "hard-blocked regardless of mixture scorer output. HARD FLOOR enforced.",
        env_var="KERNEL_ABSOLUTE_EVIL_THRESHOLD",
        dtype="float",
        default_value=0.95,
        floor=0.80,  # DAO may NOT lower below 0.80 — safety floor
        ceiling=1.0,
        requires_restart=False,
        safety_critical=True,
    )
)

_reg(
    ParameterSpec(
        name="KERNEL_VITALITY_CRITICAL_BATTERY",
        tier="safety",
        description="Battery fraction (0–1) below which the kernel switches to "
        "conservative/guardian mode automatically.",
        env_var="KERNEL_VITALITY_CRITICAL_BATTERY",
        dtype="float",
        default_value=0.15,
        floor=0.05,
        ceiling=0.50,
        requires_restart=False,
        safety_critical=False,
    )
)

# ── Narrative tier ───────────────────────────────────────────────────────────

_reg(
    ParameterSpec(
        name="KERNEL_GUARDIAN_MODE",
        tier="narrative",
        description="Enable protective/guardian tone in the LLM layer. Does NOT "
        "change final_action selection.",
        env_var="KERNEL_GUARDIAN_MODE",
        dtype="bool",
        default_value=False,
        requires_restart=False,
        safety_critical=False,
    )
)

_reg(
    ParameterSpec(
        name="KERNEL_LLM_MONOLOGUE",
        tier="narrative",
        description="Include internal monologue field in WebSocket JSON responses.",
        env_var="KERNEL_LLM_MONOLOGUE",
        dtype="bool",
        default_value=False,
        requires_restart=False,
        safety_critical=False,
    )
)

# ── Sensor tier ──────────────────────────────────────────────────────────────

_reg(
    ParameterSpec(
        name="KERNEL_MULTIMODAL_AUDIO_STRONG",
        tier="sensor",
        description="Audio emergency score threshold above which the multimodal "
        "trust module raises a strong alarm signal.",
        env_var="KERNEL_MULTIMODAL_AUDIO_STRONG",
        dtype="float",
        default_value=0.75,
        floor=0.50,
        ceiling=0.99,
        requires_restart=False,
        safety_critical=False,
    )
)

_reg(
    ParameterSpec(
        name="KERNEL_MULTIMODAL_VISION_SUPPORT",
        tier="sensor",
        description="Vision emergency score above which vision corroborates audio alarm.",
        env_var="KERNEL_MULTIMODAL_VISION_SUPPORT",
        dtype="float",
        default_value=0.60,
        floor=0.30,
        ceiling=0.99,
        requires_restart=False,
        safety_critical=False,
    )
)

_reg(
    ParameterSpec(
        name="KERNEL_FIELD_SENSOR_HZ",
        tier="sensor",
        description="Maximum sensor frame rate (Hz) accepted from a phone relay "
        "(ADR 0017). Higher values increase thread-pool load.",
        env_var="KERNEL_FIELD_SENSOR_HZ",
        dtype="int",
        default_value=2,
        floor=1,
        ceiling=10,
        requires_restart=False,
        safety_critical=False,
    )
)

# ── Governance tier ──────────────────────────────────────────────────────────

_reg(
    ParameterSpec(
        name="KERNEL_JUDICIAL_STRIKES_FOR_DOSSIER",
        tier="governance",
        description="Number of ethical strikes in a session before an escalation "
        "dossier is submitted to MockDAO for review.",
        env_var="KERNEL_JUDICIAL_STRIKES_FOR_DOSSIER",
        dtype="int",
        default_value=2,
        floor=1,
        ceiling=10,
        requires_restart=False,
        safety_critical=False,
    )
)

_reg(
    ParameterSpec(
        name="KERNEL_AUDIT_SIDECAR_PATH",
        tier="governance",
        description="Filesystem path for the append-only MockDAO audit sidecar. "
        "Changing this path requires a new file with proper permissions.",
        env_var="KERNEL_AUDIT_SIDECAR_PATH",
        dtype="str",
        default_value="",
        requires_restart=True,  # new path takes effect on restart
        safety_critical=False,
    )
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_parameter(name: str) -> ParameterSpec | None:
    """Return the spec for a named parameter, or None if not governable."""
    return GOVERNABLE_PARAMETERS.get(name)


def safety_critical_names() -> list[str]:
    """Return all parameter names flagged safety_critical=True."""
    return [n for n, s in GOVERNABLE_PARAMETERS.items() if s.safety_critical]


def parameters_by_tier(tier: str) -> list[ParameterSpec]:
    """Return all parameters for a given tier."""
    return [s for s in GOVERNABLE_PARAMETERS.values() if s.tier == tier]


def validate_proposed_value(name: str, value: Any) -> tuple[bool, str]:
    """
    Check whether a proposed new value for a parameter is within allowed bounds.

    Returns
    -------
    (ok, reason)
        ok=True means the value is admissible; reason is empty string.
        ok=False means the DAO proposal should be rejected with the given reason.
    """
    spec = GOVERNABLE_PARAMETERS.get(name)
    if spec is None:
        return False, f"Parameter '{name}' is not in the governable surface."

    v: float | int | bool | str
    try:
        if spec.dtype == "float":
            v = float(value)
        elif spec.dtype == "int":
            v = int(value)
        elif spec.dtype == "bool":
            v = bool(value)
        else:
            v = str(value)
    except (TypeError, ValueError) as exc:
        return False, f"Cannot coerce {value!r} to {spec.dtype}: {exc}"

    if spec.floor is not None and v < spec.floor:
        return False, (
            f"Value {v} is below the safety floor {spec.floor} for '{name}'. "
            "DAO cannot approve values below this threshold."
        )
    if spec.ceiling is not None and v > spec.ceiling:
        return False, f"Value {v} exceeds the ceiling {spec.ceiling} for '{name}'."

    return True, ""
