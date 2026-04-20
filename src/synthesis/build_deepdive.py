"""Round 2 — deep-dive artifact writer.

The deep-dive is a user-driven Q&A log per KEEP paper. Each Q+A records
the question, the answer, and a source_ref (paper section or review field)
so that claims stay traceable.
"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any

from artifacts.writer import write_markdown_artifact

MODULE = "synthesis.build_deepdive"


def build_deepdive(
    *,
    workbench_root: str | Path,
    target: str,
    title: str,
    created_from: str,
    logs: dict[str, list[dict[str, str]]],
    summary: str = "",
    related_sources: list[str] | None = None,
    related_artifacts: list[str] | None = None,
) -> Path:
    """Write a deep-dive artifact.

    `logs` maps paper_id → list of dicts with keys: q, a, source_ref.
    """
    workbench_root = Path(workbench_root)

    for paper_id, entries in logs.items():
        for entry in entries:
            for key in ("q", "a"):
                if key not in entry:
                    raise ValueError(f"deepdive entry for {paper_id!r} missing {key!r}: {entry}")

    logs_yaml = yaml.dump(
        {"logs": logs},
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

    body_sections = [
        ("Summary", summary or "_(to be filled)_"),
        ("Q&A Log", f"```yaml\n{logs_yaml}```"),
    ]
    body = "\n".join(f"## {heading}\n\n{content}\n" for heading, content in body_sections)

    return write_markdown_artifact(
        artifact_type="synthesis_deepdive",
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
    path = build_deepdive(workbench_root=workbench_root, **{k: v for k, v in context.items() if k != "workbench_root"})
    return {"module": MODULE, "status": "built", "path": str(path)}
