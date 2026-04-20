# Design — Multi-paper synthesis workflow

**Date:** 2026-04-20
**Status:** Approved design (pending user review)
**Target pipeline:** `crypto-workbench` Claude + Codex plugin

## 1. Goal

Let a user arrive with a real-world cryptographic scenario and a set of research papers on that topic, and produce a working, tested, security-reviewed implementation of a **composed variant** of an algorithm that fits the scenario. Each paper's contribution is explicitly attributed; every cross-paper splice is surfaced with its proof-gap note and approved by the user.

This feature is for **research problems**, not standard crypto needs. The pipeline must refuse (or loudly push back on) scenarios that map cleanly to standardized primitives with mature libraries.

## 2. Locked design decisions

| Fork | Decision |
| --- | --- |
| What "best variant" means | **Guided composition** — allowed to splice components across papers; output classified as `Research prototype / novel construction`; production-oriented classification blocked. |
| Entry point | **Use-case-first** — user arrives with a scenario, then is prompted to drop papers; dual-consent online search if no papers present. |
| Research-grade gate | **User declares research angle, Claude sanity-checks** — scenario intake requires a written research-angle declaration; Claude pushes back if scenario maps to registry-standard primitives; user can override with justification. |
| Interaction pattern | **Round-based** (4 rounds): triage → deep-dive → splice proposals → composed design. |
| Pipeline placement | **Separate branch with 3 new skills** — existing 9 skills are untouched at the behavior level; only field awareness is added where needed. |

## 3. Architecture

### 3.1 New skills (three)

**`crypto-scenario`**
- **Gate:** workspace exists, `target.mode == topic`, scenario artifact missing or incomplete.
- **Steps:**
  1. Elicit scenario prose (real-world use case).
  2. Elicit research-angle declaration (why is this not standard crypto?).
  3. Registry-backed sanity check — if scenario maps to a standardized primitive, push back concretely ("this looks solvable with X via `crypto-library-map` — want to switch, or is there something else?"). User overrides with written justification, recorded.
  4. Paper-collection loop — prompt user to drop papers into `corpus/papers/`; if none, offer dual-consent online search via existing `corpus.fetch_url`. Loop until user confirms the set (≥ 2 papers).
- **Output:** `.cryptoworkbench/extracted/scenarios/<target>-scenario.md` with: scenario prose, research angle, rejected-standard-answers log, paper list with SHA-256s, corpus-insufficient open questions.
- **Next:** `crypto-multi-review`.

**`crypto-multi-review`**
- **Gate:** scenario artifact exists with ≥ 2 papers; not all per-paper reviews written.
- **Steps:**
  1. Run `parsing.pdf_to_text` across listed papers (skip PDFs without `pypdf`, record open question).
  2. For each paper, produce a **scenario-tilted review**: standard review content (contribution, threat model, algorithms, parameters, claims) plus a `scenario_fit` section answering: what is directly relevant to the declared scenario, what is irrelevant, biggest strength and biggest weakness against the scenario.
- **Output:** one review artifact per paper in `.cryptoworkbench/extracted/reviews/` (reusing the existing artifact folder and schema; the `scenario_fit` section is an added body section).
- **Next:** `crypto-synthesize`.

**`crypto-synthesize`**
- **Gate:** every paper listed in the scenario has a review artifact; resume from first missing round artifact.
- **4 rounds** (Section 3.2).
- **Output:** `.cryptoworkbench/extracted/synthesis/<target>-composed-design.md`. This artifact acts as the "primary source" that `crypto-extract-spec` consumes.

### 3.2 The four rounds

**Round 1 — Triage.**
- Claude reads all per-paper reviews + scenario.
- Proposes a label per paper: **KEEP** (contender for backbone), **REJECT** (threat-model or correctness mismatch — cite `scenario_fit`), **SUPPORTING** (useful for evidence/attacks/proof-technique, not as backbone).
- User confirms or overrides each label.
- **Artifact:** `extracted/synthesis/<target>-round1-triage.md` with a `decisions:` YAML block: `[{paper_id, proposed, final, reason}]`.
- **Edge:** all-rejected → halt, point back to `crypto-scenario`; not a hard failure.

**Round 2 — Deep-dive.**
- User-driven Q&A against each **KEEP** paper.
- Claude opens with "Any specific questions about [paper A]?"; answers from paper text + review as context.
- User asks about threat-model assumptions, parameter implications, proof technique, attack resistance, constant-time posture, etc.
- Each Q+A logged with `source_ref` (paper section or review field).
- User says `next` (advance paper) or `done` (exit).
- **Artifact:** `extracted/synthesis/<target>-round2-deepdive.md` — nested `paper_id → [{q, a, source_ref}]`.

**Round 3 — Splice proposals.**
- Claude picks a **backbone** from the KEEP set with explicit reasoning.
- Proposes candidate splices one at a time. Each splice carries five mandatory fields:
  1. `borrowed_piece` — specific algorithmic component (e.g., "Gaussian sampler from Algorithm 3 of Paper B").
  2. `into` — backbone location (e.g., "replaces step 4 of KeyGen in Paper A's scheme").
  3. `source_paper` — paper id.
  4. `scenario_justification` — why this improves fit vs. the scenario + research angle.
  5. `proof_gap_note` — does this break the backbone's security proof; what new assumption is introduced; is the borrowed-piece's assumption compatible with the backbone's.
- User gives explicit `approve / reject / tweak` per splice. Rejected splices stay in the artifact with reason.
- **Artifact:** `extracted/synthesis/<target>-round3-splices.md` with `backbone: {paper_id, reason}` and `decisions: [{splice_fields..., status, user_reason}]`.
- **Edge:** all splices rejected → proceed with pure-backbone composed design; if *also* no parameter/encoding tweaks were discussed in Round 2, the skill announces the situation and offers to promote the chosen backbone to a standard single-paper target — the existing per-paper review from `crypto-multi-review` is already compatible with `crypto-extract-spec`, so the user can continue through the normal single-paper pipeline from that point without a misleading "novel construction" label.

**Round 4 — Composed design.**
- Claude assembles the final document:
  - scenario restatement + research angle
  - backbone (attributed)
  - each approved splice (attributed + proof-gap note)
  - **per-paper contribution table** — columns: `paper_id`, `role` (backbone / splice-source / supporting-evidence / counter-example / rejected), `what_we_used`, `why`
  - **risk ledger** — every proof gap, compound assumption, novel-composition risk
  - pseudocode of the composed scheme
  - classification hardcoded: `Research prototype / novel construction`.
- **Artifact:** `extracted/synthesis/<target>-composed-design.md`. Front-matter includes `artifact_type: composed_design` so `crypto-extract-spec` detects it.

### 3.3 Target schema additions

`current_target.yaml` gains:

```yaml
mode: topic        # new; single-paper default = target
scenario_id: str   # id of the scenario artifact
research_angle: str
papers:
  - path: str
    sha256: str
    role: str      # populated after Round 1 triage
```

`crypto-status` reads these fields for topic-mode readouts; no behavior change for single-paper targets.

### 3.4 Artifact layout

```
.cryptoworkbench/
├── corpus/papers/                         (existing)
├── extracted/
│   ├── scenarios/                         (NEW)
│   │   └── <target>-scenario.md
│   ├── reviews/                           (existing, reused)
│   │   └── <paper_id>-review.md           (adds scenario_fit section in topic mode)
│   └── synthesis/                         (NEW)
│       ├── <target>-round1-triage.md
│       ├── <target>-round2-deepdive.md
│       ├── <target>-round3-splices.md
│       └── <target>-composed-design.md
└── workbench/                             (existing)
```

### 3.5 Classification propagation

`composed-design.md` carries `classification: Research prototype / novel construction` as a literal front-matter field. When `crypto-extract-spec` sees `artifact_type: composed_design`:

- it forces `impl_spec.classification` to match; user cannot downgrade.
- it copies the `risk_ledger` into the impl spec as an `open_questions` subsection so the risks travel all the way into plan-review and security-review.
- `Production-oriented integration` is blocked for this branch.

### 3.6 Back-half integration (no code changes, only field awareness)

| Skill | Change |
| --- | --- |
| `crypto-init` | Adds a fourth menu option "research topic (use-case-driven)"; sets `target.mode = topic`, points user at `crypto-scenario`. |
| `crypto-extract-spec` | Detects `artifact_type: composed_design` in primary source, forces classification, propagates risk ledger. |
| `crypto-library-map` | No change — consumes impl spec normally. |
| `crypto-plan-review` | On `classification = Research prototype / novel construction`, adds one mandatory user prompt acknowledging "no end-to-end proof; approving implementation means accepting that risk". approve / approve-with-conditions / block. |
| `crypto-implement` | No change. |
| `crypto-security-review` | Appends a **novel-construction checklist** template when classification matches: composition proof gaps, assumption compatibility at splice boundaries, new attack surfaces, constant-time interaction at splice boundaries, absence of end-to-end proof. |

### 3.7 Shared Python modules (new)

Following the existing `src/` convention:

- `src/scenarios/build_scenario.py` — writes scenario artifact.
- `src/scenarios/research_angle_check.py` — registry-backed "is this a standard primitive?" check; returns `(is_standard: bool, matched_entries: list, suggested_redirect: str | None)`.
- `src/synthesis/build_triage.py`
- `src/synthesis/build_deepdive.py`
- `src/synthesis/build_splices.py`
- `src/synthesis/build_composed_design.py`
- `src/workbench/target.py` — extend schema for `mode`, `scenario_id`, `research_angle`, `papers[]`.

### 3.8 Templates

- `templates/artifacts/scenario.md`
- `templates/artifacts/synthesis_triage.md`
- `templates/artifacts/synthesis_deepdive.md`
- `templates/artifacts/synthesis_splices.md`
- `templates/artifacts/composed_design.md`

### 3.9 Codex parity

Every new skill must ship a Codex analog under `codex-skills/` with matching workflow contracts in `AGENTS.md`. This mirrors the existing plugin convention.

## 4. Error handling

- `< 2` papers at end of `crypto-scenario` → refuse hand-off to multi-review; loop back in scenario.
- PDF extraction fails for a paper → multi-review warns, proceeds with the remaining papers, records skipped paper as an open question.
- User rejects all papers in Round 1 → halt, write triage artifact with `status: all_rejected`, point user back to `crypto-scenario`. Not a hard failure — a re-entry point.
- User rejects all splices in Round 3 → pure-backbone composed design. If no Round 2 tweaks were discussed either, announce the situation and offer to switch to standard `crypto-paper-review` rather than misleadingly label a stock scheme as novel.
- Resume semantics: each round skill reads the prior round's artifact; if missing, reports which round to run.
- Online-search refusal: scenario artifact records "corpus insufficient, online declined" as an open question; proceed if ≥ 2 papers exist locally.

## 5. Testing

- **Unit tests** per new shared module (pattern from existing `src/`):
  - `research_angle_check` — positive fixtures (AES-GCM, ECDSA, HKDF → flagged standard) and negative fixtures (threshold-FHE with novel leakage, unusual OPRF settings → passes as research).
  - Artifact writers (triage, deepdive, splices, composed-design) — schema validation, front-matter correctness, round-trip.
  - Target schema round-trip — `mode: topic` persists through save/load.
- **Integration test:** minimal fake scenario with two stub "papers" (short markdown files), end-to-end through `crypto-scenario` → `crypto-multi-review` → `crypto-synthesize`; assert composed-design.md is produced with correct classification, non-empty risk ledger, per-paper contribution table covering both inputs.
- **Contract test:** composed-design.md is readable by `crypto-extract-spec` unchanged; single-paper flow does not regress.

## 6. Non-goals

- No automatic/silent algorithmic composition — every splice is user-approved with a proof-gap disclosure.
- No formal proof generation — the feature produces a composed design with attribution and risk notes; it does not attempt to derive a security proof for the composed scheme.
- No "production-oriented" implementation path for composed designs — classification is hardcoded and downstream classification downgrades are blocked.
- No change to the single-paper flow — users on the standard path never encounter this branch.

## 7. Open questions for implementation planning

- Should `crypto-multi-review` process papers in parallel (Agent dispatches) or sequentially? Trade-off: speed vs. predictability of gate checks between reviews.
- Does the `research_angle_check` need a training corpus or is keyword/registry matching sufficient for v1? Recommendation: start with registry + keyword matching; Claude's qualitative judgment fills the gap at the gate prompt.
- Back-half integration: does `crypto-plan-review` already have an "approve-with-conditions" path usable for novel-construction flagging, or does that need to be added? Confirm during implementation planning.
