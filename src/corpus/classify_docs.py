"""Classify corpus documents by type, authority, and target relevance."""

from __future__ import annotations

from typing import Any

MODULE = "corpus.classify_docs"

_DOC_TYPE_MAP = {
    ".pdf": "pdf",
    ".md": "markdown",
    ".txt": "text",
    ".tex": "latex",
    ".py": "code",
    ".c": "code",
    ".h": "code",
    ".rs": "code",
    ".go": "code",
    ".js": "code",
    ".ts": "code",
    ".java": "code",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".json": "json",
}

_SUBDIR_AUTHORITY = {
    "papers": "canonical",
    "standards": "canonical",
    "notes": "informal",
    "drafts": "supplementary",
    "prior_impls": "supplementary",
    "fetched": "supplementary",
}


def classify_entry(entry: dict[str, Any], subdir: str) -> dict[str, Any]:
    """Classify a single corpus entry."""
    suffix = entry.get("suffix", "").lower()
    doc_type = _DOC_TYPE_MAP.get(suffix, "unknown")
    authority = _SUBDIR_AUTHORITY.get(subdir, "unknown")
    return {**entry, "doc_type": doc_type, "authority": authority, "subdir": subdir}


def classify_inventory(inventory: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Classify all entries in a corpus inventory."""
    classified = []
    for subdir, entries in inventory.items():
        for entry in entries:
            classified.append(classify_entry(entry, subdir))
    return classified


def run(**context: Any) -> dict[str, Any]:
    """Classify documents from workflow context."""
    inventory = context.get("inventory", {})
    classified = classify_inventory(inventory)
    return {"module": MODULE, "status": "classified", "count": len(classified), "entries": classified}
