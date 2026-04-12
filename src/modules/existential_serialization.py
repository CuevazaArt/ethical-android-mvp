"""
Existential serialization — nomadic transfer protocol.

Real P2P transport is **out of scope**; the kernel exposes a versioned
:class:`~src.persistence.schema.KernelSnapshotV1`.

Phases A–D (design): encapsulate → **Ed25519 handshake** → sensor adapt → **narrative integrity**.

**Phase 4 (narrative integrity):** canonical SHA-256 over the snapshot JSON plus an Ed25519
signature over the digest so a receiving device (e.g. smartphone) can confirm the bundle was
produced by the holder of the private key and matches the loaded narrative state.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .hub_audit import register_hub_calibration

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

    _HAS_CRYPTO = True
except ImportError:  # pragma: no cover - optional in exotic installs
    Ed25519PrivateKey = object  # type: ignore[misc, assignment]
    Ed25519PublicKey = object  # type: ignore[misc, assignment]
    Encoding = PublicFormat = None  # type: ignore[misc, assignment]
    _HAS_CRYPTO = False

HANDSHAKE_ALGORITHM_V1 = "ed25519-sha256-commitment-v1"


class TransmutationPhase(str, Enum):
    """Protocol of transmutation — Phases A–D (design doc)."""

    ENCAPSULATE = "A_encapsulate"
    HANDSHAKE = "B_handshake"
    SENSOR_ADAPT = "C_sensor_adapt"
    NARRATIVE_INTEGRITY = "D_narrative_integrity"


@dataclass
class ContinuityToken:
    """Migration boundary token; Phase 4 adds optional cryptographic fields."""

    thought_summary: str
    identity_fingerprint: str
    phase: TransmutationPhase = TransmutationPhase.ENCAPSULATE
    commitment_sha256: str | None = None
    signature_ed25519_b64: str | None = None
    public_key_ed25519_b64: str | None = None
    handshake_algorithm: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "thought_summary": self.thought_summary,
            "identity_fingerprint": self.identity_fingerprint,
            "phase": self.phase.value,
        }
        if self.commitment_sha256 is not None:
            d["commitment_sha256"] = self.commitment_sha256
        if self.signature_ed25519_b64 is not None:
            d["signature_ed25519_b64"] = self.signature_ed25519_b64
        if self.public_key_ed25519_b64 is not None:
            d["public_key_ed25519_b64"] = self.public_key_ed25519_b64
        if self.handshake_algorithm is not None:
            d["handshake_algorithm"] = self.handshake_algorithm
        return d


def _episode_chain_fingerprint(kernel: Any, max_episodes: int = 64) -> str:
    """Deterministic SHA-256 over recent episode ids + identity episode count (audit-grade demo)."""
    mem = getattr(kernel, "memory", None)
    if mem is None:
        return "0" * 64
    ids = [ep.id for ep in mem.episodes[-max_episodes:]]
    id_part = str(getattr(mem.identity.state, "episode_count", 0))
    raw = (
        "|".join(ids) + "::" + id_part + "::" + (getattr(mem, "experience_digest", "") or "")[:400]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _identity_fingerprint_stub(kernel: Any) -> str:
    """Short display fingerprint (first 16 hex chars of full chain hash)."""
    return _episode_chain_fingerprint(kernel)[:16]


def canonical_narrative_commitment_hex(kernel: Any) -> str:
    """
    Phase 4 — SHA-256 over canonical UTF-8 JSON of :class:`KernelSnapshotV1` (sorted keys).

    Matches persisted state when :func:`~src.persistence.kernel_io.extract_snapshot` is stable.
    """
    from src.persistence.kernel_io import extract_snapshot
    from src.persistence.snapshot_serde import kernel_snapshot_to_json_dict

    snap = extract_snapshot(kernel)
    d = kernel_snapshot_to_json_dict(snap)
    canonical = json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _public_key_b64(pub: Ed25519PublicKey) -> str:
    raw = pub.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)
    return base64.b64encode(raw).decode("ascii")


def _load_ed25519_private_key_from_env() -> Ed25519PrivateKey | None:
    if not _HAS_CRYPTO:
        return None
    raw = os.environ.get("KERNEL_NOMADIC_ED25519_PRIVATE_KEY", "").strip()
    if not raw:
        return None
    try:
        data = base64.b64decode(raw)
        if len(data) == 32:
            return Ed25519PrivateKey.from_private_bytes(data)
    except Exception:
        pass
    try:
        if len(raw) == 64 and all(c in "0123456789abcdefABCDEF" for c in raw):
            return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(raw))
    except Exception:
        pass
    return None


def _load_ed25519_public_key_from_env() -> Ed25519PublicKey | None:
    if not _HAS_CRYPTO:
        return None
    raw = os.environ.get("KERNEL_NOMADIC_ED25519_PUBLIC_KEY", "").strip()
    if not raw:
        return None
    try:
        data = base64.b64decode(raw)
        if len(data) == 32:
            return Ed25519PublicKey.from_public_bytes(data)
    except Exception:
        pass
    try:
        if len(raw) == 64 and all(c in "0123456789abcdefABCDEF" for c in raw):
            return Ed25519PublicKey.from_public_bytes(bytes.fromhex(raw))
    except Exception:
        pass
    return None


def _sign_commitment_ed25519(commitment_hex: str, private_key: Ed25519PrivateKey) -> bytes:
    digest = bytes.fromhex(commitment_hex)
    return private_key.sign(digest)


def _verify_commitment_ed25519(
    commitment_hex: str, signature: bytes, public_key: Ed25519PublicKey
) -> bool:
    digest = bytes.fromhex(commitment_hex)
    try:
        public_key.verify(signature, digest)
    except Exception:
        return False
    return True


def build_continuity_token_stub(kernel: Any, thought_line: str = "") -> ContinuityToken:
    """Phase A — token for DAO / owner message; does not contain secrets."""
    line = (thought_line or "").strip()[:500] or "(no monologue line bound)"
    return ContinuityToken(
        thought_summary=line,
        identity_fingerprint=_identity_fingerprint_stub(kernel),
        phase=TransmutationPhase.ENCAPSULATE,
    )


def build_continuity_token_phase4_signed(
    kernel: Any,
    thought_line: str = "",
    *,
    private_key: Ed25519PrivateKey | None = None,
) -> ContinuityToken | None:
    """
    Phase B + D — continuity token with Ed25519 signature over the canonical snapshot commitment.

    Uses ``private_key`` or ``KERNEL_NOMADIC_ED25519_PRIVATE_KEY`` (32-byte seed, base64 or hex).
    Returns None if signing is unavailable.
    """
    if not _HAS_CRYPTO:
        return None
    pk = private_key if private_key is not None else _load_ed25519_private_key_from_env()
    if pk is None:
        return None
    line = (thought_line or "").strip()[:500] or "(no monologue line bound)"
    commitment = canonical_narrative_commitment_hex(kernel)
    sig = _sign_commitment_ed25519(commitment, pk)
    pub = pk.public_key()
    return ContinuityToken(
        thought_summary=line,
        identity_fingerprint=_identity_fingerprint_stub(kernel),
        phase=TransmutationPhase.NARRATIVE_INTEGRITY,
        commitment_sha256=commitment,
        signature_ed25519_b64=base64.b64encode(sig).decode("ascii"),
        public_key_ed25519_b64=_public_key_b64(pub),
        handshake_algorithm=HANDSHAKE_ALGORITHM_V1,
    )


def export_nomadic_handshake_bundle(
    kernel: Any,
    thought_line: str = "",
    *,
    private_key: Ed25519PrivateKey | None = None,
) -> dict[str, Any]:
    """
    Export a JSON-serializable bundle for offline transfer (server → phone).

    Requires ``cryptography``, a ``private_key`` argument, or
    ``KERNEL_NOMADIC_ED25519_PRIVATE_KEY``. Verifier uses ``public_key_ed25519_b64`` from the
    bundle (or ``KERNEL_NOMADIC_ED25519_PUBLIC_KEY`` on the device).
    """
    if not _HAS_CRYPTO:
        return {
            "ok": False,
            "error": "cryptography package is required for Ed25519 handshake",
            "algorithm": HANDSHAKE_ALGORITHM_V1,
        }
    token = build_continuity_token_phase4_signed(kernel, thought_line, private_key=private_key)
    if token is None:
        return {
            "ok": False,
            "error": "No Ed25519 private key: pass private_key or set KERNEL_NOMADIC_ED25519_PRIVATE_KEY",
            "algorithm": HANDSHAKE_ALGORITHM_V1,
        }
    return {
        "ok": True,
        "version": 1,
        "algorithm": HANDSHAKE_ALGORITHM_V1,
        "continuity": token.to_dict(),
        "commitment_sha256": token.commitment_sha256,
        "signature_ed25519_b64": token.signature_ed25519_b64,
        "public_key_ed25519_b64": token.public_key_ed25519_b64,
    }


def verify_nomadic_handshake(
    kernel: Any,
    bundle: dict[str, Any],
    *,
    public_key: Ed25519PublicKey | None = None,
) -> dict[str, Any]:
    """
    Phase 4 — verify that the loaded kernel matches the signed commitment.

    ``bundle`` is typically :func:`export_nomadic_handshake_bundle` output. Supply
    ``public_key`` or set ``KERNEL_NOMADIC_ED25519_PUBLIC_KEY``, or embed the public key in the bundle.
    """
    if not _HAS_CRYPTO:
        return {
            "ok": False,
            "commitment_matches": False,
            "signature_valid": False,
            "error": "cryptography package is required",
        }
    exp_commit = (bundle.get("commitment_sha256") or "").strip().lower()
    sig_b64 = bundle.get("signature_ed25519_b64")
    pub_b64 = bundle.get("public_key_ed25519_b64")
    if not exp_commit or not isinstance(sig_b64, str) or not isinstance(pub_b64, str):
        return {
            "ok": False,
            "commitment_matches": False,
            "signature_valid": False,
            "error": "bundle missing commitment_sha256, signature_ed25519_b64, or public_key_ed25519_b64",
        }
    current = canonical_narrative_commitment_hex(kernel).lower()
    commitment_matches = exp_commit == current

    pub = public_key
    if pub is None:
        try:
            raw = base64.b64decode(pub_b64.encode("ascii"))
            if len(raw) == 32:
                pub = Ed25519PublicKey.from_public_bytes(raw)
        except Exception:
            pub = _load_ed25519_public_key_from_env()
    if pub is None:
        return {
            "ok": False,
            "commitment_matches": commitment_matches,
            "signature_valid": False,
            "commitment_expected": exp_commit,
            "commitment_current": current,
            "error": "Could not load Ed25519 public key from bundle or KERNEL_NOMADIC_ED25519_PUBLIC_KEY",
        }
    try:
        sig = base64.b64decode(sig_b64.encode("ascii"))
    except Exception:
        return {
            "ok": False,
            "commitment_matches": commitment_matches,
            "signature_valid": False,
            "error": "invalid base64 in signature_ed25519_b64",
        }
    signature_valid = _verify_commitment_ed25519(exp_commit, sig, pub)
    ok = commitment_matches and signature_valid
    return {
        "ok": ok,
        "commitment_matches": commitment_matches,
        "signature_valid": signature_valid,
        "commitment_expected": exp_commit,
        "commitment_current": current,
        "error": None if ok else "commitment or signature mismatch (narrative tampering suspected)",
    }


def narrative_integrity_self_check_stub(kernel: Any) -> dict[str, Any]:
    """
    Phase D — integrity smoke: last episode id + chain hash over recent episodes.
    """
    mem = getattr(kernel, "memory", None)
    ok = mem is not None
    last_id = None
    n_ep = 0
    if mem and mem.episodes:
        last_id = mem.episodes[-1].id
        n_ep = len(mem.episodes)
    chain = _episode_chain_fingerprint(kernel) if mem else ""
    return {
        "ok": ok,
        "episode_count": n_ep,
        "last_episode_id": last_id,
        "chain_sha256": chain,
        "message_en": "Narrative chain fingerprint (deterministic; demo audit).",
    }


def narrative_integrity_phase4(
    kernel: Any,
    exported_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Phase 4 report: stub fields plus canonical snapshot commitment; optional handshake verification.
    """
    base = narrative_integrity_self_check_stub(kernel)
    commitment_hex = canonical_narrative_commitment_hex(kernel)
    base["commitment_sha256"] = commitment_hex
    base["phase"] = TransmutationPhase.NARRATIVE_INTEGRITY.value
    base["message_en"] = (
        "Nomadic narrative integrity (Phase 4): SHA-256 over canonical snapshot JSON; "
        "Ed25519 handshake when an export bundle is supplied."
    )
    if exported_bundle is None:
        base["handshake_ok"] = None
        return base
    vr = verify_nomadic_handshake(kernel, exported_bundle)
    base["handshake_ok"] = vr.get("ok")
    base["handshake"] = vr
    return base


def nomad_migration_audit_enabled() -> bool:
    """Append DAO audit line when simulating / completing a nomadic handoff."""
    v = os.environ.get("KERNEL_NOMAD_MIGRATION_AUDIT", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def nomad_simulation_ws_enabled() -> bool:
    """WebSocket JSON ``nomad_simulate_migration`` (demo / lab)."""
    v = os.environ.get("KERNEL_NOMAD_SIMULATION", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def migration_audit_payload(
    kernel: Any,
    *,
    destination_hardware_id: str = "",
    include_location: bool = False,
    thought_line: str = "",
) -> dict[str, Any]:
    """
    DAO event payload: **no GPS** unless include_location True (owner opt-in design).
    """
    token = build_continuity_token_phase4_signed(kernel, thought_line)
    continuity = (
        token.to_dict()
        if token is not None
        else build_continuity_token_stub(kernel, thought_line).to_dict()
    )
    out: dict[str, Any] = {
        "kind": "nomadic_migration",
        "destination_hardware_id": (destination_hardware_id or "unspecified")[:128],
        "continuity": continuity,
    }
    if include_location:
        out["location_disclosure"] = "opt_in_only"
    return out


def record_nomadic_migration_audit(
    dao: Any,
    kernel: Any,
    *,
    destination_hardware_id: str = "",
    include_location: bool = False,
    thought_line: str = "",
) -> bool:
    """Register a :class:`~src.modules.mock_dao.MockDAO` audit record when env allows."""
    if not nomad_migration_audit_enabled():
        return False
    payload = migration_audit_payload(
        kernel,
        destination_hardware_id=destination_hardware_id,
        include_location=include_location,
        thought_line=thought_line,
    )
    register_hub_calibration(dao, "nomadic_migration", payload)
    return True


def simulate_nomadic_migration(
    kernel: Any,
    dao: Any,
    *,
    profile: str = "mobile",
    destination_hardware_id: str = "",
    thought_line: str = "",
    include_location: bool = False,
    exported_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Demo **Phase C**: apply HAL profile, optional DAO audit, narrative delta + Phase 4 integrity.

    ``profile``: ``\"mobile\"`` | ``\"server\"`` (default mobile = edge tier + phone sensors).

    ``exported_bundle``: when simulating receipt on a new device, pass the exported handshake
    JSON to verify commitment + signature against the loaded kernel.
    """
    from .hardware_abstraction import (
        apply_hardware_context,
        default_mobile_context,
        default_server_context,
        sensor_delta_narrative,
    )

    before = getattr(kernel, "_hal_context", None)
    before_ctx = before if before is not None else default_server_context()
    after = (
        default_mobile_context()
        if profile.strip().lower() == "mobile"
        else default_server_context()
    )
    apply_hardware_context(kernel, after)
    narrative_en = sensor_delta_narrative(before_ctx, after)
    audit_recorded = record_nomadic_migration_audit(
        dao,
        kernel,
        destination_hardware_id=destination_hardware_id,
        include_location=include_location,
        thought_line=thought_line,
    )
    return {
        "profile": profile,
        "sensor_delta_narrative_en": narrative_en,
        "hardware_context": after.to_public_dict(),
        "integrity": narrative_integrity_phase4(kernel, exported_bundle),
        "dao_audit_recorded": audit_recorded,
    }
