"""Build source index artifacts from classified corpus inventory."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from artifacts.writer import write_yaml_artifact

MODULE = "specs.build_source_index"


def build_source_index(
    *,
    workbench_root: Path,
    target: str,
    created_from: str,
    sources: list[dict[str, Any]],
    source_version: str | None = None,
    source_digest: str | None = None,
    related_sources: list[str] | None = None,
    related_artifacts: list[str] | None = None,
) -> Path:
    """Build and write a source index artifact."""
    content = {"sources": sources}
    return write_yaml_artifact(
        artifact_type="source_index",
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
    """Build source index from workflow context."""
    workbench_root = Path(context.get("workbench_root", ".cryptoworkbench"))
    path = build_source_index(workbench_root=workbench_root, **{k: v for k, v in context.items() if k != "workbench_root"})
    return {"module": MODULE, "status": "built", "path": str(path)}
