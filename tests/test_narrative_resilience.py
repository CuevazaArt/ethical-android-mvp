import pytest
from datetime import datetime, timedelta
from src.modules.narrative import NarrativeMemory
from src.modules.narrative_types import BodyState

def test_significance_calculation(tmp_path):
    db_path = tmp_path / "test_significancia.db"
    mem = NarrativeMemory(db_path=db_path)
    
    # 1. Mundane episode
    ep1 = mem.register(
        place="lab",
        description="Daily check",
        action="checked",
        morals={},
        verdict="Good",
        score=0.1,
        mode="D_fast",
        sigma=0.5, # perfectly calm
        context="everyday"
    )
    assert ep1.significance < 0.5
    
    # 2. Significant episode (High arousal)
    ep2 = mem.register(
        place="street",
        description="Loud noise",
        action="investigated",
        morals={},
        verdict="Good",
        score=0.2,
        mode="D_fast",
        sigma=0.9, # extreme arousal
        context="everyday"
    )
    assert ep2.significance > 0.7
    
    # 3. Traumatic episode (Low score + High arousal)
    ep3 = mem.register(
        place="warehouse",
        description="Theft allowed",
        action="ignored",
        morals={"duty": "failed"},
        verdict="Bad",
        score=-0.8,
        mode="D_delib",
        sigma=0.9,
        context="emergency"
    )
    assert ep3.significance > 0.9
    assert ep3.is_sensitive is True
    # Verify Arc Shock: the traversal closed the previous one and started a new recovery one
    assert len(mem.arcs) == 2 # Arc 1 (Everyday) was closed, Arc 2 (Post-Trauma Emergency) started
    assert mem.arcs[0].is_active is False
    assert mem.arcs[0].predominant_archetype == "trauma_dissonance"
    assert mem.active_arc.title.startswith("Post-Traumatic")

def test_pruning_mundane(tmp_path):
    import sqlite3
    db_path = tmp_path / "test_poda.db"
    mem = NarrativeMemory(db_path=db_path)
    
    # Inject an "old" mundane episode via direct SQL because register sets 'now'
    from datetime import datetime, timedelta
    old_date = (datetime.now() - timedelta(days=70)).isoformat()
    
    # Register Normally
    ep = mem.register("lab", "test", "test", {}, "Good", 0.1, "D_fast", 0.5, "everyday")
    
    # Manually backdate it in DB
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute("UPDATE narrative_episodes SET timestamp = ?, significance = 0.1 WHERE id = ?", (old_date, ep.id))
        conn.commit()
    
    # Verify it exists
    assert len(mem.persistence.load_all_episodes()) == 1
    
    # Prune
    deleted = mem.prune(max_age_days=60, min_significance=0.5)
    assert deleted == 1
    assert len(mem.persistence.load_all_episodes()) == 0

def test_flashbulb_memory_not_pruned(tmp_path):
    import sqlite3
    db_path = tmp_path / "test_flashbulb.db"
    mem = NarrativeMemory(db_path=db_path)
    
    old_date = (datetime.now() - timedelta(days=70)).isoformat()
    
    # Significant episode
    ep = mem.register("lab", "CRITICAL", "SAVED", {}, "Good", 0.9, "D_delib", 0.9, "emergency")
    
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute("UPDATE narrative_episodes SET timestamp = ? WHERE id = ?", (old_date, ep.id))
        conn.commit()
        
    # Prune
    deleted = mem.prune(max_age_days=60, min_significance=0.7)
    assert deleted == 0 # It should STAY because significance > 0.7
    assert len(mem.persistence.load_all_episodes()) == 1
