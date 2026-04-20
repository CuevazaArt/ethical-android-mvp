import pytest
import asyncio
import time
from src.nervous_system.corpus_callosum import CorpusCallosum
from src.nervous_system.bus_modulator import BusModulator
from src.kernel_lobes.models import NervousPulse, GlobalDegradationPulse

@pytest.mark.asyncio
async def test_bus_priority_ordering():
    bus = CorpusCallosum()
    received = []
    
    async def callback(pulse):
        received.append(pulse.priority)
    
    bus.subscribe(NervousPulse, callback)
    bus.start()
    
    # Injected reverse order
    await bus.publish(NervousPulse(priority=2))
    await bus.publish(NervousPulse(priority=1))
    await bus.publish(NervousPulse(priority=0))
    
    # Wait for processing
    await asyncio.sleep(0.1)
    await bus.stop()
    
    # Critical (0) should be first, then 1, then 2
    # Note: Because they arrive near-simultaneously, the dispatcher should pick 0 first.
    assert received == [0, 1, 2]

@pytest.mark.asyncio
async def test_modulator_saturation_pulse():
    bus = CorpusCallosum(max_qsize=1000)
    modulator = BusModulator(bus)
    
    degradation_received = []
    async def sub(pulse):
        if isinstance(pulse, GlobalDegradationPulse):
            degradation_received.append(pulse.degradation_factor)
            
    bus.subscribe(GlobalDegradationPulse, sub)
    # Note: We DON'T start the bus dispatcher so the queue stays full
    modulator.start()
    
    # Manually saturate the critical queue (maxsize 1000)
    # We put 900 pulses to trigger > 80% saturation (0.9)
    for _ in range(900):
        await bus._queues[0].put(NervousPulse(priority=0))
    
    # Initial load will be high, wait for exponential smoothing to reach > 0.8
    await asyncio.sleep(5.0) 
    
    assert modulator.load_factor >= 0.8
    
    await modulator.stop()

@pytest.mark.asyncio
async def test_backpressure_yield():
    bus = CorpusCallosum()
    modulator = BusModulator(bus)
    
    # Force high load
    modulator.load_factor = 0.9
    
    t0 = time.perf_counter()
    await modulator.biological_yield()
    t1 = time.perf_counter()
    
    # Should have slept > 0.001 (base) + 0.08 (throttle)
    duration = t1 - t0
    assert duration > 0.05
