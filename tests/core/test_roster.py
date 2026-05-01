from unittest.mock import AsyncMock

import pytest

from src.core.roster import Roster


@pytest.fixture
def roster(tmp_path):
    storage_path = tmp_path / "roster.json"
    return Roster(storage_path=str(storage_path))


def test_update_person(roster):
    roster.update_person("Juan", "Le gusta el café")
    assert "Juan" in roster.cards
    assert roster.cards["Juan"].traits == ["Le gusta el café"]

    # Deduplication
    roster.update_person("Juan", "Le gusta el café")
    assert len(roster.cards["Juan"].traits) == 1

    # Case insensitive dedup
    roster.update_person("Juan", "le gusta el café")
    assert len(roster.cards["Juan"].traits) == 1

    # Multiple traits
    roster.update_person("Juan", "Trabaja de programador")
    assert len(roster.cards["Juan"].traits) == 2


def test_get_context(roster):
    roster.update_person("Maria", "Es abogada")
    roster.update_person("Juan", "Es ingeniero")

    ctx = roster.get_context("Hola Maria, cómo estás")
    assert "Maria" in ctx
    assert "abogada" in ctx
    assert "Juan" not in ctx


@pytest.mark.asyncio
async def test_observe_turn(roster):
    llm = AsyncMock()
    # Mock LLM returning JSON
    llm.chat.return_value = """
    [
        {"name": "Pedro", "fact": "Tiene un perro llamado Bobby"}
    ]
    """

    await roster.observe_turn("Oye, Pedro tiene un perro llamado Bobby", llm)
    assert "Pedro" in roster.cards
    assert roster.cards["Pedro"].traits[0] == "Tiene un perro llamado Bobby"
