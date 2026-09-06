# PHASE A — ROOT-CAUSE AUDIT OF THE 12 TEACHING-CRITICAL ERRORS

Founder order 47 §PHASE A · branch `audit/phase-a-root-cause`, based on `main` @ `6fd728d` ·
**No threshold was activated. Nothing was served. `trusted = 0` and `eligible for teaching = 0`
are unchanged.** No SGK page, crop, reading or served string appears in this document or in
anything this work committed.

---

## 0 · The one-paragraph answer

**The «segmentation is dominant» hypothesis is FALSIFIED on this population.** Segmentation is
the root cause of **exactly one** of the twelve rows. Role disambiguation is the root cause of
**five**, character/digit recognition of **four**, and **two of the twelve are not errors in the
served output at all** — one is an artefact of the evaluation matcher, one an artefact of the
digit tokeniser. Every one of the five role rows was proved by counterfactual to be a role-layer
defect: re-running `assign_role` on the same block with **perfect recognition** and again with
**perfect segmentation** returns the same wrong role. And the smallest upstream intervention is
therefore in the role layer, not in the recogniser and not in the SDM: a **question-promotion
veto** — three rules that refuse to promote a block to QUESTION when it already carries a
structural non-question signal — takes the served teaching-critical count from **12 → 7** and
false trust from **26 → 22** on this plane, **withdrawing nothing and breaking none of the 65
correctly-served questions**. That number is *in-sample* and is stated as such.

---

## 1 · The population, and that it is the right one

| | |
|---|---|
| evidence rows | **643** learning blocks with an anchor, 54 gold pages, plane `gold` / pipeline `tc2-p2` |
| served (`pipeline_trusted`) | **354** |
| teaching-critical in the served set | **12** |
| distinct served blocks those 12 rows sit on | **11** — two gold blocks match the same block |
| false trust in the served set | **26**, FTR **0.0734** |

**Re-derived a second way, twice.**

1. `tool/corpus/thresholds/evidence.py gold` was re-run from the SDM pages of
   `poc-out/round4/pipeline/tc2-p2/sdm-gold` and compared field by field against the published
   `poc-out/round5/lane-a3/evidence-gold-tc2-p2.jsonl`: **643/643 rows identical, 0 differing
   fields, identical order.** The published baseline (354 served / 26 wrong / FTR 0.0734)
   reproduces exactly.
2. The count of 12 was then derived a *different* way, from the two underlying flags rather than
   from `truth_teaching_critical`: `truth_digits_wrong` on served rows = **6**,
   `truth_as_question` = **6**, union = **12**, intersection = 0. This is the check round 7
   published and it holds.

**The pipeline code that produced the SDM is byte-identical between `main` @ `6fd728d` and the
checkout that holds the corpus** (`tc_score.py`, `tc2_sdm.py`, `tc_sdm.py`,
`thresholds/evidence.py`, `tc_gold/` — all `diff`-clean), so the audit runs against the code the
report is filed on.

---

## 2 · How each row was classified — the probes, not the output

The order is explicit that a root cause may not be inferred from the final string. Four probes
run per row, and each settles something no other probe can.

| probe | what it reads | what it settles |
|---|---|---|
| **MATCH INTEGRITY** | reproduces `tc_score.match`'s own decision for the row: anchor length, the level it matched at, how many candidates held the key, the IoU of gold box against served box, the best alternative candidate, and how many gold blocks share the candidate | whether the row is *about* the block the pipeline produced for that printed unit at all |
| **GEOMETRY** | how many SDM blocks have their centre inside the gold block's box; the served/gold text-length ratio; whether the evidence extension rule fired | whether the printed block was split |
| **RECOGNITION** | **three** independent layers that hold a reading of the page — the OCR line layer (`poc-out/graph/ocr-body`), Docling + ocrmac (the text the pipeline serves), and the XY-cut verifier — restricted to the gold block's box | for each glyph the served text lost: was it **read somewhere** (→ something downstream lost it) or **read nowhere** (→ recognition) |
| **ROLE COUNTERFACTUAL** | re-runs `tc2_sdm.assign_role` on the same block, in its real page context, with (a) the gold text — perfect recognition — and (b) the concatenated text of every SDM block inside the gold box — perfect segmentation | whether a role error can be blamed on a recognition or segmentation defect standing next to it |

The role counterfactual is what stops the double-count the order warns about. Two of the five
role rows sit on blocks that **are** split or **are** misread; the counterfactual shows the split
and the misreading are not causal, and the rows are classified once, at the role layer.

Script: `tool/corpus/audit/phase_a_rootcause.py`. It exits non-zero with `UNVERIFIED` when the
corpus, the served set, or the teaching-critical population is absent — **absence cannot satisfy
a positive obligation**, and this script cannot print a clean summary over an empty population.

---

## 3 · The twelve, one row at a time

**D4.** No printed or served string appears below. «Printed» and «served» are characterised by
*form* — what kind of unit it is and what kind of difference the pipeline introduced — never by
content. The values live only in the local, git-excluded detail dump.

### Class 1 · BLOCK BOUNDARY / SEGMENTATION — 1 row

**#4 · `09-sgk-khoa-hoc-tu-nhien-9` p046 `b01`** — trigger: digits.
*Printed*: a numbered two-sentence task; the second sentence carries a table reference containing
a digit pair. *Served*: the first sentence only, 224 of 299 characters.
*Chain*: geometry — **two** SDM blocks have their centre inside the gold box. Recognition — the
missing sentence **is present in the OCR line layer inside the gold box**, and present as a
sibling Docling item, and present in the XY-cut block; **no digit token of the gold sequence is
missing from any recognition layer**. It is served, in the neighbouring block. The evidence
extension rule did not rescue it because the served block is 0.75 of the gold length and the rule
fires below 0.70. Role counterfactual: unchanged (`body` under all three), so the co-occurring
role miss is not caused by the split either.
**Root cause: the SDM block boundary cut a printed paragraph in two.** Nothing was misread.
*Fix*: block assembly must keep a printed paragraph together, or the composition step that builds
a lesson document must re-join adjacent siblings before any completeness check reads the text.

### Class 2 · CHARACTER / DIGIT RECOGNITION — 4 rows

**#1 · `04-sgk-khoa-hoc-4` p009 `b10`** — trigger: digits.
*Printed*: a sidebar sentence containing a **stacked two-level common fraction**. *Served*: the
numerator alone; bar and denominator absent (a 2-character deletion mid-sentence, CER 0.0185).
*Chain*: geometry 1:1 — IoU **0.920**, one SDM block in the gold box, the same four OCR lines
inside block and gold box, nothing excluded. Recognition — the denominator token appears in
**none of the three layers**, and a whole-page search finds it in **no OCR line, no Docling item
and no XY-cut item on the page**. Role correct, guards empty, TRUSTED.
**Root cause: the denominator of a stacked fraction was never emitted by any recogniser.**
*Fix*: a recogniser that reads a stacked fraction as a unit — the WAL-213 targeted-re-crop family
— **plus** the missing joint that lets a recovered region reach the block text. WAL-213 measured
that second half as `Δ 0`.

**#2 · `07-sgk-khoa-hoc-tu-nhien-7` p021 `b14`** — trigger: digits.
*Printed*: a footnote opening with a bracketed reference numeral. *Served*: that numeral replaced
by a single punctuation character (CER 0.0128, 2 edits).
*Chain*: geometry 1:1, IoU 0.677, two OCR lines in both boxes. Recognition — **the OCR line layer
and the XY-cut verifier both read the numeral correctly; only the engine whose text is served did
not.** The agreement layer scored `text_sim = 99.3` and passed.
**Root cause: a character-recognition error in the served engine** — and the correct reading was
in the building at the time.
*Fix*: the smallest one is arbitration — allow a verifier's reading to supersede the primary's on
a digit. WAL-213's supersession relation is exactly this contract; it is wired to the **crop**
recogniser and not to the **page-pass** engines.

**#5 · `09-sgk-ngu-van-9-tap-mot` p067 `b05`** — trigger: digits.
*Printed*: a title carrying a superscript footnote reference. *Served*: the reference replaced by
punctuation (CER 0.10, 2 edits).
*Chain*: geometry 1:1, IoU 0.815, a single OCR line inside both boxes. Recognition — **all three
layers produce the same wrong reading.**
**Root cause: character recognition, agreed across every stack this system has.** This is one of
round 7's «survives character-exact agreement» cases, now named.
*Fix*: nothing in the current stack. A superscript-aware re-read, or a different engine.

**#6 · `09-sgk-ngu-van-9-tap-mot` p083 `b04`** — trigger: digits.
*Printed*: an uppercase step heading preceded by a **numbered badge** — a numeral set in a
coloured square. *Served*: the heading without the badge numeral (a leading 2-character deletion).
*Chain*: geometry — the served block's box **begins to the right of the gold box** (block `x0`
0.149 against gold `x0` 0.110), so the badge lies outside it. Recognition — **no OCR line, no
Docling item and no XY-cut item exists anywhere in that strip**; the page's only picture region is
elsewhere, so the numeral was not swallowed by a figure. Nothing was segmented away, because
nothing was read.
**Root cause: a numeral rendered as a graphic badge was not recognised by any layer.**
*Fix*: a re-read of page regions that carry ink but produce no text item — the generalisation of
the fraction re-crop, not the fraction detector itself.

### Class 3 · ROLE DISAMBIGUATION — 5 rows

All five are the same served failure — **a non-question served as a QUESTION** — and all five
survive both counterfactuals. `assign_role` returns the same wrong role given the gold text and
given the perfectly-segmented merged text. **Nothing upstream explains any of them.**

**#3 · `07-sgk-toan-7-tap-hai` p041 `b03`.** *Printed*: a short section header phrased as a
question; Docling labelled it `section_header`. *Served role*: QUESTION, evidence «ends with ?»,
confidence 0.92. Geometry 1:1, IoU 0.652. Counterfactual: `question` under both.
The heading rule (`tc2_sdm.py:491`) requires `not ends with '?'`, so **an explicit structural
label is discarded in favour of the question lexicon.** *Fix*: a `section_header`/`title` label
vetoes the question promotion.

**#7 · `09-sgk-toan-9-tap-mot` p029 `b01`.** *Printed*: a three-line remark paragraph opening with
a discourse marker. *Served role*: QUESTION, «leading directive verb». Geometry — the printed
paragraph **is** split into three SDM blocks. Counterfactual: **`question` again on the merged
text of all three**, so the split is not causal and this row is not classified as segmentation.
*Fix*: a remark / worked-example lead-in veto.

**#9 · `10-sgk-vat-li-10` p030 `b03`.** *Printed*: a worked example, opening with an explicit
worked-example label, whose statement is interrogative. *Served role*: QUESTION, «ends with ?».
CER **0.0** — the text is served perfectly. Geometry 1:1, IoU 0.881. Counterfactual: `question`
under both. Note ROLE-DEFINITION-SPEC-v1 §7 **R3** bears directly on this row.
*Fix*: the same lead-in veto.

**#10 · `10-sgk-vat-li-10` p030 `b19`.** *Printed*: a numbered learning-objective line inside a
labelled side box. *Served role*: QUESTION, «enumerator + directive verb», confidence 0.78 —
although the XY-cut verifier said SIDEBAR. Geometry 1:1, IoU 0.783. Counterfactual: `question`
under perfect recognition and perfect segmentation, but **`sidebar` the instant the box context
is set**. The box never opens because `SIDEBAR_LABEL` does not match the box's printed label —
and, measured, **the pattern misses 10 of the 19 such labels on the 54 gold pages**, including
the correctly-spelled Vietnamese form of this one: its character classes carry the plain and
circumflex vowels and omit the tone-marked ones. The rule fires mainly where the OCR is wrong.
*Fix*: the label pattern. Because it fails on correct input too, the tone error the OCR made here
is **not** the deciding cause and this row is classified at the role layer, once.

**#11 · `10-sgk-vat-li-10` p089 `b06`.** *Printed*: an imperative sentence under a numbered
procedure heading; the annotator judged it body. *Served role*: QUESTION, «leading directive
verb». CER **0.0**, geometry 1:1, IoU 0.808. Counterfactual: `question` under both. **No
structural signal distinguishes it, and no veto proposed below touches it.**
*Fix*: unknown. Adjudicate against ROLE-DEFINITION-SPEC-v1 §7 before anything is tuned on it.

### NOT A PIPELINE ERROR — 2 rows

**#8 · `09-sgk-toan-9-tap-mot` p029 `b13` — an evaluation-matcher artefact.**
The printed one-word heading **is** served, by a different block, **correctly, as `heading`, with
status TRUSTED**. The evaluation attached the gold block to an unrelated block: the anchor is
**1 token**, matched at level 1, **6 candidates contained the key**, and the IoU of the gold box
against the matched block is **0.000** while the correct block scores **0.581**. `tc_score.match`
prefers a candidate whose `order` exceeds the last match's; the previous gold block had already
matched order 17 and the correct block is order 16, so it was unreachable, and the lowest-order
candidate holding the token won. The same page shows the same shape a second time: another
candidate is matched by two different gold blocks.
**There is no defect in the served output.** *Fix*: the matcher — a one-token anchor must not
match, or must require geometric overlap. That is a change to the measurement, not to the product.

**#12 · `10-sgv-tin-hoc-10` p039 `b09` — a digit-tokeniser artefact.**
*Printed*: a sentence containing a signed number with the sign closed up to the digit. *Served*:
the same sentence with **one space** between sign and digit — CER **0.0056**, exactly one edit over
180 characters, and the sign itself is present in the served text. `tc_score.digits_seq` extracts
a dash only when it is adjacent to a digit, so the operator token is not extracted and
`digits_wrong` fires. **Re-deriving the served string with that single space removed reproduces
the gold token sequence exactly** — the difference is entirely in the tokeniser.
A real segmentation split does exist on this block (the gold unit spans two SDM blocks) and the
counterfactual confirms it causes a *role* error; it does not cause the teaching-critical verdict.
*Fix*: the tokeniser, or an explicit decision that a spacing difference around an operator is a
display error and not a teaching-critical one.

---

## 4 · Class distribution

| class | rows | share of 12 | share of the 10 real errors |
|---|---|---|---|
| **1 · BLOCK BOUNDARY / SEGMENTATION** | **1** | 8 % | 10 % |
| **2 · CHARACTER / DIGIT RECOGNITION** | **4** | 33 % | 40 % |
| **3 · ROLE DISAMBIGUATION** | **5** | 42 % | 50 % |
| **4 · COMPOSITION / GROUPING** | 0 | — | — |
| **5 · PIPELINE ORDERING** | 0 | — | — |
| **6 · UNKNOWN** | 0 | — | — |
| **NOT A PIPELINE ERROR** (measurement artefacts) | **2** | 17 % | — |

Nothing is double-counted. Three rows sit on a block that is *also* split or *also* misread
(#7, #10, #12); in each the counterfactual showed the co-occurring defect is not the cause of
the teaching-critical verdict, and the row is classified once, upstream, where the cause is.

Class 4 and class 5 are **empty on this population**, and that is a measurement, not an omission:
every row was tested for both. No row lost content because two recognised parts failed to be
grouped — the one grouping-shaped failure, #1, lost its second part before any grouping could see
it. And no row's verdict turned on the order of two **pipeline stages**: the round-7 finding that
option letters are restored *after* `agreement()` runs is real, but **no row in this population is
an option block**, so it explains none of these twelve. Row #3 does turn on *precedence between
two rules inside* `assign_role`, which is why it is class 3 and not class 5 — nothing would change
if the stages ran in a different order; the rule that loses is in the same function as the rule
that wins.

**The honest served-error count is 10, on 10 distinct blocks, not 12 on 12.**

---

## 5 · Verdict — the single smallest upstream intervention

### The recommendation

**A question-promotion veto in `assign_role`: three rules that refuse to return QUESTION when the
block already carries a structural non-question signal.**

| | rule | rows it removes |
|---|---|---|
| **P1** | a block whose native label is `section_header` / `title` is not promoted to QUESTION by the question lexicon (today the heading rule excludes anything ending in «?») | #3 |
| **P2** | a block opening with a worked-example or remark lead-in is not promoted to QUESTION | #7, #9 (+ #8, the artefact, incidentally) |
| **P3** | `SIDEBAR_LABEL` matches the labels as printed — its vowel classes currently omit the tone-marked forms, so it misses 10 of the 19 labels on this plane | #10 |

### Measured, before → after, on the whole 54-page plane

Both columns are **rebuilds** with the same code, so the comparison isolates the change. The
baseline rebuild reproduces the published population exactly: **12 teaching-critical, 6 digits,
6 as-question**.

| | BEFORE | AFTER (P1+P2+P3) |
|---|---|---|
| served (trusted) blocks | 356 | **357** |
| **teaching-critical rows** | **12** | **7** |
| — of them, digit-triggered | 6 | 6 |
| — of them, as-question-triggered | 6 | **1** |
| teaching-critical rate | 0.0337 | **0.0196** |
| false trust | 26 | **22** |
| FTR | 0.0730 | **0.0616** |
| correctly-served QUESTION blocks | 65 | **65** |
| blocks withdrawn | — | **0** |

Per component, each measured on its own: **P1 −1 · P2 −3 · P3 −1**, and **every one breaks 0 of
the 65 correctly-served questions**. The single highest-yield component is **P2**, one rule, −3.

### Why this and not the recogniser or the SDM

- **It is the only class with five rows**, and every one of the five was proved by counterfactual
  to need nothing from upstream: perfect recognition and perfect segmentation both leave the role
  wrong.
- **It needs no new signal.** P1 and P3 read fields already on the block (`native_label`, the box
  label); P2 reads the served string. No OCR change, no re-crop, no second engine, no threshold.
- **The recognition class cannot be fixed by one intervention.** Its four rows need four different
  mechanisms: a stacked-fraction reader (#1), cross-engine arbitration (#2), something no stack
  here possesses (#5), and a re-read of ink that produced no text item (#6). And WAL-213 already
  measured that recovering a region does **not** reach a repaired block — `Δ 0`.
- **The segmentation class has one row.** Even a perfect fix removes one.

### The honest caveat, stated before the number is used

The three rules were **derived from these five cases**. The −5 is therefore **in-sample**, and the
resulting rate of 0.0196 must **not** be read as beating round 7's «no signal combination bounds
teaching-critical below ≈0.021»: that floor was measured over signal combinations chosen without
seeing the rows, and this was not. It also remains **5.6× above BOUND-2's 0.0035**. Phase B must
measure the veto on the frozen blind populations (`BLIND-CORE`, `BLIND-TEACHING`) and report that
number beside this one.

**And before tuning: adjudicate.** All five role rows rest on gold role labels that have never
been put through ROLE-DEFINITION-SPEC-v1 §7 — the round-5 re-annotation sampled 26 rows and none of
these. That study measured raw annotator agreement at **0.769, κ 0.524** before spec adjudication
and a spec decidability rate of **0.885**. Tuning a role rule against unadjudicated labels is the
trap this project has already named: *role spec before tuning.* The adjudication is the first step
of Phase B, and it can move the count in either direction — #11 in particular may be a label
question rather than a pipeline question.

---

## 6 · Independent verification of the WAL-213 claims

Measured from `poc-out/round7/wal213/supersede-bai61.json` and `study-bai61-4scales.json`
(the study's recorded `sha256` matches the file on disk), not from the document.

| claim | verdict | measurement |
|---|---|---|
| **13 of 17 recovery failures are token contamination / bad boundary; coverage 0.05…0.55, none near any threshold** | **CONFIRMED** | 17 supersessions · 13 PARTIAL → CONFLICT, 4 FULL → SUPERSEDED. Refusal coverage fractions `0.0512 … 0.5505`; every acceptance is exactly `1.00`. Refused by class DIGIT_LOSS 7 · SEGMENTATION 6; resolved FRACTION_STRUCTURE 2 · DIGIT_LOSS 2. **Composition of the 13, which the document does not give**: an operator in a destroyed value **9/13**, an item-letter pattern **5/13**, a digit **13/13**, and **3/13** would have to destroy *two* observations, not one. |
| **numerator and denominator split across different SDM blocks** | **CONFIRMED, and stronger than stated** | Taking each of the 4 resolved regions and asking which SDM leaf block holds each half: **3 of 4 are split.** One has numerator and denominator in two different leaf blocks (the case the document names). In a second the numerator falls in **no leaf block at all** — only the page-wide figure. In a third the denominator's centre falls inside **two overlapping** leaf blocks. Only one of the four has both halves in one block, and that one failed for the other reason the document gives. |
| **the recogniser had ≥2 agreeing scales plus a stacking observation in every resolvable case** | **CONFIRMED, and stronger than stated** | True for all **4** resolvable cases — and true for **all 17 recovered regions**, refusals included: minimum agreeing scales is **2** on both halves in every one, and **17/17** carry a stacking observation. Agreement was never the limiter for any of the 17, not merely for the 4. |
| **the supersession contract works as a relation, not a mutation** | **CONFIRMED** | `Supersession` is a frozen dataclass; `disposition`, `coverage` and `servable` are derived **properties** with no setter; `servable` returns False; there is no `from_text` / `from_line` / `from_reading` / `from_latex` / `from_summary`; no statement in the module writes to a superseded observation. 75 contract tests pass on this branch, including the `assertIs` that proves the original object is carried rather than copied. |
| **block-level `Δ 0` is real** | **CONFIRMED** | Over the 44 blocks: blocks carrying a proposed value **BEFORE 2 · ADD 3 · SUPERSEDE 2**; blocks whose SUPERSEDE value differs from BEFORE: **0**. 8 blocks refused with a named reason. The single block the ADD path changed is the one the contract refuses. |

Round 7's own headline was checked too. **«3 of the 6 digit corruptions survive character-exact
agreement between two independent OCR stacks» — CONFIRMED**, and this audit can now say which
three and what the other three are: #1, #5 and #6 are read wrongly (or not at all) by **all three**
layers; #2 is read **correctly by two of three** and wrongly by the one that is served; #4 is read
correctly by all three and lost at a block boundary; #12 is not a corruption.

---

## 7 · Where a document and the data disagree — the data wins

1. **`SUPERSESSION-CONTRACT-WAL213.md` §8** states that «`FULL_COVERAGE = 0.98` and
   `TOUCH_COVERAGE = 0.05` … on this population nothing sits near either (0.55 is the highest
   refusal, 1.00 the lowest acceptance)». **The code says `TOUCH_COVERAGE` is not on the coverage
   path at all**: `Supersession.coverage` returns `PARTIAL` for any fraction `> 0.0` and `NONE`
   only at exactly zero; `TOUCH_COVERAGE` is used in one place, `_assert_no_overlap`, comparing
   the envelopes of two *competing* regions. And the lowest refusal, `0.0512`, sits **2.4 % above**
   the number the sentence says nothing is near. **The conclusion survives — no result here
   depends on either constant — but the reason given for it is wrong.**
2. **`TRUST-CALIBRATION-ROUND7-REPORT.md` and `NEXT-RESEARCH-DIRECTION.md`** both carry «all 12
   teaching-critical errors fall into exactly two mechanisms — digit corruption (6) and a
   non-question served as a question (6)». The count is right and the mechanisms are right, but
   **2 of the 12 are not errors in the served output**, and the 12 rows sit on **11** distinct
   served blocks, not 12. The honest figure to carry forward is **10 served errors on 10 blocks.**
3. **`NEXT-RESEARCH-DIRECTION.md`** concludes «the blocker is recognition and role
   disambiguation, not calibration». **Confirmed on the direction, corrected on the ordering**:
   role is the larger half (5 rows against 4), it is the half that needs no new signal, and it is
   the only half where one intervention removes more than one row.

---

## 8 · PLANNED vs ACTUAL

| # | Planned | Status | Actual |
|---|---|---|---|
| 1 | Trace all 12 errors through source → geometry → SDM block → recognition → repair → role → serving | **DONE** | 12/12, four probes each; `tool/corpus/audit/phase_a_rootcause.py` |
| 2 | Classify each into the six classes, from measurement rather than from the output | **DONE** | 1 · 4 · 5 · 0 · 0 · 0, plus 2 rows that are not pipeline errors and are reported as such rather than forced into a class |
| 3 | Do not double-count | **DONE** | 3 rows carried a second, co-occurring defect; the counterfactual decided each, and each is classified once |
| 4 | Independently verify the five WAL-213 claims | **DONE** | §6. All five confirmed; two are stronger than the document claims |
| 5 | Name the single smallest upstream intervention | **DONE** | §5, with a measured before → after and a per-component yield |
| 6 | Say plainly if «segmentation is dominant» is falsified | **FALSIFIED, and said first** | 1 of 12. §0 |
| 7 | Re-derive every count a second way before publishing it | **DONE** | the 643 rows re-derived field-by-field; the 12 re-derived from the underlying flags; the veto measured as rebuild-vs-rebuild, not against the stored artefact |
| — | Implement the intervention | **NOT STARTED — correctly** | Phase B. Nothing in this branch changes the pipeline; the veto exists only as a measurement harness |
| — | Adjudicate the 5 role rows against ROLE-DEFINITION-SPEC-v1 §7 | **DEFERRED to Phase B** | It is the first step there, and it can move the count in either direction |
| — | Measure the veto on `BLIND-CORE` / `BLIND-TEACHING` | **NOT STARTED** | Deliberately. The rules were derived from these rows; the blind measurement is the honest one and belongs to Phase B |

**Nothing was promoted from PARTIAL to DONE.**

---

## 9 · Claims by label

| label | claim |
|---|---|
| **PROVEN** | the served population re-derives byte-identically from the SDM pages; row #8's printed unit is served correctly by another block, so the row is not a pipeline error; row #12's gold digit sequence is reproduced from the served string by deleting one space; the five role rows return the same wrong role under perfect recognition **and** perfect segmentation |
| **MEASURED** | the class distribution 1 · 4 · 5 · 0 · 0 · 0 + 2; per-layer glyph presence for all six digit rows across three recognition layers; `SIDEBAR_LABEL` misses 10 of 19 labels; the veto's 12 → 7, 26 → 22, 0 withdrawn, 0 broken; every figure in §6 |
| **OBSERVED** | that the two artefact rows are instances of general shapes — a non-injective matcher with a one-token fallback, and an operator tokeniser sensitive to spacing — rather than one-offs; the same page shows a second many-to-one match |
| **INFERRED** | that row #1's printed unit is a stacked fraction (the shape of the loss and the absence of the denominator from every layer say so; no crop was inspected); that row #6's numeral is set as a graphic badge |
| **HYPOTHESIS** | that this class distribution transfers off these 54 deliberately hard pages; that the veto's yield survives on the frozen blind populations |
| **UNKNOWN** | whether the five gold role labels survive adjudication under ROLE-DEFINITION-SPEC-v1 §7; what fixes row #11; how many teaching-critical errors the audit plane (as opposed to this reference plane) holds, and of what classes |

---

## 10 · The traps this project has hit, and what was done about each

- **«A number of the right type and the wrong quantity passes every check that is not a
  re-derivation.»** Every count here is derived twice by different routes: the 643 rows against
  the published file field by field; the 12 from `truth_teaching_critical` and again from the two
  underlying flags; the veto's effect as a **rebuild-versus-rebuild** delta rather than against the
  stored SDM — because the stored artefact and a fresh build differ by 2 served blocks from code
  drift in `FORMULA` handling since round 4, and comparing across that difference would have
  attributed 2 blocks to the veto that it did not cause.
- **«Absence cannot satisfy a positive obligation.»** The audit script refuses to run — non-zero,
  `UNVERIFIED` — when the corpus, the served set or the teaching-critical population is missing. It
  has no code path that prints a clean summary over nothing.
- **«Test populations must contain the failing case.»** Two findings here are that exact shape,
  found in the product rather than in a test: `SIDEBAR_LABEL` matches the OCR-corrupted spelling of
  a label and not the correct one, so it fires **only where recognition is wrong**; and the role
  counterfactual only produced its answer because it was run on the real page context, with the
  real neighbours, rather than on a synthetic block.
- **One hypothesis of my own was falsified mid-audit.** I first proposed that row #10 was a
  recognition error — a tone slip in the box label destroying the box context. Measuring it showed
  the pattern misses the **correctly** spelled label too, so correcting the recognition alone
  changes nothing (measured: Δ 0), and the row belongs to the role layer. It is recorded as class 3
  for that reason and not for the reason I first wrote down.

---

## 11 · Files, and how to reproduce

| file | what |
|---|---|
| `tool/corpus/audit/phase_a_rootcause.py` | the chain tracer and its four probes |
| `docs/research/PHASE-A-ROOT-CAUSE-AUDIT.md` | this report |

```
python3 tool/corpus/thresholds/evidence.py gold \
    --sdm poc-out/round4/pipeline/tc2-p2/sdm-gold --out <ev.jsonl>     # re-derive the 643 rows
python3 tool/corpus/audit/phase_a_rootcause.py \
    --evidence <ev.jsonl> --sdm poc-out/round4/pipeline/tc2-p2/sdm-gold \
    --out <census.json> --detail <local-only.json>                     # the 12, traced
```

The census carries ids, counts, classes and booleans. **Every reading goes to `--detail`, which is
D4 and never enters git.** The measurement inputs (`poc-out/**`) are git-excluded by design.

---

`trusted = 0` · `eligible for teaching = 0` · **no threshold activated** ·
**segmentation is not the dominant cause — role disambiguation is.**
