# Short–medium goal: local PC + smartphone on the same network

This document states the **goal**, **architecture**, and **concrete steps** to run the runtime on your PC and use the **phone as a client** on Wi‑Fi/LAN, respecting different resources (PC = core + optional LLM; phone = lightweight UI).

**Nomadic frame (hardware classes, sensors, network):** [NOMAD_PC_SMARTPHONE_BRIDGE.md](NOMAD_PC_SMARTPHONE_BRIDGE.md) — first PC–smartphone bridge, sensor perception on the phone, testing on a safer network when the operator enables it.

**Ethical contract:** MalAbs and the buffer are unchanged; this is only deployment and transport ([RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md)).

---

## Goal

| Horizon | Target |
|---------|--------|
| **Short** | Same kernel and LLM on the PC; the smartphone **only sends/receives** JSON over WebSocket on LAN (no Python on the phone). |
| **Medium** | Narrative continuity when “jumping” sessions: **checkpoint** on disk on the PC + (future) exportable **conduct guide** for a small body ([`context_distillation.py`](../../src/modules/context_distillation.py), [`conduct_guide.template.json`](../templates/conduct_guide.template.json)). |

A **real** jump to an 8B model **inside the phone** is a separate project (Android build, ONNX/TFLite, battery budgets). Here we enable **thin client + shared network**, which already validates flow, UX, and persistence.

---

## Recommended architecture

```
+---------------------------------------------------------------------+
|  PC (LAN)                                                           |
|  Ollama / other LLM (optional, localhost)                           |
|       ^                                                             |
|  python -m src.runtime   <- Ethos Kernel + WebSocket :8765          |
|  CHAT_HOST=0.0.0.0 (listen on all interfaces)                       |
|  KERNEL_CHECKPOINT_PATH=... (optional: state across sessions)       |
+---------------------------+-----------------------------------------+
                            | WiFi / Ethernet (same subnet)
                            |  ws://<PC_IP>:8765/ws/chat
+---------------------------v-----------------------------------------+
|  Smartphone: browser -> landing/public/mobile.html (minimal UI) or  |
|  chat-test.html via python -m http.server ; optional ?host=<PC_IP>  |
+---------------------------------------------------------------------+
```

- **PC:** more RAM/GPU → `LLM_MODE=ollama` (or another documented backend) if you want richer monologue.
- **Phone:** does not run the kernel; **does not** need the same GB of model; only a **stable network** to the PC.

---

## Steps on Windows (PowerShell)

1. **PC LAN IP** (example): `ipconfig` → Wi‑Fi adapter → IPv4 `192.168.x.x`.

2. **Firewall:** allow inbound TCP on the chat port (default `8765`) for **private** network:
   - *Settings → Firewall → Inbound rule* → port `8765`, or once (admin):
   - `New-NetFirewallRule -DisplayName "Ethos Kernel Chat" -Direction Inbound -LocalPort 8765 -Protocol TCP -Action Allow -Profile Private`

3. **Start the server listening on LAN** (repo root, venv active):

   ```powershell
   .\scripts\start_lan_server.ps1
   ```

   Equivalent to `CHAT_HOST=0.0.0.0` + `python -m src.runtime`. Optional: `.\scripts\start_lan_server.ps1 -Port 8765`.

4. **Health check** from the phone (browser): `http://<PC_IP>:8765/health` → `{"status":"ok"}`.

5. **UI on the phone:** on the PC, in another terminal:

   ```powershell
   cd landing\public
   python -m http.server 8080 --bind 0.0.0.0
   ```

   On the **smartphone** (same Wi‑Fi), minimal UI: `http://<PC_IP>:8080/mobile.html` — IP/port, **Save** (local storage), **Test /health**, **Connect**, message and **Send**. Optional query: `?host=<IP>&port=8765`.

   Technical alternative (raw JSON): `http://<PC_IP>:8080/chat-test.html?host=<PC_IP>`.

---

## Useful environment variables

| Variable | Role |
|----------|------|
| `CHAT_HOST` | `0.0.0.0` to accept LAN connections (not loopback only). |
| `CHAT_PORT` | Service port (default `8765`). |
| `KERNEL_API_DOCS` | **Off** by default: no `/docs` or `/openapi.json` (smaller surface on LAN). `1` only if you need local OpenAPI. |
| `LLM_MODE` / `USE_LOCAL_LLM` | Ollama on the PC ([README](../../README.md)). |
| `KERNEL_CHECKPOINT_PATH` | JSON checkpoint file **on the PC** for continuity across sessions. |
| `KERNEL_CONDUCT_GUIDE_EXPORT_PATH` | JSON file written **on WebSocket disconnect** (after checkpoint): guide for review or future small runtime (`conduct_guide_export.py`). Optional: `KERNEL_CONDUCT_GUIDE_EXPORT_ON_DISCONNECT=0` to disable. |
| `KERNEL_CONDUCT_GUIDE_PATH` | On a small edge device: **load** an exported guide (stub `context_distillation.py`). |
| `KERNEL_LIGHTHOUSE_KB_PATH` | Optional epistemic lighthouse ([PROPOSAL_REALITY_VERIFICATION_V11.md](PROPOSAL_REALITY_VERIFICATION_V11.md)). |

**Recommended flow (same directory):** e.g. `C:\EthicalData\kernel.json` + `C:\EthicalData\conduct_guide.json` — copy the pair to the phone only when you have a consumer; today the phone uses **WebSocket only**; the guide is mainly traceability and preparation for the medium-term handoff.

---

## Security (honest read)

- **No TLS** on LAN: appropriate only on a trusted home network.
- Do not expose `0.0.0.0` on **public Wi‑Fi** without VPN or tunnel.
- Medium term: TLS at a reverse proxy or tunnel (Cloudflare Tunnel, Tailscale, etc.).

---

## Medium term: coherent “jump”

1. **Checkpoint** on the PC before closing the session (`KERNEL_CHECKPOINT_SAVE_ON_DISCONNECT`).
2. **Template** [`conduct_guide.template.json`](../templates/conduct_guide.template.json): when a distillation pipeline exists, the PC fills simple rules for a future small runtime.
3. Native Android app: out of scope for this repo; the WebSocket contract already defines the client protocol.

---

## Troubleshooting

| Symptom | What to check |
|---------|----------------|
| Phone cannot connect WebSocket | Same Wi‑Fi (not cellular data); correct IP; firewall; server with `CHAT_HOST=0.0.0.0`. |
| `health` does not load | Blocked port or wrong IP. |
| High latency | Heavy LLM on PC or congested Wi‑Fi; smaller Ollama model or `KERNEL_CHAT_EXPOSE_MONOLOGUE=0`. |

---

*Ex Machina Foundation — local and LAN deployment; align substantive changes with CHANGELOG.*
