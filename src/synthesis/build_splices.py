"""Round 3 — splice-proposals artifact writer.

Each splice carries five mandatory fields:
  1. borrowed_piece — specific algorithmic component
  2. into — location in the backbone where it slots
  3. source_paper — paper id of the donor
  4. scenario_justification — why the splice improves fit
  5. proof_gap_note — what proof/assumption gap the splice introduces

User status per splice is `approve`, `reject`, or `tweak`.
"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any

from artifacts.writer import write_markdown_artifact

MODULE = "synthesis.build_splices"

_ALLOWED_STATUS = {"approve", "reject", "tweak"}
_REQUIRED_FIELDS = (
    "borrowed_piece",
    "into",
    "source_paper",
    "scenario_justification",
    "proof_gap_note",
    "status",
)


def _validate_decisions(decisions: list[dict[str, str]]) -> None:
    for d in decisions:
        for key in _REQUIRED_FIELDS:
            if key not in d:
                raise ValueError(f"splice decision missing required key {key!r}: {d}")
        if d["status"] not in _ALLOWED_STATUS:
            raise ValueError(f"splice status must be one of {_ALLOWED_STATUS}, got {d['status']!r}")


def build_splices(
    *,
    workbench_root: str | Path,
    target: str,
    title: str,
    created_from: str,
    backbone: dict[str, str],
    decisions: list[dict[str, str]],
    summary: str = "",
    related_sources: list[str] | None = None,
    related_artifacts: list[str] | None = None,
) -> Path:
    """Write a splice-proposals artifact.

    `backbone` must have keys: paper_id, reason.
    `decisions` is a list of splice dicts with the five mandatory fields
    plus `status` (approve / reject / tweak) and optional `user_reason`.
    """
    if "paper_id" not in backbone or "reason" not in backbone:
        raise ValueError("backbone must have keys paper_id and reason")
    _validate_decisions(decisions)

    workbench_root = Path(workbench_root)
    payload_yaml = yaml.dump(
        {"backbone": backbone, "decisions": decisions},
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

    body_sections = [
        ("Summary", summary or "_(to be filled)_"),
        ("Backbone + Splice Decisions", f"```yaml\n{payload_yaml}```"),
    ]
    body = "\n".join(f"## {heading}\n\n{content}\n" for heading, content in body_sections)

    return write_markdown_artifact(
        artifact_type="synthesis_splices",
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
    path = build_splices(workbench_root=workbench_root, **{k: v for k, v in context.items() if k != "workbench_root"})
    return {"module": MODULE, "status": "built", "path": str(path)}
