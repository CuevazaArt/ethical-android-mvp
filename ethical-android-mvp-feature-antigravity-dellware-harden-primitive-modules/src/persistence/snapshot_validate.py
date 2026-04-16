"""JSON Schema validation for migrated kernel snapshot dicts (schema 3)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from .schema import SCHEMA_VERSION, KernelSnapshotV1
from .snapshot_serde import kernel_snapshot_to_json_dict

_SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "kernel_snapshot_v3.schema.json"


@lru_cache(maxsize=1)
def _kernel_snapshot_schema() -> dict[str, Any]:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_migrated_snapshot_dict(d: dict[str, Any]) -> None:
    """
    Validate a **complete** migrated dict (all top-level keys present).

    For typical loads, use :func:`validate_snapshot_for_apply` after building
    :class:`~src.persistence.schema.KernelSnapshotV1` so defaults fill missing keys.

    Raises:
        jsonschema.exceptions.ValidationError: payload does not match schema 3.
        ValueError: schema_version is not the current constant.
    """
    ver = d.get("schema_version")
    if ver != SCHEMA_VERSION:
        raise ValueError(
            f"Snapshot dict schema_version is {ver!r}; expected {SCHEMA_VERSION} after migration"
        )
    schema = _kernel_snapshot_schema()
    Draft202012Validator(schema).validate(d)


def validate_snapshot_for_apply(snap: KernelSnapshotV1) -> None:
    """Re-validate before :func:`~src.persistence.kernel_io.apply_snapshot` (round-trip safety)."""
    if snap.schema_version != SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported schema_version {snap.schema_version}; expected {SCHEMA_VERSION}"
        )
    try:
        validate_migrated_snapshot_dict(kernel_snapshot_to_json_dict(snap))
    except ValidationError as e:
        raise ValueError(f"KernelSnapshotV1 failed JSON Schema validation: {e.message}") from e
