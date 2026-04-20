"""Build scenario artifacts for topic-mode targets.

The scenario artifact is the authoritative use-case document for a
multi-paper synthesis target. It records:

- the real-world scenario prose
- the user-declared research angle
- the registry-backed sanity-check outcome (and any override justification)
- the list of papers collected for the synthesis (path + sha256 + role)
- any corpus/online-search open questions
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from artifacts.writer import write_markdown_artifact

MODULE = "scenarios.build_scenario"


def _render_paper_list(papers: list[dict[str, str]] | None) -> str:
    if not papers:
        return "_No papers recorded yet._\n"
    lines = []
    for p in papers:
        path = p.get("path", "")
        sha = p.get("sha256", "")
        role = p.get("role", "")
        line = f"- `{path}`"
        if sha:
            line += f" (sha256: `{sha[:12]}...`)"
        if role:
            line += f" — role: {role}"
        lines.append(line)
    return "\n".join(lines) + "\n"


def _render_rejected_standards(entries: list[dict[str, str]] | None) -> str:
    if not entries:
        return "_No standard-primitive matches rejected._\n"
    lines = []
    for e in entries:
        primitive = e.get("primitive", "")
        reason = e.get("user_justification", "")
        lines.append(f"- **{primitive}** — overridden by user. Justification: {reason}")
    return "\n".join(lines) + "\n"


def build_scenario(
    *,
    workbench_root: str | Path,
    target: str,
    title: str,
    created_from: str = "user",
    scenario_prose: str = "",
    research_angle: str = "",
    rejected_standards: list[dict[str, str]] | None = None,
    papers: list[dict[str, str]] | None = None,
    open_questions: str = "",
    related_sources: list[str] | None = None,
    related_artifacts: list[str] | None = None,
) -> Path:
    """Write a scenario artifact.

    `papers` is a list of dicts with keys: path, sha256, role (optional).
    `rejected_standards` records primitives the registry flagged as
    standard, along with the user's justification for overriding.
    """
    workbench_root = Path(workbench_root)

    sections = [
        ("Scenario", scenario_prose or "_(to be filled)_"),
        ("Research Angle", research_angle or "_(to be filled)_"),
        ("Rejected Standard Primitives", _render_rejected_standards(rejected_standards)),
        ("Papers", _render_paper_list(papers)),
        ("Open Questions", open_questions or "_None recorded._"),
    ]
    body = "\n".join(f"## {heading}\n\n{content}\n" for heading, content in sections)

    return write_markdown_artifact(
        artifact_type="scenario",
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
    path = build_scenario(workbench_root=workbench_root, **{k: v for k, v in context.items() if k != "workbench_root"})
    return {"module": MODULE, "status": "built", "path": str(path)}
