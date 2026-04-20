---
id: synthesis-triage-<target>-<sequence>
title: "<Target> Synthesis — Round 1 Triage"
artifact_type: synthesis_triage
status: draft
created_from: <scenario artifact id>
related_sources:
  []
related_artifacts:
  []
target: <target>
created_at: <ISO 8601>
updated_at: <ISO 8601>
---

## Summary

<One paragraph: total papers triaged, how many KEEP / REJECT / SUPPORTING, whether Round 2 is appropriate or the flow should halt.>

## Decisions

```yaml
round_status: completed   # or all_rejected if every paper was rejected
decisions:
  - paper_id: <id>
    proposed: KEEP|REJECT|SUPPORTING
    final: KEEP|REJECT|SUPPORTING
    reason: <why Claude proposed this and what the user did with it>
```
