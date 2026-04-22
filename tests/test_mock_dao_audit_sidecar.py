"""Optional KERNEL_AUDIT_SIDECAR_PATH mirror for MockDAO audit rows."""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.governance.mock_dao import MockDAO


def test_register_audit_appends_sidecar_jsonl(monkeypatch: pytest.MonkeyPatch):
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        path = f.name
    try:
        monkeypatch.setenv("KERNEL_AUDIT_SIDECAR_PATH", path)
        d = MockDAO()
        d.register_audit("decision", "hello audit")
        with open(path, encoding="utf-8") as rf:
            line = rf.readline().strip()
        assert '"type": "decision"' in line
        assert "hello audit" in line
    finally:
        monkeypatch.delenv("KERNEL_AUDIT_SIDECAR_PATH", raising=False)
        try:
            os.unlink(path)
        except OSError:
            pass
