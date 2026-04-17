"""Scan local corpus directories for source material.

Returns a structured inventory of all files in the corpus organized
by subdirectory (papers, standards, notes, drafts, prior_impls, fetched).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

MODULE = "corpus.scan_local"

CORPUS_SUBDIRS = ("papers", "standards", "notes", "drafts", "prior_impls", "fetched")


def _scan_subdir(directory: Path) -> list[dict[str, Any]]:
    """List files in a directory with basic metadata."""
    if not directory.exists():
        return []
    entries = []
    for f in sorted(directory.iterdir()):
        if f.is_file():
            entries.append({
                "name": f.name,
                "path": str(f),
                "size_bytes": f.stat().st_size,
                "suffix": f.suffix.lower(),
            })
    return entries


def scan_corpus(corpus_root: Path | str) -> dict[str, list[dict[str, Any]]]:
    """Scan all corpus subdirectories and return an inventory."""
    corpus_root = Path(corpus_root)
    result: dict[str, list[dict[str, Any]]] = {}
    for subdir_name in CORPUS_SUBDIRS:
        result[subdir_name] = _scan_subdir(corpus_root / subdir_name)
    return result


def run(**context: Any) -> dict[str, Any]:
    """Scan corpus from workflow context."""
    corpus_root = Path(context.get("corpus_root", ".cryptoworkbench/corpus"))
    inventory = scan_corpus(corpus_root)
    total = sum(len(v) for v in inventory.values())
    return {"module": MODULE, "status": "scanned", "total_files": total, "inventory": inventory}
