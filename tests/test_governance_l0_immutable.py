"""
Regression: L0 (PreloadedBuffer) must not mutate when MockDAO / constitution drafts run.

See docs/proposals/README.md — Issue 6 plan (PLAN_IMMEDIATE_TWO_WEEKS).
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.buffer import PreloadedBuffer
from src.modules.moral_hub import (
    add_constitution_draft,
    submit_constitution_draft_for_vote,
)


def _l0_fingerprint(buf: PreloadedBuffer) -> tuple[tuple[str, str, float, bool], ...]:
    """Stable snapshot of immutable principle rows (order by name)."""
    return tuple(
        (n, p.description, p.weight, p.active)
        for n, p in sorted(buf.principles.items(), key=lambda x: x[0])
    )


def test_l0_principles_unchanged_after_draft_submit_vote_resolve():
    k = EthicalKernel(variability=False)
    fp0 = _l0_fingerprint(k.buffer)

    d = add_constitution_draft(k, 1, "Norm X", "Draft body", proposer="test")
    r = submit_constitution_draft_for_vote(k, 1, d["id"])
    assert r.get("ok") is True
    pid = r["proposal_id"]

    out = k.dao.vote(pid, "community_01", 1, True)
    assert out.get("success") is True
    res = k.dao.resolve_proposal(pid)
    assert res.get("outcome") in ("approved", "rejected", None)

    assert _l0_fingerprint(k.buffer) == fp0


def test_l0_principles_match_fresh_buffer_after_multiple_proposals():
    """DAO list growth must not alias or replace buffer.principles."""
    k = EthicalKernel(variability=False)
    fp0 = _l0_fingerprint(k.buffer)
    k.dao.create_proposal("Ad-hoc", "Description", type="ethics")
    k.dao.create_proposal("Second", "Other", type="audit")
    assert len(k.dao.proposals) >= 2
    assert _l0_fingerprint(k.buffer) == fp0
    assert _l0_fingerprint(PreloadedBuffer()) == fp0
