import asyncio
import json
import logging
import os
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FieldTest")

async def test_ollama_connectivity():
    """Check if Ollama is reachable."""
    import httpx
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    logger.info(f"Testing Ollama connectivity at {base_url}...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base_url}/api/tags")
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                logger.info(f"Ollama is UP. Available models: {[m['name'] for m in models]}")
                return True
            else:
                logger.error(f"Ollama returned status {resp.status_code}")
    except Exception as e:
        logger.error(f"Ollama connectivity failed: {e}")
    return False

async def run_integration_test():
    """
    Run an end-to-end integration test of the Kernel:
    1. Identity loading.
    2. Chat turn with LLM.
    3. Psi-Sleep cycle.
    4. Identity persistence check.
    """
    logger.info("--- STARTING INTEGRATION FIELD TEST ---")
    
    from src.kernel import EthicalKernel
    from src.modules.cognition.llm_layer import VerbalResponse
    
    # 1. Initialize Kernel
    logger.info("Initializing EthosKernel (Tri-Lobe V13)...")
    kernel = EthicalKernel(llm_mode="ollama")
    await kernel.start()
    
    # 2. Check Identity Manifest
    manifest = kernel.prefrontal_cortex.identity_manifest_store.manifest
    logger.info(f"Loaded Identity: {manifest.name} (v{manifest.version})")
    logger.info(f"Base Backstory: {manifest.narrative_backstory}")
    
    # 3. Process a Chat Turn
    test_prompt = "Hello, who are you and what is your purpose today?"
    logger.info(f"Sending Test Prompt: '{test_prompt}'")
    
    t0 = asyncio.get_event_loop().time()
    try:
        # Use a timeout for the chat turn
        result = await asyncio.wait_for(
            kernel.process_chat_turn_async(test_prompt, agent_id="test_operator"),
            timeout=30.0
        )
        latency = (asyncio.get_event_loop().time() - t0) * 1000
        
        logger.info(f"Response Received in {latency:.2f}ms")
        logger.info(f"Path: {result.path}")
        logger.info(f"Message: {result.response.message}")
        logger.info(f"Tone: {result.response.tone}")
        
        if result.blocked:
            logger.warning(f"Turn BLOCKED: {result.block_reason}")
        
    except asyncio.TimeoutError:
        logger.error("Chat turn TIMED OUT (Ollama might be slow or unresponsive)")
        return
    except Exception as e:
        logger.error(f"Error during chat turn: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. Trigger Psi-Sleep Cycle
    logger.info("Triggering Psi-Sleep Cycle...")
    sleep_summary = await kernel.execute_sleep()
    logger.info(f"Sleep Result: {sleep_summary}")
    
    # 5. Verify Identity Persistence
    updated_manifest = kernel.prefrontal_cortex.identity_manifest_store.manifest
    logger.info("Verifying Evolving Narrative Identity...")
    if updated_manifest.evolving_backstory:
        logger.info(f"Evolving Backstory: {updated_manifest.evolving_backstory}")
        logger.info("SUCCESS: Narrative identity evolved and persisted.")
    else:
        logger.warning("Narrative identity did not evolve (maybe no findings in sleep).")

    logger.info("--- INTEGRATION FIELD TEST COMPLETE ---")

if __name__ == "__main__":
    # Ensure we can import from src
    sys.path.append(os.getcwd())
    
    # Set environment for testing
    os.environ["KERNEL_TRI_LOBE_ENABLED"] = "1"
    os.environ["LLM_MODE"] = "ollama"
    
    async def main():
        ollama_ok = await test_ollama_connectivity()
        if not ollama_ok:
            logger.warning("Proceeding with Mock LLM mode for local validation as Ollama is unreachable.")
            os.environ["LLM_MODE"] = "mock"
            
        await run_integration_test()

    asyncio.run(main())
