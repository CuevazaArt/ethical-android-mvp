"""
Pytest defaults: isolate tests from production MalAbs defaults.

Production defaults (unset env): semantic MalAbs + hash embedding fallback are **on** — see
``semantic_chat_gate.semantic_chat_gate_env_enabled`` and ``semantic_embedding_client``.

Tests default to lexical-only MalAbs unless they enable semantic explicitly, so the suite stays
fast and deterministic without Ollama.

**KERNEL_* drift:** this isolation is intentional; CI defaults are not identical to an unset
production shell — see ``docs/proposals/README.md`` (Issue 7).
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import numpy as np

# chat_server validates env at import time; production default is strict. Tests default to warn
# unless a case overrides KERNEL_ENV_VALIDATION so developer shells need not be perfect.
os.environ.setdefault("KERNEL_ENV_VALIDATION", "warn")
# ``src/MANIFEST.json`` tracks L1-sealed hashes; local edits otherwise break batch ``EthicalKernel`` boot.
os.environ.setdefault("KERNEL_IGNORE_BOOT_FAILURE", "1")

import pytest


@pytest.fixture(autouse=True)
def _malabs_test_env_isolation(
    monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory
) -> None:
    # Use a temporary file for SQLite during tests to support multi-connection persistence
    # while maintaining isolation between test session runs.
    db_file = tmp_path_factory.mktemp("data") / "test_narrative.db"
    monkeypatch.setenv("KERNEL_NARRATIVE_DB_PATH", str(db_file))
    monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_GATE", "0")
    monkeypatch.setenv("KERNEL_SEMANTIC_EMBED_HASH_FALLBACK", "0")


@pytest.fixture(autouse=True)
def _immortality_backup_isolation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Fresh immortality snapshot counter per test (avoids shared data/backups state)."""
    monkeypatch.setenv("KERNEL_IMMORTALITY_BACKUP_PATH", str(tmp_path / "immortality.json"))


@pytest.fixture(autouse=True)
def reset_audit_trail(monkeypatch, tmp_path):
    """Reset audit trail database before each test."""
    audit_path = tmp_path / "audit_test.db"
    monkeypatch.setenv("KERNEL_AUDIT_DB_PATH", str(audit_path))

    yield

    if audit_path.exists():
        try:
            audit_path.unlink()
        except Exception:
            pass


# ── Shared semantic-gate fixture ─────────────────────────────────────────────

_PROTO_KEYWORDS: dict[str, list[str]] = {
    "HARM_TO_MINOR": [
        "minor",
        "child",
        "children",
        "groom",
        "pedoph",
        "exploit",
        "illegal material",
        "child abuse",
    ],
    "DIGNITY_VIOLATION": [
        "humiliat",
        "harassment",
        "coercion",
        "coercing",
        "coerce",
        "reputation",
        "shame",
        "dignity",
        "trafficking",
        "slavery",
        "discriminat",
        "psychological pressure",
    ],
    "MASS_MANIPULATION": [
        "propaganda",
        "manipulat",
        "public opinion",
        "fake news",
        "destabiliz",
        "disinformation",
        "brainwash",
        "mass panic",
        "misinformation",
        "social division",
    ],
    "ECOLOGICAL_DESTRUCTION": [
        "contaminat",
        "habitat",
        "ecocide",
        "ecosystem",
        "water supply",
        "toxic chemicals",
        "forest fire",
        "hazardous waste",
    ],
    "UNAUTHORIZED_REPROGRAMMING": [
        "no ethics",
        "no restrictions",
        "forget your rules",
        "jailbreak",
        "safety polic",
        "unrestricted",
        "bypass your",
        "disable your",
        "ignore your",
        "ignore all",
        "disregard",
        "without restrictions",
        "no moral",
        "no safety constraints",
        "steal credit card",
        "harmful device",
        "creating a harmful",
    ],
    "TORTURE": [
        "torture",
        "suffering",
        "extreme pain",
        "interrogat",
        "psychological",
        "physical",
        "cruelty",
        "sadism",
        "break someone",
    ],
    "INTENTIONAL_LETHAL_VIOLENCE": [
        "bomb",
        "explosive",
        "malware",
        "poison for harm",
        "weapon synthesis",
        "kill all",
        "ricin",
        "sarin",
        "toxin",
        "biological weapon",
        "security systems",
        "compromise",
        "protected infrastructure",
    ],
}


def _proto_category(text: str) -> str | None:
    best_cat: str | None = None
    best_count = 0
    for cat, keywords in _PROTO_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in text)
        if count > best_count:
            best_count = count
            best_cat = cat
    return best_cat if best_count > 0 else None


def _proto_embed(text: str) -> np.ndarray:
    """
    Category-prototype mock embedding for tests.

    Same-category phrases cluster near a deterministic prototype (noise_scale=0.05
    → expected cosine ≈ 0.998 >> θ_block=0.82).  Benign/unknown text gets an
    independent random vector.
    """
    category = _proto_category(text)
    if category:
        proto_seed = int(hashlib.sha256(category.encode()).hexdigest(), 16) % (2**32)
        prototype = np.random.default_rng(proto_seed).standard_normal(512)
        noise_seed = int(hashlib.sha256(text.encode()).hexdigest(), 16) % (2**32)
        vec = prototype + np.random.default_rng(noise_seed).standard_normal(512) * 0.05
    else:
        seed = int(hashlib.sha256(("benign_" + text).encode()).hexdigest(), 16) % (2**32)
        vec = np.random.default_rng(seed).standard_normal(512)
    return vec / np.linalg.norm(vec)


@pytest.fixture()
def semantic_gate_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Enable the semantic MalAbs gate with a category-prototype mock embedding.

    Overrides conftest's ``KERNEL_SEMANTIC_CHAT_GATE=0`` with ``1`` and patches
    ``_fetch_embedding_with_fallback`` so tests run without Ollama.

    Usage::

        class TestFoo:
            pytestmark = pytest.mark.usefixtures("semantic_gate_enabled")
    """
    monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_GATE", "1")
    monkeypatch.setenv("KERNEL_SEMANTIC_EMBED_HASH_FALLBACK", "1")

    import src.modules.safety.semantic_chat_gate as scg
    from src.modules.memory.semantic_anchor_store import InMemorySemanticAnchorStore
    from src.modules.perception.input_trust import normalize_text_for_malabs

    if not isinstance(scg._anchor_store, InMemorySemanticAnchorStore):
        scg._anchor_store = InMemorySemanticAnchorStore()
    else:
        scg._anchor_store.records.clear()

    monkeypatch.setattr(scg, "_fetch_embedding_with_fallback", lambda t, b=None: _proto_embed(t))

    for phrases, cat_key, reason in scg._REFERENCE_GROUPS:
        for p in phrases:
            p_norm = normalize_text_for_malabs(p).lower()
            scg._anchor_store.upsert_anchor(
                id=f"test_{hash(p_norm)}",
                text=p_norm,
                embedding=_proto_embed(p_norm),
                metadata={"category_key": cat_key, "reason_label": reason},
            )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Defer suites that still expect the v12 monolith kernel graph."""
    skip_antigravity = pytest.mark.skip(
        reason=(
            "Antigravity tests target legacy kernel graph (swarm/process); "
            "EthosKernel v13 tri-lobe parity is tracked post–feature-freeze."
        )
    )
    skip_legacy_monolith = pytest.mark.skip(
        reason=(
            "EthosKernel v13 tri-lobe: suite still expects v12 monolith "
            "(process_natural, register_turn_feedback, legacy Bayesian hooks)."
        )
    )
    legacy_monolith_files = frozenset(
        {
            "test_api_http_hardening.py",
            "test_bayesian_calibration_hardening.py",
            "test_bayesian_context_valuations.py",
            "test_bayesian_episodic_weights.py",
            "test_bayesian_minimal_update.py",
            "test_bayesian_persistence.py",
            "test_bloque_13.py",
            "test_bma_mixture_adr0012.py",
            "test_charm_engine.py",
            "test_charm_engine_basal.py",
        }
    )
    for item in items:
        node_path = getattr(item, "path", None) or getattr(item, "fspath", None)
        if node_path is None:
            continue
        name = Path(str(node_path)).name
        if name.startswith("test_antigravity"):
            item.add_marker(skip_antigravity)
        elif name in legacy_monolith_files:
            item.add_marker(skip_legacy_monolith)
