"""
Optional dependency injection for `EthicalKernel`.

Use `KernelComponentOverrides` to substitute concrete module instances for tests,
experiments, or thin stubs — without editing `kernel.py` call sites.

This is **not** a full plugin ABI: overrides are typed as the same concrete classes
the kernel uses today. Duck-typed replacements may work at runtime but are not
guaranteed across refactors.
"""

from __future__ import annotations

from dataclasses import dataclass

from .modules.ethics.absolute_evil import AbsoluteEvilDetector
from .modules.cognition.bayesian_engine import BayesianInferenceEngine
from .modules.ethics.buffer import PreloadedBuffer
from .modules.governance.dao_orchestrator import DAOOrchestrator
from .modules.drive_arbiter import DriveArbiter
from .modules.ethics.ethical_poles import EthicalPoles
from .modules.ethics.ethical_reflection import EthicalReflection
from .modules.cognition.feedback_calibration_ledger import FeedbackCalibrationLedger
from .modules.memory.forgiveness import AlgorithmicForgiveness
from .modules.memory.immortality import ImmortalityProtocol
from .modules.safety.judicial_escalation import EscalationSessionTracker
from .modules.cognition.llm_layer import LLMModule
from .modules.safety.locus import LocusModule
from .modules.memory.memory_hygiene import MemoryHygieneService
from .modules.cognition.metaplan_registry import MetaplanRegistry
from .modules.governance.mock_dao import MockDAO
from .modules.cognition.motivation_engine import MotivationEngine
from .modules.memory.narrative import NarrativeMemory
from .modules.ethics.pad_archetypes import PADArchetypeEngine
from .modules.memory.psi_sleep import PsiSleep
from .modules.safety.safety_interlock import SafetyInterlock
from .modules.cognition.salience_map import SalienceMap
from .modules.cognition.sigmoid_will import SigmoidWill
from .modules.cognition.skill_learning_registry import SkillLearningRegistry
from .modules.somatic.somatic_markers import SomaticMarkerStore
from .modules.cognition.strategy_engine import ExecutiveStrategist
from .modules.cognition.subjective_time import SubjectiveClock
from .modules.social.swarm_negotiator import SwarmNegotiator
from .modules.somatic.sympathetic import SympatheticModule
from .modules.social.uchi_soto import UchiSotoModule
from .modules.social.user_model import UserModelTracker
from .modules.cognition.variability import VariabilityEngine
from .modules.ethics.weakness_pole import WeaknessPole
from .modules.ethics.weighted_ethics_scorer import WeightedEthicsScorer
from .modules.cognition.working_memory import WorkingMemory
from .persistence.checkpoint_port import CheckpointPersistencePort


@dataclass
class KernelComponentOverrides:
    """Per-field optional replacements for `EthicalKernel` subsystems.

    ``None`` on a field means: construct the kernel default for that slot.
    """

    var_engine: VariabilityEngine | None = None
    absolute_evil: AbsoluteEvilDetector | None = None
    buffer: PreloadedBuffer | None = None
    will: SigmoidWill | None = None
    bayesian: BayesianInferenceEngine | WeightedEthicsScorer | None = None
    poles: EthicalPoles | None = None
    sympathetic: SympatheticModule | None = None
    memory: NarrativeMemory | None = None
    uchi_soto: UchiSotoModule | None = None
    locus: LocusModule | None = None
    sleep: PsiSleep | None = None
    feedback_ledger: FeedbackCalibrationLedger | None = None
    dao: MockDAO | DAOOrchestrator | None = None
    safety_interlock: SafetyInterlock | None = None
    motivation_engine: MotivationEngine | None = None
    weakness: WeaknessPole | None = None
    forgiveness: AlgorithmicForgiveness | None = None
    immortality: ImmortalityProtocol | None = None
    pad_archetypes: PADArchetypeEngine | None = None
    working_memory: WorkingMemory | None = None
    ethical_reflection: EthicalReflection | None = None
    salience_map: SalienceMap | None = None
    drive_arbiter: DriveArbiter | None = None
    user_model: UserModelTracker | None = None
    subjective_clock: SubjectiveClock | None = None
    skill_learning: SkillLearningRegistry | None = None
    somatic_store: SomaticMarkerStore | None = None
    metaplan: MetaplanRegistry | None = None
    escalation_session: EscalationSessionTracker | None = None
    llm: LLMModule | None = None
    swarm_negotiator: SwarmNegotiator | None = None
    strategist: ExecutiveStrategist | None = None
    hygiene: MemoryHygieneService | None = None
    checkpoint_persistence: CheckpointPersistencePort | None = None
