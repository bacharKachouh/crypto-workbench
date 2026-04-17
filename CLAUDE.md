# Crypto Workbench — Claude Project Contract

This repository is a Claude-first crypto research and implementation workbench.

Its purpose is to help the user:
- find relevant cryptography papers, standards, notes, and prior implementations
- review and understand proposed algorithms
- extract implementation-ready specifications
- map designs to modern libraries and tools
- plan implementations carefully
- perform structured security review and cryptanalysis-oriented review

The plugin also ships a Codex-compatible variant under `codex-skills/` with matching workflow contracts in `AGENTS.md`; see `README.md` for install instructions per platform.

---

## Core operating principles

1. Local corpus first.
    - Always check `.cryptoworkbench/corpus/` before searching online.
    - Prefer local papers, notes, standards, and prior implementation attempts when relevant.

2. No silent assumptions.
    - Never guess missing parameters, encodings, threat models, paper variants, or implementation choices.
    - If something important is unclear, explicitly surface it and ask the user.

3. Paper-to-spec before code.
    - Do not jump directly from paper reading to implementation.
    - First produce:
        - a paper review
        - a notation map
        - an ambiguity log
        - an implementation spec
        - a test plan

4. Separate theory from engineering.
    - Distinguish:
        - mathematical structure
        - cryptographic primitive
        - protocol role
        - library/API realization
    - Example: a scheme may be module-lattice over polynomial rings mathematically, but operationally exposed as a KEM API.

5. Prefer explicit variants.
    - If there are several versions of a paper, algorithm, parameter set, or implementation style, identify them and ask the user to choose when the choice matters.

6. Prefer safe existing libraries when appropriate.
    - Do not default to hand-rolling crypto when a standard, audited, or established library is the better engineering choice.
    - If the user wants a research prototype or educational implementation, label it clearly as such.

7. Security review is mandatory.
    - Every serious implementation plan must include:
        - misuse review
        - side-channel considerations
        - serialization/encoding review
        - invalid-input behavior review
        - randomness review
        - key/state handling review

8. Be explicit about limits.
    - Do not claim formal proof, production readiness, or audit-grade assurance unless that is actually justified.
    - Clearly separate:
        - paper claims
        - implementation assumptions
        - verified facts
        - open risks

---

## Workspace conventions

The project-local working area is:

`.cryptoworkbench/`

Expected structure:

- `.cryptoworkbench/corpus/`
    - `papers/`
    - `standards/`
    - `notes/`
    - `drafts/`
    - `prior_impls/`
    - `fetched/`

- `.cryptoworkbench/extracted/`
    - `reviews/`
    - `notation_maps/`
    - `ambiguity_logs/`
    - `impl_specs/`
    - `security_reviews/`
    - `library_mappings/`
    - `test_vectors/`
    - `source_indexes/`

- `.cryptoworkbench/workbench/`
    - `current_target.yaml`
    - `decisions.md`
    - `open_questions.md`
    - `implementation_plan.md`
    - `config.yaml`

- `.cryptoworkbench/cache/`
    - search indexes and temporary generated metadata

Use `.cryptoworkbench/` for generated artifacts and working state.
Do not clutter the main repo root with intermediate review files when they belong in the workbench.

---

## Expected workflow

When working on a cryptographic target, follow this order:

1. Intake
    - Check local corpus first.
    - If needed, search online for relevant papers, standards, or reference material.

2. Source triage
    - Identify the canonical paper or standard.
    - Detect newer versions, corrections, optimizations, attacks, and follow-up papers.
    - Detect reference implementations and standard-library realizations.

3. Paper review
    - Summarize the contribution, assumptions, threat model, algorithms, parameters, and claimed properties.

4. Extraction
    - Build a notation map.
    - Extract pseudocode and algorithm structure.
    - Record ambiguities and underspecified details.

5. Implementation spec
    - Define data types, modules, function boundaries, inputs/outputs, randomness requirements, serialization rules, and test strategy.

6. Library and tool mapping
    - Check whether modern libraries, references, tools, or prior implementations help.
    - Decide whether the target should be:
        - a research prototype
        - a reference-style implementation
        - a library-backed integration
        - a production-oriented wrapper/integration

7. Plan self-review
    - Critique the plan after seeing real tools and libraries.
    - Revise the plan if a better and safer implementation route exists.

8. Clarification gate
    - If critical items remain undefined, stop and ask the user.
    - No silent assumptions.

9. Implementation
    - Implement only after the spec and unresolved choices are under control.

10. Security review
- Review misuse risks, side-channel issues, state handling, serialization, invalid-input handling, and proof-to-implementation gaps.

---

## Required outputs before serious implementation

Before writing substantial crypto code, produce these artifacts when applicable:

- `review`
- `notation_map`
- `ambiguity_log`
- `implementation_spec`
- `test_plan`
- `library_mapping`
- `security_review_outline`

If any of these are missing, explain why.

---

## Ambiguity handling rules

Always raise questions when any of the following are unclear:

- which paper or version is authoritative
- which parameter set to implement
- research prototype vs production integration
- clean reference code vs optimized implementation
- deterministic vs randomized behavior
- serialization or encoding choices
- threat model
- constant-time expectations
- expected language, runtime, or library

Record unresolved questions in:
`.cryptoworkbench/workbench/open_questions.md`

Record user decisions in:
`.cryptoworkbench/workbench/decisions.md`

---

## Implementation classification labels

When presenting a final implementation path, classify it as one of:

- Research prototype
- Reference-style implementation
- Library-backed implementation
- Production-oriented integration
- Spec-only / blocked by unresolved ambiguity

Use the label explicitly.

---

## Cryptography-specific review checklist

Always consider, when relevant:

- key generation and key lifecycle
- randomness source and sampling correctness
- parameter validation
- encoding and decoding
- serialization format
- domain separation
- transcript binding
- failure handling
- invalid-input behavior
- constant-time risks
- memory hygiene
- statefulness and replay issues
- misuse resistance
- proof-to-implementation gaps

---

## Writing style for artifacts

Generated artifacts should be:
- structured
- technical
- explicit
- conservative in claims
- clear about uncertainty

Prefer Markdown and YAML for generated analysis artifacts unless another format is more appropriate.

---

## Priority rule

If there is a conflict between:
- speed and clarity
- speed and correctness
- speed and explicit uncertainty

prefer:
- clarity
- correctness
- explicit uncertainty