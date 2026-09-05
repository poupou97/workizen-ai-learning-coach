# Metric denominators — the D5 convention

Founder decision **D5** (WAL-210, 2026-09-05): keep **3,679** as the historical
canonical baseline; **every metric carries its denominator definition, the
census/version it was counted against, and the subset it applies to; ranged
denominators stay separate** and are never collapsed into the canonical one.
This file is the one place that defines the denominators; reports cite it
instead of re-explaining them. Measured facts here come from the pre-autonomy
audit (`docs/research/pre-autonomy-audit/02-DATA-QUALITY.md`, PR #59) and the
TC-v1/TC-v2 studies; nothing here decides a repair — repairs are PROPOSED.

## The template

Every number that is a rate or a coverage claim is written as

```
N / <denominator> <definition> · census <id/date> · subset <…>
```

Examples (all MEASURED 2026-09-05):

- `111 / 3,679 canonical SGK lessons · census curriculum-structure.json schema 1 (301 SGK docs), reconciled 2026-09-04 · subset: default packs g1–g12 built by build_lesson_index.py@320ae88` — learnable lessons after the WAL-210 attachment/identity gates (was 113 before them).
- `3,381 / 3,679 canonical · same census · subset: lessons with a TOC pageStart` — source-addressable (ranged) lessons; a pipeline number, not a coverage number.
- `238 / 238 repaired-ranged, six Science books · TC-v2 tc2-p1 header repair 2026-09-04 · subset: Khoa học 4–5, KHTN 6–9` — lessons with a Trusted Structured Lesson; **never** written as 238 / 3,679.
- `0.100 FTR = 19 / 190 trusted gold blocks · TC-v2 science gold, 23 pages · subset: six Science books + their SGV pages` — false-trust rate; the denominator is trusted *blocks*, not lessons.

A number without all three parts is not reportable. A number whose subset is a
slice must not be divided by a corpus-wide denominator.

## The denominators

| id | value | definition | census / version | use it for | do NOT use it for |
|---|---|---|---|---|---|
| **canonical** (historical baseline) | **3,679** | SGK lessons with a lesson number in `curriculum-structure.json` (Grade 1–12, 301 SGK documents of 531) | schema 1; reconciled 2026-09-04 (`K12-CONVERGENCE-CENSUS.md`), re-derived 2026-09-05 by `pre-autonomy-audit/scripts/a_layers.py` — no drift | product coverage claims (browsable, learnable, SAM-supportable, device-validated) | anything measured only on a slice; trust rates |
| **ranged** | **3,381** | canonical lessons that also have a TOC `pageStart` | same census | source-pipeline claims (source-addressable, sourceable-555/559, layout-gate rates) | coverage claims — a ranged lesson is not a learnable one |
| **repaired-ranged, six Science books** | **238** | lessons whose boundary TC-v2 recovered from printed headers ∪ TOC in Khoa học 4–5 / KHTN 6–9 (six-book canonical 207; old ranged 194) | TC-v2 `tc2-p1`, 2026-09-04, header detection `tc2_attach.py` | TSL / block-trust / role-layer metrics on that slice | any corpus-wide rate; the 238 are PARTIAL lessons, 2 FULL |
| gold blocks | 462 (TC-v1, 38 pages) · 643 (TC-v2, 54 pages) · 190 (science, 23 pages) | learning blocks in the hand-written gold pages | `tool/corpus/tc_gold/` (38 in `main`; 54 on `research/tc-v2-science-slice`) | false-trust, TLSR, role P/R | certifying any rate below ≈ 1 % (54 pages cannot) |
| baseline learnable | 113 (historical) → 111 (after G2/G3) | lessons with ≥ 1 non-router activity in the default packs | `poc-out/p0-experiment/baseline-learnable.json` (2026-09-04) → PR-1 regeneration report (2026-09-05) | regression oracle for the pack builder | a trust claim (measures wiring, not truth) |
| pages | per book (e.g. Toán 5 tập một 142, KHTN 6 198, TV5 tập hai 162) | OCR page files under `poc-out/graph/ocr-body/<book>/` | corpus 2026-09 (62,729 page files, 531 books) | page-gate rates | lesson counts |

Proposed, **not adopted** (need a Founder decision — `architecture-review/DECISIONS-REQUESTED.md` #5, TC-19 #9): canonical ≥ 3,725 and ranged ≈ 3,425 after header-based TOC repair corpus-wide. Until adopted, reports keep 3,679 / 3,381 and may show the repaired figure beside them, labelled PROPOSED.

## Known denominator defects (measured; repairs are PROPOSED, not applied)

- Six Science books: TOC ranged 194 of 207 canonical; headers find 238 boundaries (KHTN 7 TOC 18 → 37 lessons, KHTN 8 22 → 44) — the canonical list itself is short for KHTN 7/8.
- Tiếng Việt 5: every TV5 reading sits exactly 2 printed pages before its lesson's TOC `pageStart` on 18/29 tập hai lessons (headers and units agree with each other, not with the TOC) — a systematic `pageStart` offset; measured in the WAL-210 PR-1 regeneration report.
- Khoa học 4/5, LS&ĐL 5: canonical lessons without `pageStart` (4 / 8 / 18 of them) — handled at attachment time by `tool/ui/lesson_attach.py` (header-repaired starts, fail closed), not by editing the census.
- Ngữ văn 6–12: 5–8 canonical lessons per grade for 260–312 pages — the TOC parse missed the book; those grades' "/3,679" cells are known under-counts.

## D4 — what a report may quote

Founder decision **D4**: verbatim SGK text and page crops are **INTERNAL /
RESEARCH ONLY**. A report in this repo identifies content by `book / pdf page /
printed page / lesson / block id` and may quote a short activity title; any
verbatim passage, question text or rendered crop lives only in gitignored
`poc-out/` (e.g. `poc-out/b-lane/ft-audit/`) and is never committed. No
document in this repo may assume a public-release right to that material.
