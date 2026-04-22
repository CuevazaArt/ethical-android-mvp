import asyncio
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel


class TestKernelSwarmIntegration(unittest.TestCase):
    def setUp(self):
        os.environ["KERNEL_REPARATION_VAULT_MOCK"] = "1"
        os.environ["KERNEL_BAYESIAN_MODE"] = "disabled"
        # Mock some peers in the global environment if needed,
        # but the kernel will mock them if empty.

    def test_full_swarm_justice_cycle(self):
        async def run_test():
            kernel = EthicalKernel()

            # Setup a situation that results in High Risk to trigger swarm stage
            # Risk > 0.4

            # We need to ensure we reach the swarm stage.
            # In EthicalKernel.aprocess, risk > 0.4 triggers it.
            # Let's mock the perceptive lobe to return high risk.

            from src.modules.cognition.llm_layer import LLMPerception

            LLMPerception(
                risk=0.8,
                urgency=0.9,
                hostility=0.5,
                calm=0.2,
                vulnerability=0.3,
                legality=1.0,
                manipulation=0.1,
                familiarity=0.1,
                social_tension=0.5,
                suggested_context="security",
                summary="Security alert",
            )

            # We don't mock everything, just run process_chat_turn_async
            # with manual signals if possible, or just let natural inference run.
            # To be sure, we can inject signals.

            # Let's just use a simplified call to aprocess
            from src.modules.ethics.weighted_ethics_scorer import CandidateAction

            actions = [
                CandidateAction("patrol", "Send a drone to check.", 0.1, 0.9),
                CandidateAction("ignore", "Do nothing.", 0.8, 0.1),
            ]

            # Initial balance of community_01
            initial_balance = kernel.dao.participants["community_01"].available_tokens

            await kernel.aprocess(
                scenario="Intruder alert",
                place="perimeter",
                signals={"risk": 0.8, "urgency": 0.9},  # High risk triggers swarm
                context="security",
                actions=actions,
                register_episode=True,
            )

            # Verify Swarm stage was reached and Payout executed
            # Since peers are mocked as ["PEER_LAN_01", ...], and risk is high (0.8),
            # SwarmNegotiator.cast_distributed_vote will have peers 'abstain'
            # (risk > 0.6 -> abstain).
            # Abstaining nodes are treated as negligent in apply_swarm_justice.

            # Verify Payout in DAO
            final_balance = kernel.dao.participants["community_01"].available_tokens

            # apply_swarm_justice pays 20 EthosTokens per negligent node.
            # 3 peers should have abstained.
            # Total payout = 3 * 20 = 60?
            # Wait, apply_swarm_justice loop (lines 199-234):
            # It executes payout FOR EACH negligent node.

            self.assertGreater(final_balance, initial_balance)
            print(f"Payout successful. community_01 balance: {final_balance}")

            # Verify Slashing in Oracle
            rep = kernel.swarm_oracle.get_reputation_hint("PEER_LAN_01")
            self.assertLess(rep, 1.0)
            print(f"Slashing successful. PEER_LAN_01 reputation: {rep}")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
