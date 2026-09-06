# STRUCTURED CONTENT GAP — the 118, answered (round 7 · WS-S · 2026-09-06)

**INTERNAL / RESEARCH ONLY.** Contains short verbatim SGK fragments for evidence (Founder D4);
not for distribution. Corpus: the **238 canonical TSLs**, `tc-v2/tc2-p1`, six Khoa học / KHTN
books, grades 4–9. Nothing here generalises to Toán, Tiếng Việt, LS&ĐL or Tin học — no canonical
TSL exists for them.

> **THE ONE-SENTENCE ANSWER.** Of the 118 blocks withheld because the app has no matching type,
> **I recommend adding a servable type for none of them** — and the same investigation found that
> **31 mutilated structures are served to children today**, two of them multiple-choice questions,
> one of which is mutilated *by this very type gap*; so the deliverable is the **all-or-nothing
> sibling rule**, built, measured, and **not switched on**.

**NOTHING BECAME SERVABLE.** With both new switches off, all **238** lessons emit **byte-identical**
documents to the pre-change bridge — 0 differences, measured, not asserted.

---

## 0 · PLANNED vs ACTUAL

| # | Planned | Status | Actual |
|---|---|---|---|
| S1 | Re-derive the 118 from leaf records | **DONE** | `tool/corpus/structured_gap_census.py`; 118 = footnote 64 · activity 50 · option 4, exactly |
| S2 | Inspect the 4 `option` blocks first and with most care | **DONE** | §2 — three independent reasons not to add the type |
| S3 | Decide `footnote` (64) | **DONE — RECOMMEND AGAINST** | §3 |
| S4 | Decide `activity` (50): genuine gap or `ROLE_MAP` mapping gap? | **DONE — it is a MAPPING gap, and I still recommend DEFER** | §4 |
| S5 | Bounded model change that improves truthful representation | **PARTIAL** | `BlockGroup` in `lib/core/lesson_model/` + group machinery in the bridge, **both inert by default**. PARTIAL because the machinery is built and **not applied** — that is the round's rule, and it is not DONE until a Founder throws the switch |
| S6 | Confirm nothing became servable | **DONE** | 238/238 byte-identical; `ROLE_MAP` untouched; guarded by tests |
| S7 | Defect 8 measured on the lesson path | **DONE — and it is worse than the option count suggested** | 31 mutilated structures, §1 |

**Never turned PARTIAL into DONE:** S5 is PARTIAL and stays PARTIAL.

---

## 1 · What the census actually found

`python3 tool/corpus/structured_gap_census.py --lessons poc-out/trusted-corpus/tc-v2/tc2-p1/lessons`

| | |
|---|---|
| lessons attempted / bridged / refused | 238 / 238 / 0 |
| gap blocks (`unknown_role:*`) | **118** — footnote **64** · activity **50** · option **4** |
| structural groups | **1 447** — `figure_caption` 1300 · `procedure_steps` 139 · `table_rows` 6 · `question_options` **2** |
| **mutilated structures served TODAY** | **31** — `procedure_steps` **29** (a LOWER BOUND) · `question_options` **2 of 2** |
| cost of the all-or-nothing rule | 31 → **0** mutilated, at **72** blocks (served 11 833 → 11 761) |

**Every multiple-choice group in the canonical corpus is mutilated. There are two of them, and both
are broken.** (MEASURED)

### Counterfactuals — adding the types does **not** fix this

| variant | mutilated | served | blocks un-withheld |
|---|---|---|---|
| TODAY | **31** | 11 833 | 0 |
| `+option` | 30 | 11 837 | 4 |
| `+activity` | **31** | 11 883 | 50 |
| `+footnote` | **31** | 11 897 | 64 |
| `+all three` | 30 | 11 951 | 118 |
| **TODAY + group rule** | **0** | 11 761 | 0 |
| `+all three` + group rule | **0** | 11 880 | 118 |

Adding all three types removes **one** of thirty-one mutilations. The group rule removes **all
thirty-one** and needs no new type at all. **The cheapest win on the board was not the types.**

*Re-derived a second way before recording it* (standing rule): the census computes these as
arithmetic on a disposition table; the bridge was then run over all 238 lessons actually producing
documents. **1 447 groups, 31 mutilated, 72 blocks — the two paths agree exactly.**

### Two limitations, stated where they were created, not in a footnote

1. **`procedure_steps` 29 is a LOWER BOUND.** A withheld region carries no text, and a procedure step
   is recognised by its enumerator *in the text*. A procedure whose missing step was withheld by the
   TSL cannot be seen at all. `test_a_mutilated_procedure_is_the_same_class_and_the_same_fix`
   demonstrates the blind spot rather than papering over it.
2. **The group rule does not fully repair the MCQ.** `repair/groups.py` defines `question_options` as
   a stem plus the *consecutive* option blocks. On KHTN 7 Bài 4 p32 the trailing directive
   «Hãy chọn đáp án đúng nhất.» sits **after** the options and is therefore outside the group — so
   even with the rule enforced the child would read a bare «choose the most correct answer» with
   nothing above it. **The group definition is incomplete, and extending it is doctrine I will not
   write on my own.** Recorded as an open item for the Founder / A1, not silently patched.

---

## 2 · `option` — 4 blocks · **RECOMMENDATION: DO NOT ADD THE TYPE**

Inspected first and with the most care, as instructed. There are **five** `option`-roled regions in
the corpus, not four: 4 TSL-TRUSTED (withheld by the type gap) and **1 withheld by `agree_text`** —
a distinction the 118 count hides.

### The two groups

**GROUP A — KHTN 7 Bài 4, p32 (printed 31).** Complete in the book: a stem, four options in a 2×2
grid, a directive. All four options TSL-TRUSTED, role confidence 0.95, `text_sim` 100.0.
What a child reads **today**:

```
[served]  «2. Bảng tuần hoàn các nguyên tố hóá học gồm các nguyên tố:»
[withheld × 4]  «máy chưa rõ đoạn này là gì»
[served]  «Hãy chọn đáp án đúng nhất.»
```

A question whose four answers are blank cards, followed by an instruction to choose the best one.
**This is round 5's defect 8 with the arrow reversed: the mutilation is not a withheld sibling of a
served option, it is the app's own missing type withholding every option of a served question.**
(MEASURED — `test_a_SOURCE_COMPLETE_mcq_is_mutilated_BY_THE_TYPE_GAP_ITSELF`)

**GROUP B — KHTN 9 Bài 27, p124.** Stem served; its single `option` region withheld with reason
`agree_text` — the two OCR stacks disagree. **A trust reason, not a type reason.** An `option` type
does nothing here. (MEASURED)

### Three independent reasons not to add the type

**(a) It converts a LOUD mutilation into a QUIET one.** Today Group A fails visibly: four blank
cards where four answers belong. A child, a parent or a reviewer can see something is missing. Add
the type and the failure mode changes shape: the day a trust threshold withholds one option of four
— which is exactly what already happens in Group B — the app serves **a three-option multiple-choice
question that looks complete**. A question with a missing distractor can have no correct answer, or
appear to have one when it does not, and nothing on screen says so. **The type does not remove the
danger; it removes the evidence of it.** (INFERRED, from the measured Group A/Group B pair)

**(b) The option letters were never covered by the agreement score the trust gate reads.** This one
is not an inference. In the SDM record for p32:

```
text_docling : "Kim loại và phi kim"          ← the primary stack's output
text         : "A. Kim loại và phi kim"       ← after enumerator restoration
enumerator_restored : true
agreement    : {"text_sim": 100.0, ...}
```

`tc2_sdm.py` computes `agreement(blocks, verifier)` at line 1193; the enumerator is prepended to
`b['text']` at line 1221 — **after**. So `text_sim = 100.0` certifies *«Kim loại và phi kim»*, and
says nothing about the *«A.»*. All four options have `enumerator_restored: true`.
**On a multiple-choice question the letter IS the answer's identity, and it is precisely the part no
agreement measurement covers.** (PROVEN — from the artefact and the source order)

**(c) The two stacks do not agree on the order of options C and D, and no guard fired.** The
verifier block ids aligned to A, B, C, D run **c005, c006, c008, c007**; option C and the trailing
directive **both** align to `c008`. In the verifier's own reading order D precedes C. `order_ok` is
`true` for every one of them and `agree_order` did not fire. The options are laid out as a **2×2
grid** — the two-column linearisation hazard round 5 measured. (OBSERVED, from the SDM artefact; I
could not re-derive `order_ok`'s value independently because `verifier_pos` is not persisted, so
this is OBSERVED and not PROVEN.)

### What I recommend instead

**The all-or-nothing sibling rule** (`--group-rule`, built, default off). It fixes Group A *and*
Group B *and* the 29 procedures, it needs no new type, and it can only ever withhold. It is not
switched on because switching it on removes 72 blocks a child reads today — the same shape of trade
as round 6's lost timeline, and the same person's decision.

**«Add it only with an all-or-nothing sibling rule» would still be wrong here**, because of (b): with
the rule *and* the type, Group A becomes a complete, served, four-option MCQ whose four option
letters are outside every measurement the trust gate makes. The rule is a precondition, not a
sufficient condition. **The correct order is: rule first, letters brought inside the agreement
measurement second, type last — and the type is a Founder gate either way.**

---

## 3 · `footnote` — 64 blocks · **RECOMMENDATION: DO NOT ADD THE TYPE**

A footnote served without its referent is its own mutilation, so I measured the anchor.

| | count | of 64 |
|---|---|---|
| mark is a well-formed «(N)» | 34 | 0.531 |
| …of those, **anchored to a SERVED non-footnote block** | **10** | **0.156** |
| mark is «(\*)» / «(\*\*)» — no numeric anchor possible | 12 | 0.188 |
| **mark itself OCR-mangled** — «(&nbsp;)» «(')» «("» «(i)» «®)» | **14** | 0.219 |
| no mark at all | 4 | 0.063 |

**Only 10 of 64 footnotes have a machine-resolvable referent in text a child can actually see.**
(MEASURED)

> **A number I had to re-derive before recording.** The first pass said 22 anchored. The difference
> is that 12 «anchors» were **other footnote-roled blocks anchoring each other** — a run of
> «(1)…(6)» blocks all carrying the role, each finding its own number in a sibling that is itself
> withheld. A footnote is never another footnote's referent. **10 is the true number**; the
> exclusion is now in the code with the reason written next to it.

### Worse: a large part of the bucket is not footnotes at all

15 of 64 sit under an `instruction` lead or immediately after a `caption` (MEASURED). Reading the
64 rows individually (judgement, stated as such — OBSERVED):

- **KHTN 7 Bài 9 p51 — five blocks are the PROCEDURE STEPS of an experiment**, under «Tiến hành:»
  («(1) Dùng tấm gỗ phẳng…», «(2) Lập bảng ghi kết quả…»). And **their reading order is inverted**:
  order 8 carries step **(4)** and order 9 carries step **(3)**. Serving these as footnotes would
  present an experiment's steps out of order, in the wrong role.
- **KHTN 7 Bài 9 p52 — six blocks are the CALLOUT LEGEND of Hình 9.3** («(1) Nam châm điện để giữ
  viên bi sắt.», «(2) Viên bi sắt.»). They are labels on a figure the app cannot show.
- **KHTN 7 Bài 19 p94 — three more figure callouts** («(1) Kim la bàn», «(2) Vỏ la bàn»).
- **KHTN 9 Bài 29 p134 — one is a chemical equation** whose subscripts OCR destroyed
  (`CSH ,O,CHO + 2AgNO, + 3NH,…`). That is round 5's **defect 1** class, in a bucket labelled
  «footnote».
- one is a question; two are periodic-table legend labels; one carries a destroyed exponent
  (`1 Ả = 10-10 m`).

**A role error is the one thing a new block type cannot fix — it renders the mistake more
confidently.** (INFERRED)

### And the app cannot render a footnote at all

Round 6 established it and I re-checked: **no rich text anywhere** — 0 of the **162** Dart files under `lib/`
use `RichText` or `TextSpan`, and there is no superscript. A footnote *is* a reference mark in the body
plus a note elsewhere. With no mark and, for 54 of 64, no locatable referent, a `footnote` type
would render as a paragraph that has been moved — **a presentation form becoming structure**, which
round 6 forbade explicitly.

### The negative result worth keeping

`footnote ⊂ referent` is a **fifth group kind that does not exist** in `repair/groups.py`. It is the
right shape for this content. **I do not recommend adding it**, because the anchor resolution it
would need measures **10/34 = 0.294** on well-formed marks and cannot even be attempted on the other
30. Recorded as a measured negative, not as future work with a number attached to it.

---

## 4 · `activity` — 50 blocks · **it IS a mapping gap · RECOMMENDATION: DEFER, with a named precondition**

**The brief's hypothesis is confirmed** (MEASURED). The block type already exists and already
carries **2 887** blocks (round 6's form census). `ROLE_MAP` maps four TSL roles onto it —
`objective`/`instruction`/`sidebar`/`stage_label` → `activity` with an `ActivityKind`. The TSL role
literally named `activity` has **no `ActivityKind` member**, and that is the entire gap. Adding one
would carry 50 blocks with **no new rendering, no new renderer family, no new semantics**. It is the
only one of the three that is genuinely cheap.

**And I still recommend deferring it, for one measured reason.**

**Five of the fifty are the publisher's colophon.** «Trình bày bìa: NGUYỄN BÍCH LA» — the
cover-designer credit — carries role `activity` in five books. That is round 5's **defect 6**
(imprint / back matter leaking into a lesson), unfixed, sitting inside the bucket. Mapping the role
serves a child five lines of a printer's imprint labelled as an activity.

**And the defect is much larger than these five** (MEASURED, and it is not mine to fix):

| where the imprint text sits | blocks | served to a child today |
|---|---|---|
| role `heading` | 17 | **yes** |
| role `body` | 5 | **yes** |
| role `activity` | 5 | no — withheld by the type gap |

**22 back-matter blocks already reach children as headings and paragraphs.** The type gap is the
only reason the other five do not. Defect 6 is open on the lesson path and larger than this
decision; the lesson-boundary fix (the last lesson of each book absorbs the colophon page) belongs
to the pipeline, not to a block type.

**Precondition for adding `ActivityKind.activity`:** defect 6 closed on the lesson boundary, *or* an
explicit back-matter exclusion at the boundary. There is a second, smaller coordination item: the
new kind needs a child-facing label, and `lib/features/**` is not this workstream's this round.

---

## 5 · The reason code still lies, and I did not change it

`unknown_role:footnote` says «the machine does not know what this is» about a block whose role the
machine assigned **at confidence 0.90 by lexicon**. Round 6 named that exact sin for `formula` and
fixed it with `no_carrier:formula`. The same fix applies to all three roles here.

**I did not apply it**, and the reason is measured rather than procedural.
`withheld_card.dart:24` matches `unknown_role` and says «máy chưa rõ đoạn này là gì»; renaming the
reason to `no_carrier:*` drops those blocks through to the default, **«SAM chưa chắc đọc đúng»** —
which asserts an OCR doubt that does not exist (`text_sim` median 100.0, `ocr_conf` median 1.0 for
all three roles). **Changing the reason without changing the wording makes the child-facing text
less truthful, not more.** `lib/features/**` is workstream R's this round.

**Coordination item, with the wording already worked out:** emit `no_carrier:{footnote,activity,option}`
**together with** a matching branch in `withheldReasonForChild` — something in the shape of «đoạn này
là ghi chú/hoạt động/phương án mà SAM chưa biết cách bày» — in **one** change, not two.

---

## 6 · PROVEN / FALSIFIED / STILL HYPOTHESIS

**PROVEN**
- All **238** lessons emit **byte-identical** documents with the new switches off. Nothing became
  servable. (0 byte differences across 238 lessons, both bridges run side by side)
- The option letters «A.»–«D.» were restored **after** the agreement score was computed, so
  `text_sim = 100.0` does not cover them.
- Four mutation checks on the new Dart guards each go red in the intended test and green on revert.

**MEASURED**
- 118 = footnote 64 · activity 50 · option 4, re-derived from leaf records.
- 31 mutilated structures served today; 2 of 2 MCQ groups mutilated; the rule takes it to 0 at 72
  blocks — agreed by two independent derivations.
- 10 of 64 footnotes have a resolvable anchor in served text.
- 22 imprint blocks are served to children today; 5 more sit in the `activity` bucket.

**FALSIFIED**
- *«118 blocks withheld because the CONSUMER has no type… these blocks passed every trust gate»*
  (round 6, WS-D). They passed the **TSL** gate and became `trustedStructuredLesson`, which round 3
  states explicitly is **not** production trust. For the four options the strongest available
  evidence — the agreement score — **does not cover the part that decides the answer**. The blocks
  are well-agreed; that is not the same as trustworthy, and round 5's third-signal work said so.
- *«the cheapest win on the board»* (round 6, §12). Adding all three types removes **1** of **31**
  mutilated structures. The cheap win was the group rule, which needs no type.
- My own first anchor number (22 of 34) was wrong: footnotes were anchoring each other. 10 is right.

**STILL HYPOTHESIS**
- That closing defect 6 would make `ActivityKind.activity` safe. Untested — 45 of the 50 were not
  individually audited for content, only for imprint.
- That the group rule's 72-block cost is acceptable to a child's reading experience. Not measured on
  a device; nobody has read a lesson with it on.
- That a `footnote_referent` group kind could be made to work with a better anchor rule.

---

## 7 · The plain answers

**How many of the 118 become truthfully representable?**
**Zero become servable.** **Four** — the KHTN 7 options — become truthfully **accounted for**: with
`--structural-groups` on they carry the group they belong to, and their question's mutilation
becomes countable at the model layer (`LessonDocument.mutilatedGroups`). The other **114 gain
nothing** from this work: 64 footnotes and 50 activity blocks belong to no structural group at all
(MEASURED — exactly one group in 238 lessons contains a gap block).

**How many do I recommend against adding, and why?**
**All 118.**
- **option 4** — the type converts a loud mutilation into a quiet one, and the option letters are
  outside the only measurement the trust gate reads.
- **footnote 64** — 54 of 64 have no resolvable referent, ≥14 are not footnotes but procedure steps
  or figure callouts (one set with inverted reading order), and the app has no rich text with which
  to render a footnote as a footnote.
- **activity 50** — a real mapping gap and the only cheap one, **deferred** rather than refused:
  5 of the 50 are the publisher's colophon, and defect 6 must close first.

**Did anything become servable?**
**No.** 238 of 238 documents byte-identical; `ROLE_MAP` unchanged; `LessonBlock.knownTypes`
unchanged; the group rule can only withhold; guarded by
`test_role_map_still_has_no_carrier_for_the_three_roles`,
`test_the_three_roles_still_reach_a_withheld_block` and
`test_group_machinery_is_off_by_default_and_the_bytes_do_not_move`.

---

## 8 · What the Founder is being asked to decide

1. **Switch on the all-or-nothing sibling rule?** It closes 31 teaching-critical errors — including
   both multiple-choice questions — and costs **72 blocks** a child currently reads. Round 5's
   doctrine already says a mutilated structure must never be served; this is the first chance to
   obey it where a child reads. `python3 tool/corpus/tsl_to_lesson_document.py --group-rule`.
2. **`question_options` does not include a trailing directive line.** Extending the group definition
   is doctrine. Reported, not resolved. (§1)
3. **The reason code `unknown_role:*` is false for these three roles**, and fixing it changes what a
   child reads, so it needs one coordinated change across `tool/corpus/` and `lib/features/`. (§5)
4. **Defect 6 is open and serving 22 imprint blocks to children today.** Out of scope here; it
   gates the one type addition that would otherwise be cheap. (§4)

---

## 9 · Reproducing every number

```
python3 tool/corpus/structured_gap_census.py \
    --lessons poc-out/trusted-corpus/tc-v2/tc2-p1/lessons --json <out> [--detail]
python3 tool/corpus/tsl_to_lesson_document.py --structural-groups [--group-rule] --no-crops
python3 -m unittest discover -s tool/tests -p "test_*.py"     # 760 green
flutter analyze && flutter test                                # clean · 1094 green
```

Files: `tool/corpus/structured_gap_census.py` (new) · `tool/corpus/tsl_to_lesson_document.py`
(`structural_groups_of`, `apply_structural_groups`, two switches, both default off) ·
`lib/core/lesson_model/lesson_document.dart` (`BlockGroup`, `BlockRelations.group`,
`LessonDocument.structuralGroups` / `hasGroupMeasurement` / `mutilatedGroups`) ·
`tool/tests/test_structured_gap_round7.py` (12) ·
`test/core/lesson_model/structural_group_test.dart` (10).

**DO NOT MERGE. Nothing here is activated.**

---

# ADDENDUM · FOUNDER DECISION — PRESERVE SOURCE VERBATIM (WS-S, 2026-09-06)

Received mid-round from the coordinator; it lands in files this workstream owns.

> **The 108 multi-word ALL-CAPS titles: display the source verbatim. Do not sentence-case when the
> transformation could lose or corrupt a proper noun.** This is a **fidelity fail-safe, not the final
> UX.** Normalisation may be researched later, but may only be **activated once proper-noun
> preservation is proven on a real population — not on a synthetic fixture.**

## What was implemented

| | |
|---|---|
| `displayTitle` | now the **identity**. One rule, one call site set, `lib/core/display/lesson_title.dart`. |
| the old transformation | kept as `sentenceCaseAllCaps`, **explicitly not activated**, with the activation precondition written next to it and a source-guard test asserting **no file in `lib/` calls it**. |
| the activation precondition | made **executable**: `titlesLosingCapitals(transform, titles)` returns the titles a transform strips capitals from. A normalisation may be proposed only when it returns **empty on the real population**. |
| **HO-1** | `LessonDocument.titleCase` **deleted**. `lessonLabel` delegates to `displayLessonLabel` — one rule, so the two cannot diverge on the day normalisation is activated. |
| **HO-2** | `NextAction.label` no longer returns «Về mục lục» when `view == null`; it returns **«Xem tiếp bài này»** — the same words as WS-R's `LessonNextKind.keepGoing`, so the two layers cannot contradict each other on one screen. The **`reason` was fixed too**: «đã đi qua … hoặc về mục lục chọn bài khác» → «Con đã mở đủ ba cách học SAM có cho bài này. Mở không phải là đã hiểu…». Fixing the label alone would have left the screen saying the sentence that caused the defect. |

## The measurement the decision rests on (MEASURED, real population)

Population: **every `title` in `assets/pack/lesson-index-g*.json`** — 2 623 titles, **2 382 unique**.
Not a fixture.

| | |
|---|---|
| ALL-CAPS titles | 190 |
| …single letter-word (acronyms — «GDTC 5») | 82 |
| …**multi-word — the Founder's 108** | **108** (107 unique) |
| titles the candidate normalisation **strips capitals from** | **107 of 107** |
| titles `displayTitle` changes | **0 of 2 382** |

Three named casualties, verbatim from the shipping pack:

```
ASEAN AND VIET NAM                        → Asean and viet nam
BÁC HÔ VỚI THIÊU NHI                      → Bác hô với thiêu nhi
CHIẾN TRANH VÀ HOA BÌNH TRONG THẾ KỈ XX   → … trong thế kỉ xx
```

An acronym, a person's name, a Roman numeral. **No shape-based rule separates them from ordinary
lowercase**, because Vietnamese does not encode «proper noun» in a word's shape. The only cure is
**data** — the printed table of contents (`lesson-title-v1`) or a sourced proper-noun lexicon — and
both sit upstream of display.

## The round's own lesson, turned into a test

WS-R found that `titleCase` stayed green for four rounds because **it was only ever fed ALL-CAPS
strings — only its own precondition**. A lowercasing function cannot go red on input that has no
lowercase to destroy. So the new suite has a **population-adequacy guard**: it asserts the test
population actually *contains* the cases that could make the rule red — mixed-case titles,
multi-word ALL-CAPS titles, acronyms embedded in a mixed-case title, Roman numerals. Degenerate the
population back to ALL-CAPS-only and **that guard goes red before the other tests can go quietly
green** (mutation-checked).

## Mutation checks — each red in the intended test, green on revert

| mutation | goes red in |
|---|---|
| `displayTitle` normalises again | the identity test, the 108-title test, the label test, WS-R's known-limitation test |
| the proof-obligation measure always returns empty | both proof-obligation tests |
| `NextAction.label` says «Về mục lục» again | both next-action tests |
| the `reason` invites leaving again | the 8-subset sweep |
| the population degenerates to ALL-CAPS only | **the population-adequacy guard** |
| the source guard reads prose as code | caught during construction — it now strips Dart comments, and a self-check asserts the scanner finds an identifier that really is in `lib/` |

## What this cost, stated

**«MỞ ĐẦU» now reads «MỞ ĐẦU» on screen, not «Mở đầu».** 108 lesson titles and some chapter names are
louder than they were. That is the price of the fail-safe and it is not hidden: a test pins it.

**13 tests across 6 files encoded the overruled premise** and were corrected in place, each expectation
moved to the string its own fixture actually carries — never loosened to a weaker matcher. One
*negative* assertion («the sentence-cased form must not appear») was deliberately **left lowercase**:
uppercasing it would have turned a guard into a tautology.

## Announced changes to `lib/core/**`

- `lib/core/display/lesson_title.dart` — `displayTitle` is now the identity; `isAllUpperCase` kept;
  `_letterWords` → **`letterWordCount`** (public); new `capitalsOf`, `titlesLosingCapitals`,
  `sentenceCaseAllCaps`.
- `lib/core/lesson_model/lesson_document.dart` — **`static String titleCase(String)` REMOVED.**
  `lessonLabel` kept, now delegating. New import of `../display/lesson_title.dart`.
- `lib/core/lesson_model/next_action.dart` — `NextAction.label` and the `seen.all` `reason` changed.

**Nothing became servable.** `ROLE_MAP` untouched; the bridge's default output is still **byte-identical
across all 238 lessons** (re-verified against the integration bridge after the merge); `trusted = 0`
remains a type invariant.

CI on the composed tree: `flutter analyze` clean · **1120** Dart tests green · **775** Python tests green.
