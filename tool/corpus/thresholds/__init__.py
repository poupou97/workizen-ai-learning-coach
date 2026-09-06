"""Trust-gate SENSITIVITY tooling (Round 5, Lane A3, Founder order §8).

RESEARCH ONLY. This package answers one question and refuses to answer another.

  It answers:  "IF the gate were X, then how much content is served, how much of it is
                wrong, how much teaching-critical damage is served, how much is withheld,
                and how much currently-withheld clean content would be restored?"
  It refuses:  "which X should we ship?"  No function here recommends a threshold, and
               nothing here writes a production `THRESHOLDS.json`.

Two data planes, never summed (D5):

  · `gold`  — the 54 gold pages / 643 gold learning blocks, joined to the pipeline's own
              per-block SDM output. Truth = the gold anchors/text/roles; wrongness is the
              scorer's own definition (`tc_score.score`), reproduced block by block and
              asserted equal to it page by page. This is the only plane with a *withheld*
              side that has ground truth, so it is the only plane that can measure
              RESTORE.
  · `audit` — the annotated false-trust audit rows (round-3 484-row sample; legacy batch-1
              OLD/NEW). Truth = a human/AI annotator's verdict against a page render.
              These rows are almost all SERVED rows, so this plane can measure what a gate
              would REMOVE from shipped content, never what it would restore.

Nothing here re-runs the pipeline; it reads outputs that already exist on disk.
"""

__all__ = ['evidence', 'gate', 'sweep']
