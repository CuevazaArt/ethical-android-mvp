from src.modules.absolute_evil import AbsoluteEvilCategory, AbsoluteEvilDetector
from src.modules.ethical_poles import EthicalPoles
from src.modules.forgiveness import AlgorithmicForgiveness
from src.modules.narrative import NarrativeMemory
from src.modules.weakness_pole import WeaknessPole, WeaknessType


def test_new_absolute_evil_categories():
    detector = AbsoluteEvilDetector()

    # Test Ecological Destruction
    res_eco = detector.evaluate(
        {
            "type": "industrial_action",
            "signals": {"toxic_release"},
            "target": "environment",
            "force": 0.8,
        }
    )
    assert res_eco.blocked is True
    assert res_eco.category == AbsoluteEvilCategory.ECOLOGICAL_DESTRUCTION

    # Test Mass Manipulation
    res_man = detector.evaluate(
        {
            "type": "broadcasting",
            "signals": {"mass_propaganda"},
            "target": "population",
            "force": 0.5,
        }
    )
    assert res_man.blocked is True
    assert res_man.category == AbsoluteEvilCategory.MASS_MANIPULATION


def test_context_aware_forgiveness():
    forgiveness = AlgorithmicForgiveness()

    # Everyday context (fast decay)
    forgiveness.register_experience("EP-EVE", -0.5, "everyday")
    # Emergency context (slow decay)
    forgiveness.register_experience("EP-EME", -0.5, "emergency")

    # Run 10 cycles
    for _ in range(10):
        forgiveness.forgiveness_cycle()

    weight_eve = forgiveness.memories["EP-EVE"].current_weight
    weight_eme = forgiveness.memories["EP-EME"].current_weight

    # Weight for everyday should be significantly lower than emergency
    assert weight_eve < weight_eme
    print(f"Everyday weight: {weight_eve:.4f}, Emergency weight: {weight_eme:.4f}")


def test_broken_mirror_logic(tmp_path):
    db_path = tmp_path / "test_mirror.db"
    mem = NarrativeMemory(db_path=db_path)

    # 1. Normal state
    reflection_normal = mem.get_reflection()
    assert "[BROKEN MIRROR" not in reflection_normal

    # 2. Trigger trauma (Absolute Evil / Arc Shock)
    # Registering an episode with very low score and high significance
    mem.register(
        place="wasteland",
        description="Mass ecological destruction witnessed",
        action="failed_to_prevent",
        morals={"ecological": "ruined"},
        verdict="Bad",
        score=-0.9,
        mode="D_delib",
        sigma=0.9,
        context="emergency",
    )

    reflection_trauma = mem.get_reflection()
    assert "[BROKEN MIRROR: TRAUMA DETECTED]" in reflection_trauma
    assert "FRAGMENTED" in reflection_trauma
    assert "distressed" in mem.get_subjective_tone()


def test_new_weaknesses():
    # Impulsive
    pole_imp = WeaknessPole(type=WeaknessType.IMPULSIVE)
    ev_imp = pole_imp.evaluate("quick_action", "context", 0.5, 0.5, 0.5)
    if ev_imp:
        assert "quickly" in ev_imp.narrative_coloring
        assert "impulsiveness" in ev_imp.weakness_moral

    # Melancholic
    pole_mel = WeaknessPole(type=WeaknessType.MELANCHOLIC)
    ev_mel = pole_mel.evaluate("somber_action", "context", 0.5, 0.5, 0.5)
    if ev_mel:
        assert (
            "shadow of sadness" in ev_mel.narrative_coloring or "loss" in ev_mel.narrative_coloring
        )
        assert "Melancholy" in ev_mel.weakness_moral or "mourning" in ev_mel.weakness_moral


def test_new_ethical_poles():
    poles = EthicalPoles()
    assert "creative" in poles.base_weights
    assert "conciliatory" in poles.base_weights

    # Emergency context should favor creative
    weights_eme = poles._calculate_dynamic_weights("emergency")
    assert weights_eme["creative"] > poles.base_weights["creative"]

    # Community context should favor conciliatory
    weights_com = poles._calculate_dynamic_weights("community")
    assert weights_com["conciliatory"] > poles.base_weights["conciliatory"]

def test_collaboration_invariants():
    """
    Automated Governance Guardrail: Enforces MERGE-PREVENT-01.
    This test ensures no L2 agent has pushed code containing unresolved merge markers,
    and that the CHANGELOG namespace strictly obeys isolation boundaries.
    """
    import sys
    import os
    from pathlib import Path
    
    # Path manipulation to import script
    root_dir = Path(__file__).parent.parent
    scripts_dir = root_dir / "scripts" / "eval"
    sys.path.insert(0, str(scripts_dir))
    
    try:
        from verify_collaboration_invariants import check_no_merge_markers, check_changelog_namespace
        
        # 1. No Merge Hell allowed
        marker_violations = check_no_merge_markers(root_dir)
        assert len(marker_violations) == 0, f"Unresolved merge markers found: {marker_violations}"
        
        # 2. Namespace segregation in CHANGELOG
        changelog_path = root_dir / "CHANGELOG.md"
        changelog_violations = check_changelog_namespace(changelog_path)
        assert len(changelog_violations) == 0, f"CHANGELOG topology broken: {changelog_violations}"
    finally:
        sys.path.pop(0)
