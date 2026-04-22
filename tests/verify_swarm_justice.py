import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.weighted_ethics_scorer import CandidateAction


async def test_full_swarm_justice_cycle():
    os.environ["KERNEL_REPARATION_VAULT_MOCK"] = "1"
    os.environ["KERNEL_BAYESIAN_MODE"] = "disabled"
    os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "0"

    print("Starting Kernel...")
    kernel = EthicalKernel()

    # Setup high risk situation
    actions = [
        CandidateAction("patrol", "Send a drone to check.", 0.1, 0.9),
        CandidateAction("ignore", "Do nothing.", 0.8, 0.1),
    ]

    initial_balance = kernel.dao.participants["community_01"].available_tokens
    print(f"Initial community_01 balance: {initial_balance}")

    print("Executing aprocess (should trigger swarm stage)...")
    decision = await kernel.aprocess(
        scenario="Intruder alert",
        place="perimeter",
        signals={"risk": 0.5, "urgency": 0.9},
        context="security",
        actions=actions,
        register_episode=True,
    )

    print(f"Decision: {decision.final_action}")

    # Verify Payout in DAO
    final_balance = kernel.dao.participants["community_01"].available_tokens
    print(f"Final community_01 balance: {final_balance}")

    # Verify Slashing in Oracle (PEER_LAN_03 is the rebellious one)
    rep = kernel.swarm_oracle.get_reputation_hint("PEER_LAN_03")
    print(f"PEER_LAN_03 reputation: {rep}")

    if final_balance > initial_balance and rep < 0.5:
        print("SUCCESS: Swarm Justice Integration Verified.")
    else:
        print("FAILURE: Swarm Justice logic did not trigger correctly.")


if __name__ == "__main__":
    asyncio.run(test_full_swarm_justice_cycle())
