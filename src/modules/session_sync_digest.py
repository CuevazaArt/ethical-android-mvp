"""
V14 session sync — deterministic digest tying an operator message to the biographic
identity anchor (Cerebellum narrative matrix).

Used by :mod:`scripts.swarm_sync` for offline session handoff; no network I/O.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def v14_session_sync_record(
    message: str,
    *,
    biographic_digest_snippet: str = "",
    ticket: str = "V14.0",
) -> dict[str, Any]:
    """
    Build a canonical JSON-serializable record and SHA-256 fingerprints.

    ``biographic_digest_snippet`` should be a short prefix or hash of
    :meth:`NarrativePersistence.load_identity_digest` when available (may be empty).
    """
    ts = datetime.now(timezone.utc).isoformat()
    payload = {
        "v": 1,
        "ticket": (ticket or "V14.0")[:32],
        "ts_utc": ts,
        "message": (message or "")[:4000],
        "biographic_anchor_prefix": (biographic_digest_snippet or "")[:512],
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    return {
        "payload": payload,
        "sha256_short": digest[:16],
        "sha256_full": digest,
    }


def merge_with_verdict_stub(
    session_record: dict[str, Any],
    *,
    episode_id: str = "v14-sync",
    verdict: str = "session_handoff",
    ethical_score: float = 0.0,
    context: str = "cerebellum_biographic_matrix",
) -> dict[str, Any]:
    """Attach swarm stub verdict digest for lab-stable comparison (optional)."""
    from .swarm_peer_stub import verdict_digest_v1

    vd = verdict_digest_v1(episode_id, verdict, ethical_score, context)
    merged = {
        "session": session_record,
        "verdict_stub": vd,
    }
    raw = json.dumps(merged, sort_keys=True, ensure_ascii=True).encode("utf-8")
    h = hashlib.sha256(raw).hexdigest()
    return {"merged": merged, "merged_sha256_short": h[:16], "merged_sha256_full": h}
