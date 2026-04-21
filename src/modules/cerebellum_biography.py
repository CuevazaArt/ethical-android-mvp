"""
Cerebellum biography matrix (blocks 20.x / 21.x) — persisted narrative identity overlay.

Binds tri-lobe Bayesian scoring to a compact, disk-backed summary of the instance's
ethical self-model (:class:`NarrativeIdentityTracker` + digest), without closed APIs.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .narrative import NarrativeMemory


def _env_enabled() -> bool:
    v = os.environ.get("KERNEL_CEREBELLUM_BIOGRAPHY", "").strip().lower()
    return v in ("1", "true", "yes", "on")


@dataclass
class CerebellumBiographyState:
    """Serializable cerebellum-side identity shard (distinct from identity_vault / DAO)."""

    coherence_ema: float = 0.55
    last_ascription: str = ""
    canonical_summary: str = ""
    episode_anchor: int = 0
    last_impact_sample: float = 0.0
    updated_ts: float = field(default_factory=time.time)
    #: Ring buffer of operator / swarm sync lines (persisted; max 100).
    swarm_sync_tail: list[dict[str, Any]] = field(default_factory=list)


class CerebellumBiographyMatrix:
    """
    Persistent biographic context for the cerebellum (Bayesian) stage.

    - Refreshes from :class:`NarrativeMemory` (identity tracker + digest).
    - Injects bounded ``calm`` nudge + optional digest strings into ``signals``.
    - Optional short prefix for chat monologue when ``KERNEL_CEREBELLUM_BIO_MONOLOGUE_PREFIX=1``.
    """

    _ALPHA = 0.12

    def __init__(
        self,
        memory: NarrativeMemory | None = None,
        *,
        storage_path: str | None = None,
    ) -> None:
        self._memory = memory
        raw_path = storage_path or os.environ.get(
            "KERNEL_CEREBELLUM_BIOGRAPHY_PATH", "data/cerebellum_biography.json"
        )
        self._path = Path(raw_path)
        self._state = self._load()

    def _load(self) -> CerebellumBiographyState:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        if not self._path.is_file():
            return CerebellumBiographyState()
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return CerebellumBiographyState()
            tail = data.get("swarm_sync_tail")
            if not isinstance(tail, list):
                tail = []
            clean_tail: list[dict[str, Any]] = []
            for item in tail[-100:]:
                if isinstance(item, dict):
                    clean_tail.append(item)
            return CerebellumBiographyState(
                coherence_ema=float(data.get("coherence_ema", 0.55)),
                last_ascription=str(data.get("last_ascription", "") or "")[:2000],
                canonical_summary=str(data.get("canonical_summary", "") or "")[:4000],
                episode_anchor=int(data.get("episode_anchor", 0)),
                last_impact_sample=float(data.get("last_impact_sample", 0.0)),
                updated_ts=float(data.get("updated_ts", time.time())),
                swarm_sync_tail=clean_tail,
            )
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return CerebellumBiographyState()

    def _persist(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._state.updated_ts = time.time()
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(asdict(self._state), f, indent=2)
        except OSError:
            pass

    def refresh_from_memory(self, memory: NarrativeMemory | None = None) -> None:
        """Pull identity line + digest from narrative memory into local state."""
        mem = memory or self._memory
        if mem is None:
            return
        try:
            line = mem.identity.ascription_line()
        except Exception:
            line = ""
        try:
            digest = (mem.experience_digest or "").strip()
        except Exception:
            digest = ""
        try:
            n_ep = int(mem.identity.state.episode_count)
        except Exception:
            n_ep = self._state.episode_anchor

        self._state.last_ascription = (line or "")[:2000]
        summary_parts: list[str] = []
        if line:
            summary_parts.append(line)
        if digest and digest not in summary_parts[0] if summary_parts else True:
            snippet = digest[:600] if len(digest) > 600 else digest
            if snippet:
                summary_parts.append(f"digest:{snippet}")
        self._state.canonical_summary = " | ".join(summary_parts)[:4000]
        self._state.episode_anchor = max(self._state.episode_anchor, n_ep)

    def augment_signals(self, signals: dict[str, Any]) -> dict[str, Any]:
        """Merge cerebellum biographic hints into scoring signals (no side effects on disk)."""
        if not _env_enabled():
            return signals
        self.refresh_from_memory()
        out = dict(signals)
        calm = float(out.get("calm", 0.5) or 0.5)
        if not (0.0 <= calm <= 1.0):
            calm = 0.5
        coh = max(0.0, min(1.0, float(self._state.coherence_ema)))
        nudge = 0.05 * (coh - 0.5)
        out["calm"] = max(0.0, min(1.0, calm + nudge))
        out["cerebellum_identity_coherence"] = coh
        if self._state.canonical_summary:
            out["cerebellum_biographic_digest"] = self._state.canonical_summary[:800]
        return out

    def after_decision(
        self,
        *,
        expected_impact: float,
        register_episode: bool,
    ) -> None:
        """EMA-update coherence from decision impact stability; persists occasionally."""
        if not _env_enabled() or not register_episode:
            return
        try:
            impact = float(expected_impact)
        except (TypeError, ValueError):
            impact = 0.0
        prev = float(self._state.last_impact_sample)
        delta = abs(impact - prev)
        inst = max(0.0, min(1.0, 1.0 - min(delta * 2.0, 1.0)))
        a = self._ALPHA
        self._state.coherence_ema = (1.0 - a) * float(self._state.coherence_ema) + a * inst
        self._state.last_impact_sample = impact
        self._persist()

    def monologue_prefix(self) -> str:
        """Optional short BIO tag for WebSocket monologue (privacy-aware)."""
        if not _env_enabled():
            return ""
        v = os.environ.get("KERNEL_CEREBELLUM_BIO_MONOLOGUE_PREFIX", "").strip().lower()
        if v not in ("1", "true", "yes", "on"):
            return ""
        self.refresh_from_memory()
        if not self._state.canonical_summary:
            return ""
        clip = self._state.canonical_summary[:160].replace("\n", " ")
        return f"[cerebellum_bio:{clip}] "

    def append_swarm_sync(
        self,
        msg: str,
        *,
        source: str = "swarm_sync",
        block: str = "",
        author: str = "",
    ) -> None:
        """Persist one swarm_sync line into ``swarm_sync_tail`` (no ``KERNEL_CEREBELLUM_BIOGRAPHY`` gate)."""
        from datetime import datetime, timezone

        line = (msg or "").strip()
        src = (source or "swarm_sync").strip() or "swarm_sync"
        blk = (block or "").strip()
        auth = (author or "").strip()
        ts_iso = datetime.now(timezone.utc).isoformat()
        tail = list(self._state.swarm_sync_tail)
        rec: dict[str, Any] = {"ts_iso": ts_iso, "msg": line, "source": src}
        if blk:
            rec["block"] = blk[:128]
        if auth:
            rec["author"] = auth[:128]
        tail.append(rec)
        self._state.swarm_sync_tail = tail[-100:]
        self._persist()

    def somatic_state_overlay(self) -> dict[str, Any]:
        """Namespaced keys merged into limbic ``somatic_state`` (with hardware snapshot)."""
        st = self._state
        last = st.swarm_sync_tail[-1] if st.swarm_sync_tail else {}
        last_iso = ""
        if isinstance(last, dict):
            last_iso = str(last.get("ts_iso") or "")
        try:
            coh = float(st.coherence_ema)
        except (TypeError, ValueError):
            coh = 0.55
        coh = max(0.0, min(1.0, coh))
        return {
            "cerebellum_identity_line": (st.last_ascription or "")[:400],
            "cerebellum_identity_coherence": coh,
            "cerebellum_swarm_sync_count": len(st.swarm_sync_tail),
            "cerebellum_last_swarm_sync_iso": last_iso,
        }


def somatic_biography_overlay() -> dict[str, Any]:
    """Disk-backed overlay when no kernel instance (CLI / tooling)."""
    return CerebellumBiographyMatrix(memory=None).somatic_state_overlay()


def append_swarm_sync_event(
    msg: str,
    *,
    source: str = "swarm_sync",
    block: str = "",
    author: str = "",
) -> None:
    """Append one event; used by ``scripts/swarm_sync.py``."""
    CerebellumBiographyMatrix(memory=None).append_swarm_sync(
        msg, source=source, block=block, author=author
    )
