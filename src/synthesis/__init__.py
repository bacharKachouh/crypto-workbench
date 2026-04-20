"""Four-round synthesis workflow for multi-paper (topic-mode) targets.

Rounds:
  1. Triage — classify each paper as KEEP / REJECT / SUPPORTING.
  2. Deep-dive — user-driven Q&A over KEEP papers.
  3. Splices — Claude proposes cross-paper splices; user approves each.
  4. Composed design — assemble backbone + approved splices with
     attribution, proof-gap notes, and risk ledger.
"""
