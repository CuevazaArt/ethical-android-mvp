# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

import asyncio
import base64
import logging
import math
import time
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from src.core.chat import ChatEngine
from src.core.memory import Memory
from src.core.perception import SensoryBuffer
from src.core.sleep import PsiSleepDaemon
from src.core.stt import is_available as stt_available
from src.core.stt import transcribe_pcm
from src.core.tts import synthesize
from src.core.vision import VisionEngine
from src.server.desktop_audio_adapter import (
    ContractError,
    build_error_envelope,
    build_success_envelope,
    parse_audio_perception_payload,
    safe_latency_ms,
)
from src.server.mesh_server import router as mesh_router

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)


async def _safe_send(ws: WebSocket, data: dict) -> bool:
    """Send JSON to WebSocket, returning False if client disconnected."""
    try:
        await ws.send_json(data)
        return True
    except (WebSocketDisconnect, RuntimeError):
        return False


async def _safe_send_tts(ws: WebSocket, event: dict, metadata: dict | None = None):
    msg = event.get("message", "")
    if msg:
        import base64

        pitch = "+0Hz"
        rate = "+0%"
        if metadata:
            risk = metadata.get("risk", 0.0)
            urgency = metadata.get("urgency", 0.0)
            if risk > 0.5:
                pitch = "-15Hz"
                rate = "-10%"
            elif urgency > 0.5:
                rate = "+15%"

        audio_bytes = await synthesize(msg, pitch=pitch, rate=rate)
        if audio_bytes:
            b64 = base64.b64encode(audio_bytes).decode("utf-8")
            await _safe_send(ws, {"type": "tts_audio", "audio_b64": b64, "text": msg})
        else:
            await _safe_send(ws, {"type": "tts_audio", "audio_b64": None, "text": msg})


app = FastAPI(title="Ethos Kernel Chat")
app.include_router(mesh_router)

STATIC_DIR = Path(__file__).parent / "static"
NOMAD_DIR = (
    Path(__file__).parent.parent / "clients" / "archive_nomad_pwa"
)  # V2.77: Archived
_start_time = time.time()
_last_latency: dict | None = None  # V2.19: Store last latency globally
_sleep_daemon = PsiSleepDaemon(idle_threshold_seconds=120)  # V2.76: Psi-Sleep


@app.on_event("startup")
async def startup_event():
    await _sleep_daemon.start()


@app.on_event("shutdown")
async def shutdown_event():
    await _sleep_daemon.stop()


@app.get("/")
async def get_index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/ping")
async def api_ping():
    """Lightweight health check for Android connectivity verification."""
    return JSONResponse({"pong": True, "uptime_s": int(time.time() - _start_time)})


@app.post("/api/perception/audio")
async def api_audio_perception(request: Request):
    """
    Desktop audio perception contract (Block 50.2).
    Expects v1 envelope and returns transcript + latency telemetry.
    """
    t0 = time.perf_counter()
    try:
        payload = await request.json()
    except Exception:
        latency_ms = safe_latency_ms(t0)
        envelope = build_error_envelope(
            request_payload={},
            error=ContractError(
                code="INVALID_JSON",
                message="Request body must be valid JSON.",
                retryable=False,
            ),
            latency_ms=latency_ms,
        )
        return JSONResponse(envelope, status_code=400)

    parsed, parse_error = parse_audio_perception_payload(payload)
    if parse_error:
        latency_ms = safe_latency_ms(t0)
        request_payload = payload.get("request", {}) if isinstance(payload, dict) else {}
        envelope = build_error_envelope(
            request_payload=request_payload if isinstance(request_payload, dict) else {},
            error=parse_error,
            latency_ms=latency_ms,
        )
        return JSONResponse(envelope, status_code=400)

    assert parsed is not None
    try:
        pcm_bytes = base64.b64decode(parsed.audio_b64, validate=True)
    except Exception:
        latency_ms = safe_latency_ms(t0)
        envelope = build_error_envelope(
            request_payload=parsed.request_payload,
            error=ContractError(
                code="INVALID_AUDIO_B64",
                message="'audio_b64' is not valid base64.",
                retryable=False,
            ),
            latency_ms=latency_ms,
        )
        return JSONResponse(envelope, status_code=400)

    if not pcm_bytes:
        latency_ms = safe_latency_ms(t0)
        envelope = build_error_envelope(
            request_payload=parsed.request_payload,
            error=ContractError(
                code="AUDIO_DEVICE_UNAVAILABLE",
                message="No audio bytes received. Microphone may be unavailable.",
                retryable=True,
            ),
            latency_ms=latency_ms,
        )
        return JSONResponse(envelope, status_code=400)

    transcript = await transcribe_pcm(
        pcm_bytes,
        sample_rate=parsed.sample_rate_hz,
    )
    latency_ms = safe_latency_ms(t0)

    if transcript is None:
        envelope = build_error_envelope(
            request_payload=parsed.request_payload,
            error=ContractError(
                code="STT_UNAVAILABLE",
                message="Audio received but transcription is unavailable on this node.",
                retryable=True,
            ),
            latency_ms=latency_ms,
        )
        _log.info(
            "[AUDIO_PERCEPTION] fallback | sample_rate=%sHz | bytes=%s | latency_ms=%.2f",
            parsed.sample_rate_hz,
            len(pcm_bytes),
            latency_ms,
        )
        return JSONResponse(envelope, status_code=200)

    confidence = 0.85 if transcript.strip() else 0.0
    if not math.isfinite(confidence):
        confidence = 0.0
    envelope = build_success_envelope(
        request_payload=parsed.request_payload,
        transcript=transcript.strip(),
        confidence=confidence,
        latency_ms=latency_ms,
    )
    _log.info(
        "[AUDIO_PERCEPTION] ok | sample_rate=%sHz | bytes=%s | latency_ms=%.2f",
        parsed.sample_rate_hz,
        len(pcm_bytes),
        latency_ms,
    )
    return JSONResponse(envelope, status_code=200)


@app.get("/nomad/")
async def get_nomad():
    """Serve the Archived Nomad PWA (mobile client)."""
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
    from src.core.user_model import UserModelTracker

    mem = Memory()
    identity = Identity()
    user_mod = UserModelTracker()
    uptime_s = int(time.time() - _start_time)
    h, rem = divmod(uptime_s, 3600)
    m, s = divmod(rem, 60)
    return JSONResponse(
        {
            "model": _os.environ.get("OLLAMA_MODEL", "gemma3"),
            "ollama_url": _os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            "memory_episodes": len(mem),
            "memory_reflection": mem.reflection(),
            "identity_narrative": identity.narrative(),
            "identity_profile": identity.as_dict(),
            "identity_archetype": identity._archetype,
            "user_risk": user_mod.risk_band.value,
            "user_pattern": user_mod.cognitive_pattern.value,
            "uptime": f"{h:02d}:{m:02d}:{s:02d}",
            "status": "online",
            "stt_available": stt_available(),
            "last_latency_ms": _last_latency,
        }
    )


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
  <div class="card"><div class="label">Riesgo Usuario</div><div class="value" id="user-risk">…</div></div>
  <div class="card"><div class="label">Sesgo Detectado</div><div class="value" id="user-pattern">…</div></div>
  <div class="card"><div class="label">Latencia Total</div><div class="value" id="latency-total">…</div></div>
</div>
<div class="grid" style="grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); margin-bottom: 1.5rem;">
  <div class="card"><div class="label">Percepción</div><div class="value" style="font-size:1.2rem; color:#8b949e" id="lat-perceive">…</div></div>
  <div class="card"><div class="label">Ética (CBR)</div><div class="value" style="font-size:1.2rem; color:#8b949e" id="lat-ethics">…</div></div>
  <div class="card"><div class="label">TTFT (Tokens)</div><div class="value" style="font-size:1.2rem; color:#8b949e" id="latency-ttft">…</div></div>
</div>
<div class="reflection" style="margin-bottom:1rem">
  <div class="label">Arquetipo Central</div>
  <div class="text" id="identity-archetype">…</div>
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
    document.getElementById('identity-archetype').textContent = d.identity_archetype || 'En formación...';
    
    // User Model
    const riskEl = document.getElementById('user-risk');
    riskEl.textContent = d.user_risk.toUpperCase();
    riskEl.style.color = d.user_risk === 'high' ? '#f85149' : d.user_risk === 'medium' ? '#d29922' : '#3fb950';
    
    document.getElementById('user-pattern').textContent = d.user_pattern === 'none' ? 'Ninguno' : d.user_pattern.replace('_', ' ');
    
    const lat = d.last_latency_ms;
    const latEl = document.getElementById('latency-ttft');
    const latTotalEl = document.getElementById('latency-total');
    if (lat) {
      if (lat.ttft) latEl.textContent = `${lat.ttft.toFixed(0)}ms`;
      if (lat.perceive) document.getElementById('lat-perceive').textContent = `${lat.perceive.toFixed(0)}ms`;
      if (lat.evaluate) document.getElementById('lat-ethics').textContent = `${lat.evaluate.toFixed(0)}ms`;
      
      if (lat.total) {
        latTotalEl.textContent = `${lat.total.toFixed(0)}ms`;
        latTotalEl.style.color = lat.total < 1500 ? '#3fb950' : lat.total < 4000 ? '#d29922' : '#f85149';
      }
    } else {
      latEl.textContent = '—';
      latTotalEl.textContent = '—';
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
    global _last_latency
    engine = ChatEngine()
    ready = await engine.start()
    _chat_vision: dict | None = None  # Fix 2: vision context from Nomad client

    if not ready:
        await websocket.send_json(
            {
                "type": "done",
                "message": "Error: No se pudo conectar al LLM (Ollama).",
                "blocked": True,
                "reason": "LLM_UNAVAILABLE",
            }
        )

    try:
        while True:
            data = await websocket.receive_text()
            _sleep_daemon.note_activity()  # V2.76: Wake up / reset sleep timer
            try:
                # Try to parse as JSON for typed frames (vision_context, etc.)
                import json as _json

                try:
                    frame = _json.loads(data)
                    frame_type = (
                        frame.get("type", "") if isinstance(frame, dict) else ""
                    )
                except Exception:
                    frame = None
                    frame_type = ""

                if frame_type == "vision_context":
                    # Nomad client forwarding vision signals from /ws/nomad
                    _chat_vision = frame.get("payload")
                elif frame_type == "chat_text":
                    # Explicit chat message from Nomad client
                    text = (
                        (frame.get("payload") or frame).get("text", "").strip()
                        if isinstance(frame, dict)
                        else ""
                    )
                    if text:
                        _log.info("[wsChat] User text: %s", text[:80])
                        await _run_turn_and_send(
                            engine,
                            websocket,
                            text,
                            _chat_vision,
                            label="Pipeline",
                        )
                elif frame_type == "vault_auth":
                    # Phase 19: Vault Authorization callback
                    key = frame.get("key")
                    approved = frame.get("approved")
                    if approved and key:
                        engine.vault.unlock("biometric_dummy")
                        secret = engine.vault.get_secret(
                            key, reason="User approved via UI"
                        )
                        engine.vault.lock()
                        if secret:
                            injection = f"[SISTEMA - ALTA PRIORIDAD]: Acceso concedido a la Bóveda. El valor de '{key}' es: {secret}. Procede a ayudar al usuario con esta información de forma natural."
                        else:
                            injection = f"[SISTEMA]: Acceso concedido, pero la bóveda indica que la llave '{key}' está vacía o no existe. Informa al usuario."

                        _log.info("[VAULT] Injecting secret for %s", key)
                        await _run_turn_and_send(
                            engine, websocket, injection, _chat_vision, label="Vault"
                        )
                elif frame_type:
                    _log.debug("wsChat ignoring typed frame: %s", frame_type)
                elif frame and isinstance(frame, dict) and frame.get("text"):
                    # Legacy { text: "..." } format — also treat as chat
                    text = frame["text"].strip()
                    if text:
                        _log.info("[wsChat] Legacy text: %s", text[:80])
                        await _run_turn_and_send(
                            engine,
                            websocket,
                            text,
                            _chat_vision,
                            label="Pipeline",
                        )
                elif not frame:
                    # Plain string — user typed directly
                    text = data.strip()
                    if text:
                        _log.info("[wsChat] Plain text: %s", text[:80])
                        await _run_turn_and_send(
                            engine,
                            websocket,
                            text,
                            _chat_vision,
                            label="Pipeline",
                        )
                else:
                    _log.debug("wsChat ignoring unknown frame: %s", str(data)[:100])
            except Exception as e:
                _log.error("Error during turn: %s", e)
                await _safe_send(
                    websocket,
                    {
                        "type": "done",
                        "message": "Error interno del kernel.",
                        "blocked": True,
                        "reason": str(e),
                    },
                )
    except WebSocketDisconnect:
        _log.info("Client disconnected")
    finally:
        await engine.close()


async def _run_turn_and_send(
    engine: ChatEngine,
    ws: WebSocket,
    text: str,
    vision_context: dict | None,
    label: str = "Pipeline",
    skip_tts: bool = False,
) -> None:
    """Shared helper: run turn_stream, send events, log telemetry, optionally send TTS."""
    global _last_latency
    _current_metadata: dict | None = None
    async for event in engine.turn_stream(text, vision_context=vision_context):
        if skip_tts:
            event["autonomous"] = True  # V2.60: mark so client suppresses audio
        if not await _safe_send(ws, event):
            return
        if event.get("type") == "metadata":
            _current_metadata = event.get("signals")
        if event.get("type") == "done" and not event.get("blocked"):
            lat = event.get("latency", {})
            _last_latency = lat
            _log.info(
                "[TELEMETRY] %s: Safety %.0fms | Perceive %.0fms | Ethics %.0fms | TTFT %.0fms | Total %.0fms",
                label,
                lat.get("safety", 0),
                lat.get("perceive", 0),
                lat.get("evaluate", 0),
                lat.get("ttft", 0),
                lat.get("total", 0),
            )
            if not skip_tts:
                await _safe_send_tts(ws, event, _current_metadata)


@app.websocket("/ws/nomad")
async def websocket_nomad(websocket: WebSocket):
    """
    Nomad sensory sideband — receives telemetry from mobile PWA.
    V2.57: Uses SensoryBuffer for temporal multimodal fusion.
    Audio and vision events are buffered in a 2s window and fused
    into a single semantic frame before reaching the LLM.
    """
    await websocket.accept()
    _log.info("Nomad bridge connected")

    global _last_latency
    engine = ChatEngine()
    await engine.start()
    vision = VisionEngine()
    sensory_buffer = SensoryBuffer(window_seconds=2.0)
    _last_vision: dict | None = None
    _last_autonomous_turn: float = 0.0
    _last_user_interaction: float = (
        0.0  # V2.60: suppress autonomous during conversation
    )
    _consolidation_running = True

    async def _consolidation_loop() -> None:
        """V2.60: Background loop — silent visual pulse only, no LLM, no TTS."""
        nonlocal _last_vision, _last_user_interaction
        while _consolidation_running:
            await asyncio.sleep(2.5)
            # Suppress during active conversation (60s cooldown)
            if (time.time() - _last_user_interaction) < 60.0:
                sensory_buffer.get_fused_context(flush=True)
                continue
            if sensory_buffer.has_audio:
                continue
            fused = sensory_buffer.get_fused_context(flush=True)
            if fused:
                _log.info("[FUSION/AUTO] %s", fused[:120])
                # V2.60: Only send a lightweight pulse — NO LLM, NO TTS
                await _safe_send(
                    websocket,
                    {
                        "type": "autonomous_pulse",
                        "description": fused[:200],
                    },
                )

    consolidation_task = asyncio.create_task(_consolidation_loop())

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
                    _log.debug("Nomad telemetry: %s", msg.get("payload", {}))

                elif msg_type == "chat_text":
                    # Explicit typed chat: bypass buffer entirely
                    text = (msg.get("payload") or {}).get("text", "")
                    if text:
                        _last_user_interaction = time.time()
                        await _run_turn_and_send(
                            engine,
                            websocket,
                            text,
                            _last_vision,
                            label="Pipeline",
                        )

                elif msg_type == "user_speech":
                    # V2.60: Immediate flush — fuse with concurrent vision, zero delay
                    text = msg.get("text", "").strip()
                    if text:
                        _last_user_interaction = time.time()
                        fused = sensory_buffer.add_and_flush("audio", text)
                        if fused:
                            _log.info("[FUSION/SPEECH] %s", fused[:120])
                            await _run_turn_and_send(
                                engine,
                                websocket,
                                fused,
                                _last_vision,
                                label="Fusion",
                            )

                elif msg_type == "vision_frame":
                    b64 = (msg.get("payload") or {}).get("image_b64", "")
                    if b64:
                        sig = vision.process_b64(b64)
                        if sig:
                            _last_vision = sig.to_dict()
                            await _safe_send(
                                websocket,
                                {
                                    "type": "vision_signals",
                                    "payload": _last_vision,
                                },
                            )

                            # Buffer vision triggers for potential fusion with speech
                            now = time.time()
                            if (
                                now - _last_autonomous_turn
                            ) > 120.0:  # V2.60: 120s cooldown
                                if sig.face_present or sig.motion > 0.05:
                                    _last_autonomous_turn = now
                                    _log.info(
                                        "Vision trigger -> buffer: Face=%s Motion=%.3f",
                                        sig.face_present,
                                        sig.motion,
                                    )
                                    desc = (
                                        "una persona presente"
                                        if sig.face_present
                                        else f"movimiento detectado (intensidad {sig.motion:.2f})"
                                    )
                                    sensory_buffer.add_event("vision", desc)

                elif msg_type == "audio_pcm":
                    # V2.58: Whisper transcription → immediate flush with fusion
                    if stt_available():
                        import base64

                        b64 = (msg.get("payload") or {}).get("audio_b64", "")
                        if b64:
                            try:
                                pcm_bytes = base64.b64decode(b64)
                                text = await transcribe_pcm(pcm_bytes)
                                if text:
                                    fused = sensory_buffer.add_and_flush("audio", text)
                                    if fused:
                                        _log.info("[FUSION/WHISPER] %s", fused[:120])
                                        await _run_turn_and_send(
                                            engine,
                                            websocket,
                                            fused,
                                            _last_vision,
                                            label="Fusion",
                                        )
                            except Exception as e:
                                _log.warning("audio_pcm transcription error: %s", e)

                elif msg_type == "vad_event":
                    _log.debug("Nomad VAD: %s", msg.get("payload", {}).get("state"))

                else:
                    _log.debug("Nomad unknown frame: %s", msg_type)

            except Exception as e:
                _log.warning("Nomad frame error: %s", e)
    except WebSocketDisconnect:
        _log.info("Nomad bridge disconnected")
    finally:
        _consolidation_running = False
        consolidation_task.cancel()
        try:
            await consolidation_task
        except asyncio.CancelledError:
            pass
        await engine.close()
