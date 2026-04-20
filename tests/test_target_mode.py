"""Target schema round-trip for topic-mode fields."""

from workbench.target import load_target, save_target


def test_topic_mode_round_trip(tmp_path):
    workbench_root = tmp_path / ".cryptoworkbench"
    (workbench_root / "workbench").mkdir(parents=True)

    save_target(
        workbench_root,
        {
            "name": "multi-oprf",
            "type": "topic",
            "primary_sources": [],
            "status": "scenario_pending",
            "mode": "topic",
            "scenario_id": "scenario-multi-oprf-001",
            "research_angle": "Side-channel-hardened OPRF on constrained device",
            "papers": [
                {"path": "corpus/papers/paper1.md", "sha256": "abc123"},
                {"path": "corpus/papers/paper2.md", "sha256": "def456"},
            ],
        },
    )

    loaded = load_target(workbench_root)
    assert loaded["mode"] == "topic"
    assert loaded["scenario_id"] == "scenario-multi-oprf-001"
    assert loaded["research_angle"].startswith("Side-channel-hardened")
    assert len(loaded["papers"]) == 2
    assert loaded["papers"][0]["sha256"] == "abc123"


def test_single_paper_target_has_empty_topic_fields_by_default(tmp_path):
    """Loading a fresh target yields empty topic fields — single-paper flow is unaffected."""
    workbench_root = tmp_path / ".cryptoworkbench"
    (workbench_root / "workbench").mkdir(parents=True)

    target = load_target(workbench_root)
    assert target["mode"] == ""
    assert target["scenario_id"] == ""
    assert target["research_angle"] == ""
    assert target["papers"] == []
