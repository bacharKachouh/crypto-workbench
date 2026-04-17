# crypto-implement

Implement an approved cryptographic plan.

## Gate

Verify `.cryptoworkbench/workbench/decisions.md` contains a plan review verdict of "Approved" or "Approved with conditions" for the current target with no unresolved blockers.

If the plan has not been reviewed, tell the user to run `crypto-plan-review` first.

## Steps

### Step 1: Read the spec artifacts

Read:
- The impl spec from `extracted/impl_specs/`
- The library mapping from `extracted/library_mappings/`
- The notation map from `extracted/notation_maps/`
- Open questions from `.cryptoworkbench/workbench/open_questions.md`

### Step 1.5: Confirm implementation preferences (decision gate)

**Do not write code until this is confirmed.** Ask the user:

1. **Target language** — e.g. Python, Rust, Go, C++, TypeScript, Java. The impl spec may carry a preferred language; if so, confirm rather than assume. If not, ask and list the realistic options.
2. **Implementation style** — `Research prototype` | `Reference-style implementation` | `Library-backed implementation` | `Production-oriented integration`. This affects scope, how much hand-rolled code is acceptable, and how strict the test plan is.
3. **Any unresolved design decisions** from the ambiguity log's `deferred` items that now have to be committed for code to exist.
4. **Output location** — where the implementation should live. Ask the user; do not assume a project layout. Reasonable prompts: a new package/module inside the user's project, an existing module they want to extend, or `.cryptoworkbench/impl/<target>/` if they want the code kept inside the workbench scratch area. Let the user pick — the plugin runs inside arbitrary user projects and must not assume a repo-level folder convention.

Record the user's answers in `.cryptoworkbench/workbench/decisions.md` under a new heading `## Implementation kickoff: <target>`. These decisions shape every subsequent step.

### Step 2: Implement with traceability

Keep changes traceable to the impl spec. Reference the spec ID and section in a module-level docstring or header comment of any generated file. If the user's project uses version control, also reference the spec in commit messages; if it does not (or if you cannot tell), keep traceability in the code and in the implementation artifact only — do not assume a git or other VCS workflow.

### Step 3: Write tests first

Write tests before or alongside behavior changes. Use the test plan from the impl spec as a guide:
- Known-answer vectors
- Edge cases
- Negative and invalid-input tests
- Serialization round-trip tests
- Failure-mode tests

### Step 4: Use safe APIs

Where the library mapping specifies constant-time or misuse-resistant APIs, use them. Do not substitute with naive implementations.

### Step 5: Document decisions

Record decisions that affect security, interoperability, or compatibility in `.cryptoworkbench/workbench/decisions.md`.

### Step 6: Do not guess

Do not resolve open cryptographic questions by guessing. Check `.cryptoworkbench/workbench/open_questions.md` and ask the user if a question affects the implementation path.

### Step 7: Produce implementation artifacts

Use `write_markdown_artifact()` or `write_yaml_artifact()` from `artifacts.writer` for any artifacts produced during implementation. Follow naming conventions from the base spec Section 6.4.

Report implementation progress and recommend `crypto-security-review` when implementation is complete and tests pass.

## Shared modules

- `artifacts.writer` — `write_markdown_artifact()`, `write_yaml_artifact()`
- `artifacts.naming` — `artifact_filename()`, `artifact_path()`

## Invocation convention

Shared Python modules ship inside this plugin under `${CLAUDE_PLUGIN_ROOT}/src/`. The user's current working directory is their working project — that is where `.cryptoworkbench/` lives and where any relative path like `workbench_root` resolves.

When invoking Python from this skill:

- Add the plugin's `src/` to the Python path. Inline form: `PYTHONPATH="${CLAUDE_PLUGIN_ROOT}/src" python ...`. Inside a script: `sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/src")`.
- Do not assume the cwd is the plugin repo. The cwd is the user's project.
- Pass `workbench_root` as a path relative to the user's cwd (typically `.cryptoworkbench`).
- For calls with multi-line content (code blocks, long strings), use a heredoc-fed script or a temporary `.py` file — not inline `python -c` with shell quoting.
