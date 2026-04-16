"""temporal_sync integer coercion and mypy-safe public JSON (chat_server)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.chat_server import _chat_turn_to_jsonable, _coerce_public_int
from src.kernel import ChatTurnResult, EthicalKernel
from src.modules.llm_layer import VerbalResponse


@pytest.mark.parametrize(
    "value,default,non_negative,expected",
    [
        (None, 0, False, 0),
        (42, 0, False, 42),
        (True, 0, False, 0),
        (False, 0, False, 0),
        (3.7, 0, False, 3),
        (-2.1, 0, True, 0),
        (" 15 ", 0, False, 15),
        ("bad", 99, False, 99),
        (float("nan"), 0, True, 0),
        (float("inf"), 0, True, 0),
    ],
)
def test_coerce_public_int(value: object, default: int, non_negative: bool, expected: int) -> None:
    assert _coerce_public_int(value, default=default, non_negative=non_negative) == expected


def test_temporal_sync_coerces_malformed_public_dict() -> None:
    """Bad values from to_public_dict() never break JSON; non-numeric ms fall back to 0."""

    class _BadTemporal:
        def to_public_dict(self) -> dict[str, object]:
            return {
                "sync_schema": "temporal_sync_v1",
                "turn_index": "-3",
                "processor_elapsed_ms": "x",
                "turn_delta_ms": float("nan"),
                "wall_clock_unix_ms": None,
                "local_network_sync_ready": False,
                "dao_sync_ready": False,
            }

    k = EthicalKernel(variability=False, seed=1)
    r = ChatTurnResult(
        response=VerbalResponse(message="ok", tone="calm", hax_mode="", inner_voice=""),
        path="light",
        temporal_context=_BadTemporal(),  # type: ignore[arg-type]
    )
    out = _chat_turn_to_jsonable(r, k)
    ts = out["temporal_sync"]
    assert ts["turn_index"] == 0
    assert ts["processor_elapsed_ms"] == 0
    assert ts["turn_delta_ms"] == 0
    assert ts["sync_schema"] == "temporal_sync_v1"
