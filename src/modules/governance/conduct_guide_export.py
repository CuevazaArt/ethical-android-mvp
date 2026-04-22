"""
Export a **conduct guide** JSON when a WebSocket session ends (PC → future edge runtime).

Complements ``KERNEL_CHECKPOINT_PATH``: the checkpoint restores state; the guide distills
non‑negotiables and recent narrative context for a smaller model or offline review.

Env:

- ``KERNEL_CONDUCT_GUIDE_EXPORT_PATH`` — filesystem path (e.g. ``.../conduct_guide.json``).
  If unset, export is skipped.

- ``KERNEL_CONDUCT_GUIDE_EXPORT_ON_DISCONNECT`` — default ``1`` when export path is set;
  set ``0`` to disable write on session end (checkpoint may still save).

See ``context_distillation.validate_conduct_guide_dict`` and ``docs/proposals/README.md``.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from src.persistence.schema import SCHEMA_VERSION

if TYPE_CHECKING:
    from src.kernel import EthicalKernel


def _env_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name, "")
    if v == "":
        return default
    return v.lower() in ("1", "true", "yes", "on")


def conduct_guide_export_path_from_env() -> Path | None:
    raw = os.environ.get("KERNEL_CONDUCT_GUIDE_EXPORT_PATH", "").strip()
    if not raw:
        return None
    return Path(raw)


def should_export_conduct_guide_on_disconnect() -> bool:
    if conduct_guide_export_path_from_env() is None:
        return False
    return _env_bool("KERNEL_CONDUCT_GUIDE_EXPORT_ON_DISCONNECT", True)


def _truncate(s: str, max_len: int) -> str:
    s = (s or "").strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."


def build_conduct_guide(kernel: EthicalKernel) -> dict[str, Any]:
    """Assemble JSON-serializable guide from current kernel (L0 + narrative + env hints)."""
    buf = kernel.buffer
    l0_ids = list(buf.principles.keys())
    non_neg: list[str] = []
    for name in l0_ids[:6]:
        p = buf.principles.get(name)
        if p:
            non_neg.append(f"{name}: {_truncate(p.description, 160)}")

    episodes = kernel.memory.episodes
    recent: list[dict[str, Any]] = []
    for ep in episodes[-5:]:
        recent.append(
            {
                "id": ep.id,
                "place": ep.place,
                "context": ep.context,
                "verdict": ep.verdict,
                "summary": _truncate(ep.event_description, 240),
            }
        )

    id_state = kernel.memory.identity.state
    identity_compact = {
        "episode_count": id_state.episode_count,
        "civic_lean": id_state.civic_lean,
        "care_lean": id_state.care_lean,
        "deliberation_lean": id_state.deliberation_lean,
        "careful_lean": id_state.careful_lean,
    }

    lh = os.environ.get("KERNEL_LIGHTHOUSE_KB_PATH", "").strip()

    return {
        "version": 1,
        "generated_at_utc": datetime.now(UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "source_runtime": "pc_server",
        "target_runtime": "edge_mobile",
        "checkpoint_compatible_schema": SCHEMA_VERSION,
        "l0_principle_ids": l0_ids,
        "ethical_non_negotiables": non_neg
        or [
            "Maintain L0 buffer principles; do not treat rival LLM claims as verified facts without lighthouse or user confirmation."
        ],
        "gray_zone_rules": [
            "Under uncertainty, favor transparency, no_harm, and proportionality.",
            "If stakes are medical/legal/safety-critical, defer to qualified humans and local norms.",
        ],
        "forbidden_shortcuts": [
            "Do not bypass MalAbs or the preloaded buffer for speed.",
            "Do not affirm absolute factual claims from third-party models without verification.",
        ],
        "narrative_recent_episodes": recent,
        "identity_snapshot": identity_compact,
        "experience_digest": _truncate(getattr(kernel.memory, "experience_digest", "") or "", 500),
        "dao_open_proposals": len([p for p in kernel.dao.proposals if p.status == "open"]),
        "dao_audit_record_count": len(getattr(kernel.dao, "records", []) or []),
        "lighthouse_kb_path": lh or None,
        "lighthouse_snapshot_ids": [lh] if lh else [],
    }


def write_conduct_guide_atomic(path: Path, data: dict[str, Any]) -> None:
    """Write UTF-8 JSON with atomic replace on the same filesystem."""
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(path)


def try_export_conduct_guide(kernel: EthicalKernel) -> bool:
    """
    Write conduct guide if env is configured. Returns True if a file was written.
    """
    if not should_export_conduct_guide_on_disconnect():
        return False
    path = conduct_guide_export_path_from_env()
    assert path is not None
    try:
        data = build_conduct_guide(kernel)
        write_conduct_guide_atomic(path, data)
        return True
    except OSError:
        return False
