# False-trust audit — RESULT of the 484-row shipped-content sample (measurement only)

WAL-210 · Round 3 · Lane A-DATA (A2) · 2026-09-05 · protocol: `docs/research/FALSE-TRUST-AUDIT-PROTOCOL.md` ·
**status: MEASUREMENT. No threshold is applied, no PASS/FAIL is called, no coverage changes.** The Founder sets acceptance
bars after these numbers (D3). Verbatim SGK text, crops and the annotated sheet stay in gitignored `poc-out/` (D4). Every
number carries its denominator (D5). Nothing here is divided by 3,679.

**Annotator: Claude Fable 5.1, single pass, page-render based** (an AI agent; not the author of the sampler, but the author
of the pre-check tooling and of this document). A second annotator on ≥ 10 % of rows is still required by the protocol
before any bar is called met — see §9.

## 1. What was audited

- Sample: `poc-out/b-lane/ft-audit/sample-20260905.jsonl`, seed 20260905, **484 rows = 420 stratified served blocks of the
  DEFAULT packs `g*-20260905T0413Z-320ae88e` + samUnits (25 strata, population 3,334 served blocks / 2,798 activities) + the
  mandatory KHTN 6 Bài 17 stratum (60 TRUSTED TSL blocks + 4 withheld, `tc2-p1`)**. 480 rows are served-as-trusted; the 4
  withheld rows never enter a served denominator.
- Every row was compared against a page render re-cut from the SGK PDF at 170 dpi around the matched region
  (`tool/corpus/ft_audit_sheets.py`, 206 contact sheets), with the served text beside it; pre-checks
  (`tool/corpus/ft_audit_precheck.py`: OCR-line similarity, enumerator presence, printed page ∈ curriculum lesson range,
  TC-v2 SDM status, layout family, subject) were shown as hints, never as verdicts. Two rows whose first crop cut the margin
  and two whose served page was wrong were re-judged on full-page renders.
- Outputs (internal): `poc-out/round3/ft-audit/annotated-20260905.jsonl` (484 rows, all fields filled),
  `annotations-20260905.jsonl` (append-only log), `scores-20260905.{json,md}` (`tool/corpus/ft_audit_score.py`).

## 2. Judging rules actually applied (deviations from the protocol are marked ⚠)

Per row, from the render: `display_fidelity`, `teaching_critical_fidelity`, `role_fidelity`, `lesson_attachment` (once per
activity), `false_trust` (annotator verdict) — values OK / WRONG / UNSURE / NA — plus ⚠ `reading_order` (OK / WRONG; NA when the
row is a single printed line), a display error class and a teaching-critical class.

- **display_fidelity WRONG** = any character-level difference beyond whitespace: tone-mark slips, dropped or altered enumerators
  (`1.` `a)` `I.`, circled section numerals), truncation, spliced/interleaved text, page numbers or watermark fragments appended,
  figure labels inserted, flattened fractions/tables. **Not counted:** bullet glyph `·`/`•`, straight vs curly quotes, hyphen vs en dash,
  `×` vs `x`, `hoá`/`hóa` placement variants, superscripts flattened to `m2`/`m3` when still readable, and a leading `–` bullet dropped
  from an experiment step (class `bullet_dropped`, listed but not counted — 14 rows).
- **teaching_critical_fidelity WRONG** (protocol: numbers, formulas, units, terms, negations) — applied as: a number/fraction/unit/formula
  changed or destroyed; ⚠ **truncation that removes a datum or leaves an instruction unusable** (class `truncation`); ⚠ **foreign
  text inserted inside a sentence** (figure labels, watermark, other-column lines — class `contamination`) or two layout cells
  interleaved so the statement changes (class `sequence`); ⚠ a tone slip that turns a **domain term, a proper name in a title/definition,
  or the object word of an exercise** into a different real word (class `term`, 20 rows — e.g. `vế câu`→`về câu` in a Ghi nhớ,
  `Tuệ Tĩnh`→`Tuệ Tình`, `đường thẳng`→`đường thắng`, `bỗng`×3 in an exercise that counts `bỗng`). Tone slips that produce non-words
  (`không khi`, `phẫu lọc`) are display-only. NA when the block carries none of these.
- **role_fidelity WRONG** = served kind ≠ printed role (a law statement as a procedure step, a section heading or the back cover as an
  "exercise", exercises as `section_text`, Viết/LTVC/Đọc-mở-rộng tasks as reading questions, a caption as body, a question as sidebar).
- **lesson_attachment**: judged once per activity from the page (badge/header) where visible; for the 45 rows the curriculum
  page-range pre-check flagged, the TV5 books proved to have a systematic +1…+3 offset in `pageStart` (the page carries the lesson badge)
  — attachment was judged by page content, and 12 rows without a header on the crop were accepted on that pattern (noted per row).
- **false_trust (annotator)** = served as trusted and wrong in a way that misleads: false or missing data, corrupted instruction,
  scrambled meaning, non-content served as content, wrong lesson; a display slip alone is not enough (except > 10 % characters wrong, the TC-08 text criterion — 1 row).
- **derived false trust** (scorer) = any of display / teaching-critical / role / reading-order WRONG, or attachment WRONG via the activity
  (⚠ reading order added; the protocol's 4-criterion derivation is reported beside it — identical here, every order error also failed display).
  Derived-WRONG rows are then partitioned into exactly one of **teaching-critical**, **display-only** (display wrong, everything else OK/NA)
  and **other** (role / attachment / order).

## 3. Results — rates reported separately (Wilson 95 %, k / n judged; unsure and NA beside)

### 3.1 Shipped content (420 served blocks / 398 activities; Bài 17 TSL stratum excluded)

| rate | k / n | rate [95 % CI] | unsure · NA |
|---|---|---|---|
| display fidelity error | 293 / 420 | **0.698** [0.652, 0.740] | 0 · 0 |
| teaching-critical fidelity error | 140 / 277 | **0.505** [0.447, 0.564] | 2 · 141 |
| reading-order error (multi-line rows) | 99 / 324 | **0.306** [0.258, 0.358] | 0 · 96 |
| role error | 39 / 420 | **0.093** [0.069, 0.124] | 0 · 0 |
| lesson-attachment error (per activity) | 11 / 396 | **0.028** [0.016, 0.049] | 0 · 2 |
| **false trust (derived, 5 criteria)** | 298 / 420 | **0.710** [0.664, 0.751] | 0 · 0 |
| — teaching-critical false trust | 140 / 420 | **0.333** [0.290, 0.380] | |
| — display-only false trust | 123 / 420 | **0.293** [0.251, 0.338] | |
| — other false trust (role / attachment / order) | 35 / 420 | **0.083** [0.061, 0.114] | |
| false trust (protocol 4 criteria) | 298 / 420 | 0.710 [0.664, 0.751] | |
| false trust (annotator verdict) | 160 / 419 | **0.382** [0.337, 0.429] | 1 · 0 |

Population for these rates: 3,334 served blocks / 2,798 activities in the default packs (`manifest-20260905.json`); blocks from one
activity are not independent (398 activities behind 420 blocks) — the block-level intervals are slightly optimistic.

### 3.2 KHTN 6 Bài 17 — the Trusted Structured Lesson stratum (60 TRUSTED blocks / 4 page-activities; TSL `tc2-p1`) — own line

| rate | k / n | rate [95 % CI] | unsure · NA |
|---|---|---|---|
| display fidelity error | 12 / 60 | **0.200** [0.118, 0.318] | 0 · 0 |
| teaching-critical fidelity error | 0 / 10 | **0.000** [0.000, 0.278] | 0 · 50 |
| reading-order error | 0 / 22 | 0.000 [0.000, 0.149] | 0 · 38 |
| role error | 2 / 60 | 0.033 [0.009, 0.114] | |
| lesson-attachment error | 0 / 4 | 0.000 [0.000, 0.490] | |
| false trust (derived) | 14 / 60 | **0.233** [0.144, 0.354] | |
| — teaching-critical | 0 / 60 | **0.000** [0.000, 0.060] | |
| — display-only | 12 / 60 | 0.200 [0.118, 0.318] | |
| — other | 2 / 60 | 0.033 [0.009, 0.114] | |
| false trust (annotator verdict) | 0 / 60 | **0.000** [0.000, 0.060] | |

The 12 display slips are 10 tone-mark OCR slips producing non-words (`không khi`, `lăng xuông`, `thủỷ`, `phẫu`×3, `Tiền hành`×2, `thể/răn`,
`bế/bấn`, `Em cô thể`, `vặn khoa`, `phếu`) and 2 circled section numerals (`I`→`·`, `II`→`I`); the 2 role errors are a caption
fragment served as body and question 2 of a ?-box served as sidebar. **Withheld rows reviewed: 4 / 4 are safe rejections** —
three plain figure captions withheld by `page_feature:diagram` and one procedure step with inline `1/4`, `1/2` withheld by
`math_guard`: the pipeline over-withholds here, it does not under-withhold. Numbers and terms in the 60 served blocks are correct.

### 3.3 All 480 served rows (shipped + TSL) — for completeness

display 305 / 480 = 0.635 [0.591, 0.677] · teaching-critical 140 / 287 = 0.488 [0.431, 0.545] · reading order 99 / 346 = 0.286
[0.241, 0.336] · role 41 / 480 = 0.085 [0.064, 0.114] · attachment 11 / 400 = 0.028 [0.015, 0.049] · false trust 312 / 480 = 0.650
[0.606, 0.691] (teaching-critical 140 / 480 = 0.292 [0.253, 0.334]; display-only 135 / 480 = 0.281 [0.243, 0.323]; other 37 / 480 =
0.077 [0.056, 0.104]) · annotator verdict 160 / 479 = 0.334 [0.293, 0.377].

### 3.4 By activity family (served blocks / activities)

| family | n | display | teaching-critical | reading order | role | attachment (act.) | false trust (derived) | teaching-critical FT | display-only FT | annotator FT |
|---|---|---|---|---|---|---|---|---|---|---|
| samUnits (grounding store) | 310 / 310 | 238/310 = 0.768 [0.718, 0.811] | 113/222 = 0.509 [0.444, 0.574] | 89/271 = 0.328 | 30/310 = 0.097 | 9/310 = 0.029 | **239/310 = 0.771 [0.721, 0.814]** | 113/310 = 0.365 [0.313, 0.419] | 102/310 = 0.329 | 130/309 = 0.421 |
| tvReadings | 51 / 41 | 21/51 = 0.412 [0.288, 0.548] | 6/15 = 0.400 | 6/37 = 0.162 | 6/51 = 0.118 | 0/41 [0, 0.086] | **23/51 = 0.451 [0.323, 0.586]** | 6/51 = 0.118 [0.055, 0.234] | 11/51 = 0.216 | 6/51 = 0.118 |
| khoaExperiments | 32 / 24 | 18/32 = 0.562 [0.393, 0.718] | 11/24 = 0.458 [0.279, 0.649] | 1/5 | 3/32 = 0.094 | 0/24 [0, 0.138] | **19/32 = 0.594 [0.423, 0.745]** | 11/32 = 0.344 [0.204, 0.517] | 5/32 = 0.156 | 13/32 = 0.406 |
| toanExercises | 9 / 9 | 7/9 = 0.778 | 7/9 = 0.778 [0.453, 0.937] | — | 0/9 | 1/9 | **7/9 = 0.778** | 7/9 = 0.778 | 0/9 | 7/9 |
| tvWritings | 7 / 7 | 5/7 = 0.714 | 1/1 | 1/5 | 0/7 | 0/7 | 5/7 = 0.714 [0.359, 0.918] | 1/7 | 3/7 | 1/7 |
| suSources | 6 / 4 | 4/6 | 2/6 | 2/6 | 0/6 | 0/4 | 4/6 = 0.667 [0.300, 0.903] | 2/6 | 2/6 | 2/6 |
| diaMaps | 3 / 1 | 0/3 | NA | NA | 0/3 | NA (no lesson claimed) | 0/3 [0, 0.561] | 0/3 | 0/3 | 0/3 |
| sourceAssets | 2 / 2 | 0/2 | NA | NA | 0/2 | 1/1 (map asset: Bài 1 vs Bài 2) | 1/2 | 0/2 | 0/2 | 1/2 |
| tslBai17 (TSL) | 60 / 4 | 12/60 = 0.200 | 0/10 | 0/22 | 2/60 | 0/4 | 14/60 = 0.233 | 0/60 [0, 0.060] | 12/60 | 0/60 |

### 3.5 By subject (served blocks; TSL rows included under KHTN)

| subject | n | display | teaching-critical | reading order | role | attachment | false trust (derived) | teaching-critical FT | annotator FT |
|---|---|---|---|---|---|---|---|---|---|
| Toán (4, 5) | 181 | 158/181 = 0.873 [0.817, 0.914] | 94/168 = 0.560 [0.484, 0.632] | 64/152 = 0.421 | 23/181 = 0.127 | 5/181 = 0.028 | **159/181 = 0.878 [0.823, 0.918]** | **94/181 = 0.519 [0.447, 0.591]** | 104/180 = 0.578 |
| Tiếng Việt 5 | 196 | 113/196 = 0.577 [0.507, 0.644] | 33/79 = 0.418 | 32/161 = 0.199 | 13/196 = 0.066 | 5/186 = 0.027 | **115/196 = 0.587 [0.517, 0.653]** | 33/196 = 0.168 [0.122, 0.227] | 40/196 = 0.204 |
| KHTN 6–9 (60 TSL + 17 pack) | 77 | 20/77 = 0.260 | 5/22 = 0.227 | 1/26 | 4/77 = 0.052 | 0/16 | 23/77 = 0.299 [0.208, 0.408] | 5/77 = 0.065 [0.028, 0.143] | 6/77 = 0.078 |
| Khoa học 4–5 | 10 | 6/10 | 3/7 | 0/1 | 0/10 | 0/8 | 6/10 = 0.600 | 3/10 | 3/10 |
| LS&ĐL 4–5 | 10 | 4/10 | 2/6 | 2/6 | 0/10 | 1/5 | 5/10 | 2/10 | 3/10 |
| Vật lí 10 | 3 | 3/3 | 3/3 | — | 0/3 | 0/2 | 3/3 | 3/3 | 3/3 |
| Hoá học 10 | 3 | 1/3 | 0/2 | — | 1/3 | 0/2 | 1/3 | 0/3 | 1/3 |

### 3.6 By layout family (K-12 census page class of the served page)

| layout | n | display | teaching-critical | reading order | role | attachment | false trust (derived) | teaching-critical FT |
|---|---|---|---|---|---|---|---|---|
| two_col | 214 | 167/214 = 0.780 [0.720, 0.831] | 94/170 = 0.553 [0.478, 0.626] | 77/163 = 0.472 [0.397, 0.549] | 30/214 = 0.140 | 11/191 = 0.058 | **172/214 = 0.804 [0.745, 0.851]** | **94/214 = 0.439 [0.374, 0.506]** |
| single | 265 | 138/265 = 0.521 [0.461, 0.580] | 46/117 = 0.393 [0.309, 0.484] | 22/182 = 0.121 [0.081, 0.176] | 11/265 = 0.042 | 0/209 [0, 0.018] | **140/265 = 0.528 [0.468, 0.588]** | 46/265 = 0.174 [0.133, 0.224] |
| sparse | 1 | 0/1 | — | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |

Every attachment error and 78 % of the reading-order errors sit on `two_col` pages; the teaching-critical rate on two-column pages is
2.5× the single-column rate.

### 3.7 By served role (kinds with n ≥ 5)

| family / kind | n | display | teaching-critical | role | false trust (derived) | teaching-critical FT |
|---|---|---|---|---|---|---|
| samUnits / exercise | 241 | 184/241 = 0.763 | 86/179 = 0.480 | 17/241 = 0.071 | 185/241 = 0.768 [0.710, 0.817] | 86/241 = 0.357 |
| samUnits / section_text | 63 | 49/63 = 0.778 | 24/37 = 0.649 | 13/63 = 0.206 | 49/63 = 0.778 | 24/63 = 0.381 |
| khoaExperiments / title | 8 | 8/8 (index `1.`/`2.` always dropped) | 1/3 | 2/8 | 8/8 | 1/8 |
| khoaExperiments / step1 | 6 | 4/6 | 4/5 | 1/6 | 5/6 | 4/6 |
| khoaExperiments / chuanBi | 8 | 2/8 | 2/8 | 0/8 | 2/8 | 2/8 |
| toanExercises / expr | 9 | 7/9 | 7/9 | 0/9 | 7/9 | 7/9 |
| tvReadings / passage | 5 | 5/5 (page numbers inside the text) | 1/5 | 0/5 | 5/5 | 1/5 |
| tvReadings / question1–6 | 7–10 each | 0.10–0.86 | 0–2 each | 0–2 each | 0.125–0.857 | 0–2 each |
| tvWritings / prompt | 7 | 5/7 | 1/1 | 0/7 | 5/7 | 1/7 |

### 3.8 By stratum (family × book) — the largest and the extremes (full table in `scores-20260905.md`)

samUnits Toán 5 tập một 29: FT 28/29 = 0.966, teaching-critical 22/29 = 0.759 · samUnits Toán 4 tập hai 52: FT 47/52 = 0.904, tc 34/52 = 0.654 ·
samUnits Toán 5 tập hai 46: FT 39/46 = 0.848, tc 15/46 = 0.326 · samUnits Toán 4 tập một 45: FT 38/45 = 0.844, tc 16/45 = 0.356 ·
samUnits TV5 tập một 71: FT 46/71 = 0.648, tc 14/71 = 0.197 · samUnits TV5 tập hai 67: FT 41/67 = 0.612, tc 12/67 = 0.179 ·
tvReadings TV5 tập hai 27: FT 12/27 = 0.444, tc 2/27 = 0.074 · tvReadings TV5 tập một 24: FT 11/24 = 0.458, tc 4/24 = 0.167 ·
khoaExperiments: Khoa học 4 3/6, Khoa học 5 3/3, KHTN 6 2/3, KHTN 7 3/3, KHTN 8 1/3, KHTN 9 3/8, Hoá 10 1/3, Vật lí 10 3/3 (tc 3/3).

## 4. What the failures are (classes over the 480 served rows; a row can carry several)

Display classes: tone_mark 120 · extra_text (page numbers, watermark fragments, badges, next-page headers appended) 120 ·
figure_text (labels / signs / captions served as prose) 66 · layout_merge (side-by-side boxes, bubbles, columns interleaved line by line) 60 ·
math_flattened 54 · ocr_char 54 · truncated 50 · splice 34 · enumerator_dropped 27 · table_flattened 22 · bullet_dropped 14 (not counted).
Teaching-critical classes: contamination 47 · fraction 45 · number 24 · term 20 · formula 15 · unit 15 · truncation 14 · sequence 11.

The systematic classes (each with a mechanical cause; ids are sample ids in the annotated sheet):

1. **Fractions, mixed numbers, exponents, chemical subscripts flattened** — every Toán unit with a fraction (0122–0144, 0365–0394, 0417–0425)
   and `AgNO₃`→`AgNO,` (0090), `m²`/`m³`→`m?`/`m₴`/`mở` (0342–0345, 0369, 0393–0394). Produces false data: `1/4 cái lá cỏ`→`1 cái lá cỏ` (0131),
   `8/5 dm`→`8 dm` (0138), `1/5 giờ`→`5 giờ` — flips the answer (0149), `9 dm = 9 m` inside the decimal definition (0386), `1 360 m²`→`1 360 m` (0393).
2. **Experiment steps cut at the first printed line** — khoaExperiments steps that wrap lose their second line: reagents, orientation, the
   acid addition, the observation (0067, 0070, 0074, 0082, 0091, 0096–0098); problems cut before their prices/data (0159, 0377, 0387).
3. **Cross-column / box interleaving** — speech bubbles, hint boxes, two-column definitions, poems, option boxes read line by line
   across columns (0079, 0108, 0115, 0163, 0199, 0229, 0311, 0315, 0403, 0429, 0453, 0460): definitions become false statements
   (`Góc nhọn bé hơn Góc tù lớn hơn…`, `Cạnh bên AD song song`, `Danh từ — Từ chỉ hoạt động…`).
4. **Figure text and page furniture served as content** — labels, prices, back-cover book lists, `luyện tập` icons as exercises or
   section text (0120, 0150, 0172–0173, 0186, 0260–0262, 0332–0333, 0347, 0363, 0378–0379); page numbers appended to 120 rows, sometimes
   fused into a value (`D. 20 112`, 0146).
5. **Geometry-rebuilt Toán expressions that are not in the book** — 7 of 9 toanExercises (`19/33 − 3/5` pairs two items; `2/5 + 1/4` has the
   wrong operator; `13/18 + 7/6`, `7/11 + 4/11`, `15/14 + 7/4` drop half the expression).
6. **Deliberately-false content served without its frame** — a true/false game's cards (`821 : 39 = 19`) as a standalone exercise (0113);
   matching tables flattened into wrong pairs (0234, 0453); `Tìm lỗi sai` computations as digit strings (0396).
7. **Lesson attachment**: 11 wrong activities — 8 are the **back cover** (book list, ISBN, price) attached to the last lesson of Toán 4 tập hai,
   Toán 5 tập hai, TV5 tập một, TV5 tập hai (0150, 0260–0262, 0332–0333, 0378–0379); one unit merges the end of Toán 4 Bài 21 with the whole
   Bài 22 khám phá (0177); the LS&ĐL 5 map asset claims Bài 1 while its page is Bài 2 (0410, the known registry issue); one toanExercise keyed
   to L29 sits on the Bài 35 page (0425). Source *location* errors that are not attachment errors: the diaMaps questions live on the page
   after the map page (0065–0066), a TV5 prompt's `pagePdf` is 11 pages off (0482).
8. **Role**: 41 rows — exercises as `section_text` (13), Viết/LTVC/Đọc-mở-rộng tasks as reading questions (6), non-content as exercise (9),
   a physics law as procedure step (0080), section headings as experiment titles (0086, 0095), caption as body / question as sidebar in the TSL.
9. **Tone-mark OCR slips**: 120 rows; 20 hit a term or name (`vế câu`, `Tuệ Tĩnh`×2, `Nguyễn Đình Chiểu`, `đường thẳng`×2, `Thổi`, `Dế Mèn`,
   `nóng rẫy`, `sầm uất`, `bỗng`×3, `Cộng hoà`, `mơ tưởng`, `phù thuỷ`…); the rest produce non-words.

## 5. Sample size for a «< 1 % false trust» claim (formula from the protocol; no decision)

Wilson upper bound `U(k, n) < 0.01` needs n ≥ 381 with k = 0, 563 with k = 1, 726 with k = 2, 878 with k = 3, 1,025 with k = 4, 1,166 with
k = 5 (exact: 299, 473, 628, 773, 913, 1,049). **At the observed shipped rate (298 / 420 derived; 140 / 420 teaching-critical;
160 / 419 by annotator verdict) no sample size can support the claim** — the observed proportion itself is above 1 %, so the number
that matters is not n but the count of failing classes to fix and re-sample (new seed). For the Bài 17 TSL stratum the teaching-critical
count is 0 / 60 (upper bound 0.060); a < 1 % claim for that pipeline would need ≥ 381 judged TSL blocks with 0 failures — six such lessons.

## 6. Worst examples (block / unit ids; short quotes only) — the scorer's top of 312, teaching-critical first

| sample | family · book · lesson · pdf | served (≤ 40 chars) | what is wrong |
|---|---|---|---|
| s…-0149 | samUnits · Toán 4 tập hai · L73 · p119 | `…ô tô màu đỏ đi hết 5 giờ…` | `1/5 giờ`→`5 giờ`: the answer of the MCQ changes |
| s…-0131 | samUnits · Toán 4 tập hai · L61 · p82 | `Dế trüi có cái lá cỏ…cho dế mèn 1 cái` | `3/8` dropped, `1/4`→`1` |
| s…-0138 | samUnits · Toán 4 tập hai · L63 · p91 | `…mỗi hình vuông nhỏ là 8 dm` | `8/5 dm`→`8 dm` |
| s…-0386 | samUnits · Toán 5 tập một · L10 · p33 | `9 dm = 9 m; m viết là 0,9 m` | `9 dm = 9/10 m` served as `9 dm = 9 m` in the definition of decimals |
| s…-0127 | samUnits · Toán 4 tập hai · L60 · p76 | `21+1=31` | `2/6 l + 1/6 l = 3/6 l` |
| s…-0113 | samUnits · Toán 4 tập hai · L45 · p29 | `821 : 39 = 19; … 51 x 103 = 4 973` | a true/false game's false cards served as an exercise |
| s…-0090 | khoaExperiments · KHTN 9 · L29 · p133 | `dung dịch AgNO, 1%, dung dịch NH, 5%` | `AgNO₃`, `NH₃` subscripts lost |
| s…-0082 | khoaExperiments · KHTN 8 · L5 · p25 | `…cốc (2) đựng dung` | step cut before `dịch sodium sulfate…`; second reagent lost |
| s…-0079 | khoaExperiments · KHTN 7 · L16 · p80 | `…(3) 30° 0° 30° - Một bảng chia độ…` | figure labels interleaved into the equipment list |
| s…-0080 | khoaExperiments · KHTN 7 · L16 · p80 | `Tia sáng phản xạ nằm trong mặt phẳng tới;` | the law of reflection served as procedure step 1 |
| s…-0096 | khoaExperiments · Vật lí 10 · L18 · p74 | `Găn lực kế vào giá thí nghiệm đế cố định` | `theo phương nằm ngang.` cut off; 2 tone slips |
| s…-0419 | toanExercises · Toán 4 tập hai · L73 · p118 | `19/33 - 3/5` | not in the book (mixes items a and b) |
| s…-0424 | toanExercises · Toán 5 tập một · L6 · p22 | `2/5 + 1/4` | printed `2/5 − 1/4` |
| s…-0196 | samUnits · TV5 tập hai · L1 · p11 | `…được gọi là một về câu…` | Ghi nhớ definition: `vế câu`→`về câu` ×2 |
| s…-0312 | samUnits · TV5 tập một · L25 · p125 | `Bống thấy… Bỗng thấy… Bồng tôi thấy` | the exercise counts `bỗng`; served text has it once instead of 3× |
| s…-0453 | tvReadings · TV5 tập một · L1 · p11 | `Danh từ Từ chỉ hoạt động, trạng thái…` | matching table flattened into false definitions |
| s…-0412 | suSources · LS&ĐL 4 · L7 · p35 | `…tại miếu Tố chức vào ngày 10 tháng Ba…` | body-column lines interleaved into a primary-source quote |
| s…-0177 | samUnits · Toán 4 tập một · L21 · p76 | `…James Watt… chủ đề 5 … Bài 22 …` | Bài 22 khám phá served under L21; litre unit lost |
| s…-0150 | samUnits · Toán 4 tập hai · L73 · p122 | `8. Mì thuật 4 Website: … ISBN …` | back cover served as an exercise of Bài 73 |
| s…-0311 | samUnits · TV5 tập một · L25 · p123 | `Tiếng đàn ba-la-lai-ca Ngày mai Như ngọn gió…` | a two-column poem interleaved line by line |

The full list (312 rows, with notes) is in `poc-out/round3/ft-audit/scores-20260905.md` and the annotated JSONL.

## 7. Denominators (D5)

Rates = k / n **judged served blocks of this sample** (seed 20260905), subset named in each table; population = 3,334 served blocks /
2,798 activities of packs `g*-20260905T0413Z-320ae88e` + 2,584 samUnits rows; Bài 17 = 60 TRUSTED TSL blocks of `tc2-p1`. UNSURE (3 rows)
and NA are never folded into either side. The historical 3,679 / 3,381 lesson counts are not used. The learnable count 111 / 3,679 is a
coverage number and is unaffected by this measurement.

## 8. Cross-checks against earlier measurements

- TC-v1 measured the naive extractor at FTR 0.321 on 38 hard gold pages (block text only); this sample, on the exact shipped blocks and
  with role/attachment/order included, measures 0.710 derived / 0.382 by verdict — the two are different definitions on different
  populations; the direction (Toán and two-column pages worst, single-column TV prose best) agrees with TC-v1 §08.
- The TC-v2 SDM verdict shown as a hint on the 27 Science rows that have an SDM block on the same page agreed with the annotation on
  14: 11 trusted-and-clean, 3 withheld-and-wrong (0073 `agree_text`, 0090 `page_feature:diagram`, 0091 `figure_text`). It disagreed on
  13: 12 rows whose SDM block is TRUSTED but whose *served* text is wrong — truncated steps and dropped experiment indices, i.e. errors of
  the pack's line-based extractor that the SDM block never had — and 1 withheld row (0083, `agree_text`) that is served verbatim. The SDM
  judges its own block; it is not a substitute for auditing the served text.
- The audit 02 estimate «18.8 % of experiment strings would be withheld by TC-v2» is consistent with khoaExperiments' 0.594 derived rate:
  most of the failures (truncated steps) are ones the naive extractor cannot see.

## 9. Limitations — what a second annotator should re-check first

1. **Single annotator, single pass, AI.** The protocol requires a second annotator on ≥ 10 % (≥ 48 rows) before any bar is called met.
   Suggested slice: all 20 `term` rows, all 41 role-WRONG rows, the 11 attachment-WRONG activities, and 20 random display-OK rows.
2. Judged from 170-dpi renders; six passages spanning two pages were verified on their first page only (second page from the text) —
   0213, 0247, 0319, 0329, 0449, 0472. 12 TV5 attachment rows were accepted on the +1 pageStart offset pattern without a header on the crop.
3. Reading order was judged only where the row had ≥ 2 printed lines; cross-page order was not assessed.
4. The teaching-critical extensions (truncation, in-sentence contamination, term-level tone slips) are marked ⚠ above and are separable
   by class in the JSONL (`teaching_critical_class`), so the Founder can re-slice under the literal protocol definition without re-annotating:
   of the 140 shipped teaching-critical rows, **77 carry a `fraction` / `number` / `formula` / `unit` error** (77 / 420 = 0.183 [0.148, 0.223]
   under the narrowest reading) and 63 carry only the extension classes (contamination 35, term 20, truncation 9, sequence 10; overlapping).
5. The pre-checks were visible while judging (not blind).
6. Nothing here measures what a child would *do* with the text; it measures whether the text is what the book says.

## 10. What this document does not decide

No acceptance threshold, no family is declared shippable or not, no coverage change, no pipeline change. It reports that, measured on
the exact blocks served today, the shipped packs and the grounding store carry teaching-critical errors in roughly one served block in
three (Toán: one in two; single-column TV prose: about one in six), and that the one Trusted Structured Lesson in the sample carries none
in 60 blocks while over-withholding 4 regions — the numbers the Founder asked for before setting bars (D3, G1).
