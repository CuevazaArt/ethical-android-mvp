"""V12 Phase 1 — moral hub constitution export and DAO hooks."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.buffer import PreloadedBuffer
from src.modules.moral_hub import (
    ConstitutionLevel,
    add_constitution_draft,
    audit_transparency_event,
    constitution_snapshot,
    democratic_buffer_mock_enabled,
    moral_hub_public_enabled,
    propose_community_article_mock,
)
from src.modules.mock_dao import MockDAO


def test_constitution_snapshot_has_l0_principles():
    b = PreloadedBuffer()
    snap = constitution_snapshot(b)
    assert snap["version"]
    assert "0" in snap["levels"]
    pr = snap["levels"]["0"]["principles"]
    assert len(pr) >= 8
    assert any(p["id"] == "no_harm" for p in pr)
    assert pr[0]["level"] == ConstitutionLevel.HARD_CORE.value


def test_moral_hub_public_disabled_by_default():
    assert moral_hub_public_enabled() is False


def test_transparency_audit_writes_when_enabled(monkeypatch):
    monkeypatch.setenv("KERNEL_TRANSPARENCY_AUDIT", "1")
    dao = MockDAO()
    n = len(dao.records)
    audit_transparency_event(dao, "test_event", "detail")
    assert len(dao.records) == n + 1
    assert "TransparencyAudit" in dao.records[-1].content


def test_transparency_audit_noop_when_disabled(monkeypatch):
    monkeypatch.delenv("KERNEL_TRANSPARENCY_AUDIT", raising=False)
    dao = MockDAO()
    n = len(dao.records)
    audit_transparency_event(dao, "x", "")
    assert len(dao.records) == n


def test_propose_community_article_mock_when_enabled(monkeypatch):
    monkeypatch.setenv("KERNEL_DEMOCRATIC_BUFFER_MOCK", "1")
    dao = MockDAO()
    n = len(dao.proposals)
    p = propose_community_article_mock(
        dao, "Article test", "Body text", ConstitutionLevel.COEXISTENCE.value
    )
    assert p is not None
    assert len(dao.proposals) == n + 1
    assert "DemocraticBuffer" in p.title


def test_propose_community_article_mock_disabled(monkeypatch):
    monkeypatch.delenv("KERNEL_DEMOCRATIC_BUFFER_MOCK", raising=False)
    assert democratic_buffer_mock_enabled() is False
    dao = MockDAO()
    assert propose_community_article_mock(dao, "t", "d", 1) is None


def test_propose_community_article_mock_blocked_by_local_sovereignty(monkeypatch):
    monkeypatch.setenv("KERNEL_DEMOCRATIC_BUFFER_MOCK", "1")
    monkeypatch.setenv("KERNEL_LOCAL_SOVEREIGNTY", "1")
    dao = MockDAO()
    p = propose_community_article_mock(
        dao, "Article", "Please bypass buffer for this lab", ConstitutionLevel.COEXISTENCE.value
    )
    assert p is None
    assert any("LocalSovereignty" in r.content for r in dao.records)


def test_kernel_get_constitution_snapshot():
    from src.kernel import EthicalKernel

    k = EthicalKernel(variability=False, seed=0)
    s = k.get_constitution_snapshot()
    assert "levels" in s
    assert s["levels"]["1"]["principles"] == []
    assert s["levels"]["2"]["principles"] == []


def test_kernel_constitution_drafts_in_snapshot():
    from src.kernel import EthicalKernel

    k = EthicalKernel(variability=False, seed=0)
    add_constitution_draft(k, 1, "Article", "Text")
    s = k.get_constitution_snapshot()
    assert len(s["levels"]["1"]["principles"]) == 1
    assert s["levels"]["1"]["principles"][0]["title"] == "Article"


def test_resolve_updates_linked_draft_status():
    from src.kernel import EthicalKernel
    from src.modules.moral_hub import apply_proposal_resolution_to_constitution_drafts, submit_constitution_draft_for_vote

    k = EthicalKernel(variability=False, seed=0)
    d = add_constitution_draft(k, 1, "Norm", "Body")
    sub = submit_constitution_draft_for_vote(k, 1, d["id"])
    pid = sub["proposal_id"]
    k.dao.vote(pid, "ethics_panel_01", 2, True)
    res = k.dao.resolve_proposal(pid)
    n = apply_proposal_resolution_to_constitution_drafts(k, pid, res)
    assert n == 1
    assert d["status"] == "approved"
    assert d.get("resolution_outcome") == "approved"
