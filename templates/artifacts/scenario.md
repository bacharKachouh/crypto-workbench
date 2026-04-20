---
id: scenario-<target>-<sequence>
title: "<Target> Scenario"
artifact_type: scenario
status: draft
created_from: user
related_sources:
  []
related_artifacts:
  []
target: <target>
created_at: <ISO 8601>
updated_at: <ISO 8601>
---

## Scenario

<Plain-prose description of the real-world use case: what is being built, who the user is, deployment constraints, threat model, performance budget, any compliance/standardization requirements.>

## Research Angle

<User's declared justification for why this is a research problem: what standard approaches fall short, what novel combination or constraint makes it research-grade.>

## Rejected Standard Primitives

<List every primitive that the `research_angle_check` flagged as standardized, plus the user's written justification for overriding the flag. Entries look like: "- **AES-GCM** — overridden by user. Justification: the scenario runs on a side-channel-constrained platform where standard AES-GCM's cache-timing behavior is unacceptable." Empty if nothing was flagged.>

## Papers

<Each paper that has been dropped into the corpus or fetched for this scenario. Format: path + sha256 + optional role (populated after Round 1 triage).>

## Open Questions

<Anything unresolved: corpus insufficient and online search declined, PDF extraction failed, etc.>
