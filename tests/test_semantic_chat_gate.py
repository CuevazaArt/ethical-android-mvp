"""Semantic chat gate stub (ADR 0003): reserved API, no-op until implemented."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.semantic_chat_gate import (
    evaluate_semantic_chat_gate,
    semantic_chat_gate_env_enabled,
)


def test_evaluate_semantic_chat_gate_returns_none():
    assert evaluate_semantic_chat_gate("any text") is None


def test_semantic_chat_gate_env_enabled_default_off():
    os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)
    assert semantic_chat_gate_env_enabled() is False


def test_semantic_chat_gate_env_enabled_truthy():
    os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
    try:
        assert semantic_chat_gate_env_enabled() is True
    finally:
        os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)
