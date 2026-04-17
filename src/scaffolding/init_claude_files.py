"""Initialize Claude-specific Crypto Workbench files in a target project."""

from __future__ import annotations

from pathlib import Path
from typing import Any

MODULE = "scaffolding.init_claude_files"

TEMPLATE_DIR = Path(__file__).resolve().parents[2] / "templates" / "claude"

CLAUDE_FILES = {
    "CLAUDE.md": TEMPLATE_DIR / "CLAUDE.md",
}


def initialize_claude_files(
    root: str | Path = ".", *, overwrite: bool = False
) -> dict[str, Any]:
    """Copy Claude template files into the target project root.

    Creates a CLAUDE.md in the target project so Claude picks up the
    Crypto Workbench workflow contract. Existing files are preserved
    by default.
    """
    root_path = Path(root).expanduser().resolve()

    created_files: list[str] = []
    existing_files: list[str] = []

    for filename, template_path in CLAUDE_FILES.items():
        target = root_path / filename
        if target.exists() and not overwrite:
            existing_files.append(str(target))
            continue
        content = template_path.read_text(encoding="utf-8")
        target.write_text(content, encoding="utf-8")
        created_files.append(str(target))

    return {
        "module": MODULE,
        "status": "initialized",
        "root": str(root_path),
        "created_files": created_files,
        "existing_files": existing_files,
    }


def run(**context: Any) -> dict[str, Any]:
    """Initialize Claude files from workflow context."""
    root = context.get("root") or context.get("target_project") or "."
    overwrite = bool(context.get("overwrite", False))
    result = initialize_claude_files(root, overwrite=overwrite)
    result["context"] = context
    return result
