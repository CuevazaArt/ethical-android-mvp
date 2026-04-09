"""
WebSocket chat server: one EthicalKernel (and STM) per connection.

Run from repo root:
  uvicorn src.chat_server:app --host 127.0.0.1 --port 8765

Or: python -m src.chat_server
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from .kernel import ChatTurnResult, EthicalKernel
from .real_time_bridge import RealTimeBridge

app = FastAPI(title="Ethical Android Chat", version="1.0")


def _chat_turn_to_jsonable(r: ChatTurnResult) -> Dict[str, Any]:
    """Compact JSON-safe view (no full internal objects)."""
    out: Dict[str, Any] = {
        "blocked": r.blocked,
        "path": r.path,
        "block_reason": r.block_reason,
        "response": {
            "message": r.response.message,
            "tone": r.response.tone,
            "hax_mode": r.response.hax_mode,
            "inner_voice": r.response.inner_voice,
        },
    }
    if r.perception:
        p = r.perception
        out["perception"] = {
            "risk": p.risk,
            "urgency": p.urgency,
            "hostility": p.hostility,
            "calm": p.calm,
            "manipulation": p.manipulation,
            "suggested_context": p.suggested_context,
            "summary": p.summary,
        }
    if r.decision is not None:
        d = r.decision
        out["decision"] = {
            "final_action": d.final_action,
            "decision_mode": d.decision_mode,
            "blocked": d.blocked,
        }
        if d.moral:
            out["decision"]["verdict"] = d.moral.global_verdict.value
            out["decision"]["score"] = d.moral.total_score
        if d.affect:
            out["decision"]["affect"] = {
                "pad": list(d.affect.pad),
                "dominant_archetype": d.affect.dominant_archetype_id,
                "weights": d.affect.weights,
            }
        if d.reflection:
            out["decision"]["reflection"] = {
                "conflict_level": d.reflection.conflict_level,
                "pole_spread": d.reflection.pole_spread,
                "strain_index": d.reflection.strain_index,
                "uncertainty": d.reflection.uncertainty,
                "will_mode": d.reflection.will_mode,
                "note": d.reflection.note,
            }
    if r.narrative:
        n = r.narrative
        out["narrative"] = {
            "compassionate": n.compassionate,
            "conservative": n.conservative,
            "optimistic": n.optimistic,
            "synthesis": n.synthesis,
        }
    return out


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> JSONResponse:
    return JSONResponse(
        {
            "service": "ethical-android-chat",
            "websocket": "/ws/chat",
            "protocol": "Send JSON: {\"text\": str, \"agent_id\"?: str, \"include_narrative\"?: bool}",
        }
    )


@app.websocket("/ws/chat")
async def ws_chat(ws: WebSocket) -> None:
    """
    One kernel per connection so WorkingMemory stays isolated per session.

    Client → server (JSON text):
      {"text": "...", "agent_id": "optional", "include_narrative": false}

    Server → client:
      JSON object from _chat_turn_to_jsonable (see GET /).
    """
    await ws.accept()
    kernel = EthicalKernel(
        variability=os.environ.get("KERNEL_VARIABILITY", "1") not in ("0", "false", "False"),
        llm_mode=os.environ.get("LLM_MODE", "auto"),
    )
    bridge = RealTimeBridge(kernel)

    try:
        while True:
            raw = await ws.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_json({"error": "invalid_json", "hint": "send JSON with a \"text\" field"})
                continue

            text = (data.get("text") or "").strip()
            if not text:
                await ws.send_json({"error": "empty_text"})
                continue

            agent_id = data.get("agent_id") or "user"
            include_narrative = bool(data.get("include_narrative", False))

            result = await bridge.process_chat(
                text,
                agent_id=agent_id,
                place="chat",
                include_narrative=include_narrative,
            )
            await ws.send_json(_chat_turn_to_jsonable(result))
    except WebSocketDisconnect:
        return


def main() -> None:
    import uvicorn

    host = os.environ.get("CHAT_HOST", "127.0.0.1")
    port = int(os.environ.get("CHAT_PORT", "8765"))
    uvicorn.run(app, host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
