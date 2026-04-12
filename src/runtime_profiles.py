"""
Named bundles of environment variables for demos, operators, and CI.

Each profile only lists **overrides**; unset keys keep process defaults.
See docs/proposals/STRATEGY_AND_ROADMAP.md.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Final

# Set by :func:`apply_named_runtime_profile_to_environ` when ``ETHOS_RUNTIME_PROFILE`` is used.
_APPLIED_RUNTIME_PROFILE: str | None = None

# env key -> value (only non-default toggles for that demo)
RUNTIME_PROFILES: Final[dict[str, dict[str, str]]] = {
    "baseline": {},
    "judicial_demo": {
        "KERNEL_JUDICIAL_ESCALATION": "1",
        "KERNEL_JUDICIAL_MOCK_COURT": "1",
        "KERNEL_CHAT_INCLUDE_JUDICIAL": "1",
    },
    "hub_dao_demo": {
        "KERNEL_MORAL_HUB_PUBLIC": "1",
        "KERNEL_MORAL_HUB_DAO_VOTE": "1",
    },
    "nomad_demo": {
        "KERNEL_NOMAD_SIMULATION": "1",
        "KERNEL_NOMAD_MIGRATION_AUDIT": "1",
    },
    "reality_lighthouse_demo": {
        "KERNEL_LIGHTHOUSE_KB_PATH": "tests/fixtures/lighthouse/demo_kb.json",
        "KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION": "1",
    },
    "lan_mobile_thin_client": {
        "CHAT_HOST": "0.0.0.0",
        "CHAT_PORT": "8765",
        "KERNEL_SEMANTIC_CHAT_GATE": "1",
        "KERNEL_SEMANTIC_EMBED_HASH_FALLBACK": "1",
    },
    # Issue 5 — HCI: reduce narrative vulnerability signals in WebSocket JSON (policy unchanged).
    "operational_trust": {
        "KERNEL_CHAT_INCLUDE_HOMEOSTASIS": "0",
        "KERNEL_CHAT_EXPOSE_MONOLOGUE": "0",
        "KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST": "0",
    },
    # Issue 7 — LAN bind + stoic UX (field / operator-facing demo).
    "lan_operational": {
        "CHAT_HOST": "0.0.0.0",
        "CHAT_PORT": "8765",
        "KERNEL_CHAT_INCLUDE_HOMEOSTASIS": "0",
        "KERNEL_CHAT_EXPOSE_MONOLOGUE": "0",
        "KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST": "0",
        "KERNEL_SEMANTIC_CHAT_GATE": "1",
        "KERNEL_SEMANTIC_EMBED_HASH_FALLBACK": "1",
    },
    # Issue 7 — V12 hub stack: public constitution + DAO vote + deontic gate + transparency audit lines.
    "moral_hub_extended": {
        "KERNEL_MORAL_HUB_PUBLIC": "1",
        "KERNEL_MORAL_HUB_DAO_VOTE": "1",
        "KERNEL_DEONTIC_GATE": "1",
        "KERNEL_TRANSPARENCY_AUDIT": "1",
        "KERNEL_SEMANTIC_CHAT_GATE": "1",
        "KERNEL_SEMANTIC_EMBED_HASH_FALLBACK": "1",
    },
    # v8 situated + LAN thin-client (sensor preset + fixture merge; no raw hardware required)
    "situated_v8_lan_demo": {
        "CHAT_HOST": "0.0.0.0",
        "CHAT_PORT": "8765",
        "KERNEL_SENSOR_FIXTURE": "tests/fixtures/sensor/minimal_situ.json",
        "KERNEL_SENSOR_PRESET": "low_battery",
        "KERNEL_CHAT_INCLUDE_VITALITY": "1",
        "KERNEL_CHAT_INCLUDE_MULTIMODAL": "1",
        "KERNEL_SEMANTIC_CHAT_GATE": "1",
        "KERNEL_SEMANTIC_EMBED_HASH_FALLBACK": "1",
    },
    # Production-hardening Fase 1 — lexical tier + cross-check + optional delib nudge + parse fail-closed + JSON tier field.
    "perception_hardening_lab": {
        "KERNEL_LIGHT_RISK_CLASSIFIER": "1",
        "KERNEL_PERCEPTION_CROSS_CHECK": "1",
        "KERNEL_PERCEPTION_UNCERTAINTY_DELIB": "1",
        "KERNEL_PERCEPTION_UNCERTAINTY_MIN": "0.35",
        "KERNEL_PERCEPTION_PARSE_FAIL_LOCAL": "1",
        "KERNEL_CHAT_INCLUDE_LIGHT_RISK": "1",
    },
    # ADR 0006 — Phase 2 seam: in-process event bus for extensions / telemetry.
    "phase2_event_bus_lab": {
        "KERNEL_EVENT_BUS": "1",
    },
    # Semantic MalAbs tier on without Ollama (deterministic hash embeddings); compose with LAN or hub profiles.
    "untrusted_chat_input": {
        "KERNEL_SEMANTIC_CHAT_GATE": "1",
        "KERNEL_SEMANTIC_EMBED_HASH_FALLBACK": "1",
    },
    # Explicit lexical-only MalAbs (airgap / latency); semantic tier off.
    "lexical_malabs_only": {
        "KERNEL_SEMANTIC_CHAT_GATE": "0",
    },
}

PROFILE_DESCRIPTIONS: Final[dict[str, str]] = {
    "baseline": "Default server flags; minimal regression surface.",
    "judicial_demo": "V11 judicial escalation + mock court + judicial JSON in chat.",
    "hub_dao_demo": "V12 public constitution HTTP + WebSocket dao_list / vote / resolve.",
    "nomad_demo": "Nomadic HAL migration simulation + optional DAO migration audit line.",
    "reality_lighthouse_demo": "Lighthouse KB path + WebSocket reality_verification JSON (run from repo root).",
    "lan_mobile_thin_client": "Bind chat server on all interfaces for phone browser on same WiFi (see LOCAL_PC_AND_MOBILE_LAN.md).",
    "operational_trust": "Stoic chat UX: omit homeostasis, monologue, experience_digest (Issue 5 — see POLES_WEAKNESS_PAD_AND_PROFILES.md).",
    "lan_operational": "LAN bind + operational_trust UX (Issue 7 — see KERNEL_ENV_POLICY.md).",
    "moral_hub_extended": "V12 moral hub: constitution HTTP + DAO vote + deontic gate + transparency audit (Issue 7).",
    "situated_v8_lan_demo": "V8 situated: LAN bind + sensor fixture+preset merge, vitality + multimodal JSON (see DEMO_SITUATED_V8.md, LOCAL_PC_AND_MOBILE_LAN.md).",
    "perception_hardening_lab": "Fase 1 hardening: light risk tier + perception cross-check + uncertainty→D_delib + parse fail-local + light_risk_tier in WebSocket JSON (see PRODUCTION_HARDENING_ROADMAP.md, KERNEL_ENV_POLICY.md).",
    "phase2_event_bus_lab": "Phase 2 spike: KERNEL_EVENT_BUS for kernel.decision / kernel.episode_registered (ADR 0006, PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md).",
    "untrusted_chat_input": "Semantic MalAbs on + KERNEL_SEMANTIC_EMBED_HASH_FALLBACK for CI/airgap without Ollama (PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION B2).",
    "lexical_malabs_only": "Force KERNEL_SEMANTIC_CHAT_GATE=0 (lexical MalAbs only).",
}


def profile_names() -> tuple[str, ...]:
    return tuple(sorted(RUNTIME_PROFILES.keys()))


def describe_profiles() -> Mapping[str, str]:
    return PROFILE_DESCRIPTIONS


def applied_runtime_profile() -> str | None:
    """Profile name applied at process startup via ``ETHOS_RUNTIME_PROFILE``, if any."""
    return _APPLIED_RUNTIME_PROFILE


def apply_named_runtime_profile_to_environ() -> str | None:
    """
    Merge ``RUNTIME_PROFILES[name]`` into ``os.environ`` when ``ETHOS_RUNTIME_PROFILE`` is set.

    **Precedence:** explicit environment variables win. Only keys that are unset or empty-string
    are filled from the profile bundle.

    Call once at chat server import time (before ``FastAPI`` reads settings).

    Raises:
        ValueError: if the profile name is unknown.
    """
    global _APPLIED_RUNTIME_PROFILE
    raw = os.environ.get("ETHOS_RUNTIME_PROFILE", "").strip()
    if not raw:
        _APPLIED_RUNTIME_PROFILE = None
        return None
    try:
        overrides = RUNTIME_PROFILES[raw]
    except KeyError as e:
        choices = ", ".join(sorted(RUNTIME_PROFILES.keys()))
        raise ValueError(f"unknown ETHOS_RUNTIME_PROFILE={raw!r}; choose one of: {choices}") from e
    for key, val in overrides.items():
        cur = os.environ.get(key)
        if cur is None or not str(cur).strip():
            os.environ[key] = val
    _APPLIED_RUNTIME_PROFILE = raw
    return raw


def apply_runtime_profile(monkeypatch, name: str) -> None:
    """
    Apply ``RUNTIME_PROFILES[name]`` via ``monkeypatch.setenv`` (pytest).

    Keeps profile application consistent across tests; see ``tests/test_runtime_profiles.py``
    and CI (full ``pytest tests/``).
    """
    try:
        overrides = RUNTIME_PROFILES[name]
    except KeyError as e:
        raise KeyError(f"unknown runtime profile: {name!r}") from e
    for key, value in overrides.items():
        monkeypatch.setenv(key, value)
