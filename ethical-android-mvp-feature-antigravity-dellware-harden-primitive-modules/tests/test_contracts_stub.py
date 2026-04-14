"""contracts/ tree: README + stub Solidity exist (no solc required)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_contracts_readme_and_stub_present():
    readme = ROOT / "contracts" / "README.md"
    stub = ROOT / "contracts" / "stubs" / "PlaceholderEthOracleStub.sol"
    assert readme.is_file()
    assert stub.is_file()
    text = stub.read_text(encoding="utf-8")
    assert "PlaceholderEthOracleStub" in text
    assert "NotImplemented" in text or "revert" in text.lower()
