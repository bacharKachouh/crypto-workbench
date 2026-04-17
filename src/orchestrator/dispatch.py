"""Dispatch work to local workflow stages and agent adapters.

Status: placeholder for future automation.
Not required for the current plugin workflow — work dispatch
is handled by the skill layer (SKILL.md files).
"""

from __future__ import annotations

from typing import Any

MODULE = "orchestrator.dispatch"


def run(**context: Any) -> dict[str, Any]:
    """Return scaffold metadata for this workflow stage."""
    return {"module": MODULE, "status": "scaffold", "context": context}
