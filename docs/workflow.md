# Workflow

## Stages

1. Initialize a target workspace with `.cryptoworkbench/corpus`, `.cryptoworkbench/extracted`, `.cryptoworkbench/workbench`, and `.cryptoworkbench/cache`.
2. Ingest source material into the corpus.
3. Review papers and standards.
4. Extract notation and pseudocode.
5. Build implementation specs and test plans.
6. Map libraries and tools.
7. Review the implementation plan.
8. Implement and test.
9. Run security review.

Each stage should write artifacts into `.cryptoworkbench/` and preserve open questions.

## Topic mode

For a problem no single paper solves, the first stages are replaced:

1. `crypto-scenario` records the scenario and research angle and collects the paper set.
2. `crypto-multi-review` reviews each paper against the scenario.
3. `crypto-synthesize` composes a design from the papers. Every cross-paper splice needs the user's approval, and the result is classified `Research prototype / novel construction`.

The composed design then enters the normal pipeline at `crypto-extract-spec`.
