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
}

PROFILE_DESCRIPTIONS: Final[Dict[str, str]] = {
    "baseline": "Default server flags; minimal regression surface.",
    "judicial_demo": "V11 judicial escalation + mock court + judicial JSON in chat.",
    "hub_dao_demo": "V12 public constitution HTTP + WebSocket dao_list / vote / resolve.",
    "nomad_demo": "Nomadic HAL migration simulation + optional DAO migration audit line.",
    "reality_lighthouse_demo": "Lighthouse KB path + WebSocket reality_verification JSON (run from repo root).",
    "lan_mobile_thin_client": "Bind chat server on all interfaces for phone browser on same WiFi (see LOCAL_PC_AND_MOBILE_LAN.md).",
}


def profile_names() -> tuple[str, ...]:
    return tuple(sorted(RUNTIME_PROFILES.keys()))


def describe_profiles() -> Mapping[str, str]:
    return PROFILE_DESCRIPTIONS
