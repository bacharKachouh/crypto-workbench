# Security Model

Crypto Workbench helps structure cryptographic implementation work, but it does not prove security.

## Assumptions

- Source material may be incomplete, superseded, or ambiguous.
- Generated implementation plans require expert review.
- Library support and security posture must be checked against the selected version.
- Side-channel properties depend on language, compiler, platform, and integration details.

## Required Review Areas

- Correct primitive selection.
- Parameter validation.
- Randomness and nonce handling.
- Serialization and domain separation.
- Constant-time behavior and side-channel exposure.
- Test vector and negative-test coverage.
