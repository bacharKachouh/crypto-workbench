"""Read and update `.cryptoworkbench/workbench/current_target.yaml`.

The target can be left deferred (empty `name`/`type`/`primary_sources`) after
`crypto-init`. Downstream skills that actually need a field call
`check_target_fields()` to learn what is missing and prompt the user to fill
it in, rather than hard-failing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import yaml

MODULE = "workbench.target"

TARGET_FILE = "workbench/current_target.yaml"

_DEFAULT_TARGET: dict[str, Any] = {
    "name": "",
    "type": "",
    "primary_sources": [],
    "status": "draft",
}


def _target_path(workbench_root: str | Path) -> Path:
    return Path(workbench_root) / TARGET_FILE


def load_target(workbench_root: str | Path) -> dict[str, Any]:
    """Load the target dict from `current_target.yaml`.

    Returns the `target:` sub-dict. If the file is missing or malformed,
    returns a fresh default (status=draft, empty fields).
    """
    path = _target_path(workbench_root)
    if not path.exists():
        return dict(_DEFAULT_TARGET)
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return dict(_DEFAULT_TARGET)
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        return dict(_DEFAULT_TARGET)
    target = data.get("target")
    if not isinstance(target, dict):
        return dict(_DEFAULT_TARGET)
    merged = dict(_DEFAULT_TARGET)
    merged.update(target)
    return merged


def save_target(workbench_root: str | Path, target: dict[str, Any]) -> Path:
    """Write the target dict back to `current_target.yaml`.

    Preserves other top-level keys in the file if any exist. Only the
    `target:` entry is replaced.
    """
    path = _target_path(workbench_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing: dict[str, Any] = {}
    if path.exists():
        text = path.read_text(encoding="utf-8").strip()
        if text:
            loaded = yaml.safe_load(text)
            if isinstance(loaded, dict):
                existing = loaded
    merged_target = dict(_DEFAULT_TARGET)
    merged_target.update(target)
    existing["target"] = merged_target
    path.write_text(
        yaml.dump(existing, default_flow_style=False, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path


def check_target_fields(
    workbench_root: str | Path,
    required: Iterable[str],
) -> dict[str, Any]:
    """Return current target + list of required fields that are missing/empty.

    A field is considered "missing" if it is absent, None, or equivalent
    to its default (empty string for scalars, empty list for
    `primary_sources`).
    """
    target = load_target(workbench_root)
    missing: list[str] = []
    for field in required:
        value = target.get(field)
        if value is None:
            missing.append(field)
            continue
        if isinstance(value, str) and value.strip() == "":
            missing.append(field)
            continue
        if field == "primary_sources" and isinstance(value, list) and len(value) == 0:
            missing.append(field)
            continue
    return {
        "module": MODULE,
        "target": target,
        "missing": missing,
        "is_deferred": target.get("status") == "draft" and len(missing) > 0,
    }


def mark_status(workbench_root: str | Path, status: str) -> Path:
    """Shortcut to update just the `status` field of the target."""
    target = load_target(workbench_root)
    target["status"] = status
    return save_target(workbench_root, target)
