"""
Emergency CLI — operate the kernel without the web UI (diagnostics, checkpoints, nomadic handshake).

Usage::

    python -m src.ethos_cli diagnostics [--checkpoint PATH]
    python -m src.ethos_cli checkpoint load PATH
    python -m src.ethos_cli checkpoint save PATH
    python -m src.ethos_cli nomad handshake-export [--thought LINE]
    python -m src.ethos_cli nomad handshake-verify --bundle FILE [--checkpoint PATH]

After ``pip install -e .``, the ``ethos`` console script is available.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _kernel(*, llm_mode: str = "local"):
    from src.kernel import EthicalKernel

    return EthicalKernel(variability=False, llm_mode=llm_mode)


def _load_checkpoint_if_given(kernel, path: Path | None) -> bool:
    if path is None:
        return False
    from src.persistence.checkpoint import try_load_checkpoint
    from src.persistence.checkpoint_adapters import JsonFileCheckpointAdapter

    kernel.checkpoint_persistence = JsonFileCheckpointAdapter(path)
    return try_load_checkpoint(kernel)


def cmd_diagnostics(args: argparse.Namespace) -> int:
    from src.modules.existential_serialization import (
        canonical_narrative_commitment_hex,
        narrative_integrity_phase4,
    )

    k = _kernel(llm_mode=args.llm_mode)
    loaded = _load_checkpoint_if_given(k, args.checkpoint)
    mem = k.memory
    daily = mem.daily_summary()
    commitment = canonical_narrative_commitment_hex(k)
    integrity = narrative_integrity_phase4(k, None)
    payload = {
        "checkpoint_loaded": loaded,
        "checkpoint_path": str(args.checkpoint) if args.checkpoint else None,
        "episodes": daily.get("episodes", 0),
        "average_ethical_score": daily.get("average_score"),
        "dao_record_count": len(k.dao.records),
        "narrative_commitment_sha256": commitment,
        "integrity": integrity,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("Ethos Kernel diagnostics (no HTTP)")
        print(f"  Episodes: {payload['episodes']}")
        print(f"  DAO records: {payload['dao_record_count']}")
        print(f"  Checkpoint loaded: {loaded}")
        if args.checkpoint:
            print(f"  Checkpoint path: {args.checkpoint}")
        print(f"  Narrative commitment (SHA-256): {commitment}")
    return 0


def cmd_checkpoint_load(args: argparse.Namespace) -> int:
    from src.persistence.checkpoint import try_load_checkpoint
    from src.persistence.checkpoint_adapters import JsonFileCheckpointAdapter

    path = Path(args.path)
    k = _kernel(llm_mode=args.llm_mode)
    k.checkpoint_persistence = JsonFileCheckpointAdapter(path)
    ok = try_load_checkpoint(k)
    if args.json:
        print(json.dumps({"loaded": ok, "path": str(path), "episodes": len(k.memory.episodes)}))
    else:
        print(f"checkpoint load: path={path} loaded={ok} episodes={len(k.memory.episodes)}")
    if args.require_load and not ok:
        return 1
    return 0


def cmd_checkpoint_save(args: argparse.Namespace) -> int:
    from src.persistence.checkpoint import try_save_checkpoint
    from src.persistence.checkpoint_adapters import JsonFileCheckpointAdapter

    path = Path(args.path)
    k = _kernel(llm_mode=args.llm_mode)
    _load_checkpoint_if_given(k, args.merge_from)
    k.checkpoint_persistence = JsonFileCheckpointAdapter(path)
    ok = try_save_checkpoint(k)
    if args.json:
        print(json.dumps({"saved": ok, "path": str(path)}))
    else:
        print(f"checkpoint save: path={path} saved={ok}")
    return 0 if ok else 1


def cmd_handshake_export(args: argparse.Namespace) -> int:
    from src.modules.existential_serialization import export_nomadic_handshake_bundle

    k = _kernel(llm_mode=args.llm_mode)
    _load_checkpoint_if_given(k, args.checkpoint)
    bundle = export_nomadic_handshake_bundle(k, args.thought or "")
    print(json.dumps(bundle, indent=2))
    return 0 if bundle.get("ok") else 2


def cmd_handshake_verify(args: argparse.Namespace) -> int:
    from src.modules.existential_serialization import verify_nomadic_handshake

    raw = Path(args.bundle).read_text(encoding="utf-8")
    bundle = json.loads(raw)
    k = _kernel(llm_mode=args.llm_mode)
    _load_checkpoint_if_given(k, args.checkpoint)
    vr = verify_nomadic_handshake(k, bundle)
    print(json.dumps(vr, indent=2))
    return 0 if vr.get("ok") else 3


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ethos",
        description="Ethos Kernel emergency CLI (diagnostics, checkpoints, nomadic handshake).",
    )
    parser.add_argument(
        "--llm-mode",
        default="local",
        help="LLM mode for EthicalKernel (default: local, no external calls).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_diag = sub.add_parser("diagnostics", help="Print kernel stats and Phase 4 commitment.")
    p_diag.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Optional JSON checkpoint to load before reporting.",
    )
    p_diag.add_argument("--json", action="store_true", help="Machine-readable JSON output.")
    p_diag.set_defaults(func=cmd_diagnostics)

    p_ck = sub.add_parser("checkpoint", help="Load or save JSON checkpoints.")
    ck_sub = p_ck.add_subparsers(dest="checkpoint_action", required=True)

    p_load = ck_sub.add_parser("load", help="Load snapshot from a JSON file into a fresh kernel.")
    p_load.add_argument("path", type=Path)
    p_load.add_argument(
        "--require-load",
        action="store_true",
        help="Exit non-zero if the file is missing or empty.",
    )
    p_load.add_argument("--json", action="store_true")
    p_load.set_defaults(func=cmd_checkpoint_load)

    p_save = ck_sub.add_parser("save", help="Save current kernel snapshot to a JSON file.")
    p_save.add_argument("path", type=Path)
    p_save.add_argument(
        "--merge-from",
        type=Path,
        default=None,
        help="Load this checkpoint first, then save (optional).",
    )
    p_save.add_argument("--json", action="store_true")
    p_save.set_defaults(func=cmd_checkpoint_save)

    p_nomad = sub.add_parser("nomad", help="Nomadic continuity (Phase 4 handshake).")
    nomad_sub = p_nomad.add_subparsers(dest="nomad_action", required=True)

    p_hex = nomad_sub.add_parser(
        "handshake-export",
        help="Export signed handshake JSON (needs KERNEL_NOMADIC_ED25519_PRIVATE_KEY).",
    )
    p_hex.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Load this checkpoint before signing.",
    )
    p_hex.add_argument("--thought", default="", help="Optional thought line for continuity token.")
    p_hex.set_defaults(func=cmd_handshake_export)

    p_ver = nomad_sub.add_parser(
        "handshake-verify",
        help="Verify handshake JSON against the loaded kernel state.",
    )
    p_ver.add_argument(
        "--bundle", type=Path, required=True, help="JSON file from handshake-export."
    )
    p_ver.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Load checkpoint before verify (must match export-time state).",
    )
    p_ver.set_defaults(func=cmd_handshake_verify)

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = _build_parser()
    args = parser.parse_args(argv)
    fn = getattr(args, "func", None)
    if fn is None:
        parser.print_help()
        return 2
    return int(fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
