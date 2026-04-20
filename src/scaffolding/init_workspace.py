"""Initialize Crypto Workbench workspace files."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

MODULE = "scaffolding.init_workspace"

WORKSPACE_DIR = ".cryptoworkbench"

WORKSPACE_DIRS = (
    "corpus/papers",
    "corpus/standards",
    "corpus/notes",
    "corpus/drafts",
    "corpus/prior_impls",
    "corpus/fetched",
    "extracted/reviews",
    "extracted/notation_maps",
    "extracted/ambiguity_logs",
    "extracted/impl_specs",
    "extracted/security_reviews",
    "extracted/library_mappings",
    "extracted/test_vectors",
    "extracted/source_indexes",
    "extracted/scenarios",
    "extracted/synthesis",
    "extracted/implementations",
    "workbench",
    "cache",
)

WORKBENCH_FILES = {
    "workbench/current_target.yaml": """target:
  name: ""
  type: ""
  primary_sources: []
  status: draft
""",
    "workbench/decisions.md": """# Decisions

Record implementation, review, and security decisions here.
""",
    "workbench/open_questions.md": """# Open Questions

Track unresolved cryptographic, implementation, and source-provenance questions here.
""",
    "workbench/implementation_plan.md": """# Implementation Plan

## Scope

## Dependencies

## Tests

## Risks
""",
    "workbench/config.yaml": """# Crypto Workbench configuration
# This file is managed by the crypto-init and crypto-intake skills.
""",
}


def initialize_workspace(root: str | Path = ".", *, overwrite: bool = False) -> dict[str, Any]:
    """Create the target project's `.cryptoworkbench` tree.

    Existing files are preserved by default because decisions, questions, and plans
    are user-owned once a target project has been initialized.
    """
    root_path = Path(root).expanduser().resolve()
    workbench_root = root_path / WORKSPACE_DIR

    created_dirs: list[str] = []
    existing_dirs: list[str] = []
    created_files: list[str] = []
    existing_files: list[str] = []

    for relative_dir in WORKSPACE_DIRS:
        directory = workbench_root / relative_dir
        if directory.exists():
            existing_dirs.append(str(directory))
        else:
            directory.mkdir(parents=True, exist_ok=True)
            created_dirs.append(str(directory))

    for relative_file, content in WORKBENCH_FILES.items():
        file_path = workbench_root / relative_file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.exists() and not overwrite:
            existing_files.append(str(file_path))
            continue
        file_path.write_text(content, encoding="utf-8")
        created_files.append(str(file_path))

    return {
        "module": MODULE,
        "status": "initialized",
        "root": str(root_path),
        "workbench": str(workbench_root),
        "created_dirs": created_dirs,
        "existing_dirs": existing_dirs,
        "created_files": created_files,
        "existing_files": existing_files,
    }


def run(**context: Any) -> dict[str, Any]:
    """Initialize a target workspace from workflow context."""
    root = context.get("root") or context.get("target_project") or "."
    overwrite = bool(context.get("overwrite", False))
    result = initialize_workspace(root, overwrite=overwrite)
    result["context"] = context
    return result


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for local initialization."""
    parser = argparse.ArgumentParser(description="Initialize a Crypto Workbench target workspace.")
    parser.add_argument("root", nargs="?", default=".", help="Target project root.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing workbench files.",
    )
    args = parser.parse_args(argv)

    result = initialize_workspace(args.root, overwrite=args.overwrite)
    print(f"Initialized {result['workbench']}")
    print(f"Created directories: {len(result['created_dirs'])}")
    print(f"Created files: {len(result['created_files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
