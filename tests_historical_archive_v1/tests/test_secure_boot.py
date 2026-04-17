"""
Tests for Block 5.2: Cybersecurity (Secure Boot logic mocks).
"""

import pytest
from src.kernel import EthicalKernel
from src.modules.secure_boot import IntegrityError


def test_secure_boot_success():
    # Regular startup should pass in this environment
    kernel = EthicalKernel(llm_mode="local")
    assert kernel.boot_validator is not None


def test_secure_boot_failure_missing_file(monkeypatch):
    # Mocking compute_file_hash to simulate a failure
    from src.modules.secure_boot import SecureBoot

    def mock_verify_fail(self):
        return False

    monkeypatch.setattr(SecureBoot, "verify_integrity", mock_verify_fail)
    monkeypatch.setenv("KERNEL_IGNORE_BOOT_FAILURE", "false")

    with pytest.raises(IntegrityError):
        EthicalKernel(llm_mode="local")


def test_secure_boot_ignore_failure(monkeypatch):
    # Mocking failure but enabling the ignore flag
    from src.modules.secure_boot import SecureBoot

    def mock_verify_fail(self):
        return False

    monkeypatch.setattr(SecureBoot, "verify_integrity", mock_verify_fail)
    monkeypatch.setenv("KERNEL_IGNORE_BOOT_FAILURE", "true")

    # Should not raise
    kernel = EthicalKernel(llm_mode="local")
    assert kernel is not None
