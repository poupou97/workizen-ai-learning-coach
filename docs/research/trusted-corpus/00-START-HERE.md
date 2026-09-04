# HỌC CÙNG SAM — Trusted-Corpus Feasibility Study (TC-v1) — START HERE

**Question (Founder, 2026-09-04):** can the whole SGK/SGV K-12 corpus (531 books, 62,729 scanned pages, 3,679 lessons) be turned into a Trusted Learning Corpus that SAM can teach children from, with a pipeline that scales?
**Answer:** `01-FOUNDER-REPORT.md` (one page) → verdict **GO WITH SOURCE ARCHITECTURE CHANGE**; the 25 questions are answered one by one in `18-PRODUCT-FEASIBILITY-VERDICT.md`.

## Read in this order

| file | what |
|---|---|
| 01-FOUNDER-REPORT.md | current → tested → best → trust → coverage → false trust → critical errors → cost → verdict; before/after table; three pictures |
| 18-PRODUCT-FEASIBILITY-VERDICT.md | the 25 questions, direct answers |
| 19-RECOMMENDATIONS.md | what to build, what to stop |
| 02-CURRENT-FAILURE-ANALYSIS.md | why today's extraction is unsafe (measured), with the WAL-204 page |
| 03-K12-LAYOUT-CENSUS.md (+ 03A tables) | every page of the corpus measured for layout features |
| 04-HARD-GOLD-SET.md | the 38 pages the study is measured on |
| 05-PARSER-BAKEOFF.md · 06 · 07 · 08 · 09 | bake-off, reading order, block roles, false trust, critical teaching errors |
| 10-CASCADE-ENSEMBLE-OPTIONS.md | agreement gates, guards, the proposed pipeline |
| 11-STRUCTURED-DOCUMENT-MODEL.md | the source model that replaces Markdown as truth |
| 12 · 13 · 14 · 15 · 16 · 17 | reprocess decision, old vs new, SGV, activity patterns, cost, residual risks |
| 20-JIRA-STATUS.md · MANIFEST.md | tickets, PR, file inventory, how to reproduce |

## Evidence folders in the bundle

- `renders/` — the 38 gold pages with a coordinate grid, plus crops for the Founder report (page crops only; no whole PDFs).
- `bakeoff/scores.md` — every metric per page per candidate; `cascade.md` — cascades; `family.md` — trust by layout feature; `roles.md` — role precision/recall; `pilot-result.json` — the 150-page pilot.
- `census/summary.md` — the layout census tables.
- `gold/` — the 38 gold JSON files (block text, order, roles, relations, lesson).
- `scripts/` — every script that produced a number (`tool/corpus/tc_*.py`); reproduction commands in MANIFEST.md.

## Conventions

- **MEASURED** = computed by a script on the corpus or gold set and reproducible from the bundle; **ESTIMATED** = an extrapolation, always labelled.
- Metrics are never collapsed: text accuracy (with / without diacritics) ≠ block detection ≠ reading order ≠ roles ≠ lesson attachment ≠ false trust ≠ critical errors.
- Trust > coverage: a withheld block is a safe failure; a trusted wrong block is the failure we count.
- The 27 Activity Patterns were not implemented (WAL-203/205 preserved). No raw PDFs, no learner data, no secrets in this bundle.
