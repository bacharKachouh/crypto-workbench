"""Round 4 — composed-design artifact writer.

The composed design is the terminal artifact of `crypto-synthesize`. It
serves as the `primary source` that `crypto-extract-spec` operates on in
the back-half of the pipeline.

Invariants:
  - `classification` is hardcoded "Research prototype / novel construction".
    The caller cannot override it.
  - The `risk_ledger` is required and must be non-empty — composed
    designs always carry at least one proof-gap or composition risk note.
  - The per-paper contribution table must cover every paper from the
    triage artifact (a paper's role can be "rejected").
"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any

from artifacts.writer import write_markdown_artifact

MODULE = "synthesis.build_composed_design"

CLASSIFICATION = "Research prototype / novel construction"

_ROLES = {"backbone", "splice-source", "supporting-evidence", "counter-example", "rejected"}


def _validate_contributions(contributions: list[dict[str, str]]) -> None:
    if not contributions:
        raise ValueError("per-paper contribution table must not be empty")
    for entry in contributions:
        for key in ("paper_id", "role", "what_we_used", "why"):
            if key not in entry:
                raise ValueError(f"contribution entry missing {key!r}: {entry}")
        if entry["role"] not in _ROLES:
            raise ValueError(f"role must be one of {_ROLES}, got {entry['role']!r}")


def _render_contribution_table(contributions: list[dict[str, str]]) -> str:
    header = "| paper_id | role | what_we_used | why |"
    sep = "| --- | --- | --- | --- |"
    rows = [
        f"| {c['paper_id']} | {c['role']} | {c['what_we_used']} | {c['why']} |"
        for c in contributions
    ]
    return "\n".join([header, sep, *rows])


def build_composed_design(
    *,
    workbench_root: str | Path,
    target: str,
    title: str,
    created_from: str,
    scenario_summary: str,
    research_angle: str,
    backbone: dict[str, str],
    approved_splices: list[dict[str, str]],
    contributions: list[dict[str, str]],
    risk_ledger: list[str],
    pseudocode: str,
    related_sources: list[str] | None = None,
    related_artifacts: list[str] | None = None,
) -> Path:
    """Write the composed-design artifact.

    Required fields:
      - scenario_summary, research_angle — restated from the scenario artifact
      - backbone: dict with keys paper_id, reason
      - approved_splices: list of splice dicts (see build_splices)
      - contributions: list of {paper_id, role, what_we_used, why}
      - risk_ledger: list[str] — each risk as a one-line bullet
      - pseudocode: rendered pseudocode of the composed scheme (markdown block)

    Classification is hardcoded and cannot be overridden.
    """
    if "paper_id" not in backbone or "reason" not in backbone:
        raise ValueError("backbone must have keys paper_id and reason")
    _validate_contributions(contributions)
    if not risk_ledger:
        raise ValueError(
            "risk_ledger must be non-empty — every composed design carries at "
            "least one proof-gap or composition risk note"
        )

    workbench_root = Path(workbench_root)

    splices_yaml = yaml.dump(
        {"backbone": backbone, "approved_splices": approved_splices},
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

    risk_bullets = "\n".join(f"- {r}" for r in risk_ledger)
    contribution_md = _render_contribution_table(contributions)

    body_sections = [
        ("Classification", f"**{CLASSIFICATION}** — cannot be downgraded in the back-half pipeline."),
        ("Scenario", scenario_summary),
        ("Research Angle", research_angle),
        ("Backbone + Approved Splices", f"```yaml\n{splices_yaml}```"),
        ("Per-Paper Contribution Table", contribution_md),
        ("Risk Ledger", risk_bullets),
        ("Pseudocode", pseudocode),
    ]
    body = "\n".join(f"## {heading}\n\n{content}\n" for heading, content in body_sections)

    return write_markdown_artifact(
        artifact_type="composed_design",
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
    path = build_composed_design(
        workbench_root=workbench_root,
        **{k: v for k, v in context.items() if k != "workbench_root"},
    )
    return {"module": MODULE, "status": "built", "path": str(path), "classification": CLASSIFICATION}
