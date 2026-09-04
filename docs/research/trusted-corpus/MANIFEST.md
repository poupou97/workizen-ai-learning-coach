# MANIFEST — TC-v1 Trusted-Corpus Feasibility Study

Generated 2026-09-05 on one Apple M1 (16 GB). Model: Claude (Fable 5.1 session). Jira WAL-208. Bundle: `~/Desktop/HOC-CUNG-SAM-TRUSTED-CORPUS-FEASIBILITY-<YYYYMMDD-HHMM>.zip` and `…-LATEST.zip`.

## Bundle contents

| path | what | source of truth |
|---|---|---|
| `00-START-HERE.md` … `20-JIRA-STATUS.md`, `MANIFEST.md`, `03A-CENSUS-TABLES.md` | the report set | `docs/research/trusted-corpus/` in the repo (PR) |
| `bakeoff/scores.md`, `scores.json` | every metric per page per candidate (final regeneration at bundle time) | `tool/corpus/tc_score.py` |
| `bakeoff/cascade.md`, `cascade.json` | cascade simulation | `tool/corpus/tc_cascade.py` |
| `bakeoff/family.md`, `family.json` | trust by layout feature | `tool/corpus/tc_family_breakdown.py` |
| `bakeoff/roles.md` | role precision/recall | scratch `roles_and_example.py` (logic in `tc_score.py`) |
| `pilot/pilot-result.json`, `pilot/pages.json` | 150-page pilot | `tool/corpus/tc_pilot.py` |
| `census/summary.md`, `summary.json` | layout census (62,729 pages) | `tool/corpus/tc_layout_census.py`, `tc_census_augment.py`, `tc_census_report.py` |
| `gold/*.json`, `gold/pages.json` | the 38 gold pages | `tool/corpus/tc_gold/`, `tc_gold_pages.py` |
| `renders/*.png` | gold-page renders with grid + Founder crops (page crops only) | `tool/corpus/tc_render.py` |
| `scripts/*.py` | copies of every `tool/corpus/tc_*.py` | repo |
| `logs/*.log` | batch logs with per-page seconds | `poc-out/trusted-corpus/tc-v1/logs/` |

Not in the bundle (derivative corpus data, stays under gitignored `poc-out/trusted-corpus/tc-v1/`): raw candidate outputs (`bakeoff/raw/`, 7 MB), single-page PDFs (`pages/`, 50 MB), `census/pages.jsonl` (32 MB). Never anywhere: source PDFs, learner data, secrets.

## Reproduce (from the repo root of the main checkout; all paths absolute inside the scripts)

```
# 0. one-off tooling (isolated, gitignored)
uv venv --python 3.11 .venv-bakeoff && uv pip install --python .venv-bakeoff/bin/python pymupdf pymupdf4llm ocrmac docling rapidfuzz
uv venv --python 3.11 .venv-bakeoff-marker && uv pip install --python .venv-bakeoff-marker/bin/python marker-pdf pymupdf   # + brew install llama.cpp
uv venv --python 3.11 .venv-bakeoff-mineru && uv pip install --python .venv-bakeoff-mineru/bin/python "mineru[core]" pymupdf
uv venv --python 3.11 .venv-bakeoff-mlx && uv pip install --python .venv-bakeoff-mlx/bin/python mlx-vlm jinja2 pymupdf
# 1. census (3 min)
python3 tool/corpus/tc_layout_census.py --ver tc-v1 --workers 6 && python3 tool/corpus/tc_census_augment.py && python3 tool/corpus/tc_census_report.py
# 2. gold renders + candidate proposals
python3 tool/corpus/tc_gold_select.py --per 2 ; python3 tool/corpus/tc_gold_pages.py > poc-out/trusted-corpus/tc-v1/gold/pages.json
# 3. bake-off (P = gold/pages.json)
python3 tool/corpus/tc_bakeoff_run.py current-naive --batch $P ; python3 tool/corpus/tc_bakeoff_run.py current-xycut --batch $P
DOCLING_ARTIFACTS_PATH=<cache> .venv-bakeoff/bin/python tool/corpus/tc_bakeoff_run.py docling-ocrmac --batch $P
.venv-bakeoff-mineru/bin/python tool/corpus/tc_bakeoff_run.py mineru --batch $P
.venv-bakeoff-marker/bin/python tool/corpus/tc_bakeoff_run.py marker --batch $P
.venv-bakeoff-mlx/bin/python tool/corpus/tc_bakeoff_run.py vlm-mlx --batch $P
# 4. score
.venv-bakeoff/bin/python tool/corpus/tc_score.py --json …/bakeoff/scores.json --md …/bakeoff/scores.md
.venv-bakeoff/bin/python tool/corpus/tc_cascade.py --json …/cascade.json --md …/cascade.md
.venv-bakeoff/bin/python tool/corpus/tc_family_breakdown.py --md …/family.md
# 5. pilot
python3 tool/corpus/tc_pilot.py --make ; (run current-xycut, current-naive, docling-ocrmac with --batch pilot/pages.json) ; .venv-bakeoff/bin/python tool/corpus/tc_pilot.py --analyse
```

## Integrity notes

- Nothing under `poc-out/` that existed before this study was modified or deleted; all new outputs live under `poc-out/trusted-corpus/tc-v1/`.
- Gold JSON contains short transcriptions of textbook text needed for measurement (same nature as the existing `layout_gold.py` anchors).
- Scorer changes made during calibration are listed in 08 §3 / 17 #9; the final scorer is the one in the PR.
