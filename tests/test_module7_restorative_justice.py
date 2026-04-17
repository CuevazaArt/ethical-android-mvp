"""
Tests for Módulo 7: Justicia Restaurativa y Compensación Swarm.

Bloque 7.1 — Swarm vote wired to EthosToken reparation.
Bloque 7.2 — Adversarial fingerprint mismatch triggers SlashOracle penalty.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.modules.frontier_witness import (
    FrontierWitnessManager,
    WitnessReport,
)
from src.modules.swarm_negotiator import SwarmNegotiator
from src.modules.swarm_oracle import SwarmOracle


# ─────────────────────────────────────────────────────────────
# Bloque 7.2 — Slashing
# ─────────────────────────────────────────────────────────────

def test_get_adversarial_nodes_empty_when_no_mismatch() -> None:
    mgr = FrontierWitnessManager(node_id="NODE_A")
    mgr.report_history = [
        WitnessReport(request_id="r1", witness_node="NODE_B", confidence=0.9, verified=True, signal_fingerprint="HASH_X"),
        WitnessReport(request_id="r1", witness_node="NODE_C", confidence=0.8, verified=True, signal_fingerprint="HASH_X"),
    ]
    assert mgr.get_adversarial_nodes("HASH_X") == []


def test_get_adversarial_nodes_detects_contradicting_peer() -> None:
    mgr = FrontierWitnessManager(node_id="NODE_A")
    mgr.report_history = [
        WitnessReport(request_id="r1", witness_node="NODE_B", confidence=0.9, verified=True, signal_fingerprint="HASH_X"),
        WitnessReport(request_id="r1", witness_node="NODE_LIAR", confidence=0.9, verified=True, signal_fingerprint="HASH_EVIL"),
        WitnessReport(request_id="r1", witness_node="NODE_C", confidence=0.8, verified=True, signal_fingerprint="HASH_X"),
    ]
    adversarial = mgr.get_adversarial_nodes("HASH_X")
    assert adversarial == ["NODE_LIAR"]


def test_get_adversarial_nodes_deduplicates() -> None:
    mgr = FrontierWitnessManager(node_id="NODE_A")
    mgr.report_history = [
        WitnessReport(request_id="r1", witness_node="NODE_LIAR", confidence=0.9, verified=True, signal_fingerprint="HASH_EVIL"),
        WitnessReport(request_id="r2", witness_node="NODE_LIAR", confidence=0.9, verified=True, signal_fingerprint="HASH_EVIL"),
    ]
    adversarial = mgr.get_adversarial_nodes("HASH_X")
    assert adversarial.count("NODE_LIAR") == 1


def test_get_adversarial_nodes_ignores_empty_fingerprint_peers() -> None:
    mgr = FrontierWitnessManager(node_id="NODE_A")
    # A peer that doesn't send a fingerprint should NOT be flagged
    mgr.report_history = [
        WitnessReport(request_id="r1", witness_node="NODE_SILENT", confidence=0.9, verified=True, signal_fingerprint=""),
    ]
    assert mgr.get_adversarial_nodes("HASH_X") == []


def test_get_adversarial_nodes_returns_empty_when_local_fingerprint_empty() -> None:
    mgr = FrontierWitnessManager(node_id="NODE_A")
    mgr.report_history = [
        WitnessReport(request_id="r1", witness_node="NODE_B", confidence=0.9, verified=True, signal_fingerprint="HASH_X"),
    ]
    assert mgr.get_adversarial_nodes("") == []


def test_swarm_oracle_apply_slashing_degrades_reputation() -> None:
    oracle = SwarmOracle(cache_path="/tmp/test_swarm_oracle_slash.json")
    oracle.register_interaction("NODE_LIAR", success=True)
    initial_rep = oracle.get_reputation_hint("NODE_LIAR")

    oracle.apply_slashing("NODE_LIAR", severity=0.3)
    slashed_rep = oracle.get_reputation_hint("NODE_LIAR")

    assert slashed_rep < initial_rep
    assert slashed_rep == pytest.approx(initial_rep - 0.3, abs=1e-6)


def test_slashing_pipeline_calls_oracle(tmp_path) -> None:
    """
    Integration: adversarial node detected by FrontierWitness → oracle.apply_slashing called.
    """
    mgr = FrontierWitnessManager(node_id="NODE_A")
    mgr.report_history = [
        WitnessReport(request_id="r1", witness_node="NODE_GOOD", confidence=0.9, verified=True, signal_fingerprint="HASH_OK"),
        WitnessReport(request_id="r1", witness_node="NODE_BAD", confidence=0.9, verified=True, signal_fingerprint="HASH_FAKE"),
    ]

    oracle = MagicMock(spec=SwarmOracle)
    adversarial = mgr.get_adversarial_nodes("HASH_OK")
    for node in adversarial:
        oracle.apply_slashing(node, severity=0.2)

    oracle.apply_slashing.assert_called_once_with("NODE_BAD", severity=0.2)


# ─────────────────────────────────────────────────────────────
# Bloque 7.1 — Swarm vote → EthosToken reparation
# ─────────────────────────────────────────────────────────────

def test_cast_distributed_vote_returns_consensus_on_low_risk() -> None:
    negotiator = SwarmNegotiator(node_id="NODE_A")
    peers = ["NODE_B", "NODE_C", "NODE_D"]
    result = negotiator.cast_distributed_vote(
        proposal_id="test_gray_zone",
        action="assist_human",
        signals={"risk": 0.2},
        peers=peers,
    )
    assert result is True  # low risk → all peers agree


def test_cast_distributed_vote_no_consensus_on_high_risk() -> None:
    negotiator = SwarmNegotiator(node_id="NODE_A")
    peers = ["NODE_B", "NODE_C"]
    result = negotiator.cast_distributed_vote(
        proposal_id="test_gray_zone_risky",
        action="escalate_force",
        signals={"risk": 0.9},
        peers=peers,
    )
    assert result is False  # high risk → abstain majority


def test_cast_distributed_vote_logs_to_consensus_when_agreed() -> None:
    negotiator = SwarmNegotiator(node_id="NODE_A")
    peers = ["NODE_B", "NODE_C"]
    negotiator.cast_distributed_vote(
        proposal_id="prop_safe",
        action="wave_hello",
        signals={"risk": 0.1},
        peers=peers,
    )
    # consensus_log should have an entry
    assert any(entry["proposal_id"] == "prop_safe" for entry in negotiator.state.consensus_log)


def test_reparation_issued_on_swarm_consensus(tmp_path) -> None:
    """
    Bloque 7.1 integration: when swarm reaches consensus, mock DAO receives
    issue_restorative_reparation call.
    """
    negotiator = SwarmNegotiator(node_id="NODE_A")
    negotiator.state.known_peers = {"NODE_B": {}, "NODE_C": {}}

    mock_dao = MagicMock()

    peers = list(negotiator.state.known_peers.keys())
    consensus = negotiator.cast_distributed_vote(
        proposal_id="gray_case_001",
        action="safe_action",
        signals={"risk": 0.2},
        peers=peers,
    )
    if consensus:
        mock_dao.issue_restorative_reparation(
            case_id="gray_case_001",
            recipient="community_governance_pool",
            amount=25.0,
        )

    mock_dao.issue_restorative_reparation.assert_called_once_with(
        case_id="gray_case_001",
        recipient="community_governance_pool",
        amount=25.0,
    )
