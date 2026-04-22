import asyncio

import pytest
from src.modules.somatic.affect_projection_relay import get_affect_relay
from src.modules.perception.nomad_bridge import get_nomad_bridge
from src.modules.ethics.pad_archetypes import AffectProjection


@pytest.mark.asyncio
async def test_affect_relay_transmission():
    """
    Verifies that the AffectVesselRelay correctly formats PAD data
    and injects it into the Nomad Bridge queue.
    """
    bridge = get_nomad_bridge()
    relay = get_affect_relay()

    # 1. Clear queue
    while not bridge.charm_feedback_queue.empty():
        bridge.charm_feedback_queue.get_nowait()

    # 2. Create a dummy projection (Positive/Active/Dominant)
    projection = AffectProjection(
        pad=(1.0, 1.0, 1.0),
        weights={"calm": 0.1, "alert": 0.9},
        dominant_archetype_id="alert_compasiva",
        beta=4.0,
    )

    # 3. Transmit
    relay.transmit(projection)

    # 4. Check queue
    assert not bridge.charm_feedback_queue.empty()
    msg = bridge.charm_feedback_queue.get_nowait()

    assert msg["type"] == "orb_update"
    assert "visuals" in msg
    assert msg["visuals"]["color"] == "#00ffcc"  # Correct mapping for P=1.0
    assert msg["visuals"]["pulse_s"] == 0.5  # Fast pulse for A=1.0
    assert msg["visuals"]["scale"] == 1.5  # Large scale for D=1.0

    print("✅ Affective Relay transmission validated.")


if __name__ == "__main__":
    asyncio.run(test_affect_relay_transmission())
