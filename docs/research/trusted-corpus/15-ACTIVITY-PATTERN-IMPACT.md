# 15 — Activity-Pattern Impact (WAL-203 registry preserved, not implemented)

**Rule kept:** the 27 Activity Patterns were not implemented (Founder order L). This document only measures how the *inputs* to the pattern census would move if the source layer changed.

## Measured on the 150-page pilot (13)

| | old source (XY-cut, page-trusted) | new source (Docling ▸ XY-cut + math guard, block-trusted) |
|---|---|---|
| directive-bearing units (blocks that start with a directive verb from the WAL-206 lexicon, e.g. Em hãy / Nêu / Quan sát / Tính / Viết…) | **49** | **199** |
| KHTN 7 (pages 10–59) | 24 | 88 |
| Toán 5 (pages 10–59) | 2 | 43 |
| Ngữ văn 9 (pages 10–59) | 23 | 68 |

A **4× change in the raw count of directive units on identical pages** means the current registry numbers (EXPLAIN_SHORT / OBSERVE / SELECT_MCQ …, `poc-out/k12-census-exports/fable-taxonomy.json`) are a property of the old extractor's coverage, not of the books. They must be recomputed after any source change — with the caveat that the new count includes directives inside *worked examples, procedures and objectives* that the role layer (07) must first remove: on the gold set, 23 of the XY-cut's 100 "questions" were non-questions, and the layout parsers cannot tell at all.

## What would change in the registry (ESTIMATED direction, not numbers)

- **READ_TEXT** gains: clean passages exist on pages the XY-cut withheld (Toán 5 3/50 → 77 % blocks). The WAL-206 variant (+84 lessons via EXPLAIN → Reader) was bottlenecked by passage quality; that bottleneck moves.
- **EXPLAIN_SHORT / OBSERVE** grow proportionally with directive units (they dominate Science: 166 / 190 lessons in WAL-206) — the Surface gap WAL-206 named does not change.
- **SELECT_MCQ** becomes *detectable* (options A–D come out as separate, correctly ordered blocks with Docling/Marker; the XY-cut produced A B D C on the WAL-204 page) but remains **ungradable** without SGV keys (14) — the WAL-204 rule "options without a key are never graded" stays.
- **COMPUTE_SOLVE / formula patterns**: every candidate flattens notation; the math guard withholds them. These patterns cannot be sourced as text from this corpus with the tested stacks — they need a formula-capable path or image-first delivery.
- **OBSERVE / MAP_SPATIAL / DATA_CHART / DIAGRAM_COMPLETE**: figure-dependent by construction; the SDM's `refers_figure` relation makes them *identifiable* (so they can be routed to a multimodal Surface or withheld), which the current units cannot.

## Instruction for the next census run

Re-run `tool/corpus/fable_activity_taxonomy.py` only on a role-labelled SDM (questions with precision ≥ 0.95 measured on gold), never on raw Docling blocks; report per-family counts with the old counts side by side; treat both as measurements of the pipeline, not of the curriculum.
