import logging
import math
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from src.core.chat import ChatEngine, _generate_actions_from_signals
from src.core.safety import is_dangerous, sanitize

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


@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """Streaming endpoint: sends tokens as they arrive from the LLM."""
    await websocket.accept()
    engine = ChatEngine()
    ready = await engine.start()

    if not ready:
        await websocket.send_json({"done": True, "blocked": True, "reason": "LLM_UNAVAILABLE"})
        return

    try:
        while True:
            user_message = await websocket.receive_text()

            # Step 0: Safety gate
            user_message = sanitize(user_message)
            blocked, reason = is_dangerous(user_message)
            if blocked:
                _log.warning("Stream gate blocked: %s", reason)
                engine.memory.add(
                    summary=f"BLOCKED: {user_message[:60]} reason={reason}",
                    action="safety_block", score=0.0, context="safety_violation",
                )
                await websocket.send_json({
                    "done": True, "blocked": True, "reason": reason,
                    "message": "No puedo ayudar con eso. ¿Hay algo más en lo que pueda asistirte?",
                    "context": "safety_violation",
                })
                continue

            # Steps 1–2: Perceive + Ethics (fast, before streaming starts)
            signals = await engine.perceive(user_message)
            is_casual = (
                signals.context == "everyday_ethics"
                and signals.risk < 0.2
                and signals.hostility < 0.2
                and signals.manipulation < 0.2
            )
            evaluation = None
            if not is_casual:
                actions = _generate_actions_from_signals(signals)
                evaluation = engine.ethics.evaluate(actions, signals)

            # Step 3: Stream response tokens
            full_response = []
            try:
                async for token in engine.respond_stream(user_message, signals, evaluation):
                    full_response.append(token)
                    await websocket.send_json({"token": token})
            except Exception as e:
                _log.error("Streaming error: %s", e)

            message = "".join(full_response).strip()

            # Step 4: Remember
            score = evaluation.score if evaluation else 0.0
            if not math.isfinite(score):
                score = 0.0
            engine.memory.add(
                summary=f"Usuario: {user_message[:80]} → Respondí: {message[:80]}",
                action=evaluation.chosen.name if evaluation else "casual_chat",
                score=score, context=signals.context,
            )
            engine._conversation.append({"user": user_message, "assistant": message})
            if len(engine._conversation) > 10:
                engine._conversation = engine._conversation[-10:]

            # Final frame: metadata
            await websocket.send_json({
                "done": True,
                "message": message,
                "context": signals.context,
                "blocked": False,
            })

    except WebSocketDisconnect:
        _log.info("Stream client disconnected")
    finally:
        await engine.close()

