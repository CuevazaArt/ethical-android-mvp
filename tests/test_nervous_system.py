import asyncio
import time

import pytest
from src.kernel_lobes.models import GlobalDegradationPulse, NervousPulse
from src.nervous_system.bus_modulator import BusModulator
from src.nervous_system.corpus_callosum import CorpusCallosum


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
    bus = CorpusCallosum(max_qsize=10)
    modulator = BusModulator(bus)

    degradation_received = []

    async def sub(pulse):
        if isinstance(pulse, GlobalDegradationPulse):
            degradation_received.append(pulse.degradation_factor)

    bus.subscribe(GlobalDegradationPulse, sub)
    modulator.start()

    # Saturate manually without starting the bus yet
    for _ in range(9):
        bus._queues[0].put_nowait(NervousPulse(priority=0))

    # Wait for modulator to see saturation and publish pulse
    # We need enough time for smoothing: 7-8 cycles at 0.1s each
    await asyncio.sleep(1.0)

    assert modulator.load_factor > 0.8

    # Now start bus to process the degradation pulse
    bus.start()
    await asyncio.sleep(0.2)

    assert len(degradation_received) > 0, "Should have received the degradation pulse"

    await modulator.stop()
    await bus.stop()


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
