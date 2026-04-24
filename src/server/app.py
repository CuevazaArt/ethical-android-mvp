import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from src.core.chat import ChatEngine
from src.core.memory import Memory

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

app = FastAPI(title="Ethos Kernel Chat")

STATIC_DIR = Path(__file__).parent / "static"
_start_time = time.time()


@app.get("/")
async def get_index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/status")
async def api_status():
    """Metrics snapshot for the dashboard."""
    mem = Memory()
    uptime_s = int(time.time() - _start_time)
    h, rem = divmod(uptime_s, 3600)
    m, s = divmod(rem, 60)
    return JSONResponse({
        "model": os.environ.get("OLLAMA_MODEL", "llama3.2:1b"),
        "ollama_url": os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        "memory_episodes": len(mem),
        "memory_reflection": mem.reflection(),
        "uptime": f"{h:02d}:{m:02d}:{s:02d}",
        "status": "online",
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
</div>
<div class="reflection">
  <div class="label">Reflexión de identidad</div>
  <div class="text" id="reflection">…</div>
</div>
<footer>Actualización automática cada 5s · <a href="/">↩ Chat</a></footer>
<script>
async function refresh() {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();
    document.getElementById('model').textContent = d.model;
    document.getElementById('episodes').textContent = d.memory_episodes;
    document.getElementById('uptime').textContent = d.uptime;
    document.getElementById('status').textContent = d.status === 'online' ? '🟢 Online' : '🔴 Offline';
    document.getElementById('reflection').textContent = d.memory_reflection;
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
                async for event in engine.turn_stream(data):
                    await websocket.send_json(event)
            except Exception as e:
                _log.error(f"Error during turn: {e}")
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
