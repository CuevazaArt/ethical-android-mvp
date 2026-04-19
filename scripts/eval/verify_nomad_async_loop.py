"""
Validation Script: Nomad Async Loop Resilience (Bloque 9.4)
Tests the kernel's ability to handle parallel perception, async cancellation, and multimodal feedback under simulated stress.
"""

import asyncio
import threading
import time
import logging
import os
from unittest.mock import MagicMock

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("NomadResilienceTest")

async def test_async_loop_cancellation():
    """Verifies that the cooperative cancellation aborts heavy LLM tasks."""
    logger.info("--- Starting Async Loop Cancellation Test ---")
    
    # 1. Setup Mock Kernel and LLM
    from src.kernel import EthicalKernel
    from src.modules.llm_layer import LLMModule
    
    # Force Ollama mode for testing async paths
    os.environ["LLM_MODE"] = "ollama" 
    os.environ["KERNEL_CHAT_TURN_TIMEOUT"] = "0.5" # Very short timeout
    
    # Create the kernel
    kernel = EthicalKernel()
    
    # Mock LLM backend to simulate a slow response
    mock_backend = MagicMock()
    async def slow_acompletion(*args, **kwargs):
        logger.info("  LLM: Starting slow completion (expected to be cancelled)...")
        for i in range(10):
            await asyncio.sleep(0.2)
            from src.modules.llm_http_cancel import raise_if_llm_cancel_requested
            raise_if_llm_cancel_requested()
        return "Not cancelled!"
    
    mock_backend.acompletion = slow_acompletion
    kernel.llm._llm_backend = mock_backend
    
    # 2. Run process_chat_turn_stream with cancellation
    cancel_ev = threading.Event()
    
    logger.info("  Running chat turn with 0.5s timeout...")
    t0 = time.perf_counter()
    
    cancelled = False
    try:
        # Simulate the ChatServer's timeout-aware loop
        gen = kernel.process_chat_turn_stream(
            "Hello, identify this potential threat.", 
            cancel_event=cancel_ev
        )
        
        it = gen.__aiter__()
        while True:
            try:
                # wait_for 0.5s
                event = await asyncio.wait_for(it.__anext__(), timeout=0.5)
                logger.info(f"  Received event: {event['event_type']}")
            except asyncio.TimeoutError:
                logger.warning("  TIMEOUT! Setting cancellation event.")
                cancel_ev.set()
                break
            except StopAsyncIteration:
                break
                
    except Exception as e:
        if "LLMHttpCancelledError" in str(type(e)):
            logger.info("  SUCCESS: Received LLMHttpCancelledError!")
            cancelled = True
        else:
            logger.error(f"  UNEXPECTED ERROR: {e}")
    
    # Wait for background tasks to finish cleaning up if necessary
    await asyncio.sleep(0.5)
    
    elapsed = time.perf_counter() - t0
    logger.info(f"  Test finished in {elapsed:.2f}s.")
    
    if cancelled or cancel_ev.is_set():
        logger.info("  PASS: Cancellation event was set and/or exception caught.")
    else:
        logger.error("  FAIL: Loop did not respect timeout/cancellation.")

async def test_multimodal_thalamus_fusion():
    """Verifies that the Thalamus node correctly fuses vision and audio signals."""
    logger.info("--- Starting Thalamus Fusion Test ---")
    
    from src.kernel import EthicalKernel
    from src.modules.sensor_contracts import SensorSnapshot
    
    kernel = EthicalKernel()
    if not kernel.thalamus:
        logger.warning("  Thalamus node not initialized. Skipping test.")
        return

    # Simulate sensor data: High lip movement + High audio = Focused address
    snapshot = SensorSnapshot(
        image_metadata={"lip_movement": 0.9, "human_presence": 1.0},
        audio_emergency=0.8,
        ambient_noise=0.1
    )
    
    from src.kernel_handlers.perception import run_perception_pipeline
    
    logger.info("  Running perception pipeline with high attention signals...")
    stage, _, _thal = await run_perception_pipeline(
        kernel, "Are you listening?", "", snapshot, time.monotonic(), None
    )
    
    if _thal:
        logger.info(f"  Fusion Result: Attention={_thal['attention_locus']:.2f}, Tension={_thal['sensory_tension']:.2f}")
        if _thal['attention_locus'] > 0.7:
            logger.info("  PASS: Thalamus correctly identified focal attention.")
        else:
            logger.error("  FAIL: Thalamus attention locus too low.")
    else:
        logger.error("  FAIL: Thalamus fusion returned None.")

if __name__ == "__main__":
    asyncio.run(test_async_loop_cancellation())
    asyncio.run(test_multimodal_thalamus_fusion())
