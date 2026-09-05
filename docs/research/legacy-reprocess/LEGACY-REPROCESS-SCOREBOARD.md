# Legacy reprocess scoreboard — round 4 (Lane D)

`legacy-scoreboard-v1` · generated 2026-09-05T13:53:31+00:00 · source registry `legacy-registry-v1` (aeca24300b8f) · **measurement only — no threshold, no PASS/FAIL**

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
| pending | **237** | in scope, in no batch yet |
| reprocessed (from original source) | **6** | of 243 in scope = 2.5% |
| independently audited | **6** | of 6 reprocessed |
| trusted | **0** | no Founder threshold record at docs/research/legacy-reprocess/THRESHOLDS.json — `trusted` and `eligible for teaching` stay 0 by definition |
| partial (some blocks served, some withheld) | **6** | of 6 reprocessed |
| withheld (nothing servable) | **0** | of 6 reprocessed |
| rejected (pipeline produced no lesson) | **0** | of the lessons attempted |
| **eligible for teaching** | **0** | requires `trusted` ∧ a Founder teaching authorisation |

Full-sourceability lessons (every learning block trusted): 0. Reprocessed lessons outside the registry scope: 0.

## Batch `batch-1` (spec `batch-1`) — pipeline `legacy-b1` (37 pages, code 2e424877508c7f3eded36d5cfb35815798df5cb6)

| lesson | risk | state | learning blocks | trusted | withheld | withheld reasons | audited rows |
|---|---|---|---|---|---|---|---|
| Toán 4 tập hai Bài 61 | toan, two_col, formula, order_suspect | **PARTIAL** | 19 | 9 | 10 | {'agree_text': 7, 'math_guard': 1, 'agree_order': 3} | 9 served + 5 withheld |
| Toán 4 tập hai Bài 73 | toan, two_col, formula, attachment_suspect, geometry_rebuilt_expr | **PARTIAL** | 83 | 67 | 16 | {'agree_text': 11, 'agree_order': 4, 'page_feature:color_heavy': 1, 'page_feature:diagram': 1} | 13 served + 5 withheld |
| Toán 5 tập một Bài 6 | toan, two_col, formula, geometry_rebuilt_expr | **PARTIAL** | 25 | 14 | 11 | {'math_guard': 3, 'agree_text': 10, 'low_ocr_conf': 1} | 12 served + 5 withheld |
| Tiếng Việt 5 tập một Bài 25 | tv5, two_col, order_suspect, attachment_suspect | **PARTIAL** | 85 | 62 | 23 | {'agree_text': 6, 'page_feature:color_heavy': 13, 'page_feature:diagram': 9, 'agree_order': 3} | 13 served + 5 withheld |
| Tiếng Việt 5 tập hai Bài 1 | tv5, two_col, attachment_suspect, role_suspect | **PARTIAL** | 57 | 50 | 7 | {'agree_text': 1, 'page_feature:color_heavy': 3, 'agree_order': 3} | 13 served + 5 withheld |
| KHTN 6 Bài 11 | khtn, two_col, figure_caption, role_suspect | **PARTIAL** | 95 | 85 | 10 | {'agree_text': 7, 'agree_order': 2, 'figure_dependent': 1} | 14 served + 5 withheld |

### OLD vs NEW false trust per failure class — batch `batch-1`

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

## Batch `batch-1-rerun-tc2-p2-preview` (spec `batch-1`) — pipeline `tc2-p2` (37 pages, code origin/lane-a/round4-pipeline-failure-classes@206a103 (expor)

| lesson | risk | state | learning blocks | trusted | withheld | withheld reasons | audited rows |
|---|---|---|---|---|---|---|---|
| Toán 4 tập hai Bài 61 | toan, two_col, formula, order_suspect | **PARTIAL** | 19 | 4 | 15 | {'agree_text': 7, 'agree_order': 5, 'agree_numbers': 3, 'math_guard': 1} | 4 served + 0 withheld |
| Toán 4 tập hai Bài 73 | toan, two_col, formula, attachment_suspect, geometry_rebuilt_expr | **PARTIAL** | 64 | 39 | 25 | {'agree_text': 11, 'agree_order': 7, 'agree_tones': 5, 'agree_numbers': 2} | 6 served + 0 withheld |
| Toán 5 tập một Bài 6 | toan, two_col, formula, geometry_rebuilt_expr | **PARTIAL** | 25 | 12 | 13 | {'math_guard': 3, 'agree_text': 10, 'low_ocr_conf': 1, 'agree_tones': 2, 'agree_numbers': 1} | 11 served + 0 withheld |
| Tiếng Việt 5 tập một Bài 25 | tv5, two_col, order_suspect, attachment_suspect | **PARTIAL** | 85 | 55 | 30 | {'agree_order': 6, 'agree_text': 5, 'page_feature:color_heavy': 13, 'page_feature:diagram': 9, 'agree_tones': 5} | 14 served + 0 withheld |
| Tiếng Việt 5 tập hai Bài 1 | tv5, two_col, attachment_suspect, role_suspect | **PARTIAL** | 57 | 38 | 19 | {'agree_text': 1, 'agree_order': 8, 'page_feature:color_heavy': 3, 'agree_tones': 7} | 9 served + 0 withheld |
| KHTN 6 Bài 11 | khtn, two_col, figure_caption, role_suspect | **PARTIAL** | 95 | 65 | 30 | {'agree_order': 9, 'agree_numbers': 1, 'agree_tones': 12, 'agree_text': 7, 'figure_dependent': 1} | 12 served + 0 withheld |

### OLD vs NEW false trust per failure class — batch `batch-1-rerun-tc2-p2-preview`

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

## What this scoreboard does not say

- It does not say any legacy lesson may be taught. `eligible for teaching` is 0 and stays 0 until the Founder sets a threshold record and authorises teaching.
- It does not compare against the 3,679 / 3,381 denominators as a coverage claim: 243 lessons are in Lane D scope; the rest have never been reprocessed.
- Withheld is not failure. A withheld block is the pipeline refusing to guess — the safe outcome for legacy data.
- Rates are per served block on a small audited sample; the CIs are wide and are shown so they cannot be read as precision.

