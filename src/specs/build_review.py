"""Build paper review artifacts from extracted source notes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from artifacts.writer import write_markdown_artifact

MODULE = "specs.build_review"


_VARIANTS_ALLOWED = {"yes", "no", "n/a"}


def _render_variants_section(
    variants_found: str,
    variants_reconciled: str,
    variants_list: list[dict[str, str]] | None,
) -> str:
    """Render the machine-parseable ## Variants section.

    `variants_list` entries must be dicts with keys: name, description,
    chosen (bool or "yes"/"no").
    """
    vf = variants_found.strip().lower()
    vr = variants_reconciled.strip().lower()
    if vf not in _VARIANTS_ALLOWED or vf == "n/a":
        raise ValueError(f"variants_found must be 'yes' or 'no', got {variants_found!r}")
    if vr not in _VARIANTS_ALLOWED:
        raise ValueError(f"variants_reconciled must be 'yes', 'no', or 'n/a', got {variants_reconciled!r}")
    if vf == "no" and vr != "n/a":
        raise ValueError("variants_reconciled must be 'n/a' when variants_found is 'no'")

    lines = [
        "## Variants",
        "",
        f"- variants_found: {vf}",
        f"- variants_reconciled: {vr}",
    ]
    if vf == "yes":
        if not variants_list:
            raise ValueError("variants_list must be non-empty when variants_found is 'yes'")
        lines.append("")
        for v in variants_list:
            name = v.get("name", "").strip()
            desc = v.get("description", "").strip()
            chosen = v.get("chosen", False)
            chosen_s = "yes" if (chosen is True or str(chosen).lower() == "yes") else "no"
            if not name:
                raise ValueError("each variant must have a non-empty 'name'")
            lines.append(f"- **{name}** (chosen: {chosen_s}) — {desc}")
    lines.append("")
    return "\n".join(lines)


def build_review(
    *,
    workbench_root: Path,
    target: str,
    title: str,
    created_from: str,
    source_version: str | None = None,
    source_digest: str | None = None,
    summary: str = "",
    contribution: str = "",
    threat_model: str = "",
    algorithms: str = "",
    security_claims: str = "",
    implementation_notes: str = "",
    version_comparison: str = "",
    open_questions: str = "",
    variants_found: str = "no",
    variants_reconciled: str = "n/a",
    variants_list: list[dict[str, str]] | None = None,
    related_sources: list[str] | None = None,
    related_artifacts: list[str] | None = None,
) -> Path:
    """Build and write a review artifact.

    The body includes a required `## Variants` section with machine-parseable
    `variants_found` / `variants_reconciled` lines. `crypto-paper-review`
    Step 7 reads those values to decide whether to trigger the fork gate.
    """
    sections = [
        ("Summary", summary),
        ("Contribution", contribution),
        ("Threat Model and Assumptions", threat_model),
        ("Algorithms and Parameters", algorithms),
        ("Security Claims", security_claims),
        ("Implementation Notes", implementation_notes),
        ("Version Comparison", version_comparison),
        ("Open Questions", open_questions),
    ]
    body_parts = []
    for heading, content in sections:
        body_parts.append(f"## {heading}\n\n{content}\n")
    body_parts.append(_render_variants_section(variants_found, variants_reconciled, variants_list))
    body = "\n".join(body_parts)

    return write_markdown_artifact(
        artifact_type="review",
        target=target,
        title=title,
        created_from=created_from,
        body=body,
        workbench_root=workbench_root,
        source_version=source_version,
        source_digest=source_digest,
        related_sources=related_sources,
        related_artifacts=related_artifacts,
    )


def run(**context: Any) -> dict[str, Any]:
    """Build a review from workflow context."""
    workbench_root = Path(context.get("workbench_root", ".cryptoworkbench"))
    path = build_review(workbench_root=workbench_root, **{k: v for k, v in context.items() if k != "workbench_root"})
    return {"module": MODULE, "status": "built", "path": str(path)}
