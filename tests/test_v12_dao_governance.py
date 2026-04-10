"""V12.3 — off-chain DAO vote pipeline (MockDAO + moral_hub + snapshot)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.moral_hub import (
    add_constitution_draft,
    dao_governance_api_enabled,
    proposal_to_public,
    submit_constitution_draft_for_vote,
)
from src.persistence import extract_snapshot, apply_snapshot


def test_submit_constitution_draft_for_vote_creates_proposal():
    k = EthicalKernel(variability=False)
    d = add_constitution_draft(k, 1, "Norm X", "Body text", proposer="tester")
    r = submit_constitution_draft_for_vote(k, 1, d["id"])
    assert r.get("ok") is True
    pid = r["proposal_id"]
    assert any(p.id == pid for p in k.dao.proposals)
    assert d["status"] == "voting"
    assert d["dao_proposal_id"] == pid


def test_submit_constitution_draft_for_vote_idempotent():
    k = EthicalKernel(variability=False)
    d = add_constitution_draft(k, 2, "T", "B")
    r1 = submit_constitution_draft_for_vote(k, 2, d["id"])
    r2 = submit_constitution_draft_for_vote(k, 2, d["id"])
    assert r1["proposal_id"] == r2["proposal_id"]
    assert r2.get("already_submitted") is True


def test_quadratic_vote_on_submitted_draft_proposal():
    k = EthicalKernel(variability=False)
    d = add_constitution_draft(k, 1, "T", "B")
    r = submit_constitution_draft_for_vote(k, 1, d["id"])
    pid = r["proposal_id"]
    out = k.dao.vote(pid, "community_01", 1, True)
    assert out["success"] is True
    res = k.dao.resolve_proposal(pid)
    assert res["outcome"] in ("approved", "rejected")


def test_proposal_to_public_weighted_totals():
    from src.modules.mock_dao import MockDAO

    dao = MockDAO()
    p = dao.create_proposal("x", "y", type="ethics")
    dao.vote(p.id, "community_01", 1, True)
    pub = proposal_to_public(dao.proposals[-1])
    assert pub["id"] == p.id
    assert pub["weighted_votes_for"] > 0


def test_dao_governance_env_default_off():
    assert dao_governance_api_enabled() is False


def test_dao_governance_env_on(monkeypatch):
    monkeypatch.setenv("KERNEL_MORAL_HUB_DAO_VOTE", "1")
    assert dao_governance_api_enabled() is True


def test_dao_proposals_persist_in_snapshot():
    k1 = EthicalKernel(variability=False)
    k1.dao.create_proposal("P", "D", type="ethics")
    snap = extract_snapshot(k1)
    assert len(snap.dao_proposals) >= 1

    k2 = EthicalKernel(variability=False)
    apply_snapshot(k2, snap)
    assert len(k2.dao.proposals) == len(k1.dao.proposals)
    assert k2.dao.proposals[-1].id == k1.dao.proposals[-1].id
