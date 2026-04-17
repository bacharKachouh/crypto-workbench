"""Load and manage workbench/config.yaml for Crypto Workbench."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def load_config(path: Path) -> dict[str, Any]:
    """Load config from a YAML file. Returns empty dict if missing or empty."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    data = yaml.safe_load(text)
    return data if isinstance(data, dict) else {}


def save_config(path: Path, updates: dict[str, Any]) -> None:
    """Merge updates into an existing config file and write it back."""
    existing = load_config(path)
    existing.update(updates)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.dump(existing, default_flow_style=False, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def get_search_policy(config_path: Path) -> dict[str, Any] | None:
    """Read the search_policy from config. Returns None if not set."""
    cfg = load_config(config_path)
    return cfg.get("search_policy")


def set_search_policy(config_path: Path, *, allowed: bool) -> None:
    """Write search policy consent to config."""
    policy = {
        "online_search_allowed": allowed,
        "decided_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "decided_by": "user",
    }
    save_config(config_path, {"search_policy": policy})
