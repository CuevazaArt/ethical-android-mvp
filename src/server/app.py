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

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    engine = ChatEngine()
    ready = await engine.start()
    
    if not ready:
        await websocket.send_json({
            "message": "Error: No se pudo conectar al LLM (Ollama).", 
            "blocked": True, 
            "reason": "LLM_UNAVAILABLE"
        })
        
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                result = await engine.turn(data)
                
                is_blocked = result.perception_raw.get("blocked", False)
                reason = result.perception_raw.get("reason", "")
                
                response_payload = {
                    "message": result.message,
                    "context": result.signals.context,
                    "blocked": is_blocked,
                }
                if is_blocked:
                    response_payload["reason"] = reason
                
                await websocket.send_json(response_payload)
            except Exception as e:
                _log.error(f"Error during turn: {e}")
                await websocket.send_json({
                    "message": "Error interno del kernel.", 
                    "blocked": True, 
                    "reason": str(e)
                })
    except WebSocketDisconnect:
        _log.info("Client disconnected")
    finally:
        await engine.close()
