# ROUND 5 — DATA ACCURACY: REPAIR → VALIDATE → RESTORE
## Consolidated Founder report — 2026-09-06

> **Status: LIVE DRAFT.** Sections marked **[PENDING]** are awaiting a lane that is
> still running. Every number already printed here has been verified by the
> coordinator against the repository or against a page render, not relayed from a
> lane's summary. Where a lane's own wording was wrong, the correction is stated.
>
> **Nothing is merged.** Six round-5 PRs are open against
> `integration/round5-2026-09-06`, which is itself open against `main` as PR #79.
> READY FOR FOUNDER REVIEW.

---

## 0. The one-paragraph answer

The round's thesis was that `WRONG → WITHHOLD → DONE` is not a strategy and that
every failure class must move to `DETECT → REPAIR candidate → VALIDATE → RESTORE or
WITHHOLD`. The round produced the evidence that settles the alternative: **relaxing
a guard is not repair, and it does not work.** On the batch-2 legacy rerun the
pipeline recovered **1 of 19** falsely-withheld regions by changing a guard, and an
independent blind judgement of the single region that came back scored it **WRONG**
— restore precision **0 / 1 = 0.000**. The same run also shows the opposite result
is reachable: the one lane that built an actual repair path (A2, math) restored
**10 of 10 correct**, every one hand-verified against the printed page, with a
measured false-correction rate of **0** after the identity gap it found was closed.
The difference between 0.000 and 1.000 is not effort — it is whether a
**deterministic validator** stood between the candidate and the child.

---

## 1. What was verified first-hand by the coordinator

These were re-checked against the repository or a page render before being written
down, because a Founder report that relays a lane's claim inherits the lane's error.

| Claim | Source | Verdict |
|---|---|---|
| A single unrecognised block kind rejects the **entire** LessonDocument | `lib/core/lesson_model/lesson_document.dart:1017-1018` | **CONFIRMED** — `if (blk == null) return null; // một block hỏng ⇒ không tài liệu nửa vời`. This is deliberate fail-closed design (documented at `:9`), not a defect. Its consequence is a forward-compatibility constraint: a pack that emits a new block kind blanks the lesson on an older app. Packs and app must ship together. |
| The TSL→LessonDocument bridge has no `formula` role | `tool/corpus/tsl_to_lesson_document.py:71-82` | **CONFIRMED** — `ROLE_MAP` holds 11 keys, none of them `formula`; the string `formula` does not appear anywhere in the bridge. A validated `MathExpression` has **no path** from corpus to app today. *(Lane A2 cited this file as `tool/ui/…`; the path is `tool/corpus/…`.)* |
| The app has no rich-text capability at all | `lib/**`, `pubspec.yaml:35-42` | **CONFIRMED** — **0 of 147** Dart files contain `RichText`, `TextSpan` or `Text.rich`; no math, markdown, LaTeX, SVG or WebView dependency. A superscript or a fraction cannot render correctly even when the data is right. |
| Restore precision on the batch-2 rerun | blind judgement from page render, `poc-out/round5/legacy/batch-2-repaired/restore/` | **CONFIRMED 0 / 1 = 0.000 [0.000, 0.793]** |

---

## 2. RESTORE PRECISION — the round's most important number

**0 / 1 = 0.000.** One region was restored; it is wrong.

Row `n20260906-0064` — `09-sgk-khoa-hoc-tu-nhien-9`, Bài 5, pdf p27, role `heading`,
withheld by `chem_guard`, which the 97-row audit had classed **OVER**-withheld.

- Printed inside the box: `II – Định luật khúc xạ ánh sáng`
- Served after restore: `I1 - Định luật khúc xạ ánh sáng Ô C. SỐNG`

Two independent defects:

1. **Roman `II` served as `I1`.** At 3× zoom the two printed glyphs are identical
   vertical strokes; the served second glyph carries a digit's top-left flag. The
   OCR genuinely emitted `1`. This is the Founder's own named defect from the
   97-row audit, still present after restore.
2. **A watermark spliced into lesson text.** `Ô C. SỐNG` is a fragment of the faint
   diagonal series slogan «KẾT NỐI TRI THỨC / VỚI CUỘC SỐNG»; the bbox right edge
   overlaps it. Page furniture served to a child as content.

Not counted against it: the printed en dash `–` is served as `-`. That is
normalisation and would not alone have made the row wrong. The role `heading` is
itself defensible — the text is what fails.

**The structural finding.** Both defects sit at the **edges** of the bounding box —
a mis-read leading numeral and a trailing bleed from an overlapping layer. The box
geometry, not the parser's core text, is what came back unrepaired. That is a
generalisable signal and it has been routed to Lane A4 to measure.

**Honesty about the mechanism.** Lane D's own output file records it:
`"restoreMechanism": "guard change in the pipeline build — NOT a repair. No REPAIRED
stage ran."` The REPAIRED stage is running now against A1's newly-green framework;
guard-relax at **1/19 recovered, 0.000 precision** is the baseline it must beat.
**[PENDING — Lane D]**

---

## 3. The counter-example: what a validated repair path produces

Lane A2 (PR #84, CI green) built the missing structured math path and measured it.

| Measure | Result |
|---|---|
| Fraction detection (89 hand-counted printed fractions, 3 pages) | precision **1.000** [0.957–1.000], recall **0.955** [0.890–0.982] |
| Restored expressions, all hand-verified against the printed page | **10 / 10 = 1.000** [0.722–1.000] |
| …of which on the HOLDOUT (pages never opened while the rules were written) | **8 / 8 = 1.000** |
| Surviving false corrections | **0** |
| Fabricated expressions, before → after | 2 → **0** |
| Physics false trust | **−3 blocks**, at **0** over-withhold cost, across 36,029 blocks / 1,410 pages |
| Toán coverage (97 Toán pages, 2,692 blocks) | 0.1686 → **0.1705** |

Six deterministic validators justify each restore (`vinculum-raster-v1`,
`ink-accounted-v1`, `operator-raster-v1`, `structure-grammar-v1`,
`digit-provenance-v1`, `arith-selfcheck-v1`); RESTORE needs ≥1 PASS and no FAIL, and
all-abstain withholds.

**The finding of the round, and it is a warning.** Two wrong repairs were produced,
and **neither was found by a metric — both were found by looking at the page.**
`c) 16/21 × 3/5` came back as `16/21 - 3/5`, because Apple Vision returns a token
whose text is `-` for the printed `×`. Ink was fully accounted for, nothing was
invented, the grammar was sound, both vinculums were real. **Ink-accounting proves
completeness; provenance proves honesty; neither proves identity.** The same gap
produces `3×10⁸ → 3×10°`. It was closed by a glyph check, after which the printed
`×` is refused and the correct `b) 8/11 − 19/33` on the same row still restores.

---

## 4. Where each named defect is actually born

Attribution matters because it decides what to build.

- **`3×10⁸ m/s` → `3×10° m/s` is born in OCR recognition, not normalisation.**
  The raw `poc-out/graph/ocr-body` line already reads `c = 3.10° m/s`; no downstream
  step rewrites it. The digits `3` and `10` survive — the *exponent's value* dies at
  recognition. The missing structured model is the second failure: nothing could
  have carried the exponent, and no guard covers scientific notation, so both stacks
  agree on the wrong character and it is served **TRUSTED**. The fix is recognition
  on the crop, validated — not a parser, and not normalisation.
- **`b) 3/10 + 5/21` → `b) 10 +` is born in recognition *and* serialisation.** The
  numerator `3` is absent from the OCR output entirely; the denominator `10` is
  glued into the enumerator token `b) 10 +.`. The geometry that would prove
  something is missing is then discarded at `tc2_sdm.py:1060`. No text rule can
  reach it.
- **`I1 - Định luật khúc xạ ánh sáng` is born in recognition, and survives because
  no signal checks sequence.** The book numbers its sections I, II, III; `I1` breaks
  a sequence observable elsewhere in the same book. The corpus carries its own
  evidence and nothing consults it.
- **`chem_guard` on a physics heading is born in guard design.** `CHEM` matches any
  capital run + digit. It fires **173×** in A2's review set with **≥40 non-chemical
  matches**: `S2` (**Ω** misread, 12×, all physics), `VD2` (teacher cross-reference,
  9×), `I1` (Roman II, 4×), `A3` (paper size), `E5` (fuel). The Founder's other named
  defect, `1 MS = 1 000 000 S2`, is printed `1 MΩ = 1 000 000 Ω` — a guard false
  positive and a destroyed symbol in the same line.

---

## 5. Structural holes found, with the line that causes them

| Hole | Location | Consequence |
|---|---|---|
| Line geometry read, then discarded one step before the guards | `tool/corpus/tc2_sdm.py:1060`, spent on a verse boolean at `:1110` | The evidence a repair needs is thrown away before anything can use it |
| Formula-labelled blocks die as `empty` for "no letters" | `tool/corpus/tc2_sdm.py:276-277` | **14 of 15** Docling formula blocks on the Toán pages, one carrying `7 8 2 8 7 - 2 8 5 8`. The reason code misstates what was lost. **4 validated math restores are blocked by `empty_block` alone** — half of A2's correct output held out by a role decision, not a math one |
| ~~A `FORMULA` role buys trust 0.95 and waives the math/unit/chem guards~~ | was `tool/corpus/tc2_sdm.py:290-291` | **CLOSED — see §5.1** |
| Bridge has no `formula` role | `tool/corpus/tsl_to_lesson_document.py:71-82` | A validated `MathExpression` cannot reach the app |
| Provenance dropped on the pack path | `tool/ui/build_lesson_index.py` | **FIXED on `lane-d/round5-legacy-packs`, fail-closed — see §5.2** |


### 5.1 Founder STEM §4 — the latent formula trust hole is closed, and verified

Ordered in «FOUNDER DECISION — STEM STRUCTURED DATA» §4. Verified by the coordinator
against Lane A1's branch, in production code **and** in tests — not taken on report.

Before (`integration/round5-2026-09-06`, `tc2_sdm.py:290-291`):

```python
if b['role'] == 'FORMULA':
    return 'formula', 'native', 0.95, ['docling formula']
```

A label bought confidence 0.95, and `role_guards` then waived the math/unit/chem
guards for that role. The day Docling formula enrichment was switched on, formula
recognition would have become trusted teaching content silently.

After (`a1/round5-repair-framework`, `tc2_sdm.py:380-390`):

```python
structured = bool(b.get('formula_structured'))
return ('formula', 'native', 0.95 if structured else 0.60,
        ['docling formula'] + ([] if structured else ['structure NOT validated: label only']))
```

Four regression tests fix it in place (`tool/tests/test_repair_vi_defects.py`,
`class FormulaTrustHole`): a label alone does not buy confidence; an unvalidated
formula block is `WITHHELD` with reason `formula_unvalidated`; a formula label does
not waive the math/unit/chem guards; and the exemption is **earned by a validated
structure, not by a role name**. The test class states its own purpose: *"Dormant
today (Docling formula enrichment is off, FORMULA recall 0.000) — these tests exist
so that switching it on cannot silently turn formula recognition into trusted
content."*

**A convergence worth noting.** A1 gates the exemption on a `formula_structured`
flag; A2, working independently in another worktree, sets `formula_structured`
**only** from a validated structure. Two lanes arrived at the same contract from
opposite ends without coordination. The hole is closed by construction rather than
by luck, which is exactly what §4 asked for.


### 5.2 Founder STEM §3 — the unsafe legacy math path, closed by failing closed

Verified by the coordinator on disk and on Lane D's branch.

**The defect, re-confirmed live.** `tool/extract/rebuild_fractions.py:124` stamps
every row it writes `status: 'INFERRED'`, `method: 'geometric-fraction-rebuild-v1'`,
with the comment «dựng từ hình học ⇒ KHÔNG phải nguyên văn». All 41 rows carry it.
The pack builder copied only `expr / skillCaseId / page / book`. On the integration
branch's on-disk packs today: **g4 26 expressions across 6 lessons, g5 15 across 4
lessons — 41 in total, every one carrying exactly `['book','expr','page',
'skillCaseId']`** and no trace of `status` or `method`. Expressions rebuilt from
geometry shipped as if printed in the book, carrying a `skillCaseId` — that is, into
the exercise path a child is taught from. Same family as `b) 3/10 + 5/21` → `b) 10 +`.

**The fix, and why this shape.** The pack schema has no provenance field for an
activity and the app has no way to show an INFERRED caveat, so Lane D chose **fail
closed**: a non-verbatim upstream record is not emitted at all. Nothing is deleted
upstream, every drop is counted and logged with a reason, and the rows return the
moment provenance can travel with them. This is the correct call — the alternative
was to invent a provenance field on both sides mid-round, and shipping a caveat the
UI cannot display is not a caveat.

**Coverage consequence, stated rather than hidden:** 41 expressions leave the packs.
Per the Founder's rule that a coverage drop caused by removing wrong content is a
correctness gain, this is recorded as a gain, with the count named.

---

## 6. A design precedent worth adopting ecosystem-wide

Lane A2's `MathExpression` has `from_json` but **deliberately no `from_latex`**;
`latex` and `text` are computed properties with no setter. A rendering string cannot
become structure, so model-generated LaTeX cannot launder itself into truth.

This is the concrete mechanism behind `LLM OUTPUT != TRUTH`. It has been routed to
Lane E1 (SemanticClaim) and Lane E2 (VisualSpec) as a rule: **no constructor from a
presentation form.** Any `from_<rendered>` factory in the semantic layer is the hole
through which unvalidated content becomes trusted.

Related: `3×10°` has **no representation at all** in the AST — there is no degree
node — so the §6 "structurally impossible transformation" is impossible rather than
merely flagged.

---

## 7. A scoring correction the Founder should see

For flattened formulas, **`false_correction` understates the harm**. A flattened
expression is always wrong *before*, so a bad repair is scored `still_wrong`
(`false_correction = 0`) while showing a child arithmetic the book does not contain.
For the `formula_flattened` class the honest figure is **`1 − correction_precision`**.
Any scoreboard that averages a false-correction rate over a population containing
formula rows is reporting a number that is true and misleading at once.

---

## 8. Data Accuracy Scoreboard — BEFORE → AFTER

Lane D, PR #82, CI PASS on head `0113019`. Batch 2 is six lessons across five failure
classes and includes **History/Geography, never measured before**. Batch 1 is the
holdout.

| Founder direction | Round 4 | Round 5 REPAIRED | Note |
|---|---|---|---|
| **FALSE TRUST ↓** | 0.297 [0.199, 0.418] | **0.318** [0.218, 0.438] vs OLD **0.619** | 10/13 = 0.769 of batch 1's false-trust rows no longer served as before (was 7/13) |
| **TEACHING-CRITICAL ↓** | 0.176 [0.062, 0.410] | **0.100** [0.043, 0.214] vs OLD 0.476 | 2/5 closed; **9 and 13 mutilated structures unchanged** |
| **CORRECT SERVED ↑** | 221 served, ≈155 correct | **239 served**, ≈163 correct — 0.632 as reported, **0.589 once silent loss is in the denominator** | −8 colophon, +1 guard fix; **no served text changed** |
| **OVER-WITHHOLD ↓** | 12/30 = 0.400 | **19/30 = 0.633** [0.455, 0.781] | **Moved the wrong way.** 1 of the 19 restored |
| **RESTORE PRECISION ↑** | not measured | **3/6 = 0.500** [0.188, 0.812]; the one NEW restore is **0/1 — wrong** | |
| **ATTACHMENT** (added) | 5/8 = 0.625 rescued | **8/8 = 1.000 — closed** | Every attachment defect closed, credited to Lane A1 |
| Display fidelity | — | 0.595 → **0.164** | |
| Reading order | — | 0.455 → **0.000** | |
| Role | — | 0.116 → **0.151** | **Not better** |
| `trusted` / `eligible for teaching` | 0 / 0 | **0 / 0** | Unchanged, by design |

### 8.1 The result the Founder most needs to see: REPAIR is built and NOT CONNECTED

Attachment closed completely; **nothing else moved, and it could not have.** Lane A1's
Vietnamese repairers and group rule live in the repair harness
(`tool/corpus/repair/run_gold.py`) and are **not wired into the path that produces a
lesson**.

The coordinator verified this structurally rather than accepting it: on Lane D's
branch, **no file outside `tool/corpus/repair/` and `tool/tests/` imports the `repair`
package at all.** So "no served text changed anywhere" is not a measurement outcome —
it is a certainty of the current wiring. What reached the pipeline this round is two
guard/attach fixes.

This is the correct state given the Founder gate on production trust thresholds, and
it must not be read as accuracy having improved for a child. **The repair path is a
validated laboratory with a measured false-correction rate and no connection to the
product.** Connecting it is a Founder decision, not a lane's.

### 8.2 R13 — SILENT LOSS: the structural finding of the round

Two lanes found the same hole from opposite ends without coordinating. Lane A2 found
Docling formula blocks dying at `tc2_sdm.py:276-277` as role `empty` / reason
`empty_block` / evidence "no letters". Lane D checked it against its own denominators
and found something worse:

> A block whose role is `empty` reaches **neither** `blocks` **nor** `withheld` of the
> Trusted Structured Lesson.

Withholding is a decision a lesson can be audited for. **This is a disappearance, and
it carries no reason code.** Every rate published by every lane is blind to it:
`learning blocks = trusted + withheld` has already dropped it, so served share is
computed over a base that shrank; and the over-withhold rate cannot see it at all,
because it reviews only regions that *were* withheld.

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
`7 641 - 2 815`, `62 748 - 35 261`, `2 667 + 3 825`, `74 165 : 5`, the flattened
`3 7 + 11 12`, and A2's `7 8 2 8 7 - 2 8 5 8`. On LS&ĐL 4 Bài 12 they are map and
table figures (`0,6`, `1408`, `1010`) — **not a Toán-only effect.**

Every served-share figure elsewhere in this report is the "as reported" column. Those
figures are not withdrawn: they correctly answer *"of the blocks the pipeline
classified, what share did it serve?"* They do **not** answer *"of what was extracted
from the page, what share reached a child?"* Until this round nothing distinguished
the two.

**R13, filed to the pipeline lanes:** a block the role layer drops must arrive in the
TSL as a withheld region with a truthful reason, not vanish. `empty_block` on a block
reading `7 8 2 8 7 - 2 8 5 8` also misstates what was lost.

### 8.3 The 97-row audit's OVER/SAFE classification is predictive

Of the restores measured: **3 of 4** regions the audit had called **OVER**-withheld
came back **correct**; **both** regions it had called **SAFE refusals** came back
**wrong**. The Founder's own audit labels, applied blind, predicted restore outcomes.
That is a usable routing rule — restore from OVER, do not restore from SAFE without a
repair — and it is independent evidence that the 97-row set is a sound evaluation set.

## 9. Legacy Reprocess Scoreboard

**Pack rebuild (§13) — snapshot discipline enforced in code.** `packs.py`: a snapshot
never overwrites; a rebuild refuses unless a snapshot matches the packs on disk by
sha256; a restore re-checks every hash. Three snapshots under `poc-out/round5/legacy/`
(`packs-before-round5`, `-before-inferred-fix`, `-before-a1`), each with `SHA256SUMS`,
full `buildProvenance`, baseline metrics, pipeline version and README.

| Measure | Result |
|---|---|
| Pack `verify` | **0/12 FAIL → 12/12 PASS** |
| OLD baseline reproduced | **three times** — twice by `restore`, once by re-deriving metrics, identical to stored `BASELINE-METRICS.json` field for field |
| Content delta of the provenance rebuild | **exactly zero** (248/248 unchanged, 12/12 hashes identical), confirmed by byte-comparing canonical JSON independently of the tool |
| Blind badge audit of the diagnostic delta | **27/27 = 1.000**; four unbadged pages scored *unjudgeable*, and all three newly-flagged rows are among them — reported as **unmeasurable**, not as 0.964 |
| Founder §3 fail-closed | **−41 of 248** activities; 10 grades byte-identical; **10 lessons lose their exercise list entirely**; defect 6 on shipped packs **ABSENT** (0 of 207) |
| Tests | Dart **948 pass / 15 skipped**; Python **348 OK**; `flutter analyze` clean |

The zero content delta has a cause worth stating: `range_mismatch` is **counted, never
dropped**, so `capped-toc-v2` can only change the diagnosis, not the output.

**Surviving defects:** R1 **FIXED** and the class closed on a second book (tail-scan
1/6 → 0/6), credited to Lane A1. R2 and R3 **PRESENT** on a fourth build. R7c
**PARTIAL** — Lane D's own probe first reported it FIXED and the blind audit caught
the error.

**Two open items raised to the Founder, not decided by a lane:**

- **R15 — attach provenance does not reproduce.** The stored artefact differs from a
  fresh run on **950 of 6,176** page verdicts, 896 of them unexplained. Batch
  comparisons never touch it; the **pack build does**, and rebuilding against a fresh
  attach gives 207/207 and 12/12 identical. Filed as a Founder decision.
- **Defect 8 is not closed on the lesson path.** Lane A1 measures 7 → 0 on the gold
  set; Lane D measures **9 → 9** and **13 → 13** on the lesson path, with the Founder's
  option group byte-identical. Both lanes are right about their own population — the
  mutilated-structure class is closed where A1 looks and open where a child reads.

**Lane D's corrections against its own tooling** (recorded because they bear on how
much weight its other numbers carry): a false FIXED verdict on R7c; blank restore
sheets that the annotator refused to score, which is why there is no fabricated 6/6; a
sandbox guarantee that silently depended on alphabetical file order; an orphan detector
that **missed the exact case the Founder named** by grouping on the wrong field; and a
mechanism string that named a branch and went stale, now checked.

**Operational fact:** the main checkout's packs are still the old ones. **No APK built
on this Mac carries any of these corrections** until the PR is merged and packs are
rebuilt there.

## 10. The five product scores

**[PENDING — requires Lane B device evidence and Lane D packs]**

## 11. Answers to the Founder's ten checkpoint questions (§18)

**1 · DATA CHÍNH XÁC HƠN BAO NHIÊU?**
On the measured batches, substantially — but **not for a child yet**. False trust
0.619 → **0.318**; teaching-critical 0.476 → **0.100**; display fidelity 0.595 →
**0.164**; reading order 0.455 → **0.000**. Role went the wrong way, 0.116 →
**0.151**. Two counterweights that must travel with those numbers: over-withholding
got **worse** (0.400 → **0.633**), and the corrected served share, once R13's silent
loss is in the denominator, is **0.589** on the evaluation set and **0.523** on the
holdout rather than the 0.632 / 0.613 reported. `trusted` = 0 and `eligible for
teaching` = 0, unchanged and by design.

**2 · LỖI NÀO ĐÃ ĐƯỢC SỬA THẬT, thay vì chỉ withhold?**
Three classes were genuinely repaired, and one important thing was not.

- **Attachment — closed. 8/8 = 1.000.** Every attachment defect in the batch, fixed
  in the pipeline, plus the R1 class closed on a second book (tail-scan 1/6 → 0/6).
- **Math expressions — repaired and validated.** 10 restored, all hand-verified,
  including on a holdout; 2 fabricated expressions → 0; physics false trust −3 blocks
  at zero over-withhold cost across 36,029 blocks / 1,410 pages.
- **History dispositions — 6 of 16 withheld Bài 8 blocks became restorable**, every
  one print-confirmed, **with no guard changed**, recovering the events block and the
  «Âu Lạc (179 TCN)» anchor that round 4 had lost.
- **Not repaired:** the mutilated-structure class (defect 8) on the path a child
  reads — 9 → 9 and 13 → 13 — and the two named recognition defects `II` → `I1` and
  `3×10⁸` → `3×10°`, which are born in OCR and need recognition on the crop, not a
  parser.

**3 · BAO NHIÊU NỘI DUNG ĐÚNG ĐÃ ĐƯỢC RESTORE?**
Counted honestly and separated by mechanism, because the two differ by everything:

| Path | Restored | Precision |
|---|---|---|
| Guard relaxation (legacy batch 2) | 1 of 19 falsely-withheld | **0 / 1 = 0.000** |
| Verdicts transferred (legacy batch 1) | 4 of 12 falsely-withheld | **3 / 6 = 0.500** |
| Validated math repair (A2) | 10 | **10 / 10 = 1.000**, holdout **8 / 8** |
| History disposition repair (C) | 6 of 16, + 1 recovered event anchor | print-confirmed, guard unchanged |

**The lesson is in the first row against the third.** Relaxing a guard restored one
region and it was wrong. A deterministic validator restored ten and all ten were
right. And **the audit's own labels predicted it**: 3 of 4 OVER-withheld restores
came back correct; **both** SAFE-refusal restores came back **wrong**.

**4 · WRONG SERVED giảm bao nhiêu?**
False trust 0.619 → **0.318** on batch 2; **10 of 13** of batch 1's false-trust rows
are no longer served as they were (up from 7/13). On Lane C's independently
print-verified Bài 8 ledger, false trust **8 → 6** across 51 judged blocks. Two
fabricated math expressions → **0**. Physics false trust **−3 blocks**. And 41
geometry-rebuilt expressions stopped shipping as if printed.

**5 · CORRECT SERVED tăng bao nhiêu?**
221 → **239 served** (≈155 → ≈163 correct) on batch 2, and Lane C's correct-served
rose **26 → 30** on Bài 8 with false-withheld falling **14 → 10**. But this is the
number most at risk of being read too kindly, and R13 is why: **the served share is
0.589 corrected, not 0.632**, and on Toán 4 tập hai Bài 61 it is **0.078, not 0.211**.
Coverage also deliberately fell by 41 activities and 10 lessons lost their exercise
list entirely — recorded as a correctness gain with the count named.

**6 · THIRD SIGNAL nào thực sự có ích?**
Measured, and the answer separates cleanly. **[A4's systematic per-signal attribution
is PENDING.]**

*Signals that earned their place — all of them read physical evidence from the page:*
- **Raster / ink / geometry (A2):** `vinculum-raster-v1`, `ink-accounted-v1`,
  `operator-raster-v1`, `digit-provenance-v1`, `arith-selfcheck-v1`. Detection
  precision **1.000**, recall **0.955**; restore precision **1.000**.
- **Human verification against the print (C):** the single largest mover of both
  error directions on Bài 8 — false trust 8 → 6 and false withheld 14 → 10.

*The signal that failed, and it is the round's cautionary result:* **`agree_tones`.**
Book-wide it cut trusted text **1,263 → 1,020**, and on Bài 8 it withheld `p039:000`
— the one block carrying **all seven dated events** — on a single token, «Bạch
**Đằng**» primary versus «đăng» verifier, **where the print says the primary was
right.** Its dominant-majority variant reaches precision 0.889 / recall 0.533 at a
**false-correction rate of 0.111**, and the false correction it proposes **rewrites a
person's name** («Đặng Khoa» for the author). That is the empirical case for «a repair
is never trusted by default», produced by the pipeline itself rather than argued.

*And the round-4 falsification held again:* the six remaining false-trust blocks on
Bài 8 are display-font headings at `text_sim` 100 with `agree_tones` silent — **A26
confirmed on new data. Agreement is not verbatim.**

**7 · Legacy data có tiến gần teaching-ready không?**
Closer on measurable accuracy, **not closer to teaching-ready**, and the gap is
structural rather than a matter of degree. `trusted` = 0 and `eligible for teaching` =
0, unchanged. Three reasons, all of them now named: **the repair path is not wired
into the pipeline at all** (§8.1); **R13 means the denominators everyone reports are
not the population a child reads from**; and the mutilated-structure class is still
open on the lesson path. The pack machinery, by contrast, *is* ready — verify went
0/12 FAIL → **12/12 PASS**, the old baseline reproduced three times, and the rebuild's
content delta was **exactly zero**.

**8 · Bài 17 thật hơn ở đâu?** **[PENDING — Lane B]**

**9 · History đã phá/chứng minh gì?**
Lane C falsified its own round-4 rule, which is the most valuable thing it could have
done. **`prose-dated-events-v1` does not survive a different date style.** The book
prints **112 date mentions in eight forms**; the rule accepts **one** of them (21
parenthesised years) and extracts **3 events across 28 lessons**. Centuries (13),
reign phrases (12), un-parenthesised ranges (8) and bare TCN years are invisible to
it. **It is a Bài-8 shape, not a History rule** — a direct warning against the
«compile 3,679 lessons from a grammar» plan: a grammar validated on one lesson
generalises to almost nothing, and only a census over real date forms would have
revealed it.

It also proved the harder half of the doctrine: when the repair signal proposed
correcting an attribution, **two independent signals objected and the candidate was
rejected — so the attribution stopped being served rather than being half-corrected.**
That is `DETECT → REPAIR → VALIDATE → WITHHOLD` completing correctly.

**10 · Trẻ nhìn thấy sản phẩm tốt hơn ở đâu?** **[PENDING — Lane B device evidence.]**
One thing can be said now, and it should be said plainly: **no APK built on this Mac
carries any of this round's corrections.** The main checkout's packs are still the old
ones, and nothing merges. Every accuracy result in this report is a result about the
pipeline and the corpus, not about what a child currently sees.

---

## 11.1 Open P0 and the next bottleneck

**Next bottleneck — recognition, not reasoning.** Both remaining named defects
(`II` → `I1`, `3×10⁸` → `3×10°`) are born at OCR recognition; the digits and letters
around them survive. No parser, normaliser or agreement check can reach them, and
82 % of A2's unrepairable fractions (274 of 336) failed for the same reason: *the OCR
never read the digit.* The next real gain is recognition on the crop with
deterministic validation — not more rules over text that was never captured.

**Open P0, in the order they block things:**
1. **R13 silent loss** — a block the role layer drops must arrive as a withheld region
   with a truthful reason. Until then every published rate has the wrong denominator.
2. **Wire the repair path into the pipeline** — Founder gate; currently a validated
   laboratory with no connection to the product.
3. **R15 attach provenance does not reproduce** — 950 of 6,176 verdicts differ, 896
   unexplained; the pack build depends on it. Founder decision, not taken.
4. **Defect 8 on the lesson path** — closed where A1 measures, open where a child reads.
5. **Bridge has no carrier for validated structured STEM** — `ROLE_MAP` has no
   `formula`; the app union has no formula member and fails closed on the whole
   document.

---

## 12. Round-5 pull requests — all open, none merged

| PR | Branch | Lane | CI |
|---|---|---|---|
| #79 | `integration/round5-2026-09-06` → `main` | integration base | PASS |
| #80 | `lane-a3/round5-role-spec-trust-gate` | A3 role spec + threshold curve | PASS |
| #81 | `lane-c/round5-history` | Lane C History | PASS |
| #82 | `lane-d/round5-legacy-packs` | Lane D packs + legacy reprocess | PASS |
| #83 | `a1/round5-repair-framework` | A1 repair framework | PASS |
| #84 | `a2/round5-math-formula-accuracy` | A2 math / formula / number | PASS |

Lanes still running with pushed branches not yet raised as PRs: A4
(`a4/round5-multi-signal-verification`), Lane B (`lane-b/round5-experience`), E1, E2
(`e2/round5-visualspec-renderer`).

**No standing merge authority. READY FOR FOUNDER REVIEW.**
