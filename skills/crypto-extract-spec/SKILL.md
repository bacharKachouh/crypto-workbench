# crypto-extract-spec

Convert reviewed material into implementation-facing specifications.

## Gate

Verify `extracted/reviews/` contains a review artifact for the current target. If not, tell the user to run `crypto-paper-review` first.

## Steps

### Step 1: Read source material

Read the paper, the review artifact, and any supplementary sources identified in the source index.

### Step 2: Build notation map

Extract all notation from the paper: symbols, meanings, domains, encodings, conventions, and any conflicts between sources.

Call `build_notation_map()` from `specs.build_notation_map` with:
- `workbench_root` = `.cryptoworkbench`
- `target` = current target name
- `created_from` = path to primary source
- `symbols` = list of dicts, each with: symbol, meaning, domain, encoding, notes
- `conventions` = list of paper-specific conventions
- `conflicts` = list of notation conflicts between sources

### Step 3: Extract pseudocode

Read the paper's algorithms. Normalize pseudocode into explicit steps with clear inputs, outputs, and control flow. Record any steps that are underspecified.

### Step 4: Track ambiguities

Identify every ambiguity, underspecified detail, and implementation choice that requires user input. Do not silently resolve them.

Call `build_ambiguity_log()` from `specs.build_ambiguity_log` with:
- `workbench_root` = `.cryptoworkbench`
- `target` = current target name
- `title` = descriptive title
- `created_from` = path to primary source
- `summary` = overview of ambiguity scope
- `ambiguities` = list of dicts, each with: title, description, source_location, impact, resolution_options, status

### Step 4.5: Resolve blocking ambiguities (decision gate)

Re-read the ambiguity log. Classify each item as **blocking** or **deferred** based on its `impact` field (scope / correctness / security → blocking; cosmetic / doc-only → deferred).

**Surface the classification to the user before escalating**, so they can object before you walk through the questions:

> "Ambiguity log has N items. I'm treating these as blocking: [list with one-line impact summaries]. I'm deferring these: [list]. OK with that split, or move something?"

Then, only after the split is confirmed:

- **Deferred items** — leave `status: deferred` and move on; the impl spec records them as open items.
- **Blocking items** — walk them one at a time, **announcing the count upfront** ("3 blocking items — I'll walk them in order"). For each, present description + source location + resolution options and ask for a decision. Record the user's decision back into the ambiguity log (`status: resolved`, add a `resolution` field) and into `.cryptoworkbench/workbench/decisions.md`.

Do not guess on blocking items. If the user wants to defer a blocker, note that explicitly — a deferred blocker becomes a classification constraint (impl spec classification shifts toward "Spec-only / blocked by unresolved ambiguity").

### Step 5: Produce implementation spec

Call `build_impl_spec()` from `specs.build_impl_spec` with:
- `workbench_root` = `.cryptoworkbench`
- `target` = current target name
- `title` = descriptive title
- `created_from` = path to primary source
- `classification` = one of: "Research prototype", "Reference-style implementation", "Library-backed implementation", "Production-oriented integration", "Spec-only / blocked by unresolved ambiguity"
- `summary`, `data_types`, `module_boundaries`, `function_signatures`, `randomness_requirements`, `serialization_rules`, `parameter_constraints`, `dependencies` = your spec content
- `test_plan_kat` = known-answer test vectors
- `test_plan_edge_cases` = edge case tests
- `test_plan_negative` = negative and invalid-input tests
- `test_plan_serialization` = serialization round-trip tests
- `test_plan_failure` = failure-mode tests
- `test_plan_coverage` = coverage goals

Report the extraction summary and recommend `crypto-library-map` as the next step.

## Shared modules

- `specs.build_notation_map` — `build_notation_map()`
- `specs.build_ambiguity_log` — `build_ambiguity_log()`
- `specs.build_impl_spec` — `build_impl_spec()`

## Invocation convention

Shared Python modules ship inside this plugin under `${CLAUDE_PLUGIN_ROOT}/src/`. The user's current working directory is their working project — that is where `.cryptoworkbench/` lives and where any relative path like `workbench_root` resolves.

When invoking Python from this skill:

- Add the plugin's `src/` to the Python path. Inline form: `PYTHONPATH="${CLAUDE_PLUGIN_ROOT}/src" python ...`. Inside a script: `sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/src")`.
- Do not assume the cwd is the plugin repo. The cwd is the user's project.
- Pass `workbench_root` as a path relative to the user's cwd (typically `.cryptoworkbench`).
- For calls with multi-line content (code blocks, long strings), use a heredoc-fed script or a temporary `.py` file — not inline `python -c` with shell quoting.
