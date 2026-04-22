# Core ethical decision modules (MalAbs → scoring → poles → will path)
# See docs/proposals/CORE_DECISION_CHAIN.md for the flow
# This subpackage provides a clear boundary for the "core policy" tier

from src.modules.ethics.absolute_evil import AbsoluteEvilDetector
from src.modules.ethics.buffer import PreloadedBuffer
from src.modules.ethics.ethical_poles import EthicalPoles
from src.modules.safety.locus import LocusModule
from src.modules.cognition.sigmoid_will import SigmoidWill
from src.modules.somatic.sympathetic import SympatheticModule
from src.modules.social.uchi_soto import UchiSotoModule
from src.modules.ethics.weighted_ethics_scorer import WeightedEthicsScorer

__all__ = [
    "AbsoluteEvilDetector",
    "PreloadedBuffer",
    "WeightedEthicsScorer",
    "EthicalPoles",
    "SigmoidWill",
    "SympatheticModule",
    "LocusModule",
    "UchiSotoModule",
]
