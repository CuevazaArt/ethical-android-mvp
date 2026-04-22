import asyncio
import logging
import time

import pytest
from src.kernel_lobes.models import NervousPulse
from src.nervous_system.corpus_callosum import CorpusCallosum

logging.basicConfig(level=logging.INFO)


@pytest.mark.asyncio
async def test_corpus_callosum_throughput():
    bus = CorpusCallosum()
    bus.start()

    received_count = 0

    async def subscriber(pulse):
        nonlocal received_count
        received_count += 1

    bus.subscribe(NervousPulse, subscriber)

    start_time = time.time()
    n_pulses = 1000

    for i in range(n_pulses):
        pulse = NervousPulse(origin_lobe="test", payload=i)
        await bus.publish(pulse)

    # Wait for processing
    for _ in range(50):
        if received_count >= n_pulses:
            break
        await asyncio.sleep(0.1)

    end_time = time.time()
    duration = end_time - start_time

    print(f"\nThroughput: {received_count / duration:.2f} pulses/sec")
    assert received_count == n_pulses

    await bus.stop()


if __name__ == "__main__":
    asyncio.run(test_corpus_callosum_throughput())
