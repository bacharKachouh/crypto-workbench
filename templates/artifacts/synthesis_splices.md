---
id: synthesis-splices-<target>-<sequence>
title: "<Target> Synthesis — Round 3 Splice Proposals"
artifact_type: synthesis_splices
status: draft
created_from: <deepdive artifact id>
related_sources:
  []
related_artifacts:
  []
target: <target>
created_at: <ISO 8601>
updated_at: <ISO 8601>
---

## Summary

<One paragraph: chosen backbone, count of splices proposed / approved / rejected, flavor of the splices (parameter substitutions vs. algorithm-stage replacements).>

## Backbone + Splice Decisions

```yaml
backbone:
  paper_id: <id>
  reason: <why this paper was chosen as the skeleton>
decisions:
  - borrowed_piece: <specific algorithmic component>
    into: <location in the backbone>
    source_paper: <donor paper id>
    scenario_justification: <why this improves fit>
    proof_gap_note: <what proof/assumption gap this introduces>
    status: approve|reject|tweak
    user_reason: <optional free-form note>
```
