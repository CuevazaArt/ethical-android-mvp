from src.kernel_lobes.models import EthicalSentence, SemanticState


class ExecutiveLobe:
    """
    Lóbulo Frontal: Generates the Narrative Monologue and Motor Plans.
    Triggered only if LimbicEthicalLobe outputs a Safe/Valid sentence.
    """

    def __init__(self):
        # TODO(Copilot): Initialize MotivationEngine, Narrative Arcs here
        pass

    def formulate_response(self, state: SemanticState, ethics: EthicalSentence) -> str:
        """
        Generates actual output (speech or motor intent).
        """
        if not ethics.is_safe:
            return "Veto Triggered: " + (ethics.veto_reason or "Unsafe intent")

        # If safe, write a proper response considering limbic tension (tri-lobe stub)
        if ethics.social_tension_locus > 0.05:
            return (
                f"Response generated for intent: {state.raw_prompt} "
                f"(tension={ethics.social_tension_locus:.2f})"
            )
        return f"Response generated for intent: {state.raw_prompt}"
