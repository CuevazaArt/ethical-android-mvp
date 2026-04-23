"""
WebSocket sidecars: Nomad bridge and L0 dashboard (Bloque 34.2 / 34.4 — extraction).

``[SYNC_IDENTITY]`` is built via :func:`src.server.identity_envelope.build_sync_identity_ws_message`
(no lazy import; shared with :mod:`src.chat_server` ``/ws/chat``).
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from fastapi import APIRouter, WebSocket

from ..kernel import EthicalKernel
from ..observability.metrics import observe_chat_turn, record_chat_turn_async_timeout
from ..persistence.checkpoint import try_load_checkpoint
from ..real_time_bridge import RealTimeBridge
from .identity_envelope import build_sync_identity_ws_message

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/nomad")
async def nomad_bridge_ws_handler(websocket: WebSocket) -> None:
    """Nomad LAN bridge sensory endpoint (Module S)."""
    from src.modules.perception.nomad_bridge import get_nomad_bridge
    from ..settings import kernel_settings

    st = kernel_settings()
    nomad_timeout = st.kernel_nomad_chat_timeout_seconds

    await websocket.accept()
    logger.info("Nomad Bridge: Inbound WebSocket attempt from %s", websocket.client.host if websocket.client else "unknown")
    
    nomad_kernel = EthicalKernel(
        variability=st.kernel_variability,
        llm_mode=st.llm_mode,
        aclient=getattr(websocket.app.state, "aclient", None),
    )
    try_load_checkpoint(nomad_kernel)
    nomad_rt_bridge = RealTimeBridge(nomad_kernel)
    nb = get_nomad_bridge()

    async def _nomad_session_ready(ws: WebSocket) -> None:
        """Push the same ``[SYNC_IDENTITY]`` envelope as ``/ws/chat`` (Bloque 22.2)."""
        try:
            await ws.send_json(build_sync_identity_ws_message(nomad_kernel))
        except Exception as sync_e:
            logger.warning("nomad_sync_identity_emit_failed: %s", sync_e)

    async def _nomad_chat_callback(text: str) -> None:
        """Process a Nomad typed message with a strict timeout (Bloque 13.1)."""
        t0 = time.perf_counter()
        try:
            gen = nomad_rt_bridge.process_chat_stream(text, agent_id="nomad", place="chat")
            it = gen.__aiter__()
            result = None
            while True:
                try:
                    event = await asyncio.wait_for(it.__anext__(), timeout=nomad_timeout)
                    if event["event_type"] == "turn_finished":
                        result = event["payload"]["result"]
                        break
                except TimeoutError:
                    logger.warning(
                        "nomad_chat_text_timeout text_len=%d timeout=%.1fs",
                        len(text),
                        nomad_timeout,
                    )
                    record_chat_turn_async_timeout()
                    try:
                        nb.charm_feedback_queue.put_nowait(
                            {"type": "error", "message": "nomad_chat_turn_timeout"}
                        )
                    except Exception:
                        pass
                    break
                except StopAsyncIteration:
                    break
            if result is not None:
                observe_chat_turn(result.path, time.perf_counter() - t0)
                response_text = result.response.message if result.response else ""
                if response_text:
                    try:
                        nb.charm_feedback_queue.put_nowait(
                            {"type": "kernel_voice", "text": response_text}
                        )
                    except Exception:
                        pass
        except asyncio.CancelledError:
            raise
        except Exception as chat_e:
            logger.warning("nomad_chat_text error: %s", chat_e)

    try:
        await nomad_kernel.start()
        await nb.handle_websocket(
            websocket,
            chat_text_callback=_nomad_chat_callback,
            session_ready_hook=_nomad_session_ready,
        )
    finally:
        try:
            await nomad_kernel.stop()
        except Exception:
            logger.debug("nomad_kernel_stop_failed", exc_info=True)


@router.websocket("/ws/dashboard")
async def dashboard_ws_handler(websocket: WebSocket) -> None:
    """L0 Dashboard telemetry stream and command receiver."""
    from src.modules.perception.nomad_bridge import get_nomad_bridge
    from ..settings import kernel_settings

    await websocket.accept()
    q: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=30)
    bridge = get_nomad_bridge()
    bridge.dashboard_queues.append(q)

    st = kernel_settings()
    kernel = EthicalKernel(
        variability=st.kernel_variability,
        llm_mode=st.llm_mode,
        aclient=getattr(websocket.app.state, "aclient", None),
    )
    rt_bridge = RealTimeBridge(kernel)
    _turn_seq = 0

    async def recv_task() -> None:
        nonlocal _turn_seq
        session_context = ""

        try:
            while True:
                data = await websocket.receive_json()
                if data.get("type") == "user_input":
                    text = data.get("payload", {}).get("text", "")
                    if text:
                        _turn_seq += 1
                        logger.info("Dashboard User Input: %s", text)

                        async for event in rt_bridge.process_chat_stream(
                            text,
                            agent_id="dashboard_op",
                            place="dashboard",
                            conversation_context=session_context,
                        ):
                            if event["event_type"] == "turn_finished":
                                result = event["payload"]["result"]
                                response_text = (
                                    result.response.message if result.response else "Affirmative."
                                )

                                if len(session_context) > 2000:
                                    session_context = session_context[-1000:]
                                session_context += f"User: {text}\nKernel: {response_text}\n"

                                await websocket.send_json(
                                    {
                                        "type": "thought",
                                        "payload": {
                                            "text": response_text,
                                            "dissonance": bool(result.epistemic_dissonance.active)
                                            if result.epistemic_dissonance
                                            else False,
                                        },
                                    }
                                )

                                # Enviar telemetría del Kernel
                                tension_val = 0.0
                                trust_val = 0.0
                                if result.limbic_profile:
                                    tension_val = result.limbic_profile.get("social_tension", 0.0)
                                    trust_val = result.limbic_profile.get("social_trust", 0.0)
                                
                                bayes_conf = 0.0
                                bayes_delta = 0.0
                                if hasattr(result.perception_confidence, "confidence"):
                                    bayes_conf = result.perception_confidence.confidence
                                
                                social_circle = "unknown"
                                social_posture = "unknown"
                                if result.perception and hasattr(result.perception, "social_context"):
                                    social_circle = getattr(result.perception.social_context, "circle", "unknown")
                                    social_posture = getattr(result.perception.social_context, "posture", "unknown")

                                import psutil
                                cpu_p = psutil.cpu_percent() if hasattr(psutil, "cpu_percent") else 0.0
                                mem_p = psutil.virtual_memory().percent if hasattr(psutil, "virtual_memory") else 0.0
                                
                                # Extract GestaltSnapshot data for richer telemetry
                                pad_state = ""
                                dominant_archetype = ""
                                try:
                                    snap = getattr(result, "gestalt_snapshot", None) or getattr(result, "snapshot", None)
                                    if snap:
                                        pad = getattr(snap, "pad_state", None)
                                        if pad:
                                            pad_state = f"P={pad[0]:.2f} A={pad[1]:.2f} D={pad[2]:.2f}"
                                        dominant_archetype = getattr(snap, "dominant_archetype", "")
                                except Exception:
                                    pass
                                
                                ep_count = 0
                                identity_epoch = 0
                                try:
                                    ep_count = len(kernel.memory.episodes)
                                    identity_epoch = ep_count // 50
                                except Exception:
                                    pass

                                await websocket.send_json(
                                    {
                                        "type": "telemetry",
                                        "payload": {
                                            "turn_index": _turn_seq,
                                            "tension": tension_val,
                                            "trust": trust_val,
                                            "bayes_confidence": bayes_conf,
                                            "bayes_delta": bayes_delta,
                                            "social_circle": str(social_circle),
                                            "social_posture": str(social_posture),
                                            "vitality": result.weighted_score,
                                            "llm_mode": kernel.llm.mode if hasattr(kernel, "llm") else st.llm_mode,
                                            "vad_state": bridge.vad_speaking if hasattr(bridge, "vad_speaking") else False,
                                            "cpu_usage": cpu_p,
                                            "ram_usage": mem_p,
                                            "gov_status": kernel.dao_status(),
                                            "pad_state": pad_state,
                                            "dominant_archetype": dominant_archetype,
                                            "identity_epoch": identity_epoch,
                                            "episode_count": ep_count,
                                        }
                                    }
                                )

                                bridge.charm_feedback_queue.put_nowait(
                                    {
                                        "type": "kernel_voice",
                                        "text": response_text,
                                        "role": "dashboard_relay",
                                    }
                                )
                                break

        except Exception as e:
            logger.debug("Dashboard recv task ended: %s", e)

    async def send_task() -> None:
        try:
            while True:
                msg = await q.get()
                await websocket.send_json(msg)
        except Exception as e:
            logger.debug("Dashboard send task ended: %s", e)

    async def heartbeat_task() -> None:
        """Push system telemetry to dashboard every 2s regardless of chat activity."""
        import psutil

        try:
            while True:
                await asyncio.sleep(2.0)
                try:
                    cpu_p = psutil.cpu_percent()
                    mem_p = psutil.virtual_memory().percent

                    # Identity epoch from kernel memory
                    ep_count = 0
                    identity_epoch = 0
                    identity_digest = ""
                    try:
                        ep_count = len(kernel.memory.episodes)
                        identity_epoch = ep_count // 50
                        identity_digest = kernel.memory.get_reflection()[:80] if hasattr(kernel.memory, "get_reflection") else ""
                    except Exception:
                        pass

                    llm_mode = kernel.llm.mode if hasattr(kernel, "llm") and kernel.llm else st.llm_mode
                    vad_active = bridge.vad_speaking if hasattr(bridge, "vad_speaking") else False

                    heartbeat_payload = {
                        "type": "telemetry",
                        "payload": {
                            "cpu_usage": cpu_p,
                            "ram_usage": mem_p,
                            "llm_mode": llm_mode,
                            "vad_state": vad_active,
                            "heartbeat": True,
                            "identity_epoch": identity_epoch,
                            "identity_digest": identity_digest,
                            "episode_count": ep_count,
                        },
                    }
                    await websocket.send_json(heartbeat_payload)
                except Exception as hb_err:
                    logger.debug("Dashboard heartbeat error: %s", hb_err)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.debug("Dashboard heartbeat task ended: %s", e)

    try:
        await asyncio.gather(recv_task(), send_task(), heartbeat_task())
    except Exception as e:
        logger.error("Dashboard WS handler error: %s", e)
    finally:
        if q in bridge.dashboard_queues:
            bridge.dashboard_queues.remove(q)
