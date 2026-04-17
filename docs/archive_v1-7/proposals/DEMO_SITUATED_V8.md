# Demo: situated v8 + LAN (thin client)

**Purpose:** reproducible **field-style** demo: kernel on PC, phone browser on WiFi, **sensor hints** merged from env (fixture + preset) without raw hardware drivers.

**Ethical contract:** unchanged — MalAbs, buffer, Bayes; sensors only nudge sympathetic signals and JSON telemetry ([`PROPOSAL_SITUATED_ORGANISM_V8.md`](PROPOSAL_SITUATED_ORGANISM_V8.md)).

## One-command profile

Named bundle: **`situated_v8_lan_demo`** in [`src/runtime_profiles.py`](../../src/runtime_profiles.py).

| Env (set by profile) | Role |
|----------------------|------|
| `CHAT_HOST` / `CHAT_PORT` | Bind `0.0.0.0:8765` for LAN access |
| `KERNEL_SENSOR_FIXTURE` | `tests/fixtures/sensor/minimal_situ.json` (repo-relative) |
| `KERNEL_SENSOR_PRESET` | `low_battery` (merged after fixture; see `perceptual_abstraction.SENSOR_PRESETS`) |
| `KERNEL_CHAT_INCLUDE_VITALITY` / `…_MULTIMODAL` | Expose `vitality`, `multimodal_trust` in WebSocket JSON |

From repository root:

```powershell
# PowerShell example: set profile vars then start (adjust for your shell)
$env:CHAT_HOST="0.0.0.0"; $env:CHAT_PORT="8765"
$env:KERNEL_SENSOR_FIXTURE="tests/fixtures/sensor/minimal_situ.json"
$env:KERNEL_SENSOR_PRESET="low_battery"
python -m src.chat_server
```

Or import `apply_runtime_profile` in a small launcher script / pytest — for production use, duplicate the keys from `RUNTIME_PROFILES["situated_v8_lan_demo"]`.

## Client

On the phone: open `ws://<PC_LAN_IP>:8765/ws/chat` via [`landing/public/mobile.html`](../landing/public/mobile.html) or the flow in [`LOCAL_PC_AND_MOBILE_LAN.md`](LOCAL_PC_AND_MOBILE_LAN.md).

Optional: send a `sensor` object in the WebSocket JSON; server merges **fixture → preset → client** (last wins per key).

## Closing the roadmap slice

This profile closes the **demo** leg of **§3.1** in [`STRATEGY_AND_ROADMAP.md`](STRATEGY_AND_ROADMAP.md) (robustness → epistemology → demo) without implying raw multimodal pipelines are implemented.
