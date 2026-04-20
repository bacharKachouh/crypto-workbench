---
id: composed-design-<target>-<sequence>
title: "<Target> Composed Design"
artifact_type: composed_design
status: draft
created_from: <splices artifact id>
related_sources:
  []
related_artifacts:
  []
target: <target>
created_at: <ISO 8601>
updated_at: <ISO 8601>
---

## Classification

**Research prototype / novel construction** — cannot be downgraded in the back-half pipeline.

## Scenario

<Restatement of the real-world use case from the scenario artifact.>

## Research Angle

<Restatement of the user's declared research angle.>

## Backbone + Approved Splices

```yaml
backbone:
  paper_id: <id>
  reason: <why chosen>
approved_splices:
  - borrowed_piece: <component>
    into: <location>
    source_paper: <paper id>
    scenario_justification: <reason>
    proof_gap_note: <gap / new assumption>
```

## Per-Paper Contribution Table

| paper_id | role | what_we_used | why |
| --- | --- | --- | --- |
| <id> | backbone / splice-source / supporting-evidence / counter-example / rejected | <component or evidence used> | <scenario-tied reason> |

## Risk Ledger

- <Every proof gap, compound assumption, or novel-composition risk surfaced during the rounds. Must be non-empty.>

## Pseudocode

<Pseudocode of the composed scheme, with inline attribution of which paper each step or component comes from.>
