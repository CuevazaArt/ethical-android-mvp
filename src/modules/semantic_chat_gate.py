"""
Optional semantic similarity gate for **chat text** (future; ADR 0003).

Intended to complement :meth:`AbsoluteEvilDetector.evaluate_chat_text` with embedding-based
signals — **not** to replace MalAbs on structured actions or the kernel pipeline.

Default: **inactive**. :func:`evaluate_semantic_chat_gate` returns ``None`` until a concrete
implementation is merged (see ``docs/LLM_STACK_OLLAMA_VS_HF.md``).

Env: ``KERNEL_SEMANTIC_CHAT_GATE`` — ``1`` / ``true`` / ``yes`` / ``on`` reserved for when
the implementation exists; currently does not alter behavior elsewhere.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .absolute_evil import AbsoluteEvilResult


def semantic_chat_gate_env_enabled() -> bool:
    """True if operator opted into the semantic gate path (implementation may still no-op)."""
    v = os.environ.get("KERNEL_SEMANTIC_CHAT_GATE", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def evaluate_semantic_chat_gate(_text: str) -> Optional["AbsoluteEvilResult"]:
    """
    Reserved for embedding-based screening. Returning ``None`` means: defer to substring MalAbs.

    When implemented, callers (e.g. ``evaluate_chat_text``) may chain: semantic → substring.
    """
    return None
