"""Workstream B · RECOGNITION — read what the page prints, not what the OCR left behind.

Round 5 established that recognition, not reasoning, is the bottleneck: `3x10^8 -> 3x10°`,
`II -> I1` and 274 of 336 unrepairable fractions are all born in Apple Vision's single
whole-page pass, and no downstream rule can reach them because the character was never read.

This package holds two things and nothing else:

* `census`  — a FAILURE CENSUS. Forms before rules: every failure class gets a count, a
              denominator and named real examples, measured on the corpus.
* `boxes` / `consensus` / `score` — the targeted RE-CROP experiment: ask Vision about one
              printed region at a time, treat every answer as an untrusted observation, and
              accept a reading only when independent observations agree.

Doctrine carried in from round 5, verbatim, because it applies to a recogniser hardest:

    ink-accounting proves completeness, provenance proves honesty, neither proves identity.

A recogniser that raises recall and does not report its false-recognition rate looks perfect
by recognising nothing. Every metric in `score` is reported beside its opposite.

Nothing here imports numpy or PyMuPDF; the raster work lives behind `vision.py`, which shells
out to `tool/ocr/ocr_crop.swift` and is never imported by a test.
"""
