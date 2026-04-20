import pytest
import asyncio
import time
from src.nervous_system.corpus_callosum import CorpusCallosum
from src.kernel_lobes.models import NervousPulse

class DummyPulse(NervousPulse):
    def __init__(self, priority=1):
        self.priority = priority
        self.pulse_id = f"test_pulse_{time.time()}"
        self.timestamp = time.time()
        self.payload = {}
        self.source = "test"

@pytest.mark.asyncio
async def test_corpus_callosum_max_in_flight_throttling():
    bus = CorpusCallosum(max_qsize=100)
    bus._max_in_flight = 2 # Artificially low
    bus.start()
    
    events_received = []
    
    async def subscriber(pulse):
        events_received.append(pulse)
        await asyncio.sleep(0.01) # Simulate slow lobe
        
    bus.subscribe(DummyPulse, subscriber)
    
    # Send pulses
    for _ in range(5):
        await bus.publish(DummyPulse())
        
    await asyncio.sleep(0.2)
    
    assert len(events_received) == 5, "Subscriber should receive all events"
    assert bus.total_pulses_processed == 5
    
    await bus.stop()

@pytest.mark.asyncio
async def test_corpus_callosum_priority_dropping():
    bus = CorpusCallosum(max_qsize=2)
    
    class FakeModulator:
        load_factor = 1.0
    
    bus.modulator = FakeModulator()
    
    await bus.publish(DummyPulse(priority=1))
    await bus.publish(DummyPulse(priority=0))
    
    assert bus.pulses_dropped > 0, "Should drop priority 1 pulse due to high load factor"
