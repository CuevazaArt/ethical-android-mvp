"""
Registry of Mnemonic Modules (Ethos V13.0).
Provides on-demand access to the absolute evil detector, strategist, and LLM modules.
"""

import logging
from typing import Any

_log = logging.getLogger(__name__)


class LobeRegistry:
    def __init__(self):
        self._instances: dict[str, Any] = {}

    def get_evil_detector(self):
        if "evil" not in self._instances:
            from src.modules.absolute_evil import AbsoluteEvilDetector

            self._instances["evil"] = AbsoluteEvilDetector()
        return self._instances["evil"]

    def get_llm(self):
        if "llm" not in self._instances:
            from src.modules.llm_layer import LLMModule

            self._instances["llm"] = LLMModule()
        return self._instances["llm"]

    def get_strategist(self):
        if "strategist" not in self._instances:
            from src.modules.strategy_engine import ExecutiveStrategist

            self._instances["strategist"] = ExecutiveStrategist()
        return self._instances["strategist"]

    # Add more factory methods as needed...
    def get_all_executive_modules(self):
        from src.modules.ethical_poles import EthicalPoles
        from src.modules.ethical_reflection import EthicalReflection
        from src.modules.pad_archetypes import PADArchetypeEngine
        from src.modules.salience_map import SalienceMap
        from src.modules.sigmoid_will import SigmoidWill

        return {
            "poles": EthicalPoles(),
            "will": SigmoidWill(),
            "reflection_engine": EthicalReflection(),
            "salience_map": SalienceMap(),
            "pad_archetypes": PADArchetypeEngine(),
        }
