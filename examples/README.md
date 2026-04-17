# Crypto Workbench — Bundled Demo Targets

This directory ships small, self-contained example targets used for onboarding
and for testing the end-to-end plugin workflow. They are **demos, not real
research targets**, and should not be used as reference implementations.

Each example has:

- `paper.md` — a short self-authored spec written specifically for the demo.
  It is not an external publication, has no external copyright, and is safe
  to redistribute.
- `target.yaml` — the `current_target.yaml` preset that `install_example`
  copies into the user's workbench.
- `README.md` — labelling + intended-use note.

Install a demo from the `crypto-init` skill ("Use demo" path) or directly via
`scaffolding.install_example.install_example(workbench_root, name)`.
