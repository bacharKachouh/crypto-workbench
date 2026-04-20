"""Registry-backed check that standard primitives are flagged while
genuinely research-grade scenarios pass.
"""

from scenarios.research_angle_check import check_scenario


def test_flags_aes_gcm():
    text = "We need AES-GCM for at-rest encryption in our storage service."
    result = check_scenario(text)
    assert result["is_standard"] is True
    assert "AES-GCM" in result["matched"]
    assert result["suggested_redirect"] is not None
    assert "standardized primitives" in result["suggested_redirect"]


def test_flags_ecdsa_and_hkdf():
    text = "Mixing ECDSA for signatures and HKDF for key derivation."
    result = check_scenario(text)
    assert result["is_standard"] is True
    assert "ECDSA" in result["matched"]
    assert "HKDF" in result["matched"]


def test_passes_research_scenario():
    text = (
        "Threshold fully-homomorphic encryption with bootstrapping for secure "
        "multi-party computation in a leaky-randomness adversary model. We "
        "need a novel composition of FHE.CKKS with distributed keygen that "
        "resists partial key-recovery under t-1 corruptions."
    )
    result = check_scenario(text)
    assert result["is_standard"] is False
    assert result["matched"] == []
    assert result["suggested_redirect"] is None


def test_passes_exotic_oprf_scenario():
    text = (
        "Oblivious pseudorandom function evaluation with malicious-server "
        "security under timing leakage for use in a private set intersection "
        "protocol over LoRaWAN radios."
    )
    result = check_scenario(text)
    # OPRF is not in the standard-primitives list; this should pass.
    assert result["is_standard"] is False
