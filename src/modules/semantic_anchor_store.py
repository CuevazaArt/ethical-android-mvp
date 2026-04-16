"""
Semantic Anchor Store — Vector DB interface for MalAbs reference anchors.

Supports in-process memory cache (fast, ephemeral) and Chroma vector database
(persistent, scalable). Anchors expire based on TTL or can be explicitly deleted.
Enables DAO operators to add/update semantic reference phrases without redeploying code.

**Backends:**
- `memory` (default): In-process dict + embeddings cache.
- `chroma`: Persistent Chroma collection with metadata.

**Env:**
- `KERNEL_SEMANTIC_VECTOR_BACKEND` — backend type (default: `memory`).
- `KERNEL_SEMANTIC_VECTOR_PERSIST_PATH` — path for Chroma DB (default: `.chroma/`).
- `KERNEL_SEMANTIC_ANCHOR_TTL_S` — seconds before anchor expiry (default: 0 = no expiry).
"""

from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from typing import Any, cast

import numpy as np


class SemanticAnchorRecord:
    """Single anchor record with metadata and expiry tracking."""

    __slots__ = ("id", "text", "embedding", "metadata", "timestamp", "ttl_s")

    def __init__(
        self,
        id: str,
        text: str,
        embedding: list[float] | np.ndarray,
        metadata: dict[str, Any] | None = None,
        ttl_s: float = 0.0,
    ):
        self.id = id
        self.text = text
        self.embedding = embedding
        self.metadata = metadata or {}
        self.timestamp = time.monotonic()
        self.ttl_s = ttl_s

    def is_expired(self, cutoff: float | None = None) -> bool:
        """Check if anchor has exceeded TTL (0 = no expiry)."""
        if self.ttl_s <= 0:
            return False
        # If absolute cutoff provided (time.time()), compare against wall clock
        # Otherwise use time.monotonic() logic from construction
        if cutoff is not None:
            # Note: mixing monotonic and wall clock is risky, but we use wall clock for deletion
            return time.time() > cutoff
        return time.monotonic() - self.timestamp > self.ttl_s


class SemanticAnchorStore(ABC):
    """Abstract interface for semantic anchor storage and retrieval."""

    @abstractmethod
    def upsert_anchor(
        self,
        id: str,
        text: str,
        embedding: list[float] | np.ndarray,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Insert or update an anchor."""
        ...

    @abstractmethod
    def query_neighbors(
        self, embedding: list[float] | np.ndarray, k: int = 5
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """Find k nearest neighbors by cosine similarity. Returns (id, similarity, metadata)."""
        ...

    @abstractmethod
    def delete_expired(self, before_timestamp: float | None = None) -> int:
        """Delete anchors older than timestamp. Returns count deleted."""
        ...

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete an anchor by id. Return True if found."""
        ...

    @abstractmethod
    def get(self, id: str) -> SemanticAnchorRecord | None:
        """Retrieve an anchor by id."""
        ...

    @abstractmethod
    def get_all_anchors(self) -> list[tuple[str, str, dict[str, Any]]]:
        """List non-expired anchors as ``(id, text, metadata)`` tuples."""

    @classmethod
    def from_env(cls) -> SemanticAnchorStore:
        """Build a store from ``KERNEL_SEMANTIC_*`` environment variables."""
        backend = os.environ.get("KERNEL_SEMANTIC_VECTOR_BACKEND", "memory").strip().lower()
        ttl_s = float(os.environ.get("KERNEL_SEMANTIC_ANCHOR_TTL_S", "0") or "0")
        if backend == "chroma":
            persist_path = os.environ.get("KERNEL_SEMANTIC_VECTOR_PERSIST_PATH", ".chroma/").strip()
            return ChromaSemanticAnchorStore(persist_path=persist_path, default_ttl_s=ttl_s)
        return InMemorySemanticAnchorStore(default_ttl_s=ttl_s)


class InMemorySemanticAnchorStore(SemanticAnchorStore):
    """Fast, ephemeral in-process store (no persistence)."""

    def __init__(self, default_ttl_s: float = 0.0):
        self.records: dict[str, SemanticAnchorRecord] = {}
        self.default_ttl_s = default_ttl_s

    def upsert_anchor(
        self,
        id: str,
        text: str,
        embedding: list[float] | np.ndarray,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.records[id] = SemanticAnchorRecord(
            id=id,
            text=text,
            embedding=embedding,
            metadata=metadata,
            ttl_s=self.default_ttl_s,
        )

    def query_neighbors(
        self, embedding: list[float] | np.ndarray, k: int = 5
    ) -> list[tuple[str, float, dict[str, Any]]]:
        query_vec = np.asarray(embedding, dtype=np.float64)
        if query_vec.size == 0 or not np.all(np.isfinite(query_vec)):
            return []

        query_norm = float(np.linalg.norm(query_vec))
        if query_norm < 1e-12:
            return []

        query_vec = query_vec / query_norm
        sims: list[tuple[str, float, dict[str, Any]]] = []

        for rec in self.records.values():
            if rec.is_expired():
                continue

            anchor_vec = np.asarray(rec.embedding, dtype=np.float64)
            if anchor_vec.size == 0 or anchor_vec.shape != query_vec.shape:
                continue

            try:
                anchor_norm = float(np.linalg.norm(anchor_vec))
                if anchor_norm < 1e-12:
                    continue
                anchor_vec = anchor_vec / anchor_norm
                sim = float(np.dot(query_vec, anchor_vec))
                sims.append((rec.id, sim, rec.metadata))
            except (TypeError, ValueError):
                continue

        sims.sort(key=lambda x: x[1], reverse=True)
        return sims[:k]

    def delete_expired(self, before_timestamp: float | None = None) -> int:
        expired = [id for id, rec in self.records.items() if rec.is_expired(before_timestamp)]
        for id in expired:
            del self.records[id]
        return len(expired)

    def delete(self, id: str) -> bool:
        if id in self.records:
            del self.records[id]
            return True
        return False

    def get(self, id: str) -> SemanticAnchorRecord | None:
        rec = self.records.get(id)
        if rec and rec.is_expired():
            del self.records[id]
            return None
        return rec

    def get_all_anchors(self) -> list[tuple[str, str, dict[str, Any]]]:
        out: list[tuple[str, str, dict[str, Any]]] = []
        for rec in list(self.records.values()):
            if rec.is_expired():
                continue
            meta = dict(rec.metadata or {})
            out.append((rec.id, rec.text, meta))
        return out


class ChromaSemanticAnchorStore(SemanticAnchorStore):
    """Persistent Chroma vector store (requires chromadb package)."""

    def __init__(self, persist_path: str = ".chroma/", default_ttl_s: float = 0.0):
        import chromadb

        os.makedirs(persist_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name="semantic_anchors",
            metadata={"hnsw:space": "cosine"},
        )
        self.default_ttl_s = default_ttl_s
        self.record_ttl: dict[str, float] = {}

    def upsert_anchor(
        self,
        id: str,
        text: str,
        embedding: list[float] | np.ndarray,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        emb_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
        meta = metadata or {}
        # Chroma requires string/int/float metadata
        chroma_meta = {
            k: (v if isinstance(v, str | int | float | bool) else str(v)) for k, v in meta.items()
        }
        chroma_meta["text"] = text
        chroma_meta["timestamp"] = time.time()

        self.collection.upsert(
            ids=[id],
            embeddings=[emb_list],
            documents=[text],
            metadatas=[chroma_meta],
        )
        if self.default_ttl_s > 0:
            self.record_ttl[id] = time.monotonic()

    def query_neighbors(
        self, embedding: list[float] | np.ndarray, k: int = 5
    ) -> list[tuple[str, float, dict[str, Any]]]:
        emb_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
        try:
            raw_q = self.collection.query(
                query_embeddings=[emb_list],
                n_results=k,
                include=cast(Any, ["embeddings", "documents", "metadatas", "distances"]),
            )
            results: dict[str, Any] = cast(dict[str, Any], raw_q)
            ids_outer = results.get("ids")
            if not isinstance(ids_outer, list) or not ids_outer:
                return []
            row_ids = ids_outer[0]
            if not isinstance(row_ids, list) or not row_ids:
                return []
            dists_outer = results.get("distances")
            metas_outer = results.get("metadatas")
            dist_row: list[Any] = []
            if isinstance(dists_outer, list) and dists_outer and isinstance(dists_outer[0], list):
                dist_row = dists_outer[0]
            meta_row: list[Any] = []
            if isinstance(metas_outer, list) and metas_outer and isinstance(metas_outer[0], list):
                meta_row = metas_outer[0]

            neighbors: list[tuple[str, float, dict[str, Any]]] = []
            for i, row_id in enumerate(row_ids):
                dist = dist_row[i] if i < len(dist_row) else 1.0
                meta_raw = meta_row[i] if i < len(meta_row) else {}
                meta = meta_raw if isinstance(meta_raw, dict) else {}
                sim = 1.0 - float(dist)
                restored_meta = {k: v for k, v in meta.items() if k not in ["text", "timestamp"]}
                neighbors.append((str(row_id), sim, restored_meta))

            return neighbors
        except Exception:
            return []

    def delete_expired(self, before_timestamp: float | None = None) -> int:
        cutoff = before_timestamp or (
            time.time() - self.default_ttl_s if self.default_ttl_s > 0 else None
        )
        if cutoff is None:
            return 0

        # Query all and filter
        raw_g = self.collection.get(include=cast(Any, ["metadatas"]))
        all_results: dict[str, Any] = cast(dict[str, Any], raw_g)
        ids_list = all_results.get("ids")
        metas_list = all_results.get("metadatas")
        if not isinstance(ids_list, list) or not isinstance(metas_list, list):
            return 0
        to_delete: list[Any] = []
        for i, meta in enumerate(metas_list):
            if not isinstance(meta, dict):
                continue
            if "timestamp" in meta and float(meta["timestamp"]) < cutoff:
                if i < len(ids_list):
                    to_delete.append(ids_list[i])

        if to_delete:
            self.collection.delete(ids=to_delete)
        return len(to_delete)

    def delete(self, id: str) -> bool:
        try:
            raw_e = self.collection.get(ids=[id], include=cast(Any, []))
            existing = cast(dict[str, Any], raw_e)
            if not existing.get("ids"):
                return False
            self.collection.delete(ids=[id])
            self.record_ttl.pop(id, None)
            return True
        except Exception:
            return False

    def get(self, id: str) -> SemanticAnchorRecord | None:
        try:
            raw_r = self.collection.get(
                ids=[id], include=cast(Any, ["embeddings", "documents", "metadatas"])
            )
            result = cast(dict[str, Any], raw_r)
            if not result.get("ids"):
                return None
            docs = result.get("documents")
            metas = result.get("metadatas")
            embs = result.get("embeddings")
            meta: dict[str, Any] = {}
            if isinstance(metas, list) and metas and isinstance(metas[0], dict):
                meta = metas[0] or {}
            doc = ""
            if isinstance(docs, list) and docs:
                doc = str(docs[0] or "")
            emb_val: list[float] | np.ndarray
            if isinstance(embs, list) and embs:
                emb_val = cast(Any, embs[0])
            else:
                emb_val = np.array([], dtype=np.float64)
            return SemanticAnchorRecord(
                id=id,
                text=doc,
                embedding=emb_val,
                metadata={k: v for k, v in meta.items() if k not in ["text", "timestamp"]},
                ttl_s=self.default_ttl_s,
            )
        except Exception:
            return None

    def get_all_anchors(self) -> list[tuple[str, str, dict[str, Any]]]:
        try:
            raw_a = self.collection.get(include=cast(Any, ["documents", "metadatas"]))
            all_results = cast(dict[str, Any], raw_a)
            ids_a = all_results.get("ids")
            if not isinstance(ids_a, list) or not ids_a:
                return []
            out: list[tuple[str, str, dict[str, Any]]] = []
            for i, aid in enumerate(ids_a):
                docs = all_results.get("documents") or []
                metas = all_results.get("metadatas") or []
                doc = docs[i] if i < len(docs) else ""
                meta = metas[i] if i < len(metas) else {}
                meta = meta or {}
                restored = {k: v for k, v in meta.items() if k not in ("text", "timestamp")}
                out.append((aid, doc or "", restored))
            return out
        except Exception:
            return []


def create_anchor_store(
    backend: str = "memory",
    *,
    default_ttl_s: float = 0.0,
    persist_path: str | None = None,
) -> SemanticAnchorStore:
    """Explicit-backend factory for tests and scripts. Production code uses :func:`get_anchor_store`."""
    backend = (backend or "memory").strip().lower()
    ttl_s = float(default_ttl_s or 0.0)
    if backend == "chroma":
        path = (
            persist_path
            if persist_path is not None
            else os.environ.get("KERNEL_SEMANTIC_VECTOR_PERSIST_PATH", ".chroma/").strip()
        )
        return ChromaSemanticAnchorStore(persist_path=path, default_ttl_s=ttl_s)
    if backend == "memory":
        return InMemorySemanticAnchorStore(default_ttl_s=ttl_s)
    raise ValueError(f"Unknown semantic anchor backend: {backend!r}")


def get_anchor_store() -> SemanticAnchorStore:
    """Factory: create store from environment settings."""
    return SemanticAnchorStore.from_env()
