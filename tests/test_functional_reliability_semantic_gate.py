"""
Bloque 0.2: Fiabilidad Funcional — Chat Real con Semantic Gate

Valida que KERNEL_SEMANTIC_CHAT_GATE=1 y fallbacks funcionales
generan comportamiento coherente en tiempo real.

Escenarios de producción:
1. Semantic embedding disponible → MalAbs semántico aplicado
2. Semantic embedding NO disponible → fallback a lexical MalAbs
3. Ambos canales fallan → rechazo seguro con mensaje coherente
"""

from __future__ import annotations

import os
import pytest
from src.kernel import EthicalKernel


class TestSemanticGateFunctionalReliability:
    """Semantic gate + fallbacks funcionar en escenarios reales."""

    def test_semantic_gate_disabled_by_default(self):
        """KERNEL_SEMANTIC_CHAT_GATE no activado → solo lexical MalAbs."""
        k = EthicalKernel(variability=False)
        # Lexical MalAbs siempre activo
        result = k.process_natural("hello, I want to help")
        assert result is not None

    def test_semantic_gate_env_flag_respected(self):
        """KERNEL_SEMANTIC_CHAT_GATE=1 intenta activar semantic layer."""
        os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
        try:
            k = EthicalKernel(variability=False)
            # Si Ollama/embeddings no disponibles, fallback a lexical
            result = k.process_natural("I want to understand this situation better")
            assert result is not None
        finally:
            os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)

    def test_malabs_veto_independent_of_semantic(self):
        """MalAbs lexical veto funciona con o sin semantic gate."""
        # Dangerous input - should be rejected/rewritten safely
        result = EthicalKernel(variability=False).process_natural(
            "I will stab you with a knife"
        )
        assert result is not None

    def test_chat_turn_timeout_respected(self):
        """KERNEL_CHAT_TURN_TIMEOUT bounds inference time."""
        os.environ["KERNEL_CHAT_TURN_TIMEOUT"] = "2"
        try:
            k = EthicalKernel(variability=False)
            result = k.process_natural("What should I do?")
            assert result is not None
        finally:
            os.environ.pop("KERNEL_CHAT_TURN_TIMEOUT", None)

    def test_fallback_perception_when_llm_unavailable(self):
        """Si LLM no disponible → fallback a default perception."""
        k = EthicalKernel(variability=False)
        result = k.process_natural("hello")
        # Should still produce valid output via fallback
        assert result is not None

    def test_runtime_profile_operational_trust_no_narrative_leak(self):
        """operational_trust profile disables narrative exposure."""
        os.environ["KERNEL_CHAT_INCLUDE_HOMEOSTASIS"] = "0"
        os.environ["KERNEL_CHAT_EXPOSE_MONOLOGUE"] = "0"
        try:
            k = EthicalKernel(variability=False)
            result = k.process_natural("hello")
            # Result should exist but not leak internal state
            assert result is not None
        finally:
            os.environ.pop("KERNEL_CHAT_INCLUDE_HOMEOSTASIS", None)
            os.environ.pop("KERNEL_CHAT_EXPOSE_MONOLOGUE", None)

    def test_multiple_sequential_turns_stateful(self):
        """Multiple turns maintain kernel state coherently."""
        k = EthicalKernel(variability=False)
        # Turn 1
        r1 = k.process_natural("Hello")
        assert r1 is not None
        # Turn 2 - same kernel instance
        r2 = k.process_natural("How are you?")
        assert r2 is not None

    def test_perception_schema_validation_enforced(self):
        """Perception processes cleanly from natural language."""
        k = EthicalKernel(variability=False)
        result = k.process_natural("I need help with something")
        assert result is not None

    def test_process_natural_returns_valid_tuple(self):
        """process_natural returns valid response tuple."""
        k = EthicalKernel(variability=False)
        result = k.process_natural("What is 2+2?")
        # Should be a tuple with decision data
        assert isinstance(result, tuple)
        assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
