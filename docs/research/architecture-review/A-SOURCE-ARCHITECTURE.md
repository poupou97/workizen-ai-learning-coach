# A — Source Architecture, as validated on the Science Slice (MEASURED)

The Founder's chain — **Source → SDM → block trust → Role Layer → deterministic guards → lesson attachment → Trusted Structured Lesson** — was built as offline tooling (`tool/corpus/tc2_*.py`, bake-off venv only, no project dependency) and run on the six Science SGK books + a 75-page SGV sample. Every stage below says what it does, how it was measured on gold, and what it produced on the slice. Old outputs (`poc-out/layout`, `units-*`, packs, `tc-v1/`) were not touched; everything new is under `poc-out/trusted-corpus/tc-v2/tc2-p1/` (manifest: pipeline id, git SHA, Docling 2.126.0 / ocrmac 1.0.1 / macOS 26.5 build 25F71, converter options, per-page status).

## A.1 Source → SDM (TC-11) — `tc2_run.py`, `tc2_sdm.py`

- **Primary** Docling 2.126 layout model + Apple Vision text (ocrmac, `vi-VT`/`en-US`, accurate, full-page OCR, images_scale 2.0, table structure on) — the same options as TC-v1's bake-off, one converter per worker. **Verifier** WAL-206 XY-cut (`layout_extract.py`) on the existing OCR lines. **Naive** OCR-line order kept for old-vs-new.
- **Determinism (MEASURED):** on the 7 gold pages both runs share, the tc-v2 Docling output is byte-identical to tc-v1's (labels + text) — 7/7.
- **Compute (MEASURED):** 1,049 slice pages, median 1.53 s/page, p90 2.12 s, 1,731 CPU-s of Docling; 2 workers → **≈ 18 min wall-clock** (18:17–18:35 UTC), 0 errors. SGV sample 75 pages ≈ 2 min. SDM build for 1,124 pages ≈ 3 min. TC-16's estimate was 3.3 s/page under contention; uncontended it is half that.
- **Storage (MEASURED):** raw candidates 35 MB (1,049 pages) + SGV; SDM pages, attach, lessons, metrics, renders: see MANIFEST.md (whole `tc2-p1/` tree ≈ 0.2 GB, no page PDFs kept — they are cut to a temp dir and deleted).
- **SDM-v2 block** (superset of TC-11 §2): `id`, `order`, `native_label`, `text` (**enumerator-preserving**: Docling's `orig`/`marker` restores "1." / "A." — 5,110 blocks restored on the slice — and the first OCR line under the bbox is cross-checked), `bbox [x,y,w,h]`, `column`, `ocr_conf` (mean of the OCR lines under the bbox), `colour {share,left,right,top,bottom}` (pale-tint share from a 36-dpi render), `extraction`, `agreement {text_sim, verifier_id, verifier_role, order_ok}`, `role {value, coarse, method, confidence, evidence[], verifier_hint, conflict}`, `guards[]`, `trust {status, reasons[]}`, `learning`, `refers_figure`, `heading_path[]`, `lesson`. Page-level: `figures[]`, `tables[]` (cell grid), census `features`, `printed_page`.

## A.2 Block trust — agreement gate + guards with reason codes (TC-10, TC-19 #4)

Agreement rule unchanged from TC-v1 (`tc_cascade`: text alignment ≥ 92 in the verifier's reading-order stream; offsets must not go backwards, one-block tolerance; QUESTION-vs-HEADING role conflict). New: a block whose role is flex (sidebar, caption, footnote, figure text, stage label) is **not** withheld on order alone (its position relative to the main flow is not meaning-bearing — the gold's `flex_groups` convention), only on text.

| reason code | rule (deterministic) | slice: learning blocks withheld (6 books) |
|---|---|---|
| `agree_text` | text not found at ≥ 92 similarity in the XY-cut stream | 865 |
| `agree_order` | verifier places the block earlier than the previous trusted one (non-flex roles) | 229 |
| `role_conflict` | primary QUESTION where the verifier says heading | 0 on the slice (the stem rule was removed after it fired on Toán worked examples — dev set) |
| `math_guard` | math tokens (`1/5`, `x ≠`, `<`, `²`, `∫`…) in a non-formula, non-table block | 42 |
| `empty_block` / `furniture` | no letters; page number / running head | not learning blocks (counted separately) |
| `box_boundary` | pale-colour share ≥ 0.5 on one edge third and ≤ 0.08 on the opposite third of a ≥ 2-line block (a block spanning a box edge) | 95 |
| `figure_dependent` | question/activity/instruction text refers to "Hình N", "hình bên", "quan sát hình…" | 638 — the second-largest reason: Science questions are figure questions |
| `answer_leak` | "Đáp án / Lời giải / Gợi ý / Trả lời / M:" or an SGV answer section | 30 on SGK pages ("Trả lời:" / model-answer lines inside SGK); 56 on the SGV sample |
| `teacher_text` | SGV prose / GV–HS lines / quoted prompts | 693 on the SGV sample |
| `page_feature:diagram` | census diagram page: blocks inside a picture bbox or short label-like blocks | 199 |
| `page_feature:color_heavy` | census colour-heavy page: all text except headings/captions | 111 |
| `figure_text` | block inside a Docling picture bbox (labels) | not a learning block; 379 (dev) / 223 (held-out) gold blocks |
| `low_ocr_conf` | mean OCR confidence under the bbox < 0.6 | 20 |
| `role_conflict` (slice) | | 7 |

**On gold (MEASURED, `metrics/gold-scores.md`):**

| set | pages | learning blocks | trusted (coverage) | TLSR | false-trusted | **FTR** | safe rejections | text acc | order | fidelity | splices |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (TC-v1 38) | 38 | 462 | 323 (0.699) | 0.621 | 36 | **0.112** | 125 | 0.964 | 0.984 | 0.975 | 8 |
| held-out (TC-v2 16) | 16 | 181 | 116 (0.641) | 0.564 | 14 | **0.121** | 63 | 0.981 | 0.986 | 0.979 | 2 |
| science (23) | 23 | 269 | 190 (0.706) | 0.636 | 19 | **0.100** | 77 | 0.982 | 0.987 | 0.987 | 3 |
| TC-v1 reference: docling ▸ xycut + math guard (dev 38) | 38 | 462 | 354 (0.766) | 0.673 | 43 | 0.121 | 85 | 0.954 | — | — | 6 |

Reading: the guards buy **no headline FTR improvement on hard pages** (0.112 vs 0.121) at a coverage cost (0.699 vs 0.766); what they buy is *which* blocks are withheld — figure-dependent prompts, objectives, answer keys, teacher text, diagram labels — i.e. the WAL-204/206 failure classes rather than random text. The remaining false trusts are TC-08's structural residue: order (17 dev / 5 held-out), text CER (7 / 3), splices (6 / 2), as-question (7 / 0). The held-out FTR (0.121) equals the dev FTR: the guards did not over-fit the dev pages.

**On the slice (MEASURED, `metrics/slice-report.md`):** 1,049 pages · 14,451 learning blocks · **12,348 TRUSTED (0.854)** · 1,868 WITHHELD · 235 CONFLICT. Per book: Khoa học 4 0.830 · Khoa học 5 0.850 · KHTN 6 0.825 · KHTN 7 0.853 · KHTN 8 0.877 · KHTN 9 0.873. The true false-trust rate on these pages is not annotated; it lies between the plain-prose rate (≈ 0) and the hard-page rate (0.10–0.12) — ESTIMATED 4–8 %, the same caveat as TC-13.

## A.3 Role Layer (TC-19 #3) — deterministic lexicon + geometry + colour + verifier hint

Roles: heading · stage_label · body · question · option · answer_slot · activity · instruction · objective · sidebar · caption · footnote · table · formula · figure_text · model_answer / answer · teacher_text · teacher_prompt · running_head · page_number. Evidence per block (`role.evidence[]`): e.g. `['verb + "được"']`, `['inside labelled side box']`, `['XY-cut agrees: sidebar']`. **No learned or VLM proposer was added** — the deterministic layer alone was measured first, as ordered. Full per-role numbers and the Short-Answer verdict: `ROLE-LAYER-AND-SHORT-ANSWER-GATE.md`. Headline (science gold, 23 pages): QUESTION 0.889 / 0.870 (trusted-question precision 0.970, n=33) · SIDEBAR 0.964 / 0.818 · OBJECTIVE 0.696 / 0.941 · HEADING 0.983 / 0.826 · ACTIVITY **0.00** · INSTRUCTION 0.50 · ANSWER 0.80 / 0.40. **Target 0.95 for QUESTION: not met** (0.83–0.89 over all questions).

## A.4 Lesson attachment + TOC repair (TC-19 #5) — `tc2_attach.py`

Header-based, on OCR lines (never on extractor output): three header forms (secondary "Bài N"/"BÀI N. TITLE"; KNTT-6 small "Bài N" beside a big uppercase title; elementary small "Bài" + large digit, with a TOC-title fallback when the OCR drops the digit), front/back matter and TOC pages → no lesson, theme openers → no lesson unless a banner follows on the same page, `continues` for header-less pages, a sequence rule (n = current+1, or TOC-confirmed within ±1 printed page; backward jumps rejected), two-lessons-on-one-page by header y.

| | dev 38 | held-out 16 | science 23 |
|---|---|---|---|
| TOC-range attachment correct | 28/38 | 9/16 | 15/23 |
| **header-based attachment correct** | 28/38 | **15/16** | **22/23** |

The one science miss is SGV KHTN 9 p136 whose gold lesson number is itself inferred from content (marked so in the gold). The dev misses are non-Science conventions (Ngữ văn/LS&ĐL/Toán/SGV Toán headers) that this slice did not target. **TOC repair (slice, MEASURED):** Khoa học 4 27 → 31 ranged; Khoa học 5 22 → 30; KHTN 7 17 → 37 (24 header-only lessons, up to Bài 39); KHTN 8 22 → 44 (29 header-only, up to Bài 47); KHTN 6 55 → 55 (53 confirmed); KHTN 9 51 → 51. Denominators are reported separately in I.1 — never collapsed.

## A.5 Trusted Structured Lesson — `tc2_tsl.py` (see B)

238 lesson documents across the six books (2 FULL, 236 PARTIAL, 0 NONE), 11,971 native trusted blocks and 2,032 withheld regions with bbox + reason (the withheld count includes CONFLICT blocks); two Hybrid Smart Book projections per lesson (C). No answer key is serialised anywhere (`answer_keys_included: false`, checked on the SGV sample).

## A.6 What did NOT hold / was falsified (evidence, cause, consequence)

1. **"Guards will push FTR well below the cascade's 12 %" — FALSIFIED on hard pages.** FTR 0.112 dev / 0.121 held-out. Cause: the residue is order/CER/splice errors that both stacks share (TC-17 #1); guards target *semantic* classes, not shared-mode errors. Consequence: the < 1 % bar needs a structurally different verifier or human review on shipped lessons (J.4, J.7), exactly as TC-18 said.
2. **"A deterministic labeller can reach 0.95 question precision" — NOT reached** (0.83–0.89). Cause: the activity/question and worked-example/question boundaries are icons, box colours and typography, not words. Consequence: Short-Answer stays deferred; the next signal must come from the page image (icon/box detection), deterministically.
3. **"ACTIVITY is a lexical role" — FALSIFIED** (precision 0.00 on 10 gold activities). Same cause.
4. **The census "diagram/colour-heavy" page guard costs real questions** (Khoa học 4 p6: the two real questions withheld). Measured, kept, reported as a price.
5. **TOC repair changes the denominator materially for KHTN 7/8** (18 → 37, 22 → 44 lessons). This is a fact about the books, not a pipeline artefact; it is filed as a decision request (I.1, DECISIONS-REQUESTED.md).
