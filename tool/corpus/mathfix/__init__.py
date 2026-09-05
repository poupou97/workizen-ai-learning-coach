"""Round 5 · Lane A2 — MATH / FORMULA / NUMBER accuracy.

The Founder's order for this lane, in one line:

    formula withheld → specialised extraction → deterministic validation → restored structured formula
    — and never «formula withheld forever», never «reconstructed speculatively from OCR prose».

So this package never reads a block's flattened text and guesses what the arithmetic «must» have
been. It reads the PAGE:

  1. `inkmask`   a binary ink raster of the printed page, with no dependency the CI runner lacks
                 (a PyMuPDF loader exists, but every rule is testable on an ASCII picture).
  2. `bars`      horizontal ink runs — the printed vinculum, the minus sign, the table rule.
  3. `tokens`    the OCR lines of the same page, as geometry rather than as prose.
  4. `detect`    formula REGIONS: a bar with ink above and below it is a stacked fraction region
                 whether or not the OCR read either half. A region is detected from the page, so a
                 region whose digits the OCR lost is still *found* — and then withheld, not missed.
  5. `extract`   a RepairCandidate assembled ONLY from original observations. The single character
                 this layer is allowed to synthesise is «/», and only where a validated vinculum
                 licences it.
  6. `validate`  independent deterministic checks. A candidate is restored only when a signal that
                 did not produce it confirms it.
  7. `plugin`    the repairer, registered against Lane A1's repair registry (`adapter` falls back to
                 an identical local protocol while A1's branch is not yet published).

Nothing here overwrites a source observation, and nothing here decides a production threshold.
A region that fails validation stays WITHHELD and keeps its crop, so the printed formula survives
as an image — which is the current behaviour, and the floor this lane must never fall below.
"""
