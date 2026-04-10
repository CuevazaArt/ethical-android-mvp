# Objetivo corto–mediano: PC local + smartphone en la misma red

Este documento fija el **objetivo**, la **arquitectura** y los **pasos concretos** para ejecutar el runtime en tu PC y usar el **teléfono como cliente** en WiFi/LAN, respetando recursos distintos (PC = núcleo + LLM opcional; móvil = interfaz liviana).

**Marco nomada (capas por hardware, sensores, red):** [NOMAD_PC_SMARTPHONE_BRIDGE.md](NOMAD_PC_SMARTPHONE_BRIDGE.md) — primer puente PC↔smartphone, percepción sensorial en el móvil, testeo en red más segura cuando el operador lo indique.

**Contrato ético:** no cambia MalAbs ni el buffer; solo despliegue y transporte ([RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md)).

---

## Objetivo

| Plazo | Meta |
|-------|------|
| **Corto** | Mismo kernel y LLM en el PC; el smartphone **solo envía/recibe** JSON por WebSocket en LAN (sin instalar Python en el móvil). |
| **Mediano** | Continuidad narrativa al “saltar” de sesión: **checkpoint** en disco en el PC + (futuro) **guía de conducta** exportable para un cuerpo pequeño ([`context_distillation.py`](../src/modules/context_distillation.py), [`conduct_guide.template.json`](templates/conduct_guide.template.json)). |

El **salto real** a un modelo 8B **dentro del teléfono** es un proyecto aparte (build Android, ONNX/TFLite, cuotas de batería). Aquí habilitamos el camino **thin client + red común**, que ya valida flujo, UX y persistencia.

---

## Arquitectura recomendada

```
┌────────────────────────────── PC (LAN) ──────────────────────────────┐
│  Ollama / otro LLM (opcional, localhost)                                │
│       ↑                                                                 │
│  python -m src.runtime   ← EthicalKernel + WebSocket :8765           │
│  CHAT_HOST=0.0.0.0          (escucha en todas las interfaces)           │
│  KERNEL_CHECKPOINT_PATH=…   (opcional: estado entre sesiones)          │
└────────────────────────────┬───────────────────────────────────────────┘
                             │ WiFi / Ethernet (misma subred)
                             │  ws://<IP_DEL_PC>:8765/ws/chat
┌────────────────────────────▼───────────────────────────────────────────┐
│  Smartphone: navegador → **`landing/public/mobile.html`** (UI mínima) o │
│  `chat-test.html` vía `python -m http.server` · `?host=<IP_PC>` opcional. │
└────────────────────────────────────────────────────────────────────────┘
```

- **PC:** más RAM/GPU → `LLM_MODE=ollama` (u otro backend documentado en README) si quieres monólogo rico.
- **Móvil:** no ejecuta el kernel; **no** necesita los mismos GB de modelo; solo **red estable** hacia el PC.

---

## Pasos en Windows (PowerShell)

1. **IP del PC en la LAN** (ejemplo): `ipconfig` → adaptador WiFi → IPv4 `192.168.x.x`.

2. **Firewall:** permitir entrada TCP al puerto del chat (por defecto `8765`) para **red privada**:
   - *Configuración → Firewall → Regla de entrada* → puerto `8765`, o ejecutar una vez (admin):
   - `New-NetFirewallRule -DisplayName "Ethos Kernel Chat" -Direction Inbound -LocalPort 8765 -Protocol TCP -Action Allow -Profile Private`

3. **Arrancar el servidor escuchando en LAN** (desde la raíz del repo, con venv activado):

   ```powershell
   .\scripts\start_lan_server.ps1
   ```

   Equivale a `CHAT_HOST=0.0.0.0` + `python -m src.runtime`. Opcional: `.\scripts\start_lan_server.ps1 -Port 8765`.

4. **Probar salud** desde el móvil (navegador): `http://<IP_PC>:8765/health` → `{"status":"ok"}`.

5. **Interfaz en el móvil:** en el PC, en otra terminal:

   ```powershell
   cd landing\public
   python -m http.server 8080 --bind 0.0.0.0
   ```

   En el **smartphone** (misma WiFi), interfaz mínima: `http://<IP_DEL_PC>:8080/mobile.html` — IP/puerto, **Guardar** (memoria local), **Probar /health**, **Conectar**, mensaje y **Enviar**. Query opcional: `?host=<IP>&port=8765`.

   Alternativa técnica (JSON crudo): `http://<IP_PC>:8080/chat-test.html?host=<IP_PC>`.

---

## Variables de entorno útiles

| Variable | Rol |
|----------|-----|
| `CHAT_HOST` | `0.0.0.0` para aceptar conexiones LAN (no solo loopback). |
| `CHAT_PORT` | Puerto del servicio (default `8765`). |
| `LLM_MODE` / `USE_LOCAL_LLM` | Ollama en el PC ([README](../README.md)). |
| `KERNEL_CHECKPOINT_PATH` | Archivo JSON de checkpoint **en el PC** para continuidad entre sesiones. |
| `KERNEL_CONDUCT_GUIDE_EXPORT_PATH` | Archivo JSON escrito **al cerrar** la sesión WebSocket (después del checkpoint): guía para revisión o futuro runtime pequeño (`conduct_guide_export.py`). Opcional: `KERNEL_CONDUCT_GUIDE_EXPORT_ON_DISCONNECT=0` para desactivar. |
| `KERNEL_CONDUCT_GUIDE_PATH` | En un edge/dispositivo pequeño: **cargar** una guía exportada (stub `context_distillation.py`). |
| `KERNEL_LIGHTHOUSE_KB_PATH` | Faro epistémico opcional ([PROPUESTA_VERIFICACION_REALIDAD_V11.md](discusion/PROPUESTA_VERIFICACION_REALIDAD_V11.md)). |

**Flujo recomendado (mismo directorio):** por ejemplo `C:\EthicalData\kernel.json` + `C:\EthicalData\conduct_guide.json` — copia el par al móvil solo cuando tengas un consumidor; hoy el teléfono usa **solo** WebSocket; la guía es sobre todo trazabilidad y preparación del salto mediano.

---

## Seguridad (lectura honesta)

- Tráfico **sin TLS** en LAN: adecuado solo en red doméstica de confianza.
- No expongas `0.0.0.0` en **WiFi pública** sin VPN o túnel.
- Mediano plazo: TLS terminado en proxy inverso o túnel (Cloudflare Tunnel, Tailscale, etc.).

---

## Mediano plazo: “salto” con coherencia

1. **Checkpoint** en el PC antes de cerrar sesión (`KERNEL_CHECKPOINT_SAVE_ON_DISCONNECT`).
2. **Plantilla** [`conduct_guide.template.json`](templates/conduct_guide.template.json): cuando exista pipeline de destilación, el PC rellena reglas simples para un futuro runtime pequeño.
3. App nativa Android: fuera del alcance de este repo; el contrato WebSocket ya define el protocolo cliente.

---

## Resolución de problemas

| Síntoma | Qué revisar |
|---------|-------------|
| El móvil no conecta al WebSocket | Mismo WiFi (no datos móviles); IP correcta; firewall; servidor con `CHAT_HOST=0.0.0.0`. |
| `health` no carga | Puerto bloqueado o IP equivocada. |
| Latencia alta | LLM pesado en PC o WiFi congestionada; bajar modelo Ollama o `KERNEL_CHAT_EXPOSE_MONOLOGUE=0`. |

---

*Ex Machina Foundation — despliegue local y LAN; alinear cambios con CHANGELOG.*
