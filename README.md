# Crypto Workbench

A guided, paper-to-implementation workflow for cryptography. Works with **Claude Code** and **Codex**.

Crypto Workbench turns a cryptographic paper, standard, or RFC into a reviewed, tested implementation — through a staged pipeline with explicit decision gates at every stage where scope can shift. It is a **guided collaborator**, not a silent pipeline: at each fork (which paper variant, which library, which implementation style, which output location) it surfaces the choice and asks rather than deciding silently.

## What it does

Drop a PDF, a URL, or a local Markdown file into the workbench. The plugin walks you through:

1. **Intake** — scan your corpus, fetch URL sources with per-fetch consent, extract text from PDFs.
2. **Paper review** — read the source, produce a review artifact, surface any version/variant forks for you to resolve.
3. **Spec extraction** — build a notation map, an ambiguity log, and an implementation spec with a test plan. Blocking ambiguities become explicit questions, not silent guesses.
4. **Library mapping** — match each primitive you need to reviewed, maintained libraries from the bundled registry. Fork decisions go to you.
5. **Plan review** — approve, approve-with-conditions, or block the plan before any code is written.
6. **Implementation** — tests-first, traceable to the spec, in the language and style you pick; output location is yours to decide.
7. **Security review** — cryptanalysis + side-channel checklists, findings classified as exploitable vs hardening, verdict recorded.

At any point, `crypto-status` gives you a read-only "where am I in the pipeline?" readout.

## Who it's for

- Researchers turning a paper into a reference implementation.
- Engineers integrating a crypto scheme into a real codebase and needing a review trail.
- Anyone who wants paper → code to go through explicit gates instead of guessing.

Not for: production-hardened crypto without expert review. The workbench helps *structure* the work and surface risks; it does not replace audit.

## Install

### Claude Code

Clone this repository, then either:

**Option A — local marketplace** (recommended for trying it out):

```
/plugin marketplace add /path/to/crypto-workbench
/plugin install crypto-workbench@crypto-workbench
```

**Option B — drop into your plugins directory**: copy the repo contents into `~/.claude/plugins/crypto-workbench/`.

Once installed, the 9 `crypto-*` skills are auto-discovered. Start with `/crypto-init`.

### Codex

Clone this repository. Codex picks up the plugin via `.codex-plugin/plugin.json`, which points at `./codex-skills/`.

Set the plugin root so skills can find bundled modules and registry data:

```
export CODEX_PLUGIN_ROOT=/path/to/crypto-workbench
```

Then invoke skills by name (e.g. `crypto-init`). The Codex skill contract lives in `templates/codex/AGENTS.md` — `crypto-init` copies it into your project on initialization.

### Python dependency

One optional dependency enables PDF text extraction:

```
pip install pypdf
```

Without `pypdf`, PDFs are skipped during intake with a clear message. All other functionality works.

## Quick start

From your project directory:

```
crypto-init          # creates .cryptoworkbench/ and asks: real target, demo, or init-only?
crypto-intake        # fetches URL sources (with consent), extracts PDF text, builds source index
crypto-paper-review  # produces review artifact; stops on variant forks
crypto-extract-spec  # builds notation map, ambiguity log, impl spec; classifies blockers vs deferred
crypto-library-map   # matches primitives to registry libraries
crypto-plan-review   # approves / approves-with-conditions / blocks the plan
crypto-implement     # asks language + style + output location; writes code + tests
crypto-security-review  # cryptanalysis + side-channel review, exploitable/hardening classification
crypto-status        # read-only "where am I?" at any point
```

First time? Run `crypto-init` and pick **"Use a demo"** — the bundled `hkdf-demo` example walks the full pipeline on a small self-contained pedagogical KDF so you can see every stage end-to-end.

## How it touches your project

The plugin creates one directory in your working project:

```
.cryptoworkbench/
├── corpus/        # source material (papers, standards, notes, drafts, prior_impls, fetched)
├── extracted/     # generated artifacts (reviews, notation_maps, ambiguity_logs, impl_specs,
│                  # library_mappings, implementations, security_reviews, source_indexes, test_vectors)
├── workbench/     # current target, decisions.md, open_questions.md, config.yaml
└── cache/         # regenerable indexes
```

Implementation code goes wherever *you* tell it to in `crypto-implement` — a new package in your project, an existing module, or `.cryptoworkbench/impl/<target>/` as scratch space. The plugin will not assume a project layout.

A platform-appropriate contract file (`CLAUDE.md` for Claude Code, `AGENTS.md` for Codex) is copied into your project on `crypto-init` so the agent has the Guided Interaction Contract available regardless of which frontend is driving.

## Safety model

- **Online fetches are dual-consent.** A workspace-level `search_policy` sets a ceiling ("online search allowed in this workspace at all?"). Every individual fetch still requires per-fetch approval. The policy is a ceiling, not silent consent.
- **Decision gates are explicit.** Variant selection, ambiguity resolution, library forks, implementation style, output location, and security-scope decisions are all user-owned; the plugin surfaces them and waits.
- **Traceability is required.** Every artifact records `created_from` and a source digest. Implementation code references the spec ID it implements.
- **Classification is explicit.** Every implementation path is labeled: Research prototype / Reference-style / Library-backed / Production-oriented / Spec-only.

## Repository layout (for contributors)

```text
crypto-workbench/
├── .claude-plugin/        # Claude plugin manifest + marketplace entry
├── .claude/agents/        # Claude subagent role descriptors
├── .codex-plugin/         # Codex plugin manifest
├── skills/                # Claude skill definitions (9 crypto-* skills)
├── codex-skills/          # Codex skill definitions (same 9, Codex conventions)
├── src/                   # Shared Python modules (corpus, specs, libraries, artifacts, ...)
├── registry/              # Curated YAML: algorithms, libraries, math families, tools, checklists
├── templates/             # Artifact templates + installed contract files (CLAUDE.md / AGENTS.md)
├── examples/              # Bundled pedagogical demo targets (e.g. hkdf-demo)
├── docs/                  # Architecture, workflow, security model, plugin commands
├── AGENTS.md              # Repo-level Codex contract
├── CLAUDE.md              # Repo-level Claude contract
└── README.md              # This file
```

## License

MIT — see `LICENSE`.
