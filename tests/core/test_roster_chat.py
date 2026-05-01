from unittest.mock import AsyncMock

import pytest

from src.core.chat import ChatEngine
from src.core.ethics import Signals


@pytest.mark.asyncio
async def test_roster_chat_continuity():
    """
    Validates that a continuous chat correctly triggers the Roster extraction
    and then injects that extracted context into subsequent turns.
    """
    engine = ChatEngine()
    # Mock LLM to return a fast dummy response for the chat
    engine.llm.chat = AsyncMock(return_value="Respuesta del LLM")

    # Mock LLM chat for the Roster observation (it must return the JSON)
    async def mock_chat(*args, **kwargs):
        prompt = args[0] if args else kwargs.get("prompt", "")
        if "extrae información sobre PERSONAS" in prompt:
            return '[{"name": "Alejandro", "fact": "le gusta el café"}]'
        return "Respuesta del LLM"

    engine.llm.chat.side_effect = mock_chat

    # Turn 1: Mention a person
    await engine.respond("Ayer salí con Alejandro", Signals())

    # Manually trigger observe_turn to bypass async background scheduling in tests
    await engine.roster.observe_turn(
        "Ayer salí con Alejandro, le gusta el café", engine.llm
    )

    # Validate Roster has the person
    assert "Alejandro" in engine.roster.cards
    assert "le gusta el café" in engine.roster.cards["Alejandro"].traits

    # Turn 2: _build_system should now include Alejandro's ficha
    system_prompt = engine._build_system("¿Te acuerdas de Alejandro?", Signals())
    assert "[FICHAS DE IDENTIDAD EN MEMORIA]" in system_prompt
    assert "- Alejandro: le gusta el café" in system_prompt
