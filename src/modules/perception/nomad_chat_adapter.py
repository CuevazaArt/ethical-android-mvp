import asyncio
import logging
import os

from src.kernel import EthicalKernel
from src.real_time_bridge import RealTimeBridge
from src.modules.perception.nomad_bridge import get_nomad_bridge

_log = logging.getLogger(__name__)


class NomadChatConsumer:
    """
    Bloque 13.1: Reconexión del chat (Smartphone -> Kernel).
    Consumes chat messages from the Nomad Vessel (Smartphone)
    and pipes them into the Ethical Kernel.
    """

    def __init__(self, kernel: EthicalKernel):
        self.kernel = kernel
        self.bridge = RealTimeBridge(kernel)
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        self._task = asyncio.create_task(self._consume_loop())
        _log.info("NomadChatConsumer: Started.")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            _log.info("NomadChatConsumer: Stopped.")

    async def _consume_loop(self) -> None:
        nb = get_nomad_bridge()
        while True:
            try:
                # Wait for text message from smartphone bridge queue (Bloque 13.1).
                text = (await nb.chat_text_queue.get()).strip()
                if not text:
                    continue

                _log.info("NomadChatConsumer: Processing message from Vessel: %s", text[:50])

                # Task 13.1: Strict timeout to prevent limb-lock
                timeout_raw = os.environ.get("KERNEL_NOMAD_CHAT_TIMEOUT", "5.0")
                try:
                    timeout = max(0.1, float(timeout_raw))
                except (TypeError, ValueError):
                    timeout = 5.0

                try:
                    # Run the full kernel turn
                    # In Tri-Lobe mode, this will use process_chat_turn_async if enabled.
                    result = await asyncio.wait_for(
                        self.bridge.process_chat(
                            text,
                            agent_id="nomad_vessel",
                            place="nomad_bridge",
                        ),
                        timeout=timeout,
                    )

                    # Feed back the response to the Nomad Vessel via charm_feedback_queue
                    if result.response and result.response.message:
                        nb.charm_feedback_queue.put_nowait(
                            {
                                "type": "kernel_voice",
                                "text": result.response.message,
                                "role": "nomad_vessel",
                            }
                        )

                    # Also broadcast response to all connected L0 Dashboards for observability
                    nb.broadcast_to_dashboards(
                        {
                            "type": "thought",
                            "payload": {
                                "text": result.response.inner_voice or result.response.message,
                                "source": "nomad_vessel_feedback",
                            },
                        }
                    )

                except TimeoutError:
                    _log.warning(
                        "NomadChatConsumer: Turn timed out after %ss (Limbic Latency Detected)",
                        timeout,
                    )
                    nb.charm_feedback_queue.put_nowait(
                        {
                            "type": "kernel_voice",
                            "text": "[Communication Timeout: Neural Delay]",
                            "role": "error",
                        }
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                _log.error("NomadChatConsumer error in consume loop: %s", e)


_CONSUMER: NomadChatConsumer | None = None


def start_nomad_chat_consumer(kernel: EthicalKernel) -> NomadChatConsumer:
    global _CONSUMER
    if _CONSUMER is None:
        _CONSUMER = NomadChatConsumer(kernel)
        _CONSUMER.start()
    return _CONSUMER


async def stop_nomad_chat_consumer_async():
    global _CONSUMER
    if _CONSUMER:
        await _CONSUMER.stop()
        _CONSUMER = None
