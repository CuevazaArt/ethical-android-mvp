#!/usr/bin/env python3
"""
V14 swarm hand-off — persiste en ``CerebellumBiographyMatrix`` (JSON) + JSONL local.

Sin APIs cerradas; sin red. Ver ``src/modules/cerebellum_biography.append_swarm_sync_event``.

Usage::

    python scripts/swarm_sync.py --msg '...' --block 20.0 --author Cursor
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.modules.cerebellum_biography import append_swarm_sync_event  # noqa: E402
from src.modules.llm_layer import resolve_llm_mode  # noqa: E402
from src.modules.session_sync_digest import v14_session_sync_record  # noqa: E402


def _biographic_snippet_from_disk() -> str:
    """Prefijo corto desde ``cerebellum_biography.json`` (sin arrancar el kernel)."""
    raw = os.environ.get("KERNEL_CEREBELLUM_BIOGRAPHY_PATH", "").strip() or "data/cerebellum_biography.json"
    p = Path(raw)
    if not p.is_file():
        return ""
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            s = str(data.get("canonical_summary") or "").strip()
            return s[:512] if s else ""
    except (OSError, json.JSONDecodeError, TypeError):
        pass
    return ""


def _somatic_biographic_anchor() -> dict[str, object] | None:
    """JSON escrito por :meth:`CerebellumNode.update_biographic_anchor` tras episodios registrados."""
    raw = os.environ.get("KERNEL_CEREBELLUM_BIOGRAPHIC_PATH", "").strip() or "data/cerebellum_biographic_anchor.json"
    p = Path(raw)
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Swarm sync — cola de biografía + auditoría V14 (huella LLM local)."
    )
    ap.add_argument("--block", default="", help="Id de bloque (ej. 20.0)")
    ap.add_argument("--author", default="", help="Etiqueta del agente (ej. Cursor)")
    ap.add_argument("--msg", required=True, help="Mensaje breve de progreso")
    ap.add_argument(
        "--source",
        default="swarm_sync",
        help="Etiqueta de origen (default: swarm_sync)",
    )
    ap.add_argument(
        "--ticket",
        default="V14.0",
        help="Ticket embebido en digest V14 (default V14.0)",
    )
    ap.add_argument(
        "--log",
        default=None,
        help="Ruta JSONL (sustituye KERNEL_SWARM_SYNC_LOG; default data/swarm_sync_log.jsonl)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo imprime JSON a stdout; no escribe archivos.",
    )
    args = ap.parse_args(argv)

    llm_mode = resolve_llm_mode()
    snippet = _biographic_snippet_from_disk()
    v14 = v14_session_sync_record(
        args.msg,
        biographic_digest_snippet=snippet,
        ticket=(args.ticket or "V14.0")[:32],
    )

    raw_log = (args.log or os.environ.get("KERNEL_SWARM_SYNC_LOG", "") or "").strip()
    jsonl = Path(raw_log) if raw_log else REPO_ROOT / "data" / "swarm_sync_log.jsonl"

    rec = {
        "ts": time.time(),
        "iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "block": (args.block or "").strip(),
        "author": (args.author or "").strip(),
        "msg": (args.msg or "").strip(),
        "source": (args.source or "").strip(),
        "pid": os.getpid(),
        "llm_resolved_mode": llm_mode,
        "kernel_llm_cloud_disabled": os.environ.get("KERNEL_LLM_CLOUD_DISABLED", "").strip().lower()
        in ("1", "true", "yes", "on"),
        "somatic_biographic_anchor": _somatic_biographic_anchor(),
        "v14": v14,
    }
    line = json.dumps(rec, ensure_ascii=False) + "\n"

    if args.dry_run:
        sys.stdout.write(line)
        return 0

    try:
        append_swarm_sync_event(
            args.msg,
            source=args.source,
            block=(args.block or "").strip(),
            author=(args.author or "").strip(),
        )
    except OSError as e:
        print(f"swarm_sync: biography append failed: {e}", file=sys.stderr)
        return 1

    try:
        jsonl.parent.mkdir(parents=True, exist_ok=True)
        with open(jsonl, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError as e:
        print(f"swarm_sync: jsonl append failed: {e}", file=sys.stderr)

    print(f"swarm_sync ok -> {jsonl}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
