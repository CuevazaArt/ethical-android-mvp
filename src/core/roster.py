# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
Ethos Core — Roster (Fichas de Identidad)
V2.75: Narrative Identity Enrichment

Maintains an evolving registry of people Ethos interacts with or hears about.
Extracts facts from conversation and builds identity cards ("fichas") for each person.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

_log = logging.getLogger(__name__)


@dataclass
class PersonCard:
    name: str
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    relationship: str = "Conocido"
    traits: list[str] = field(default_factory=list)


class Roster:
    """
    Maintains identity cards for people mentioned in conversations.
    Persists to JSON.
    """

    DEFAULT_PATH = str(Path.home() / ".ethos" / "roster.json")

    def __init__(self, storage_path: str | None = None) -> None:
        self._path = storage_path or os.environ.get("ETHOS_ROSTER_PATH", self.DEFAULT_PATH)
        self.cards: dict[str, PersonCard] = {}
        self._load()

    def _load(self) -> None:
        try:
            p = Path(self._path)
            if p.exists():
                with open(p, encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        self.cards[k] = PersonCard(**v)
        except Exception as e:
            _log.warning("Failed to load roster: %s", e)
            self.cards = {}

    def _save(self) -> None:
        p = Path(self._path)
        p.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(
                    {k: asdict(v) for k, v in self.cards.items()}, f, indent=2, ensure_ascii=False
                )
        except Exception as e:
            _log.error("Failed to save roster: %s", e)

    def update_person(self, name: str, fact: str) -> None:
        """Update or create a person card with a new fact."""
        name_key = name.strip().title()
        if not name_key:
            return

        if name_key not in self.cards:
            self.cards[name_key] = PersonCard(name=name_key)
            _log.info("[Roster] Nueva ficha creada: %s", name_key)
        else:
            self.cards[name_key].last_seen = time.time()

        # Add trait if not already present (case-insensitive deduplication)
        existing = {t.lower() for t in self.cards[name_key].traits}
        if fact.lower() not in existing and fact.strip():
            self.cards[name_key].traits.append(fact.strip())
            # Keep max 10 traits per person to prevent bloat
            if len(self.cards[name_key].traits) > 10:
                self.cards[name_key].traits = self.cards[name_key].traits[-10:]

        self._save()

    async def observe_turn(self, user_message: str, llm_client) -> None:
        """
        Background task: analyze user message for new people or facts.
        """
        # Quick heuristic to avoid calling LLM if no names likely exist
        # We look for capitalized words that aren't at the start of a sentence.
        # This is very basic but saves LLM calls.
        words = user_message.split()
        if len(words) < 2:
            return

        has_potential_names = any(w[0].isupper() for w in words[1:] if re.sub(r"[^a-zA-Z]", "", w))
        if not has_potential_names:
            return

        prompt = (
            "Analiza el siguiente mensaje del usuario y extrae información sobre PERSONAS específicas. "
            "Devuelve ÚNICAMENTE un bloque JSON válido con el siguiente formato, o una lista vacía [] si no hay personas:\n"
            '[\n  {"name": "NombreDeLaPersona", "fact": "dato importante sobre ella"}\n]\n\n'
            f"Mensaje: '{user_message}'\n\n"
            "JSON:"
        )

        try:
            response = await llm_client.chat(prompt, temperature=0.1)
            # Find JSON block
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                for item in data:
                    name = item.get("name")
                    fact = item.get("fact")
                    if name and fact:
                        self.update_person(name, fact)
        except Exception as e:
            _log.debug("[Roster] Extraction failed: %s", e)

    def get_context(self, user_message: str) -> str:
        """
        Retrieve roster facts for people mentioned in the current query.
        """
        if not self.cards:
            return ""

        mentioned = []
        msg_lower = user_message.lower()

        # Simple string matching for names
        for name, card in self.cards.items():
            if name.lower() in msg_lower:
                mentioned.append(card)

        if not mentioned:
            return ""

        lines = ["\n[FICHAS DE IDENTIDAD EN MEMORIA]:"]
        for card in mentioned:
            traits = ", ".join(card.traits) if card.traits else "Sin datos"
            lines.append(f"- {card.name}: {traits}")

        return "\n".join(lines)
