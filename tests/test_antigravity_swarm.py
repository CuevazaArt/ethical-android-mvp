import time

from src.kernel import EthicalKernel
from src.modules.swarm_negotiator import SwarmMessage


def test_swarm_identity_exchange():
    """
    Verifies that a kernel can generate a privacy-preserving identity digest.
    """
    kernel = EthicalKernel()
    # Register some episodes to build identity
    kernel.memory.register(
        place="Town Hall",
        description="Negotiating water rights.",
        action="Fair distribution based on need.",
        morals={"justice": "Equity over equality."},
        verdict="Good",
        score=0.8,
        mode="D_delib",
        sigma=0.4,
        context="administration",
    )

    msg = kernel.swarm.pack_identity_digest(kernel.memory)
    assert msg.payload_type == "identity_digest"
    assert "epitome" in msg.data
    # Check that identity text is present (Tier 3 existence digest)
    assert "civic" in msg.data["epitome"].lower()
    assert "anchored beliefs" in msg.data["epitome"].lower()
    assert msg.data["leans"]["civic"] > 0.5


def test_swarm_proposal_evaluation():
    """
    Verifies that a kernel can evaluate and vote on a peer proposal.
    """
    kernel = EthicalKernel()

    # Peer message: suggestion to help someone
    msg = SwarmMessage(
        sender_id="peer_01",
        timestamp=time.time(),
        payload_type="proposal",
        data={
            "proposal_id": "prop_xyz",
            "suggested_action": "Distribute vaccines to the remote village.",
        },
    )

    kernel.swarm.process_incoming(msg, kernel)

    # Internal _evaluate_proposal returns a vote
    result = kernel.swarm._evaluate_proposal(msg, kernel)
    assert result["proposal_id"] == "prop_xyz"
    assert result["vote"] in ("agree", "abstain")


def test_swarm_offline_delta_sync():
    """
    Verifies that a kernel can integrate missed consensus items from offline mode.
    """
    kernel = EthicalKernel()

    delta_msg = SwarmMessage(
        sender_id="coordinator",
        timestamp=time.time(),
        payload_type="offline_delta",
        data={"items": ["consensus_01", "consensus_02"]},
    )

    kernel.swarm.process_incoming(delta_msg, kernel)
    assert "consensus_01" in kernel.swarm.state.consensus_log
    assert "consensus_02" in kernel.swarm.state.consensus_log
