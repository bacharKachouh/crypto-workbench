"""Registry-backed sanity check — is the declared scenario actually research?

This module performs a lightweight check against the bundled registry's
algorithms list. If the scenario text mentions a primitive that is a
standardized, mature-library primitive (e.g., AES-GCM, ECDSA, HKDF),
the check flags it. The skill then surfaces the match to the user and
requires a written justification to proceed.

The check is intentionally keyword-based: it errs on the side of
flagging. The user always has the final say via an override + written
justification. We do not block silently; we surface and ask.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from libraries.registry_loader import load_all_registries

MODULE = "scenarios.research_angle_check"

# Known standardized primitives that have mature, reviewed library
# implementations. If the user's scenario maps to one of these, the
# check pushes back. Keys are display labels; values are keyword
# patterns (lowercase) that match common ways of naming the primitive.
_STANDARD_PRIMITIVES: dict[str, list[str]] = {
    "AES-GCM": ["aes-gcm", "aes gcm", "aesgcm"],
    "AES-CTR": ["aes-ctr", "aes ctr"],
    "ChaCha20-Poly1305": ["chacha20-poly1305", "chacha20 poly1305", "chacha-poly"],
    "HKDF": ["hkdf"],
    "HMAC": ["hmac-sha", "hmac sha", "hmac-256", "hmac-512"],
    "SHA-2": ["sha-256", "sha256", "sha-512", "sha512"],
    "SHA-3": ["sha-3", "sha3", "keccak"],
    "ECDSA": ["ecdsa"],
    "EdDSA / Ed25519": ["ed25519", "eddsa"],
    "ECDH / X25519": ["ecdh", "x25519"],
    "RSA-OAEP": ["rsa-oaep", "rsa oaep"],
    "RSA-PSS": ["rsa-pss", "rsa pss"],
    "TLS 1.3": ["tls 1.3", "tls1.3"],
    "Kyber (FIPS 203 ML-KEM)": ["ml-kem", "fips 203", "ml kem"],
    "Dilithium (FIPS 204 ML-DSA)": ["ml-dsa", "fips 204", "ml dsa"],
}


def _scan_keywords(scenario_text: str) -> list[str]:
    """Return the display labels of standard primitives mentioned in the text."""
    lowered = scenario_text.lower()
    hits: list[str] = []
    for label, patterns in _STANDARD_PRIMITIVES.items():
        for kw in patterns:
            if re.search(rf"\b{re.escape(kw)}\b", lowered):
                hits.append(label)
                break
    return hits


def _suggested_redirect(matches: list[str]) -> str | None:
    if not matches:
        return None
    joined = ", ".join(matches)
    return (
        f"This scenario mentions standardized primitives ({joined}) that are "
        "covered by mature audited libraries. The existing `crypto-library-map` "
        "flow in a single-paper target can match them directly. Want to switch, "
        "or is there a specific research angle that puts this beyond the "
        "standard library path?"
    )


def check_scenario(
    scenario_text: str,
    registry_root: str | Path | None = None,
) -> dict[str, Any]:
    """Check whether a scenario is research-grade or covered by standards.

    Returns a dict:
      - is_standard: bool — at least one standardized primitive matched
      - matched: list[str] — display labels of matched primitives
      - suggested_redirect: str | None — human-readable redirect message
      - registry_loaded: bool — whether the registry was loaded successfully
    """
    matched = _scan_keywords(scenario_text)

    registry_loaded = False
    if registry_root is not None:
        data = load_all_registries(registry_root)
        registry_loaded = bool(data)

    return {
        "module": MODULE,
        "is_standard": bool(matched),
        "matched": matched,
        "suggested_redirect": _suggested_redirect(matched),
        "registry_loaded": registry_loaded,
    }


def run(**context: Any) -> dict[str, Any]:
    scenario_text = context.get("scenario_text", "")
    registry_root = context.get("registry_root")
    return check_scenario(scenario_text, registry_root)
