# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""Tests for src.core.swarm_telemetry — backward-compatibility shim.

These tests verify that the deprecated shim still exports ScoutReport and
SwarmLedger (which now alias InstanceReport and FleetLedger from
fleet_telemetry) and that importing the shim emits a DeprecationWarning.

New code should use src.core.fleet_telemetry directly.
"""

import warnings
from pathlib import Path


class TestSwarmShimDeprecation:
    """Verify the shim emits DeprecationWarning on import."""

    def test_import_emits_deprecation_warning(self) -> None:
        """Importing swarm_telemetry must raise DeprecationWarning."""
        import importlib
        import sys

        # Force a fresh import to reliably trigger the module-level warning
        sys.modules.pop("src.core.swarm_telemetry", None)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            importlib.import_module("src.core.swarm_telemetry")
        deprecation_warnings = [
            w for w in caught if issubclass(w.category, DeprecationWarning)
        ]
        assert deprecation_warnings, (
            "Expected a DeprecationWarning from swarm_telemetry"
        )
        assert "fleet_telemetry" in str(deprecation_warnings[0].message).lower()

    def test_scout_report_alias(self) -> None:
        """ScoutReport from the shim must behave like InstanceReport."""
        import sys

        sys.modules.pop("src.core.swarm_telemetry", None)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            from src.core.swarm_telemetry import ScoutReport

        r = ScoutReport(
            instance_id="test",
            model="test",
            task_summary="alias test",
        )
        assert r.total_tokens == 0
        assert r.quality_score == 0.0

    def test_swarm_ledger_alias(self, tmp_path: Path) -> None:
        """SwarmLedger from the shim must behave like FleetLedger."""
        import sys

        sys.modules.pop("src.core.swarm_telemetry", None)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            from src.core.swarm_telemetry import SwarmLedger

        ledger = SwarmLedger(path=tmp_path)
        s = ledger.summary()
        assert s.get("total_instances", -1) == 0
