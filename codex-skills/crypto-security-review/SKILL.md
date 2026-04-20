# crypto-security-review

Security-focused review of a cryptographic implementation.

## Gate

Verify:
- Implementation code exists for the current target
- Tests exist and pass

If no implementation exists, tell the user to run `crypto-implement` first.

## Steps

### Step 1: Read context

Read:
- The implementation code
- The impl spec from `extracted/impl_specs/`
- The library mapping from `extracted/library_mappings/`
- The test suite and test results

### Step 2: Apply cryptanalysis checklist

Read `${CODEX_PLUGIN_ROOT}/registry/checklists/cryptanalysis.yml`. For each item in the checklist, evaluate the implementation:

- Does the implementation satisfy the check?
- If not, what is the severity and what is the specific finding?

Record each finding with: checklist item id, severity, category, description, recommendation.

### Step 3: Apply side-channel checklist

Read `${CODEX_PLUGIN_ROOT}/registry/checklists/side_channels.yml`. For each item, evaluate:

- Are there secret-dependent branches, memory accesses, or timing variations?
- Is zeroization correctly applied?
- Are compiler optimizations accounted for?

Record each finding with the same structure.

### Step 3.5: Novel-construction checklist (conditional)

Read the impl spec's `classification`. If it is `Research prototype / novel construction`, apply the **novel-construction checklist** in addition to the standard checks:

- **Proof composition gaps** — the backbone paper's security proof does not cover the spliced components. For each splice listed in the composed-design artifact's "Approved Splices", note whether the proof gap is documented and whether any attempt has been made to argue informally about why the splice is sound.
- **Assumption compatibility** — do the borrowed pieces rely on the same computational assumptions as the backbone (e.g., LWE vs. Ring-LWE, DDH vs. CDH, random-oracle vs. standard-model)? List mismatches.
- **New attack surfaces** — the composition may expose data paths that neither original paper examined. Identify any splice boundaries that cross a trust boundary, a randomness domain, or an adversary-visible surface.
- **Constant-time at splice boundaries** — when two components are spliced, the concatenation's constant-time posture is not guaranteed even if each piece is individually constant-time. Audit the joined path.
- **Absence of end-to-end proof** — record explicitly that no end-to-end proof exists for the composed scheme and that any deployment decision must treat this as a research prototype.

Record each novel-construction finding with the same `{severity, category, description, recommendation}` schema used for the standard checks, but tag `category = novel_construction`. The risk ledger from the composed-design artifact (propagated through the impl spec's open questions) is the starting point — every entry there should appear somewhere in the findings (either as confirmed-resolved, confirmed-unresolved, or newly-discovered implication).

### Step 4: Verify test coverage

Confirm the test suite includes:
- Known-answer vectors
- Negative and invalid-input cases
- Regression tests for any findings

Flag missing coverage.

### Step 5: Classify findings

Separate findings into:
- **Exploitable** — real vulnerabilities that must be fixed
- **Hardening** — improvements that strengthen the implementation but are not exploitable

### Step 5.5: Scope decision (decision gate)

If the findings change the acceptable scope, present them clearly and ask the user how to proceed:

- **Stop** — exploitable findings must be fixed before this implementation is used for anything; do not approve.
- **Narrow scope to prototype-only** — keep the implementation but classify it as `Research prototype`, with all findings documented as known-risks. This is a legitimate outcome for research work.
- **Continue as-is** — only appropriate if findings are hardening-only, or if the user explicitly accepts exploitable findings with a written rationale recorded in `decisions.md`.

Do not silently decide. Record the user's choice in `.cryptoworkbench/workbench/decisions.md`.

### Step 6: Produce security review artifact

Call `write_markdown_artifact()` from `artifacts.writer` with:
- `artifact_type` = `"security_review"`
- `target` = current target name
- `title` = descriptive title
- `created_from` = implementation path
- `body` = security review content following base spec Section 7.4:
  - Summary
  - Classification
  - Findings (each with severity, category, description, recommendation)
  - Checklist Coverage (key generation, randomness, parameters, encoding, domain separation, failure handling, side channels, memory hygiene, replay, misuse)
  - Open Risks
  - Verdict: approved, conditionally approved, or blocked
- `workbench_root` = `.cryptoworkbench`

### Step 7: Record verdict

Append the security review verdict to `.cryptoworkbench/workbench/decisions.md`.

Report findings summary and verdict to the user.

## Shared modules

- `artifacts.writer` — `write_markdown_artifact()`
- `libraries.registry_loader` — `load_registry_file()` (to load checklists)

## Shared data

- `${CODEX_PLUGIN_ROOT}/registry/checklists/cryptanalysis.yml`
- `${CODEX_PLUGIN_ROOT}/registry/checklists/side_channels.yml`

## Invocation convention

Shared Python modules ship inside this plugin under `${CODEX_PLUGIN_ROOT}/src/`. The user's current working directory is their working project — that is where `.cryptoworkbench/` lives and where any relative path like `workbench_root` resolves.

When invoking Python from this skill:

- Add the plugin's `src/` to the Python path. Inline form: `PYTHONPATH="${CODEX_PLUGIN_ROOT}/src" python ...`. Inside a script: `sys.path.insert(0, "${CODEX_PLUGIN_ROOT}/src")`.
- Do not assume the cwd is the plugin repo. The cwd is the user's project.
- Pass `workbench_root` as a path relative to the user's cwd (typically `.cryptoworkbench`).
- For calls with multi-line content (code blocks, long strings), use a heredoc-fed script or a temporary `.py` file — not inline `python -c` with shell quoting.
