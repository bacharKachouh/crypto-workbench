# Crypto Workbench — Codex Project Contract

This repository is a cryptographic research-to-implementation workbench. It provides a staged workflow from paper or concept to implementation-ready specification and code, with explicit review gates and security thinking at every stage.

## Authoritative references

- **Workflow stages:** `docs/workflow.md`
- **Architecture:** `docs/architecture.md`
- **Security model:** `docs/security_model.md`
- **Plugin commands:** `docs/plugin_commands.md`

## Workspace

All working state lives in `.cryptoworkbench/` inside the target project. Key paths:

- `corpus/` — source material (papers, standards, notes, drafts, prior implementations, fetched)
- `extracted/` — generated artifacts (reviews, notation maps, ambiguity logs, impl specs, security reviews, library mappings, test vectors, source indexes)
- `workbench/` — current target, decisions, open questions, implementation plan, config
- `cache/` — regenerable indexes and metadata

## Workflow gates

These gates are mandatory. Do not skip or reorder them.

1. **Intake before review** — know what is in the corpus before reviewing it
2. **Review before extraction** — do not extract specs from unreviewed material
3. **Spec before implementation** — reviews, notation maps, ambiguity logs, and impl specs (with test plan) must exist before code
4. **Security review is mandatory** — every implementation gets one
5. **No silent assumptions** — unresolved questions go to `workbench/open_questions.md`
6. **Local corpus first** — check `corpus/` before searching online
7. **Search consent before online access** — `workbench/config.yaml` must record the user's search policy before any online queries

## Skills

This plugin provides 12 skills for the staged workflow:

| Skill | Stage |
|-------|-------|
| `crypto-init` | Initialize `.cryptoworkbench/` workspace |
| `crypto-intake` | Scan, classify, and optionally fetch source material (with consent) |
| `crypto-paper-review` | Review papers for contribution, assumptions, security claims |
| `crypto-extract-spec` | Extract notation, pseudocode, ambiguities, impl specs |
| `crypto-library-map` | Map primitives to libraries and tools |
| `crypto-plan-review` | Review implementation plan against specs and threats |
| `crypto-implement` | Implement with traceability, tests-first, safe APIs |
| `crypto-security-review` | Security-focused implementation review |
| `crypto-status` | Read-only pipeline state readout ("where am I?") |
| `crypto-scenario` | Topic mode: scenario, research angle and paper set |
| `crypto-multi-review` | Topic mode: one scenario-tilted review per paper |
| `crypto-synthesize` | Topic mode: compose a research-prototype design from several papers |

Skill definitions for Codex live in `codex-skills/crypto-*/SKILL.md`.

## Core principles

1. **Local corpus first.** Check `.cryptoworkbench/corpus/` before searching online.
2. **No silent assumptions.** Surface unclear parameters, encodings, threat models, or paper variants. Ask the user.
3. **Paper-to-spec before code.** Produce review, notation map, ambiguity log, impl spec, and test plan before implementation.
4. **Separate theory from engineering.** Distinguish mathematical structure, cryptographic primitive, protocol role, and library API.
5. **Prefer safe existing libraries.** Do not hand-roll crypto when an audited library is the better choice. Label research prototypes clearly.
6. **Security review is mandatory.** Cover misuse, side channels, serialization, invalid inputs, randomness, and key handling.
7. **Be explicit about limits.** Separate paper claims, implementation assumptions, verified facts, and open risks.

## Artifact standards

Artifact formats, metadata fields, and naming conventions are enforced by the builder modules in `src/specs/` and the templates in `templates/artifacts/`. Do not invent ad-hoc formats.

## Implementation classification

Every implementation path must be labeled as one of:
- Research prototype
- Reference-style implementation
- Library-backed implementation
- Production-oriented integration
- Spec-only / blocked by unresolved ambiguity

## Shared infrastructure

- `src/` — Python modules for corpus scanning, artifact generation, config, registry loading, and builders
- `registry/` — curated YAML entries for algorithms, libraries, math families, and tools
- `templates/artifacts/` — canonical templates for all 8 artifact types
