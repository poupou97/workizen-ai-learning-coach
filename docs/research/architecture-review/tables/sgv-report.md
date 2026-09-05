# TC-v2 SGV sample (MEASURED on the sampled pages only)

| SGV book | pages | trusted learning blk | answer_leak | teacher_text | would reach a learner w/o SGV guards | pairing cand. | PAIRABLE | AMBIGUOUS | UNPAIRED | SGV lessons canonical / TOC-ranged / header-detected / repaired |
|---|---|---|---|---|---|---|---|---|---|---|
| 04-sgv-khoa-hoc-4 | 7 | 34 | 13 | 84 | 93 | 6 | 1 | 3 | 2 | 31 / 24 / 23 / 30 |
| 05-sgv-khoa-hoc-5 | 3 | 15 | 30 | 16 | 38 | 18 | 0 | 0 | 18 | 30 / 23 / 24 / 30 |
| 06-sgv-khoa-hoc-tu-nhien-6 | 17 | 88 | 7 | 153 | 142 | 2 | 1 | 1 | 0 | 55 / 36 / 26 / 45 |
| 07-sgv-khoa-hoc-tu-nhien-7 | 16 | 86 | 3 | 148 | 150 | 0 | 0 | 0 | 0 | 42 / 28 / 26 / 34 |
| 08-sgv-khoa-hoc-tu-nhien-8 | 16 | 140 | 0 | 126 | 124 | 0 | 0 | 0 | 0 | 47 / 28 / 29 / 38 |
| 09-sgv-khoa-hoc-tu-nhien-9 | 16 | 110 | 3 | 166 | 164 | 0 | 0 | 0 | 0 | 51 / 18 / 27 / 31 |
| **total** | 75 | 473 | 56 | 693 | 711 | 26 | 2 | 4 | 20 | |

Reading: on SGV pages the SDM-v2 role layer marks prose as teacher_text and answer-section blocks as answer; both carry a withholding reason, so **no SGV block is TRUSTED for a learner surface** (learning_trusted counts headings/captions only). "Would reach a learner" counts the blocks that pass the agreement gate and would have been served as text without the SGV lexicon — the size of the leak the guards close on this sample. Pairing is by (lesson, printed enumerator) against TRUSTED SGK question/activity blocks and fails closed on ambiguity; it is an upper bound on what an `answer_of` relation could key today, not a shipped feature.

