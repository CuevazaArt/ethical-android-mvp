"""Tests for V14 session sync digest helpers."""

from __future__ import annotations

from src.modules.session_sync_digest import merge_with_verdict_stub, v14_session_sync_record


def test_v14_session_sync_record_deterministic_shape() -> None:
    r = v14_session_sync_record("hello", biographic_digest_snippet="bio", ticket="V14.0")
    assert r["sha256_short"] == r["sha256_full"][:16]
    assert len(r["sha256_short"]) == 16
    assert r["payload"]["message"] == "hello"
    assert r["payload"]["biographic_anchor_prefix"] == "bio"


def test_merge_with_verdict_stub_has_merged_sha() -> None:
    base = v14_session_sync_record("x")
    m = merge_with_verdict_stub(base)
    assert "merged_sha256_short" in m
    assert len(m["merged_sha256_short"]) == 16
