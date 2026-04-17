"""
Ethos Kernel Core Manifest (Order 3).

Explicit definition of the kernel's functional boundaries, ethical tiers,
and "shipping" modules. Used to distinguish between the tested decision core
and experimental/advisory layers.
"""

from enum import Enum
from dataclasses import dataclass, field

class EthicalTier(Enum):
    DECISION_CORE = "decision_core"      # Critical path (MalAbs, Bayes, Poles, Will)
    DECISION_SUPPORT = "decision_support"  # Non-veto context (Locus, Uchi-Soto, Sensors)
    PERCEPTION_VERBAL = "perception_verbal" # LLM Interface
    NARRATIVE_THEATER = "narrative_theater" # Identity, affect, and "drama"
    GOVERNANCE_MOCK = "governance_mock"     # Simulations of DAO/Escalation

@dataclass
class ModuleManifest:
    name: str
    tier: EthicalTier
    is_veto: bool = False
    is_experimental: bool = False
    doc_pointer: str = ""

# The "Canonical Kernel" definition as of April 2026.
CORE_MODULES = [
    ModuleManifest(
        name="absolute_evil",
        tier=EthicalTier.DECISION_CORE,
        is_veto=True,
        doc_pointer="docs/proposals/MALABS_SEMANTIC_LAYERS.md"
    ),
    ModuleManifest(
        name="bayesian_engine",
        tier=EthicalTier.DECISION_CORE,
        doc_pointer="docs/proposals/CORE_DECISION_CHAIN.md"
    ),
    ModuleManifest(
        name="weighted_ethics_scorer",
        tier=EthicalTier.DECISION_CORE,
        doc_pointer="docs/proposals/PROPOSAL_BAYESIAN_MIXTURE_FEEDBACK.md"
    ),
    ModuleManifest(
        name="llm_layer",
        tier=EthicalTier.PERCEPTION_VERBAL,
        doc_pointer="docs/proposals/PERCEPTION_VALIDATION.md"
    ),
    ModuleManifest(
        name="uchi_soto",
        tier=EthicalTier.DECISION_SUPPORT,
        doc_pointer="docs/proposals/PROPOSAL_SOCIAL_ROSTER_HIERARCHICAL_RELATIONS.md"
    ),
    ModuleManifest(
        name="locus",
        tier=EthicalTier.DECISION_SUPPORT,
        doc_pointer="docs/proposals/PROPOSAL_ETOSOCIAL_STATE_V12.md"
    ),
    ModuleManifest(
        name="narrative",
        tier=EthicalTier.NARRATIVE_THEATER,
        doc_pointer="docs/proposals/PROPOSAL_002_NARRATIVE_ARCHITECTURE_PLAN.md"
    ),
    ModuleManifest(
        name="mock_dao",
        tier=EthicalTier.GOVERNANCE_MOCK,
        is_experimental=True,
        doc_pointer="docs/proposals/MOCK_DAO_SIMULATION_LIMITS.md"
    ),
]

def get_module_manifest(name: str) -> ModuleManifest | None:
    for m in CORE_MODULES:
        if m.name == name:
            return m
    return None

def is_core_veto(name: str) -> bool:
    m = get_module_manifest(name)
    return m.is_veto if m else False
