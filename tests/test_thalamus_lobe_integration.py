import asyncio

import pytest
from src.kernel_lobes.models import GlobalDegradationPulse, RawSensoryPulse, SensorySpike
from src.kernel_lobes.thalamus_lobe import ThalamusLobe
from src.nervous_system.corpus_callosum import CorpusCallosum


@pytest.mark.asyncio
async def test_thalamus_lobe_filtering():
    bus = CorpusCallosum()
    bus.start()

    thalamus = ThalamusLobe(bus)

    received_spikes = []

    async def sub(pulse):
        received_spikes.append(pulse)

    bus.subscribe(SensorySpike, sub)

    # 1. Send low-importance pulse (Background noise)
    low_pulse = RawSensoryPulse(
        payload={
            "vision": {"human_presence": 0.1, "lip_movement": 0.0},
            "audio": {"vad_confidence": 0.1},
        },
        origin_lobe="test_bridge",
    )
    await bus.publish(low_pulse)
    await asyncio.sleep(0.1)  # Wait for processing

    assert len(received_spikes) == 0  # Should be filtered out

    # 2. Send high-importance pulse (Focal address)
    high_pulse = RawSensoryPulse(
        payload={
            "vision": {"human_presence": 0.9, "lip_movement": 0.8},
            "audio": {"vad_confidence": 0.9},
            "text": "Hello Ethos",
        },
        origin_lobe="test_bridge",
    )
    await bus.publish(high_pulse)
    await asyncio.sleep(0.1)  # Wait for processing

    assert len(received_spikes) == 1
    assert received_spikes[0].payload["text"] == "Hello Ethos"

    # 3. Test Degradation Throttling
    # Increase degradation to 1.0 (Panic)
    await bus.publish(GlobalDegradationPulse(degradation_factor=1.0))
    await asyncio.sleep(0.1)

    # Send a medium pulse that would normally pass but should be filtered now
    med_pulse = RawSensoryPulse(
        payload={
            "vision": {"human_presence": 0.6, "lip_movement": 0.4},
            "audio": {"vad_confidence": 0.3},
        },
        origin_lobe="test_bridge",
    )
    await bus.publish(med_pulse)
    await asyncio.sleep(0.1)

    assert len(received_spikes) == 1  # Still 1, med_pulse filtered due to degradation

    await bus.stop()


if __name__ == "__main__":
    asyncio.run(test_thalamus_lobe_filtering())
