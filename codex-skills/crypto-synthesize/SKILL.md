# crypto-synthesize

Run the four-round interactive synthesis for a topic-mode target. Produces a composed-design artifact classified as `Research prototype / novel construction` that the existing `crypto-extract-spec` then consumes.

Every cross-paper splice is surfaced with its proof-gap note and user-approved explicitly. Nothing is silently composed.

## Gate

Call `load_target(workbench_root)` from `workbench.target`.

- If `target.mode != "topic"`, tell the user this skill is for topic-mode targets only.
- If any paper in `target.papers` lacks a review artifact, tell the user to run `crypto-multi-review` first.
- If a composed-design artifact already exists for this target, announce it and recommend `crypto-extract-spec`.

**Resume logic:** scan `extracted/synthesis/` for existing round artifacts. Enter at the first round that is missing. If all four are present, the composed design exists — see the final branch above.

## Steps

### Round 1 — Triage

Read every per-paper review + the scenario artifact.

For each paper, propose a label: **KEEP** (contender for backbone), **REJECT** (threat-model or correctness mismatch — cite the paper's `scenario_fit` field), or **SUPPORTING** (useful for evidence/attacks/proof technique but not a backbone).

Surface all proposals to the user in one batch, then walk them one-at-a-time for final approval/override. Record each final label on the paper in `target.papers[*].role`.

Call `build_triage(...)` from `synthesis.build_triage`. If every paper ends up REJECT, set `round_status: all_rejected`, write the artifact, stop, and point the user back to `crypto-scenario` to collect more papers.

### Round 2 — Deep-dive

For each KEEP paper, open a user-driven Q&A with: "Any specific questions about `<paper id>`?"

- The user asks about threat-model assumptions, parameter implications, proof technique, attack resistance, constant-time posture, implementation experience, etc.
- You answer from the paper text + the review artifact. Every answer carries a `source_ref` (paper section or review field).
- The user says `next` to advance to the next KEEP paper, or `done` to exit the round.

Call `build_deepdive(...)` from `synthesis.build_deepdive` with the collected `logs` dict.

If the user immediately says `done` with no questions, still write the artifact with `logs: {}` — the empty log is the record.

### Round 3 — Splice proposals

Pick a **backbone** from the KEEP set with explicit reasoning (state it out loud before proposing splices). The backbone is the scheme whose skeleton the composed design inherits.

For each candidate splice, propose it one at a time with all five mandatory fields:

1. `borrowed_piece` — specific algorithmic component (e.g., "Gaussian sampler from Algorithm 3 of Paper B").
2. `into` — location in the backbone (e.g., "replaces step 4 of KeyGen in Paper A's scheme").
3. `source_paper` — donor paper id.
4. `scenario_justification` — why the splice improves fit vs. the scenario + research angle.
5. `proof_gap_note` — does this break the backbone's security proof; what new assumption does the splice introduce; is the borrowed-piece's assumption compatible with the backbone's.

User gives explicit `approve / reject / tweak` per splice. Rejected splices stay in the artifact with a reason.

Call `build_splices(...)` from `synthesis.build_splices`.

**Edge:** if every splice is rejected *and* Round 2 surfaced no parameter/encoding tweaks either, announce: "No cross-paper composition is happening — this is just Paper X with no changes. Labeling this `novel construction` would be misleading. Want to (a) proceed anyway with a pure-backbone composed design and a minimal risk ledger, or (b) promote the backbone to a standard single-paper target and continue through `crypto-extract-spec` against its existing review?" Honor the user's choice.

### Round 4 — Composed design

Assemble the final document:

- Scenario restatement + research angle (copied from the scenario artifact).
- Backbone (attributed) + every approved splice (attributed + proof-gap note).
- **Per-paper contribution table**: every paper in `target.papers` gets a row; `role` is one of `backbone / splice-source / supporting-evidence / counter-example / rejected`; `what_we_used` and `why` describe the contribution (or explicitly say "none — rejected for <reason>").
- **Risk ledger**: every proof gap surfaced in Round 3, every compound-assumption risk, every novel-composition risk. Must be non-empty; the writer enforces this.
- **Pseudocode** of the composed scheme, with inline attribution.

Call `build_composed_design(...)` from `synthesis.build_composed_design`. Classification is hardcoded `Research prototype / novel construction` and the writer will refuse a downgrade.

Call `save_target(...)` to set `status: composed_design_written`.

### Hand-off

Summarize to the user:
- backbone paper + count of approved splices
- size of the risk ledger
- recommended next step: `crypto-extract-spec` (will read the composed design as primary source and propagate classification + risk ledger into the impl spec).

Warn explicitly that no end-to-end security proof exists for the composed scheme, and the pipeline will continue to flag this through plan-review and security-review.

## Shared modules

- `workbench.target` — `load_target()`, `save_target()`
- `synthesis.build_triage` — `build_triage()`
- `synthesis.build_deepdive` — `build_deepdive()`
- `synthesis.build_splices` — `build_splices()`
- `synthesis.build_composed_design` — `build_composed_design()`

## Invocation convention

(Same as other skills — see `crypto-scenario` for the `PYTHONPATH` and `workbench_root` conventions.)
