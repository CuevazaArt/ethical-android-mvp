import logging
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from src.core.chat import ChatEngine

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

app = FastAPI(title="Ethos Kernel Chat")

STATIC_DIR = Path(__file__).parent / "static"

@app.get("/")
async def get_index():
    return FileResponse(STATIC_DIR / "index.html")

@app.websocket("/ws/stream")
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
