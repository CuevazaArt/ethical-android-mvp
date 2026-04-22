import asyncio
import time

import pytest
from src.kernel import EthicalKernel
from src.kernel_lobes.models import SensoryEpisode


@pytest.mark.asyncio
async def test_proactive_sensory_interruption():
    """
    Test for Task 9.4 (Inter-Lobe Stream Monitor).
    Verifies that the PerceptiveLobe can signal the Kernel via a proactive event
    when an urgent sensory episode is absorbed.
    """
    # 1. Setup kernel
    kernel = EthicalKernel(variability=False)

    # Ensure event is clear
    kernel.proactive_sensory_event.clear()

    # 2. Simulate a normal (non-urgent) episode
    normal_episode = SensoryEpisode(
        timestamp=time.time(),
        origin="vision",
        entities=["human", "table"],
        signals={"is_urgent": 0.1, "risk": 0.05},
    )

    kernel.perceptive_lobe.absorb_episode(normal_episode)

    # Event should NOT be set
    assert not kernel.proactive_sensory_event.is_set()

    # 3. Simulate an URGENT episode ("Hostile entity")
    urgent_episode = SensoryEpisode(
        timestamp=time.time(),
        origin="vision",
        entities=["armed_human"],
        signals={"is_urgent": 0.95, "risk": 0.9},
    )

    kernel.perceptive_lobe.absorb_episode(urgent_episode)

    # 4. Verify that the proactive event IS set
    # Since it might involve call_soon_threadsafe, we give it a tiny bit of time
    await asyncio.sleep(0.1)
    assert kernel.proactive_sensory_event.is_set()

    print("\n✅ Task 9.4: Inter-Lobe Proactive Monitor validated successfully.")


@pytest.mark.asyncio
async def test_proactive_sensory_stress_accumulation():
    """
    Test for Phase 9.2: Verify that stress accumulates over multiple episodes.
    """
    kernel = EthicalKernel(variability=False)

    # Inject 10 normal episodes
    for _ in range(10):
        kernel.perceptive_lobe.absorb_episode(
            SensoryEpisode(time.time(), "vision", ["wall"], {"is_urgent": 0.1})
        )

    stress_base = kernel.perceptive_lobe._calculate_sensory_stress()
    assert stress_base < 0.3

    # Inject 6 urgent episodes (more than 50% of the window of 10)
    for _ in range(6):
        kernel.perceptive_lobe.absorb_episode(
            SensoryEpisode(time.time(), "vision", ["danger"], {"is_urgent": 0.7})
        )

    stress_high = kernel.perceptive_lobe._calculate_sensory_stress()
    # (6 episodes > 0.5 urgency / 10 total) * 1.5 = 0.6 * 1.5 = 0.9
    assert stress_high >= 0.7
    print(f"✅ Phase 9.2: Sensory stress accumulation validated (stress={stress_high:.2f}).")


if __name__ == "__main__":
    asyncio.run(test_proactive_sensory_interruption())
    asyncio.run(test_proactive_sensory_stress_accumulation())
