# Copyright 2026 Ethos Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from src.core.models.mesh_models import (
    DiscoveryPayload,
    DiscoveryCapabilities,
    TelemetryPayload,
    BatteryInfo,
    CpuInfo,
    MemoryInfo,
    AudioChunkHeader
)


def test_discovery_payload_serialization():
    caps = DiscoveryCapabilities(
        available_ram_mb=4096,
        has_microphone=True,
        has_camera=True,
        slm_available=True
    )
    payload = DiscoveryPayload(
        protocol_version="1.0",
        device_id="node-001",
        ip="192.168.1.50",
        port=8443,
        capabilities=caps
    )

    data = payload.to_dict()
    assert data["protocol_version"] == "1.0"
    assert data["capabilities"]["available_ram_mb"] == 4096
    assert data["capabilities"]["slm_available"] is True

    restored = DiscoveryPayload.from_dict(data)
    assert restored.device_id == "node-001"
    assert restored.capabilities.available_ram_mb == 4096
    assert restored.capabilities.has_camera is True


def test_telemetry_payload_serialization():
    battery = BatteryInfo(level=0.85, is_charging=False, temperature_c=32.5)
    cpu = CpuInfo(temperature_c=45.0, load_percent=12.5)
    memory = MemoryInfo(available_mb=2048, total_mb=8192)

    payload = TelemetryPayload(
        protocol_version="1.0",
        device_id="node-001",
        timestamp_ms=1620000000000,
        battery=battery,
        cpu=cpu,
        memory=memory
    )

    data = payload.to_dict()
    assert data["type"] == "telemetry"
    assert data["battery"]["level"] == 0.85
    assert data["cpu"]["temperature_c"] == 45.0
    assert data["memory"]["available_mb"] == 2048

    restored = TelemetryPayload.from_dict(data)
    assert restored.device_id == "node-001"
    assert restored.battery.temperature_c == 32.5
    assert restored.memory.total_mb == 8192


def test_telemetry_payload_optional_memory():
    battery = BatteryInfo(level=0.5, is_charging=True)
    cpu = CpuInfo(temperature_c=40.0)

    payload = TelemetryPayload(
        protocol_version="1.0",
        device_id="node-001",
        timestamp_ms=1620000000000,
        battery=battery,
        cpu=cpu,
        memory=None
    )

    data = payload.to_dict()
    assert "memory" not in data or data["memory"] is None
    
    restored = TelemetryPayload.from_dict(data)
    assert restored.memory is None


def test_audio_chunk_header_serialization():
    header = AudioChunkHeader(
        protocol_version="1.0",
        device_id="node-001",
        seq=42,
        pcm_length_bytes=3200,
        timestamp_ms=1620000000100
    )

    data = header.to_dict()
    assert data["type"] == "audio_chunk"
    assert data["seq"] == 42
    assert data["sample_rate_hz"] == 16000

    restored = AudioChunkHeader.from_dict(data)
    assert restored.seq == 42
    assert restored.pcm_length_bytes == 3200
    assert restored.bits_per_sample == 16
