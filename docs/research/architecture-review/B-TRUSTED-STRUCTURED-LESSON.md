# B — Trusted Structured Lesson (TSL): the document a View would consume (data only, no UI)

Builder: `tool/corpus/tc2_tsl.py` → `poc-out/trusted-corpus/tc-v2/tc2-p1/lessons/<book>/bai-NN.tsl.json` — **238 documents** on the six Science SGK books (MEASURED). No Flutter code, no pack, no Dart consumer was written or changed.

## B.1 Shape (one document per attached lesson)

```
{ book, lesson, title, pipeline: "tc2-p1", docType: "SGK",
  boundary:  { page_start, page_end, pages[], attach_methods{header|continuation…}, confidence (min page conf),
               header_found, header_page, source: header|toc|both },
  sourceability: FULL | PARTIAL | NONE,
  stats:     { learning_blocks, trusted, withheld, withheld_by_reason{}, roles_trusted{}, figures },
  blocks[]:  ordered TRUSTED learning blocks —
             { id, page, page_printed, order, role{value, coarse, confidence, method}, text, bbox[x,y,w,h],
               heading_path[], refers_figure, enumerator_restored,
               provenance{book, page_pdf, page_printed, bbox, extraction, ocr_conf, text_sim, pipeline, sdm_version, block_id} },
  withheld[]: every non-trusted learning block — { id, page, order, role, bbox, reasons[], status, text_len, provenance, text: null },
  figures[]: { id, page, bbox, caption (block id), labels (count) },
  hybridSmartBook: { with_images[], no_images[], counts{native, source_crop, withheld_ref, crops_by_reason} },   ← see C
  answer_keys_included: false }
```
Invariants enforced in the builder: a WITHHELD/CONFLICT block never carries its text (only bbox + reasons + provenance); answer-key and teacher-text blocks are never serialised with text anywhere; SGV pages are never merged into an SGK document (they live under their own book id); every block id resolves to `(book, pdf page, bbox, pipeline)`.

## B.2 What the slice produced (MEASURED)

| book | lessons (TSL) | FULL | PARTIAL | native trusted blocks | withheld regions | trusted roles (top) |
|---|---|---|---|---|---|---|
| Khoa học 4 | 31 | 1 | 30 | 1,166 | 240 | body, question, caption, heading, sidebar |
| Khoa học 5 | 30 | 0 | 30 | 1,077 | 191 | body, question, heading, caption, sidebar |
| KHTN 6 | 53 | 0 | 53 | 2,441 | 517 | body, heading, caption, question, objective |
| KHTN 7 | 33 | 0 | 33 | 1,869 | 323 | body, heading, question, caption, sidebar |
| KHTN 8 | 42 | 0 | 42 | 2,614 | 363 | body, heading, question, caption, objective |
| KHTN 9 | 49 | 1 | 48 | 2,804 | 398 | body, heading, question, caption, sidebar |
| **total** | **238** | **2** | **236** | **11,971** | **2,032** | body 4,076 · heading 2,274 · question 1,669 · caption 1,241 · sidebar 1,086 · objective 869 · stage_label 609 · instruction 367 · footnote 75 · activity 53 · table 25 |

- **FULL = every learning block on the lesson's pages is trusted or furniture/figure.** Only 2 of 238 lessons are FULL. This is the slice's version of TC-18 Q17 ("≈ 16 % fully sourceable" estimated corpus-wide from features): on the Science family, measured per lesson with the guards on, it is **< 1 %**. The reason is the guards themselves — a Science lesson always contains a figure-dependent question, a diagram page or a box edge — so "fully sourceable" is the wrong unit; **every lesson is PARTIAL with a small withheld set** (median 8 withheld regions per lesson).
- **Withheld regions by reason (238 lessons):** agree_text 865 · figure_dependent 638 · agree_order 229 · page_feature:diagram 199 · page_feature:color_heavy 111 · box_boundary 95 · math_guard 42 · answer_leak 30 · low_ocr_conf 20 · role_conflict 7.
- **Boundary confidence:** 224 of 238 lessons start on a detected header page (0.85–0.95); the 14 others come from the TOC fallback (0.6). `continues` pages: every non-header page in a lesson carries `method: continuation` with the header's confidence.
- Denominators: these 238 are **per-book repaired lesson counts** (header ∪ TOC) — 31 + 30 + 53 + 33 + 42 + 49 — not the canonical 3,679 (six-book canonical `lessonCount` sum = 207) nor the ranged 3,381 (six-book old ranged = 194). See I.1.

## B.3 What a TSL is good for, measured against gold

- Reading a lesson: on the 23 science gold pages, TLSR 0.636, FTR 0.100, text accuracy 0.982, order 0.987, fidelity 0.987, 3 splices (A.2). Read with the same caveat as any hard-page number: ≈ 1 trusted block in 10 is wrong on hard pages, ≈ 0 on plain prose.
- Attaching a lesson: 22/23 science gold pages attach to the right lesson by header (15/23 by TOC range) — A.4.
- Asking from a lesson: not licensed (ROLE-LAYER-AND-SHORT-ANSWER-GATE.md).

## B.4 Not in the TSL, on purpose

- No SGV content and no `answer_of` relation (the SGV sample measured pairing as an upper bound only — I.5).
- No typed learning data (Concept / Process / Comparison) — D.
- No page images: the `with_images` projection carries *references* (page + bbox) only; whether a client may render them is J.1.
- No LLM output of any kind.
