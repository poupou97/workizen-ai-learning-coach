# Subject-family census (MEASURED unless marked)

Denominators: canonical lessons = `lessonCount` per SGK book (sums to 3,679 corpus-wide); ranged = lessons with a TOC `pageStart`; pages = SGK pages in the TC-v1 census; units = units-k12 SGK units with a lesson (old extractor). Pattern labels are the WAL-203 registry labels on old-extractor units — they rank shapes, they do not size them (TC-15).

| family | books | canonical | ranged | TOC OK / PARTIAL / NO_TOC | missing pageStart | labelled lessons | top patterns (unique lessons) |
|---|---|---|---|---|---|---|---|
| science | 17 | 499 | 473 | 10 / 7 / 0 | 26 | 233 | EXPLAIN_SHORT 181, OBSERVE 97, EXPERIMENT 61, ORAL_SHARE 47, RESEARCH_PROJECT 45, DRAW_CREATE 36 |
| history_geo | 12 | 238 | 205 | 4 / 7 / 1 | 33 | 120 | EXPLAIN_SHORT 76, RESEARCH_PROJECT 49, DIAGRAM_COMPLETE 48, SOURCE_REASONING 26, OBSERVE 26, ORAL_SHARE 24 |
| math | 18 | 377 | 358 | 11 / 7 / 0 | 19 | 47 | SELECT_MCQ 24, COMPUTE_SOLVE 15, DRAW_CREATE 12, EXPLAIN_SHORT 12, HANDS_ON_TOOL 6, RESEARCH_PROJECT 4 |
| language | 18 | 182 | 157 | 11 / 6 / 1 | 25 | 76 | EXPLAIN_SHORT 76, READ_TEXT 73, ORAL_SHARE 57, WRITE_TEXT 48, SELECT_MCQ 28, FILL_BLANK 22 |
| informatics | 9 | 201 | 184 | 5 / 4 / 0 | 17 | 129 | EXPLAIN_SHORT 70, SELECT_MCQ 65, DRAW_CREATE 44, RESEARCH_PROJECT 34, HANDS_ON_TOOL 32, ORAL_SHARE 25 |
| english | 12 | 103 | 78 | 8 / 4 / 0 | 25 | 75 | SELECT_MCQ 75, FILL_BLANK 6 |
| primary_1_3 | 45 | 688 | 665 | 23 / 6 / 16 | 23 | 250 | ORAL_SHARE 122, EXPLAIN_SHORT 95, OBSERVE 73, AUDIO_PERFORM 73, READ_TEXT 72, DICTATION 59 |
| other | 170 | 1391 | 1261 | 89 / 36 / 45 | 130 | 557 | EXPLAIN_SHORT 364, OBSERVE 133, RESEARCH_PROJECT 129, DRAW_CREATE 119, ORAL_SHARE 98, READ_TEXT 63 |

## Layout hard features on SGK pages (% of the family's pages; overlapping)

| family | pages | formula | table | diagram | sidebar | side-by-side | colour-heavy | figure | coloured box | no unhandled feature |
|---|---|---|---|---|---|---|---|---|---|---|
| science | 2730 | 17.4 | 10.6 | 34.5 | 46.8 | 42.4 | 3.3 | 59.0 | 35.1 | 46.7 |
| history_geo | 1856 | 10.8 | 19.0 | 28.9 | 43.4 | 45.9 | 4.3 | 64.1 | 41.8 | 60.9 |
| math | 2197 | 55.5 | 19.1 | 33.5 | 52.7 | 61.3 | 6.2 | 44.2 | 35.2 | 19.8 |
| language | 2668 | 0.3 | 2.9 | 7.8 | 30.7 | 23.6 | 5.6 | 30.7 | 24.4 | 85.9 |
| informatics | 1003 | 17.3 | 18.8 | 27.4 | 49.4 | 56.4 | 2.3 | 43.1 | 37.5 | 51.5 |
| english | 1325 | 1.1 | 18.6 | 72.0 | 11.2 | 85.1 | 7.8 | 76.2 | 54.2 | 19.7 |
| primary_1_3 | 4601 | 5.5 | 10.0 | 45.6 | 12.0 | 41.8 | 21.2 | 89.3 | 68.6 | 40.5 |
| other | 13563 | 6.7 | 8.3 | 27.2 | 23.8 | 33.3 | 8.9 | 65.9 | 37.8 | 59.2 |

## Lexical shape markers in activity units (% of units; HYPOTHESIS — a marker says the unit points at a shape, not that the shape is extractable)

| family | units | timeline_year | source_text | map_spatial | figure_ref | table_ref | process_steps | compare | cause_why | definition | math_ops | write | read_aloud | mcq_options | blank | oral |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| science | 4611 | 4.4 | 0.4 | 0.2 | 32.6 | 5.3 | 6.9 | 11.5 | 14.3 | 7.5 | 6.2 | 0.9 | 0.1 | 0.9 | 3.1 | 11.4 |
| history_geo | 2666 | 33.8 | 14.4 | 12.8 | 35.5 | 3.2 | 0.4 | 7.3 | 16.2 | 3.5 | 19.2 | 2.3 | 0.1 | 0.0 | 7.0 | 11.3 |
| math | 1431 | 8.7 | 4.5 | 0.2 | 27.7 | 2.1 | 5.3 | 8.5 | 8.9 | 9.8 | 33.3 | 0.4 | 0.0 | 3.3 | 2.2 | 10.0 |
| language | 4171 | 10.2 | 7.3 | 0.7 | 0.1 | 0.2 | 1.6 | 9.0 | 18.1 | 6.4 | 11.7 | 9.7 | 4.7 | 1.3 | 4.4 | 25.6 |
| informatics | 2489 | 6.4 | 1.7 | 0.4 | 25.2 | 3.6 | 8.2 | 9.2 | 6.5 | 6.0 | 8.2 | 1.3 | 0.2 | 6.5 | 3.4 | 11.5 |
| english | 5756 | 2.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 3.2 | 0.0 | 0.0 | 15.9 | 0.5 | 0.1 |
| primary_1_3 | 3660 | 2.8 | 6.0 | 0.1 | 3.2 | 0.9 | 1.5 | 2.7 | 9.8 | 1.6 | 10.1 | 2.2 | 1.3 | 2.2 | 1.7 | 23.5 |
| other | 12043 | 7.8 | 2.3 | 0.2 | 18.9 | 2.1 | 6.9 | 7.0 | 9.5 | 3.9 | 9.3 | 0.8 | 0.0 | 0.5 | 4.1 | 9.2 |

## TC-v2 gold pages outside the Science slice (the only measured trust numbers there; n is tiny)

| family | page | trusted | false-trusted | TLSR | FTR | question P (gold n) | order | text acc | meaning inversions | lesson attach |
|---|---|---|---|---|---|---|---|---|---|---|
| history_geo | 05-sgk-lich-su-va-dia-li-5 p041 | 9 | 0 | 1.0 | 0.0 | 1.0 (3) | 0.972 | 0.9983 | 0 | WRONG (toc=8, gold=9) |
| history_geo | 05-sgk-lich-su-va-dia-li-5 p080 | 5 | 0 | 1.0 | 0.0 | 1.0 (1) | 0.955 | 0.9983 | 0 | WRONG (toc=15, gold=17) |
| history_geo | 07-sgk-lich-su-va-dia-li-7 p094 | 7 | 0 | 0.5 | 0.0 | None (1) | 1.0 | 0.9782 | 0 | WRONG (toc=16, gold=18) |
| history_geo | 08-sgk-lich-su-va-dia-li-8 p071 | 7 | 0 | 0.778 | 0.0 | 1.0 (2) | 1.0 | 0.9745 | 0 | OK |
| history_geo | 10-sgk-dia-li-10 p040 | 11 | 2 | 0.818 | 0.182 | 1.0 (1) | 1.0 | 0.8747 | 0 | OK |
| history_geo | 10-sgk-dia-li-10 p115 | 1 | 0 | 1.0 | 0.0 | None (0) | 1.0 | 1.0 | 0 | gold=none (TOC attaches 31 → WRONG) |
| math | 05-sgk-toan-5-tap-mot p021 | 3 | 1 | 0.133 | 0.333 | None (0) | 0.855 | 0.7759 | 9 | OK |
| math | 05-sgk-toan-5-tap-mot p092 | 9 | 2 | 0.5 | 0.222 | None (0) | 1.0 | 0.9649 | 0 | OK |
| math | 07-sgk-toan-7-tap-hai p041 | 8 | 1 | 0.467 | 0.125 | 0.5 (3) | 1.0 | 0.9661 | 0 | OK |
| math | 09-sgk-toan-9-tap-mot p029 | 10 | 9 | 0.067 | 0.9 | 0.0 (5) | 0.903 | 0.9668 | 10 | OK |
| math | 12-sgk-toan-12-tap-hai p020 | 8 | 4 | 0.286 | 0.5 | None (1) | 0.938 | 0.9115 | 3 | OK |
| language | 04-sgk-tieng-viet-4-tap-mot p028 | 15 | 2 | 0.812 | 0.133 | 1.0 (7) | 0.993 | 0.9727 | 1 | WRONG (toc=5, gold=6) |
| language | 05-sgk-tieng-viet-5-tap-hai p008 | 0 | 0 | 0.0 | None | None (0) | 1.0 | 1.0 | 0 | gold=none (TOC attaches none → OK) |
| language | 06-sgk-ngu-van-6-tap-mot p021 | 9 | 0 | 0.692 | 0.0 | 1.0 (6) | 1.0 | 0.9906 | 0 | OK |
| language | 08-sgk-ngu-van-8-tap-mot p038 | 15 | 1 | 0.933 | 0.067 | 0.0 (0) | 1.0 | 0.993 | 0 | WRONG (toc=1, gold=2) |
| language | 09-sgk-ngu-van-9-tap-mot p067 | 12 | 0 | 0.75 | 0.0 | 1.0 (1) | 1.0 | 0.9867 | 0 | OK |
| language | 09-sgk-ngu-van-9-tap-mot p083 | 13 | 0 | 0.812 | 0.0 | 1.0 (4) | 1.0 | 0.9892 | 0 | OK |
| language | 11-sgk-ngu-van-11-tap-mot p039 | 4 | 0 | 0.4 | 0.0 | 1.0 (1) | 1.0 | 0.9982 | 0 | OK |
| informatics | 06-sgk-tin-hoc-6 p021 | 9 | 0 | 0.6 | 0.0 | 1.0 (2) | 1.0 | 0.9522 | 0 | OK |
| informatics | 09-sgk-tin-hoc-9 p020 | 14 | 4 | 0.667 | 0.286 | 1.0 (5) | 1.0 | 0.9937 | 0 | OK |
| primary_1_3 | 01-sgk-tu-nhien-va-xa-hoi-1 p006 | 0 | 0 | 0.0 | None | None (0) | 1.0 | 1.0 | 0 | gold=none (TOC attaches none → OK) |
| primary_1_3 | 02-sgk-tieng-viet-2-tap-hai p014 | 10 | 0 | 0.769 | 0.0 | 1.0 (8) | 1.0 | 0.8626 | 0 | WRONG (toc=1, gold=2) |
| primary_1_3 | 02-sgk-tieng-viet-2-tap-mot p103 | 14 | 1 | 0.867 | 0.071 | 1.0 (8) | 1.0 | 0.9577 | 0 | OK |
| primary_1_3 | 02-sgk-toan-2-tap-hai p048 | 1 | 0 | 0.067 | 0.0 | None (1) | 1.0 | 0.871 | 0 | OK |
| primary_1_3 | 03-sgk-toan-3-tap-mot p032 | 1 | 0 | 0.1 | 0.0 | None (1) | 0.925 | 0.8618 | 5 | OK |
| sgv | 04-sgv-khoa-hoc-4 p028 | 5 | 0 | 0.357 | 0.0 | None (3) | 1.0 | 0.9982 | 0 | OK |
| sgv | 04-sgv-toan-4 p054 | 8 | 0 | 0.615 | 0.0 | None (0) | 1.0 | 0.9936 | 0 | OK |
| sgv | 06-sgv-khoa-hoc-tu-nhien-6 p005 | 0 | 0 | 0.0 | None | None (0) | 1.0 | 1.0 | 0 | gold=none (TOC attaches none → OK) |
| sgv | 06-sgv-khoa-hoc-tu-nhien-6 p071 | 5 | 4 | 0.05 | 0.8 | None (2) | 0.909 | 0.9777 | 6 | OK |
| sgv | 07-sgv-khoa-hoc-tu-nhien-7 p168 | 9 | 0 | 0.562 | 0.0 | None (1) | 1.0 | 0.9582 | 0 | WRONG (toc=33, gold=34) |
| sgv | 07-sgv-toan-7 p043 | 2 | 0 | 1.0 | 0.0 | None (0) | 1.0 | 0.9902 | 0 | WRONG (toc=None, gold=6) |
| sgv | 09-sgv-khoa-hoc-tu-nhien-9 p136 | 6 | 0 | 0.462 | 0.0 | None (0) | 1.0 | 0.992 | 0 | WRONG (toc=14, gold=19) |
| sgv | 10-sgv-tin-hoc-10 p039 | 10 | 0 | 0.556 | 0.0 | None (0) | 1.0 | 0.9763 | 0 | gold=none (TOC attaches 5 → WRONG) |

## SGV availability and pack wiring

| family | SGK books with an SGV units file | SGK lessons with SGV markers | …with answer/expected marker | …with objective marker | pack entries | lessons with any pack entry |
|---|---|---|---|---|---|---|
| science | 14 / 17 | 343 | 113 | 307 | khoaExperiments 46 | 37 |
| history_geo | 12 / 12 | 154 | 47 | 149 | suSources 4, diaMaps 1 | 5 |
| math | 18 / 18 | 105 | 79 | 105 | — | 0 |
| language | 18 / 18 | 32 | 2 | 31 | tvReadings 66, tvWritings 54 | 60 |
| informatics | 7 / 9 | 168 | 77 | 162 | — | 0 |
| english | 9 / 12 | 0 | 0 | 0 | — | 0 |
| primary_1_3 | 39 / 45 | 54 | 20 | 52 | — | 0 |
| other | 115 / 170 | 154 | 111 | 152 | — | 0 |
