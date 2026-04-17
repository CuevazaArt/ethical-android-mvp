"""
Lock ``docs/proposals/PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md`` to the same **default**
θ_block / θ_allow numerals as ``semantic_chat_gate`` constants.

`tests/test_semantic_chat_gate.py` already asserts the constants; this test ensures the
evidence posture doc cannot drift without an intentional doc+code update together.
"""

from __future__ import annotations

from pathlib import Path

from src.modules.semantic_chat_gate import (
    DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
    DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
)

_REPO = Path(__file__).resolve().parents[1]


def test_proposal_doc_mentions_same_defaults_as_code():
    text = (_REPO / "docs/proposals/PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md").read_text(
        encoding="utf-8"
    )
    assert "engineering priors" in text.lower() or "engineering prior" in text.lower()
    # Proposal explicitly discusses example alternatives; require our shipped defaults appear.
    assert "0.82" in text
    assert "0.45" in text
    assert DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD == 0.82
    assert DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD == 0.45
