"""
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
"""

from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
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