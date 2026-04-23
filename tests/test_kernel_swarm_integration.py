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
        """Kernel DAO + oracle + negotiator: consensus log → apply_swarm_justice payout/slash.

        Note: ``EthicalKernel.aprocess`` does not call ``apply_swarm_justice``; integration
        is exercised via the negotiator API attached to the kernel (same pattern as
        ``tests/test_swarm_justice.py``).
        """
        kernel = EthicalKernel()
        peers = ["PEER_0", "PEER_1", "PEER_2"]
        initial_balance = kernel.dao.participants["community_01"].available_tokens

        consensus = kernel.swarm.cast_distributed_vote(
            proposal_id="PROP-SWARM-INT",
            action="patrol",
            signals={"risk": 0.5},
            peers=peers,
        )
        self.assertTrue(consensus)
        # Force one negligent abstention (lab-stable), as in test_swarm_justice.
        kernel.swarm.state.consensus_log[-1]["votes"] = ["agree", "agree", "abstain"]

        kernel.swarm.apply_swarm_justice(
            kernel.dao, kernel.swarm_oracle, "swarm-integration-case"
        )

        final_balance = kernel.dao.participants["community_01"].available_tokens
        self.assertEqual(final_balance, initial_balance + 20)

        rep = kernel.swarm_oracle.get_reputation_hint("PEER_2")
        self.assertLess(rep, 1.0)

if __name__ == "__main__":
    unittest.main()
