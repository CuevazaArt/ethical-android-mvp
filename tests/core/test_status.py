import subprocess
from unittest.mock import MagicMock, patch

from src.core.status import _check, _importable, _ollama_reachable, _run_tests


def test_check_success():
    # We use a lambda that returns True
    assert _check("Test label", lambda: True) is True


def test_check_failure():
    # We use a lambda that returns False
    assert _check("Test label", lambda: False) is False


def test_check_exception():
    def fail():
        raise Exception("Boom")

    assert _check("Test label", fail) is False


def test_importable_exists():
    assert _importable("os") is True


def test_importable_missing():
    assert _importable("non_existent_module_xyz") is False


@patch("httpx.get")
def test_ollama_reachable_ok(mock_get):
    mock_get.return_value = MagicMock(status_code=200)
    assert _ollama_reachable() is True


@patch("httpx.get")
def test_ollama_reachable_fail(mock_get):
    mock_get.return_value = MagicMock(status_code=500)
    assert _ollama_reachable() is False


@patch("httpx.get")
def test_ollama_reachable_exception(mock_get):
    mock_get.side_effect = Exception("No connection")
    assert _ollama_reachable() is False


@patch("subprocess.run")
def test_run_tests_handles_timeout(mock_run):
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="pytest", timeout=30)
    ok, summary = _run_tests()
    assert ok is False
    assert "timed out" in summary
