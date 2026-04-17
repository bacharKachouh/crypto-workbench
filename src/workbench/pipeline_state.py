"""Report the workbench's current pipeline state.

Pure read-only. No artifacts written, no decisions made, no side effects.
Consumed by the `crypto-status` skill to give the user a clear "where am I?"
readout at any point in the workflow.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from workbench.target import load_target


STAGE_ORDER = [
    "source_indexes",
    "reviews",
    "notation_maps",
    "ambiguity_logs",
    "impl_specs",
    "library_mappings",
    "implementations",
    "security_reviews",
]

STAGE_TO_NEXT_SKILL = {
    None: "crypto-init",
    "source_indexes": "crypto-paper-review",
    "reviews": "crypto-extract-spec",
    "notation_maps": "crypto-extract-spec",
    "ambiguity_logs": "crypto-extract-spec",
    "impl_specs": "crypto-library-map",
    "library_mappings": "crypto-plan-review",
    "implementations": "crypto-security-review",
    "security_reviews": None,
}


def _count_artifacts(extracted_root: Path, stage: str, target: str) -> int:
    """Count artifact files for a given stage + target."""
    stage_dir = extracted_root / stage
    if not stage_dir.exists():
        return 0
    return sum(
        1
        for p in stage_dir.iterdir()
        if p.is_file() and target in p.stem and p.suffix in (".md", ".yml", ".yaml")
    )


def _count_lines(path: Path, non_empty: bool = False) -> int:
    if not path.exists():
        return 0
    lines = path.read_text(encoding="utf-8").splitlines()
    if non_empty:
        return sum(1 for l in lines if l.strip() and not l.strip().startswith("#"))
    return len(lines)


def get_state(workbench_root: Path | str = ".cryptoworkbench") -> dict[str, Any]:
    """Read the workbench and return a structured state report."""
    workbench_root = Path(workbench_root)
    if not workbench_root.exists():
        return {
            "workbench_exists": False,
            "next_skill": "crypto-init",
            "message": "No workbench found. Run crypto-init first.",
        }

    target = load_target(workbench_root)
    extracted_root = workbench_root / "extracted"
    workbench_dir = workbench_root / "workbench"

    target_name = target.get("name", "")
    target_status = target.get("status", "unknown")
    target_deferred = not target_name or target_status == "draft"

    stage_counts: dict[str, int] = {}
    for stage in STAGE_ORDER:
        stage_counts[stage] = (
            _count_artifacts(extracted_root, stage, target_name) if target_name else 0
        )

    # Find the deepest stage with an artifact — that's where the pipeline sits.
    last_stage: str | None = None
    if target_name:
        for stage in STAGE_ORDER:
            if stage_counts.get(stage, 0) > 0:
                last_stage = stage

    next_skill = STAGE_TO_NEXT_SKILL.get(last_stage)
    if target_deferred:
        next_skill = "crypto-init"
    elif last_stage is None:
        next_skill = "crypto-intake"

    open_questions_count = max(_count_lines(workbench_dir / "open_questions.md", non_empty=True) - 1, 0)
    decisions_lines = _count_lines(workbench_dir / "decisions.md", non_empty=True)

    return {
        "workbench_exists": True,
        "workbench_root": str(workbench_root),
        "target": {
            "name": target_name or None,
            "type": target.get("type", "") or None,
            "status": target_status,
            "primary_sources": target.get("primary_sources", []),
            "deferred": target_deferred,
        },
        "stage_counts": stage_counts,
        "last_stage": last_stage,
        "next_skill": next_skill,
        "open_questions_nonempty_lines": open_questions_count,
        "decisions_nonempty_lines": decisions_lines,
    }


def format_state(state: dict[str, Any]) -> str:
    """Render the state dict as a short human-readable report."""
    if not state.get("workbench_exists"):
        return f"No workbench. Next: {state.get('next_skill')}"

    t = state["target"]
    name = t["name"] or "<deferred>"
    lines = [
        f"Workbench: {state['workbench_root']}",
        f"Target:    {name}  (type: {t['type'] or '?'}, status: {t['status']})",
    ]
    if t["deferred"]:
        lines.append("           -> TARGET IS DEFERRED; run crypto-init to pick a target.")
    if t["primary_sources"]:
        lines.append(f"Sources:   {', '.join(str(s) for s in t['primary_sources'])}")

    lines.append("")
    lines.append("Pipeline progress:")
    for stage in STAGE_ORDER:
        count = state["stage_counts"].get(stage, 0)
        marker = "x" if count else " "
        lines.append(f"  [{marker}] {stage:<18} ({count} artifact{'s' if count != 1 else ''})")

    lines.append("")
    lines.append(f"Open questions:  {state['open_questions_nonempty_lines']} non-empty line(s)")
    lines.append(f"Decisions log:   {state['decisions_nonempty_lines']} non-empty line(s)")

    nxt = state.get("next_skill")
    if nxt:
        lines.append("")
        lines.append(f"Next recommended skill: {nxt}")
    else:
        lines.append("")
        lines.append("Pipeline end reached - target has gone through security review.")

    return "\n".join(lines)


def run(**context: Any) -> dict[str, Any]:
    """Workflow entry for `crypto-status`."""
    workbench_root = context.get("workbench_root", ".cryptoworkbench")
    state = get_state(workbench_root)
    return {
        "module": "workbench.pipeline_state",
        "status": "read",
        "state": state,
        "report": format_state(state),
    }
