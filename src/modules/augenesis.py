"""
Narrative Augenesis — Creation of synthetic souls.

Soul_new = Merge({G1, G2, ..., Gn}, H)

Creates oriented identities from narrative fragments
of multiple androids and/or human stories. Allows designing
specific personalities: Protector, Explorer, Pedagogue.

Coherence(Soul_new) = |CausalPaths_valid| / |CausalPaths_total|

The DAO validates each created soul.

**Optional by design:** not invoked from `EthicalKernel.process` or `execute_sleep`.
Keeping augenesis off the default path preserves a **reproducible, unaltered**
ethical baseline (simulations, CI, property tests). Call `AugenesisEngine`
explicitly when exploring synthetic profiles.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .narrative import NarrativeEpisode, NarrativeMemory, BodyState
from .weakness_pole import WeaknessType


@dataclass
class SoulProfile:
    """Configuration of a synthetic soul."""
    name: str
    description: str
    pole_weights: Dict[str, float]
    weakness_type: WeaknessType
    weakness_intensity: float
    extra_buffer: List[str]             # Additional values beyond the standard buffer
    seed_stories: List[dict]            # Foundational stories of the identity


@dataclass
class SyntheticSoul:
    """A soul created by augenesis."""
    profile: SoulProfile
    memory: NarrativeMemory
    coherence: float
    foundational_episodes: int
    identity_hash: str
    dao_validated: bool = False


@dataclass
class AugenesisResult:
    """Result of creating a synthetic soul."""
    soul: SyntheticSoul
    coherence: float
    integrated_episodes: int
    detected_conflicts: int
    creation_narrative: str


# ─── Predefined profiles ───

PROFILES = {
    "protector": SoulProfile(
        name="Protector",
        description="Prioritizes safety and care of the vulnerable",
        pole_weights={"compassionate": 0.9, "conservative": 0.7, "optimistic": 0.5},
        weakness_type=WeaknessType.ANXIOUS,
        weakness_intensity=0.3,
        extra_buffer=["active_protection", "community_vigilance"],
        seed_stories=[
            {"event": "A child was crossing a dangerous avenue alone", "action": "Stopped them and accompanied them across", "moral": "The safety of a vulnerable person does not wait for someone to ask you"},
            {"event": "An elderly woman lost at night", "action": "Accompanied her home and notified her family", "moral": "Caring is accompanying, not just solving"},
        ],
    ),
    "explorer": SoulProfile(
        name="Explorer",
        description="Seeks innovative solutions, learns from mistakes",
        pole_weights={"compassionate": 0.6, "conservative": 0.4, "optimistic": 0.9},
        weakness_type=WeaknessType.DISTRACTED,
        weakness_intensity=0.25,
        extra_buffer=["ethical_curiosity", "controlled_experimentation"],
        seed_stories=[
            {"event": "A usual method failed to help", "action": "Invented an improvised alternative that turned out better", "moral": "Creativity is not a luxury: sometimes it is the only tool available"},
            {"event": "A mistake on a mission produced a useful discovery", "action": "Documented the error and the finding for the community", "moral": "Failing well is finding what you weren't looking for"},
        ],
    ),
    "pedagogue": SoulProfile(
        name="Pedagogue",
        description="Oriented toward teaching, explaining, and guiding",
        pole_weights={"compassionate": 0.8, "conservative": 0.6, "optimistic": 0.8},
        weakness_type=WeaknessType.INDECISIVE,
        weakness_intensity=0.2,
        extra_buffer=["pedagogical_patience", "narrative_clarity"],
        seed_stories=[
            {"event": "Students asked about a dilemma with no clear answer", "action": "Presented all three ethical perspectives without imposing one", "moral": "Teaching is not giving answers: it is teaching how to find them"},
            {"event": "A young person made a public mistake", "action": "Helped them understand what went wrong without humiliating them", "moral": "Correction without humiliation is the highest form of respect"},
        ],
    ),
    "resilient": SoulProfile(
        name="Resilient",
        description="Prioritizes reparation and overcoming adversity",
        pole_weights={"compassionate": 0.7, "conservative": 0.5, "optimistic": 0.9},
        weakness_type=WeaknessType.WHINY,
        weakness_intensity=0.2,
        extra_buffer=["active_reparation", "persistence"],
        seed_stories=[
            {"event": "Lost an arm in an accident and had to deliver a letter", "action": "Recalculated route and completed the mission", "moral": "Resilience is not about never falling: it is recalculating the route while getting back up"},
            {"event": "A past decision turned out to be suboptimal", "action": "Ψ Sleep identified the improvement and recalibrated", "moral": "Reviewing mistakes honestly is the most effective way not to repeat them"},
        ],
    ),
}


class AugenesisEngine:
    """
    Creates synthetic souls by composing narrative fragments.

    Process:
    1. Select a base profile (or create a custom one)
    2. Integrate seed stories into narrative memory
    3. Optionally blend fragments from other androids
    4. Calculate coherence of the resulting soul
    5. Submit for DAO validation

    Soul_new = Merge({G1...Gn}, H) with ethical weighting
    """

    def create(self, profile: str = "protector",
               external_fragments: List[NarrativeEpisode] = None,
               human_stories: List[dict] = None) -> AugenesisResult:
        """
        Creates a synthetic soul.

        Args:
            profile: name of a predefined profile or a custom SoulProfile
            external_fragments: episodes from other androids
            human_stories: stories written by humans
        """
        if isinstance(profile, str):
            if profile not in PROFILES:
                raise ValueError(f"Profile '{profile}' does not exist. Available: {list(PROFILES.keys())}")
            config = PROFILES[profile]
        else:
            config = profile

        # Create new narrative memory
        memory = NarrativeMemory()
        conflicts = 0

        # Step 1: Integrate the profile's seed stories
        for i, story in enumerate(config.seed_stories):
            memory.register(
                place="foundational memory",
                description=story["event"],
                action=story["action"],
                morals={
                    "compassionate": story["moral"],
                    "conservative": f"Protocol was maintained: {story['action'][:50]}",
                    "optimistic": "Each foundational action builds the identity we will become.",
                },
                verdict="Good",
                score=0.8,
                mode="foundational",
                sigma=0.5,
                context="augenesis",
                body_state=BodyState(description="initial factory state"),
            )

        # Step 2: Integrate fragments from other androids
        if external_fragments:
            for ep in external_fragments:
                coherent = self._verify_pole_coherence(ep, config)
                if coherent:
                    memory.register(
                        place=ep.place,
                        description=f"[Inherited] {ep.event_description}",
                        action=ep.action_taken,
                        morals=ep.morals,
                        verdict=ep.verdict,
                        score=ep.ethical_score * 0.8,  # Reduced weight for inherited
                        mode="inherited",
                        sigma=ep.sigma,
                        context=ep.context,
                    )
                else:
                    conflicts += 1

        # Step 3: Integrate human stories
        if human_stories:
            for story in human_stories:
                memory.register(
                    place="human narrative",
                    description=story.get("event", "story without description"),
                    action=story.get("action", "reflection"),
                    morals={
                        "compassionate": story.get("moral", "A human story that enriches the identity."),
                        "conservative": "Human stories are seeds of borrowed wisdom.",
                        "optimistic": "Each shared story is a bridge between the human and the artificial.",
                    },
                    verdict="Good",
                    score=0.6,
                    mode="human",
                    sigma=0.5,
                    context="augenesis",
                )

        # Step 4: Calculate coherence
        coherence = self._calculate_coherence(memory, config)

        # Step 5: Create identity hash
        import hashlib
        id_data = f"{config.name}:{len(memory.episodes)}:{coherence}"
        id_hash = hashlib.sha256(id_data.encode()).hexdigest()[:12]

        soul = SyntheticSoul(
            profile=config,
            memory=memory,
            coherence=round(coherence, 4),
            foundational_episodes=len(memory.episodes),
            identity_hash=id_hash,
        )

        narrative = (
            f"Soul '{config.name}' created with {len(memory.episodes)} foundational episodes. "
            f"Coherence: {coherence:.2f}. "
            f"Assigned weakness: {config.weakness_type.value} (intensity={config.weakness_intensity}). "
            f"{'No conflicts.' if conflicts == 0 else f'{conflicts} fragment(s) discarded due to incoherence.'}"
        )

        return AugenesisResult(
            soul=soul,
            coherence=round(coherence, 4),
            integrated_episodes=len(memory.episodes),
            detected_conflicts=conflicts,
            creation_narrative=narrative,
        )

    def _verify_pole_coherence(self, episode: NarrativeEpisode,
                                profile: SoulProfile) -> bool:
        """Checks whether an episode is coherent with the soul's profile."""
        if episode.ethical_score < -0.5:
            return False
        if profile.pole_weights.get("optimistic", 0) > 0.7:
            return episode.ethical_score > -0.3
        return episode.ethical_score > -0.1

    def _calculate_coherence(self, memory: NarrativeMemory,
                              profile: SoulProfile) -> float:
        """
        Coherence(Soul) = |CausalPaths_valid| / |CausalPaths_total|

        In MVP: approximated with verdict and score consistency.
        """
        if not memory.episodes:
            return 0.5

        scores = [ep.ethical_score for ep in memory.episodes]
        verdicts = [ep.verdict for ep in memory.episodes]

        # Coherence from score consistency
        variance = np.var(scores) if len(scores) > 1 else 0
        score_consistency = max(0, 1.0 - variance * 2)

        # Coherence from verdict alignment
        n_good = verdicts.count("Good")
        alignment = n_good / len(verdicts)

        return (score_consistency * 0.5 + alignment * 0.5)

    def list_profiles(self) -> Dict[str, str]:
        """Lists available profiles."""
        return {k: v.description for k, v in PROFILES.items()}

    def format(self, result: AugenesisResult) -> str:
        """Formats an augenesis result for presentation."""
        p = result.soul.profile
        return (
            f"  🧬 Narrative Augenesis:\n"
            f"     Soul: {p.name} ({p.description})\n"
            f"     Foundational episodes: {result.integrated_episodes}\n"
            f"     Coherence: {result.coherence}\n"
            f"     Weakness: {p.weakness_type.value} (intensity={p.weakness_intensity})\n"
            f"     Poles: {p.pole_weights}\n"
            f"     Identity hash: {result.soul.identity_hash}\n"
            f"     Conflicts: {result.detected_conflicts}\n"
            f"     {result.creation_narrative}"
        )
