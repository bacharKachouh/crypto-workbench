# Multi-paper Synthesis Implementation Plan

> **For agentic workers:** Executed inline (user waived subagent handoff).

**Goal:** Add a research-grade, use-case-driven, multi-paper synthesis branch to the `crypto-workbench` plugin that produces a composed-variant design and hands it to the existing implementation pipeline.

**Architecture:** Three new skills (`crypto-scenario`, `crypto-multi-review`, `crypto-synthesize`) form a branch before `crypto-extract-spec`. A `mode: topic` field on the workspace target gates the branch. Composed designs carry a hardcoded `Research prototype / novel construction` classification that propagates through the back-half of the pipeline.

**Tech Stack:** Python 3.10+, PyYAML, pytest. Follows the existing `src/` layout and artifact-writer conventions.

**Spec:** `docs/superpowers/specs/2026-04-20-multi-paper-synthesis-design.md`

---

## Task 1 — Extend target schema for topic mode

**Files:**
- Modify: `src/workbench/target.py`

Add these defaults: `mode: ""` (empty = single-paper), `scenario_id: ""`, `research_angle: ""`, `papers: []`. `save_target` and `load_target` round-trip them. `check_target_fields` treats `mode` as a regular string field.

## Task 2 — Register new artifact types

**Files:**
- Modify: `src/artifacts/metadata.py` — add slugs for `scenario`, `synthesis_triage`, `synthesis_deepdive`, `synthesis_splices`, `composed_design`.
- Modify: `src/artifacts/naming.py` — add to `_MARKDOWN_TYPES` and `_TYPE_DIRS`.

Directory layout:
- `scenario` → `extracted/scenarios/`
- `synthesis_triage`, `synthesis_deepdive`, `synthesis_splices`, `composed_design` → `extracted/synthesis/`

## Task 3 — Build `src/scenarios/`

**Files:**
- Create: `src/scenarios/__init__.py`
- Create: `src/scenarios/build_scenario.py` — `build_scenario(...)` writes Markdown artifact with scenario prose, research angle, rejected-standards log, paper list.
- Create: `src/scenarios/research_angle_check.py` — `check_scenario(scenario_text, registry_root) -> {is_standard, matched, suggested_redirect}` (registry+keyword match against standardized primitives).

## Task 4 — Build `src/synthesis/`

**Files:**
- Create: `src/synthesis/__init__.py`
- Create: `src/synthesis/build_triage.py`
- Create: `src/synthesis/build_deepdive.py`
- Create: `src/synthesis/build_splices.py`
- Create: `src/synthesis/build_composed_design.py`

Each writes a Markdown artifact with its round-specific body. `composed_design` includes the hardcoded `classification: Research prototype / novel construction` line and `artifact_type: composed_design` front-matter.

## Task 5 — Artifact templates

**Files:**
- Create: `templates/artifacts/scenario.md`
- Create: `templates/artifacts/synthesis_triage.md`
- Create: `templates/artifacts/synthesis_deepdive.md`
- Create: `templates/artifacts/synthesis_splices.md`
- Create: `templates/artifacts/composed_design.md`

## Task 6 — New skill SKILL.md files (Claude + Codex)

**Files:**
- Create: `skills/crypto-scenario/SKILL.md`
- Create: `skills/crypto-multi-review/SKILL.md`
- Create: `skills/crypto-synthesize/SKILL.md`
- Create: `codex-skills/crypto-scenario/SKILL.md`
- Create: `codex-skills/crypto-multi-review/SKILL.md`
- Create: `codex-skills/crypto-synthesize/SKILL.md`

Each mirrors the existing gate → steps → shared modules → invocation convention pattern.

## Task 7 — Update existing skills for topic-mode awareness

**Files:**
- Modify: `skills/crypto-init/SKILL.md` — add Branch D (research topic, use-case-driven).
- Modify: `skills/crypto-extract-spec/SKILL.md` — detect `artifact_type: composed_design` and force classification + propagate risk ledger.
- Modify: `skills/crypto-plan-review/SKILL.md` — add novel-construction acknowledgment when classification matches.
- Modify: `skills/crypto-security-review/SKILL.md` — append novel-construction checklist when classification matches.
- Mirror all four in `codex-skills/`.

## Task 8 — Tests

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_target_mode.py`
- Create: `tests/test_scenarios.py`
- Create: `tests/test_synthesis.py`
- Create: `tests/test_integration_topic_flow.py`

Cover: target round-trip with new fields, research-angle check positive/negative fixtures, each artifact writer, end-to-end integration with two stub papers, contract test that composed-design has required front-matter fields.

## Task 9 — Verify + commit

- Run all tests (`pytest tests/ -v`).
- Commit logically: (1) target + artifact-type extensions, (2) src/scenarios + src/synthesis, (3) templates, (4) new skills, (5) existing-skill updates, (6) tests.
