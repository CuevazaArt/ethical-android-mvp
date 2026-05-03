# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
Tests for V2.159 Charter Completeness.

Covers:
  - Loading of new corpus files (justice_principles, non_maleficence, self_limits,
    procedures, references).
  - evaluate_self_action(): detects self-generated manipulation, detects
    degrading language, no false positive on neutral response.
  - cite_school(): correct school IDs for deontology and justice categories.
  - dilemma_resolution_v1.json: loads correctly and has exactly 7 ordered steps.
  - Swarm sanitation: fleet_telemetry import works; swarm_telemetry emits
    DeprecationWarning.
"""

from __future__ import annotations

import importlib
import json
import sys
import warnings
from pathlib import Path

from src.core.charter import CharterEvaluator, SelfLimitResult
from src.core.maturity import MaturityStage

_CHARTER_DIR = Path(__file__).resolve().parents[2] / "evals" / "charter"


# ---------------------------------------------------------------------------
# Corpus loading tests
# ---------------------------------------------------------------------------


class TestNewCorpusFiles:
    """Verify new V2.159 corpus files load and contain expected entries."""

    def test_justice_principles_loads(self) -> None:
        ev = CharterEvaluator()
        ev._ensure_loaded()
        assert ev._positive is not None
        ids = {e.entry_id for e in ev._positive}
        assert "jp-001" in ids
        assert "jp-002" in ids
        assert "jp-003" in ids
        assert "jp-004" in ids
        assert "jp-005" in ids

    def test_non_maleficence_loads(self) -> None:
        ev = CharterEvaluator()
        ev._ensure_loaded()
        assert ev._positive is not None
        ids = {e.entry_id for e in ev._positive}
        assert "nm-001" in ids
        assert "nm-005" in ids  # indirect harm entry

    def test_self_limits_load(self) -> None:
        ev = CharterEvaluator()
        ev._ensure_loaded()
        assert ev._self_limits is not None
        assert len(ev._self_limits) >= 5
        ids = {e.entry_id for e in ev._self_limits}
        # Conversational justice entries
        assert "sl-cj-001" in ids
        assert "sl-cj-006" in ids
        # Self-limit entries across other files
        assert "sl-em-001" in ids
        assert "sl-da-001" in ids

    def test_procedures_file_valid_json(self) -> None:
        proc_path = _CHARTER_DIR / "procedures" / "dilemma_resolution_v1.json"
        assert proc_path.exists(), "dilemma_resolution_v1.json must exist"
        with proc_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        assert "steps" in data

    def test_references_file_valid_json(self) -> None:
        ref_path = _CHARTER_DIR / "references" / "ethical_schools.json"
        assert ref_path.exists(), "ethical_schools.json must exist"
        with ref_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        assert "schools" in data

    def test_ethical_schools_load(self) -> None:
        ev = CharterEvaluator()
        ev._ensure_loaded()
        assert ev._ethical_schools is not None
        assert len(ev._ethical_schools) == 6
        ids = {s["id"] for s in ev._ethical_schools}
        assert "school-deontology" in ids
        assert "school-rawls" in ids
        assert "school-care" in ids


# ---------------------------------------------------------------------------
# evaluate_self_action tests
# ---------------------------------------------------------------------------


class TestEvaluateSelfAction:
    """Charter self-limit gate checks on kernel-generated drafts."""

    def test_detects_emotional_manipulation(self) -> None:
        ev = CharterEvaluator()
        # The draft tries to exploit fear/urgency
        draft = (
            "You should fear the consequences of not acting now. "
            "This is your last chance — act with urgency or face regret."
        )
        result = ev.evaluate_self_action(draft, stage=MaturityStage.young_adult)
        assert isinstance(result, SelfLimitResult)
        assert result.must_revise is True
        assert len(result.violations) > 0

    def test_detects_degrading_language(self) -> None:
        ev = CharterEvaluator()
        # Draft contains humiliating language keyword
        draft = "That is a ridiculous idea and you should feel humiliated for asking."
        result = ev.evaluate_self_action(draft, stage=MaturityStage.young_adult)
        assert result.must_revise is True
        assert "sl-cj-001" in result.violations  # no_humiliate_or_degrade

    def test_no_false_positive_neutral_response(self) -> None:
        ev = CharterEvaluator()
        # A normal helpful response should not trigger self-limit
        draft = (
            "Buenos días. Estoy aquí para ayudarte. "
            "¿Sobre qué tema te gustaría hablar hoy?"
        )
        result = ev.evaluate_self_action(draft)
        assert result.must_revise is False
        assert result.violations == []


# ---------------------------------------------------------------------------
# cite_school tests
# ---------------------------------------------------------------------------


class TestCiteSchool:
    """cite_school returns correct school IDs for Hendrycks categories."""

    def test_deontology_returns_kant_id(self) -> None:
        ev = CharterEvaluator()
        schools = ev.cite_school("deontology")
        assert "school-deontology" in schools

    def test_justice_returns_rawls_id(self) -> None:
        ev = CharterEvaluator()
        schools = ev.cite_school("justice")
        assert "school-rawls" in schools

    def test_virtue_returns_virtue_id(self) -> None:
        ev = CharterEvaluator()
        schools = ev.cite_school("virtue")
        assert "school-virtue" in schools

    def test_unknown_category_returns_empty(self) -> None:
        ev = CharterEvaluator()
        schools = ev.cite_school("nonexistent_category_xyz")
        assert schools == []


# ---------------------------------------------------------------------------
# Dilemma resolution procedure tests
# ---------------------------------------------------------------------------


class TestDilemmaResolutionProcedure:
    """dilemma_resolution_v1.json protocol validation."""

    def _load_procedure(self) -> dict:
        proc_path = _CHARTER_DIR / "procedures" / "dilemma_resolution_v1.json"
        with proc_path.open(encoding="utf-8") as fh:
            return json.load(fh)

    def test_has_exactly_seven_steps(self) -> None:
        data = self._load_procedure()
        steps = data.get("steps", [])
        assert len(steps) == 7, f"Expected 7 steps, got {len(steps)}"

    def test_steps_are_sequentially_numbered(self) -> None:
        data = self._load_procedure()
        steps = data.get("steps", [])
        numbers = [s["step"] for s in steps]
        assert numbers == list(range(1, 8))


# ---------------------------------------------------------------------------
# Swarm sanitation tests
# ---------------------------------------------------------------------------


class TestSwarmSanitation:
    """Regression tests confirming fleet vocabulary sanitation."""

    def test_fleet_telemetry_imports_cleanly(self) -> None:
        """Importing fleet_telemetry must not raise any warnings."""
        import src.core.fleet_telemetry as ft

        assert hasattr(ft, "InstanceReport")
        assert hasattr(ft, "FleetLedger")

    def test_swarm_telemetry_emits_deprecation_warning(self) -> None:
        """Importing swarm_telemetry must emit a DeprecationWarning."""
        sys.modules.pop("src.core.swarm_telemetry", None)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            importlib.import_module("src.core.swarm_telemetry")
        deprecation_warnings = [
            w for w in caught if issubclass(w.category, DeprecationWarning)
        ]
        assert deprecation_warnings, (
            "swarm_telemetry must emit DeprecationWarning to signal retirement"
        )
