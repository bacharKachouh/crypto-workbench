"""Load Crypto Workbench registry YAML files.

The registry is a curated core knowledge layer under registry/.
This module loads individual files, categories (directories), and
the full registry tree.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

MODULE = "libraries.registry_loader"


def load_registry_file(path: Path | str) -> dict[str, Any] | None:
    """Load a single registry YAML file. Returns None if file doesn't exist."""
    path = Path(path)
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None
    data = yaml.safe_load(text)
    return data if isinstance(data, dict) else None


def load_registry_category(directory: Path | str) -> list[dict[str, Any]]:
    """Load all .yml files in a directory as a list of dicts."""
    directory = Path(directory)
    if not directory.exists():
        return []
    results = []
    for f in sorted(directory.glob("*.yml")):
        data = load_registry_file(f)
        if data is not None:
            data["_source_file"] = str(f.name)
            results.append(data)
    return results


def load_all_registries(registry_root: Path | str) -> dict[str, list[dict[str, Any]]]:
    """Load the full registry tree into a dict keyed by category.

    Walks one level of subdirectories under registry_root. Directories
    with nested subdirectories (e.g., algorithms/classical/) are flattened
    into a single list for the parent category.
    """
    registry_root = Path(registry_root)
    result: dict[str, list[dict[str, Any]]] = {}
    if not registry_root.exists():
        return result

    for subdir in sorted(registry_root.iterdir()):
        if not subdir.is_dir():
            continue
        category = subdir.name
        entries = load_registry_category(subdir)
        for nested in sorted(subdir.iterdir()):
            if nested.is_dir():
                entries.extend(load_registry_category(nested))
        result[category] = entries

    return result


def run(**context: Any) -> dict[str, Any]:
    """Load registries from workflow context."""
    registry_root = Path(context.get("registry_root", "registry"))
    data = load_all_registries(registry_root)
    return {"module": MODULE, "status": "loaded", "categories": list(data.keys()), "data": data}
