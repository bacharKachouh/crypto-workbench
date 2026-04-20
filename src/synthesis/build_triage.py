"""Round 1 — triage artifact writer.

Each paper in the scenario receives one of three labels:
  - KEEP: contender for backbone
  - REJECT: threat-model or correctness mismatch
  - SUPPORTING: useful for evidence/attacks/proof technique, not a backbone

The artifact records both Claude's proposed label and the user's final
label per paper so the decision trail is preserved.
"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any

from artifacts.writer import write_markdown_artifact

MODULE = "synthesis.build_triage"

_ALLOWED_LABELS = {"KEEP", "REJECT", "SUPPORTING"}


def _validate_decisions(decisions: list[dict[str, str]]) -> None:
    for d in decisions:
        for key in ("paper_id", "proposed", "final"):
            if key not in d:
                raise ValueError(f"triage decision missing required key {key!r}: {d}")
        if d["proposed"] not in _ALLOWED_LABELS:
            raise ValueError(f"proposed label must be one of {_ALLOWED_LABELS}, got {d['proposed']!r}")
        if d["final"] not in _ALLOWED_LABELS:
            raise ValueError(f"final label must be one of {_ALLOWED_LABELS}, got {d['final']!r}")


def build_triage(
    *,
    workbench_root: str | Path,
    target: str,
    title: str,
    created_from: str,
    decisions: list[dict[str, str]],
    summary: str = "",
    round_status: str = "completed",
    related_sources: list[str] | None = None,
    related_artifacts: list[str] | None = None,
) -> Path:
    """Write a triage artifact.

    `decisions` is a list of dicts with keys: paper_id, proposed, final, reason.
    `round_status` is `completed` normally, or `all_rejected` if every paper
    was rejected — the synthesis skill uses this to halt and re-enter scenario.
    """
    _validate_decisions(decisions)
    workbench_root = Path(workbench_root)

    decisions_yaml = yaml.dump(
        {"round_status": round_status, "decisions": decisions},
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

    body_sections = [
        ("Summary", summary or "_(to be filled)_"),
        ("Decisions", f"```yaml\n{decisions_yaml}```"),
    ]
    body = "\n".join(f"## {heading}\n\n{content}\n" for heading, content in body_sections)

    return write_markdown_artifact(
        artifact_type="synthesis_triage",
        target=target,
        title=title,
        created_from=created_from,
        body=body,
        workbench_root=workbench_root,
        related_sources=related_sources,
        related_artifacts=related_artifacts,
    )


def run(**context: Any) -> dict[str, Any]:
    workbench_root = Path(context.get("workbench_root", ".cryptoworkbench"))
    path = build_triage(workbench_root=workbench_root, **{k: v for k, v in context.items() if k != "workbench_root"})
    return {"module": MODULE, "status": "built", "path": str(path)}
