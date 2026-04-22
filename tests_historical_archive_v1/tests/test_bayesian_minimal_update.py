import os
import unittest
import numpy as np
from src.kernel import EthicalKernel
from src.modules.cognition.bayesian_engine import BayesianMode

class TestBayesianMinimalUpdate(unittest.TestCase):
    def setUp(self):
        # Set mode to POSTERIOR_DRIVEN so weights update immediately
        os.environ["KERNEL_BAYESIAN_MODE"] = "posterior_driven"
        self.kernel = EthicalKernel()

    def test_bayesian_learning_from_events(self):
        """Verify that record_turn_feedback shifts the hypothesis weights."""
        
        # Initial weights (approx [0.33, 0.33, 0.33] given Alpha [3,3,3])
        initial_weights = self.kernel.bayesian.current_weights_meta
        self.assertAlmostEqual(initial_weights[0], 0.3333, places=2)
        
        # 1. Simulate many positive social events
        for _ in range(10):
            self.kernel.register_turn_feedback("POSITIVE_SOCIAL", weight=1.0)
            
        new_weights = self.kernel.bayesian.current_weights_meta
        # Social (index 1) should have increased significantly
        # New Alpha[1] = 3 + 10 = 13. Sum = 3 + 13 + 3 = 19.
        # Target Weight[1] = 13/19 ≈ 0.684
        self.assertGreater(new_weights[1], initial_weights[1])
        self.assertAlmostEqual(new_weights[1], 13.0/19.0, places=2)
        
        # 2. Simulate Legal Compliance shift
        self.kernel.register_turn_feedback("LEGAL_COMPLIANCE", weight=10.0)
        final_weights = self.kernel.bayesian.current_weights_meta
        # Deontological (index 0) should now be higher than before
        # Alpha[0] = 3 + 10 = 13. Sum = 13 + 13 + 3 = 29.
        # Weight[0] = 13/29 ≈ 0.448
        self.assertGreater(final_weights[0], new_weights[0])
        self.assertAlmostEqual(final_weights[0], 13.0/29.0, places=2)

    def test_penalization_increases_uncertainty_spread(self):
        """Verify that PENALTY reduces alpha mass, making priors less certain."""
        # Initial mass: 3+3+3 = 9
        initial_total = np.sum(self.kernel.bayesian.posterior_alpha)
        
        self.kernel.register_turn_feedback("PENALTY", weight=5.0)
        
        final_total = np.sum(self.kernel.bayesian.posterior_alpha)
        # PENALTY reduces alpha by 0.2 * weight = 1.0 each. Total reduced by 3.
        self.assertLess(final_total, initial_total)
        self.assertAlmostEqual(final_total, initial_total - 3.0, places=1)

if __name__ == "__main__":
    unittest.main()
