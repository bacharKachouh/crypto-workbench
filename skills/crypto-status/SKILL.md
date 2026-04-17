# crypto-status

Report the current pipeline state for the workbench. Read-only — no artifacts written, no decisions made, no prompts.

Use this skill at any time to answer "where am I in the pipeline?" and "what's the next recommended step?".

## Gate

None. If no workbench exists, the skill reports that fact and recommends `crypto-init`.

## Steps

### Step 1: Read state

Call `get_state(workbench_root)` from `workbench.pipeline_state` with `workbench_root = ".cryptoworkbench"` (or wherever the user's workbench lives relative to cwd).

### Step 2: Render the report

Call `format_state(state)` and print the result verbatim to the user. The report includes:

- workbench path
- current target (name, type, status, primary sources, deferred flag)
- pipeline progress (per-stage artifact counts)
- open-question and decision-log line counts
- next recommended skill

### Step 3: Optional follow-ups

Do **not** take any action. If the user wants to act on the recommended next step, tell them the skill name; let them invoke it.

If the pipeline state shows a deferred target, the report will say so — recommend `crypto-init` to pick a target.

If the pipeline end is reached (security review present), tell the user the demo/implementation path is complete and suggest running `crypto-security-review` again only if code has changed.

## Shared modules

- `workbench.pipeline_state` — `get_state()`, `format_state()`, `run()`

## Invocation convention

Shared Python modules ship inside this plugin under `${CLAUDE_PLUGIN_ROOT}/src/`. The user's current working directory is their working project — that is where `.cryptoworkbench/` lives and where any relative path like `workbench_root` resolves.

When invoking Python from this skill:

- Add the plugin's `src/` to the Python path. Inline form: `PYTHONPATH="${CLAUDE_PLUGIN_ROOT}/src" python ...`. Inside a script: `sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/src")`.
- Do not assume the cwd is the plugin repo. The cwd is the user's project.
- Pass `workbench_root` as a path relative to the user's cwd (typically `.cryptoworkbench`).
