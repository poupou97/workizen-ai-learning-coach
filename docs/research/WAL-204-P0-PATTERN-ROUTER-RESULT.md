# WAL-204 — P0 Pattern-Router Falsification Experiment: RESULT = FAIL

Founder decision 2026-09-04 (PROCEED WITH PATTERN-DRIVEN SCALE): test the
Fable 5.1 hypothesis on Khoa học/KHTN grades 4-9 — TOC-range attachment →
activity pattern detection → pattern router → existing Surfaces → SAM →
Evidence → device. Success: ≥ 50 new unique lessons device-verified AND
zero regression of the 37 Experiment lessons. Per the decision: FAIL ⇒ stop
pattern mass implementation, analyze, update architecture evidence.

## Report (required format)
| | |
|---|---|
| BEFORE proven lessons | 113 / 3,679 (Khoa học/KHTN 4-9: 32) |
| NEW unique lessons unlocked | **0 device-valid** (7 listed by the pack, all rejected on content quality) |
| AFTER proven lessons | 113 / 3,679 (router gated off; packs rebuilt and re-verified) |
| % of 3,679 | 3.07% (unchanged) |
| Subjects / grades unlocked | none |
| Device validation | Nokia 6.1: routed lesson KHTN 7 Bài 4 listed ("1 bài đọc từ SGK"), Reader opened, READ gate present — **passage column-scrambled, attached "question" is a section heading** (screenshots `~/Desktop/wal-evidence/wal204-*.png`) |
| Regressions | 0 — `khoaExperiments` byte-identical across grades 1-12 vs baseline; 647/647 tests; analyze clean |
| Largest remaining blocker | **Column-aware text extraction** — the generic extractor interleaves two textbook columns line-by-line; 10/13 routed passages came from two-column pages (measured from OCR line x-positions) |

## What was built (kept, gated)
- `tool/ui/pattern_router.py` + hook in `build_lesson_index.py` (env `PATTERN_ROUTER=1`): TOC-range attachment (printed→PDF offset from footer digits, mode ≥3), directive classification, routing into `tvReadings`/`tvWritings` shapes. Never emits experiments.
- `TvQuestion.options` (+ parse, + `_openReading` passes them): options with no key ⇒ `gradable=false` ⇒ Reader records `correct=null`. Structural guarantee that an MCQ without an SGV key is never graded. Test added.
- Taxonomy fix: bare "chọn" is an ordinary verb ("Chọn dụng cụ đo") — SELECT_MCQ now requires an option object or structural A/B/C; registry regenerated (SELECT_MCQ 397 → 287 unique lessons; B_NEAR_TERM 420 → 404).

## Why it failed — three findings, all measured
1. **Wrong pattern mix for this family.** In the 6 books the corpus activities are EXPLAIN_SHORT (35-40 lessons per book) and OBSERVE (20-28). READ_TEXT is rare (0-7 lessons/book); SELECT_MCQ 2-4 units/book and mostly false positives. The strict scope (Reader/Compose/QuizSelect only) therefore had ~7 candidates, not ~100. The Fable census's per-family "near-term" count was over-stated because its primary-label priority put READ/MCQ above EXPLAIN/OBSERVE and because of the "chọn" false positive.
2. **Generic-extractor text is not display-grade on multi-column pages.** The KHTN 7 passage read on device: "Trong số 118 nguyên tố đã biết có 7 nguyên tố là Các nguyên tử kim loại có nguyên tố khí hiếm…" — two columns interleaved. Same blocker that stopped Ngữ văn (sidebar/column content) — now shown to apply to Science too. This invalidates *any* routing that displays extractor passages (READ_TEXT, and the context passage of the EXPLAIN→Reader diagnostic) until column-aware extraction exists.
3. **Neighbour-unit "question" selection is unreliable.** The router took the next directive-labeled unit as the question; on device it was a section heading. Question/prompt selection needs the *directive unit itself* to be the prompt, never a neighbour.

## What still holds
- Plumbing: TOC-range attachment attaches (offsets derivable for all 6 books; units land in lesson ranges); pattern routing reaches the shipped Surface; the evidence gate and fail-closed grading are intact. The failure is content fidelity, not architecture.
- Diagnostic (not wired): EXPLAIN/COMPARE/CLASSIFY/text-OBSERVE → Reader open mode would add **86** lessons in these 6 books — but every one of those needs a *context passage* from the same extractor, so it inherits blocker #2. Single-directive prompts (the question sentence itself) are single-line and mostly survive columns; passages do not.

## Architecture evidence update (cumulative)
| Relation | Status |
|---|---|
| TOC page range → lesson attachment | PROVEN (mechanics); content fidelity NOT proven |
| Generic extractor unit text → display-grade passage (multi-column page) | **FALSIFIED** (Science, this experiment; Ngữ văn, earlier) |
| Directive classifier → activity pattern | PARTIAL (≈85% precision; "chọn" fixed; heading-as-question failure) |
| Pattern → existing Surface routing | PROVEN (mechanics), 0 lessons validated on content |
| "525 near-term via existing Surfaces" (Fable census) | **PARTIALLY FALSIFIED** — over-stated for Science; per-family counts must be re-measured with the fixed taxonomy before use |
| Options without SGV key ⇒ never graded | PROVEN (type-level, tested) |

## Recommendation (stopping here per the decision)
The bottleneck is now precisely named and it is one capability, not many: **column-aware text extraction** (line clustering by x-position into columns, reading order per column, then unit segmentation). It is the prerequisite for READ_TEXT routing, for the EXPLAIN/OBSERVE Surface's context passage (+86 measured in this family alone), and it was the Ngữ văn blocker. Proposed next experiment, same success criteria: build column-aware extraction as a corpus tool, re-run this exact router on the same 6 books with `PATTERN_ROUTER=1`, and re-walk the device. Until then, pattern-driven scaling stays un-validated and the router stays off.
