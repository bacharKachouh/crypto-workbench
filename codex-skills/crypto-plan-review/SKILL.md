# crypto-plan-review

Review the implementation plan before code is written.

## Gate

Verify all three exist for the current target:
- Impl spec in `extracted/impl_specs/`
- Ambiguity log in `extracted/ambiguity_logs/`
- Library mapping in `extracted/library_mappings/`

If any are missing, tell the user which prerequisite stage to run.

## Steps

### Step 1: Read all artifacts

Read:
- The impl spec (data types, module boundaries, function signatures, test plan)
- The ambiguity log (unresolved items, remaining blockers)
- The library mapping (chosen libraries, rejected options)
- Open questions from `.cryptoworkbench/workbench/open_questions.md`
- The notation map from `extracted/notation_maps/`

### Step 2: Check plan completeness

Verify the plan covers:
- All data types defined in the spec
- All function signatures with correct inputs and outputs
- All module boundaries
- Randomness requirements
- Serialization rules

### Step 3: Validate test plan

Confirm the test plan includes:
- Known-answer vectors (reference to test_vectors artifact if applicable)
- Edge cases
- Negative and invalid-input tests
- Serialization round-trip tests
- Failure-mode tests
- Coverage goals

### Step 4: Check library delegation

Identify any custom cryptographic code in the plan that should be delegated to the libraries identified in the library mapping. Flag hand-rolled primitives.

### Step 5: Validate assumptions

Check dependency choices and threat-model assumptions against the review and library mapping. Flag any mismatches.

### Step 5.5: Novel-construction acknowledgment (conditional)

Check the impl spec's `classification` field. If it is `Research prototype / novel construction` (the classification produced by the topic-mode branch's composed-design artifact), surface a mandatory acknowledgment before any verdict can be recorded:

> "This plan is for a cross-paper composed scheme. No end-to-end security proof exists for the composition. The risk ledger from the composed design has been copied into the impl spec's open questions. Approving implementation means you accept that the scheme is a research prototype and must not be deployed to production. Do you want to (a) approve (research prototype), (b) approve-with-conditions (list the conditions), or (c) block (list the blockers)?"

Record the user's acknowledgment verbatim in `decisions.md` under a `## Novel-construction acknowledgment` section. If the user picks (c), the verdict is `Blocked` and the skill stops here.

### Step 6: Record verdict

Write the plan review verdict to `.cryptoworkbench/workbench/decisions.md`:
- **Approved** — plan is ready for implementation
- **Approved with conditions** — list specific changes required
- **Blocked** — list unresolved blockers that must be addressed first

Verify the plan carries an implementation classification label. For novel-construction classifications, the verdict must either be `Approved with conditions` (naming the conditions) or `Blocked`; a plain `Approved` is not acceptable for a research-prototype composed scheme.

Report the verdict and either recommend `crypto-implement` (if approved) or list what must be resolved first.

## Shared modules

None — this is a reasoning-only skill. It reads artifacts produced by earlier stages.
