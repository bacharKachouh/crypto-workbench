"""Build notation maps for cryptographic implementations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from artifacts.writer import write_yaml_artifact

MODULE = "specs.build_notation_map"


def build_notation_map(
    *,
    workbench_root: Path,
    target: str,
    created_from: str,
    symbols: list[dict[str, str]],
    conventions: list[str] | None = None,
    conflicts: list[str] | None = None,
    source_version: str | None = None,
    source_digest: str | None = None,
    related_sources: list[str] | None = None,
    related_artifacts: list[str] | None = None,
) -> Path:
    """Build and write a notation map artifact."""
    content = {
        "symbols": symbols,
        "conventions": conventions or [],
        "conflicts": conflicts or [],
    }
    return write_yaml_artifact(
        artifact_type="notation_map",
        target=target,
        created_from=created_from,
        content=content,
        workbench_root=workbench_root,
        source_version=source_version,
        source_digest=source_digest,
        related_sources=related_sources,
        related_artifacts=related_artifacts,
    )


def run(**context: Any) -> dict[str, Any]:
    """Build a notation map from workflow context."""
    workbench_root = Path(context.get("workbench_root", ".cryptoworkbench"))
    path = build_notation_map(workbench_root=workbench_root, **{k: v for k, v in context.items() if k != "workbench_root"})
    return {"module": MODULE, "status": "built", "path": str(path)}
