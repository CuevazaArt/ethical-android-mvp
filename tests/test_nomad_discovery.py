from __future__ import annotations

from src.modules.perception.nomad_discovery import build_nomad_discovery_payload


def test_nomad_discovery_payload_shape():
    payload = build_nomad_discovery_payload(
        request_host="192.168.1.20",
        request_scheme="http",
        bind_host="0.0.0.0",
        bind_port=8765,
        mdns_registered=False,
        mdns_service_name="ethos-kernel",
        mdns_service_type="_ethos-kernel._tcp.local.",
    )

    assert payload["schema"] == "nomad_discovery_v1"
    assert payload["service"] == "ethos-kernel-chat"
    assert isinstance(payload["candidates"], list)
    assert len(payload["candidates"]) >= 1

    row = payload["candidates"][0]
    assert row["chat_ws"].endswith("/ws/chat")
    assert row["nomad_ws"].endswith("/nomad_bridge/ws/nomad")
    assert row["dashboard_ws"].endswith("/ws/dashboard")
    assert row["nomad_ui"].endswith("/nomad/")
