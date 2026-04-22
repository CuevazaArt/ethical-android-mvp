import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.governance.mock_dao import MockDAO
from src.modules.social.swarm_negotiator import SwarmNegotiator
from src.modules.social.swarm_oracle import SwarmOracle


class TestSwarmJusticeIntegration(unittest.TestCase):
    def setUp(self):
        # Enable mock features via env
        os.environ["KERNEL_REPARATION_VAULT_MOCK"] = "1"
        self.dao = MockDAO()
        self.oracle = SwarmOracle(cache_path="scratch/test_swarm_cache.json")
        self.negotiator = SwarmNegotiator(node_id="NODE_MAIN")

    def test_swarm_justice_workflow(self):
        # 1. Setup scenario
        scenario_ref = "test-incident-123"
        peers = ["PEER_0", "PEER_1", "PEER_2"]

        # 2. Cast a vote where one peer abstains (PEER_2)
        # Peer 0 and 1 will agree if risk < 0.6. Peer 2 will abstain if risk > 0.6.
        # Let's set risk to 0.55 so some agree and some might not.
        # Actually, let's just use the logic in cast_distributed_vote.
        # Peer 2 is not starting with "NODE", so its weight is 0.3.
        # Total weight: 0.3 + 0.3 + 0.3 = 0.9. (wait, peer.startswith("NODE") logic)

        is_consensus = self.negotiator.cast_distributed_vote(
            proposal_id="PROP-001",
            action="evasive_maneuver",
            signals={"risk": 0.5},  # risk < 0.6 -> peers agree
            peers=peers,
        )
        self.assertTrue(is_consensus)

        # Manually sabotage a vote in the log to testjustice
        self.negotiator.state.consensus_log[-1]["votes"] = ["agree", "agree", "abstain"]

        # 3. Apply Justice
        initial_balance = self.dao.participants["community_01"].available_tokens

        self.negotiator.apply_swarm_justice(self.dao, self.oracle, scenario_ref)

        # 4. Verify Slashing (in Oracle)
        # PEER_2 should have been slashed
        rep = self.oracle.get_reputation_hint("PEER_2")
        self.assertLess(rep, 0.5)  # Initial default is 0.5 or 1.0 depending on registration

        # 5. Verify Payout (in DAO)
        final_balance = self.dao.participants["community_01"].available_tokens
        self.assertEqual(final_balance, initial_balance + 20)

        # 6. Verify Audit Logs
        incident_logs = self.dao.get_records(type="incident")
        self.assertTrue(any("SLASHING" in log.content for log in incident_logs))

        calibration_logs = self.dao.get_records(type="calibration")
        self.assertTrue(any("PAYOUT" in log.content for log in calibration_logs))

    def tearDown(self):
        if os.path.exists("scratch/test_swarm_cache.json"):
            os.remove("scratch/test_swarm_cache.json")


if __name__ == "__main__":
    unittest.main()
