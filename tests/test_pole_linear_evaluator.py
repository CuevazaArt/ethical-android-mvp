"""Linear pole evaluator — regression vs legacy formulas (ADR 0004)."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.ethics.ethical_poles import EthicalPoles, Verdict
from src.modules.ethics.pole_linear import LinearPoleEvaluator


def test_default_linear_matches_known_scores():
    ep = EthicalPoles()
    ctx = {
        "risk": 0.1,
        "benefit": 0.5,
        "third_party_vulnerability": 0.2,
        "legality": 1.0,
    }
    c = ep.evaluate_pole("compassionate", "help_elder", ctx)
    assert c.score == 0.36
    assert c.verdict == Verdict.GOOD

    cons = ep.evaluate_pole("conservative", "help_elder", ctx)
    # 1.0*0.5 + 0.9*0.3 - 0.5*0.1
    assert cons.score == 0.72
    assert cons.verdict == Verdict.GOOD

    opt = ep.evaluate_pole("optimistic", "help_elder", ctx)
    assert opt.score == 0.63
    assert opt.verdict == Verdict.GOOD


def test_unknown_pole_falls_back():
    ep = EthicalPoles()
    r = ep.evaluate_pole("nonexistent", "x", {})
    assert r.score == 0.0
    assert r.verdict == Verdict.GRAY_ZONE
    assert "no evaluation" in r.moral


def test_kernel_pole_linear_config_env(tmp_path):
    cfg = {
        "version": 1,
        "poles": {
            "compassionate": {
                "terms": [{"feature": "const", "weight": 0.99}],
                "thresholds": {"good": 0.3, "bad": -0.3},
                "moral": {"good": "G:{action}", "bad": "B:{action}", "gray": "Z:{action}"},
            },
            "conservative": {
                "terms": [{"feature": "const", "weight": 0.0}],
                "thresholds": {"good": 0.3, "bad": -0.3},
                "moral": {"good": "g", "bad": "b", "gray": "z"},
            },
            "optimistic": {
                "terms": [{"feature": "const", "weight": 0.0}],
                "thresholds": {"good": 0.3, "bad": -0.3},
                "moral": {"good": "g", "bad": "b", "gray": "z"},
            },
        },
    }
    p = tmp_path / "poles.json"
    p.write_text(json.dumps(cfg), encoding="utf-8")
    os.environ["KERNEL_POLE_LINEAR_CONFIG"] = str(p)
    try:
        ep = EthicalPoles()
        ev = ep.evaluate_pole("compassionate", "act", {})
        assert ev.score == 0.99
        assert ev.verdict == Verdict.GOOD
    finally:
        os.environ.pop("KERNEL_POLE_LINEAR_CONFIG", None)


def test_linear_evaluator_from_dict_minimal():
    ev = LinearPoleEvaluator.from_dict(
        {
            "poles": {
                "p1": {
                    "terms": [{"feature": "risk", "weight": 1.0}],
                    "thresholds": {"good": 0.5, "bad": -0.5},
                    "moral": {"good": "g:{action}", "bad": "b", "gray": "z"},
                }
            }
        }
    )
    out = ev.evaluate("p1", "run", {"risk": 0.6})
    assert out is not None
    assert out.score == 0.6
    assert out.verdict == Verdict.GOOD
