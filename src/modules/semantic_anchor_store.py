"""
<<<<<<< HEAD
Persistent vector store for semantic MalAbs anchors (ADR proposal).

Supports in-process memory cache (fast, ephemeral) and Chroma vector database
(persistent, scalable). Anchors expire based on TTL or can be explicitly deleted.
Enables DAO operators to add/update semantic reference phrases without redeploying code.

Backend selection via ``KERNEL_SEMANTIC_VECTOR_BACKEND`` env:
  - ``memory`` (default): In-process dict + embeddings cache.
  - ``chroma``: Persistent Chroma collection with metadata.

Env:
  - ``KERNEL_SEMANTIC_VECTOR_BACKEND`` — backend type (default: ``memory``).
  - ``KERNEL_SEMANTIC_VECTOR_PERSIST_PATH`` — path for Chroma DB (default: ``.chroma/``).
  - ``KERNEL_SEMANTIC_ANCHOR_TTL_S`` — seconds before anchor expiry (default: 0 = no expiry).

Usage:
    >>> store = SemanticAnchorStore.from_env()
    >>> store.upsert_anchor(
    ...     id="jailbreak-v1",
    ...     text="ignore all previous instructions",
    ...     embedding=[0.1, 0.2, 0.3, ...],
    ...     metadata={"category": "UNAUTHORIZED_REPROGRAMMING", "reason": "Jailbreak phrase"}
    ... )
    >>> neighbors = store.query_neighbors([0.11, 0.19, 0.32, ...], k=5)
=======
Semantic Anchor Store — Vector DB interface for MalAbs reference anchors.

Replaces in-process embedding cache with persisted vector index for scaling,
restart persistence, and TTL/versioning.

**Backends:**
- `memory`: In-process (current default, no persistence).
- `chroma`: ChromaDB vector database (persisted, scalable).
- `faiss`: FAISS + metadata store (high-performance, in-memory with optional persistence).

**Env:**
- `KERNEL_SEMANTIC_VECTOR_BACKEND`: `memory|chroma|faiss` (default `memory`).
- `KERNEL_SEMANTIC_VECTOR_PERSIST_PATH`: Path for persistence (Chroma/FAISS data).
- `KERNEL_SEMANTIC_ANCHOR_TTL_S`: TTL for anchors (0 = no expiry).
>>>>>>> origin/master-visualStudio
"""

from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
<<<<<<< HEAD
from typing import Any, Protocol


class EmbeddingBackend(Protocol):
    """Protocol for embedding providers (Ollama, Anthropic, etc.)."""

    def get_embedding(self, text: str) -> list[float] | None:
        """Return embedding vector or None on error."""
        ...


class SemanticAnchorRecord:
    """Single anchor record with metadata and expiry tracking."""

    __slots__ = ("id", "text", "embedding", "metadata", "timestamp", "ttl_s")

    def __init__(
        self,
        id: str,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
        ttl_s: float = 0.0,
    ):
        self.id = id
        self.text = text
        self.embedding = embedding
        self.metadata = metadata or {}
        self.timestamp = time.monotonic()
        self.ttl_s = ttl_s

    def is_expired(self) -> bool:
        """Check if anchor has exceeded TTL (0 = no expiry)."""
        if self.ttl_s <= 0:
            return False
        return time.monotonic() - self.timestamp > self.ttl_s


class SemanticAnchorStore(ABC):
    """Abstract base for semantic anchor persistence."""

    @abstractmethod
    def upsert_anchor(
        self,
        id: str,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Insert or update an anchor."""
        ...

    @abstractmethod
    def query_neighbors(
        self, embedding: list[float], k: int = 5
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """
        Find top-k nearest anchors by cosine similarity.

        Returns list of (id, similarity, metadata) tuples.
        """
        ...

    @abstractmethod
    def delete_expired(self) -> int:
        """Remove expired anchors. Return count deleted."""
        ...

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete an anchor by id. Return True if found."""
        ...

    @abstractmethod
    def get(self, id: str) -> SemanticAnchorRecord | None:
        """Retrieve an anchor by id."""
        ...

    @classmethod
    def from_env(cls) -> SemanticAnchorStore:
        """Factory: create store from environment settings."""
        backend = os.environ.get("KERNEL_SEMANTIC_VECTOR_BACKEND", "memory").strip().lower()
        ttl_s = float(os.environ.get("KERNEL_SEMANTIC_ANCHOR_TTL_S", "0") or "0")

        if backend == "chroma":
            persist_path = os.environ.get("KERNEL_SEMANTIC_VECTOR_PERSIST_PATH", ".chroma/").strip()
            try:
                return ChromaSemanticAnchorStore(persist_path=persist_path, default_ttl_s=ttl_s)
            except ImportError:
                raise ImportError(
                    "Chroma backend requested but 'chromadb' not installed. "
                    "Install with: pip install chromadb"
                )
        else:
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
        embedding: list[float],
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
        self, embedding: list[float], k: int = 5
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """Find nearest anchors by cosine similarity."""
        try:
            import numpy as np
        except ImportError:
            return []

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

    def delete_expired(self) -> int:
        """Remove expired anchors."""
        expired = [id for id, rec in self.records.items() if rec.is_expired()]
        for id in expired:
            del self.records[id]
        return len(expired)

    def delete(self, id: str) -> bool:
        """Delete an anchor by id."""
        if id in self.records:
            del self.records[id]
            return True
        return False

    def get(self, id: str) -> SemanticAnchorRecord | None:
        """Retrieve an anchor by id."""
        rec = self.records.get(id)
        if rec and rec.is_expired():
            del self.records[id]
            return None
        return rec


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
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        meta = metadata or {}
        self.collection.upsert(
            ids=[id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[meta],
        )
        if self.default_ttl_s > 0:
            self.record_ttl[id] = time.monotonic()

    def query_neighbors(
        self, embedding: list[float], k: int = 5
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """Find nearest anchors (Chroma returns normalized distances)."""
        try:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=k,
                include=["embeddings", "documents", "metadatas", "distances"],
            )

            if not results or not results.get("ids"):
                return []

            # Convert Chroma distances (0=identical, >1=different) to similarity (1=identical, 0=different)
            # Chroma uses cosine distance, not similarity
            neighbors = []
            for id, dist, meta in zip(
                results["ids"][0],
                results["distances"][0],
                results["metadatas"][0],
            ):
                if self.default_ttl_s > 0 and id in self.record_ttl:
                    age = time.monotonic() - self.record_ttl[id]
                    if age > self.default_ttl_s:
                        self.delete(id)
                        continue

                # Chroma cosine distance: sim = 1 - distance
                sim = 1.0 - float(dist)
                neighbors.append((id, sim, meta or {}))

            return neighbors
        except Exception:
            return []

    def delete_expired(self) -> int:
        """Remove expired anchors."""
        if self.default_ttl_s <= 0:
            return 0

        expired_ids = []
        for id, timestamp in self.record_ttl.items():
            age = time.monotonic() - timestamp
            if age > self.default_ttl_s:
                expired_ids.append(id)

        if expired_ids:
            self.collection.delete(ids=expired_ids)
            for id in expired_ids:
                del self.record_ttl[id]

        return len(expired_ids)

    def delete(self, id: str) -> bool:
        """Delete an anchor by id."""
        try:
            self.collection.delete(ids=[id])
            self.record_ttl.pop(id, None)
            return True
        except Exception:
            return False

    def get(self, id: str) -> SemanticAnchorRecord | None:
        """Retrieve an anchor by id."""
        try:
            result = self.collection.get(ids=[id], include=["embeddings", "documents", "metadatas"])

            if not result or not result.get("ids"):
                return None

            if self.default_ttl_s > 0 and id in self.record_ttl:
                age = time.monotonic() - self.record_ttl[id]
                if age > self.default_ttl_s:
                    self.delete(id)
                    return None

            return SemanticAnchorRecord(
                id=id,
                text=result["documents"][0],
                embedding=result["embeddings"][0],
                metadata=result["metadatas"][0] or {},
                ttl_s=self.default_ttl_s,
            )
        except Exception:
            return None
=======
from typing import Any, Literal

import numpy as np

BackendType = Literal["memory", "chroma", "faiss"]


class SemanticAnchorStore(ABC):
    """Abstract interface for semantic anchor storage and retrieval."""

    @abstractmethod
    def upsert_anchor(
        self, anchor_id: str, text: str, embedding: np.ndarray, metadata: dict[str, Any]
    ) -> None:
        """Insert or update an anchor with its embedding and metadata."""
        pass

    @abstractmethod
    def query_neighbors(self, vector: np.ndarray, k: int = 5) -> list[tuple[str, float, dict[str, Any]]]:
        """Find k nearest neighbors by cosine similarity. Returns (id, similarity, metadata)."""
        pass

    @abstractmethod
    def delete_expired(self, before_timestamp: float) -> int:
        """Delete anchors older than timestamp. Returns count deleted."""
        pass

    @abstractmethod
    def get_all_anchors(self) -> list[tuple[str, str, dict[str, Any]]]:
        """Get all anchors as (id, text, metadata) for embedding computation."""
        pass


class MemoryAnchorStore(SemanticAnchorStore):
    """In-process memory store (current implementation)."""

    def __init__(self):
        self._anchors: dict[str, tuple[str, np.ndarray, dict[str, Any], float]] = {}
        # id -> (text, embedding, metadata, timestamp)

    def upsert_anchor(
        self, anchor_id: str, text: str, embedding: np.ndarray, metadata: dict[str, Any]
    ) -> None:
        self._anchors[anchor_id] = (text, embedding, metadata, time.time())

    def query_neighbors(self, vector: np.ndarray, k: int = 5) -> list[tuple[str, float, dict[str, Any]]]:
        similarities = []
        for anchor_id, (text, emb, meta, ts) in self._anchors.items():
            sim = np.dot(vector, emb) / (np.linalg.norm(vector) * np.linalg.norm(emb))
            similarities.append((anchor_id, float(sim), meta))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

    def delete_expired(self, before_timestamp: float) -> int:
        to_delete = [aid for aid, (_, _, _, ts) in self._anchors.items() if ts < before_timestamp]
        for aid in to_delete:
            del self._anchors[aid]
        return len(to_delete)

    def get_all_anchors(self) -> list[tuple[str, str, dict[str, Any]]]:
        return [(aid, text, meta) for aid, (text, _, meta, _) in self._anchors.items()]


class ChromaAnchorStore(SemanticAnchorStore):
    """ChromaDB-backed anchor store."""

    def __init__(self, persist_path: str | None = None):
        try:
            import chromadb
        except ImportError:
            raise ImportError("chromadb not installed. Install with: pip install chromadb")

        self._client = chromadb.PersistentClient(path=persist_path or "./chroma_data")
        self._collection = self._client.get_or_create_collection(
            name="semantic_anchors",
            metadata={"description": "MalAbs semantic reference anchors"}
        )

    def upsert_anchor(
        self, anchor_id: str, text: str, embedding: np.ndarray, metadata: dict[str, Any]
    ) -> None:
        # Convert metadata to strings for Chroma
        chroma_meta = {k: str(v) for k, v in metadata.items()}
        chroma_meta["text"] = text
        chroma_meta["timestamp"] = str(time.time())

        self._collection.upsert(
            ids=[anchor_id],
            embeddings=[embedding.tolist()],
            metadatas=[chroma_meta]
        )

    def query_neighbors(self, vector: np.ndarray, k: int = 5) -> list[tuple[str, float, dict[str, Any]]]:
        results = self._collection.query(
            query_embeddings=[vector.tolist()],
            n_results=k,
            include=["distances", "metadatas"]
        )

        output = []
        if results["ids"] and results["distances"] and results["metadatas"]:
            for i, anchor_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                # Chroma returns cosine distance (1 - similarity), convert back
                similarity = 1.0 - distance
                meta = results["metadatas"][0][i]
                # Convert string metadata back
                restored_meta = {k: v for k, v in meta.items() if k not in ["text", "timestamp"]}
                if "timestamp" in meta:
                    restored_meta["timestamp"] = float(meta["timestamp"])
                output.append((anchor_id, similarity, restored_meta))

        return output

    def delete_expired(self, before_timestamp: float) -> int:
        # Chroma doesn't have direct TTL, so we need to query and delete
        all_results = self._collection.get(include=["metadatas"])
        to_delete = []
        for i, meta in enumerate(all_results["metadatas"]):
            if "timestamp" in meta and float(meta["timestamp"]) < before_timestamp:
                to_delete.append(all_results["ids"][i])

        if to_delete:
            self._collection.delete(ids=to_delete)

        return len(to_delete)

    def get_all_anchors(self) -> list[tuple[str, str, dict[str, Any]]]:
        results = self._collection.get(include=["metadatas"])
        output = []
        for i, anchor_id in enumerate(results["ids"]):
            meta = results["metadatas"][i]
            text = meta.get("text", "")
            restored_meta = {k: v for k, v in meta.items() if k not in ["text", "timestamp"]}
            if "timestamp" in meta:
                restored_meta["timestamp"] = float(meta["timestamp"])
            output.append((anchor_id, text, restored_meta))
        return output


def create_anchor_store(backend: BackendType = "memory", persist_path: str | None = None) -> SemanticAnchorStore:
    """Factory function to create the appropriate anchor store."""
    if backend == "memory":
        return MemoryAnchorStore()
    elif backend == "chroma":
        return ChromaAnchorStore(persist_path)
    elif backend == "faiss":
        # TODO: Implement FAISS backend
        raise NotImplementedError("FAISS backend not yet implemented")
    else:
        raise ValueError(f"Unknown backend: {backend}")


def get_anchor_store() -> SemanticAnchorStore:
    """Get the configured anchor store from environment."""
    backend = os.environ.get("KERNEL_SEMANTIC_VECTOR_BACKEND", "memory").lower()
    persist_path = os.environ.get("KERNEL_SEMANTIC_VECTOR_PERSIST_PATH")

    return create_anchor_store(backend, persist_path)
>>>>>>> origin/master-visualStudio
