"""Build ambiguity logs for unresolved specification questions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from artifacts.writer import write_markdown_artifact

MODULE = "specs.build_ambiguity_log"


def build_ambiguity_log(
    *,
    workbench_root: Path,
    target: str,
    title: str,
    created_from: str,
    source_version: str | None = None,
    source_digest: str | None = None,
    summary: str = "",
    ambiguities: list[dict[str, str]] | None = None,
    resolved_items: str = "",
    remaining_blockers: str = "",
    related_sources: list[str] | None = None,
    related_artifacts: list[str] | None = None,
) -> Path:
    """Build and write an ambiguity log artifact."""
    amb_section = ""
    for i, amb in enumerate(ambiguities or [], start=1):
        amb_section += f"### AMB-{i:03d}: {amb.get('title', 'Untitled')}\n\n"
        amb_section += f"- **Description:** {amb.get('description', '')}\n"
        amb_section += f"- **Source location:** {amb.get('source_location', '')}\n"
        amb_section += f"- **Impact on implementation:** {amb.get('impact', '')}\n"
        amb_section += f"- **Resolution options:** {amb.get('resolution_options', '')}\n"
        amb_section += f"- **Current status:** {amb.get('status', 'open')}\n\n"

    body = f"## Summary\n\n{summary}\n\n## Ambiguities\n\n{amb_section}## Resolved Items\n\n{resolved_items}\n\n## Remaining Blockers\n\n{remaining_blockers}\n"

    return write_markdown_artifact(
        artifact_type="ambiguity_log",
        target=target,
        title=title,
        created_from=created_from,
        body=body,
        workbench_root=workbench_root,
        source_version=source_version,
        source_digest=source_digest,
        related_sources=related_sources,
        related_artifacts=related_artifacts,
    )


def run(**context: Any) -> dict[str, Any]:
    """Build an ambiguity log from workflow context."""
    workbench_root = Path(context.get("workbench_root", ".cryptoworkbench"))
    path = build_ambiguity_log(workbench_root=workbench_root, **{k: v for k, v in context.items() if k != "workbench_root"})
    return {"module": MODULE, "status": "built", "path": str(path)}
