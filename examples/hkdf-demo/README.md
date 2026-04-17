# hkdf-demo — onboarding example target

**This is a pedagogical demo, not a real research artifact.**

The demo paper `paper.md` is a short self-contained description of a trivial
key-derivation function ("HKDF-Demo") written specifically to exercise the
Crypto Workbench pipeline end-to-end:

- It has enough structure (abstract, parameters, algorithm, claims,
  serialization note) for every skill to produce a non-trivial artifact.
- It is small enough to review in minutes.
- It is self-authored and carries no external licence or copyright.

## What it is NOT

- Not RFC 5869 HKDF. It is deliberately simplified.
- Not a production KDF. Do not use it for anything beyond walking through
  the plugin.
- Not a security reference. Any "security claim" in the demo paper is for
  demonstration only.

## Install

From the `crypto-init` skill, choose the "Use demo" path.

Programmatic install:

```python
from scaffolding.install_example import install_example
install_example(workbench_root=".cryptoworkbench", name="hkdf-demo")
```
