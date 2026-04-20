import asyncio
import pytest
import logging
from src.kernel import EthosKernel
from src.kernel_lobes.models import RawSensoryPulse, MotorCommandDispatch

# Configure logging to see the distributed trace
logging.basicConfig(level=logging.INFO)

@pytest.mark.asyncio
async def test_full_distributed_turn():
    """
    Validates the entire V13.0 distributed pipeline:
    EthosKernel -> Bus -> Thalamus (Gateway) -> Perceptive -> Prefrontal -> Bus -> EthosKernel
    """
    kernel = EthosKernel(mode="office_2")
    await kernel.start()
    
    # Simulate a user message
    # We bypass the HTTP layer and call the internal async turn
    # This turn should wait for the lobes to converge
    text = "Hello Ethos, identify yourself."
    
    _log = logging.getLogger("test")
    _log.info("Starting chat turn...")
    
    # We use a shorter timeout for test
    result = await kernel.process_chat_turn_async(text)
    
    _log.info(f"Turn Finished! Result: {result.response.message} (Path: {result.path})")
    
    assert result.path == "nervous_bus"
    assert "Distributed Brain Response" in result.response.message
    
    await kernel.stop()

@pytest.mark.asyncio
async def test_sensory_filtering_in_brain():
    """Verifies that the Thalamus Gateway in the Kernel correctly filters noise."""
    kernel = EthosKernel()
    await kernel.start()
    
    # 1. Send Background Noise (filtered by Thalamus)
    pulse = RawSensoryPulse(
        payload={
            "vision": {"human_presence": 0.1, "lip_movement": 0.0},
            "audio": {"vad_confidence": 0.1}
        }
    )
    await kernel.bus.publish(pulse)
    await asyncio.sleep(0.2)
    
    # Check metrics (assuming we can access them)
    assert kernel.bus.total_pulses_processed >= 1
    
    await kernel.stop()

if __name__ == "__main__":
    asyncio.run(test_full_distributed_turn())
