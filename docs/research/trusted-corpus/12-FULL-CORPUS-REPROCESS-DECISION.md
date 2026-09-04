# 12 — Full-Corpus Reprocess Decision

**Founder condition (order I):** a full re-parse is authorised only after hard gold set → benchmark → measured winner/cascade → bounded pilot → quality gate PASS.

| step | done | result |
|---|---|---|
| hard gold set | yes (04) | 38 pages, 462 learning blocks |
| benchmark | yes (05–09) | Docling+Apple Vision and Marker beat the current pipeline on every fidelity axis; neither meets the trust targets alone |
| measured cascade | yes (10) | best on one Mac: docling ▸ xycut + math guard — coverage 0.77, TLSR 0.67, FTR 0.12 on hard pages; best overall: marker ▸ docling — FTR 0.078 (needs GPU) |
| bounded pilot | yes (13, 16) | 150 non-gold pages / 3 books: 3.33 s/page median; 84.7 % of blocks pass the gate (83.3 % with math guard); XY-cut alone trusted 50 / 150 pages |
| **quality gate PASS** | **no** | false trust 6–12 % on hard pages vs the < 0.1 % gate; critical errors ≠ 0 |

## Decision: **DO NOT re-parse the whole corpus now. Re-parse in bounded, versioned slices under a gate that does not yet exist.**

Reasons (measured):
1. The re-parse would raise coverage from the current 19–25 % trusted blocks (XY-cut) to ≈ 77–85 %, but **12 % of the newly trusted blocks on hard pages would be wrong** with the only cascade that runs on this Mac. That is a coverage win and a trust loss — the opposite of "trust > coverage".
2. The two things that reduce false trust below the shared-mode floor are not built: the **role layer** (07) and the **deterministic guards** beyond the math guard (10 §"Proposed cascade"). Reprocessing before they exist produces a corpus that must be reprocessed again (13 shows the outputs differ materially, so any downstream census/pack would drift twice).
3. Cost is not the blocker: Docling over 62,729 pages ≈ 58 h single-Mac wall time (16), storage ≈ 1.1 GB of JSON. It can run over a weekend. That is exactly why it should wait for the gate — the run is cheap to repeat, the trust debt is not.

## What IS authorised by this study's own evidence (reversible, versioned)

- Keep `poc-out/trusted-corpus/tc-v1/` as the frozen evidence set (gold outputs for 7 candidates, pilot outputs for 150 pages). Nothing old was overwritten or deleted.
- A **slice reprocess** is justified for the Science family already on the WAL-206 path (Khoa học 4–5, KHTN 6–9 ≈ 2,680 pages ≈ 2.5 h): Docling ▸ XY-cut + math guard, written to `poc-out/trusted-corpus/tc-v2/<book>/pNNN.sdm.json`, side by side with `poc-out/layout/`, so WAL-206's funnel can be re-run on both sources and compared. This is the next experiment, not part of this study (it requires the role layer to be at least as good as the XY-cut's question labeller, otherwise the funnel cannot route).

## Requirements if/when the full run happens (all met by the tooling here)

| requirement | how |
|---|---|
| no overwrite / delete of old outputs | new version directory `tc-v2`; `poc-out/layout`, `units-*`, `graph/ocr-body` untouched |
| versioned pipeline + outputs | pipeline id in every block's `provenance` (`docling-2.126+ocrmac`, `layout-xycut-v1`, gate rule ids); output dir carries the version |
| reproducible | `tc_bakeoff_run.py --batch pages.json` per candidate; models pinned (Docling 2.126.0, ocrmac 1.0.1); Apple Vision version = macOS build recorded |
| resumable | the batch runner skips existing raw files; `tc_layout_census.py` is resumable by design |
| deterministic where possible | Docling on CPU and the XY-cut are deterministic; Apple Vision is deterministic per OS build; the VLM is excluded from the production path |
| provenance preserved | book / pdf page / printed page / bbox / order / native label / extraction method / OCR conf on every block |
| old-vs-new comparison | `tc_pilot.py --analyse` pattern: same pages, both sources, block-level agreement + directive-unit counts (13) |
| rollback | delete `tc-v2`; nothing else changes |
| no raw corpus in git | `poc-out/` is gitignored; bundles carry crops only |
| compute / time / storage reported | 16 |
