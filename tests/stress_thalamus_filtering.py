import asyncio
import time
import random
from src.nervous_system.corpus_callosum import CorpusCallosum
from src.nervous_system.bus_modulator import BusModulator
from src.kernel_lobes.thalamus_lobe import ThalamusLobe
from src.kernel_lobes.models import RawSensoryPulse, SensorySpike

async def run_thalamus_stress(duration=5.0):
    bus = CorpusCallosum(max_qsize=10000)
    modulator = BusModulator(bus)
    thalamus = ThalamusLobe(bus)
    
    # Register the gate
    bus.set_ingress_gate(thalamus.can_conscious_access)
    
    bus.start()
    modulator.start()
    
    print(f"[*] Starting Thalamus Stress Test ({duration}s)...")
    
    pulses_sent = 0
    pulses_promoted = 0
    t0 = time.time()
    
    # Subscribe to promoted spikes to count them
    def on_spike(pulse):
        nonlocal pulses_promoted
        pulses_promoted += 1
    bus.subscribe(SensorySpike, on_spike)
    
    async def high_freq_producer():
        nonlocal pulses_sent
        while time.time() - t0 < duration:
            # Simulate a mix of noise and real stimuli
            is_focal = random.random() < 0.1 # 10% are "important"
            
            # Update Thalamus node manually for the test to simulate its internal state
            if is_focal:
                thalamus.node.state.confidence = 0.9
            else:
                thalamus.node.state.confidence = 0.1
            
            pulse = RawSensoryPulse(
                payload={
                    "vision": {"lip_movement": 0.8 if is_focal else 0.05, "human_presence": 0.9},
                    "audio": {"vad_confidence": 0.7 if is_focal else 0.1},
                    "rms_audio": 0.2 if is_focal else 0.01
                }
            )
            await bus.publish(pulse)
            pulses_sent += 1
            if pulses_sent % 1000 == 0:
                await asyncio.sleep(0) # Yield for dispatcher

    # Create multiple producers to flood the bus
    tasks = [asyncio.create_task(high_freq_producer()) for _ in range(5)]
    
    while time.time() - t0 < duration:
        print(f"    - Sent: {pulses_sent} | Promoted Spikes: {pulses_promoted} | Gated (Thalamus): {bus.pulses_gated} | Dropped (Modulator): {bus.pulses_dropped} | Load: {modulator.load_factor:.2f}")
        await asyncio.sleep(1.0)
        
    await asyncio.gather(*tasks)
    bus.stop()
    await modulator.stop()
    
    print(f"\n[!] Final Results:")
    print(f"    - Total Raw Pulses Sent: {pulses_sent}")
    print(f"    - Spikes promoted to Cortex: {pulses_promoted}")
    print(f"    - Gated by Thalamus: {bus.pulses_gated}")
    print(f"    - Throughput: {pulses_sent / duration:.2f} pulses/sec")

if __name__ == "__main__":
    asyncio.run(run_thalamus_stress())
