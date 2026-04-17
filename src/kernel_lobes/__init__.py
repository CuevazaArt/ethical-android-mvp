# Architecture V1.5 — Triune Brain + Cerebellum Node
#
# Pipeline: observe → judge → formulate
# ─────────────────────────────────────────────────────────────────────────────
#
#   raw_input ──► PerceptiveLobe.observe()
#                 │  async HTTP + asyncio.wait_for deadline
#                 │  returns SemanticState (confidence, raw_prompt, trauma?)
#                 ▼
#              LimbicEthicalLobe.judge()
#                 │  sync CPU-only: AbsoluteEvilDetector + Bayesian penalty
#                 │  returns EthicalSentence (is_safe, veto_reason?)
#                 ▼
#              ExecutiveLobe.formulate_response()
#                 │  is_safe=False → veto string (short-circuit)
#                 │  is_safe=True  → MotivationEngine drives + monologue line
#                 ▼
#              final response str
#
#   ┌─────────────────────────────────────────┐
#   │  CerebellumNode  (daemon thread)        │
#   │  100 Hz sensor poll (battery / temp)   │
#   │  sets hardware_interrupt_event on crit │
#   └─────────────────────────────────────────┘
#
# Shared state flows top-down; lobes do NOT reference each other directly.
# CerebellumNode is independent — it signals via threading.Event only.
# ─────────────────────────────────────────────────────────────────────────────

from .cerebellum_node import CerebellumNode
from .executive_lobe import ExecutiveLobe
from .limbic_lobe import LimbicEthicalLobe
from .models import EthicalSentence, SemanticState, TimeoutTrauma
from .perception_lobe import PerceptiveLobe

__all__ = [
    "SemanticState",
    "EthicalSentence",
    "TimeoutTrauma",
    "PerceptiveLobe",
    "LimbicEthicalLobe",
    "ExecutiveLobe",
    "CerebellumNode",
]
