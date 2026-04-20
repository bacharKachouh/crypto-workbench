"""Round 1-4 artifact writers."""

from pathlib import Path

import pytest

from synthesis.build_triage import build_triage
from synthesis.build_deepdive import build_deepdive
from synthesis.build_splices import build_splices
from synthesis.build_composed_design import build_composed_design, CLASSIFICATION


def _prep(tmp_path: Path) -> Path:
    root = tmp_path / ".cryptoworkbench"
    (root / "extracted" / "synthesis").mkdir(parents=True)
    return root


def test_triage_happy_path(tmp_path):
    root = _prep(tmp_path)
    path = build_triage(
        workbench_root=root,
        target="x",
        title="Triage",
        created_from="scenario-x-001",
        decisions=[
            {"paper_id": "review-x-001", "proposed": "KEEP", "final": "KEEP", "reason": "Best fit"},
            {"paper_id": "review-x-002", "proposed": "KEEP", "final": "SUPPORTING", "reason": "Better as evidence"},
            {"paper_id": "review-x-003", "proposed": "REJECT", "final": "REJECT", "reason": "Wrong threat model"},
        ],
        summary="Three papers triaged.",
    )
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "artifact_type: synthesis_triage" in text
    assert "round_status: completed" in text


def test_triage_rejects_unknown_label(tmp_path):
    root = _prep(tmp_path)
    with pytest.raises(ValueError):
        build_triage(
            workbench_root=root,
            target="x",
            title="Triage",
            created_from="scenario-x-001",
            decisions=[{"paper_id": "p", "proposed": "NOPE", "final": "KEEP", "reason": ""}],
        )


def test_triage_all_rejected_status(tmp_path):
    root = _prep(tmp_path)
    path = build_triage(
        workbench_root=root,
        target="x",
        title="Triage",
        created_from="scenario-x-001",
        decisions=[
            {"paper_id": "p1", "proposed": "REJECT", "final": "REJECT", "reason": "Wrong model"},
            {"paper_id": "p2", "proposed": "REJECT", "final": "REJECT", "reason": "Wrong model"},
        ],
        round_status="all_rejected",
    )
    text = path.read_text(encoding="utf-8")
    assert "round_status: all_rejected" in text


def test_deepdive_writes_logs(tmp_path):
    root = _prep(tmp_path)
    path = build_deepdive(
        workbench_root=root,
        target="x",
        title="Deep-dive",
        created_from="synthesis-triage-x-001",
        logs={
            "review-x-001": [
                {"q": "What's the RO model assumption?", "a": "Paper uses ROM on H only.", "source_ref": "Section 3.2"},
            ],
        },
    )
    text = path.read_text(encoding="utf-8")
    assert "artifact_type: synthesis_deepdive" in text
    assert "RO model assumption" in text


def test_splices_requires_all_five_fields(tmp_path):
    root = _prep(tmp_path)
    with pytest.raises(ValueError):
        build_splices(
            workbench_root=root,
            target="x",
            title="Splices",
            created_from="synthesis-deepdive-x-001",
            backbone={"paper_id": "review-x-001", "reason": "best"},
            decisions=[
                # missing proof_gap_note + status
                {
                    "borrowed_piece": "Gaussian sampler",
                    "into": "keygen step 4",
                    "source_paper": "review-x-002",
                    "scenario_justification": "constant-time",
                },
            ],
        )


def test_splices_rejects_unknown_status(tmp_path):
    root = _prep(tmp_path)
    with pytest.raises(ValueError):
        build_splices(
            workbench_root=root,
            target="x",
            title="Splices",
            created_from="synthesis-deepdive-x-001",
            backbone={"paper_id": "review-x-001", "reason": "best"},
            decisions=[
                {
                    "borrowed_piece": "sampler",
                    "into": "keygen",
                    "source_paper": "review-x-002",
                    "scenario_justification": "ct",
                    "proof_gap_note": "unknown",
                    "status": "maybe",
                },
            ],
        )


def test_splices_happy_path(tmp_path):
    root = _prep(tmp_path)
    path = build_splices(
        workbench_root=root,
        target="x",
        title="Splices",
        created_from="synthesis-deepdive-x-001",
        backbone={"paper_id": "review-x-001", "reason": "Best overall scenario fit"},
        decisions=[
            {
                "borrowed_piece": "Gaussian sampler (Alg 3)",
                "into": "KeyGen step 4 of backbone",
                "source_paper": "review-x-002",
                "scenario_justification": "Constant-time on smartcards",
                "proof_gap_note": "Backbone proof assumes rejection sampling; new proof sketch needed.",
                "status": "approve",
                "user_reason": "worth the trade-off",
            },
        ],
    )
    text = path.read_text(encoding="utf-8")
    assert "artifact_type: synthesis_splices" in text
    assert "Gaussian sampler" in text


def test_composed_design_hardcoded_classification(tmp_path):
    root = _prep(tmp_path)
    path = build_composed_design(
        workbench_root=root,
        target="x",
        title="Composed design",
        created_from="synthesis-splices-x-001",
        scenario_summary="Side-channel-hardened OPRF on smartcards.",
        research_angle="Existing OPRFs assume branch-free sampling.",
        backbone={"paper_id": "review-x-001", "reason": "best fit"},
        approved_splices=[
            {
                "borrowed_piece": "Gaussian sampler (Alg 3)",
                "into": "KeyGen step 4",
                "source_paper": "review-x-002",
                "scenario_justification": "Constant-time",
                "proof_gap_note": "Proof does not carry over.",
            }
        ],
        contributions=[
            {"paper_id": "review-x-001", "role": "backbone", "what_we_used": "Scheme skeleton", "why": "Best fit"},
            {"paper_id": "review-x-002", "role": "splice-source", "what_we_used": "Sampler", "why": "Constant-time"},
            {"paper_id": "review-x-003", "role": "rejected", "what_we_used": "none", "why": "Wrong model"},
        ],
        risk_ledger=["No end-to-end proof for the composed scheme."],
        pseudocode="```\nKeyGen(): ...\n```",
    )
    text = path.read_text(encoding="utf-8")
    assert "artifact_type: composed_design" in text
    assert CLASSIFICATION in text
    assert "cannot be downgraded" in text
    assert "| paper_id | role |" in text
    assert "Risk Ledger" in text


def test_composed_design_requires_non_empty_risk_ledger(tmp_path):
    root = _prep(tmp_path)
    with pytest.raises(ValueError):
        build_composed_design(
            workbench_root=root,
            target="x",
            title="Composed design",
            created_from="synthesis-splices-x-001",
            scenario_summary="...",
            research_angle="...",
            backbone={"paper_id": "p1", "reason": "..."},
            approved_splices=[],
            contributions=[
                {"paper_id": "p1", "role": "backbone", "what_we_used": "everything", "why": "..."},
            ],
            risk_ledger=[],
            pseudocode="",
        )


def test_composed_design_requires_valid_role(tmp_path):
    root = _prep(tmp_path)
    with pytest.raises(ValueError):
        build_composed_design(
            workbench_root=root,
            target="x",
            title="Composed design",
            created_from="synthesis-splices-x-001",
            scenario_summary="...",
            research_angle="...",
            backbone={"paper_id": "p1", "reason": "..."},
            approved_splices=[],
            contributions=[
                {"paper_id": "p1", "role": "weirdrole", "what_we_used": "x", "why": "y"},
            ],
            risk_ledger=["a risk"],
            pseudocode="",
        )
