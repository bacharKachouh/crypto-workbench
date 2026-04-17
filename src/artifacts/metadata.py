"""Generate artifact metadata for the Crypto Workbench artifact system.

Supports both Markdown frontmatter (for analytical artifacts) and YAML
header dicts (for structured artifacts), per the artifact format policy.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Maps artifact_type values to the slug used in IDs and filenames.
_TYPE_SLUGS = {
    "review": "review",
    "ambiguity_log": "ambiguity-log",
    "impl_spec": "impl-spec",
    "security_review": "security-review",
    "design_note": "design-note",
    "comparison": "comparison",
    "notation_map": "notation-map",
    "library_mapping": "library-mapping",
    "test_vectors": "test-vectors",
    "source_index": "source-index",
    "implementation": "implementation",
}


def generate_artifact_id(artifact_type: str, target: str, sequence: int = 1) -> str:
    """Build an artifact ID: <type-slug>-<target>-<sequence>.

    Raises ValueError if target is empty or sequence < 1.
    """
    if not target:
        raise ValueError("target must not be empty")
    if sequence < 1:
        raise ValueError("sequence must be >= 1")
    slug = _TYPE_SLUGS.get(artifact_type, artifact_type)
    return f"{slug}-{target}-{sequence:03d}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def build_markdown_frontmatter(
    *,
    artifact_type: str,
    target: str,
    title: str,
    created_from: str,
    source_version: str | None = None,
    source_digest: str | None = None,
    related_sources: list[str] | None = None,
    related_artifacts: list[str] | None = None,
    sequence: int = 1,
) -> str:
    """Build YAML frontmatter string for a Markdown artifact.

    Returns a string starting and ending with '---\\n'.
    """
    now = _now_iso()
    artifact_id = generate_artifact_id(artifact_type, target, sequence)

    lines = [
        "---",
        f"id: {artifact_id}",
        f"title: {title}",
        f"artifact_type: {artifact_type}",
        "status: draft",
        f"created_from: '{created_from}'" if ":" in created_from else f"created_from: {created_from}",
    ]
    if source_version is not None:
        lines.append(f"source_version: {source_version}")
    if source_digest is not None:
        lines.append(f"source_digest: {source_digest}")

    sources = related_sources or []
    lines.append("related_sources:")
    if sources:
        for s in sources:
            lines.append(f"  - {s}")
    else:
        lines.append("  []")

    artifacts = related_artifacts or []
    lines.append("related_artifacts:")
    if artifacts:
        for a in artifacts:
            lines.append(f"  - {a}")
    else:
        lines.append("  []")

    lines.append(f"target: {target}")
    lines.append(f"created_at: {now}")
    lines.append(f"updated_at: {now}")
    lines.append("---")

    return "\n".join(lines) + "\n"


def build_yaml_header(
    *,
    artifact_type: str,
    target: str,
    created_from: str,
    source_version: str | None = None,
    source_digest: str | None = None,
    related_sources: list[str] | None = None,
    related_artifacts: list[str] | None = None,
    sequence: int = 1,
) -> dict[str, Any]:
    """Build a metadata dict for a YAML-first artifact.

    Returns a dict with all required top-level keys per the spec.
    """
    now = _now_iso()
    artifact_id = generate_artifact_id(artifact_type, target, sequence)

    header: dict[str, Any] = {
        "artifact_type": artifact_type,
        "id": artifact_id,
        "status": "draft",
        "target": target,
        "created_from": created_from,
    }
    if source_version is not None:
        header["source_version"] = source_version
    if source_digest is not None:
        header["source_digest"] = source_digest

    header["related_sources"] = related_sources or []
    header["related_artifacts"] = related_artifacts or []
    header["created_at"] = now
    header["updated_at"] = now

    return header


def compute_source_digest(path: Path) -> str:
    """Compute SHA-256 hex digest of a file.

    Raises FileNotFoundError if the file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path}")
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
