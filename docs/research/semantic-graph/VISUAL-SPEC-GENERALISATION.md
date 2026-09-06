# VISUAL-SPEC §19 — same renderer, same schema, different subject (Lane E2, round 5)

**READY FOR FOUNDER REVIEW — nothing merged.** The lane's failure condition was stated up
front: *a beautiful Bài 17 visual is not success.* This is the measurement that decides it.

## The claim under test

> One `OrderedStepsRenderer` and one `VisualSpec` schema serve sequential structure in
> **subjects that have nothing to do with each other**, with no branch on subject, book or
> lesson anywhere in the path.

## Substrate — chosen so a clean clone can reproduce it

`poc-out/` is gitignored (SGK copyright), so anything measured there is a claim only this
machine can check. I used **`tool/corpus/tc_gold/`** instead: **54 pages, 759 blocks, 10
subjects, human-annotated** (role, bbox, reading order, printed page) — and **committed**.
A `flutter test` on a fresh clone re-runs every number below.

The measurement is fed by two *different* semantic paths into the *same* schema:

| path | input | rule |
|---|---|---|
| typed semantic layer | `SemanticData` in the committed fixtures | `tsl-enumerated-steps-v1`, `prose-dated-events-v1`, `synthetic` |
| document structure | numbered section headings in reading order | `numbered-section-sequence-v1` (**PROPOSED, bounded**) |

## Result

```
SPEC  KHTN     06-sgk-khoa-hoc-tu-nhien-6#17   sections=2  [process, comparison]
SPEC  LS&ĐL    05-sgk-lich-su-va-dia-li-5#8    sections=1  [timeline]
SEQ   KHTN     07-sgk-khoa-hoc-tu-nhien-7#p21  nodes=2  «1. Tên gọi của nguyên tố hoá học»
SEQ   Ngữ văn  09-sgk-ngu-van-9-tap-mot#p83    nodes=2  «1 TRƯỚC KHI NÓI»
SEQ   Vật lí   10-sgk-vat-li-10#p89            nodes=3  «1. Dụng cụ thí nghiệm (Hình 22.3)»
```

**The same `OrderedStepsRenderer` instance draws all four ordered structures** — a grade-6
chemistry separation procedure, a grade-7 chemistry naming section, a grade-9 **literature**
speaking task, and a grade-10 **physics** lab procedure. Chemistry and «Nói và nghe» share no
vocabulary, no page layout and no pedagogy; they share a *shape*, and the shape is all the
renderer sees.

| | value |
|---|---|
| subjects with ≥1 spec | **4** (KHTN · LS&ĐL · Ngữ văn · Vật lí) |
| subjects served by the ONE ordered-steps renderer | **3** (KHTN · Ngữ văn · Vật lí) |
| families in the artefact | `process` 1 · `comparison` 1 · `timeline` 1 · `sequence` 3 |
| artefact | 5 specs · 6 sections · 19,289 bytes · byte-identical across builds |
| lane tests | 48 passed; full suite 968 passed / 42 skipped / 0 failed |

## What did **not** work — reported, not tuned away

**1 · The rule fires on 6 of 54 gold pages (0.111), and 3 of those 6 were teacher books.**
Before the gate, `numbered-section-sequence-v1` produced a "sequence" for Khoa học 4 SGV
(«1. Câu hỏi → 2. Đáp án và đánh giá»), Toán 4 SGV («1. Khám phá → 2. Hoạt động») and Tin học 10
SGV («1. KIẾN THỨC → 2. KĨ NĂNG → 3. PHẨM CHẤT»). The last is a **competency list**: the numbers
are labels, the order carries no meaning, and it is teacher material a child should never see.
Precision as learner-facing content was therefore **3/6 = 0.500**. The gold pages already record
`docType`, so the fix is a real gate rather than a guess; the builder still prints the
**unfiltered** count so the false-positive number cannot quietly leave the report.

**2 · Toán, Tiếng Việt and Tin học produced no learner-facing spec at all.** Not because the
renderer failed — because **nothing upstream emits structure for them**. Across the whole corpus
the semantic layer emits `semantic[]` only for KHTN/Khoa học (Process, Comparison) and one LS&ĐL
lesson (Timeline). Toán's gold pages carry `formula` regions (19 blocks) which round 4 proved
must stay **withheld**, not reconstructed; Tiếng Việt's gold page is 3 blocks, all `WITHHELD`.
**This lane cannot fix that, and should not:** inventing a Toán or Tiếng Việt semantic rule here
would be the visual layer deciding meaning, which is the boundary the architecture exists to
protect. It is a P0 input for E1/A/C, not a renderer problem.

**3 · The rule is deliberately weaker than it looks.** It emits family `sequence`, not
`process`. «The book prints these in this order» is an observation; «you must do these in this
order» is a claim about the world. Same renderer, different child-facing sentence, looked up by
rule id in `derivation_lexicon.dart`.

**4 · `charSpan` is carried but not yet used by any renderer.** The LS&ĐL fixture has
character spans; `ProvenanceRef` preserves them; no renderer highlights the exact substring yet.
Honest state: plumbed, not spent.

## Why this is not a Bài 17 demo in disguise

- `no_lesson_branching_test` scans every `.dart` file in both lane directories for
  `lessonNo ==`, `slotKey ==`, `book ==`, `bai17`, `khtn6`, `lessonId ==`. Comments may name a
  lesson; code may not.
- A second test asserts no file under `visual_grammar/` imports `lesson_document.dart` at all.
- `cross_subject_renderer_test` never names a lesson: it walks **every** committed gold page and
  requires ≥2 distinct subjects, one renderer accepting all of them, every node resolving to a
  real block with page and bbox, and the rendered widget showing the book's own words.
- A final test asserts the gold directory still holds >40 pages, so the suite cannot pass by
  quietly having no data.

## Next measurement, when E1's census lands

The census decides **which families are worth building next**, and this lane is deliberately
short of renderers until it does. The existing round-3 evidence already narrows it: history/geo
units are 33.8 % `timeline_year` and 14.4 % `source_text`; math 33.3 % `math_ops`; informatics
8.2 % `process_steps`. `tsl-enumerated-steps-v1` yields a Process in **68/238** TSL lessons while
`tsl-summary-parenthesis-v1` yields a Comparison in **6/238** — which argues *against* investing
in comparison breadth and *for* timeline and source-excerpt families. That is a hypothesis for
the census to confirm, not a decision taken here.
