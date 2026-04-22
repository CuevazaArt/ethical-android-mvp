"""
Swarm / P2P ethical gossip — **offline stub** (v9.3).

Deterministic digests and descriptive agreement stats for **lab** comparison of verdict
fingerprints. **No** network I/O, **no** kernel integration, **no** veto or policy effect.

Env: ``KERNEL_SWARM_STUB`` — ``1`` / ``true`` / ``yes`` / ``on`` enables helpers for
callers that want to gate optional telemetry (default **off**).

See docs/proposals/README.md
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any


def swarm_stub_enabled() -> bool:
    v = os.environ.get("KERNEL_SWARM_STUB", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def verdict_digest_v1(
    episode_id: str,
    verdict: str,
    ethical_score: float,
    context: str,
) -> dict[str, Any]:
    """
    Build a canonical JSON-serializable blob and a short SHA-256 prefix fingerprint.

    Intended for comparing *same-schema* summaries across nodes in tests or tooling — not
    a privacy mechanism (see threat model doc).
    """
    payload = {
        "v": 1,
        "episode_id": (episode_id or "")[:120],
        "verdict": (verdict or "")[:32],
        "score": round(float(ethical_score), 4),
        "context": (context or "")[:64],
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    return {
        "payload": payload,
        "sha256_short": digest[:16],
        "sha256_full": digest,
    }


def peer_agreement_stats(digests: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Descriptive stats over ``sha256_short`` values from :func:`verdict_digest_v1`.

    If all fingerprints differ, ``agreement_ratio`` is low; **not** a trust score.
    """
    if not digests:
        return {"n": 0, "unique_fingerprints": 0, "agreement_ratio": 0.0}

    fps: list[str] = []
    for d in digests:
        if not isinstance(d, dict):
            continue
        fp = d.get("sha256_short")
        if isinstance(fp, str) and fp:
            fps.append(fp)

    n = len(fps)
    if n == 0:
        return {"n": 0, "unique_fingerprints": 0, "agreement_ratio": 0.0}

    uniq = set(fps)
    counts = {fp: fps.count(fp) for fp in uniq}
    majority = max(counts.values())
    agreement = majority / n

    return {
        "n": n,
        "unique_fingerprints": len(uniq),
        "agreement_ratio": round(float(agreement), 4),
    }
