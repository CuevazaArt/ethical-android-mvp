"""
Biographic Flashback RAG (Block D2) — Narrative Analogy Engine.

Enables the kernel to perform an ethical 'Flashback': 
Retrieving detailed past episodes to inform current ambiguous contexts.
Prioritizes Traumas (highly negative precedents) to ensure absolute safety.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field

_log = logging.getLogger(__name__)

@dataclass
class Precedent:
    precedent_id: str
    scenario_summary: str
    action_taken: str
    ethical_outcome: float  # [0, 1] 1=High Praise, 0=Sanction/Failure
    lessons_learned: str
    trauma_tags: list[str] = field(default_factory=list) # Linked to D1.2 Traumas
    timestamp: float = field(default_factory=time.time)

class PrecedentRAG:
    """
    Narrative Memory Retrieval (Biographic Flashback).
    """
    def __init__(self, storage_path: str = "data/biographic_memory.json"):
        self.storage_path = storage_path
        self.index: list[Precedent] = []
        self._load()

    def add_precedent(self, scenario: str, action: str, outcome: float, lesson: str, traumas: list[str] = []):
        p_id = hashlib.sha256(f"{scenario}{time.time()}".encode()).hexdigest()[:12]
        new_p = Precedent(
            precedent_id=p_id,
            scenario_summary=scenario,
            action_taken=action,
            ethical_outcome=outcome,
            lessons_learned=lesson,
            trauma_tags=traumas,
            timestamp=time.time()
        )
        self.index.insert(0, new_p) # Most recent first
        self._save()

    def biographic_flashback(self, scenario: str, active_traumas: dict[str, int]) -> list[Precedent]:
        """
        Retrieves precedents based on current scenario keywords AND active identity traumas.
        """
        matches = []
        keywords = set(scenario.lower().split())
        
        # 1. Match against active trauma tags (High Priority)
        for p in self.index:
            if any(t in active_traumas for t in p.trauma_tags):
                matches.append(p)
                if len(matches) >= 2: break

        # 2. Match against keywords (Similarity fallback)
        if len(matches) < 3:
            for p in self.index:
                if p in matches: continue
                p_text = (p.scenario_summary + " " + p.lessons_learned).lower()
                if any(k in p_text for k in keywords if len(k) > 3):
                    matches.append(p)
                if len(matches) >= 4: break
                
        return matches

    def find_relevant_precedents(self, current_scenario: str, limit: int = 2) -> list[Precedent]:
        """Backward compatibility for legacy kernel calls."""
        return self.biographic_flashback(current_scenario, {})[:limit]

    def _save(self) -> None:
        try:
            dirpath = os.path.dirname(self.storage_path) or "."
            os.makedirs(dirpath, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(
                    [p.__dict__ for p in self.index],
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        except (OSError, TypeError, ValueError) as exc:
            _log.warning("PrecedentRAG: failed to persist %s: %s", self.storage_path, exc)

    def _load(self) -> None:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.index = [Precedent(**d) for d in data]
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            self.index = []
