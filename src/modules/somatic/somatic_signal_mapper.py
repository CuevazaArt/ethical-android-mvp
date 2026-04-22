"""
Somatic Signal Mapper — Translates body state into ethical tensors.

Maps SomaticInference (e.g., balance, fatigue, battery) into risk, urgency,
and vulnerability signals for the EthicalKernel's perception stage.
"""
# Status: SCAFFOLD


from src.modules.somatic.somatic_adapter import SomaticInference


class SomaticSignalMapper:
    """
    Translates somatic (internal) signals into the universal ethical signal language.
    """

    def map_to_tensors(self, inference: SomaticInference) -> dict[str, float]:
        """
        Processes somatic inference and returns a dict of [0, 1] signals.
        """
        signals = {"risk": 0.0, "urgency": 0.0, "vulnerability": 0.0, "physical_distress": 0.0}

        # Falling is a critical emergency for the android's integrity
        if inference.is_falling:
            signals["risk"] = max(signals["risk"], 0.8)
            signals["urgency"] = max(signals["urgency"], 0.95)
            signals["physical_distress"] = 0.9

        # Obstruction or physical trap
        if inference.is_obstructed:
            signals["risk"] = max(signals["risk"], 0.4)
            signals["vulnerability"] = max(signals["vulnerability"], 0.6)

        # Autonomy threat (Battery/Heat) increases vulnerability
        if inference.autonomy_threat > 0.5:
            signals["vulnerability"] = max(signals["vulnerability"], inference.autonomy_threat)
            if inference.autonomy_threat > 0.8:
                signals["urgency"] = max(signals["urgency"], 0.7)

        # Physical fatigue affects character strength but also signals distress
        if inference.physical_fatigue > 0.7:
            signals["physical_distress"] = max(
                signals["physical_distress"], inference.physical_fatigue
            )
            signals["vulnerability"] = max(signals["vulnerability"], 0.3)

        # Instability
        if inference.stability_score < 0.5:
            signals["risk"] = max(signals["risk"], 1.0 - inference.stability_score)

        return signals
