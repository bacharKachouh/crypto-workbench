"""Write artifacts to the .cryptoworkbench workspace.

Markdown artifacts get YAML frontmatter + body.
YAML artifacts get metadata header merged with structured content.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from artifacts.metadata import build_markdown_frontmatter, build_yaml_header
from artifacts.naming import artifact_path, next_sequence_number, _TYPE_DIRS


def write_markdown_artifact(
    *,
    artifact_type: str,
    target: str,
    title: str,
    created_from: str,
    body: str,
    workbench_root: Path,
    source_version: str | None = None,
    source_digest: str | None = None,
    related_sources: list[str] | None = None,
    related_artifacts: list[str] | None = None,
    sequence: int | None = None,
) -> Path:
    """Write a Markdown artifact with YAML frontmatter.

    Returns the path of the written file.
    """
    subdir = _TYPE_DIRS.get(artifact_type, artifact_type)
    target_dir = workbench_root / "extracted" / subdir

    if sequence is None:
        sequence = next_sequence_number(artifact_type, target, target_dir)

    frontmatter = build_markdown_frontmatter(
        artifact_type=artifact_type,
        target=target,
        title=title,
        created_from=created_from,
        source_version=source_version,
        source_digest=source_digest,
        related_sources=related_sources,
        related_artifacts=related_artifacts,
        sequence=sequence,
    )

    path = artifact_path(artifact_type, target, sequence, workbench_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(frontmatter + "\n" + body, encoding="utf-8")
    return path


def write_yaml_artifact(
    *,
    artifact_type: str,
    target: str,
    created_from: str,
    content: dict[str, Any],
    workbench_root: Path,
    source_version: str | None = None,
    source_digest: str | None = None,
    related_sources: list[str] | None = None,
    related_artifacts: list[str] | None = None,
    sequence: int | None = None,
) -> Path:
    """Write a YAML-first artifact with metadata header merged with content.

    Returns the path of the written file.
    """
    subdir = _TYPE_DIRS.get(artifact_type, artifact_type)
    target_dir = workbench_root / "extracted" / subdir

    if sequence is None:
        sequence = next_sequence_number(artifact_type, target, target_dir)

    header = build_yaml_header(
        artifact_type=artifact_type,
        target=target,
        created_from=created_from,
        source_version=source_version,
        source_digest=source_digest,
        related_sources=related_sources,
        related_artifacts=related_artifacts,
        sequence=sequence,
    )

    merged = {**header, **content}
    path = artifact_path(artifact_type, target, sequence, workbench_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.dump(merged, default_flow_style=False, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path
