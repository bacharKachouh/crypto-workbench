# HKDF-Demo: A Minimal HMAC-Based Key Derivation Function for Plugin Onboarding

**Status:** pedagogical demo. Not a real research artifact. Not reviewed for
deployment. The scheme described here is a toy; do not use it in production.

## Abstract

HKDF-Demo is a minimal HMAC-based key-derivation function written specifically
as an onboarding example for the Crypto Workbench plugin. It takes a
high-entropy secret and a short context label and produces a fixed-length
derived key. It is a deliberately simplified sibling of HKDF (RFC 5869)
with two stages — `extract` and `expand` — but without salt handling or
variable-length output.

The contribution of the demo is purely structural: the document exercises
every stage of the plugin (paper-review, notation extraction, ambiguity log,
implementation spec, library mapping, plan review, implementation, security
review) without requiring the reader to ingest a real 30-page paper.

## Notation

- `H` — a fixed cryptographic hash function. For the demo we fix
  `H = SHA-256`, so `hLen = 32` bytes.
- `HMAC(key, msg)` — standard HMAC construction instantiated with `H`.
- `IKM` — input keying material (a byte string, any length).
- `info` — context / domain-separation label (a byte string, ≤ 255 bytes).
- `PRK` — pseudorandom key produced by the extract stage, `hLen` bytes.
- `OKM` — output keying material (derived key), `hLen` bytes.

## Parameters

| Parameter | Value | Note |
| --- | --- | --- |
| `H`       | SHA-256         | fixed; not user-configurable in this demo |
| `hLen`    | 32 bytes        | SHA-256 output length |
| `L`       | `hLen` = 32     | output length, fixed in this demo |
| `info_max_len` | 255 bytes | hard cap |

## Algorithms

### Extract

```
def extract(IKM: bytes) -> bytes:       # returns PRK of length hLen
    # Uses a fixed zero salt of length hLen (demo simplification).
    salt = b"\x00" * hLen
    PRK = HMAC(key=salt, msg=IKM)
    return PRK
```

### Expand

```
def expand(PRK: bytes, info: bytes) -> bytes:   # returns OKM of length L
    if len(info) > 255:
        raise ValueError("info too long")
    # Single block because L == hLen; HKDF's N-block loop is unnecessary.
    T1 = HMAC(key=PRK, msg=info + b"\x01")
    OKM = T1
    return OKM
```

### Derive (top-level)

```
def derive(IKM: bytes, info: bytes) -> bytes:
    PRK = extract(IKM)
    OKM = expand(PRK, info)
    return OKM
```

## Security claims (demo-only)

Under the assumption that `HMAC-SHA-256` is a PRF, HKDF-Demo's output is
indistinguishable from random for adversaries who do not know `IKM`, provided
`IKM` has sufficient min-entropy. This claim is inherited from the HKDF
paper (Krawczyk 2010) for the single-block expand case, up to the
fixed-zero-salt simplification.

**Caveats the demo intentionally ignores:**

- salt handling (HKDF-Demo always uses zero-salt)
- variable-length output (HKDF-Demo emits exactly `hLen` bytes)
- info-less derivation
- streaming / chunked IKM

These omissions exist so downstream plugin skills can legitimately flag the
scheme as "reference prototype, not production."

## Serialization

- `IKM`, `info`, `PRK`, `OKM` are all raw byte strings.
- No framing, no length prefix, no version byte. If a real deployment
  wanted those, it would have to wrap the primitive.
- `info` is a label chosen by the caller for domain separation. The
  demo does not prescribe a format.

## Test vectors (worked example)

```
IKM  = b"demo input keying material"
info = b"demo-context"

PRK = HMAC(SHA-256, key=0x00...00 (32 bytes), msg=IKM)
OKM = HMAC(SHA-256, key=PRK, msg=info || 0x01)
```

A reference-style implementation should ship at minimum three test vectors
with explicit hex values: zero-length `info`, a short `info`, and a
maximum-length `info` (255 bytes).

## Implementation notes

- `HMAC` should be delegated to a standard library (Python `hmac`, Rust
  `hmac` crate, Go `crypto/hmac`). Do not hand-roll HMAC.
- The construction is deterministic — no randomness is required at runtime.
- Input validation: `len(info) <= 255`; everything else is opaque bytes.
- Failure modes: invalid `info` length → raise. No partial output.

## Known limitations

This is a DEMO scheme. Known gaps vs real HKDF:

1. no salt parameter (always zero)
2. no variable-length output (L fixed)
3. no negative-input tests specified for the demo
4. no side-channel requirements specified

Any implementation produced from this spec should be labeled
"Reference-style implementation (demo)" and not shipped into a production
protocol.
