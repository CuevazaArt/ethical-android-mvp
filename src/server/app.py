import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from src.core.chat import ChatEngine
from src.core.memory import Memory
from src.core.stt import transcribe_pcm, is_available as stt_available
from src.core.vision import VisionEngine

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

app = FastAPI(title="Ethos Kernel Chat")

STATIC_DIR = Path(__file__).parent / "static"
NOMAD_DIR = Path(__file__).parent.parent / "clients" / "nomad_pwa"
_start_time = time.time()
_last_latency: dict | None = None  # V2.19: Store last latency globally


@app.get("/")
async def get_index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/nomad")
async def get_nomad():
    """Serve the Nomad PWA (mobile client)."""
    return FileResponse(NOMAD_DIR / "index.html")


@app.get("/nomad/{filename:path}")
async def get_nomad_static(filename: str):
    """Serve Nomad PWA static assets (app.js, style.css, manifest.json, sw.js, icon)."""
    target = NOMAD_DIR / filename
    if not target.exists() or not target.is_file():
        from fastapi.responses import Response
        return Response(status_code=404)
    return FileResponse(target)


@app.get("/api/status")
async def api_status():
    """Metrics snapshot for the dashboard."""
    import os as _os
    from src.core.identity import Identity
    mem = Memory()
    identity = Identity()
    uptime_s = int(time.time() - _start_time)
    h, rem = divmod(uptime_s, 3600)
    m, s = divmod(rem, 60)
    return JSONResponse({
        "model": _os.environ.get("OLLAMA_MODEL", "llama3.2:1b"),
        "ollama_url": _os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        "memory_episodes": len(mem),
        "memory_reflection": mem.reflection(),
        "identity_narrative": identity.narrative(),
        "identity_profile": identity.as_dict(),
        "uptime": f"{h:02d}:{m:02d}:{s:02d}",
        "status": "online",
        "stt_available": stt_available(),
        "last_latency_ms": _last_latency,
    })


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Minimal real-time telemetry dashboard."""
    return HTMLResponse("""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ethos — Dashboard</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d1117;color:#e6edf3;font-family:'Segoe UI',system-ui,sans-serif;padding:2rem}
h1{font-size:1.4rem;font-weight:700;margin-bottom:1.5rem;color:#58a6ff}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem;margin-bottom:1.5rem}
.card{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:1.1rem}
.card .label{font-size:0.72rem;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.4rem}
.card .value{font-size:1.6rem;font-weight:700;color:#3fb950}
.card .value.blue{color:#58a6ff}
.card .value.yellow{color:#d29922}
.reflection{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:1.1rem;font-size:.9rem;color:#8b949e;line-height:1.6}
.reflection .label{font-size:0.72rem;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.5rem}
.reflection .text{color:#e6edf3}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#3fb950;margin-right:.4rem;box-shadow:0 0 6px #3fb950}
footer{margin-top:1.5rem;font-size:.75rem;color:#484f58}
a{color:#58a6ff;text-decoration:none}
</style>
</head>
<body>
<h1><span class="dot"></span>Ethos Kernel — Dashboard</h1>
<div class="grid">
  <div class="card"><div class="label">Modelo LLM</div><div class="value blue" id="model">…</div></div>
  <div class="card"><div class="label">Episodios en memoria</div><div class="value" id="episodes">…</div></div>
  <div class="card"><div class="label">Uptime servidor</div><div class="value yellow" id="uptime">…</div></div>
  <div class="card"><div class="label">Estado</div><div class="value" id="status">…</div></div>
  <div class="card"><div class="label">Score ético</div><div class="value" id="eth-score">…</div></div>
  <div class="card"><div class="label">Tendencia</div><div class="value" id="eth-trend">…</div></div>
  <div class="card"><div class="label">Latencia (TTFT)</div><div class="value" id="latency-ttft">…</div></div>
</div>
<div class="reflection" style="margin-bottom:1rem">
  <div class="label">Narrativa de identidad</div>
  <div class="text" id="identity-narrative">…</div>
</div>
<div class="reflection">
  <div class="label">Reflexión de memoria</div>
  <div class="text" id="reflection">…</div>
</div>
<footer>Actualización automática cada 5s · <a href="/">↩ Chat</a></footer>
<script>
const TREND_LABEL = {mejorando:'📈 Mejorando', deteriorando:'📉 Deteriorando', estable:'⚖️ Estable'};
function scoreColor(v) {
  if (v === null || v === undefined) return '';
  return v > 0.65 ? 'color:#3fb950' : v > 0.35 ? 'color:#d29922' : 'color:#f85149';
}
async function refresh() {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();
    document.getElementById('model').textContent = d.model;
    document.getElementById('episodes').textContent = d.memory_episodes;
    document.getElementById('uptime').textContent = d.uptime;
    document.getElementById('status').textContent = d.status === 'online' ? '🟢 Online' : '🔴 Offline';
    document.getElementById('reflection').textContent = d.memory_reflection;
    const prof = d.identity_profile || {};
    const score = prof.avg_ethical_score ?? null;
    const scoreEl = document.getElementById('eth-score');
    scoreEl.textContent = score !== null ? score.toFixed(2) : '—';
    scoreEl.style.cssText = scoreColor(score);
    document.getElementById('eth-trend').textContent = TREND_LABEL[prof.trending] || '—';
    document.getElementById('identity-narrative').textContent = d.identity_narrative || '—';
    
    const lat = d.last_latency_ms;
    const latEl = document.getElementById('latency-ttft');
    if (lat && lat.ttft) {
      const ttft = lat.ttft;
      latEl.textContent = `${ttft.toFixed(0)}ms`;
      latEl.style.color = ttft < 800 ? '#3fb950' : ttft < 2000 ? '#d29922' : '#f85149';
      latEl.title = `Total: ${lat.total ? lat.total.toFixed(0) : 0}ms`;
    } else {
      latEl.textContent = '—';
      latEl.style.color = '';
    }
  } catch(e) {
    document.getElementById('status').textContent = '🔴 Error';
  }
}
refresh();
setInterval(refresh, 5000);
</script>
</body>
</html>""")


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    engine = ChatEngine()
    ready = await engine.start()
    _chat_vision: dict | None = None  # Fix 2: vision context from Nomad client

    if not ready:
        await websocket.send_json({
            "type": "done",
            "message": "Error: No se pudo conectar al LLM (Ollama).",
            "blocked": True,
            "reason": "LLM_UNAVAILABLE"
        })

    try:
        while True:
            data = await websocket.receive_text()
            try:
                # Try to parse as JSON for typed frames (vision_context, etc.)
                import json as _json
                try:
                    frame = _json.loads(data)
                    frame_type = frame.get("type", "") if isinstance(frame, dict) else ""
                except Exception:
                    frame = None
                    frame_type = ""

                if frame_type == "vision_context":
                    # Nomad client forwarding vision signals from /ws/nomad
                    _chat_vision = frame.get("payload")
                else:
                    # Plain text or other — treat as chat turn
                    text = data if not frame else (frame.get("text") or data)
                    async for event in engine.turn_stream(text, vision_context=_chat_vision):
                        await websocket.send_json(event)
                        if event.get("type") == "done" and not event.get("blocked"):
                            global _last_latency
                            lat = event.get("latency", {})
                            _last_latency = lat
                            _log.info(
                                "[TELEMETRY] Pipeline: Safety %.0fms | Perceive %.0fms | Ethics %.0fms | TTFT %.0fms | Total %.0fms",
                                lat.get("safety", 0), lat.get("perceive", 0),
                                lat.get("evaluate", 0), lat.get("ttft", 0), lat.get("total", 0),
                            )
            except Exception as e:
                _log.error("Error during turn: %s", e)
                await websocket.send_json({
                    "type": "done",
                    "message": "Error interno del kernel.",
                    "blocked": True,
                    "reason": str(e)
                })
    except WebSocketDisconnect:
        _log.info("Client disconnected")
    finally:
        await engine.close()


@app.websocket("/ws/nomad")
async def websocket_nomad(websocket: WebSocket):
    """
    Nomad sensory sideband — receives telemetry from mobile PWA.
    Handles: ping→pong, telemetry (battery/kinetics/orientation), chat_text relay.
    """
    await websocket.accept()
    _log.info("Nomad bridge connected")

    engine = ChatEngine()
    await engine.start()
    vision = VisionEngine()  # V2.12: stateful per-connection vision processor
    _last_vision: dict | None = None   # V2.13: last vision signals for context injection

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                import json as _json
                msg = _json.loads(raw)
                msg_type = msg.get("type", "")

                if msg_type == "ping":
                    await websocket.send_json({"type": "pong", "payload": {}})

                elif msg_type == "telemetry":
                    payload = msg.get("payload", {})
                    _log.debug("Nomad telemetry: %s", payload)

                elif msg_type == "chat_text":
                    text = (msg.get("payload") or {}).get("text", "")
                    if text:
                        async for event in engine.turn_stream(text, vision_context=_last_vision):
                            await websocket.send_json(event)
                            if event.get("type") == "done" and not event.get("blocked"):
                                global _last_latency
                                lat = event.get("latency", {})
                                _last_latency = lat
                                _log.info(
                                    "[TELEMETRY] Pipeline: Safety %.0fms | Perceive %.0fms | Ethics %.0fms | TTFT %.0fms | Total %.0fms",
                                    lat.get("safety", 0), lat.get("perceive", 0),
                                    lat.get("evaluate", 0), lat.get("ttft", 0), lat.get("total", 0),
                                )

                elif msg_type == "user_speech":
                    # V2.10: STT transcript from media_engine.js SpeechRecognition
                    text = msg.get("text", "").strip()
                    if text:
                        _log.info("Nomad STT -> kernel: %s", text[:80])
                        async for event in engine.turn_stream(text, vision_context=_last_vision):
                            await websocket.send_json(event)
                            if event.get("type") == "done" and not event.get("blocked"):
                                global _last_latency
                                lat = event.get("latency", {})
                                _last_latency = lat
                                _log.info(
                                    "[TELEMETRY] Pipeline: Safety %.0fms | Perceive %.0fms | Ethics %.0fms | TTFT %.0fms | Total %.0fms",
                                    lat.get("safety", 0), lat.get("perceive", 0),
                                    lat.get("evaluate", 0), lat.get("ttft", 0), lat.get("total", 0),
                                )

                elif msg_type == "vision_frame":
                    # V2.12+V2.13: process JPEG frame, cache signals for next turn
                    b64 = (msg.get("payload") or {}).get("image_b64", "")
                    if b64:
                        sig = vision.process_b64(b64)
                        if sig:
                            _last_vision = sig.to_dict()
                            await websocket.send_json({
                                "type": "vision_signals",
                                "payload": _last_vision,
                            })

                elif msg_type == "audio_pcm":
                    # V2.11: PCM audio from media_engine.js → Whisper STT → turn_stream()
                    if stt_available():
                        import base64
                        b64 = (msg.get("payload") or {}).get("audio_b64", "")
                        if b64:
                            try:
                                pcm_bytes = base64.b64decode(b64)
                                text = await transcribe_pcm(pcm_bytes)
                                if text:
                                    _log.info("Whisper STT: '%s'", text[:80])
                                    async for event in engine.turn_stream(text, vision_context=_last_vision):
                                        await websocket.send_json(event)
                                        if event.get("type") == "done" and not event.get("blocked"):
                                            global _last_latency
                                            lat = event.get("latency", {})
                                            _last_latency = lat
                                            _log.info(
                                                "[TELEMETRY] Pipeline: Safety %.0fms | Perceive %.0fms | Ethics %.0fms | TTFT %.0fms | Total %.0fms",
                                                lat.get("safety", 0), lat.get("perceive", 0),
                                                lat.get("evaluate", 0), lat.get("ttft", 0), lat.get("total", 0),
                                            )
                            except Exception as e:
                                _log.warning("audio_pcm transcription error: %s", e)
                    # If STT not available, client uses Web Speech API (already works)

                elif msg_type == "vad_event":
                    _log.debug("Nomad VAD: %s", msg.get("payload", {}).get("state"))

                else:
                    _log.debug("Nomad unknown frame: %s", msg_type)

            except Exception as e:
                _log.warning("Nomad frame error: %s", e)
    except WebSocketDisconnect:
        _log.info("Nomad bridge disconnected")
    finally:
        await engine.close()
