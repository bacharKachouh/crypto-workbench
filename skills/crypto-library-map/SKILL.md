# crypto-library-map

Map required cryptographic primitives to libraries and tools.

## Gate

Verify `extracted/impl_specs/` contains an impl spec for the current target. If not, tell the user to run `crypto-extract-spec` first.

## Steps

### Step 1: Identify requirements

Read the impl spec. Extract the required:
- Math families (lattices, pairings, finite fields, etc.)
- Cryptographic primitives (KEM, signature, hash, AEAD, etc.)
- Encodings and serialization formats
- Protocol-level dependencies

### Step 2: Load registry data

Run `load_all_registries(registry_root)` from `libraries.registry_loader` where `registry_root` points to the plugin's bundled `registry/` directory (under `${CLAUDE_PLUGIN_ROOT}/registry`).

This returns a dict keyed by category (algorithms, libraries, math_families, tools) with lists of registry entries.

### Step 3: Evaluate library options

For each required primitive, evaluate available libraries from the registry:
- Maintenance status and version coverage
- Side-channel posture (known, unknown, mitigated, vulnerable)
- License compatibility
- Platform support
- Whether the library covers the exact parameter set needed

Prefer maintained, reviewed implementations over custom primitive code.

### Step 4: Record rejected options

For each library considered but rejected, record the reason (unmaintained, missing primitive, license issue, known vulnerability, etc.).

### Step 4.5: Surface library forks (decision gate)

If more than one valid library path exists for any primitive (e.g., `cryptography` vs `pyca/cryptography` vs `oqs-python` for a lattice KEM), summarize the tradeoffs to the user:

- maturity / audit status
- side-channel posture
- license implications
- platform support
- whether parameter coverage is exact

Ask the user which path they want. Do not silently pick the "default" — picking a library is a scope-shaping decision that the user should own.

If every primitive has exactly one reasonable library choice, do not stop for a fork decision — but announce the one-option path briefly before writing the artifact ("One viable library per primitive: [list]. Proceeding unless you object.") so the user can still redirect. Do not silently skip the user.

### Step 5: Produce library mapping artifact

Call `write_yaml_artifact()` from `artifacts.writer` with:
- `artifact_type` = `"library_mapping"`
- `target` = current target name
- `created_from` = impl spec artifact id
- `content` = dict following base spec Section 7.6:
  - `primitives_needed` = list of required primitives
  - `mappings` = list of dicts with: primitive, library, function_or_api, version, license, side_channel_status, notes
  - `rejected` = list of dicts with: library, reason
  - `recommendation` = summary recommendation
- `workbench_root` = `.cryptoworkbench`

Report the mapping summary and recommend `crypto-plan-review` as the next step.

## Shared modules

- `libraries.registry_loader` — `load_all_registries()`
- `artifacts.writer` — `write_yaml_artifact()`

## Shared data

- `${CLAUDE_PLUGIN_ROOT}/registry/libraries/` — library metadata
- `${CLAUDE_PLUGIN_ROOT}/registry/algorithms/` — algorithm metadata
- `${CLAUDE_PLUGIN_ROOT}/registry/math_families/` — math family metadata
- `${CLAUDE_PLUGIN_ROOT}/registry/tools/` — tool metadata

## Invocation convention

Shared Python modules ship inside this plugin under `${CLAUDE_PLUGIN_ROOT}/src/`. The user's current working directory is their working project — that is where `.cryptoworkbench/` lives and where any relative path like `workbench_root` resolves.

When invoking Python from this skill:

- Add the plugin's `src/` to the Python path. Inline form: `PYTHONPATH="${CLAUDE_PLUGIN_ROOT}/src" python ...`. Inside a script: `sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/src")`.
- Do not assume the cwd is the plugin repo. The cwd is the user's project.
- Pass `workbench_root` as a path relative to the user's cwd (typically `.cryptoworkbench`).
- For calls with multi-line content (code blocks, long strings), use a heredoc-fed script or a temporary `.py` file — not inline `python -c` with shell quoting.
