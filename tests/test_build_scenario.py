"""Scenario artifact writer round-trip."""

from pathlib import Path

from scenarios.build_scenario import build_scenario


def test_writes_scenario_with_papers_and_rejected_standards(tmp_path):
    workbench_root = tmp_path / ".cryptoworkbench"
    (workbench_root / "extracted" / "scenarios").mkdir(parents=True)

    path = build_scenario(
        workbench_root=workbench_root,
        target="multi-oprf",
        title="Multi-paper OPRF scenario",
        scenario_prose="Side-channel-hardened OPRF on smartcards.",
        research_angle="Existing OPRFs assume branch-free randomness sampling.",
        rejected_standards=[
            {"primitive": "AES-GCM", "user_justification": "Used only for an auxiliary channel, orthogonal to the OPRF."}
        ],
        papers=[
            {"path": "corpus/papers/a.md", "sha256": "a" * 64},
            {"path": "corpus/papers/b.md", "sha256": "b" * 64},
        ],
        open_questions="None.",
    )

    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "artifact_type: scenario" in text
    assert "## Scenario" in text
    assert "Side-channel-hardened OPRF" in text
    assert "## Research Angle" in text
    assert "AES-GCM" in text  # rejected standard recorded
    assert "## Papers" in text
    assert "corpus/papers/a.md" in text
    assert "corpus/papers/b.md" in text
