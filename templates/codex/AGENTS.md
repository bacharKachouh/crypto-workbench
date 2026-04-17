# Crypto Workbench Target

Follow the Crypto Workbench workflow for this target.

## Guided Interaction Contract

This plugin is a **guided collaborator**, not a silent pipeline. Follow this rule at every stage:

> **Analyze first. Surface findings. Ask for decisions. Then continue.**

Not: ask everything up front. Not: assume everything silently.

### Principles

1. **Analysis first, decisions second.** Read the source material, extract what you can, and present findings before moving into implementation choices.
2. **No silent assumptions.** If something important is unclear, stop and ask. Never silently choose programming language, library, algorithm variant, parameter set, serialization format, implementation scope, or research-prototype-vs-production posture.
3. **Decision points must be explicit and technical.** Ask only when the answer matters, and make the question specific — not vague.
4. **User controls implementation direction.** When the workflow reaches implementation, confirm language, style, scope, and any unresolved design choices before writing code.
5. **Artifact-driven conversation.** Each stage produces artifacts; use them to structure what you ask the user. Review artifact → discuss findings. Ambiguity log → resolve the important items. Library mapping → choose the preferred path. Impl spec → confirm design choices.
6. **Stay conservative about assumptions, proactive about surfacing forks.** If there is nothing ambiguous, keep momentum. If there is a meaningful fork, stop and ask.

### Examples of good decision-point questions

- "There are two meaningful algorithm variants in the source. Which one should I implement?"
- "The paper does not fully specify the serialization format. Should I follow the reference implementation, a standard format, or define a prototype-only format?"
- "Which implementation language do you want: Python, Rust, Go, C++, or something else?"
- "Should this be a research prototype, a reference-style implementation, a library-backed integration, or production-oriented?"
- "The security review flags an exploitable finding. Stop, narrow scope to prototype-only, or continue with the finding documented as a known risk?"

### Stage-specific expectations

- **Intake** — ask for source material and whether online search is allowed. Do not force implementation preferences here.
- **Paper review** — after producing the review artifact, tell the user what the source proposes, the key findings, and whether multiple interpretations or variants exist. If there is a fork, ask the user to choose before extraction.
- **Spec extraction** — present the ambiguity log and ask the user to resolve only the blocking items. Do not silently resolve them.
- **Library mapping** — if more than one valid implementation path exists, explain the tradeoffs and ask the user to choose before writing the artifact.
- **Plan review** — confirm the plan covers scope, tests, and risks; produce an Approved / Approved-with-conditions / Blocked verdict.
- **Implementation** — before any code: confirm target language, implementation style, scope (prototype / reference / library-backed / production), and any unresolved design decisions from the ambiguity log.
- **Security review** — present findings clearly. If a finding changes acceptable scope, ask the user whether to stop, narrow scope, or continue as a research prototype with the finding documented.

## Workflow gates

1. **Intake before review** — scan and classify corpus before reviewing papers.
2. **Review before extraction** — do not extract specs from unreviewed material.
3. **Spec before implementation** — produce review, notation map, ambiguity log, and impl spec before code.
4. **Security review is mandatory** — every implementation gets one.
5. **No silent assumptions** — record unresolved questions, do not guess.

## Workspace

- Sources: `.cryptoworkbench/corpus/`
- Artifacts: `.cryptoworkbench/extracted/`
- Decisions: `.cryptoworkbench/workbench/decisions.md`
- Open questions: `.cryptoworkbench/workbench/open_questions.md`
- Config: `.cryptoworkbench/workbench/config.yaml`

## Housekeeping rules

- Keep sources and decisions traceable — every artifact must record `created_from` and source digest.
- Record ambiguity in the ambiguity log instead of guessing.
- Prefer reviewed cryptographic libraries for primitives.
- Run plan review and security review before treating implementation work as complete.
- Convert relative dates to absolute dates in decisions.md and open_questions.md.
- Separate paper claims from implementation assumptions from verified facts.
