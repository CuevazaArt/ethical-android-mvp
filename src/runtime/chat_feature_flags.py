"""
Chat Feature Flags — Helper functions for extracting KERNEL_* environment variables.
Part of the Block 28.1 monolith decoupling.
"""

from __future__ import annotations
import os
import math
from typing import Any

def env_truthy(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")

def chat_expose_monologue() -> bool:
    """If false, omit monologue from WebSocket JSON (privacy; skips LLM embellishment)."""
    v = os.environ.get("KERNEL_CHAT_EXPOSE_MONOLOGUE", "1").strip().lower()
    return v not in ("0", "false", "no", "off")

def chat_include_homeostasis() -> bool:
    """If false, omit affective_homeostasis (pilar 4 UX telemetry)."""
    v = os.environ.get("KERNEL_CHAT_INCLUDE_HOMEOSTASIS", "1").strip().lower()
    return v not in ("0", "false", "no", "off")

def chat_include_experience_digest() -> bool:
    """If false, omit experience_digest (pilar 3; updated in Ψ Sleep)."""
    v = os.environ.get("KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST", "1").strip().lower()
    return v not in ("0", "false", "no", "off")

def chat_include_user_model() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_USER_MODEL", "1").strip().lower()
    return v not in ("0", "false", "no", "off")

def chat_include_chrono() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_CHRONO", "1").strip().lower()
    return v not in ("0", "false", "no", "off")

def chat_include_premise() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_PREMISE", "1").strip().lower()
    return v not in ("0", "false", "no", "off")

def chat_include_teleology() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_TELEOLOGY", "1").strip().lower()
    return v not in ("0", "false", "no", "off")

def chat_include_multimodal_trust() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_MULTIMODAL", "1").strip().lower()
    return v not in ("0", "false", "no", "off")

def chat_include_vitality() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_VITALITY", "1").strip().lower()
    return v not in ("0", "false", "no", "off")

def chat_include_guardian() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_GUARDIAN", "1").strip().lower()
    return v not in ("0", "false", "no", "off")

def chat_include_guardian_routines() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_GUARDIAN_ROUTINES", "0").strip().lower()
    return v in ("1", "true", "yes", "on")

def chat_include_epistemic() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_EPISTEMIC", "1").strip().lower()
    return v not in ("0", "false", "no", "off")

def chat_include_reality_verification() -> bool:
    """Lighthouse KB vs asserted premises — ``reality_verification`` in JSON (default off)."""
    v = os.environ.get("KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION", "0").strip().lower()
    return v in ("1", "true", "yes", "on")

def chat_include_judicial() -> bool:
    """V11 Phase 1 — include judicial_escalation when KERNEL_CHAT_INCLUDE_JUDICIAL is on."""
    from src.modules.judicial_escalation import chat_include_judicial as ci_judicial
    return ci_judicial()

def chat_include_constitution() -> bool:
    """V12 — include full constitution JSON (L0 + L1/L2 drafts) on WebSocket payloads."""
    from src.modules.moral_hub import chat_include_constitution as ci_constitution
    return ci_constitution()

def chat_include_nomad_identity() -> bool:
    """Include NomadIdentity / immortality bridge summary (see UNIVERSAL_ETHOS_AND_HUB.md)."""
    v = os.environ.get("KERNEL_CHAT_INCLUDE_NOMAD_IDENTITY", "0").strip().lower()
    return v in ("1", "true", "yes", "on")

def chat_include_light_risk() -> bool:
    """Lexical ``light_risk_tier`` from ``KERNEL_LIGHT_RISK_CLASSIFIER`` (default off in JSON)."""
    v = os.environ.get("KERNEL_CHAT_INCLUDE_LIGHT_RISK", "0").strip().lower()
    return v in ("1", "true", "yes", "on")

def chat_include_malabs_trace() -> bool:
    """Include ``malabs_trace`` (atomic decision steps) when the last chat MalAbs result has them."""
    from src.settings import kernel_settings
    return kernel_settings().kernel_chat_include_malabs_trace

def chat_include_transparency_s10() -> bool:
    """Embodied sociability S10.1/S10.3/S10.4 — ``transparency_s10`` in WebSocket JSON (default on)."""
    v = os.environ.get("KERNEL_CHAT_INCLUDE_TRANSPARENCY_S10", "1").strip().lower()
    return v not in ("0", "false", "no", "off")

def coerce_public_int(value: object, *, default: int = 0, non_negative: bool = False) -> int:
    """
    JSON-safe int for public WebSocket payloads (e.g. temporal_sync).
    """
    if value is None:
        out = default
    elif isinstance(value, bool):
        out = default
    elif isinstance(value, int):
        out = value
    elif isinstance(value, float):
        out = int(value) if math.isfinite(value) else default
    elif isinstance(value, str):
        try:
            s = value.strip()
            out = int(s, 10) if s else default
        except ValueError:
            out = default
    else:
        out = default
    if non_negative:
        out = max(0, out)
    return out
