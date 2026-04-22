"""MockDAO audit ledger fingerprinting (distributed justice DJ-BL-01)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.governance.mock_dao import MockDAO
from src.modules.governance.mock_dao_audit_replay import (
    audit_record_to_public_dict,
    fingerprint_audit_ledger,
)


def test_fingerprint_stable_for_same_sequence() -> None:
    d = MockDAO()
    d.register_audit("decision", "alpha")
    d.register_audit("escalation", "beta", episode_id="ep1")
    fp = fingerprint_audit_ledger(d.records)
    assert len(fp) == 64
    fp2 = fingerprint_audit_ledger(d.records)
    assert fp == fp2


def test_fingerprint_differs_when_order_differs() -> None:
    d = MockDAO()
    d.register_audit("decision", "first")
    d.register_audit("decision", "second")
    fp_ordered = fingerprint_audit_ledger(d.records)
    rev = list(reversed(d.records))
    assert fingerprint_audit_ledger(rev) != fp_ordered


def test_fingerprint_from_dict_rows_matches_records() -> None:
    d = MockDAO()
    d.register_audit("alert", "x")
    from_records = fingerprint_audit_ledger(d.records)
    rows = [audit_record_to_public_dict(r) for r in d.records]
    from_dicts = fingerprint_audit_ledger(rows)
    assert from_records == from_dicts


def test_compare_script_matching_tmp_files(tmp_path) -> None:
    import subprocess

    p1 = tmp_path / "a.json"
    p2 = tmp_path / "b.json"
    payload = (
        '[{"id":"AUD-0001","type":"decision","content":"c","timestamp":"t","episode_id":null}]'
    )
    p1.write_text(payload, encoding="utf-8")
    p2.write_text(payload, encoding="utf-8")
    root = os.path.join(os.path.dirname(__file__), "..")
    r = subprocess.run(
        [
            sys.executable,
            "scripts/eval/verify_mock_dao_audit_replay.py",
            str(p1),
            "--compare",
            str(p2),
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    assert "match" in r.stdout
