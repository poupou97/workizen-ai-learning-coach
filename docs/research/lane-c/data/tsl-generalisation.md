# TSL generalisation audit — Bài 17 abstractions × 238 Science TSLs (MEASURED)

Denominator: 238 / 238 repaired-ranged lessons, six Science books · TC-v2 tc2-p1 · subset: TSLs on disk. Generator rules imported from `tool/fixtures/make_lesson_fixture.py` unchanged.

| question | value |
|---|---|
| lessons whose trusted blocks ALL map onto Bài 17 block kinds | 178 / 238 |
| trusted blocks the generator would drop as «vai trò lạ» | 118 / 11971 (1.0 %) — by role {'activity': 50, 'footnote': 64, 'option': 4} |
| lessons with a `table` role block · table blocks carrying `cells` | 12 · 0 / 20 |
| lessons showing every Bài 17 kind (heading, body, question, caption, instruction, objective, sidebar, stage label) | 76 / 238 |
| lessons with ≥1 instruction block (Process precondition) | 96 / 238 |
| lessons where `tsl-enumerated-steps-v1` yields ≥1 Process · with ≥2 steps | 68 · 60 / 238 |
| lessons with an instruction block but NO derivable Process | 28 |
| process step-count histogram (steps → processes; 6 = ≥6) | {1: 34, 2: 58, 3: 37, 4: 18, 5: 9, 6: 25} |
| processes containing a withheld step | 30 / 181 |
| lessons with an «Em đã học» stage label · where `tsl-summary-parenthesis-v1` yields ≥1 row | 209 · 6 / 238 |
| withheld regions by reason | {'agree_text': 824, 'figure_dependent': 632, 'agree_order': 224, 'page_feature:diagram': 197, 'page_feature:color_heavy': 95, 'box_boundary': 92, 'math_guard': 41, 'answer_leak': 29, 'low_ocr_conf': 19, 'role_conflict': 7} |
| withheld that are diagram / math / colour / figure-dependent | 44.7 % of 2160 |
| lessons whose withheld regions are ONLY visual/math (the Bài 17 case) | 11 / 236 with any withheld |
| lessons with an `agree_text` / `agree_order` withheld region (a text disagreement, not a diagram) | 222 / 238 |
| trusted question blocks | 1642 — enumerated 70.2 % · ends with «?» 50.8 % · mentions «hình N» 0.0 % · «quan sát» 5.7 % · MCQ-shaped 0.0 % |
| WITHHELD question regions · of which `figure_dependent` | 648 · 561 — 28.3 % of all question regions never reach the TSL text; lessons with ≥1 such question: 188 / 238 |
| withheld table regions · withheld model-answer regions | 174 · 29 |
| figures · with a caption link · kept by the ≥3 % / caption rule | 3864 · 33.6 % · 42.3 % (lessons with 0 kept figures: 1) |
| boundary from a printed header · source · confidence | 238 / 238 · {'both': 168, 'header': 70} · {'0.95': 161, '0.85': 71, '0.6': 3, '0.77': 1, '0.8': 2} |
| pages per lesson (9 = ≥9) · sourceability | {2: 15, 3: 60, 4: 67, 5: 48, 6: 25, 7: 8, 8: 7, 9: 8} · {'PARTIAL': 236, 'FULL': 2} |
| Next-Action rule 1 (Trực quan first) reachable | 68 / 238 lessons |
| Next-Action rule 3 (Học với SAM) reachable | 1 / 238 — tutor_script_bai17() returns None for every TSL except KHTN 6 Bài 17 (MEASURED in the generator source) |

## Per book

| book | lessons | Process | Comparison | unmapped block | table | withheld only visual/math |
|---|---|---|---|---|---|---|
| 04-sgk-khoa-hoc-4 | 31 | 5 | 0 | 2 | 1 | 2 |
| 05-sgk-khoa-hoc-5 | 30 | 5 | 0 | 1 | 1 | 3 |
| 06-sgk-khoa-hoc-tu-nhien-6 | 53 | 13 | 6 | 16 | 4 | 1 |
| 07-sgk-khoa-hoc-tu-nhien-7 | 33 | 6 | 0 | 10 | 2 | 1 |
| 08-sgk-khoa-hoc-tu-nhien-8 | 42 | 22 | 0 | 16 | 3 | 1 |
| 09-sgk-khoa-hoc-tu-nhien-9 | 49 | 17 | 0 | 15 | 1 | 3 |

Reading rules: a lesson «has a Process» when the generator rule returns ≥1 process with ≥1 step; «unmapped» blocks are trusted blocks with a role outside the generator's `to_block` mapping (they would vanish from the Smart Book silently — the generator only logs them).
