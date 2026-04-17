# crypto-paper-review

Review cryptographic papers and standards.

## Gate

Call `check_target_fields(workbench_root, ["name", "primary_sources"])` from `workbench.target`. If any are missing, the target is still deferred or incomplete — prompt the user to fill them in before continuing (or point them back to `crypto-init` / `crypto-intake`).

Then verify `extracted/source_indexes/` contains a source index artifact for the current target. If not, tell the user to run `crypto-intake` first.

## Steps

### Step 1: Identify sources

Read the source index artifact for the current target. Identify:
- The primary source (highest authority, highest rank)
- Any supplementary sources
- Any fetched sources with their provenance

### Step 2: Read and analyze the paper

Read the primary paper or standard directly. Analyze for:
- **Contribution** — what is new or claimed
- **Assumptions** — what the construction relies on
- **Threat model** — what adversary is considered
- **Algorithms** — core operations and their structure
- **Parameters** — sizes, security levels, choices
- **Security claims** — what is proven, what is conjectured

### Step 3: Compare versions (if applicable)

If multiple versions exist (eprint revisions, draft rounds, conference vs journal), compare them and note material differences that affect implementation.

### Step 4: Flag issues

Flag:
- Unclear reductions or proof gaps
- Missing parameters or underspecified constants
- Non-standard notation
- Inconsistencies between versions

### Step 5: Produce review artifact

Call `build_review()` from `specs.build_review` with:
- `workbench_root` = `.cryptoworkbench`
- `target` = current target name
- `title` = descriptive review title
- `created_from` = path to primary source
- `source_version` = version identifier if known
- `source_digest` = SHA-256 of local file (use `compute_source_digest()` from `artifacts.metadata`)
- `summary`, `contribution`, `threat_model`, `algorithms`, `security_claims`, `implementation_notes`, `version_comparison`, `open_questions` = your analysis content

**Required `## Variants` section (data-driven fork check):**

The review body must include a `## Variants` section with two explicit machine-parseable lines, even when there are no variants. This section drives Step 7's fork gate — the gate reads the data here, it does not re-judge the prose.

Format:

```
## Variants

- variants_found: <yes|no>
- variants_reconciled: <yes|no|n/a>

<If variants_found: yes, list each variant on its own line with a one-line description and whether it is the chosen one.>
```

Examples of "variants" that must be declared: multiple paper versions (eprint rounds, conference vs journal), multiple parameter sets, algorithm variants within one paper, attacks or follow-up papers that would change scope.

### Step 6: Record open questions

Append any unresolved questions to `.cryptoworkbench/workbench/open_questions.md`.

### Step 7: Surface findings & check for forks (decision gate)

Summarize to the user, out loud, before moving on:

- what the source is proposing (1–2 sentences)
- the 2–4 key technical findings
- whether any claim or assumption materially affects implementation scope

**Fork check is data-driven.** Read the `## Variants` section from the review artifact written in Step 5:

- If `variants_found: no` → continue and recommend `crypto-extract-spec`. Do not ask.
- If `variants_found: yes` and `variants_reconciled: yes` → present the chosen variant to the user and continue. Ask only for confirmation, not for a fresh choice.
- If `variants_found: yes` and `variants_reconciled: no` or `n/a` → **stop and ask the user to choose** before proceeding to `crypto-extract-spec`. List the variants with their one-line descriptions. Record the chosen one in `decisions.md` under a new `## Variant selection: <target>` section, then re-run Step 5 to update the review artifact with `variants_reconciled: yes`.

This gate never relies on model judgment — it reads `yes`/`no` from the artifact.

## Shared modules

- `specs.build_review` — `build_review()`
- `artifacts.metadata` — `compute_source_digest()`

## Invocation convention

Shared Python modules ship inside this plugin under `${CODEX_PLUGIN_ROOT}/src/`. The user's current working directory is their working project — that is where `.cryptoworkbench/` lives and where any relative path like `workbench_root` resolves.

When invoking Python from this skill:

- Add the plugin's `src/` to the Python path. Inline form: `PYTHONPATH="${CODEX_PLUGIN_ROOT}/src" python ...`. Inside a script: `sys.path.insert(0, "${CODEX_PLUGIN_ROOT}/src")`.
- Do not assume the cwd is the plugin repo. The cwd is the user's project.
- Pass `workbench_root` as a path relative to the user's cwd (typically `.cryptoworkbench`).
- For calls with multi-line content (code blocks, long strings), use a heredoc-fed script or a temporary `.py` file — not inline `python -c` with shell quoting.
