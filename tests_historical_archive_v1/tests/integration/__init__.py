"""
tests/integration/ — cross-tier integration tests (ADR 0016 Axis D1).

Tests here exercise the full kernel → decision → narrative chain with
realistic signal combinations, verifying invariants at tier boundaries.
They run without Ollama (lexical MalAbs + mock LLM).

See docs/adr/0016-consolidation-before-dao-and-field-tests.md Axis D1.
"""
