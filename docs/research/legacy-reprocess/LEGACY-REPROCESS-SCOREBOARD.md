# Legacy reprocess scoreboard — rounds 4 + 5 (Lane D)

`legacy-scoreboard-v1` · generated 2026-09-05T16:25:48+00:00 · source registry `legacy-registry-v1` (aeca24300b8f) · **measurement only — no threshold, no PASS/FAIL**

Legacy content is never a trusted teaching source. REPROCESSED ≠ TRUSTED: a reprocessed lesson is a *candidate* until it clears an independent audit against a threshold **the Founder sets**.

## Denominators (D5 — never summed, never mixed)

| denominator | N | definition |
|---|---|---|
| canonical | 3,679 | SGK lessons with a lesson number in curriculum-structure.json (Grade 1–12, 301 SGK documents) |
| ranged | 3,381 | canonical lessons that also have a TOC pageStart |
| baseline_learnable | 113 | lessons with ≥ 1 non-router activity in the default packs (poc-out/p0-experiment/baseline-learnable.json, 2026-09-04); 111 after the WAL-210 G2/G3 gates |
| in_scope | 243 | legacy lessons in Lane D scope = 113 baseline ∪ lessons with sam-units rows |

## Scoreboard

| measure | count | of what |
|---|---|---|
| total legacy lessons in scope | **243** | 113 baseline ∪ sam-units lessons; = 6.6% of the 3,679 canonical historical lessons |
| pending | **231** | in scope, in no batch yet |
| reprocessed (from original source) | **12** | of 243 in scope = 4.9% |
| independently audited | **6** | of 12 reprocessed |
| trusted | **0** | no Founder threshold record at docs/research/legacy-reprocess/THRESHOLDS.json — `trusted` and `eligible for teaching` stay 0 by definition |
| partial (some blocks served, some withheld) | **12** | of 12 reprocessed |
| withheld (nothing servable) | **0** | of 12 reprocessed |
| rejected (pipeline produced no lesson) | **0** | of the lessons attempted |
| **eligible for teaching** | **0** | requires `trusted` ∧ a Founder teaching authorisation |

Full-sourceability lessons (every learning block trusted): 0. Reprocessed lessons outside the registry scope: 0.

## Batch `round4/legacy/batch-1` (spec `batch-1`) — pipeline `legacy-b1` (37 pages, code 2e424877508c7f3eded36d5cfb35815798df5cb6)

| lesson | risk | state | learning blocks | trusted | withheld | withheld reasons | audited rows |
|---|---|---|---|---|---|---|---|
| Toán 4 tập hai Bài 61 | toan, two_col, formula, order_suspect | **PARTIAL** | 19 | 9 | 10 | {'agree_text': 7, 'math_guard': 1, 'agree_order': 3} | 9 served + 5 withheld |
| Toán 4 tập hai Bài 73 | toan, two_col, formula, attachment_suspect, geometry_rebuilt_expr | **PARTIAL** | 83 | 67 | 16 | {'agree_text': 11, 'agree_order': 4, 'page_feature:color_heavy': 1, 'page_feature:diagram': 1} | 13 served + 5 withheld |
| Toán 5 tập một Bài 6 | toan, two_col, formula, geometry_rebuilt_expr | **PARTIAL** | 25 | 14 | 11 | {'math_guard': 3, 'agree_text': 10, 'low_ocr_conf': 1} | 12 served + 5 withheld |
| Tiếng Việt 5 tập một Bài 25 | tv5, two_col, order_suspect, attachment_suspect | **PARTIAL** | 85 | 62 | 23 | {'agree_text': 6, 'page_feature:color_heavy': 13, 'page_feature:diagram': 9, 'agree_order': 3} | 13 served + 5 withheld |
| Tiếng Việt 5 tập hai Bài 1 | tv5, two_col, attachment_suspect, role_suspect | **PARTIAL** | 57 | 50 | 7 | {'agree_text': 1, 'page_feature:color_heavy': 3, 'agree_order': 3} | 13 served + 5 withheld |
| KHTN 6 Bài 11 | khtn, two_col, figure_caption, role_suspect | **PARTIAL** | 95 | 85 | 10 | {'agree_text': 7, 'agree_order': 2, 'figure_dependent': 1} | 14 served + 5 withheld |

### OLD vs NEW false trust per failure class — batch `round4/legacy/batch-1`

rate = WRONG / (OK + WRONG) among **served** rows (what the side actually showed a child), Wilson 95 % · NA / UNSURE excluded and counted beside · no threshold applied.

OLD = 55 served blocks of the old units + packs · NEW = 74 served blocks of the new Trusted Structured Lessons (+ 30 withheld regions reviewed separately). The two sides are different block sets — the comparable quantity is *the share of what each side served that is wrong*.

| failure class | basis | OLD | NEW |
|---|---|---|---|
| display | verdict field | 39 / 55 = 0.709 [0.579, 0.812] | 15 / 74 = 0.203 [0.127, 0.308] |
| teaching_critical | verdict field | 26 / 36 = 0.722 [0.560, 0.842] | 5 / 24 = 0.208 [0.092, 0.405] |
| reading_order | verdict field | 14 / 33 = 0.424 [0.272, 0.592] | 0 / 26 = 0.000 [0.000, 0.129] |
| role | verdict field | 9 / 55 = 0.164 [0.089, 0.283] | 16 / 74 = 0.216 [0.138, 0.323] |
| attachment | verdict field | 2 / 55 = 0.036 [0.010, 0.123] | 8 / 74 = 0.108 [0.056, 0.199] |
| formula_number_unit | annotator tag / all judged | 22 / 55 = 0.400 [0.281, 0.532] | 7 / 74 = 0.095 [0.047, 0.183] |
| formula_number_unit (rows where the class applies) | annotator tag / applicable | 21 / 48 = 0.438 [0.307, 0.577] | 4 / 30 = 0.133 [0.053, 0.297] |
| figure_caption | annotator tag / all judged | 2 / 55 = 0.036 [0.010, 0.123] | 1 / 74 = 0.013 [0.002, 0.073] |
| figure_caption (rows where the class applies) | annotator tag / applicable | 2 / 2 = 1.000 [0.342, 1.000] | 1 / 2 = 0.500 [0.095, 0.905] |

### False withheld — batch `round4/legacy/batch-1`

| measure | value | of what |
|---|---|---|
| withheld regions reviewed | 30 | every withheld region in the audit sample |
| **FALSE WITHHELD (over-withheld)** | **12 / 30 = 0.400 [0.246, 0.577]** | clean, legible text refused for a reason that did not apply to it |
| safe refusals | 18 | genuinely damaged, ambiguous or figure-dependent |
| unclassifiable | 0 | excluded from the rate, counted here |


### Restore — batch `round4/legacy/batch-1`

**No restore stage ran.** no restore stage ran for this batch — no build change restored a reviewed withheld region, and no REPAIRED stage exists yet `restored`, `falsely-withheld recovered` and `RESTORE PRECISION` are **empty, not zero** — see «What this scoreboard does not say».


## Batch `round4/legacy/batch-1-rerun-tc2-p2-preview` (spec `batch-1`) — pipeline `tc2-p2` (37 pages, code origin/lane-a/round4-pipeline-failure-classes@206a103 (expor)

| lesson | risk | state | learning blocks | trusted | withheld | withheld reasons | audited rows |
|---|---|---|---|---|---|---|---|
| Toán 4 tập hai Bài 61 | toan, two_col, formula, order_suspect | **PARTIAL** | 19 | 4 | 15 | {'agree_text': 7, 'agree_order': 5, 'agree_numbers': 3, 'math_guard': 1} | 4 served + 0 withheld |
| Toán 4 tập hai Bài 73 | toan, two_col, formula, attachment_suspect, geometry_rebuilt_expr | **PARTIAL** | 64 | 39 | 25 | {'agree_text': 11, 'agree_order': 7, 'agree_tones': 5, 'agree_numbers': 2} | 6 served + 0 withheld |
| Toán 5 tập một Bài 6 | toan, two_col, formula, geometry_rebuilt_expr | **PARTIAL** | 25 | 12 | 13 | {'math_guard': 3, 'agree_text': 10, 'low_ocr_conf': 1, 'agree_tones': 2, 'agree_numbers': 1} | 11 served + 0 withheld |
| Tiếng Việt 5 tập một Bài 25 | tv5, two_col, order_suspect, attachment_suspect | **PARTIAL** | 85 | 55 | 30 | {'agree_order': 6, 'agree_text': 5, 'page_feature:color_heavy': 13, 'page_feature:diagram': 9, 'agree_tones': 5} | 14 served + 0 withheld |
| Tiếng Việt 5 tập hai Bài 1 | tv5, two_col, attachment_suspect, role_suspect | **PARTIAL** | 57 | 38 | 19 | {'agree_text': 1, 'agree_order': 8, 'page_feature:color_heavy': 3, 'agree_tones': 7} | 9 served + 0 withheld |
| KHTN 6 Bài 11 | khtn, two_col, figure_caption, role_suspect | **PARTIAL** | 95 | 65 | 30 | {'agree_order': 9, 'agree_numbers': 1, 'agree_tones': 12, 'agree_text': 7, 'figure_dependent': 1} | 12 served + 0 withheld |

### OLD vs NEW false trust per failure class — batch `round4/legacy/batch-1-rerun-tc2-p2-preview`

rate = WRONG / (OK + WRONG) among **served** rows (what the side actually showed a child), Wilson 95 % · NA / UNSURE excluded and counted beside · no threshold applied.

OLD = not re-sampled for this batch — the product side is unchanged, see the batch it re-runs · NEW = 56 served blocks of the new Trusted Structured Lessons (+ 0 withheld regions reviewed separately). The two sides are different block sets — the comparable quantity is *the share of what each side served that is wrong*.

**53 of the NEW verdicts were carried over** from the batch this one re-runs, and only where this build serves the identical text in the same region (tool/corpus/legacy/rerun.py). That makes this a *conditional* rate over the rows that survived, not a fresh stratified sample of this build — read it beside the re-run delta, not as a replacement for it.

| failure class | basis | OLD | NEW |
|---|---|---|---|
| display | verdict field | — (n = 0) | 10 / 56 = 0.179 [0.100, 0.298] |
| teaching_critical | verdict field | — (n = 0) | 3 / 15 = 0.200 [0.070, 0.452] |
| reading_order | verdict field | — (n = 0) | 1 / 17 = 0.059 [0.011, 0.270] |
| role | verdict field | — (n = 0) | 7 / 56 = 0.125 [0.062, 0.236] |
| attachment | verdict field | — (n = 0) | 3 / 56 = 0.054 [0.018, 0.146] |
| formula_number_unit | annotator tag / all judged | — (n = 0) | 4 / 56 = 0.071 [0.028, 0.170] |
| formula_number_unit (rows where the class applies) | annotator tag / applicable | — (n = 0) | 2 / 19 = 0.105 [0.029, 0.314] |
| figure_caption | annotator tag / all judged | — (n = 0) | 1 / 56 = 0.018 [0.003, 0.095] |
| figure_caption (rows where the class applies) | annotator tag / applicable | — (n = 0) | 1 / 2 = 0.500 [0.095, 0.905] |

### Restore — batch `round4/legacy/batch-1-rerun-tc2-p2-preview`

**No restore stage ran.** no restore stage ran for this batch — no build change restored a reviewed withheld region, and no REPAIRED stage exists yet `restored`, `falsely-withheld recovered` and `RESTORE PRECISION` are **empty, not zero** — see «What this scoreboard does not say».


## Batch `round4/legacy/batch-1-rerun-tc2-p2` (spec `batch-1`) — pipeline `tc2-p2` (37 pages, code af2245ab9c28990da92e56b295cbfd58b050bcd2)

| lesson | risk | state | learning blocks | trusted | withheld | withheld reasons | audited rows |
|---|---|---|---|---|---|---|---|
| Toán 4 tập hai Bài 61 | toan, two_col, formula, order_suspect | **PARTIAL** | 19 | 4 | 15 | {'agree_text': 7, 'agree_order': 5, 'agree_numbers': 3, 'math_guard': 1} | 4 served + 0 withheld |
| Toán 4 tập hai Bài 73 | toan, two_col, formula, attachment_suspect, geometry_rebuilt_expr | **PARTIAL** | 64 | 39 | 25 | {'agree_text': 11, 'agree_order': 7, 'agree_tones': 5, 'agree_numbers': 2} | 6 served + 0 withheld |
| Toán 5 tập một Bài 6 | toan, two_col, formula, geometry_rebuilt_expr | **PARTIAL** | 25 | 12 | 13 | {'math_guard': 3, 'agree_text': 10, 'low_ocr_conf': 1, 'agree_tones': 2, 'agree_numbers': 1} | 11 served + 0 withheld |
| Tiếng Việt 5 tập một Bài 25 | tv5, two_col, order_suspect, attachment_suspect | **PARTIAL** | 85 | 61 | 24 | {'agree_order': 6, 'agree_text': 5, 'page_feature:diagram': 8, 'page_feature:color_heavy': 1, 'agree_tones': 5} | 20 served + 0 withheld |
| Tiếng Việt 5 tập hai Bài 1 | tv5, two_col, attachment_suspect, role_suspect | **PARTIAL** | 57 | 40 | 17 | {'agree_text': 1, 'agree_order': 8, 'page_feature:color_heavy': 1, 'agree_tones': 7} | 11 served + 0 withheld |
| KHTN 6 Bài 11 | khtn, two_col, figure_caption, role_suspect | **PARTIAL** | 95 | 65 | 30 | {'agree_order': 9, 'agree_numbers': 1, 'agree_tones': 12, 'agree_text': 7, 'figure_dependent': 1} | 12 served + 0 withheld |

### OLD vs NEW false trust per failure class — batch `round4/legacy/batch-1-rerun-tc2-p2`

rate = WRONG / (OK + WRONG) among **served** rows (what the side actually showed a child), Wilson 95 % · NA / UNSURE excluded and counted beside · no threshold applied.

OLD = not re-sampled for this batch — the product side is unchanged, see the batch it re-runs · NEW = 64 served blocks of the new Trusted Structured Lessons (+ 0 withheld regions reviewed separately). The two sides are different block sets — the comparable quantity is *the share of what each side served that is wrong*.

**53 of the NEW verdicts were carried over** from the batch this one re-runs, and only where this build serves the identical text in the same region (tool/corpus/legacy/rerun.py). That makes this a *conditional* rate over the rows that survived, not a fresh stratified sample of this build — read it beside the re-run delta, not as a replacement for it.

| failure class | basis | OLD | NEW |
|---|---|---|---|
| display | verdict field | — (n = 0) | 13 / 64 = 0.203 [0.123, 0.317] |
| teaching_critical | verdict field | — (n = 0) | 3 / 17 = 0.176 [0.062, 0.410] |
| reading_order | verdict field | — (n = 0) | 1 / 21 = 0.048 [0.009, 0.227] |
| role | verdict field | — (n = 0) | 8 / 64 = 0.125 [0.065, 0.228] |
| attachment | verdict field | — (n = 0) | 3 / 64 = 0.047 [0.016, 0.129] |
| formula_number_unit | annotator tag / all judged | — (n = 0) | 4 / 64 = 0.062 [0.025, 0.150] |
| formula_number_unit (rows where the class applies) | annotator tag / applicable | — (n = 0) | 2 / 19 = 0.105 [0.029, 0.314] |
| figure_caption | annotator tag / all judged | — (n = 0) | 1 / 64 = 0.016 [0.003, 0.083] |
| figure_caption (rows where the class applies) | annotator tag / applicable | — (n = 0) | 1 / 2 = 0.500 [0.095, 0.905] |

### Restore — batch `round4/legacy/batch-1-rerun-tc2-p2`

**No restore stage ran.** no restore stage ran for this batch — no build change restored a reviewed withheld region, and no REPAIRED stage exists yet `restored`, `falsely-withheld recovered` and `RESTORE PRECISION` are **empty, not zero** — see «What this scoreboard does not say».


## Batch `round5/legacy/batch-2` (spec `batch-2`) — pipeline `tc2-p2` (34 pages, code 90f75e0daffab2cc34b388df8ad4a6e8d0b599b2)

| lesson | risk | state | learning blocks | trusted | withheld | withheld reasons | audited rows |
|---|---|---|---|---|---|---|---|
| LS&ĐL 4 Bài 12 | lsdl, two_col, figure_caption, order_suspect | **PARTIAL** | 46 | 24 | 22 | {'agree_order': 4, 'agree_tones': 9, 'figure_dependent': 5, 'agree_text': 4, 'agree_numbers': 1} | 11 served + 5 withheld |
| LS&ĐL 5 Bài 9 | lsdl, prose_dated_events, figure_caption, order_suspect | **PARTIAL** | 54 | 35 | 19 | {'agree_tones': 10, 'box_boundary': 3, 'agree_text': 7} | 12 served + 5 withheld |
| Khoa học 4 Bài 6 | khoa, two_col, figure_caption, order_suspect | **PARTIAL** | 55 | 33 | 22 | {'agree_text': 5, 'agree_tones': 5, 'figure_dependent': 9, 'agree_order': 1, 'math_guard': 2, 'page_feature:diagram': 1} | 11 served + 5 withheld |
| KHTN 9 Bài 5 | khtn, two_col, formula, figure_caption, order_suspect | **PARTIAL** | 105 | 74 | 31 | {'page_feature:diagram': 1, 'agree_tones': 8, 'agree_text': 8, 'figure_dependent': 3, 'box_boundary': 1, 'agree_order': 4, 'answer_leak': 3, 'chem_guard': 1, 'agree_numbers': 2} | 12 served + 5 withheld |
| Toán 4 tập một Bài 37 | toan, two_col, formula, attachment_suspect, last_lesson_of_book | **PARTIAL** | 58 | 31 | 27 | {'agree_order': 6, 'agree_numbers': 3, 'agree_text': 6, 'agree_tones': 6, 'page_feature:diagram': 4, 'math_guard': 4, 'unit_guard': 2, 'line_structure': 1} | 10 served + 5 withheld |
| Tiếng Việt 5 tập một Bài 5 | tv5, poem, two_col, color_heavy, order_suspect, attachment_suspect | **PARTIAL** | 60 | 42 | 18 | {'agree_order': 2, 'page_feature:color_heavy': 9, 'agree_text': 7, 'line_structure': 6, 'agree_tones': 3} | 11 served + 5 withheld |

### OLD vs NEW false trust per failure class — batch `round5/legacy/batch-2`

rate = WRONG / (OK + WRONG) among **served** rows (what the side actually showed a child), Wilson 95 % · NA / UNSURE excluded and counted beside · no threshold applied.

OLD = 43 served blocks of the old units + packs · NEW = 67 served blocks of the new Trusted Structured Lessons (+ 30 withheld regions reviewed separately). The two sides are different block sets — the comparable quantity is *the share of what each side served that is wrong*.

| failure class | basis | OLD | NEW |
|---|---|---|---|
| display | verdict field | 25 / 42 = 0.595 [0.445, 0.730] | 11 / 67 = 0.164 [0.094, 0.271] |
| teaching_critical | verdict field | 10 / 21 = 0.476 [0.283, 0.676] | 5 / 50 = 0.100 [0.043, 0.214] |
| reading_order | verdict field | 10 / 22 = 0.455 [0.269, 0.653] | 0 / 30 = 0.000 [0.000, 0.114] |
| role | verdict field | 5 / 43 = 0.116 [0.051, 0.245] | 10 / 66 = 0.151 [0.084, 0.257] |
| attachment | verdict field | 2 / 43 = 0.046 [0.013, 0.155] | 1 / 66 = 0.015 [0.003, 0.081] |
| formula_number_unit | annotator tag / all judged | 5 / 42 = 0.119 [0.052, 0.250] | 1 / 67 = 0.015 [0.003, 0.080] |
| formula_number_unit (rows where the class applies) | annotator tag / applicable | 4 / 24 = 0.167 [0.067, 0.358] | 1 / 35 = 0.029 [0.005, 0.145] |
| figure_caption | annotator tag / all judged | 0 / 42 = 0.000 [0.000, 0.084] | 2 / 67 = 0.030 [0.008, 0.102] |
| figure_caption (rows where the class applies) | annotator tag / applicable | — (n = 0) | 2 / 6 = 0.333 [0.097, 0.700] |

### False withheld — batch `round5/legacy/batch-2`

| measure | value | of what |
|---|---|---|
| withheld regions reviewed | 30 | every withheld region in the audit sample |
| **FALSE WITHHELD (over-withheld)** | **19 / 30 = 0.633 [0.455, 0.781]** | clean, legible text refused for a reason that did not apply to it |
| safe refusals | 11 | genuinely damaged, ambiguous or figure-dependent |
| unclassifiable | 0 | excluded from the rate, counted here |

Withholding is not automatically safe. A withheld block that leaves a sibling stranded — one option of a multiple-choice, a caption cut from its figure, a hole in an enumerated run — makes what IS served wrong, not merely smaller, and is counted **teaching-critical** (`tool/corpus/legacy/orphan.py`).

| measure | value |
|---|---|
| structures mutilated by withholding | **9** |
| kinds | {'SPLIT_ENUMERATED_RUN': 5, 'SPLIT_CAPTION_SET': 3, 'SPLIT_OPTION_GROUP': 1} |
| **withheld regions that orphan a sibling** | **12 / 139 = 0.086 [0.050, 0.145]** |


### Restore — batch `round5/legacy/batch-2`

**No restore stage ran.** no restore stage ran for this batch — no build change restored a reviewed withheld region, and no REPAIRED stage exists yet `restored`, `falsely-withheld recovered` and `RESTORE PRECISION` are **empty, not zero** — see «What this scoreboard does not say».


### Figure-caption RELATION — batch `round5/legacy/batch-2` (quota sample, within-class only)

Round 4 found captions that are character-perfect and still teach nothing, and had no field to record them (batch-1 report §5a). `figure_relation` is that field.

| measure | value |
|---|---|
| caption blocks judged | 20 |
| verdicts | {'OK': 9, 'NA': 1, 'DETACHED': 10} |
| **detached from their figure** | **10 / 19 = 0.526** |

This is a rate **within the caption class**, from a quota sample. It is never pooled with the stratified rates above.


## Batch `round5/legacy/batch-1-round5` (spec `batch-1`) — pipeline `tc2-p2r` (37 pages, code 90f75e0daffab2cc34b388df8ad4a6e8d0b599b2)

| lesson | risk | state | learning blocks | trusted | withheld | withheld reasons | audited rows |
|---|---|---|---|---|---|---|---|
| Toán 4 tập hai Bài 61 | toan, two_col, formula, order_suspect | **PARTIAL** | 19 | 4 | 15 | {'agree_text': 7, 'agree_order': 5, 'agree_numbers': 3, 'math_guard': 1} | 0 served + 0 withheld |
| Toán 4 tập hai Bài 73 | toan, two_col, formula, attachment_suspect, geometry_rebuilt_expr | **PARTIAL** | 64 | 39 | 25 | {'agree_text': 11, 'agree_order': 7, 'agree_tones': 5, 'agree_numbers': 2} | 0 served + 0 withheld |
| Toán 5 tập một Bài 6 | toan, two_col, formula, geometry_rebuilt_expr | **PARTIAL** | 25 | 12 | 13 | {'math_guard': 3, 'agree_text': 10, 'low_ocr_conf': 1, 'agree_tones': 2, 'agree_numbers': 1} | 0 served + 0 withheld |
| Tiếng Việt 5 tập một Bài 25 | tv5, two_col, order_suspect, attachment_suspect | **PARTIAL** | 85 | 59 | 26 | {'agree_order': 6, 'agree_text': 5, 'line_structure': 7, 'page_feature:diagram': 8, 'page_feature:color_heavy': 1, 'agree_tones': 5} | 0 served + 0 withheld |
| Tiếng Việt 5 tập hai Bài 1 | tv5, two_col, attachment_suspect, role_suspect | **PARTIAL** | 57 | 40 | 17 | {'agree_text': 1, 'agree_order': 8, 'page_feature:color_heavy': 1, 'agree_tones': 7} | 0 served + 0 withheld |
| KHTN 6 Bài 11 | khtn, two_col, figure_caption, role_suspect | **PARTIAL** | 95 | 65 | 30 | {'agree_order': 9, 'agree_numbers': 1, 'agree_tones': 12, 'agree_text': 7, 'figure_dependent': 1} | 0 served + 0 withheld |

### OLD vs NEW false trust per failure class — batch `round5/legacy/batch-1-round5`

rate = WRONG / (OK + WRONG) among **served** rows (what the side actually showed a child), Wilson 95 % · NA / UNSURE excluded and counted beside · no threshold applied.

OLD = not re-sampled for this batch — the product side is unchanged, see the batch it re-runs · NEW = 0 served blocks of the new Trusted Structured Lessons (+ 0 withheld regions reviewed separately). The two sides are different block sets — the comparable quantity is *the share of what each side served that is wrong*.

| failure class | basis | OLD | NEW |
|---|---|---|---|
| display | verdict field | — (n = 0) | — (n = 0) |
| teaching_critical | verdict field | — (n = 0) | — (n = 0) |
| reading_order | verdict field | — (n = 0) | — (n = 0) |
| role | verdict field | — (n = 0) | — (n = 0) |
| attachment | verdict field | — (n = 0) | — (n = 0) |
| formula_number_unit | annotator tag / all judged | — (n = 0) | — (n = 0) |
| formula_number_unit (rows where the class applies) | annotator tag / applicable | — (n = 0) | — (n = 0) |
| figure_caption | annotator tag / all judged | — (n = 0) | — (n = 0) |
| figure_caption (rows where the class applies) | annotator tag / applicable | — (n = 0) | — (n = 0) |

### False withheld — batch `round5/legacy/batch-1-round5`

Withholding is not automatically safe. A withheld block that leaves a sibling stranded — one option of a multiple-choice, a caption cut from its figure, a hole in an enumerated run — makes what IS served wrong, not merely smaller, and is counted **teaching-critical** (`tool/corpus/legacy/orphan.py`).

| measure | value |
|---|---|
| structures mutilated by withholding | **13** |
| kinds | {'SPLIT_OPTION_GROUP': 1, 'OPTIONS_WITHOUT_QUESTION': 1, 'SPLIT_ENUMERATED_RUN': 5, 'SPLIT_CAPTION_SET': 6} |
| **withheld regions that orphan a sibling** | **12 / 126 = 0.095 [0.055, 0.159]** |


### Restore — batch `round5/legacy/batch-1-round5`

Restore mechanism: guard change in the pipeline build — NOT a repair. No REPAIRED stage ran: the repair framework and the math repairer had not landed green.

| measure | value | of what |
|---|---|---|
| reviewed withheld regions | 30 | the withheld regions the earlier audit reviewed |
| **restored** | **6** | of those, served again by this build |
| falsely withheld (earlier audit) | 12 | reviewed regions judged OVER-withheld |
| **falsely-withheld recovered** | **4** | 4 / 12 = 0.333 [0.138, 0.609] |
| restored that the earlier audit called a SAFE refusal | 2 | the dangerous direction — judged fresh, never inherited |
| **RESTORE PRECISION** | **3 / 6 = 0.500 [0.188, 0.812]** | correctly restored / all restored, from a fresh blind judgement of what is served NOW |
| — fresh verdicts | {'CORRECT': 3, 'WRONG': 3} | UNSURE excluded from the precision and counted beside |
| falsely-withheld recovered AND correct | 3 | the only cell that means coverage went up without a new wrong claim |


## What this scoreboard does not say

- It does not say any legacy lesson may be taught. `eligible for teaching` is 0 and stays 0 until the Founder sets a threshold record and authorises teaching.
- It does not compare against the 3,679 / 3,381 denominators as a coverage claim: 243 lessons are in Lane D scope; the rest have never been reprocessed.
- Withheld is not failure. A withheld block is the pipeline refusing to guess — the safe outcome for legacy data.
- Rates are per served block on a small audited sample; the CIs are wide and are shown so they cannot be read as precision.
- An **empty** restore section is not a zero. It means no build change restored a reviewed withheld region and no REPAIRED stage exists yet; a batch with restores states its RESTORE PRECISION, and a restore by a loosened guard is never summed with a restore by a validated repair.
- `restored` counts regions the earlier audit had already reviewed as withheld. It is not the total number of regions this build serves that the previous one did not.

