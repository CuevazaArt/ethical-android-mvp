# Mesh Protocol V1 — JSON Schema Contract

> **Authority:** Scout-Opus-1 · Ethos Kernel ↔ Nomad Android Parasite
> **Wire format:** JSON over WebSocket (`ws://<host>:<port>/ws/mesh`)
> **Byte order:** Little-endian for binary fields (PCM audio)
> **Versioning:** Every payload carries `protocol_version`. The kernel MUST reject payloads with an unknown major version. Minor bumps are backward-compatible.

---

## 1. `DiscoveryPayload`

Emitted by the Android node via mDNS TXT record on service type `_ethos._tcp.local.`.
The kernel's `MeshListener` parses TXT properties into this schema to populate the device roster.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://ethos-kernel.dev/schemas/mesh/discovery-v1.json",
  "title": "DiscoveryPayload",
  "description": "Advertised by an Android Nomad node during mDNS service registration. Fields map 1:1 to mDNS TXT record keys.",
  "type": "object",
  "required": ["protocol_version", "device_id", "ip", "port", "capabilities"],
  "additionalProperties": false,
  "properties": {
    "protocol_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$",
      "description": "Semantic version of this mesh protocol (e.g. '1.0'). Major changes break compat.",
      "examples": ["1.0"]
    },
    "device_id": {
      "type": "string",
      "minLength": 8,
      "maxLength": 64,
      "pattern": "^[a-zA-Z0-9_-]+$",
      "description": "Stable unique identifier for the Android node. Derived from ANDROID_ID or a locally-generated UUID persisted in SharedPreferences."
    },
    "ip": {
      "type": "string",
      "format": "ipv4",
      "description": "LAN IPv4 address the node is reachable on."
    },
    "port": {
      "type": "integer",
      "minimum": 1024,
      "maximum": 65535,
      "description": "TCP port the node's WebSocket server listens on."
    },
    "capabilities": {
      "type": "object",
      "description": "Hardware and software capabilities of this node.",
      "required": ["available_ram_mb", "has_microphone"],
      "additionalProperties": false,
      "properties": {
        "available_ram_mb": {
          "type": "integer",
          "minimum": 0,
          "description": "Free RAM in megabytes at discovery time."
        },
        "has_microphone": {
          "type": "boolean",
          "description": "Whether the device has a functional microphone for audio streaming."
        },
        "has_camera": {
          "type": "boolean",
          "default": false,
          "description": "Whether the device can stream video frames."
        },
        "slm_available": {
          "type": "boolean",
          "default": false,
          "description": "Whether a small language model is loaded locally on this node."
        }
      }
    }
  }
}
```

### Design rationale

| Decision | Why |
|----------|-----|
| `device_id` is opaque string, not UUID | Android's `ANDROID_ID` is hex, not UUID format. Accepting both avoids unnecessary conversion. |
| `capabilities` is a nested object | Flat payloads don't scale. When we add GPU info or sensor inventory, we extend this object without touching top-level keys. |
| `port` minimum is 1024 | Nomad nodes are unprivileged processes; they cannot bind below 1024. |
| No `hostname` field | mDNS already provides the hostname in the service record. Duplicating it here invites drift. |

---

## 2. `TelemetryPayload`

Heartbeat sent by Android → Kernel at a configurable interval (default: every 5 seconds).
Transmitted as a JSON text frame on the established WebSocket connection.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://ethos-kernel.dev/schemas/mesh/telemetry-v1.json",
  "title": "TelemetryPayload",
  "description": "Periodic heartbeat from an Android Nomad node reporting hardware vitals.",
  "type": "object",
  "required": ["protocol_version", "type", "device_id", "timestamp_ms", "battery", "cpu"],
  "additionalProperties": false,
  "properties": {
    "protocol_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$"
    },
    "type": {
      "type": "string",
      "const": "telemetry",
      "description": "Discriminator field for payload routing on the WebSocket."
    },
    "device_id": {
      "type": "string",
      "minLength": 8,
      "maxLength": 64,
      "description": "Must match the device_id from the DiscoveryPayload."
    },
    "timestamp_ms": {
      "type": "integer",
      "minimum": 0,
      "description": "Unix epoch milliseconds (System.currentTimeMillis()). Kernel uses this for clock-drift detection and heartbeat timeout."
    },
    "battery": {
      "type": "object",
      "required": ["level", "is_charging"],
      "additionalProperties": false,
      "properties": {
        "level": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "description": "Battery charge as a fraction [0.0, 1.0]. Read from BatteryManager.EXTRA_LEVEL / EXTRA_SCALE."
        },
        "is_charging": {
          "type": "boolean",
          "description": "True if USB or AC power is connected."
        },
        "temperature_c": {
          "type": "number",
          "description": "Battery temperature in Celsius (BatteryManager.EXTRA_TEMPERATURE / 10). Optional; some devices don't report it.",
          "minimum": -40.0,
          "maximum": 100.0
        }
      }
    },
    "cpu": {
      "type": "object",
      "required": ["temperature_c"],
      "additionalProperties": false,
      "properties": {
        "temperature_c": {
          "type": "number",
          "minimum": -40.0,
          "maximum": 150.0,
          "description": "CPU thermal zone temperature in Celsius. Read from /sys/class/thermal/thermal_zone0/temp (divided by 1000)."
        },
        "load_percent": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 100.0,
          "description": "CPU utilization percentage. Optional; derived from /proc/stat deltas."
        }
      }
    },
    "memory": {
      "type": "object",
      "properties": {
        "available_mb": {
          "type": "integer",
          "minimum": 0,
          "description": "Current available RAM in MB."
        },
        "total_mb": {
          "type": "integer",
          "minimum": 0,
          "description": "Total device RAM in MB."
        }
      },
      "additionalProperties": false
    }
  }
}
```

### Heartbeat protocol

1. Android sends `TelemetryPayload` every **5 seconds** (configurable via kernel command).
2. If the kernel receives no heartbeat for **15 seconds**, the node is marked `STALE` in the roster.
3. After **30 seconds** of silence, the node is marked `DEAD` and removed from active task scheduling.
4. The kernel MAY reply with a `TelemetryAck` containing updated configuration (e.g., new heartbeat interval). This is a future extension; current nodes ignore unknown incoming message types.

---

## 3. `AudioChunkPayload`

Wrapper for real-time PCM audio streaming from Android → Kernel.
Transmitted as a **binary WebSocket frame** with a fixed-size JSON header prepended, followed by raw PCM bytes.

### Wire format

```
[ 4 bytes: header_length (uint32 LE) ][ header_length bytes: JSON header ][ remaining bytes: PCM data ]
```

### JSON header schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://ethos-kernel.dev/schemas/mesh/audio-chunk-v1.json",
  "title": "AudioChunkPayload (header)",
  "description": "Metadata header for a binary audio chunk. Precedes raw PCM bytes in the WebSocket binary frame.",
  "type": "object",
  "required": ["protocol_version", "type", "device_id", "seq", "sample_rate_hz", "channels", "bits_per_sample", "pcm_length_bytes"],
  "additionalProperties": false,
  "properties": {
    "protocol_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$"
    },
    "type": {
      "type": "string",
      "const": "audio_chunk",
      "description": "Discriminator for payload routing."
    },
    "device_id": {
      "type": "string",
      "minLength": 8,
      "maxLength": 64
    },
    "seq": {
      "type": "integer",
      "minimum": 0,
      "description": "Monotonically increasing sequence number per device session. Resets to 0 on reconnect. Kernel uses gaps to detect dropped chunks."
    },
    "sample_rate_hz": {
      "type": "integer",
      "enum": [8000, 16000, 44100, 48000],
      "description": "Audio sample rate. Default and recommended: 16000 (16kHz) for speech."
    },
    "channels": {
      "type": "integer",
      "enum": [1, 2],
      "description": "Number of audio channels. Default: 1 (mono)."
    },
    "bits_per_sample": {
      "type": "integer",
      "enum": [8, 16],
      "description": "Bit depth per sample. Default: 16 (PCM 16-bit signed LE)."
    },
    "pcm_length_bytes": {
      "type": "integer",
      "minimum": 1,
      "maximum": 65536,
      "description": "Exact byte count of the PCM payload following this header. Kernel MUST reject frames where actual remaining bytes != pcm_length_bytes."
    },
    "timestamp_ms": {
      "type": "integer",
      "minimum": 0,
      "description": "Capture timestamp (Unix epoch ms) of the first sample in this chunk."
    }
  }
}
```

### Audio streaming protocol

| Parameter | Default | Notes |
|-----------|---------|-------|
| Sample rate | 16,000 Hz | Speech-optimized. Whisper/VAD models expect 16kHz. |
| Bit depth | 16-bit signed LE | Standard `AudioRecord` PCM encoding. |
| Channels | 1 (mono) | Stereo is wasteful for speech; mono halves bandwidth. |
| Chunk duration | ~100ms | ≈ 3,200 bytes per chunk at 16kHz/16-bit/mono. Small enough for real-time, large enough to avoid frame overhead. |
| Max chunk size | 64 KB | Hard limit. Kernel drops frames exceeding this. |

### Decoding (Python kernel side)

```python
import struct, json

def decode_audio_frame(raw: bytes) -> tuple[dict, bytes]:
    """Decode a binary WebSocket frame into (header, pcm_bytes)."""
    header_len = struct.unpack_from("<I", raw, 0)[0]
    header = json.loads(raw[4 : 4 + header_len])
    pcm = raw[4 + header_len :]
    assert len(pcm) == header["pcm_length_bytes"], "PCM length mismatch"
    return header, pcm
```

---

## Payload type discriminator

All JSON payloads on the WebSocket MUST include a `type` field for routing:

| `type` value | Schema | Direction |
|-------------|--------|-----------|
| `"telemetry"` | `TelemetryPayload` | Android → Kernel |
| `"audio_chunk"` | `AudioChunkPayload` | Android → Kernel (binary frame) |
| `"discovery"` | `DiscoveryPayload` | mDNS TXT record (not WebSocket) |

The kernel's WebSocket handler dispatches on `type` first. Unknown types are logged and ignored (forward compatibility).

---

## Version history

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-26 | Initial contract. Discovery, Telemetry, AudioChunk schemas. |
