"""End-to-end integration test for the topic-mode branch.

Walks: scenario → (stub reviews) → triage → deepdive → splices → composed design,
and asserts the composed-design artifact carries the expected classification,
risk ledger, and per-paper attribution.
"""

from pathlib import Path

from workbench.target import load_target, save_target
from scenarios.build_scenario import build_scenario
from synthesis.build_triage import build_triage
from synthesis.build_deepdive import build_deepdive
from synthesis.build_splices import build_splices
from synthesis.build_composed_design import build_composed_design, CLASSIFICATION


def _make_workspace(tmp_path: Path) -> Path:
    root = tmp_path / ".cryptoworkbench"
    for sub in (
        "corpus/papers",
        "extracted/reviews",
        "extracted/scenarios",
        "extracted/synthesis",
        "workbench",
    ):
        (root / sub).mkdir(parents=True)
    return root


def _stub_paper(root: Path, name: str, content: str) -> Path:
    p = root / "corpus" / "papers" / f"{name}.md"
    p.write_text(content, encoding="utf-8")
    return p


def test_topic_flow_end_to_end(tmp_path):
    root = _make_workspace(tmp_path)

    # Stub two papers into the corpus.
    p1 = _stub_paper(root, "paper-alpha", "# Alpha\nA KEM scheme with efficient keygen.")
    p2 = _stub_paper(root, "paper-beta", "# Beta\nA KEM scheme with constant-time encaps.")

    # 1. Target + save.
    save_target(
        root,
        {
            "name": "multi-kem",
            "type": "topic",
            "primary_sources": [],
            "status": "scenario_pending",
            "mode": "topic",
            "scenario_id": "",
            "research_angle": "",
            "papers": [
                {"path": str(p1.relative_to(root.parent)), "sha256": "a" * 64},
                {"path": str(p2.relative_to(root.parent)), "sha256": "b" * 64},
            ],
        },
    )

    # 2. Scenario artifact.
    scenario_path = build_scenario(
        workbench_root=root,
        target="multi-kem",
        title="Multi-KEM scenario",
        scenario_prose="Constant-time KEM for smartcards.",
        research_angle="Efficient keygen combined with constant-time encaps is not a standard combination.",
        rejected_standards=[],
        papers=[
            {"path": str(p1), "sha256": "a" * 64},
            {"path": str(p2), "sha256": "b" * 64},
        ],
    )
    assert scenario_path.exists()

    # 3. Round 1 — triage (pretend multi-review has produced review artifact ids).
    triage_path = build_triage(
        workbench_root=root,
        target="multi-kem",
        title="Triage",
        created_from="scenario-multi-kem-001",
        decisions=[
            {"paper_id": "review-multi-kem-001", "proposed": "KEEP", "final": "KEEP", "reason": "Scheme skeleton fits."},
            {"paper_id": "review-multi-kem-002", "proposed": "SUPPORTING", "final": "SUPPORTING", "reason": "Constant-time encaps useful as splice."},
        ],
        summary="Two papers: one KEEP (backbone candidate), one SUPPORTING (splice donor).",
    )
    assert triage_path.exists()

    # 4. Round 2 — deepdive.
    deepdive_path = build_deepdive(
        workbench_root=root,
        target="multi-kem",
        title="Deep-dive",
        created_from="synthesis-triage-multi-kem-001",
        logs={
            "review-multi-kem-001": [
                {"q": "Is the encaps constant-time?", "a": "No — table lookup in hash step.", "source_ref": "Section 4.1"}
            ],
        },
    )
    assert deepdive_path.exists()

    # 5. Round 3 — splices.
    splices_path = build_splices(
        workbench_root=root,
        target="multi-kem",
        title="Splices",
        created_from="synthesis-deepdive-multi-kem-001",
        backbone={"paper_id": "review-multi-kem-001", "reason": "Backbone: paper-alpha — efficient keygen is the scenario's critical axis."},
        decisions=[
            {
                "borrowed_piece": "Constant-time encapsulation routine",
                "into": "Encaps step of backbone (replaces Section 4.1 table lookup)",
                "source_paper": "review-multi-kem-002",
                "scenario_justification": "Smartcard deployment requires CT; backbone's table lookup leaks.",
                "proof_gap_note": "Backbone's IND-CCA proof relied on the specific encaps structure. New proof sketch needed.",
                "status": "approve",
                "user_reason": "Worth the proof gap for CT.",
            }
        ],
    )
    assert splices_path.exists()

    # 6. Round 4 — composed design.
    composed_path = build_composed_design(
        workbench_root=root,
        target="multi-kem",
        title="Composed Multi-KEM",
        created_from="synthesis-splices-multi-kem-001",
        scenario_summary="Constant-time KEM for smartcards.",
        research_angle="Efficient keygen combined with constant-time encaps is not a standard combination.",
        backbone={"paper_id": "review-multi-kem-001", "reason": "Best keygen efficiency for the scenario."},
        approved_splices=[
            {
                "borrowed_piece": "Constant-time encapsulation",
                "into": "Encaps step",
                "source_paper": "review-multi-kem-002",
                "scenario_justification": "Smartcard CT requirement.",
                "proof_gap_note": "Backbone proof does not carry over.",
            }
        ],
        contributions=[
            {"paper_id": "review-multi-kem-001", "role": "backbone", "what_we_used": "KEM skeleton + keygen", "why": "Most efficient keygen."},
            {"paper_id": "review-multi-kem-002", "role": "splice-source", "what_we_used": "Constant-time encaps routine", "why": "Smartcard CT requirement."},
        ],
        risk_ledger=[
            "Backbone's IND-CCA proof is invalidated by the encaps replacement.",
            "Composition introduces a new randomness dependency not analyzed by either paper.",
        ],
        pseudocode="```\nKeyGen():\n  ...  # from backbone (alpha)\nEncaps():\n  ...  # from splice (beta)\n```",
    )
    assert composed_path.exists()

    text = composed_path.read_text(encoding="utf-8")
    # Classification invariants
    assert f"**{CLASSIFICATION}**" in text
    assert "cannot be downgraded" in text
    # Attribution invariants
    assert "review-multi-kem-001" in text
    assert "review-multi-kem-002" in text
    # Risk ledger non-empty
    assert "IND-CCA proof is invalidated" in text
    # Pseudocode present
    assert "KeyGen()" in text
    assert "Encaps()" in text

    # 7. Target still carries the topic-mode fields we put on it.
    loaded = load_target(root)
    assert loaded["mode"] == "topic"
    assert len(loaded["papers"]) == 2
