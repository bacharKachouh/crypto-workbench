"""Rank source material for review priority."""

from __future__ import annotations

from typing import Any

MODULE = "corpus.rank_sources"

_AUTHORITY_SCORES = {
    "canonical": 100,
    "supplementary": 50,
    "informal": 20,
    "unknown": 10,
}

_DOC_TYPE_SCORES = {
    "pdf": 30,
    "latex": 25,
    "markdown": 15,
    "text": 10,
    "code": 20,
    "yaml": 5,
    "json": 5,
    "unknown": 0,
}


def rank_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Add a priority_score to a classified entry."""
    authority_score = _AUTHORITY_SCORES.get(entry.get("authority", "unknown"), 0)
    doc_score = _DOC_TYPE_SCORES.get(entry.get("doc_type", "unknown"), 0)
    score = authority_score + doc_score
    return {**entry, "priority_score": score}


def rank_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank a list of classified entries by priority, highest first."""
    ranked = [rank_entry(e) for e in entries]
    ranked.sort(key=lambda e: e["priority_score"], reverse=True)
    return ranked


def run(**context: Any) -> dict[str, Any]:
    """Rank entries from workflow context."""
    entries = context.get("entries", [])
    ranked = rank_entries(entries)
    return {"module": MODULE, "status": "ranked", "count": len(ranked), "entries": ranked}
