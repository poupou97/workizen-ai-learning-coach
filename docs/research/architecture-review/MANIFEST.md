# MANIFEST — TC-v2 Science Slice + Founder Architecture Review

Generated 2026-09-05 on one Apple M1 (16 GB, macOS 26.5 build 25F71). Model: Claude (Fable 5.1 session). Jira WAL-209. PRs: repo #58, knowledge-base #1. Bundle: `~/Desktop/HOC-CUNG-SAM-ARCHITECTURE-REVIEW-<YYYYMMDD-HHMM>.zip` and `…-LATEST.zip`.

## The requested 00–09 files → the Founder's A–J (update item 4)

| originally requested | delivered as | letter |
|---|---|---|
| 00-START-HERE.md | `00-START-HERE.md` | map |
| 01-FOUNDER-SUMMARY.md | `01-FOUNDER-SUMMARY.md` | H + I summary |
| 02-SOURCE-ARCHITECTURE.md | `A-SOURCE-ARCHITECTURE.md` + `B-TRUSTED-STRUCTURED-LESSON.md` | A, B |
| 03-LEARNING-VIEWS.md | `C-HYBRID-SMART-BOOK.md` + `D-VISUAL-LEARNING.md` + `E-SAM-TUTOR.md` | C, D, E |
| 04-RUNTIME-SEMANTICS.md | `F-LEARNINGCONTEXT-VS-LEARNINGVIEW.md` (LearningSession kept OPEN) + `G-EVIDENCE-FLOW.md` | F, G |
| 05-SCIENCE-SLICE-RESULTS.md | `I-MEASURED-TRUST-AND-COVERAGE.md` + `tables/` | I |
| 06-ROLE-LAYER-AND-SHORT-ANSWER-GATE.md | `ROLE-LAYER-AND-SHORT-ANSWER-GATE.md` (six roles, per role, with numbers) | I (extended) |
| 07-DECISIONS-REQUESTED.md | `DECISIONS-REQUESTED.md` | H, J (extended) |
| 08-RISKS.md | `RISKS.md` | J (extended) |
| 09-JIRA-STATUS.md | `JIRA-STATUS.md` | — |
| — | `H-NEXT-ACTION.md`, `J-LEGAL-PRODUCT-GATES.md`, `MANIFEST.md` | H, J |

## Bundle contents

| path | what | source of truth |
|---|---|---|
| `*.md` (this package) | the review | `docs/research/architecture-review/` in the repo (PR #58) |
| `tables/gold-scores.md`, `tables/slice-report.md`, `tables/sgv-report.md` | every measured table (+ `.json` twins in `metrics/`) | `tool/corpus/tc2_score.py`, `tc2_slice_report.py`, `tc2_sgv_report.py` |
| `metrics/*.json` | machine-readable metrics incl. per-page rows and false-question examples | same scripts |
| `manifest.json` | pipeline id `tc2-p1`, git SHA, Docling/ocrmac/macOS versions, converter options, per-page status, timing, storage | `tool/corpus/tc2_run.py --manifest` |
| `gold/*.json` | the 16 new held-out gold pages (short transcriptions, same nature as TC-v1) | `tool/corpus/tc_gold/` |
| `renders/*-grid.png` | the 16 held-out pages with a coordinate grid (what the gold was read from) | `tool/corpus/tc_render.py --grid` |
| `renders/evidence/*.png` | 6 page **crops** illustrating measured findings (banner+objective, side-by-side boxes, SGV answer section, experiment box, activity-vs-question icons, the WAL-204 control region) | `tc_render.py --crop` |
| `attach/*.json` | per-book attachment + TOC repair for the 6 SGK + 6 SGV books | `tool/corpus/tc2_attach.py` |
| `lessons-sample/` | 6 Trusted Structured Lessons (one per book) as examples of the TSL shape incl. both Hybrid Smart Book projections | `tool/corpus/tc2_tsl.py` |
| `scripts/*.py` | copies of `tool/corpus/tc2_*.py` | repo |
| `logs/` | slice / SGV / SDM run logs with per-page seconds | `poc-out/trusted-corpus/tc-v2/tc2-p1/logs/` |

Not in the bundle (derived corpus data, stays under gitignored `poc-out/trusted-corpus/tc-v2/tc2-p1/`): raw candidate outputs (`bakeoff/raw/`, 42 MB), all SDM pages (`sdm/`, 31 MB), all 238 lesson documents (`lessons/`, 16 MB). Never anywhere: source PDFs, single-page PDFs (cut to a temp dir and deleted), learner data, secrets.

## Reproduce (bake-off venv from TC-v1; all paths absolute inside the scripts; run from the repo checkout)

```
# 0. tooling: .venv-bakeoff (Docling 2.126.0, ocrmac 1.0.1, pymupdf, rapidfuzz) — see docs/research/trusted-corpus/MANIFEST.md
export DOCLING_ARTIFACTS_PATH=<docling model cache>
P=poc-out/trusted-corpus/tc-v2/tc2-p1
# 1. page lists + fast candidates (seconds)
python3 tool/corpus/tc2_run.py --pipeline tc2-p1 --make-pages slice
python3 tool/corpus/tc2_run.py --pipeline tc2-p1 --pages $P/pages-slice.json --fast
# 2. Docling primary, 2 workers, resumable (≈ 18 min for 1,049 pages)
.venv-bakeoff/bin/python tool/corpus/tc2_run.py --pipeline tc2-p1 --pages $P/pages-slice.json --workers 2
.venv-bakeoff/bin/python tool/corpus/tc2_run.py --pipeline tc2-p1 --pages $P/pages-slice.json --pages $P/pages-sgv.json --manifest
# 3. SDM-v2 for the slice and for the gold pages (≈ 3 min)
.venv-bakeoff/bin/python tool/corpus/tc2_sdm.py --pipeline tc2-p1 --pages $P/pages-slice.json --pages $P/pages-sgv.json
.venv-bakeoff/bin/python tool/corpus/tc2_sdm.py --pipeline tc2-p1 --gold
# 4. attachment + TOC repair (OCR lines only; seconds)
python3 tool/corpus/tc2_attach.py --pipeline tc2-p1 --gold-books <six SGK> <six SGV>
# 5. gold scoring, slice report (builds the TSLs), SGV report
.venv-bakeoff/bin/python tool/corpus/tc2_score.py --pipeline tc2-p1 --json $P/metrics/gold-scores.json --md $P/metrics/gold-scores.md
.venv-bakeoff/bin/python tool/corpus/tc2_slice_report.py --pipeline tc2-p1 --json $P/metrics/slice-report.json --md $P/metrics/slice-report.md
.venv-bakeoff/bin/python tool/corpus/tc2_sgv_report.py --pipeline tc2-p1 --json $P/metrics/sgv-report.json --md $P/metrics/sgv-report.md
```

## Integrity notes

- Nothing under `poc-out/` that existed before this slice (`tc-v1/`, `layout/`, `units-*`, packs, `p0-experiment/`) was modified or deleted; all new outputs live under `poc-out/trusted-corpus/tc-v2/tc2-p1/`.
- Docling output on the 7 gold pages shared with TC-v1 is byte-identical (labels + text) — determinism check in A.1.
- Gold convention change after the first held-out scoring (captions / floating objective boxes as flex groups) is recorded in each affected file's `gold_revision`; no threshold was tuned on held-out pages. First-pass held-out numbers are kept in I.2.
- Guards and lexicon were calibrated on the 38 TC-v1 pages (dev) only; the three lexicon bug fixes after the first held-out run are listed in I.2.
- No LLM/VLM output is source truth anywhere in the pipeline; the gold was read by a VLM from page renders (the TC-v1 method), never from extractor output.
- Cleanup: no background process of this round (Docling workers, SDM build) is left running; `pgrep -fl "docling|tc_|ocrmac|python3 tool/corpus"` was verified empty before the final report.
