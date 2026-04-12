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

from .modules.absolute_evil import AbsoluteEvilDetector
from .modules.augenesis import AugenesisEngine
from .modules.weighted_ethics_scorer import BayesianEngine
from .modules.buffer import PreloadedBuffer
from .modules.drive_arbiter import DriveArbiter
from .modules.ethical_poles import EthicalPoles
from .modules.ethical_reflection import EthicalReflection
from .modules.feedback_calibration_ledger import FeedbackCalibrationLedger
from .modules.forgiveness import AlgorithmicForgiveness
from .modules.immortality import ImmortalityProtocol
from .modules.judicial_escalation import EscalationSessionTracker
from .modules.llm_layer import LLMModule
from .modules.locus import LocusModule
from .modules.metaplan_registry import MetaplanRegistry
from .modules.mock_dao import MockDAO
from .modules.narrative import NarrativeMemory
from .modules.pad_archetypes import PADArchetypeEngine
from .modules.psi_sleep import PsiSleep
from .modules.salience_map import SalienceMap
from .modules.sigmoid_will import SigmoidWill
from .modules.skill_learning_registry import SkillLearningRegistry
from .modules.somatic_markers import SomaticMarkerStore
from .modules.subjective_time import SubjectiveClock
from .modules.sympathetic import SympatheticModule
from .modules.uchi_soto import UchiSotoModule
from .modules.user_model import UserModelTracker
from .modules.variability import VariabilityEngine
from .modules.weakness_pole import WeaknessPole
from .modules.working_memory import WorkingMemory
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
    bayesian: BayesianEngine | None = None
    poles: EthicalPoles | None = None
    sympathetic: SympatheticModule | None = None
    memory: NarrativeMemory | None = None
    uchi_soto: UchiSotoModule | None = None
    locus: LocusModule | None = None
    sleep: PsiSleep | None = None
    feedback_ledger: FeedbackCalibrationLedger | None = None
    dao: MockDAO | None = None
    weakness: WeaknessPole | None = None
    forgiveness: AlgorithmicForgiveness | None = None
    immortality: ImmortalityProtocol | None = None
    augenesis: AugenesisEngine | None = None
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
    checkpoint_persistence: CheckpointPersistencePort | None = None
