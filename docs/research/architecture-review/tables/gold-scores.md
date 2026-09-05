# TC-v2 pipeline tc2-p1 on the gold set (MEASURED)

| set | pages | learning blk | trusted (cov) | TLSR | false trusted | FTR | safe rej | found | order | inv | text acc | CER no-tone | fidelity | splices | CTE | CTE pages | attach TOC ok | attach header ok |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 54 | 643 | 439 (0.683) | 0.605 | 50 | 0.1139 | 188 | 0.979 | 0.985 | 44 | 0.969 | 0.027 | 0.976 | 10 | 89 | 28 | 37/54 | 43/54 |
| dev | 38 | 462 | 323 (0.699) | 0.621 | 36 | 0.1115 | 125 | 0.978 | 0.984 | 31 | 0.964 | 0.031 | 0.975 | 8 | 71 | 22 | 28/38 | 28/38 |
| heldout | 16 | 181 | 116 (0.641) | 0.564 | 14 | 0.1207 | 63 | 0.982 | 0.986 | 13 | 0.981 | 0.017 | 0.979 | 2 | 18 | 6 | 9/16 | 15/16 |
| science | 23 | 269 | 190 (0.706) | 0.636 | 19 | 0.1000 | 77 | 0.985 | 0.987 | 15 | 0.982 | 0.015 | 0.987 | 3 | 27 | 10 | 15/23 | 22/23 |
| science_sgk | 18 | 205 | 165 (0.805) | 0.732 | 15 | 0.0909 | 39 | 0.983 | 0.989 | 9 | 0.981 | 0.015 | 0.983 | 3 | 21 | 9 | 12/18 | 18/18 |
| sgv | 8 | 97 | 45 (0.464) | 0.423 | 4 | 0.0889 | 50 | 0.988 | 0.989 | 6 | 0.986 | 0.012 | 1.000 | 0 | 7 | 2 | 4/8 | 4/8 |

## Role Layer — precision / recall per role (matched blocks; "(n)" = gold blocks of that role)

### all (54 pages) — trusted-QUESTION precision 0.917 (n=84)
| role | precision | recall | tp | predicted | gold |
|---|---|---|---|---|---|
| **QUESTION** | 0.882 | 0.776 | 90 | 102 | 116 |
| **ANSWER** | 0.800 | 0.267 | 4 | 5 | 15 |
| **ACTIVITY** | 0.000 | 0.000 | 0 | 6 | 11 |
| **INSTRUCTION** | 0.300 | 0.500 | 3 | 10 | 6 |
| **OBJECTIVE** | 0.704 | 0.826 | 19 | 27 | 23 |
| **SIDEBAR** | 0.738 | 0.620 | 31 | 42 | 50 |
| HEADING | 0.901 | 0.753 | 128 | 142 | 170 |
| BODY | 0.699 | 0.825 | 146 | 209 | 177 |
| CAPTION | 0.824 | 0.800 | 28 | 34 | 35 |
| OPTION | 1.000 | 1.000 | 4 | 4 | 4 |
| ANSWER_SLOT | — | 0.000 | 0 | 0 | 1 |
| TABLE | 1.000 | 0.550 | 11 | 11 | 20 |
| FORMULA | — | 0.000 | 0 | 0 | 13 |
| FOOTNOTE | 1.000 | 0.727 | 8 | 8 | 11 |
| FIGURE_TEXT | 0.292 | 0.750 | 21 | 72 | 28 |
| PAGENUM | 1.000 | 0.944 | 51 | 51 | 54 |
| TEACHER_PROMPT | 1.000 | 0.667 | 4 | 4 | 6 |

confusion (gold→pipeline): {'HEADING->FIGURE_TEXT': 27, 'QUESTION->BODY': 20, 'HEADING->BODY': 11, 'BODY->SIDEBAR': 9, 'FORMULA->EMPTY': 8, 'TABLE->FIGURE_TEXT': 8, 'SIDEBAR->BODY': 8, 'ANSWER->BODY': 6, 'SIDEBAR->HEADING': 6, 'BODY->FIGURE_TEXT': 5, 'ACTIVITY->BODY': 5, 'FORMULA->FIGURE_TEXT': 4, 'SIDEBAR->OBJECTIVE': 4, 'CAPTION->FIGURE_TEXT': 4, 'BODY->QUESTION': 4, 'FOOTNOTE->BODY': 3, 'BODY->CAPTION': 3, 'ANSWER->HEADING': 3, 'ACTIVITY->QUESTION': 3, 'QUESTION->ACTIVITY': 3, 'OBJECTIVE->BODY': 3, 'BODY->ACTIVITY': 3, 'PAGENUM->EMPTY': 2, 'QUESTION->FIGURE_TEXT': 2, 'INSTRUCTION->BODY': 2}
unmatched pipeline blocks by role: {'BODY': 77, 'HEADING': 4, 'FIGURE_TEXT': 117, 'SIDEBAR': 12, 'QUESTION': 6, 'EMPTY': 9, 'OBJECTIVE': 3, 'FOOTNOTE': 6, 'CAPTION': 1, 'OPTION': 9, 'INSTRUCTION': 3}
trust reasons (blocks): {'agree_text': 119, 'furniture': 58, 'empty_block': 104, 'page_feature:diagram': 18, 'figure_text': 598, 'low_ocr_conf': 13, 'math_guard': 21, 'page_feature:color_heavy': 49, 'agree_order': 15, 'figure_dependent': 13, 'teacher_text': 36, 'answer_leak': 7, 'empty': 1, 'box_boundary': 4}
CTE by class: {'lesson_attach_wrong': 17, 'corrupted_data': 22, 'enumerator_dropped': 2, 'order_changes_meaning': 44, 'cross_column_contamination': 10, 'nonquestion_as_question': 9, 'heading_as_question': 2}

### dev (38 pages) — trusted-QUESTION precision 0.917 (n=72)
| role | precision | recall | tp | predicted | gold |
|---|---|---|---|---|---|
| **QUESTION** | 0.893 | 0.750 | 75 | 84 | 100 |
| **ANSWER** | — | 0.000 | 0 | 0 | 5 |
| **ACTIVITY** | 0.000 | 0.000 | 0 | 3 | 5 |
| **INSTRUCTION** | 0.000 | — | 0 | 7 | 0 |
| **OBJECTIVE** | 0.700 | 0.700 | 7 | 10 | 10 |
| **SIDEBAR** | 0.444 | 0.348 | 8 | 18 | 23 |
| HEADING | 0.869 | 0.729 | 86 | 99 | 118 |
| BODY | 0.710 | 0.833 | 115 | 162 | 138 |
| CAPTION | 0.947 | 0.750 | 18 | 19 | 24 |
| OPTION | 1.000 | 1.000 | 4 | 4 | 4 |
| ANSWER_SLOT | — | 0.000 | 0 | 0 | 1 |
| TABLE | 1.000 | 0.400 | 6 | 6 | 15 |
| FORMULA | — | 0.000 | 0 | 0 | 13 |
| FOOTNOTE | 1.000 | 0.727 | 8 | 8 | 11 |
| FIGURE_TEXT | 0.283 | 0.708 | 17 | 60 | 24 |
| PAGENUM | 1.000 | 0.947 | 36 | 36 | 38 |

confusion (gold→pipeline): {'HEADING->FIGURE_TEXT': 20, 'QUESTION->BODY': 19, 'HEADING->BODY': 9, 'BODY->SIDEBAR': 9, 'FORMULA->EMPTY': 8, 'TABLE->FIGURE_TEXT': 8, 'SIDEBAR->HEADING': 6, 'SIDEBAR->BODY': 6, 'BODY->FIGURE_TEXT': 5, 'FORMULA->FIGURE_TEXT': 4, 'CAPTION->FIGURE_TEXT': 4, 'BODY->QUESTION': 4, 'FOOTNOTE->BODY': 3, 'ANSWER->HEADING': 3, 'QUESTION->ACTIVITY': 3, 'ANSWER->BODY': 2, 'PAGENUM->EMPTY': 2, 'QUESTION->FIGURE_TEXT': 2, 'SIDEBAR->OBJECTIVE': 2, 'ACTIVITY->INSTRUCTION': 2, 'HEADING->QUESTION': 2, 'BODY->INSTRUCTION': 2, 'FIGURE_TEXT->HEADING': 2, 'FIGURE_TEXT->BODY': 2, 'ACTIVITY->BODY': 2}
unmatched pipeline blocks by role: {'BODY': 77, 'HEADING': 4, 'FIGURE_TEXT': 65, 'SIDEBAR': 12, 'QUESTION': 6, 'EMPTY': 9, 'OBJECTIVE': 3, 'OPTION': 9, 'FOOTNOTE': 4, 'INSTRUCTION': 3}
trust reasons (blocks): {'agree_text': 91, 'furniture': 42, 'empty_block': 99, 'page_feature:diagram': 18, 'figure_text': 376, 'low_ocr_conf': 5, 'math_guard': 20, 'figure_dependent': 8, 'agree_order': 10, 'teacher_text': 16, 'page_feature:color_heavy': 1, 'box_boundary': 3}
CTE by class: {'lesson_attach_wrong': 10, 'corrupted_data': 21, 'enumerator_dropped': 2, 'order_changes_meaning': 31, 'cross_column_contamination': 8, 'heading_as_question': 2, 'nonquestion_as_question': 7}

### heldout (16 pages) — trusted-QUESTION precision 0.917 (n=12)
| role | precision | recall | tp | predicted | gold |
|---|---|---|---|---|---|
| **QUESTION** | 0.833 | 0.938 | 15 | 18 | 16 |
| **ANSWER** | 0.800 | 0.400 | 4 | 5 | 10 |
| **ACTIVITY** | 0.000 | 0.000 | 0 | 3 | 6 |
| **INSTRUCTION** | 1.000 | 0.500 | 3 | 3 | 6 |
| **OBJECTIVE** | 0.706 | 0.923 | 12 | 17 | 13 |
| **SIDEBAR** | 0.958 | 0.852 | 23 | 24 | 27 |
| HEADING | 0.977 | 0.808 | 42 | 43 | 52 |
| BODY | 0.660 | 0.795 | 31 | 47 | 39 |
| CAPTION | 0.667 | 0.909 | 10 | 15 | 11 |
| TABLE | 1.000 | 1.000 | 5 | 5 | 5 |
| FIGURE_TEXT | 0.333 | 1.000 | 4 | 12 | 4 |
| PAGENUM | 1.000 | 0.938 | 15 | 15 | 16 |
| TEACHER_PROMPT | 1.000 | 0.667 | 4 | 4 | 6 |

confusion (gold→pipeline): {'HEADING->FIGURE_TEXT': 7, 'ANSWER->BODY': 4, 'ACTIVITY->BODY': 3, 'BODY->ACTIVITY': 3, 'INSTRUCTION->BODY': 2, 'SIDEBAR->OBJECTIVE': 2, 'ACTIVITY->QUESTION': 2, 'TEACHER_PROMPT->CAPTION': 2, 'HEADING->BODY': 2, 'BODY->CAPTION': 2, 'SIDEBAR->BODY': 2, 'ACTIVITY->OBJECTIVE': 1, 'ANSWER->OBJECTIVE': 1, 'QUESTION->BODY': 1, 'HEADING->SIDEBAR': 1, 'ANSWER->CAPTION': 1, 'BODY->ANSWER': 1, 'BODY->HEADING': 1, 'PAGENUM->FIGURE_TEXT': 1, 'BODY->OBJECTIVE': 1, 'OBJECTIVE->BODY': 1, 'CAPTION->BODY': 1, 'INSTRUCTION->QUESTION': 1}
unmatched pipeline blocks by role: {'FIGURE_TEXT': 52, 'FOOTNOTE': 2, 'CAPTION': 1}
trust reasons (blocks): {'furniture': 16, 'figure_text': 222, 'page_feature:color_heavy': 48, 'agree_order': 5, 'agree_text': 28, 'figure_dependent': 5, 'teacher_text': 20, 'math_guard': 1, 'answer_leak': 7, 'empty_block': 5, 'low_ocr_conf': 8, 'empty': 1, 'box_boundary': 1}
CTE by class: {'corrupted_data': 1, 'cross_column_contamination': 2, 'lesson_attach_wrong': 7, 'nonquestion_as_question': 2, 'order_changes_meaning': 13}

### science (23 pages) — trusted-QUESTION precision 0.970 (n=33)
| role | precision | recall | tp | predicted | gold |
|---|---|---|---|---|---|
| **QUESTION** | 0.889 | 0.870 | 40 | 45 | 46 |
| **ANSWER** | 0.800 | 0.400 | 4 | 5 | 10 |
| **ACTIVITY** | 0.000 | 0.000 | 0 | 3 | 10 |
| **INSTRUCTION** | 0.500 | 0.500 | 3 | 6 | 6 |
| **OBJECTIVE** | 0.696 | 0.941 | 16 | 23 | 17 |
| **SIDEBAR** | 0.964 | 0.818 | 27 | 28 | 33 |
| HEADING | 0.983 | 0.826 | 57 | 58 | 69 |
| BODY | 0.642 | 0.827 | 43 | 67 | 52 |
| CAPTION | 0.750 | 0.783 | 18 | 24 | 23 |
| OPTION | 1.000 | 1.000 | 1 | 1 | 1 |
| TABLE | 1.000 | 1.000 | 7 | 7 | 7 |
| FOOTNOTE | 1.000 | 1.000 | 1 | 1 | 1 |
| FIGURE_TEXT | 0.429 | 0.818 | 9 | 21 | 11 |
| PAGENUM | 1.000 | 0.957 | 22 | 22 | 23 |
| TEACHER_PROMPT | 1.000 | 0.667 | 4 | 4 | 6 |

confusion (gold→pipeline): {'HEADING->FIGURE_TEXT': 9, 'QUESTION->BODY': 6, 'SIDEBAR->OBJECTIVE': 4, 'ANSWER->BODY': 4, 'ACTIVITY->BODY': 4, 'BODY->CAPTION': 3, 'ACTIVITY->QUESTION': 3, 'BODY->ACTIVITY': 3, 'INSTRUCTION->BODY': 2, 'CAPTION->FIGURE_TEXT': 2, 'TEACHER_PROMPT->CAPTION': 2, 'HEADING->BODY': 2, 'ACTIVITY->INSTRUCTION': 2, 'SIDEBAR->BODY': 2, 'CAPTION->BODY': 2, 'ACTIVITY->OBJECTIVE': 1, 'FIGURE_TEXT->INSTRUCTION': 1, 'ANSWER->OBJECTIVE': 1, 'HEADING->SIDEBAR': 1, 'ANSWER->CAPTION': 1, 'BODY->ANSWER': 1, 'BODY->HEADING': 1, 'PAGENUM->FIGURE_TEXT': 1, 'BODY->OBJECTIVE': 1, 'OBJECTIVE->BODY': 1}
unmatched pipeline blocks by role: {'FIGURE_TEXT': 84, 'SIDEBAR': 4, 'BODY': 11, 'FOOTNOTE': 2, 'CAPTION': 1, 'OPTION': 3, 'INSTRUCTION': 1}
trust reasons (blocks): {'furniture': 23, 'figure_text': 279, 'page_feature:color_heavy': 48, 'agree_order': 5, 'agree_text': 34, 'figure_dependent': 11, 'empty_block': 10, 'page_feature:diagram': 1, 'teacher_text': 20, 'math_guard': 1, 'answer_leak': 7, 'low_ocr_conf': 8, 'empty': 1, 'box_boundary': 1}
CTE by class: {'corrupted_data': 5, 'cross_column_contamination': 3, 'lesson_attach_wrong': 8, 'order_changes_meaning': 15, 'nonquestion_as_question': 4}

### science_sgk (18 pages) — trusted-QUESTION precision 0.970 (n=33)
| role | precision | recall | tp | predicted | gold |
|---|---|---|---|---|---|
| **QUESTION** | 0.889 | 0.870 | 40 | 45 | 46 |
| **ACTIVITY** | — | 0.000 | 0 | 0 | 10 |
| **INSTRUCTION** | 0.500 | 0.500 | 3 | 6 | 6 |
| **OBJECTIVE** | 0.750 | 1.000 | 15 | 20 | 15 |
| **SIDEBAR** | 0.964 | 0.818 | 27 | 28 | 33 |
| HEADING | 1.000 | 0.800 | 40 | 40 | 50 |
| BODY | 0.550 | 0.880 | 22 | 40 | 25 |
| CAPTION | 0.857 | 0.783 | 18 | 21 | 23 |
| OPTION | 1.000 | 1.000 | 1 | 1 | 1 |
| TABLE | 1.000 | 1.000 | 3 | 3 | 3 |
| FOOTNOTE | 1.000 | 1.000 | 1 | 1 | 1 |
| FIGURE_TEXT | 0.450 | 0.818 | 9 | 20 | 11 |
| PAGENUM | 1.000 | 0.944 | 17 | 17 | 18 |

confusion (gold→pipeline): {'HEADING->FIGURE_TEXT': 8, 'QUESTION->BODY': 6, 'SIDEBAR->OBJECTIVE': 4, 'ACTIVITY->BODY': 4, 'BODY->CAPTION': 3, 'ACTIVITY->QUESTION': 3, 'INSTRUCTION->BODY': 2, 'CAPTION->FIGURE_TEXT': 2, 'ACTIVITY->INSTRUCTION': 2, 'SIDEBAR->BODY': 2, 'CAPTION->BODY': 2, 'ACTIVITY->OBJECTIVE': 1, 'FIGURE_TEXT->INSTRUCTION': 1, 'HEADING->SIDEBAR': 1, 'PAGENUM->FIGURE_TEXT': 1, 'HEADING->BODY': 1, 'INSTRUCTION->QUESTION': 1, 'CAPTION->QUESTION': 1, 'FIGURE_TEXT->BODY': 1}
unmatched pipeline blocks by role: {'FIGURE_TEXT': 84, 'SIDEBAR': 4, 'BODY': 11, 'FOOTNOTE': 2, 'CAPTION': 1, 'OPTION': 3, 'INSTRUCTION': 1}
trust reasons (blocks): {'furniture': 18, 'figure_text': 278, 'page_feature:color_heavy': 48, 'agree_order': 4, 'agree_text': 30, 'figure_dependent': 11, 'empty_block': 10, 'page_feature:diagram': 1, 'low_ocr_conf': 8, 'empty': 1, 'box_boundary': 1}
CTE by class: {'corrupted_data': 5, 'cross_column_contamination': 3, 'lesson_attach_wrong': 6, 'order_changes_meaning': 9, 'nonquestion_as_question': 4}

### sgv (8 pages) — trusted-QUESTION precision — (n=0)
| role | precision | recall | tp | predicted | gold |
|---|---|---|---|---|---|
| **ANSWER** | 0.800 | 0.308 | 4 | 5 | 13 |
| **ACTIVITY** | 0.000 | — | 0 | 3 | 0 |
| **INSTRUCTION** | 0.000 | — | 0 | 2 | 0 |
| **OBJECTIVE** | 0.600 | 0.500 | 3 | 5 | 6 |
| **SIDEBAR** | 1.000 | 1.000 | 1 | 1 | 1 |
| HEADING | 0.853 | 0.853 | 29 | 34 | 34 |
| BODY | 0.763 | 0.806 | 29 | 38 | 36 |
| CAPTION | 0.000 | — | 0 | 3 | 0 |
| TABLE | 1.000 | 0.857 | 6 | 6 | 7 |
| FIGURE_TEXT | 0.667 | 1.000 | 2 | 3 | 2 |
| PAGENUM | 1.000 | 1.000 | 8 | 8 | 8 |
| TEACHER_PROMPT | 1.000 | 0.667 | 4 | 4 | 6 |

confusion (gold→pipeline): {'ANSWER->BODY': 4, 'HEADING->BODY': 3, 'ANSWER->HEADING': 3, 'BODY->ACTIVITY': 3, 'TEACHER_PROMPT->CAPTION': 2, 'BODY->HEADING': 2, 'OBJECTIVE->BODY': 2, 'ANSWER->OBJECTIVE': 1, 'OBJECTIVE->INSTRUCTION': 1, 'HEADING->INSTRUCTION': 1, 'HEADING->FIGURE_TEXT': 1, 'ANSWER->CAPTION': 1, 'BODY->ANSWER': 1, 'BODY->OBJECTIVE': 1, 'TABLE->EMPTY': 1}
unmatched pipeline blocks by role: {'FIGURE_TEXT': 4, 'BODY': 5, 'OBJECTIVE': 1}
trust reasons (blocks): {'teacher_text': 36, 'agree_text': 6, 'math_guard': 1, 'answer_leak': 7, 'furniture': 8, 'figure_text': 13, 'agree_order': 2, 'page_feature:diagram': 1, 'empty_block': 2}
CTE by class: {'order_changes_meaning': 6, 'lesson_attach_wrong': 4, 'corrupted_data': 1}

## Per page

| page | set | found | order | text | fidelity | splices | TLSR | FTR | trusted/withheld | CTE | lesson TOC | lesson header | false Qs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01-sgk-tu-nhien-va-xa-hoi-1 p006 | dev | 1.000 | 1.000 | 1.000 | — | 0 | 0.000 | — | 0/0 | 0 | gold=none (TOC attaches none → OK) | None none OK | 0 |
| 02-sgk-tieng-viet-2-tap-hai p014 | dev | 0.929 | 1.000 | 0.863 | 1.000 | 0 | 0.769 | 0.000 | 10/2 | 1 | WRONG (toc=1, gold=2) | 2 continuation OK | 0 |
| 02-sgk-tieng-viet-2-tap-mot p103 | dev | 1.000 | 1.000 | 0.958 | 1.000 | 0 | 0.867 | 0.071 | 14/1 | 0 | OK | 23 continuation OK | 0 |
| 02-sgk-toan-2-tap-hai p048 | dev | 1.000 | 1.000 | 0.871 | — | 0 | 0.067 | 0.000 | 1/14 | 3 | OK | 50 header OK | 0 |
| 03-sgk-toan-3-tap-mot p032 | dev | 1.000 | 0.925 | 0.862 | 1.000 | 0 | 0.100 | 0.000 | 1/9 | 7 | OK | 10 header OK | 0 |
| 04-sgk-khoa-hoc-4 p006 | held-out | 1.000 | 1.000 | 0.961 | 1.000 | 0 | 0.167 | 0.000 | 2/10 | 0 | OK | 1 header OK | 0 |
| 04-sgk-khoa-hoc-4 p009 | held-out | 1.000 | 1.000 | 0.980 | 0.875 | 1 | 0.833 | 0.091 | 11/1 | 2 | OK | 1 continuation OK | 0 |
| 04-sgk-khoa-hoc-4 p010 | held-out | 1.000 | 1.000 | 0.974 | 1.000 | 0 | 0.800 | 0.000 | 8/2 | 1 | WRONG (toc=1, gold=2) | 2 header OK | 0 |
| 04-sgk-khoa-hoc-4 p030 | dev | 1.000 | 1.000 | 0.967 | 1.000 | 0 | 0.571 | 0.000 | 4/3 | 0 | OK | 7 header OK | 0 |
| 04-sgk-khoa-hoc-4 p078 | dev | 1.000 | 0.955 | 0.991 | 1.000 | 0 | 0.692 | 0.182 | 11/2 | 2 | WRONG (toc=19, gold=20) | 20 continuation OK | 0 |
| 04-sgk-tieng-viet-4-tap-mot p028 | dev | 0.944 | 0.993 | 0.973 | 1.000 | 0 | 0.812 | 0.133 | 15/0 | 2 | WRONG (toc=5, gold=6) | 6 continuation OK | 0 |
| 04-sgv-khoa-hoc-4 p028 | held-out | 1.000 | 1.000 | 0.998 | 1.000 | 0 | 0.357 | 0.000 | 5/9 | 0 | OK | 1 continuation OK | 0 |
| 04-sgv-toan-4 p054 | dev | 1.000 | 1.000 | 0.994 | 1.000 | 0 | 0.615 | 0.000 | 8/5 | 0 | OK | 10 continuation WRONG | 0 |
| 05-sgk-khoa-hoc-5 p042 | held-out | 1.000 | 1.000 | 0.973 | 1.000 | 0 | 0.889 | 0.000 | 16/2 | 1 | OK | 10 continuation OK | 1 |
| 05-sgk-khoa-hoc-5 p043 | held-out | 1.000 | 1.000 | 0.994 | 1.000 | 0 | 0.800 | 0.000 | 8/2 | 2 | WRONG (toc=10, gold=11) | 11 header OK | 1 |
| 05-sgk-lich-su-va-dia-li-5 p041 | dev | 1.000 | 0.972 | 0.998 | 1.000 | 0 | 1.000 | 0.000 | 9/0 | 1 | WRONG (toc=8, gold=9) | 8 continuation WRONG | 0 |
| 05-sgk-lich-su-va-dia-li-5 p080 | dev | 1.000 | 0.955 | 0.998 | 1.000 | 0 | 1.000 | 0.000 | 5/0 | 1 | WRONG (toc=15, gold=17) | 18 continuation WRONG | 0 |
| 05-sgk-tieng-viet-5-tap-hai p008 | dev | 1.000 | 1.000 | 1.000 | — | 0 | 0.000 | — | 0/1 | 0 | gold=none (TOC attaches none → OK) | None none OK | 0 |
| 05-sgk-toan-5-tap-mot p021 | dev | 0.938 | 0.855 | 0.776 | 1.000 | 0 | 0.133 | 0.333 | 3/11 | 16 | OK | 6 header OK | 0 |
| 05-sgk-toan-5-tap-mot p092 | dev | 1.000 | 1.000 | 0.965 | 0.667 | 2 | 0.500 | 0.222 | 9/5 | 2 | OK | 25 header OK | 0 |
| 06-sgk-ngu-van-6-tap-mot p021 | dev | 1.000 | 1.000 | 0.991 | 0.857 | 2 | 0.692 | 0.000 | 9/4 | 2 | OK | 1 continuation OK | 0 |
| 06-sgk-tin-hoc-6 p021 | dev | 1.000 | 1.000 | 0.952 | 1.000 | 0 | 0.600 | 0.000 | 9/6 | 0 | OK | 4 continuation WRONG | 0 |
| 06-sgv-khoa-hoc-tu-nhien-6 p005 | held-out | 1.000 | 1.000 | 1.000 | — | 0 | 0.000 | — | 0/1 | 0 | gold=none (TOC attaches none → OK) | None none OK | 0 |
| 06-sgv-khoa-hoc-tu-nhien-6 p071 | held-out | 0.957 | 0.909 | 0.978 | 1.000 | 0 | 0.050 | 0.800 | 5/14 | 6 | OK | 11 continuation OK | 0 |
| 07-sgk-khoa-hoc-tu-nhien-7 p020 | dev | 1.000 | 1.000 | 0.988 | 1.000 | 0 | 0.733 | 0.000 | 11/4 | 0 | OK | 3 header OK | 0 |
| 07-sgk-khoa-hoc-tu-nhien-7 p021 | dev | 1.000 | 0.990 | 0.983 | 1.000 | 0 | 0.857 | 0.143 | 14/0 | 4 | OK | 3 continuation OK | 0 |
| 07-sgk-khoa-hoc-tu-nhien-7 p026 | held-out | 0.750 | 1.000 | 1.000 | — | 0 | 0.667 | 0.000 | 2/0 | 0 | OK | 4 continuation OK | 0 |
| 07-sgk-khoa-hoc-tu-nhien-7 p032 | dev | 0.941 | 1.000 | 0.990 | 1.000 | 0 | 1.000 | 0.000 | 15/0 | 0 | OK | 4 continuation OK | 0 |
| 07-sgk-khoa-hoc-tu-nhien-7 p096 | held-out | 1.000 | 1.000 | 0.983 | 1.000 | 0 | 1.000 | 0.000 | 13/0 | 1 | WRONG (toc=18, gold=19) | 19 continuation OK | 0 |
| 07-sgk-khoa-hoc-tu-nhien-7 p097 | held-out | 1.000 | 0.982 | 0.953 | 1.000 | 0 | 0.692 | 0.100 | 10/3 | 1 | WRONG (toc=18, gold=20) | 20 header OK | 0 |
| 07-sgk-lich-su-va-dia-li-7 p094 | dev | 1.000 | 1.000 | 0.978 | 1.000 | 0 | 0.500 | 0.000 | 7/7 | 1 | WRONG (toc=16, gold=18) | 18 continuation OK | 0 |
| 07-sgk-toan-7-tap-hai p041 | dev | 0.875 | 1.000 | 0.966 | 1.000 | 0 | 0.467 | 0.125 | 8/5 | 1 | OK | 28 continuation OK | 1 |
| 07-sgv-khoa-hoc-tu-nhien-7 p168 | held-out | 1.000 | 1.000 | 0.958 | 1.000 | 0 | 0.562 | 0.000 | 9/7 | 1 | WRONG (toc=33, gold=34) | 34 header OK | 0 |
| 07-sgv-toan-7 p043 | dev | 1.000 | 1.000 | 0.990 | — | 0 | 1.000 | 0.000 | 2/0 | 1 | WRONG (toc=None, gold=6) | 24 continuation WRONG | 0 |
| 08-sgk-khoa-hoc-tu-nhien-8 p095 | held-out | 1.000 | 1.000 | 0.974 | 0.857 | 1 | 0.833 | 0.167 | 12/0 | 1 | OK | 22 continuation OK | 0 |
| 08-sgk-khoa-hoc-tu-nhien-8 p096 | held-out | 1.000 | 0.882 | 0.987 | 1.000 | 0 | 0.167 | 0.750 | 8/4 | 8 | WRONG (toc=22, gold=23) | 23 header OK | 1 |
| 08-sgk-lich-su-va-dia-li-8 p071 | dev | 1.000 | 1.000 | 0.975 | 1.000 | 1 | 0.778 | 0.000 | 7/2 | 1 | OK | 15 continuation OK | 0 |
| 08-sgk-ngu-van-8-tap-mot p038 | dev | 1.000 | 1.000 | 0.993 | 1.000 | 0 | 0.933 | 0.067 | 15/0 | 3 | WRONG (toc=1, gold=2) | 1 continuation WRONG | 1 |
| 09-sgk-khoa-hoc-tu-nhien-9 p013 | held-out | 1.000 | 1.000 | 0.992 | — | 0 | 0.500 | 0.000 | 1/1 | 0 | OK | 1 continuation OK | 0 |
| 09-sgk-khoa-hoc-tu-nhien-9 p038 | dev | 1.000 | 0.993 | 0.999 | 1.000 | 1 | 0.875 | 0.000 | 14/2 | 2 | OK | 7 continuation OK | 1 |
| 09-sgk-khoa-hoc-tu-nhien-9 p046 | dev | 1.000 | 1.000 | 0.966 | 1.000 | 0 | 0.500 | 0.200 | 5/3 | 2 | OK | 8 continuation OK | 1 |
| 09-sgk-ngu-van-9-tap-mot p067 | dev | 0.882 | 1.000 | 0.987 | 1.000 | 0 | 0.750 | 0.000 | 12/2 | 3 | OK | 3 continuation OK | 0 |
| 09-sgk-ngu-van-9-tap-mot p083 | dev | 1.000 | 1.000 | 0.989 | 1.000 | 0 | 0.812 | 0.000 | 13/3 | 1 | OK | 3 continuation OK | 0 |
| 09-sgk-tin-hoc-9 p020 | dev | 1.000 | 1.000 | 0.994 | 0.636 | 2 | 0.667 | 0.286 | 14/1 | 2 | OK | 4 continuation OK | 0 |
| 09-sgk-toan-9-tap-mot p029 | dev | 0.938 | 0.903 | 0.967 | 1.000 | 0 | 0.067 | 0.900 | 10/4 | 12 | OK | 3 continuation WRONG | 2 |
| 09-sgv-khoa-hoc-tu-nhien-9 p136 | held-out | 1.000 | 1.000 | 0.992 | 1.000 | 0 | 0.462 | 0.000 | 6/7 | 1 | WRONG (toc=14, gold=19) | 21 continuation WRONG | 0 |
| 10-sgk-dia-li-10 p040 | dev | 1.000 | 1.000 | 0.875 | 1.000 | 0 | 0.818 | 0.182 | 11/0 | 1 | OK | 11 continuation OK | 0 |
| 10-sgk-dia-li-10 p115 | dev | 1.000 | 1.000 | 1.000 | — | 0 | 1.000 | 0.000 | 1/0 | 1 | gold=none (TOC attaches 31 → WRONG) | None none OK | 0 |
| 10-sgk-vat-li-10 p030 | dev | 0.952 | 0.942 | 0.979 | 1.000 | 0 | 0.778 | 0.125 | 16/1 | 2 | OK | 5 continuation OK | 2 |
| 10-sgk-vat-li-10 p089 | dev | 1.000 | 0.988 | 0.988 | 1.000 | 0 | 0.615 | 0.200 | 10/3 | 2 | OK | 22 continuation OK | 1 |
| 10-sgv-tin-hoc-10 p039 | dev | 0.950 | 1.000 | 0.976 | 1.000 | 0 | 0.556 | 0.000 | 10/7 | 2 | gold=none (TOC attaches 5 → WRONG) | 4 continuation WRONG | 0 |
| 11-sgk-ngu-van-11-tap-mot p039 | dev | 1.000 | 1.000 | 0.998 | 1.000 | 0 | 0.400 | 0.000 | 4/6 | 0 | OK | 1 continuation OK | 0 |
| 11-sgk-vat-li-11 p105 | dev | 0.810 | 1.000 | 0.993 | 1.000 | 0 | 0.444 | 0.000 | 8/6 | 0 | OK | None none WRONG | 0 |
| 12-sgk-toan-12-tap-hai p020 | dev | 1.000 | 0.938 | 0.911 | 1.000 | 0 | 0.286 | 0.500 | 8/6 | 3 | OK | 1 continuation WRONG | 0 |
