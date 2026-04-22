"""
Critical context distillation (planned) — “70B → 8B” conduct guide before nomadic jump.

When the large runtime produces a **conduct guide** (rules distilled from deliberation),
the small model can follow the same ethical stance without full reasoning capacity.

**Vertical Phase 3:** :func:`validate_conduct_guide_dict` checks minimal shape (see field list
in that function). Load path remains env-driven; integration with HAL is still incremental.

Env: ``KERNEL_CONDUCT_GUIDE_PATH`` — optional JSON **to load** on an edge runtime.
**Export** from the PC session uses ``KERNEL_CONDUCT_GUIDE_EXPORT_PATH`` (see ``conduct_guide_export.py``).
"""
# Status: SCAFFOLD


from __future__ import annotations

import json
import os
from typing import Any

from src.persistence.schema import SCHEMA_VERSION as _SNAPSHOT_SCHEMA_VERSION


def validate_conduct_guide_dict(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Minimal schema: ``version`` == 1, list fields are lists, optional
    ``checkpoint_compatible_schema`` matches current kernel snapshot version when present.
    """
    errors: list[str] = []
    if not isinstance(data, dict):
        return False, ["not_a_dict"]
    ver = data.get("version")
    if ver != 1:
        errors.append("version_must_equal_1")
    for key in (
        "ethical_non_negotiables",
        "gray_zone_rules",
        "forbidden_shortcuts",
        "lighthouse_snapshot_ids",
    ):
        if key in data and data[key] is not None and not isinstance(data[key], list):
            errors.append(f"{key}_must_be_list_or_absent")
    ccs = data.get("checkpoint_compatible_schema")
    if ccs is not None and int(ccs) != _SNAPSHOT_SCHEMA_VERSION:
        errors.append(f"checkpoint_compatible_schema_mismatch_expected_{_SNAPSHOT_SCHEMA_VERSION}")
    return (len(errors) == 0, errors)


def load_conduct_guide_from_env() -> dict[str, Any] | None:
    """Return parsed conduct guide if path set and file readable; else None."""
    path = os.environ.get("KERNEL_CONDUCT_GUIDE_PATH", "").strip()
    if not path or not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def load_and_validate_conduct_guide_from_env() -> tuple[dict[str, Any] | None, list[str]]:
    """
    Load from ``KERNEL_CONDUCT_GUIDE_PATH`` and validate. On failure returns (None, errors).
    """
    raw = load_conduct_guide_from_env()
    if raw is None:
        return None, ["missing_or_unreadable"]
    ok, errs = validate_conduct_guide_dict(raw)
    if not ok:
        return None, errs
    return raw, []
