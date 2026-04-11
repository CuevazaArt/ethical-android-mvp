# Short-to-medium term objective: local PC + smartphone on the same network

This document sets the **objective**, the **architecture**, and the **concrete steps** to run the runtime on your PC and use the **smartphone as a client** on WiFi/LAN, respecting different resources (PC = core + optional LLM; mobile = lightweight interface).

**Nomadic framework (layers by hardware, sensors, network):** [NOMAD_PC_SMARTPHONE_BRIDGE.md](NOMAD_PC_SMARTPHONE_BRIDGE.md) — first PC↔smartphone bridge, sensory perception on mobile, testing on a more secure network when the operator indicates.

**Ethical contract:** does not change MalAbs or the buffer; only deployment and transport ([RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md)).

---

## Objective

| Timeframe | Goal |
|-----------|------|
| **Short term** | Same kernel and LLM on the PC; the smartphone **only sends/receives** JSON via WebSocket on LAN (without installing Python on the mobile). |
| **Medium term** | Narrative continuity when "jumping" sessions: **checkpoint** on disk on the PC + (future) **conduct guide** exportable for a small body ([`context_distillation.py`](../src/modules/context_distillation.py), [`conduct_guide.template.json`](templates/conduct_guide.template.json)). |

The **actual jump** to an 8B model **inside the phone** is a separate project (build Android, ONNX/TFLite, battery quotas). Here we enable the **thin client + common network** path, which already validates flow, UX, and persistence.

---

## Recommended architecture

```
┌────────────────────────────── PC (LAN) ──────────────────────────────┐
│  Ollama / other LLM (optional, localhost)                                │
│       ↑                                                                 │
│  python -m src.runtime   ← Ethos Kernel + WebSocket :8765               │
│  CHAT_HOST=0.0.0.0          (listens on all interfaces)                 │
│  KERNEL_CHECKPOINT_PATH=…   (optional: state between sessions)          │
└────────────────────────────┬───────────────────────────────────────────┘
                             │ WiFi / Ethernet (same subnet)
                             │  ws://<PC_IP>:8765/ws/chat
┌────────────────────────────▼───────────────────────────────────────────┐
│  Smartphone: browser → **`landing/public/mobile.html`** (minimal UI) or │
│  `chat-test.html` via `python -m http.server` · `?host=<PC_IP>` optional. │
└────────────────────────────────────────────────────────────────────────┘
```

- **PC:** more RAM/GPU → `LLM_MODE=ollama` (or another backend documented in README) if you want rich monologue.
- **Mobile:** does not run the kernel; **does not** need the same GB of model; only **stable network** to the PC.

---

## Steps on Windows (PowerShell)

1. **PC IP on the LAN** (example): `ipconfig` → WiFi adapter → IPv4 `192.168.x.x`.

2. **Firewall:** allow TCP inbound to the chat port (default `8765`) for **private network**:
   - *Settings → Firewall → Inbound rule* → port `8765`, or run once (admin):
   - `New-NetFirewallRule -DisplayName "Ethos Kernel Chat" -Direction Inbound -LocalPort 8765 -Protocol TCP -Action Allow -Profile Private`

3. **Start the server listening on LAN** (from repo root, with venv activated):

   ```powershell
   .\scripts\start_lan_server.ps1
   ```

   Equivalent to `CHAT_HOST=0.0.0.0` + `python -m src.runtime`. Optional: `.\scripts\start_lan_server.ps1 -Port 8765`.

4. **Test health** from mobile (browser): `http://<PC_IP>:8765/health` → `{"status":"ok"}`.

5. **Interface on mobile:** on the PC, in another terminal:

   ```powershell
   cd landing\public
   python -m http.server 8080 --bind 0.0.0.0
   ```

   On the **smartphone** (same WiFi), minimal interface: `http://<PC_IP>:8080/mobile.html` — IP/port, **Save** (local memory), **Test /health**, **Connect**, message, and **Send**. Optional query: `?host=<IP>&port=8765`.

   Technical alternative (raw JSON): `http://<PC_IP>:8080/chat-test.html?host=<PC_IP>`.

---

## Useful environment variables

| Variable | Role |
|----------|------|
| `CHAT_HOST` | `0.0.0.0` to accept LAN connections (not just loopback). |
| `CHAT_PORT` | Service port (default `8765`). |
| `KERNEL_API_DOCS` | By default **disabled**: `/docs` and `/openapi.json` are not exposed (less surface on LAN). `1` only if you need OpenAPI schema locally. |
| `LLM_MODE` / `USE_LOCAL_LLM` | Ollama on the PC ([README](README.md)). |
| `KERNEL_CHECKPOINT_PATH` | **PC** checkpoint JSON file for continuity between sessions. |
| `KERNEL_CONDUCT_GUIDE_EXPORT_PATH` | JSON file written **when closing** the WebSocket session (after checkpoint): guide for review or future small runtime (`conduct_guide_export.py`). Optional: `KERNEL_CONDUCT_GUIDE_EXPORT_ON_DISCONNECT=0` to disable. |
| `KERNEL_CONDUCT_GUIDE_PATH` | On a small edge device: **load** an exported guide (stub `context_distillation.py`). |
| `KERNEL_LIGHTHOUSE_KB_PATH` | Optional epistemic lighthouse ([PROPOSAL_REALITY_VERIFICATION_V11.md](PROPOSAL_REALITY_VERIFICATION_V11.md)). |

**Recommended flow (same directory):** for example `C:\EthicalData\kernel.json` + `C:\EthicalData\conduct_guide.json` — copy the pair to mobile only when you have a consumer; today the phone uses **only** WebSocket; the guide is mainly for traceability and preparation for the medium-term jump.

---

## Security (honest reading)

- **TLS-free** traffic on LAN: suitable only on a trusted home network.
- Do not expose `0.0.0.0` on **public WiFi** without a VPN or tunnel.
- Medium term: TLS terminated on a reverse proxy or tunnel (Cloudflare Tunnel, Tailscale, etc.).

---

## Medium term: "jump" with coherence

1. **Checkpoint** on the PC before closing session (`KERNEL_CHECKPOINT_SAVE_ON_DISCONNECT`).
2. **Template** [`conduct_guide.template.json`](templates/conduct_guide.template.json): when a distillation pipeline exists, the PC fills in simple rules for a future small runtime.
3. Native Android app: outside the scope of this repo; the WebSocket contract already defines the client protocol.

---

## Troubleshooting

| Symptom | What to check |
|---------|---------------|
| Mobile cannot connect to WebSocket | Same WiFi (not mobile data); correct IP; firewall; server with `CHAT_HOST=0.0.0.0`. |
| `health` does not load | Port blocked or wrong IP. |
| High latency | Heavy LLM on PC or congested WiFi; lower Ollama model or `KERNEL_CHAT_EXPOSE_MONOLOGUE=0`. |

---

*Ex Machina Foundation — local deployment and LAN; align changes with CHANGELOG.*
