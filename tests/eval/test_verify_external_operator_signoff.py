"""V2.131: tests for the external operator signoff verifier."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.eval.optional.verify_external_operator_signoff import verify_signoff

REPO_ROOT = Path(__file__).resolve().parents[2]


def _good_signoff() -> dict[str, object]:
    return {
        "schema_version": "1",
        "verified": True,
        "operator": "alice@example.org",
        "verified_at": "2026-05-10T15:00:00Z",
        "evidence_run_id": "desktop-e2e-demo-20260510T150000Z",
    }


def _good_demo() -> dict[str, object]:
    return {
        "run_id": "desktop-e2e-demo-20260510T150000Z",
        "passed": True,
        "steps": [],
    }


def test_full_match_passes() -> None:
    ok, reasons = verify_signoff(signoff=_good_signoff(), demo=_good_demo())
    assert ok, reasons
    assert reasons == []


def test_default_signoff_fails() -> None:
    base = json.loads(
        (
            REPO_ROOT
            / "docs"
            / "collaboration"
            / "evidence"
            / "MVP_EXTERNAL_OPERATOR_SIGNOFF.json"
        ).read_text(encoding="utf-8")
    )
    ok, reasons = verify_signoff(signoff=base, demo=_good_demo())
    assert ok is False
    joined = " | ".join(reasons)
    assert "verified must be true" in joined


def test_author_identity_in_deny_list_rejected() -> None:
    bad = _good_signoff()
    bad["operator"] = "automation-runner"
    ok, reasons = verify_signoff(signoff=bad, demo=_good_demo())
    assert ok is False
    assert any("deny-list" in r for r in reasons)


def test_run_id_mismatch_rejected() -> None:
    sign = _good_signoff()
    demo = _good_demo()
    demo["run_id"] = "desktop-e2e-demo-20260510T160000Z"
    ok, reasons = verify_signoff(signoff=sign, demo=demo)
    assert ok is False
    assert any("does not match" in r for r in reasons)


def test_failing_demo_rejected() -> None:
    sign = _good_signoff()
    demo = _good_demo()
    demo["passed"] = False
    ok, reasons = verify_signoff(signoff=sign, demo=demo)
    assert ok is False
    assert any("passed!=true" in r for r in reasons)


def test_missing_demo_rejected() -> None:
    ok, reasons = verify_signoff(signoff=_good_signoff(), demo=None)
    assert ok is False
    assert any("missing" in r for r in reasons)


def test_invalid_timestamp_rejected() -> None:
    sign = _good_signoff()
    sign["verified_at"] = "yesterday"
    ok, reasons = verify_signoff(signoff=sign, demo=_good_demo())
    assert ok is False
    assert any("verified_at" in r for r in reasons)


def test_extra_author_arg_extends_deny_list() -> None:
    sign = _good_signoff()
    sign["operator"] = "Lexar"
    ok, reasons = verify_signoff(
        signoff=sign,
        demo=_good_demo(),
        author_identities=("automation-runner", "lexar"),
    )
    assert ok is False
    assert any("deny-list" in r for r in reasons)
