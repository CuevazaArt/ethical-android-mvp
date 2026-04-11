"""
Named bundles of environment variables for demos, operators, and CI.

Each profile only lists **overrides**; unset keys keep process defaults.
See docs/ESTRATEGIA_Y_RUTA.md.
"""

from __future__ import annotations

from typing import Dict, Final, Mapping

# env key -> value (only non-default toggles for that demo)
RUNTIME_PROFILES: Final[Dict[str, Dict[str, str]]] = {
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
    },
    # Issue 7 — V12 hub stack: public constitution + DAO vote + deontic gate + transparency audit lines.
    "moral_hub_extended": {
        "KERNEL_MORAL_HUB_PUBLIC": "1",
        "KERNEL_MORAL_HUB_DAO_VOTE": "1",
        "KERNEL_DEONTIC_GATE": "1",
        "KERNEL_TRANSPARENCY_AUDIT": "1",
    },
    # v8 situated + LAN thin-client (sensor preset + fixture merge; no raw hardware required)
    "situated_v8_lan_demo": {
        "CHAT_HOST": "0.0.0.0",
        "CHAT_PORT": "8765",
        "KERNEL_SENSOR_FIXTURE": "tests/fixtures/sensor/minimal_situ.json",
        "KERNEL_SENSOR_PRESET": "low_battery",
        "KERNEL_CHAT_INCLUDE_VITALITY": "1",
        "KERNEL_CHAT_INCLUDE_MULTIMODAL": "1",
    },
}

PROFILE_DESCRIPTIONS: Final[Dict[str, str]] = {
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
}


def profile_names() -> tuple[str, ...]:
    return tuple(sorted(RUNTIME_PROFILES.keys()))


def describe_profiles() -> Mapping[str, str]:
    return PROFILE_DESCRIPTIONS


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
