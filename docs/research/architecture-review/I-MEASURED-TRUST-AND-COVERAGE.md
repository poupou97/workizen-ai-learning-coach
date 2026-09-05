# I — Measured trust and coverage, with denominators (never collapsed)

Everything here is MEASURED unless marked ESTIMATED. Sources: `poc-out/trusted-corpus/tc-v2/tc2-p1/metrics/{gold-scores,slice-report,sgv-report}.md` (+ `.json`), `manifest.json`. Copies of the three tables are in `tables/` next to this file.

## I.1 Denominators — two numbers, two purposes, both kept (Founder update item 3)

| denominator | value | purpose | source |
|---|---|---|---|
| **canonical K-12 SGK lessons** | **3,679** | curriculum / product coverage statements | `curriculum-structure.json`, sum of SGK `lessons[]` (301 SGK docs) |
| **ranged SGK lessons** | **3,381** | source-pipeline measurements that need a page range | same file, lessons with `pageStart` |

Six-book view (Khoa học 4, 5; KHTN 6, 7, 8, 9), old → new:

| book | TOC status | canonical `lessonCount` | ranged (old TOC) | header-detected | **repaired ranged (new)** | lessons beyond canonical (max Bài) | candidate new canonical count |
|---|---|---|---|---|---|---|---|
| Khoa học 4 | PARTIAL | 31 | 27 | 31 | **31** | 0 | 31 (unchanged) |
| Khoa học 5 | PARTIAL | 30 | 22 | 30 | **30** | 0 | 30 (unchanged) |
| KHTN 6 | OK | 55 | 55 | 53 | **55** | 0 | 55 |
| KHTN 7 | PARTIAL | 18 | 17 | 33 | **37** | 20 (Bài 39) | **≥ 39** — the printed book continues past the TOC's Bài 18 |
| KHTN 8 | "OK" (but truncated) | 22 | 22 | 42 | **44** | 22 (Bài 47) | **≥ 47** |
| KHTN 9 | OK | 51 | 51 | 49 | **51** | 0 | 51 |
| **six books** | | **207** | **194** (WAL-206's funnel denominator) | 238 | **248 ∪ → 238 lesson documents** | 42 | **≥ 253** |

Method: `tc2_attach.py` (A.4) — headers from OCR lines, TOC cross-check ±1 printed page, sequence rule; 0–2 rejected headers per book. Consequence for the corpus denominators (not applied, requested): the ranged count 3,381 → 3,381 + (238 − 194) = **3,425** for these six books alone (ESTIMATED for the rest: other PARTIAL books would move too); the canonical 3,679 → **≥ 3,725** if KHTN 7/8's header-detected lessons replace `lessonCount` (a curriculum fact, Founder to confirm — DECISIONS-REQUESTED.md #5). **No number in this package is reported over a denominator it does not belong to.**

## I.2 Trust on gold — the TC-v1 scorer, unchanged, on the SDM-v2 pipeline

| set | pages | learning blocks | trusted (coverage) | TLSR | false-trusted | **FTR** | safe rejected | found | order | meaning inversions | text acc (diacritics) | CER no-tone | fidelity | splices | CTE (all output) | CTE pages |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (TC-v1 38) | 38 | 462 | 323 (0.699) | 0.621 | 36 | **0.112** | 125 | 0.978 | 0.984 | 31 | 0.964 | 0.031 | 0.975 | 8 | 71 | 22 |
| held-out (TC-v2 16) | 16 | 181 | 116 (0.641) | 0.564 | 14 | **0.121** | 63 | 0.982 | 0.986 | 13 | 0.981 | 0.017 | 0.979 | 2 | 18 | 6 |
| science (23) | 23 | 269 | 190 (0.706) | 0.636 | 19 | **0.100** | 77 | 0.985 | 0.987 | 15 | 0.982 | 0.015 | 0.987 | 3 | 27 | 10 |
| all (54) | 54 | 643 | 439 (0.683) | 0.605 | 50 | 0.114 | 188 | 0.979 | 0.985 | 44 | 0.969 | 0.027 | 0.976 | 10 | 89 | 28 |
| *TC-v1 docling ▸ xycut + math guard (dev 38)* | 38 | 462 | 354 (0.766) | 0.673 | 43 | 0.121 | 85 | — | 0.987 | — | 0.954 | — | — | 6 | — | — |

- **First-pass held-out numbers, before any change** (recorded for honesty): FTR 0.261, TLSR 0.470, 24 of 30 false trusts were order-only. Cause: my held-out gold had not applied TC-v1's flex-group convention to captions/floating objective boxes; fix = gold convention (`gold_revision` field in each file), plus three lexicon bugs ("·" bullet, "Em có biêt?" slip, a stem rule that fired on Toán worked examples). No threshold was tuned on the held-out pages.
- **Critical-teaching-error events on all output (science 23 pages): 27** — order_changes_meaning 15, corrupted_data 4, cross_column_contamination 3, nonquestion_as_question 2, enumerator_dropped 0 (was 65 in TC-v1 for Docling — the enumerator fix), lesson_attach_wrong (TOC) 8 → (header) 1.
- **Reading order** 0.987 science; **text accuracy** 0.982 (CER without tone marks 0.015); **caption association** 0.75 (science) / 0.95 (dev); **table role** 1.00/1.00 on the 7 science gold tables; **formula role** 0 (Docling never labels formulas; math guard withholds them).

## I.3 Role Layer — the six roles (science gold, 23 pages; full tables in ROLE-LAYER-AND-SHORT-ANSWER-GATE.md)

QUESTION 0.889 / 0.870 (n=46; trusted-question precision **0.970**, n=33) · ANSWER 0.800 / 0.400 (10) · ACTIVITY **0.000 / 0.000** (10) · INSTRUCTION 0.500 / 0.500 (6) · OBJECTIVE 0.696 / 0.941 (17) · SIDEBAR 0.964 / 0.818 (33). Dev/held-out: QUESTION 0.893 / 0.750 and 0.833 / 0.938. **Target QUESTION ≥ 0.95: not met.**

## I.4 The slice (1,049 pages, MEASURED)

| | value |
|---|---|
| pages · learning blocks | 1,049 · 14,451 |
| TRUSTED · WITHHELD · CONFLICT | **12,348 (0.854)** · 1,868 · 235 |
| per-book trusted rate | Khoa học 4 0.830 · Khoa học 5 0.850 · KHTN 6 0.825 · KHTN 7 0.853 · KHTN 8 0.877 · KHTN 9 0.873 |
| withheld by reason | agree_text 865 · figure_dependent 638 · agree_order 229 · page_feature:diagram 199 · page_feature:color_heavy 111 · box_boundary 95 · math_guard 42 · answer_leak 30 · low_ocr_conf 20 · role_conflict 7 |
| trusted blocks by role | body 4,076 · heading 2,274 · question 1,669 · caption 1,241 · sidebar 1,086 · objective 869 · stage_label 609 · instruction 367 · footnote 75 · activity 53 · table 25 · option 4 |
| enumerators restored | 5,110 blocks |
| Trusted Structured Lessons | 238 (2 FULL, 236 PARTIAL, 0 NONE) — 11,971 native blocks, 2,032 withheld regions |
| true false-trust on these pages | not annotated; between ≈ 0 (prose) and 0.10–0.12 (hard pages); ESTIMATED 4–8 % |

## I.5 SGV sample (75 pages, MEASURED on the sampled pages only)

| | value |
|---|---|
| blocks withheld as answer_leak / teacher_text | 56 / 693 |
| blocks that would have reached a learner without the SGV lexicon (agreement gate alone) | 711 |
| SGV blocks TRUSTED for a learner surface | 0 (473 trusted blocks are headings/captions only) |
| answer-key blocks serialised with text into any TSL | 0 |
| pairing candidates (SGV answer block with an enumerator under lesson L) | 26 → **PAIRABLE 2 · AMBIGUOUS 4 · UNPAIRED 20** (key = lesson + printed enumerator against TRUSTED SGK question/activity blocks; fails closed) |
| SGV lesson structure (canonical / TOC-ranged / header-detected / repaired) | Khoa học 4 31/24/23/30 · Khoa học 5 30/23/24/30 · KHTN 6 55/36/26/45 · KHTN 7 42/28/26/34 · KHTN 8 47/28/29/38 · KHTN 9 51/18/27/31 |

Reading: the answer-leak / teacher-text guards close a leak of 711 blocks on 75 pages; pairing by enumerator alone keys 2 of 26 — SGV pairing needs the section context and table cells (TC-14), not just enumerators.

## I.6 Old vs new funnel (MEASUREMENT — explicitly not the success criterion)

| WAL-206 funnel step (six books) | OLD units-layout, exact | OLD variant (+EXPLAIN) | **NEW tc-v2 TSL** |
|---|---|---|---|
| TOC lessons | 194 | 194 | **238** (header ∪ TOC repair) |
| recovered (≥ 1 trusted passage/question) | 185 | 185 | 237 |
| with any recognised activity pattern | 169 | 169 | 211 |
| with a pattern in the exact scope (READ/MCQ/WRITE) | 19 | 19 | 29 |
| EXPLAIN/OBSERVE only | — | — | 161 |
| gate-at-source pass, exact scope | 5 (content-valid 5, device-valid 0) | — | **12** |
| gate-at-source pass, variant (+EXPLAIN) | — | 96 (content-valid 96, device-valid 6) | **154** |

Caveats that keep this a measurement: the NEW column counts lessons whose TSL has a TRUSTED question passing the WAL-206 content gate against the nearest preceding trusted body block — no pack was built, nothing was walked on a device, and the QUESTION precision measured on gold (0.83–0.89; 0.97 among trusted questions on science pages) applies to every one of those questions. The old numbers come from `poc-out/p0-experiment/funnel-{exact,variant}.json` unchanged.

## I.7 Compute · time · storage (MEASURED)

| item | value |
|---|---|
| Docling + ocrmac, slice | 1,049 pages · median 1.53 s · p90 2.12 s · 1,731 CPU-s · **≈ 18 min wall** with 2 workers · 0 errors |
| Docling, SGV sample | 75 pages · ≈ 2 min |
| XY-cut + naive candidates | 1,049 pages · 1.9 s total |
| SDM-v2 build (colour masks, agreement, roles, guards) | 1,124 pages · ≈ 3 min |
| attachment, TSL, reports, gold scoring | seconds each |
| storage under `tc-v2/tc2-p1/` | raw candidates 42 MB · SDM 31 MB · lessons 16 MB · attach 1.4 MB · renders 23 MB · sdm-gold 1.8 MB · metrics 0.3 MB ≈ **115 MB**; no page PDFs kept |
| whole-corpus extrapolation (62,729 pages, ESTIMATED from the uncontended rate) | ≈ 27 h single process, ≈ 14 h with 2 workers; ≈ 7 GB with SDM + lessons — **not run, not authorised** |
| cloud / paid spend | none |
