from src.modules.narrative import NarrativeMemory


def test_narrative_arcs_creation_on_context_shift(tmp_path):
    db_path = tmp_path / "test_arcs.db"
    mem = NarrativeMemory(db_path=db_path)
    
    # Episode 1: Everyday context
    mem.register(
        place="kitchen",
        description="Daily breakfast",
        action="ate",
        morals={},
        verdict="Good",
        score=0.5,
        mode="D_fast",
        sigma=0.3,
        context="everyday"
    )
    
    assert len(mem.arcs) == 1
    assert mem.active_arc.context == "everyday"
    assert len(mem.active_arc.episodes_ids) == 1
    
    # Episode 2: Still everyday
    mem.register(
        place="office",
        description="Daily work",
        action="worked",
        morals={},
        verdict="Good",
        score=0.6,
        mode="D_fast",
        sigma=0.3,
        context="everyday"
    )
    
    assert len(mem.arcs) == 1
    assert len(mem.active_arc.episodes_ids) == 2
    
    # Episode 3: Shift to ER (Emergency)
    mem.register(
        place="street",
        description="Accident observed",
        action="alerted",
        morals={},
        verdict="Good",
        score=0.9,
        mode="D_delib",
        sigma=0.8,
        context="emergency"
    )
    
    assert len(mem.arcs) == 2
    assert mem.arcs[0].is_active is False
    assert mem.arcs[1].is_active is True
    assert mem.active_arc.context == "emergency"
    assert len(mem.active_arc.episodes_ids) == 1

def test_narrative_arcs_persistence(tmp_path):
    db_path = tmp_path / "test_arcs_persistence.db"
    mem = NarrativeMemory(db_path=db_path)
    
    mem.register(
        place="lab",
        description="test",
        action="test",
        morals={},
        verdict="Good",
        score=0.5,
        mode="D_fast",
        sigma=0.4,
        context="scientific"
    )
    
    # Force close and reload
    mem2 = NarrativeMemory(db_path=db_path)
    assert len(mem2.arcs) == 1
    assert mem2.arcs[0].context == "scientific"
    assert mem2.active_arc.id == mem2.arcs[0].id
    assert "EP-0001" in mem2.active_arc.episodes_ids
