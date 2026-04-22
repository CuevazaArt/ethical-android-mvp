"""Smoke tests for LLM backend adapters and public alias names."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.cognition.llm_backends import (
    HttpJsonLLMBackend,
    HTTPRemote,
    MockBackend,
    OllamaLLMBackend,
    OllamaRemote,
)


def test_public_aliases_match_implementations() -> None:
    assert OllamaRemote is OllamaLLMBackend
    assert HTTPRemote is HttpJsonLLMBackend
    m = MockBackend(completion_text="{}")
    assert m.is_available() is True
    assert m.completion("", "") == "{}"
