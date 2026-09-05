# 113 proven lessons — extractor and TC-v2 trust join (MEASURED, scripts/b_113_join.py)

Baseline 113 by activity type (multi-label): {'EXPERIMENT': 37, 'TOAN_EXERCISE': 10, 'READING': 61, 'WRITING': 41, 'SOURCE': 4}

Extractor per type:
- EXPERIMENT: ocr-body naive line order (build_lesson_index.py Chuẩn bị/Tiến hành scan) = TC-v1 "current-naive", FTR 0.32 on hard pages
- READING: poc-out/units TV5 extractor (extract_units_tv, SECTION_TEXT >=400 chars + numbered EXERCISE) = naive line order
- WRITING: poc-out/units TV5 extractor (EXERCISE "Viết…") = naive line order
- SOURCE: ocr-body naive lines ("TƯ LIỆU" block + attribution) = naive line order
- TOAN_EXERCISE: poc-out/units/exercise-case-map.json (Toán 4-5 fraction expressions; page from footer)

khoaExperiments entries carrying baseline lessons: 49; covered by TC-v2 SDM (six Science books): 44

String-level: {'WITHHELD': 35, 'CONFLICT': 3, 'reason:page_feature:color_heavy': 1, 'reason:agree_order': 3, 'experiments': 44, 'attach_agree': 39, 'attach_disagree': 5, 'xycut_page_trusted': 15, 'xycut_page_untrusted': 29, 'TRUSTED': 164, 'reason:figure_dependent': 7, 'reason:figure_text': 18, 'reason:agree_text': 7, 'reason:empty_block': 2}

Lesson-level (TC-v2-covered): covered 32; all strings matched AND trusted 11; >=1 string WITHHELD/CONFLICT 21; >=1 string unmatched 0; TC-v2 header attachment disagrees with pack lesson 3; experiment page fails WAL-206 XY-cut page gate 22

| book | lesson | pdf page | strings | trusted | withheld | conflict | unmatched | reasons | tc2 lesson (method) | agrees | xycut page trusted |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 04-sgk-khoa-hoc-4 | 1 | 6 | 3 | 0 | 1 | 2 | 0 | {'page_feature:color_heavy': 1, 'agree_order': 2} | 1 (header) | True | False |
| 04-sgk-khoa-hoc-4 | 1 | 11 | 7 | 5 | 2 | 0 | 0 | {'figure_dependent': 1, 'figure_text': 1} | 2 (continuation) | False | True |
| 04-sgk-khoa-hoc-4 | 4 | 18 | 4 | 4 | 0 | 0 | 0 | {} | 4 (header) | True | False |
| 04-sgk-khoa-hoc-4 | 5 | 22 | 3 | 2 | 1 | 0 | 0 | {'figure_dependent': 1} | 5 (header) | True | False |
| 04-sgk-khoa-hoc-4 | 6 | 26 | 5 | 5 | 0 | 0 | 0 | {} | 6 (header) | True | False |
| 04-sgk-khoa-hoc-4 | 6 | 27 | 4 | 4 | 0 | 0 | 0 | {} | 6 (continuation) | True | True |
| 04-sgk-khoa-hoc-4 | 8 | 33 | 5 | 5 | 0 | 0 | 0 | {} | 8 (continuation) | True | True |
| 04-sgk-khoa-hoc-4 | 10 | 41 | 4 | 3 | 1 | 0 | 0 | {'figure_dependent': 1} | 10 (continuation) | True | True |
| 04-sgk-khoa-hoc-4 | 12 | 46 | 5 | 4 | 1 | 0 | 0 | {'figure_dependent': 1} | 12 (header) | True | True |
| 04-sgk-khoa-hoc-4 | 12 | 48 | 5 | 4 | 1 | 0 | 0 | {'figure_text': 1} | 12 (continuation) | True | True |
| 04-sgk-khoa-hoc-4 | 13 | 49 | 4 | 3 | 1 | 0 | 0 | {'figure_dependent': 1} | 13 (header) | True | True |
| 05-sgk-khoa-hoc-5 | 1 | 6 | 4 | 3 | 0 | 1 | 0 | {'agree_order': 1} | 1 (header) | True | True |
| 05-sgk-khoa-hoc-5 | 3 | 17 | 7 | 7 | 0 | 0 | 0 | {} | 3 (continuation) | True | True |
| 05-sgk-khoa-hoc-5 | 3 | 20 | 6 | 5 | 1 | 0 | 0 | {'agree_text': 1} | 4 (continuation) | False | True |
| 05-sgk-khoa-hoc-5 | 5 | 22 | 4 | 2 | 2 | 0 | 0 | {'agree_text': 1, 'figure_text': 1} | 5 (header) | True | False |
| 05-sgk-khoa-hoc-5 | 14 | 57 | 5 | 5 | 0 | 0 | 0 | {} | 14 (continuation) | True | False |
| 06-sgk-khoa-hoc-tu-nhien-6 | 11 | 39 | 5 | 3 | 2 | 0 | 0 | {'figure_text': 2} | 11 (continuation) | True | False |
| 06-sgk-khoa-hoc-tu-nhien-6 | 46 | 164 | 3 | 2 | 1 | 0 | 0 | {'figure_dependent': 1} | 46 (continuation) | True | False |
| 06-sgk-khoa-hoc-tu-nhien-6 | 48 | 170 | 4 | 2 | 2 | 0 | 0 | {'figure_text': 1, 'agree_text': 1} | 48 (continuation) | True | False |
| 06-sgk-khoa-hoc-tu-nhien-6 | 50 | 176 | 4 | 2 | 2 | 0 | 0 | {'figure_dependent': 1, 'figure_text': 1} | 50 (continuation) | True | True |
| 07-sgk-khoa-hoc-tu-nhien-7 | 16 | 80 | 3 | 3 | 0 | 0 | 0 | {} | 16 (continuation) | True | False |
| 08-sgk-khoa-hoc-tu-nhien-8 | 5 | 25 | 4 | 4 | 0 | 0 | 0 | {} | 5 (header) | True | True |
| 08-sgk-khoa-hoc-tu-nhien-8 | 7 | 33 | 7 | 5 | 2 | 0 | 0 | {'agree_text': 2} | 7 (continuation) | True | False |
| 08-sgk-khoa-hoc-tu-nhien-8 | 7 | 34 | 7 | 7 | 0 | 0 | 0 | {} | 7 (continuation) | True | False |
| 08-sgk-khoa-hoc-tu-nhien-8 | 15 | 66 | 5 | 5 | 0 | 0 | 0 | {} | 15 (continuation) | True | False |
| 08-sgk-khoa-hoc-tu-nhien-8 | 16 | 68 | 3 | 1 | 2 | 0 | 0 | {'figure_text': 1, 'agree_text': 1} | 16 (header) | True | True |
| 08-sgk-khoa-hoc-tu-nhien-8 | 22 | 100 | 5 | 4 | 1 | 0 | 0 | {'empty_block': 1} | 24 (header) | False | True |
| 08-sgk-khoa-hoc-tu-nhien-8 | 22 | 101 | 5 | 5 | 0 | 0 | 0 | {} | 24 (continuation) | False | False |
| 08-sgk-khoa-hoc-tu-nhien-8 | 22 | 116 | 5 | 5 | 0 | 0 | 0 | {} | 28 (continuation) | False | False |
| 09-sgk-khoa-hoc-tu-nhien-9 | 5 | 26 | 5 | 5 | 0 | 0 | 0 | {} | 5 (header) | True | False |
| 09-sgk-khoa-hoc-tu-nhien-9 | 5 | 27 | 4 | 3 | 1 | 0 | 0 | {'figure_text': 1} | 5 (continuation) | True | False |
| 09-sgk-khoa-hoc-tu-nhien-9 | 5 | 28 | 4 | 3 | 1 | 0 | 0 | {'figure_text': 1} | 5 (continuation) | True | False |
| 09-sgk-khoa-hoc-tu-nhien-9 | 8 | 43 | 6 | 6 | 0 | 0 | 0 | {} | 8 (continuation) | True | False |
| 09-sgk-khoa-hoc-tu-nhien-9 | 12 | 63 | 3 | 2 | 1 | 0 | 0 | {'agree_text': 1} | 12 (continuation) | True | False |
| 09-sgk-khoa-hoc-tu-nhien-9 | 14 | 68 | 4 | 4 | 0 | 0 | 0 | {} | 14 (header) | True | False |
| 09-sgk-khoa-hoc-tu-nhien-9 | 14 | 69 | 4 | 3 | 1 | 0 | 0 | {'empty_block': 1} | 14 (continuation) | True | False |
| 09-sgk-khoa-hoc-tu-nhien-9 | 14 | 70 | 4 | 4 | 0 | 0 | 0 | {} | 14 (continuation) | True | False |
| 09-sgk-khoa-hoc-tu-nhien-9 | 19 | 93 | 4 | 4 | 0 | 0 | 0 | {} | 19 (header) | True | False |
| 09-sgk-khoa-hoc-tu-nhien-9 | 19 | 94 | 3 | 2 | 1 | 0 | 0 | {'figure_text': 1} | 19 (continuation) | True | False |
| 09-sgk-khoa-hoc-tu-nhien-9 | 23 | 110 | 5 | 5 | 0 | 0 | 0 | {} | 23 (continuation) | True | False |
| 09-sgk-khoa-hoc-tu-nhien-9 | 24 | 113 | 5 | 5 | 0 | 0 | 0 | {} | 24 (continuation) | True | False |
| 09-sgk-khoa-hoc-tu-nhien-9 | 26 | 120 | 3 | 0 | 3 | 0 | 0 | {'figure_text': 3} | 26 (continuation) | True | False |
| 09-sgk-khoa-hoc-tu-nhien-9 | 29 | 133 | 6 | 6 | 0 | 0 | 0 | {} | 29 (continuation) | True | False |
| 09-sgk-khoa-hoc-tu-nhien-9 | 30 | 137 | 7 | 3 | 4 | 0 | 0 | {'figure_text': 4} | 30 (continuation) | True | True |
