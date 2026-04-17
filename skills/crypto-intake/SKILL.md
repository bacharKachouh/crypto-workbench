# crypto-intake

Ingest and classify local source material. Optionally search online if workspace config permits.

## Gate

Verify `.cryptoworkbench/` workspace exists. If not, tell the user to run `crypto-init` first.

Read the current target using `load_target(workbench_root)` from `workbench.target`. If `status == "draft"` and `name` is empty (i.e. crypto-init was run with the deferred path), tell the user:

> "Target is still deferred. I can scan whatever is in `corpus/` and build a source index, but the index needs a target name. Want to (a) name the target now, (b) let me scan and use a placeholder name I'll ask you to rename afterwards, or (c) go back and run `crypto-init` again?"

Branch A (name now): prompt for `name`, `type`, `primary_sources`, call `save_target(...)` with `status: "intake"`, continue.
Branch B (placeholder): continue with the literal name `unnamed-target` and record an open question reminding the user to rename.
Branch C (bail out): stop and point the user back to `crypto-init`.

## Steps

### Step 1: Check search consent (lazy)

Read `.cryptoworkbench/workbench/config.yaml` using `load_config()` from `config.loader` and check `get_search_policy()`.

**Do not prompt for policy up front.** The policy is only needed when a fetch is about to happen. Flow:

- If a `search_policy` is already recorded — honor it and continue.
- If absent — continue to Step 2 without asking. Only if Step 5 (sufficiency assessment) concludes that a fetch is required *and* no policy is on file, then prompt the user with both decisions in a single message:
  > "Local corpus is insufficient for this target. I'd like to fetch `<URL>` because `<reason>`. Two questions:
  >  1. Allow online search in this workspace at all? (yes/no — stored as a ceiling, not silent-consent)
  >  2. Approve *this specific fetch* right now? (yes/no)"

Record the ceiling answer with `set_search_policy(config_path, allowed=True|False)`. Record the per-fetch answer in memory for this run only.

**Policy semantics (unchanged):**
- `allowed=False` — never reach out to the network; work with whatever is in `corpus/`.
- `allowed=True` — online search is *permitted*, but not automatic. Per-fetch ask remains mandatory every time ("I'd like to fetch <URL> because <reason>. OK?"). The policy is a ceiling, not a silent-consent flag.

### Step 2: Fetch URL primary sources (if any, with consent)

If `current_target.primary_sources` contains any `http(s)://` entries, handle them before scanning:

1. Check search policy (lazy — Step 1). If policy is absent, trigger the combined policy + per-fetch consent prompt now (this is the first actual need for the policy).
2. For each URL, ask the user per-fetch: "I'd like to fetch `<URL>` because it was listed as a primary source. OK?"
3. For each approved URL, call `fetch_url(url, workbench_root, policy_allowed=True, per_fetch_consent=True, reason="primary source")` from `corpus.fetch_url`. The module writes the payload to `corpus/fetched/` and returns provenance (url, path, content_type, size, sha256, fetched_at).
4. Update `current_target.primary_sources` entries: replace the URL with the fetched local path, and record the provenance under `current_target.fetched_provenance`.

If the user refuses a fetch, leave the URL in `primary_sources` and add an open question. Do not fail the skill — downstream skills can still walk, just without that source.

### Step 3: Extract PDF text

Before scanning, call `parsing.pdf_to_text.run(corpus_root=...)` to walk `corpus/papers/`, `corpus/standards/`, and `corpus/fetched/` and write a companion `.md` for every `.pdf` found. The `.md` is what downstream skills and the agent Read; the PDF remains as the authoritative source.

If `pypdf` is not installed, the module will skip each PDF and return `skipped` entries with a reason. Report the skip list to the user and recommend installing `pypdf` (or providing a manually-extracted `.md`).

### Step 4: Scan the corpus

Run `scan_corpus(corpus_root)` from `corpus.scan_local` where `corpus_root` is `.cryptoworkbench/corpus`.

This returns a dict keyed by subdirectory (papers, standards, notes, drafts, prior_impls, fetched) with lists of file entries.

### Step 5: Classify documents

Run `classify_inventory(inventory)` from `corpus.classify_docs`, passing the scan output.

This adds `doc_type` and `authority` to each entry.

### Step 6: Rank sources

Run `rank_entries(classified_entries)` from `corpus.rank_sources`.

This adds `priority_score` and returns entries sorted highest-first.

### Step 7: Assess sufficiency

Review the ranked inventory. Determine whether the corpus contains:
- A primary paper or standard for the target
- Relevant supplementary material

If the corpus is insufficient:

- If no search policy is recorded, invoke the combined policy + per-fetch consent flow from Step 1.
- If policy allows and the user approves a specific fetch, call `corpus.fetch_url.fetch_url(...)` with the per-fetch consent signal. Save the returned provenance dict; record `fetched_from`, `downloaded_at`, and `retrieval_method` in the source index.
- If policy denies or the user refuses, record an open question ("corpus insufficient, fetch declined") and continue with what exists.

Note: API-backed discovery (arXiv / OpenAlex / Semantic Scholar) is handled by `papers.search_*` modules (future work). Until then, URL fetches are the online path.

### Step 8: Build source index

Run `build_source_index()` from `specs.build_source_index` with:
- `workbench_root` = `.cryptoworkbench`
- `target` = current target name from `current_target.yaml`
- `created_from` = `corpus/` scan
- `sources` = list of dicts, each with: id, type, title, path, version, authority_level, notes (and fetched_from, downloaded_at, retrieval_method, sha256 for fetched sources)

### Step 9: Record open questions

Append any unresolved provenance questions to `.cryptoworkbench/workbench/open_questions.md`.

Report the intake summary to the user — including any PDF→text extractions performed and any URL fetches — and recommend `crypto-paper-review` as the next step.

## Shared modules

- `config.loader` — `load_config()`, `get_search_policy()`, `set_search_policy()`
- `corpus.scan_local` — `scan_corpus()`
- `corpus.classify_docs` — `classify_inventory()`
- `corpus.rank_sources` — `rank_entries()`
- `corpus.fetch_url` — `fetch_url()` (with explicit `policy_allowed` + `per_fetch_consent` args)
- `parsing.pdf_to_text` — `extract_pdf_text()`, `write_extracted_text()`, `run()`
- `specs.build_source_index` — `build_source_index()`
- `workbench.target` — `load_target()`, `save_target()`, `check_target_fields()`

## Invocation convention

Shared Python modules ship inside this plugin under `${CLAUDE_PLUGIN_ROOT}/src/`. The user's current working directory is their working project — that is where `.cryptoworkbench/` lives and where any relative path like `workbench_root` resolves.

When invoking Python from this skill:

- Add the plugin's `src/` to the Python path. Inline form: `PYTHONPATH="${CLAUDE_PLUGIN_ROOT}/src" python ...`. Inside a script: `sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/src")`.
- Do not assume the cwd is the plugin repo. The cwd is the user's project.
- Pass `workbench_root` as a path relative to the user's cwd (typically `.cryptoworkbench`).
- For calls with multi-line content (code blocks, long strings), use a heredoc-fed script or a temporary `.py` file — not inline `python -c` with shell quoting.
