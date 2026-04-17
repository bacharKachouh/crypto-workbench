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

### Step 6: Record verdict

Write the plan review verdict to `.cryptoworkbench/workbench/decisions.md`:
- **Approved** — plan is ready for implementation
- **Approved with conditions** — list specific changes required
- **Blocked** — list unresolved blockers that must be addressed first

Verify the plan carries an implementation classification label.

Report the verdict and either recommend `crypto-implement` (if approved) or list what must be resolved first.

## Shared modules

None — this is a reasoning-only skill. It reads artifacts produced by earlier stages.
