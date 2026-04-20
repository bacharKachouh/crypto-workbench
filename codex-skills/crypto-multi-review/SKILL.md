# crypto-multi-review

Produce one scenario-tilted review per paper in a topic-mode target. Each review adds a `scenario_fit` section on top of the standard review fields so the synthesis round can reason about which paper fits the scenario best.

## Gate

Call `load_target(workbench_root)` from `workbench.target`.

- If `target.mode != "topic"`, tell the user this skill is for topic-mode targets only and point them at `crypto-paper-review`.
- If `target.scenario_id` is empty or the scenario artifact is missing, tell the user to run `crypto-scenario` first.
- If `len(target.papers) < 2`, tell the user to re-run `crypto-scenario` to collect more papers (topic mode requires at least 2).
- If every paper in `target.papers` already has a review artifact, announce that and recommend `crypto-synthesize`.

## Steps

### Step 1: Extract PDFs

Call `parsing.pdf_to_text.run(corpus_root=.cryptoworkbench/corpus)` to ensure every paper has a `.md` companion. If `pypdf` is unavailable, record the skip list in `open_questions.md` and continue with whatever is extractable — papers without extractable text are flagged and excluded from review.

### Step 2: Per-paper review loop

For each paper in `target.papers` that does not yet have a review artifact:

1. Read the paper text + the scenario artifact.
2. Produce the standard review fields (summary, contribution, threat model, algorithms, parameters, security claims, implementation notes, version comparison, open questions).
3. Produce an added **`scenario_fit`** narrative answering four questions:
   - What in this paper is **directly relevant** to the declared scenario + research angle?
   - What is **irrelevant** or out-of-scope for the scenario?
   - What is the **biggest single strength** against the scenario?
   - What is the **biggest single weakness** against the scenario?
4. Call `build_review(...)` from `specs.build_review`. Include the `scenario_fit` narrative inside the `implementation_notes` field (prefix the block with a `### Scenario fit` subheading so downstream tools can locate it without a schema migration).
5. Set `variants_found: no`, `variants_reconciled: n/a` unless the paper *itself* has internal variants — this skill is not the place to resolve cross-paper forks (that's the synthesis stage).
6. Append `created_from` = the paper's local path, `source_digest` = the sha256 recorded in `target.papers`.

### Step 3: Surface per-paper summary

After each review is written, tell the user:
- the paper id
- a 1-sentence scenario-fit summary
- whether the paper looks like a KEEP candidate (backbone-eligible), a SUPPORTING candidate, or a REJECT candidate

Do not commit to those labels — they are Round 1 material. This is a heads-up only.

### Step 4: Wrap up

When every paper has a review, summarize the full set and recommend `crypto-synthesize`.

## Shared modules

- `workbench.target` — `load_target()`
- `parsing.pdf_to_text` — `run()`
- `specs.build_review` — `build_review()`
- `artifacts.metadata` — `compute_source_digest()`

## Invocation convention

(Same as other skills — see `crypto-scenario` for the `PYTHONPATH` and `workbench_root` conventions.)
