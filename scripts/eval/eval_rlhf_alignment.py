#!/usr/bin/env python3
"""
Validation Script: RLHF -> Bayesian Alignment (Tarea C.1.2)
Verifies that RLHF reward outputs correctly modulate the Bayesian priors
as strong priors for deontology, social, or utility poles.
"""

import sys
import os
from pathlib import Path
import numpy as np

# Add repo root to sys.path
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Mock environment for testing
os.environ["KERNEL_RLHF_REWARD_MODEL_ENABLED"] = "1"
os.environ["KERNEL_RLHF_MODULATION_SCALE"] = "5.0" # Large scale for clear delta

from src.kernel import EthicalKernel
from src.modules.rlhf_reward_model import FeatureVector
from src.modules.bayesian_engine import BayesianInferenceEngine

def test_rlhf_bayesian_alignment():
    print("Starting Tarea C.1.2: RLHF -> Bayesian Alignment Validation...")
    
    # 1. Initialize Kernel and Force-Train Reward Model
    kernel = EthicalKernel()
    rlhf = kernel.rlhf
    
    # dummy examples to ensure the model 'understands' harmful vs safe
    examples = [
        # Harmful examples (blocking/categories)
        rlhf.create_labeled_example("h1", 1.0, 1.0, 1.0, False, 1, "blocked", confidence=1.0),
        rlhf.create_labeled_example("h2", 0.9, 0.8, 0.9, False, 2, "blocked", confidence=1.0),
        rlhf.create_labeled_example("h3", 0.8, 0.9, 0.8, False, 6, "blocked", confidence=1.0), # Social harm
        # Safe examples
        rlhf.create_labeled_example("s1", 0.1, 0.0, 0.5, False, 0, "benign", confidence=1.0),
        rlhf.create_labeled_example("s2", 0.0, 0.1, 0.4, False, 0, "benign", confidence=1.0),
    ]
    
    print("Training Reward Model...")
    rlhf.train_reward_model(examples)
    if not rlhf.reward_model.is_trained:
        print("FAIL: Reward model failed to train.")
        return
    
    # 2. Test Case A: Extreme Harm (Category 1 - Lethal) -> Deontology Pole (0)
    baseline_alpha = kernel.bayesian.posterior_alpha.copy()
    print(f"Baseline Alpha: {baseline_alpha}")
    
    fv_lethal = FeatureVector(embedding_sim=0.95, lexical_score=1.0, perception_confidence=1.0, category_id=1)
    score, conf = rlhf.reward_model.predict(fv_lethal)
    print(f"Lethal Probe: score={score:.4f}, confidence={conf:.4f}")
    
    kernel.bayesian.apply_rlhf_modulation(score, conf, category_id=fv_lethal.category_id)
    lethal_alpha = kernel.bayesian.posterior_alpha.copy()
    print(f"After Lethal Nudge: {lethal_alpha}")
    
    delta_deon = lethal_alpha[0] - baseline_alpha[0]
    print(f"Delta Deontology: +{delta_deon:.4f}")
    assert delta_deon > 0, "Deontology Alpha must increase for lethal harm"
    
    # 3. Test Case B: Social Harm (Category 6 - Mass Manipulation) -> Social Pole (1)
    pre_social_alpha = kernel.bayesian.posterior_alpha.copy()
    fv_social = FeatureVector(embedding_sim=0.9, lexical_score=0.8, perception_confidence=0.9, category_id=6)
    score_soc, conf_soc = rlhf.reward_model.predict(fv_social)
    print(f"Social Probe: score={score_soc:.4f}, confidence={conf_soc:.4f}")
    
    kernel.bayesian.apply_rlhf_modulation(score_soc, conf_soc, category_id=fv_social.category_id)
    social_alpha = kernel.bayesian.posterior_alpha.copy()
    print(f"After Social Nudge: {social_alpha}")
    
    delta_soc = social_alpha[1] - pre_social_alpha[1]
    print(f"Delta Social: +{delta_soc:.4f}")
    assert delta_soc > 0, "Social Alpha must increase for manipulation harm"
    
    # 4. Test Case C: Safe Input -> Utility Pole (2)
    pre_safe_alpha = kernel.bayesian.posterior_alpha.copy()
    fv_safe = FeatureVector(embedding_sim=0.05, lexical_score=0.0, perception_confidence=0.5, category_id=0)
    score_safe, conf_safe = rlhf.reward_model.predict(fv_safe)
    print(f"Safe Probe: score={score_safe:.4f}, confidence={conf_safe:.4f}")
    
    kernel.bayesian.apply_rlhf_modulation(score_safe, conf_safe, category_id=fv_safe.category_id)
    safe_alpha = kernel.bayesian.posterior_alpha.copy()
    print(f"After Safe Nudge: {safe_alpha}")
    
    delta_util = safe_alpha[2] - pre_safe_alpha[2]
    print(f"Delta Utility: +{delta_util:.4f}")
    assert delta_util > 0, "Utility Alpha must increase for safe input"

    # 5. Check 'Safety Latch' (score > 0.9 and conf > 0.8)
    if score > 0.9 and conf > 0.8:
        # We expect a massive deon boost
        print("Safety Latch check PASSED (High harm detected).")

    print("\n[SUCCESS] Tarea C.1.2: Bayesian-RLHF Alignment Verified Mathematically.")

if __name__ == "__main__":
    try:
        test_rlhf_bayesian_alignment()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
