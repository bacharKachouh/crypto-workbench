# crypto-scenario

Intake a real-world cryptographic scenario, declare the research angle, run the registry-backed sanity check, and collect the paper set for a multi-paper synthesis target.

This is the entry point of the topic-mode branch. It only runs when `target.mode == topic`; single-paper targets never encounter this skill.

## Gate

Call `load_target(workbench_root)` from `workbench.target`.

- If the workspace is missing, tell the user to run `crypto-init` first.
- If `target.mode != "topic"`, tell the user: "This scenario intake is for research-topic targets. Re-run `crypto-init` and pick Branch D (research topic) if you want to use multi-paper synthesis. Otherwise, `crypto-intake` is the right next step for a single-paper target."
- If `target.scenario_id` is already populated and the scenario artifact exists under `extracted/scenarios/`, tell the user the scenario is already intake-complete and offer to re-open it for edits, or proceed to `crypto-multi-review`.

## Steps

### Step 1: Elicit the scenario

Ask the user to describe the real-world use case in plain prose. Explicitly request:
- what is being built (system / protocol / deployment)
- who the adversary is (threat model)
- deployment constraints (platform, runtime, perf budget, side-channel expectations)
- any compliance or standardization constraints

Do not accept a one-word topic ("post-quantum KEM"). This is the research intake; prose is mandatory so the later rounds have something to check papers against.

### Step 2: Elicit the research angle

Ask the user to declare in writing *why this is a research problem*:
- what standard answer falls short
- what novel combination of constraints makes this research-grade

Record the answer verbatim in `target.research_angle`.

### Step 3: Registry-backed sanity check

Run `check_scenario(scenario_text, registry_root)` from `scenarios.research_angle_check` where `registry_root` points to the plugin's bundled `registry/` (under `${CLAUDE_PLUGIN_ROOT}/registry`).

If `is_standard: true`, surface the `suggested_redirect` message to the user verbatim along with the list of matched primitives. Ask:

> "I flagged these standardized primitives: `<list>`. `<suggested_redirect text>`. Do you want to (a) switch to the standard single-paper pipeline — run `crypto-init` again and pick Branch A, (b) proceed with topic-mode synthesis and provide a written justification per flagged primitive, or (c) bail out?"

For each flagged primitive the user chooses to override, capture the written justification and append to `rejected_standards` as `{primitive, user_justification}`.

If `is_standard: false`, announce this briefly ("Registry sanity check: no standard primitives matched — proceeding.") and continue.

### Step 4: Paper-collection loop

Scan `corpus/papers/` using `scan_corpus(corpus_root)` from `corpus.scan_local`. Filter to papers not already referenced by any existing review (so re-entry doesn't double-count).

Then:

1. Tell the user: "You have N papers in `corpus/papers/`. For multi-paper synthesis I need at least 2 papers relevant to the scenario. Please drop any additional papers you want included, then tell me you're done."
2. When the user confirms, re-scan. If the count is still `< 2`, ask whether they want to (a) drop more papers, or (b) consent to an online search.
3. If the user consents to online search, follow the dual-consent pattern from `crypto-intake`: call `load_config` / `get_search_policy`; if a workspace ceiling is not yet recorded, prompt for it + the per-fetch consent in a single message. Per-fetch consent is mandatory every time — never silent.
4. For each approved URL, call `fetch_url(...)` from `corpus.fetch_url` and record the provenance.
5. If the final paper count is still `< 2`, record an open question and stop. Do not write a scenario artifact — topic mode requires at least 2 papers.

For every accepted paper, compute `compute_source_digest(path)` from `artifacts.metadata` and record `{path, sha256}` in `target.papers`.

### Step 5: Write the scenario artifact

Call `build_scenario(...)` from `scenarios.build_scenario` with:
- `workbench_root` = `.cryptoworkbench`
- `target` = `target.name`
- `title` = descriptive (e.g. "Scenario — <target>")
- `scenario_prose` = Step 1 answer
- `research_angle` = Step 2 answer
- `rejected_standards` = list from Step 3
- `papers` = list of `{path, sha256}` from Step 4
- `open_questions` = free-form summary of open items

Call `save_target(...)` to persist `mode: topic`, `scenario_id: <returned artifact id>`, `research_angle`, `papers`, and `status: scenario_complete`.

### Step 6: Record open questions

Append any unresolved items (online search declined, PDF extraction failed, etc.) to `.cryptoworkbench/workbench/open_questions.md`.

### Step 7: Hand off

Summarize to the user:
- what the scenario is (1–2 sentences)
- the research angle (verbatim)
- how many papers are in the set

Recommend `crypto-multi-review` as the next step.

## Shared modules

- `workbench.target` — `load_target()`, `save_target()`
- `corpus.scan_local` — `scan_corpus()`
- `corpus.fetch_url` — `fetch_url()`
- `config.loader` — `load_config()`, `get_search_policy()`, `set_search_policy()`
- `artifacts.metadata` — `compute_source_digest()`
- `scenarios.research_angle_check` — `check_scenario()`
- `scenarios.build_scenario` — `build_scenario()`

## Invocation convention

Shared Python modules ship inside this plugin under `${CLAUDE_PLUGIN_ROOT}/src/`. The user's cwd is their working project — that is where `.cryptoworkbench/` lives and where any relative path like `workbench_root` resolves.

When invoking Python from this skill:

- Add the plugin's `src/` to the Python path: `PYTHONPATH="${CLAUDE_PLUGIN_ROOT}/src" python ...` or `sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/src")` inside a script.
- Do not assume the cwd is the plugin repo.
- Pass `workbench_root` as a path relative to the user's cwd (typically `.cryptoworkbench`).
- For multi-line content, use a heredoc-fed script or a temporary `.py` file — not inline `python -c`.
