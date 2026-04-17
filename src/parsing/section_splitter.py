"""Split source text into section-level units.

Status: placeholder for future automation.
Not required for the current plugin workflow — the agent reads
and splits documents directly during analysis.
"""

from __future__ import annotations

from typing import Any

MODULE = "parsing.section_splitter"


def run(**context: Any) -> dict[str, Any]:
    """Return scaffold metadata for this workflow stage."""
    return {"module": MODULE, "status": "scaffold", "context": context}
