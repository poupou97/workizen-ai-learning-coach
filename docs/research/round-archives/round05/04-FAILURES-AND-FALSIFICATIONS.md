# 04 · FAILURES AND FALSIFICATIONS

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.** Verbatim SGK fragments below are quoted for
> defect attribution and are internal research material under Founder rule D4.

This is the most important file in the archive. Round 5's value is concentrated in what it
**disproved**, not in what it shipped.

---

## 1. THE GUARD-RELAXATION FAILURE — restore precision **0 / 1 = 0.000**

**Status: FAILED. Label: MEASURED + OBSERVED (blind judgement from a page render).**

One region was restored on the batch-2 legacy rerun by changing a guard. It is **wrong**.

Row `n20260906-0064` — `09-sgk-khoa-hoc-tu-nhien-9`, Bài 5, pdf p27, role `heading`, withheld by
`chem_guard`, which the Founder's 97-row audit had classed **OVER**-withheld.

- **Printed inside the box:** `II – Định luật khúc xạ ánh sáng`
- **Served after restore:** `I1 - Định luật khúc xạ ánh sáng Ô C. SỐNG`

**Two independent defects:**

1. **Roman `II` served as `I1`.** At 3× zoom the two printed glyphs are identical vertical
   strokes; the served second glyph carries a digit's top-left flag. **The OCR genuinely emitted
   `1`.** This is the Founder's own named defect from the 97-row audit, **still present after
   restore**.
2. **A watermark spliced into lesson text.** `Ô C. SỐNG` is a fragment of the faint diagonal
   series slogan «KẾT NỐI TRI THỨC / VỚI CUỘC SỐNG»; the bbox right edge overlaps it. **Page
   furniture served to a child as content.**

*Not counted against it:* the printed en dash `–` served as `-` is normalisation and would not
alone have made the row wrong. The role `heading` is defensible — **the text is what fails.**

**The structural finding.** Both defects sit at the **edges** of the bounding box — a mis-read
leading numeral and a trailing bleed from an overlapping layer. **The box geometry, not the
parser's core text, is what came back unrepaired.** Routed to Lane A4, which then confirmed it at
scale: **line-end tokens carry 3–4× the interior unattested rate (n = 486,000)**. The follow-on
refinement — "runs into the right margin" — was **falsified at 0.5×**. Both reported.

**The mechanism, in Lane D's own output file:**
`"restoreMechanism": "guard change in the pipeline build — NOT a repair. No REPAIRED stage ran."`

**Guard relaxation therefore stands at 1 of 19 falsely-withheld regions recovered, at 0.000
restore precision.**

### The counter-example on the same round

| Path | Restored | Precision |
|---|---|---|
| **Guard relaxation** (legacy batch 2) | 1 of 19 falsely-withheld | **0 / 1 = 0.000** |
| Verdicts transferred (legacy batch 1) | 4 of 12 falsely-withheld | **3 / 6 = 0.500** |
| **Validated math repair** (A2) | 10 | **10 / 10 = 1.000**, holdout **8 / 8** |
| History disposition repair (C) | 6 of 16, + 1 recovered event anchor | print-confirmed, **guard unchanged** |

**The difference between 0.000 and 1.000 is not effort — it is whether a deterministic validator
stood between the candidate and the child.**

**And the Founder's own audit labels predicted it.** Of the restores measured: **3 of 4** regions
the audit called **OVER**-withheld came back **correct**; **both** regions it called **SAFE
refusals** came back **wrong**. That is a usable routing rule — *restore from OVER, do not restore
from SAFE without a repair* — and independent evidence that the 97-row set is a sound evaluation
set.

---

## 2. R13 — SILENT LOSS: the structural finding of the round

**Status: DISCOVERED, OPEN. Label: MEASURED (two lanes, independently, from opposite ends).**

> A block whose role is `empty` reaches **neither** `blocks` **nor** `withheld` of the Trusted
> Structured Lesson.

Withholding is a decision a lesson can be audited for. **This is a disappearance, and it carries
no reason code.** Every rate published by every lane is blind to it: `learning blocks = trusted +
withheld` has already dropped it, so served share is computed over a base that shrank; and the
over-withhold rate cannot see it at all, because it reviews only regions that *were* withheld.

| batch | trusted | withheld | **silently lost** | of those, digits | expressions | served share as reported | **corrected** |
|---|---|---|---|---|---|---|---|
| batch 2 (evaluation set) | 232 | 135 | **27** | 17 | 8 | 0.632 | **0.589** |
| batch 1 (**holdout**) | 196 | 124 | **55** | 21 | 10 | 0.613 | **0.523** |

| lesson | trusted | withheld | silently lost | as reported | corrected |
|---|---|---|---|---|---|
| **Toán 4 tập hai Bài 61** | 4 | 15 | **32** | 0.211 | **0.078** |
| Toán 4 tập một Bài 37 | 23 | 24 | 15 | 0.489 | 0.371 |
| Toán 5 tập một Bài 6 | 12 | 13 | 9 | 0.480 | 0.353 |
| LS&ĐL 4 Bài 12 | 24 | 22 | 8 | 0.522 | 0.444 |

**The lost blocks are the printed exercises** — `40 613 + 47 519`, `3 675 + 2 918`,
`7 641 - 2 815`, `62 748 - 35 261`, `2 667 + 3 825`, `74 165 : 5`, the flattened `3 7 + 11 12`,
and A2's `7 8 2 8 7 - 2 8 5 8`. On LS&ĐL 4 Bài 12 they are map and table figures (`0,6`, `1408`,
`1010`) — **not a Toán-only effect.**

**The cause, with the line.** Formula-labelled blocks die as role `empty` for "no letters" at
`tool/corpus/tc2_sdm.py:276-277` — **14 of 15** Docling formula blocks on the Toán pages. The
reason code `empty_block` also **misstates what was lost**: it is stamped on a block reading
`7 8 2 8 7 - 2 8 5 8`. And **4 validated math restores are blocked by `empty_block` alone** —
half of A2's correct output held out by a **role** decision, not a math one.

**Every served-share figure elsewhere in this archive marked "as reported" is not withdrawn.**
Those figures correctly answer *"of the blocks the pipeline classified, what share did it
serve?"* They do **not** answer *"of what was extracted from the page, what share reached a
child?"* **Until this round nothing distinguished the two.**

---

## 3. THE LLM FINDING — recall 0.717 at a false-correction rate of **1.000**

**Status: FALSIFIED (as a proposer). Label: MEASURED, n = 60 already-correct rows.**

| | value |
|---|---|
| Detection recall | **0.717 — the best in the lane** |
| **False correction rate** | **1.000** |
| Corrections proposed on already-correct lines | 13 |
| …of which wrong | **13 of 13** |
| Share of clean rows flagged | 26.7 % |

**It finds real trouble and is wrong about the fix every single time.** This is the strongest
empirical statement of `LLM OUTPUT != TRUTH` the project has produced, and it is produced by the
pipeline's own instrument rather than argued.

**Verdict adopted into round 6 as a standing rule:** an LLM **MAY** detect an anomaly, route,
propose a candidate, and perform semantic review. It **MUST NOT** auto-correct canonical truth,
be a trust authority, or silently rewrite the corpus.

---

## 4. `prose-dated-events-v1` FALSIFIED — a Bài-8 shape, not a History rule

**Status: FALSIFIED by its own author (Lane C). Label: MEASURED across 28 lessons.**

LS&ĐL 5 prints **112 date mentions in eight forms**. The rule accepts **one** of them (21
parenthesised years) and extracts **3 events across 28 lessons**. Centuries (13), reign phrases
(12), un-parenthesised ranges (8) and bare TCN years are **invisible** to it.

Round 4 had measured the same rule at **7 events on Bài 8** and called it a History rule. It is a
**Bài-8 shape**. This is a direct warning against the «compile 3,679 lessons from a grammar»
plan: **a grammar validated on one lesson generalises to almost nothing, and only a census over
real date forms would have revealed it.**

**Why the events vanished in round 5 specifically:** `p039:000` — the single block carrying **all
seven dated events** — is withheld for `agree_tones` on **one token**: the primary reads «Bạch
**Đằng**», the verifier reads «đăng». **The human read of the printed page says the primary is
right.** Fail-closed is correct behaviour with only two stacks, and it costs the whole timeline.

### The same falsification, found twice more, independently

- **Lane E1, at 47× the scale.** Enumeration is a nearly closed form — **7 of 10 forms, coverage
  0.992** — which is why PROCESS reaches **104 / 224** lessons. Date is wide open — **3 of 12
  forms, 0.140**; LS&ĐL uses all twelve at 0.131, Địa lí 0.003 — which is **exactly** why
  TIMELINE reaches **3 / 224**.
- **Lane E2, on the gold set.** The sequence rule fires on **6 of 54** gold pages, **3 of them
  teacher books** (one a competency list whose order means nothing). Learner-facing precision
  **0.500**. **Toán, Tiếng Việt and Tin học produce nothing at all** — no upstream structure
  exists, and inventing a rule there would be the visual layer deciding meaning.

**Standing rule adopted from this: FORMS BEFORE RULES —
`FORM CENSUS → CLUSTER → REPRESENTATIVE EXAMPLES → RULE → HOLDOUT → MEASURE → GENERALIZE`.
Never infer coverage from a few examples.** `forms.py` runs in seconds; it would have caught this
before the rule was written.

---

## 5. `agree_tones` — the third signal that failed

**Status: FAILED as a repairer. Label: MEASURED.**

- Book-wide it cut trusted text **1,263 → 1,020** on LS&ĐL 5.
- On Bài 8 it withheld `p039:000` — **all seven dated events** — on a single token, **where the
  print says the primary stack was right**.
- Its dominant-majority variant reaches precision 0.889 / recall 0.533 at a **false-correction
  rate of 0.111**, and the false correction it proposes **rewrites a person's name** («Đặng Khoa»
  for the author).

**That is the empirical case for «a repair is never trusted by default», produced by the pipeline
itself rather than argued.**

**And round 4's falsification held again on new data:** the six remaining false-trust blocks on
Bài 8 are display-font headings at `text_sim` **100** with `agree_tones` **silent** — **A26
confirmed. Agreement is not verbatim.**

---

## 6. THE IDENTITY GUARANTEE WAS NOMINAL — retracted, then made structural

**Status: FALSIFIED, then FIXED. Label: PROVEN by mutation testing.**

E2's original guards checked that `VisualSpec` carries no `book` / `lessonNo` / `slotKey` field
and that `VisualRenderContext` carries no `LessonDocument`. **Both guards were green while every
element a renderer holds carried lesson identity inside a *value*.** Lane E1 found it while
adopting the same constraint.

Audited across all 5 built specs, every string, by JSON path: ids were clean (`process-1`,
`step-1`, `event-0`, `cell-0-0`, `derivationRule`, `family`, `kind`), but **`ProvenanceRef.blockIds`
leaked in every position** — nodes, edges, groups and `titleProvenance` — carrying values like
`06-sgk-khoa-hoc-tu-nhien-6:p062:synthetic:015`.
`if (n.provenance.primaryBlockId.startsWith('06-sgk-khoa-hoc-tu-nhien-6'))` was **one line away.**

**A field-name guard does not catch identity inside a value.**

**The fix is structural rather than another naming rule.** At the render boundary
`VisualRenderContext` replaces each `blockIds` value with an opaque handle (`h0`, `h1`, …) and
keeps the handle→ref map itself; `pageOf` / `openSource` resolve handles, so the provenance chain
is unchanged and **the artefact on disk keeps the real block ids** — that chain must stay
auditable. Only the renderer's view is redacted. **A renderer no longer *should not* read
identity; it has nothing left to read.** Verified by mutation: disabling the redaction fails 2 of
the 6 new tests, and the suite also pins that the leak still exists *in the artefact*, so the
guard cannot go vacuous.

A second latent channel closed at the same time: `VisualSection.id` was copied verbatim from
`SemanticData.id` — today `process-1`, but an upstream `khtn6-bai17-process` would have flowed
straight through. Compiler-minted ids are now constrained by **shape**.

**One channel stays open by necessity and is recorded rather than hidden:** `title` / `label` /
`detail` / `badge` carry the book's own words, which may say «Bài 22». That is **content the child
reads, not an identifier** — redacting it would delete the lesson from the screen.

### Two more provenance holes, found by tests that existed to look for them

1. **A sentence that was true in type and false in content.** «vì sao SAM chọn sơ đồ này» was
   keyed on the **Dart type**, so every `ProcessSemantic` was told the book used «·» bullets —
   Bài 17's own rule asserted as universal. **No test caught it: the type is right, the widget
   renders, the sentence is false.** Fixed by keying explanations on the **rule id**. This is
   exactly `TRACE ≠ EVIDENCE`, appearing in the explanation surface.
2. **Evidence strengthened itself through a file write.** A regression test caught a
   **save/load round trip upgrading a grounding from `inheritedFromEntity` to `cellStated`**.
   **Serialisation is a provenance-laundering channel.** Recommended as a general rule: every
   provenance-bearing type needs a round-trip test asserting grounding **never strengthens**.

---

## 7. THREE INTEGRATION DEFECTS NO PER-LANE CI COULD SEE

**Status: FOUND AND FIXED. Label: PROVEN — found by composing the round, not by any lane's CI.**

**1 · Lane B × Lane E2 — a compatibility claim true for readers, false for constructors.**
E2's provenance fix made `cells` required and kept `values` as a **getter**. That covers every
site that *reads* `values[i]` — genuinely true, and what E2 checked — but **a getter is not a
constructor parameter**. Lane B's new round-5 test held the repo's only such constructors, and
they did not exist when E2 measured. Fixed by building those sites through
**`SemanticData.fromJson`**, so the test now exercises the same parser the real fixtures use and
every cell inherits a checkable `ValueGrounding.inheritedFromEntity` — deliberately **not** by
adding a `fromStrings` convenience to `lib/core`, which would have made an unsourced cell
constructible again.

**2 · Lane A4 × Lane A2 — a loader that silently returned less than it was asked for.**
`verify.load_plugins()` registered by **module-import side effect**. Once A2's test legitimately
called `registry.reset()`, the modules were already in `sys.modules`, so re-importing was a no-op
and registration was never replayed. Minimal reproduction: `test_verify_signals` alone → 42 OK;
`test_mathfix_plugin test_verify_signals` → **FAILED**. A4 then proved the old path directly
rather than inferring it: **the old loader would have returned `signals = []`** — worse than the
diagnosis. The lone `G.llm_semantic` survivor was the tell, being the one module first imported
*inside* a test method. Fixed with an explicit idempotent `register()` per module and a
`load_plugins` that **verifies its manifest against the registry afterwards and raises
`RegistrationIncomplete`**, refusing a module that has no `register()`.

**3 · Lane E2 × Lane E1 — a guarantee that was nominal.** §6 above.

**The pattern, and why it matters more than the three fixes.** None of the three was visible to
the lane that owned it. Each was found either by **composing the round** or by **a second lane
adopting the same rule**. Two of the three — the silent registry and the identity leak — are the
same species as this round's headline data findings (**R13**'s disappearance with no reason code,
and grounding **strengthening itself** through a file write): *a component quietly delivering
something other than what it promised, with nothing checking.*

---

## 8. WHERE EACH NAMED DEFECT IS ACTUALLY BORN — attribution decides what to build

**Label: MEASURED against raw OCR output, not inferred from the served string.**

- **`3×10⁸ m/s` → `3×10° m/s` is born in OCR recognition, not normalisation.** The raw
  `poc-out/graph/ocr-body` line already reads `c = 3.10° m/s`; **no downstream step rewrites it**.
  The digits `3` and `10` survive — **the exponent's value dies at recognition**. The missing
  structured model is the second failure: nothing could have carried the exponent, and no guard
  covers scientific notation, so both stacks agree on the wrong character and it is served
  **TRUSTED**. **The fix is recognition on the crop, validated — not a parser, and not
  normalisation.**
- **`b) 3/10 + 5/21` → `b) 10 +` is born in recognition *and* serialisation.** The numerator `3`
  is absent from the OCR output entirely; the denominator `10` is glued into the enumerator token
  `b) 10 +.`. The geometry that would prove something is missing is then **discarded at
  `tc2_sdm.py:1060`** (spent on a verse boolean at `:1110`). **No text rule can reach it.**
- **`I1 - Định luật khúc xạ ánh sáng` is born in recognition, and survives because no signal
  checks sequence.** The book numbers its sections I, II, III; `I1` breaks a sequence observable
  elsewhere **in the same book**. The corpus carries its own evidence and nothing consults it.
- **`chem_guard` on a physics heading is born in guard design.** `CHEM` matches any capital run +
  digit. It fires **173×** in A2's review set with **≥40 non-chemical matches**: `S2` (**Ω**
  misread, 12×, all physics), `VD2` (teacher cross-reference, 9×), `I1` (Roman II, 4×), `A3`
  (paper size), `E5` (fuel). The Founder's other named defect, `1 MS = 1 000 000 S2`, is printed
  `1 MΩ = 1 000 000 Ω` — **a guard false positive and a destroyed symbol in the same line**.

---

## 9. THE RECOGNITION CEILING — 274 of 336, and why round 6's North Star changed

**Label: MEASURED.**

| Unrepairable fraction cause | count |
|---|---|
| **a fraction region the OCR could not read** (`numerator_token_missing` and kin) | **274** |
| everything else | 62 |
| **total** | **336** |

**274 of 336 — 82 % — is one problem: the OCR did not read the digit.** The ceiling is **274
unreadable regions, not validator strictness**. No parser, normaliser or agreement check can
reach text that was never captured.

Together with §8, this is why the next bottleneck is **recognition, not reasoning**.

---

## 10. A MEASURED NEGATIVE, KEPT WITH ITS EVIDENCE

**Running Lane A1's engine with Lane A4's signals end to end: 0 repairs, 0 false corrections** —
the independent-support rule held and nothing was rewritten. **But 4 blocks moved TRUSTED →
SUSPECT, 1 rightly and 3 wrongly: demotion precision 0.250.**

**This produced the round's most useful methodological rule, adopted as standing:**

> **`false_correction_rate` is the correct P0 for a *repairer* and is blind to a *detector*.**
> A lane that raises detection recall must report **false demotion rate** beside it — otherwise it
> scores perfectly by never repairing anything, while withdrawing correct content from children.

**And a second negative:** learning page furniture from repetition **fails** — the fuzzy cluster
containing `C SỐNG` also contained «đời sống.». The form that works is a **3-string publisher
registry plus a stray-single-letter guard**.

**And a third:** «Cộng hoà» → «Cộng hoa» — **the corpus writes the error 358× across ≥5 books**.
Every signal abstains, correctly, and this is now asserted as a test. It corroborates Lane A1's
independent finding from the other side (268 vs 303 pages). The doctrine it establishes:
**frequency is evidence about the corpus, not about the truth.** A majority vote over a corpus
that consistently mis-sets a diacritic will confidently propose the error.

---

## 11. A SCORING CORRECTION THE FOUNDER SHOULD SEE

For flattened formulas, **`false_correction` understates the harm**. A flattened expression is
always wrong *before*, so a bad repair is scored `still_wrong` (`false_correction = 0`) while
showing a child arithmetic the book does not contain. For the `formula_flattened` class the
honest figure is **`1 − correction_precision`**. **Any scoreboard that averages a
false-correction rate over a population containing formula rows is reporting a number that is
true and misleading at once.**

---

## 12. A PIPELINE REBUILD CAN DELETE A VISUAL FAMILY WITH NO RULE AT FAULT

**Label: MEASURED (E1).** 4 of 28 LS&ĐL lessons **lost** a family and **none gained** — while
`tc2-r5` had *more* trusted blocks. **Accuracy work can silently destroy semantic yield, and
nothing currently gates for it.** E1's recommendation: a **semantic-yield gate**.

Related, and sharper: **one tone slip deletes a family.** «Tiền hành» for «Tiến hành» → **0 Steps
instead of 5.** The distance between a working visual lesson and none is **one diacritic**.
