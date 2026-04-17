# crypto-init

Initialize a Crypto Workbench target workspace.

## Gate

None — this is the entry point for any new crypto target.

## Steps

### Step 1: Create the workspace

Run `initialize_workspace(root)` from `scaffolding.init_workspace` to create the `.cryptoworkbench/` tree with all required directories and workbench files.

Verify these exist after initialization:
- `corpus/` with subdirs: papers, standards, notes, drafts, prior_impls, fetched
- `extracted/` with subdirs: reviews, notation_maps, ambiguity_logs, impl_specs, security_reviews, library_mappings, test_vectors, source_indexes
- `workbench/` with files: current_target.yaml, decisions.md, open_questions.md, implementation_plan.md, config.yaml
- `cache/`

### Step 2: Create agent contract file

Run `initialize_codex_files(root)` from `scaffolding.init_codex_files` to place an `AGENTS.md` in the target project with the Crypto Workbench workflow contract. Existing files are preserved.

### Step 3: Pick an initialization path

Ask the user which path they want:

> "How would you like to start?
>  1. **Real target now** — tell me what paper / spec / scheme you want to work on
>  2. **Use a demo** — install a bundled example target and walk through the pipeline end-to-end
>  3. **Init only** — finish here; leave the target deferred and pick it up later"

Then execute the chosen branch:

#### Branch A — Real target now

Ask the user all three fields in **one consolidated prompt**, not three sequential questions:

> "Tell me about the target in one message. I need:
>  - `name` — short slug (e.g. `kyber-768`, `hkdf-sha512`)
>  - `type` — one of: algorithm / scheme / protocol / paper
>  - `primary_sources` — path(s) to the paper/standard, or URL(s) to fetch
>
> You can answer in any format — a single line, a bullet list, or separate messages if easier."

If the user partially answers, only re-prompt for the missing fields. Do not re-ask fields that were already provided. If the user says "I only have a URL, name it for me" or similar, propose a slug derived from the URL/title and confirm before saving.

Call `save_target(workbench_root, {name, type, primary_sources, status: "intake"})` from `workbench.target`.

If sources are URLs, leave `primary_sources` as the URLs and tell the user to run `crypto-intake` next — it is responsible for fetching material when search policy allows.

#### Branch B — Use a demo

List bundled examples with `list_examples()` from `scaffolding.install_example`.

- If zero examples are bundled: tell the user and point them to Branch A or C.
- If one example is bundled: tell the user the name and **explicitly confirm** before installing ("I'll install `<name>` — OK?"). Do not silently default — silent defaults violate the guided-interaction contract.
- If more than one is bundled: list them with short descriptions and ask which one.

Call `install_example(workbench_root, name=<demo>)`. This copies the demo paper into `corpus/papers/` and writes the preset target to `current_target.yaml` (with `status: demo`).

Tell the user clearly that this target is labeled as a demo — any artifact produced downstream will carry a "demo only" note and should not be treated as a real implementation.

#### Branch C — Init only (deferred)

Leave `current_target.yaml` with its default empty fields and `status: draft`. Do not prompt further. Tell the user they can invoke `crypto-intake` later; if they run it with a deferred target, downstream skills will prompt for the missing fields at that point.

### Step 4: Confirm initialization

Report to the user:
- Workspace location
- Path taken (real / demo / deferred) and the recorded target
- Next step: `crypto-intake` to scan and classify source material (or `crypto-init` again to pick a path when deferred)

## Shared modules

- `scaffolding.init_workspace` — `initialize_workspace(root)`
- `scaffolding.init_codex_files` — `initialize_codex_files(root)`
- `scaffolding.install_example` — `list_examples()`, `install_example(workbench_root, name)`
- `workbench.target` — `load_target()`, `save_target()`, `check_target_fields()`
- `config.loader` — `load_config(path)`, `save_config(path, updates)`

## Invocation convention

Shared Python modules ship inside this plugin under `${CODEX_PLUGIN_ROOT}/src/`. The user's current working directory is their working project — that is where `.cryptoworkbench/` lives and where any relative path like `workbench_root` resolves.

When invoking Python from this skill:

- Add the plugin's `src/` to the Python path. Inline form: `PYTHONPATH="${CODEX_PLUGIN_ROOT}/src" python ...`. Inside a script: `sys.path.insert(0, "${CODEX_PLUGIN_ROOT}/src")`.
- Do not assume the cwd is the plugin repo. The cwd is the user's project.
- Pass `workbench_root` as a path relative to the user's cwd (typically `.cryptoworkbench`).
- For calls with multi-line content (code blocks, long strings), use a heredoc-fed script or a temporary `.py` file — not inline `python -c` with shell quoting.
