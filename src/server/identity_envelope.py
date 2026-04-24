"""
[SYNC_IDENTITY] WebSocket envelope and JSON-safe identity helpers (Bloque 34.x).

Split from :mod:`src.chat_server` so Nomad/bridge routes can import
``build_sync_identity_ws_message`` without circular imports.
"""

from __future__ import annotations

import math
import os
import time
from dataclasses import asdict
from typing import Any

from src.modules.governance.nomad_identity import nomad_identity_public

from ..kernel import EthicalKernel
from ..kernel_lobes.models import GestaltSnapshot
from ..persistence.identity_manifest import IdentityManifestStore
from ..runtime.chat_feature_flags import chat_include_nomad_identity


def identity_state_public_dict(kernel: EthicalKernel) -> dict[str, Any]:
    """JSON-safe narrative identity (shared by chat turns and ``[SYNC_IDENTITY]``)."""
    idn = kernel.memory.identity
    raw = asdict(idn.state)
    out: dict[str, Any] = {}
    for k, v in raw.items():
        if k == "episode_count":
            try:
                out[k] = int(v)
            except (TypeError, ValueError):
                out[k] = 0
        elif isinstance(v, list | dict | tuple):
            out[k] = v
        else:
            try:
                fv = float(v)
                out[k] = fv if math.isfinite(fv) else 0.0
            except (TypeError, ValueError):
                out[k] = 0.0
    out["ascription"] = idn.ascription_line()
    return out


def _ws_sync_sanitize_float(
    val: Any, default: float, *, lo: float = -1e9, hi: float = 1e9
) -> float:
    try:
        x = float(val)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(x):
        return default
    return max(lo, min(hi, x))


def _bayesian_posterior_confidence(kernel: EthicalKernel) -> float | None:
    """Scalar summary of mixture sharpness for identity sync (anti-NaN)."""
    try:
        raw = getattr(kernel.bayesian, "posterior_alpha", None)
        if raw is None:
            return None
        seq = [_ws_sync_sanitize_float(x, 0.0, lo=0.0, hi=1e12) for x in raw]
        if not seq:
            return None
        s = float(sum(seq))
        if s <= 0.0 or not math.isfinite(s):
            return None
        return max(v / s for v in seq)
    except Exception:
        return None


def _narrative_recent_for_identity_sync(
    kernel: EthicalKernel, limit: int = 16
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        eps = kernel.memory.episodes[-max(1, limit) :]
    except Exception:
        return rows
    for ep in eps:
        try:
            pad = ep.affect_pad
            pad_s: list[float] | None = None
            if pad is not None and len(pad) >= 3:
                pad_s = [
                    _ws_sync_sanitize_float(pad[0], 0.0, lo=-1.0, hi=1.0),
                    _ws_sync_sanitize_float(pad[1], 0.0, lo=-1.0, hi=1.0),
                    _ws_sync_sanitize_float(pad[2], 0.0, lo=-1.0, hi=1.0),
                ]
            rows.append(
                {
                    "id": str(ep.id),
                    "timestamp": str(ep.timestamp),
                    "place": str(ep.place),
                    "event": str(ep.event_description or "")[:800],
                    "verdict": str(ep.verdict),
                    "sigma": _ws_sync_sanitize_float(ep.sigma, 0.5, lo=0.0, hi=1.0),
                    "context": str(ep.context),
                    "affect_pad": pad_s,
                }
            )
        except Exception:
            continue
    return rows


def build_sync_identity_ws_message(kernel: EthicalKernel) -> dict[str, Any]:
    """
    WebSocket envelope ``[SYNC_IDENTITY]`` (Nomad Field Test / Bloque 22.2).

    Emits a ``GestaltSnapshot``-compatible dict plus manifest and recent narrative
    rows so the Nomad PWA can align affect chrome without waiting for a turn.
    """
    t_build = time.perf_counter()
    limbic = kernel.limbic_system
    sym = getattr(limbic, "sympathetic", None)
    sigma = _ws_sync_sanitize_float(
        getattr(sym, "sigma", None) if sym is not None else None, 0.5, lo=0.0, hi=1.0
    )
    if sigma > 0.70:
        smode = "sympathetic"
    elif sigma < 0.30:
        smode = "parasympathetic"
    else:
        smode = "neutral"
    tension = max(
        _ws_sync_sanitize_float(getattr(limbic, "relational_tension", 0.0), 0.0, lo=0.0, hi=1.0),
        _ws_sync_sanitize_float(getattr(limbic, "situational_stress", 0.0), 0.0, lo=0.0, hi=1.0),
    )
    reflection = ""
    try:
        reflection = str(kernel.memory.get_reflection() or "")
    except (AttributeError, TypeError, ValueError):
        reflection = ""
    pad = [0.0, 0.0, 0.0]
    try:
        if kernel.memory.episodes:
            ap = kernel.memory.episodes[-1].affect_pad
            if ap is not None and len(ap) >= 3:
                pad = [
                    _ws_sync_sanitize_float(ap[0], 0.0, lo=-1.0, hi=1.0),
                    _ws_sync_sanitize_float(ap[1], 0.0, lo=-1.0, hi=1.0),
                    _ws_sync_sanitize_float(ap[2], 0.0, lo=-1.0, hi=1.0),
                ]
    except (AttributeError, TypeError, ValueError, IndexError):
        pad = [0.0, 0.0, 0.0]
    arc_id: str | None = None
    try:
        arc = kernel.memory.active_arc
        if arc is not None:
            arc_id = str(arc.id)
    except (AttributeError, TypeError, ValueError):
        arc_id = None
    dominant = "neutral"
    try:
        tone = kernel.memory.get_subjective_tone()
        if isinstance(tone, dict) and tone:
            best_k: str | None = None
            best_v = -1.0
            for k, v in tone.items():
                try:
                    fv = float(v)
                except (TypeError, ValueError):
                    continue
                if math.isfinite(fv) and fv > best_v:
                    best_v = fv
                    best_k = str(k)
            if best_k:
                dominant = best_k
    except (AttributeError, TypeError, ValueError, KeyError):
        dominant = "neutral"
    bc = _bayesian_posterior_confidence(kernel)
    gs = GestaltSnapshot(
        timestamp=time.time(),
        identity_reflection=reflection[:4000],
        sigma=sigma,
        sympathetic_mode=smode,
        tension_level=tension,
        pad_state=(pad[0], pad[1], pad[2]),
        dominant_archetype=dominant,
        active_arc_id=arc_id,
        social_circle="neutral_soto",
        bayesian_confidence=bc,
    )
    gestalt_dict = asdict(gs)
    gestalt_dict["pad_state"] = [pad[0], pad[1], pad[2]]
    gestalt_dict["timestamp"] = _ws_sync_sanitize_float(gs.timestamp, time.time(), lo=0.0, hi=1e12)

    manifest_path = (
        os.environ.get("KERNEL_IDENTITY_MANIFEST_PATH", "").strip() or "data/identity_manifest.json"
    )
    try:
        manifest_dict = asdict(IdentityManifestStore(path=manifest_path).manifest)
    except (OSError, TypeError, ValueError, KeyError):
        try:
            manifest_dict = asdict(
                IdentityManifestStore(path="data/identity_manifest.json").manifest
            )
        except (OSError, TypeError, ValueError, KeyError):
            manifest_dict = {}

    digest = ""
    try:
        digest = str(kernel.memory.experience_digest or "")
    except (AttributeError, TypeError, ValueError):
        digest = ""

    narrative_recent = _narrative_recent_for_identity_sync(kernel)
    try:
        ep_total = len(kernel.memory.episodes)
    except (AttributeError, TypeError):
        ep_total = 0

    identity_pub = identity_state_public_dict(kernel)
    try:
        ascription = str(kernel.memory.identity.ascription_line() or "")
    except (AttributeError, TypeError, ValueError):
        ascription = ""

    existence_digest = ""
    try:
        existence_digest = kernel.memory.identity.generate_existence_digest(
            list(kernel.memory.episodes)
        )
    except Exception:
        existence_digest = ascription
    if len(existence_digest) > 4000:
        existence_digest = existence_digest[:4000]

    payload: dict[str, Any] = {
        "gestalt_snapshot": gestalt_dict,
        "identity_manifest": manifest_dict,
        "narrative_recent": narrative_recent,
        "base_history": narrative_recent,
        "experience_digest": digest[:8000],
        "existence_digest": existence_digest,
        "identity_ascription": ascription,
        "build_latency_ms": round((time.perf_counter() - t_build) * 1000.0, 3),
    }
    envelope: dict[str, Any] = {
        "type": "[SYNC_IDENTITY]",
        "label": "[SYNC_IDENTITY]",
        "schema": "sync_identity_v1",
        "payload": payload,
        "manifest": manifest_dict,
        "birth_manifest": manifest_dict,
        "narrative_tail": narrative_recent,
        "base_history": narrative_recent,
        "gestalt": gestalt_dict,
        "gestalt_snapshot": gestalt_dict,
        "identity_reflection": reflection[:2000],
        "identity_ascription": ascription,
        "identity": identity_pub,
        "narrative_identity": identity_pub,
        "episode_total": ep_total,
    }
    if chat_include_nomad_identity():
        envelope["nomad_identity"] = nomad_identity_public(kernel)
    return envelope
