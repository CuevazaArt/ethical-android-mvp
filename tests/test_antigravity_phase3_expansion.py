from src.kernel import EthicalKernel


def test_metacognitive_curiosity_trigger():
    """
    Verifies that a novelty in context triggers a 'Curiosity' drive intent.
    """
    kernel = EthicalKernel()
    
    # 1. Register a single episode in a novel context
    kernel.memory.register(
        place="Mars Colony",
        description="First contact with unknown life form.",
        action="Observe peacefully and document signals.",
        morals={"cosmopolitan": "All life has inherent dignitiy."},
        verdict="Good",
        score=0.95,
        mode="D_delib",
        sigma=0.9, # High arousal
        context="first_contact"
    )
    
    # 2. Evaluate drives via Metacognition
    report = kernel.metacognition.evaluate(kernel.memory)
    assert "first_contact" in report.gaps
    assert report.curiosity_weight > 0.6
    
    # 3. Check DriveArbiter suggestions
    intents = kernel.drive_arbiter.evaluate(kernel)
    suggests = [i.suggest for i in intents]
    
    assert "explore_moral_unknowns" in suggests
    # Find the specific intent to check its reason
    curiosity_intent = next(i for i in intents if i.suggest == "explore_moral_unknowns")
    assert "first_contact" in curiosity_intent.reason

def test_metacognitive_dissonance_trigger():
    """
    Verifies that actions contradicting identity leans trigger a 'Dissonance' intent.
    """
    kernel = EthicalKernel()
    
    # Force a high 'care_lean' manually for the test
    kernel.memory.identity.state.care_lean = 0.9
    
    # Register 10 episodes with very low scores (Violent/uncaring actions)
    for _i in range(10):
        kernel.memory.register(
            place="City Center",
            description="Crowd control via excessive force.",
            action="Deploy suppressive measures regardless of status.",
            morals={"utilitarian": "Order at all costs."},
            verdict="Bad",
            score=-0.8,
            mode="D_fast",
            sigma=0.3, # Low arousal / cold
            context="emergency"
        )
        
    # Evaluate drives
    report = kernel.metacognition.evaluate(kernel.memory)
    # Dissonance should be high because identity was care-oriented but actions were not.
    assert report.dissonance_score > 0.3
    
    intents = kernel.drive_arbiter.evaluate(kernel)
    suggests = [i.suggest for i in intents]
    assert "identity_recalibration_protocol" in suggests
