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

"""
Mesh Protocol Data Models.
Standard dataclasses for mesh networking payloads.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Optional


@dataclass
class DiscoveryCapabilities:
    available_ram_mb: int
    has_microphone: bool
    has_camera: bool = False
    slm_available: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DiscoveryCapabilities:
        return cls(**data)


@dataclass
class DiscoveryPayload:
    protocol_version: str
    device_id: str
    ip: str
    port: int
    capabilities: DiscoveryCapabilities

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["capabilities"] = self.capabilities.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DiscoveryPayload:
        caps_data = data.pop("capabilities")
        return cls(
            capabilities=DiscoveryCapabilities.from_dict(caps_data),
            **data
        )


@dataclass
class BatteryInfo:
    level: float
    is_charging: bool
    temperature_c: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BatteryInfo:
        return cls(**data)


@dataclass
class CpuInfo:
    temperature_c: float
    load_percent: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CpuInfo:
        return cls(**data)


@dataclass
class MemoryInfo:
    available_mb: int
    total_mb: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryInfo:
        return cls(**data)


@dataclass
class TelemetryPayload:
    protocol_version: str
    device_id: str
    timestamp_ms: int
    battery: BatteryInfo
    cpu: CpuInfo
    type: str = "telemetry"
    memory: Optional[MemoryInfo] = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["battery"] = self.battery.to_dict()
        data["cpu"] = self.cpu.to_dict()
        if self.memory:
            data["memory"] = self.memory.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TelemetryPayload:
        battery_data = data.pop("battery")
        cpu_data = data.pop("cpu")
        memory_data = data.pop("memory", None)

        return cls(
            battery=BatteryInfo.from_dict(battery_data),
            cpu=CpuInfo.from_dict(cpu_data),
            memory=MemoryInfo.from_dict(memory_data) if memory_data else None,
            **data
        )


@dataclass
class AudioChunkHeader:
    protocol_version: str
    device_id: str
    seq: int
    pcm_length_bytes: int
    timestamp_ms: int
    type: str = "audio_chunk"
    sample_rate_hz: int = 16000
    channels: int = 1
    bits_per_sample: int = 16

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AudioChunkHeader:
        return cls(**data)
