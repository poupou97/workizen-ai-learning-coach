# LS&ĐL 5 Bài 8 — round-4 vs round-5 pipeline (Lane C, round 5)

Same book, same CLIs, **same raw OCR candidate files** (round 4's) — every difference is pipeline code (sdm-v2 → sdm-v3). Verbatim verdicts come from a human read of the printed renders (51 blocks, 2026-09-06), not from stack agreement.

## Book (28 lessons of LS&ĐL 5)

| measure | round 4 | round 5 |
|---|---|---|
| lessons with a TSL | 23 | 28 |
| learning blocks | 1483 | 1472 |
| trusted | 1263 | 1020 |
| withheld | 220 | 452 |

**Withheld by reason (book):**

| reason | round 4 | round 5 |
|---|---|---|
| agree_numbers | 0 | 22 |
| agree_order | 21 | 63 |
| agree_text | 115 | 113 |
| agree_tones | 0 | 179 |
| box_boundary | 19 | 19 |
| chem_guard | 0 | 1 |
| figure_dependent | 39 | 58 |
| line_structure | 0 | 4 |
| low_ocr_conf | 1 | 1 |
| page_feature:color_heavy | 23 | 10 |
| page_feature:diagram | 12 | 11 |

## Bài 8

| measure | round 4 | round 5 |
|---|---|---|
| boundary | 38–41 conf 0.95 (both) | 38–41 conf 0.95 (both) |
| learning blocks | 51 | 51 |
| trusted | 34 | 36 |
| withheld | 17 | 15 |
| roles trusted | {"heading": 8, "stage_label": 5, "body": 14, "question": 4, "caption": 3} | {"heading": 5, "objective": 1, "body": 15, "stage_label": 5, "question": 3, "attribution": 4, "caption": 3} |
| withheld by reason | {"page_feature:color_heavy": 14, "agree_text": 3, "agree_order": 2, "box_boundary": 1} | {"agree_tones": 7, "page_feature:color_heavy": 4, "agree_text": 3, "figure_dependent": 1, "box_boundary": 1, "agree_order": 1} |

### Newly trusted (10)

| block | role |
|---|---|
| p038:tc2-p1:005 | objective |
| p038:tc2-p1:006 | body |
| p038:tc2-p1:010 | question |
| p038:tc2-p1:011 | body |
| p038:tc2-p1:012 | body |
| p038:tc2-p1:013 | body |
| p038:tc2-p1:014 | body |
| p038:tc2-p1:015 | attribution |
| p039:tc2-p1:007 | body |
| p039:tc2-p1:008 | body |

### Newly withheld (8)

| block | role | reasons |
|---|---|---|
| p038:tc2-p1:003 | heading | agree_tones |
| p038:tc2-p1:018 | heading | agree_tones |
| p039:tc2-p1:000 | body | agree_tones |
| p039:tc2-p1:003 | question | figure_dependent |
| p039:tc2-p1:009 | heading | agree_tones |
| p041:tc2-p1:001 | body | agree_tones |
| p041:tc2-p1:006 | question | agree_order |
| p041:tc2-p1:021 | question | agree_tones |

## Verbatim scoreboard (denominator: the 51 Bài 8 learning blocks the human read judged)

| cell | round 4 | round 5 |
|---|---|---|
| correct_served | 26 | 30 |
| FALSE_TRUST | 8 | 6 |
| FALSE_WITHHELD | 14 | 10 |
| correct_withheld | 3 | 5 |

### Round 5 — every judged block

| block | status | role | reasons | print verdict | cell | slips |
|---|---|---|---|---|---|---|
| p038:tc2-p1:002 | TRUSTED | heading |  | verbatim | correct_served |  |
| p038:tc2-p1:003 | WITHHELD | heading | agree_tones | slip | correct_withheld | ĐẦU→ĐẤU; KĨ→KÌ |
| p038:tc2-p1:004 | TRUSTED | heading |  | verbatim | correct_served |  |
| p038:tc2-p1:005 | TRUSTED | objective |  | verbatim_glyph | correct_served |  |
| p038:tc2-p1:006 | TRUSTED | body |  | slip | FALSE_TRUST | tẩm→tầm |
| p038:tc2-p1:009 | TRUSTED | stage_label |  | verbatim | correct_served |  |
| p038:tc2-p1:010 | TRUSTED | question |  | verbatim | correct_served |  |
| p038:tc2-p1:011 | TRUSTED | body |  | verbatim | correct_served |  |
| p038:tc2-p1:012 | TRUSTED | body |  | verbatim | correct_served |  |
| p038:tc2-p1:013 | TRUSTED | body |  | verbatim | correct_served |  |
| p038:tc2-p1:014 | TRUSTED | body |  | verbatim | correct_served |  |
| p038:tc2-p1:015 | TRUSTED | attribution |  | verbatim | correct_served |  |
| p038:tc2-p1:017 | TRUSTED | stage_label |  | verbatim | correct_served |  |
| p038:tc2-p1:018 | WITHHELD | heading | agree_tones | slip | correct_withheld | đầu→đấu |
| p038:tc2-p1:020 | WITHHELD | question | page_feature:color_heavy | verbatim_glyph | FALSE_WITHHELD |  |
| p038:tc2-p1:021 | WITHHELD | question | page_feature:color_heavy | verbatim_glyph | FALSE_WITHHELD |  |
| p038:tc2-p1:022 | WITHHELD | question | page_feature:color_heavy | verbatim_glyph | FALSE_WITHHELD |  |
| p038:tc2-p1:023 | WITHHELD | body | agree_text | verbatim | FALSE_WITHHELD |  |
| p038:tc2-p1:024 | WITHHELD | body | agree_text | verbatim | FALSE_WITHHELD |  |
| p038:tc2-p1:026 | TRUSTED | stage_label |  | verbatim | correct_served |  |
| p038:tc2-p1:027 | WITHHELD | sidebar | agree_text,page_feature:color_heavy | verbatim_glyph | FALSE_WITHHELD |  |
| p039:tc2-p1:000 | WITHHELD | body | agree_tones | verbatim_glyph | FALSE_WITHHELD |  |
| p039:tc2-p1:001 | TRUSTED | heading |  | slip | FALSE_TRUST | đầu→đấu |
| p039:tc2-p1:003 | WITHHELD | question | figure_dependent | verbatim | FALSE_WITHHELD |  |
| p039:tc2-p1:004 | TRUSTED | question |  | verbatim_glyph | correct_served |  |
| p039:tc2-p1:005 | TRUSTED | body |  | verbatim_glyph | correct_served |  |
| p039:tc2-p1:006 | TRUSTED | body |  | verbatim_glyph | correct_served |  |
| p039:tc2-p1:007 | TRUSTED | body |  | verbatim | correct_served |  |
| p039:tc2-p1:008 | TRUSTED | body |  | slip | FALSE_TRUST | Lích→Lịch |
| p039:tc2-p1:009 | WITHHELD | heading | agree_tones | slip | correct_withheld | TRỮ→TRỪ; HÂN→HÁN |
| p039:tc2-p1:010 | TRUSTED | body |  | verbatim_glyph | correct_served |  |
| p039:tc2-p1:011 | TRUSTED | body |  | verbatim_glyph | correct_served |  |
| p039:tc2-p1:012 | TRUSTED | body |  | verbatim | correct_served |  |
| p039:tc2-p1:013 | TRUSTED | attribution |  | verbatim | correct_served |  |
| p039:tc2-p1:015 | TRUSTED | caption |  | verbatim_glyph | correct_served |  |
| p040:tc2-p1:002 | TRUSTED | heading |  | slip | FALSE_TRUST | BĨ→BÍ |
| p040:tc2-p1:003 | WITHHELD | body | agree_tones,box_boundary | slip | correct_withheld | triểu→triều |
| p040:tc2-p1:004 | TRUSTED | body |  | verbatim | correct_served |  |
| p040:tc2-p1:005 | TRUSTED | attribution |  | verbatim | correct_served |  |
| p040:tc2-p1:007 | TRUSTED | caption |  | verbatim_glyph | correct_served |  |
| p040:tc2-p1:008 | TRUSTED | heading |  | slip | FALSE_TRUST | PHẢ→PHÁ; HÃN→HÁN |
| p040:tc2-p1:011 | TRUSTED | body |  | verbatim_glyph | correct_served |  |
| p041:tc2-p1:000 | TRUSTED | body |  | verbatim | correct_served |  |
| p041:tc2-p1:001 | WITHHELD | body | agree_tones | verbatim | FALSE_WITHHELD |  |
| p041:tc2-p1:002 | TRUSTED | attribution |  | slip | FALSE_TRUST | Đăng→Đằng; hóa→hoá |
| p041:tc2-p1:004 | TRUSTED | stage_label |  | verbatim | correct_served |  |
| p041:tc2-p1:005 | TRUSTED | question |  | verbatim | correct_served |  |
| p041:tc2-p1:006 | WITHHELD | question | agree_order | verbatim | FALSE_WITHHELD |  |
| p041:tc2-p1:020 | TRUSTED | stage_label |  | verbatim | correct_served |  |
| p041:tc2-p1:021 | WITHHELD | question | agree_tones | slip | correct_withheld | hiếu→hiểu |
| p041:tc2-p1:023 | TRUSTED | caption |  | verbatim_glyph | correct_served |  |
