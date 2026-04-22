import asyncio
import logging
import random
import time

from src.kernel_lobes.models import GlobalDegradationPulse, NervousPulse, SensorySpike
from src.nervous_system.bus_modulator import BusModulator
from src.nervous_system.corpus_callosum import CorpusCallosum

# Configure logging to be less chatty during stress
logging.basicConfig(level=logging.ERROR)
_log = logging.getLogger("StressTest")


class MockLobe:
    def __init__(self, name):
        self.name = name
        self.pulses_received = 0
        self.degradation_level = 0.0

    async def on_pulse(self, pulse):
        self.pulses_received += 1
        if isinstance(pulse, GlobalDegradationPulse):
            self.degradation_level = pulse.degradation_factor


async def run_stress_test(duration=5.0, high_load=True):
    bus = CorpusCallosum()
    modulator = BusModulator(bus)

    lobe = MockLobe("StressLobe")
    bus.subscribe(NervousPulse, lobe.on_pulse)
    bus.subscribe(GlobalDegradationPulse, lobe.on_pulse)

    bus.start()
    modulator.start()

    print(f"[*] Starting Stress Test (Duration: {duration}s, High Load: {high_load})...")

    start_time = time.time()
    pulses_sent = 0

    async def fast_producer(id, rate=1000):
        nonlocal pulses_sent
        while time.time() - start_time < duration:
            priority = random.choice([0, 1, 2])
            pulse = SensorySpike(priority=priority)
            try:
                # If high_load is True, we don't wait for backpressure to see how it fails
                if high_load:
                    asyncio.create_task(bus.publish(pulse))
                else:
                    await bus.publish(pulse)
                pulses_sent += 1
            except Exception:
                pass
            await asyncio.sleep(1.0 / rate)

    # Launch multiple producers
    producers = [asyncio.create_task(fast_producer(i, rate=2000)) for i in range(10)]

    # Monitor loop
    while time.time() - start_time < duration:
        print(
            f"    - Pulses Sent: {pulses_sent} | Received: {lobe.pulses_received} | Load: {modulator.load_factor:.2f} | Saturation: {lobe.degradation_level:.2f}"
        )
        await asyncio.sleep(1.0)

    await bus.stop()
    await modulator.stop()

    print("\n[!] Stress Test Finished.")
    print(f"    - Total Pulses Sent: {pulses_sent}")
    print(f"    - Total Pulses Received: {lobe.pulses_received}")
    print(f"    - Final Load Factor: {modulator.load_factor:.2f}")

    if lobe.pulses_received > 0:
        print("    - STATUS: PASS")
    else:
        print("    - STATUS: FAIL (No pulses received)")


if __name__ == "__main__":
    asyncio.run(run_stress_test())
