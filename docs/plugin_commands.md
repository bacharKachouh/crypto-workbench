# Plugin Commands

## Skills

| Skill | Path | Purpose |
|-------|------|---------|
| `crypto-init` | all | Create `.cryptoworkbench/` and choose a starting path |
| `crypto-status` | all | Read-only "where am I?" |
| `crypto-intake` | paper | Scan, classify and optionally fetch source material (with consent) |
| `crypto-paper-review` | paper | Review a paper or standard |
| `crypto-extract-spec` | paper, topic | Notation map, ambiguity log, implementation spec |
| `crypto-library-map` | paper, topic | Match primitives to libraries and tools |
| `crypto-plan-review` | paper, topic | Approve, condition or block the plan |
| `crypto-implement` | paper, topic | Implement test-first |
| `crypto-security-review` | paper, topic | Review the implementation |
| `crypto-scenario` | topic | Scenario, research angle, paper set |
| `crypto-multi-review` | topic | Per-paper review against the scenario |
| `crypto-synthesize` | topic | Compose a research-prototype design |

In Claude Code, invoke a skill as `/crypto-init`. In Codex, invoke it by name.

## Tests

```
pip install -r requirements.txt pytest
python -m pytest
```
