"""Test core boundary imports and packaging.

Verifies the core policy tier is cleanly importable as a subpackage.
See docs/proposals/CORE_DECISION_CHAIN.md § core vs theater.
"""

import pytest


def test_core_imports():
    """Test that core modules can be imported from src.core subpackage."""
    try:
        from src.core import (
            AbsoluteEvilDetector,
            EthicalPoles,
            LocusModule,
            PreloadedBuffer,
            SigmoidWill,
            SympatheticModule,
            UchiSotoModule,
            WeightedEthicsScorer,
        )
    except ImportError as e:
        pytest.fail(f"Failed to import core modules: {e}")

    # Verify they are the expected classes
    assert AbsoluteEvilDetector is not None
    assert PreloadedBuffer is not None
    assert WeightedEthicsScorer is not None
    assert EthicalPoles is not None
    assert SigmoidWill is not None
    assert SympatheticModule is not None
    assert LocusModule is not None
    assert UchiSotoModule is not None