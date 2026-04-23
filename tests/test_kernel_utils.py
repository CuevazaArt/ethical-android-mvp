"""Unit tests for :mod:`src.kernel_utils` (MINOR_CONTRIBUTIONS_BACKLOG §5)."""

import math

import pytest

from src.kernel_utils import (
    _MAX_PERCEPTION_PARALLEL_ENV_WORKERS,
    format_proactive_candidate_line,
    kernel_dao_as_mock,
    kernel_env_float,
    kernel_env_int,
    kernel_env_truthy,
    kernel_mixture_scorer,
    perception_coercion_u_value,
    perception_parallel_workers,
)
from src.modules.bayesian_engine import BayesianEngine
from src.modules.dao_orchestrator import DAOOrchestrator
from src.modules.mock_dao import MockDAO
from src.modules.weighted_ethics_scorer import WeightedEthicsScorer


def test_kernel_env_truthy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_T", "1")
    assert kernel_env_truthy("TEST_T") is True
    monkeypatch.setenv("TEST_T", "0")
    assert kernel_env_truthy("TEST_T") is False
    monkeypatch.setenv("TEST_T", "yes")
    assert kernel_env_truthy("TEST_T") is True


def test_kernel_env_int_invalid_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_I", "not-an-int")
    assert kernel_env_int("TEST_I", 7) == 7
    monkeypatch.setenv("TEST_I", "42")
    assert kernel_env_int("TEST_I", 7) == 42
    monkeypatch.delenv("TEST_I", raising=False)
    assert kernel_env_int("TEST_I", 7) == 7


def test_kernel_env_int_scientific_or_floatish_string(monkeypatch: pytest.MonkeyPatch) -> None:
    """Finite float text that int() rejects still yields a truncated int when unambiguously numeric."""
    monkeypatch.setenv("TEST_I", "1e2")
    assert kernel_env_int("TEST_I", 0) == 100
    monkeypatch.setenv("TEST_I", "3.0")
    assert kernel_env_int("TEST_I", 0) == 3
    monkeypatch.setenv("TEST_I", "-2.1")
    assert kernel_env_int("TEST_I", 0) == -2


def test_kernel_env_int_nonfinite_float_string_falls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    d = 9
    for val in ("nan", "inf", "-inf", "1e400"):
        monkeypatch.setenv("TEST_INF", val)
        assert kernel_env_int("TEST_INF", d) == d


def test_kernel_env_float_invalid_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_F", "x")
    assert kernel_env_float("TEST_F", 0.5) == 0.5
    monkeypatch.setenv("TEST_F", "1.25")
    assert math.isclose(kernel_env_float("TEST_F", 0.5), 1.25)


def test_kernel_env_float_nonfinite_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    d = 12.0
    for val in ("nan", "inf", "-inf", "NaN", "+Inf"):
        monkeypatch.setenv("TEST_FNF", val)
        assert kernel_env_float("TEST_FNF", d) == d


def test_perception_parallel_workers_respects_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    for k in ("KERNEL_PERCEPTION_PARALLEL", "KERNEL_PERCEPTION_PARALLEL_WORKERS"):
        monkeypatch.delenv(k, raising=False)
    assert perception_parallel_workers() == 0
    monkeypatch.setenv("KERNEL_PERCEPTION_PARALLEL", "1")
    w = perception_parallel_workers()
    assert 2 <= w <= 8
    monkeypatch.setenv("KERNEL_PERCEPTION_PARALLEL_WORKERS", "3")
    assert perception_parallel_workers() == 3


def test_perception_parallel_workers_env_capped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KERNEL_PERCEPTION_PARALLEL", "1")
    monkeypatch.setenv("KERNEL_PERCEPTION_PARALLEL_WORKERS", "99999")
    assert perception_parallel_workers() == _MAX_PERCEPTION_PARALLEL_ENV_WORKERS


def test_perception_coercion_u_value() -> None:
    assert perception_coercion_u_value(None) is None
    assert perception_coercion_u_value(0.4) == pytest.approx(0.4)
    assert perception_coercion_u_value(float("nan")) is None
    assert perception_coercion_u_value(1.5) == pytest.approx(1.0)
    assert perception_coercion_u_value("not") is None


def test_perception_coercion_u_value_rejects_bool() -> None:
    assert perception_coercion_u_value(True) is None
    assert perception_coercion_u_value(False) is None


def test_format_proactive_candidate_line_smoke() -> None:
    class A:
        name = "n"
        description = "d"
        estimated_impact = 0.1
        confidence = 0.8

    out = format_proactive_candidate_line(A())
    assert "n" in out and "0.100" in out


def test_format_proactive_candidate_line_bool_impact_is_not_numeric() -> None:
    class B:
        name = "x"
        description = "y"
        estimated_impact = True
        confidence = 0.5

    out = format_proactive_candidate_line(B())
    assert "impact=0.000" in out
    assert "conf=0.500" in out


def test_kernel_dao_as_mock_plain_and_orchestrator() -> None:
    plain = MockDAO()
    assert kernel_dao_as_mock(plain) is plain
    orch = DAOOrchestrator()
    assert kernel_dao_as_mock(orch) is orch.local_dao


def test_kernel_mixture_scorer_bayesian_or_facade() -> None:
    be = BayesianEngine()
    assert kernel_mixture_scorer(be) is be.scorer
    ws = WeightedEthicsScorer()
    assert kernel_mixture_scorer(ws) is ws


def test_kernel_module_reexports_match_kernel_utils() -> None:
    """
    Guard against reintroducing duplicate `def` bodies in :mod:`src.kernel` that shadow
    :mod:`src.kernel_utils` imports (Bloque 0.1.10 / Backlog §5).
    """
    import src.kernel as kernel_mod
    from src import kernel_utils

    assert kernel_mod._format_proactive_candidate_line is kernel_utils.format_proactive_candidate_line
    assert kernel_mod._kernel_env_float is kernel_utils.kernel_env_float
    assert kernel_mod._kernel_env_int is kernel_utils.kernel_env_int
    assert kernel_mod._kernel_env_truthy is kernel_utils.kernel_env_truthy
    assert kernel_mod._perception_parallel_workers is kernel_utils.perception_parallel_workers
    assert kernel_mod.kernel_dao_as_mock is kernel_utils.kernel_dao_as_mock
    assert kernel_mod.kernel_mixture_scorer is kernel_utils.kernel_mixture_scorer
