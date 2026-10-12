# Crypto Workbench

A free plugin for **Claude Code** and **Codex** that takes a cryptography paper, standard or RFC through to a reviewed, tested implementation.

It works in stages and stops at every real choice: which paper version, which parameter set, which library, which implementation style, where the code goes. It asks instead of guessing.

## Quick start

You need Python 3 with PyYAML. `pypdf` is optional and lets the plugin read PDFs.

**1. Get the plugin**

```
git clone https://github.com/bacharKachouh/crypto-workbench.git
cd crypto-workbench
pip install -r requirements.txt
```

**2. Add it to Claude Code**

```
/plugin marketplace add /path/to/crypto-workbench
/plugin install crypto-workbench@crypto-workbench
```

For Codex, see [Install on Codex](#install-on-codex).

**3. Try the demo**

Open Claude Code in an empty project folder and run:

```
/crypto-init
```

Pick **Use a demo**. The bundled `hkdf-demo` walks the whole pipeline on a small key-derivation function, so you see every stage before using your own paper.

## Using it on your own paper

Put a PDF or Markdown file in your project, or have a URL ready, then run the skills in order.

| Step | Skill | What it does | What you decide |
|------|-------|--------------|-----------------|
| 1 | `crypto-init` | Creates the `.cryptoworkbench/` working folder | Real target, demo, or research topic |
| 2 | `crypto-intake` | Scans your sources, extracts PDF text, fetches URLs | Whether each URL may be fetched |
| 3 | `crypto-paper-review` | Writes a review: contribution, assumptions, threat model, algorithms, parameters | Which version or variant is authoritative |
| 4 | `crypto-extract-spec` | Builds a notation map, an ambiguity log and an implementation spec with a test plan | How each blocking ambiguity is resolved |
| 5 | `crypto-library-map` | Matches each primitive to maintained libraries | Which library, when several fit |
| 6 | `crypto-plan-review` | Reviews the plan before any code exists | Approve, approve with conditions, or block |
| 7 | `crypto-implement` | Writes tests first, then code traceable to the spec | Language, style and output location |
| 8 | `crypto-security-review` | Reviews the code for misuse, side channels, encoding, invalid input, randomness and key handling | What to do about each finding |

Run `/crypto-status` at any point for a read-only "where am I?".

### Research topics

For a problem no single paper solves, pick **Research topic** in `crypto-init`. Three skills replace the first stages:

| Skill | What it does |
|-------|--------------|
| `crypto-scenario` | Records your scenario and research angle, and collects the set of papers |
| `crypto-multi-review` | Reviews each paper against the scenario |
| `crypto-synthesize` | Composes one design from the papers; every cross-paper splice needs your approval |

The result is labelled `Research prototype / novel construction` and continues at `crypto-extract-spec`. Use this path for hard research problems only. If you need AES-GCM or ECDSA, use the normal path and let `crypto-library-map` pick a mature library.

## What it writes to your project

```
.cryptoworkbench/
├── corpus/        # your source material: papers, standards, notes, fetched pages
├── extracted/     # generated reviews, notation maps, ambiguity logs, specs, library mappings, security reviews
├── workbench/     # current target, decisions.md, open_questions.md, config.yaml
└── cache/         # regenerable indexes
```

- Your decisions are recorded in `workbench/decisions.md` and unresolved questions in `workbench/open_questions.md`.
- Implementation code goes where you tell `crypto-implement` to put it.
- `crypto-init` also copies a contract file (`CLAUDE.md` or `AGENTS.md`) into your project, so the agent follows the same rules every session.

## Safety

- **Online fetches need your consent twice.** A workspace setting says whether online access is allowed at all, and every single fetch still asks.
- **Every implementation is labelled**: research prototype, reference-style, library-backed, production-oriented, or spec-only.
- **Every artifact is traceable.** It records what it was built from, and the code references the spec it implements.

## What it does not do

- It does not prove anything secure. The security review is the agent reading code against checklists; nothing is measured, so do not treat code as constant-time or audited on its word.
- It does not replace review by a cryptographer. Anything headed for production needs one.
- It does not audit existing codebases. It reviews the code it helped write.

## Install on Codex

Clone the repository and install the requirements as in the quick start. Codex reads `.codex-plugin/plugin.json`, which points at `./codex-skills/`. Set the plugin root so the skills can find the bundled modules:

```
export CODEX_PLUGIN_ROOT=/path/to/crypto-workbench
```

Then invoke skills by name, for example `crypto-init`.

## Repository layout

```text
crypto-workbench/
├── .claude-plugin/   # Claude plugin manifest and marketplace entry
├── .codex-plugin/    # Codex plugin manifest
├── skills/           # Claude skills (12)
├── codex-skills/     # Codex skills (the same 12)
├── src/              # Shared Python modules
├── registry/         # Algorithms, libraries, math families, tools, checklists
├── templates/        # Artifact templates and contract files
├── examples/         # Bundled demo target (hkdf-demo)
├── tests/            # Test suite
└── docs/             # Workflow, commands, architecture, security model
```

## Development

```
pip install -r requirements.txt pytest
python -m pytest
```

## License

MIT. See `LICENSE`.
