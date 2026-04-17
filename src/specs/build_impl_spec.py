"""Build implementation-facing cryptographic specifications."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from artifacts.writer import write_markdown_artifact

MODULE = "specs.build_impl_spec"


def build_impl_spec(
    *,
    workbench_root: Path,
    target: str,
    title: str,
    created_from: str,
    source_version: str | None = None,
    source_digest: str | None = None,
    classification: str = "",
    summary: str = "",
    data_types: str = "",
    module_boundaries: str = "",
    function_signatures: str = "",
    randomness_requirements: str = "",
    serialization_rules: str = "",
    parameter_constraints: str = "",
    test_plan_kat: str = "",
    test_plan_edge_cases: str = "",
    test_plan_negative: str = "",
    test_plan_serialization: str = "",
    test_plan_failure: str = "",
    test_plan_coverage: str = "",
    dependencies: str = "",
    related_sources: list[str] | None = None,
    related_artifacts: list[str] | None = None,
) -> Path:
    """Build and write an implementation spec artifact."""
    body = f"""## Summary

{summary}

**Implementation classification:** {classification}

## Data Types

{data_types}

## Module Boundaries

{module_boundaries}

## Function Signatures

{function_signatures}

## Randomness Requirements

{randomness_requirements}

## Serialization Rules

{serialization_rules}

## Parameter Constraints

{parameter_constraints}

## Test Plan

### Known-Answer Vectors

{test_plan_kat}

### Edge Cases

{test_plan_edge_cases}

### Negative and Invalid-Input Tests

{test_plan_negative}

### Serialization Round-Trip Tests

{test_plan_serialization}

### Failure-Mode Tests

{test_plan_failure}

### Coverage Goals

{test_plan_coverage}

## Dependencies

{dependencies}

## Implementation Classification Label

{classification}
"""

    return write_markdown_artifact(
        artifact_type="impl_spec",
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
    """Build an impl spec from workflow context."""
    workbench_root = Path(context.get("workbench_root", ".cryptoworkbench"))
    path = build_impl_spec(workbench_root=workbench_root, **{k: v for k, v in context.items() if k != "workbench_root"})
    return {"module": MODULE, "status": "built", "path": str(path)}
