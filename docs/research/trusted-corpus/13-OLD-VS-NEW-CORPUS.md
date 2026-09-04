# 13 — Old vs New Corpus (150-page pilot + 38-page gold)

**Old** = what the product reads today: Apple-Vision lines → WAL-204 generic units (`units-k12`) and, on the WAL-206 branch, XY-cut blocks with a page-level trust gate (`poc-out/layout`, `units-layout`).
**New** = Docling layout + the same Apple-Vision text, verified by the XY-cut (agreement gate) + math guard, in the SDM (11).
Pilot pages: KHTN 7, Toán 5 tập một, Ngữ văn 9 tập một, PDF pages 10–59 each (150 pages, none in the gold set). Script: `tool/corpus/tc_pilot.py --analyse`; result: `poc-out/trusted-corpus/tc-v1/pilot/pilot-result.json`.

## 1. What each source delivers on the same 150 pages (MEASURED)

| | old: XY-cut (WAL-206) | new: Docling ▸ XY-cut gate (+ math guard) |
|---|---|---|
| pages with a trusted page-level verdict | 50 / 150 (33 %) — KHTN 7: 20, Toán 5: **3**, Ngữ văn 9: 27 | n/a — trust is per block |
| blocks emitted (text ≥ 12 chars) | 3,472 (line-level segmentation) | 1,889 (paragraph-level) |
| blocks trusted | 863 (24.9 %) | 1,600 (84.7 %); 1,573 (83.3 %) with math guard |
| per book trusted-block share | — | KHTN 7 0.893 · Toán 5 0.769 · Ngữ văn 9 0.849 |
| gate reasons | marginal cuts, table-like pages, > 5 % overlap | text disagreement 362, order disagreement 282 (of 3,064 checks), math guard 27 |
| directive-bearing units available for routing (question-like blocks) | **49** | **199** |

Reading: the XY-cut's page-level gate is the reason WAL-206 recovered only +4 lessons in the exact scope — on Toán 5 it trusts **3 pages in 50**. Block-level gating with an independent layout model keeps ~84 % of blocks on the same pages. **But the gold set says ~12 % of those trusted blocks are wrong on hard pages** (10); on these pilot pages the true rate is unknown because they are not annotated — it lies between the plain-prose rate (0 %) and the hard-page rate (12 %). ESTIMATED: 5–10 %.

## 2. What changes in the text itself (gold set, same OCR)

| | old naive | old XY-cut | new Docling |
|---|---|---|---|
| text accuracy (diacritics kept) | 0.902 | 0.907 | 0.954 |
| fidelity of contiguous passages | 0.718 | 0.847 | 0.975 |
| cross-column splices | 24 | 17 | 6 |
| meaning-changing inversions | 49 | 34 | 21 |
| provenance per block | page + bbox (line) | page + bbox + region path | page + bbox + order + native label |
| roles | none | heading/body/question/caption/sidebar/footnote (P 0.69 on questions) | heading/body/caption/table/footnote (no question) |
| list enumerators | kept | kept | **dropped (65 events)** — must be restored from OCR lines |

## 3. What the product would notice

- **Passages** (READ_TEXT context): the WAL-204 column-interleave class disappears on the gold pages for Docling (6 splices left, all on box-dense pages) — the Reader would show readable paragraphs on pages the XY-cut currently withholds.
- **Questions**: nothing gains a question role automatically; the new source has 4× more *candidate* directive units but every one of them needs the role layer (07) before it can be a prompt. The WAL-206 router would have to consume Docling blocks + the XY-cut's role hints — not built.
- **Math**: unchanged — fractions and operators are flattened by both; the math guard withholds them (27 blocks on the pilot pages; on Toán 5 the withheld share is highest).
- **Lesson attachment**: unchanged unless header-based attachment is built (10 / 38 gold pages wrong today).

## 4. Regression risk

The old outputs stay in place (`poc-out/layout`, `units-*`, packs). The new outputs are in `poc-out/trusted-corpus/tc-v1/bakeoff/raw/docling-ocrmac/` (188 pages) and can be deleted without effect. No pack, index or Dart consumer was changed by this study.
