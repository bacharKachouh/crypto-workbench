"""Artifact filename and path generation.

Naming convention: <artifact-type-slug>-<target-slug>-<sequence>.<ext>
"""

from __future__ import annotations

import re
from pathlib import Path

from artifacts.metadata import _TYPE_SLUGS

# Artifact types that use Markdown format.
_MARKDOWN_TYPES = {"review", "ambiguity_log", "impl_spec", "security_review", "design_note", "comparison", "implementation"}

# Artifact types that use YAML format.
_YAML_TYPES = {"notation_map", "library_mapping", "test_vectors", "source_index"}

# Maps artifact_type to its extracted/ subdirectory name.
_TYPE_DIRS = {
    "review": "reviews",
    "ambiguity_log": "ambiguity_logs",
    "impl_spec": "impl_specs",
    "security_review": "security_reviews",
    "design_note": "reviews",
    "comparison": "reviews",
    "notation_map": "notation_maps",
    "library_mapping": "library_mappings",
    "test_vectors": "test_vectors",
    "source_index": "source_indexes",
    "implementation": "implementations",
}


def artifact_filename(artifact_type: str, target: str, sequence: int) -> str:
    """Generate the filename for an artifact."""
    slug = _TYPE_SLUGS.get(artifact_type, artifact_type)
    ext = "md" if artifact_type in _MARKDOWN_TYPES else "yml"
    return f"{slug}-{target}-{sequence:03d}.{ext}"


def artifact_path(
    artifact_type: str,
    target: str,
    sequence: int,
    workbench_root: Path,
) -> Path:
    """Generate the full path for an artifact within the workspace."""
    workbench_root = Path(workbench_root)
    subdir = _TYPE_DIRS.get(artifact_type, artifact_type)
    fname = artifact_filename(artifact_type, target, sequence)
    return workbench_root / "extracted" / subdir / fname


def next_sequence_number(artifact_type: str, target: str, directory: Path) -> int:
    """Find the next available sequence number for an artifact type + target in a directory."""
    slug = _TYPE_SLUGS.get(artifact_type, artifact_type)
    pattern = re.compile(rf"^{re.escape(slug)}-{re.escape(target)}-(\d{{3}})\.\w+$")
    max_seq = 0
    if directory.exists():
        for entry in directory.iterdir():
            m = pattern.match(entry.name)
            if m:
                max_seq = max(max_seq, int(m.group(1)))
    return max_seq + 1
