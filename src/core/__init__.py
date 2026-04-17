# Core ethical decision modules (MalAbs → scoring → poles → will path)
# See docs/proposals/CORE_DECISION_CHAIN.md for the flow
# This subpackage provides a clear boundary for the "core policy" tier

from ..modules.absolute_evil import AbsoluteEvilDetector
from ..modules.buffer import PreloadedBuffer
from ..modules.ethical_poles import EthicalPoles
from ..modules.locus import LocusModule
from ..modules.sigmoid_will import SigmoidWill
from ..modules.sympathetic import SympatheticModule
from ..modules.uchi_soto import UchiSotoModule
from ..modules.weighted_ethics_scorer import WeightedEthicsScorer

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