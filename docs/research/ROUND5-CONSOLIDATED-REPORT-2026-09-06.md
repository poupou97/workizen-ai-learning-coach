# ROUND 5 — DATA ACCURACY: REPAIR → VALIDATE → RESTORE
## Consolidated Founder report — 2026-09-06

> **Status: COMPLETE.** All nine lanes have reported. Every number here was verified
> by the coordinator against the repository, against a page render, or by running the
> suites — not relayed from a lane's summary. Where a lane's own wording was wrong or
> over-strong, the correction is stated in place rather than the claim quietly dropped.
>
> **Nothing is merged.** Nine round-5 PRs are open against
> `integration/round5-2026-09-06`, which is itself open against `main` as PR #79.
> The composed round was verified in a throw-away worktree (§11.3): **0 conflicts,
> `flutter analyze` clean, 623 Python tests OK, 1061 Dart tests pass.**
> **READY FOR FOUNDER REVIEW.**

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
stage ran."` Guard relaxation therefore stands at **1 of 19 falsely-withheld regions
recovered, at 0.000 restore precision.**

**The REPAIRED stage then ran against A1's framework, and changed nothing served.**
It closed attachment completely (8/8) and fixed the R1 class on a second book, but
**no served text changed anywhere** — see §8.1, where that is shown to be a structural
certainty of the wiring rather than a measurement outcome.

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

## 10. The five product scores — never averaged

Lane B, **PR #87**, CI pass (2m16s), `flutter analyze` clean, `flutter test` **995
passed / 1 skipped**. Device: **Nokia 6.1, «Na · Lớp 6», 5 iterations, 36 frames, 28
steps, 0 downgraded.**

| Score | Round 4 | Round 5 | Basis |
|---|---|---|---|
| **Experience Fidelity** | 80–85 % | **85–88 %** | Trực quan **70–80 % → 85–90 %** (reached the board), Bookshelf 65–75 % → 80–85 %, Book 70–80 % → 80–88 % |
| **Source Reality** | 97 | **97** | unchanged |
| **Source Trust** | 0 / 97 | **0 / 97** | unchanged — no trust threshold set, by Founder gate |
| **Pedagogy Reality** | 7 / 17 | **7 / 17** | unchanged |
| **Evidence Reality** | 0 of 0 | **0 of 0** | unchanged |

Only Experience Fidelity moved. The four data-side scores are flat, and §8.1 is why:
the repair path is not wired into the product, so nothing this round could have moved
Source Trust or Pedagogy Reality even in principle.

### 10.1 The Lesson Workspace duplication problem — measured, then fixed

The Founder's complaint («thấy lặp lại, quá nhiều biểu diễn của ba Learning View, SAM
chiếm chỗ cố định, CTA trùng») was quantified two independent ways before anything was
designed:

- Widget tree at the exact Nokia viewport (392.7 × 698.2 dp): pinned chrome in «Học
  với SAM» = **411 dp = 58.9 % of the viewport**, with **7 occurrences** of the three
  view names on one screen.
- On the device, real Bài 17 fixture, template match error 0.0: **first lesson content
  at y = 820 px — 42.7 % of the screen consumed before content.**

A 13-entry duplication map found **4 genuine duplicates**: the picker's SAM bubble; the
view-changing CTA on the recommendation card, repeating the tab directly above it;
SAM's portrait where SAM is not speaking; and the tutor end-card's «Về mục lục». Plus a
finding nobody had named: the three views carry **two different word sets** — «Học
**với** SAM» on the tab versus «Học **cùng** SAM» on the card — **six labels for three
things.**

**Three substantially different concepts, four builds from one commit**
(`--dart-define=WAL_ASSIST=…`, default = current behaviour):

| | first content (device) | % screen | view labels | «why» in place |
|---|---|---|---|---|
| CURRENT (card) | 820 px | 42.7 % | 7 | 0 taps |
| A · icon | 634 px | 33.0 % | 3 | 1 tap (sheet) |
| **B · peek** | **712 px** (634 collapsed) | 37.1 % | 4 | **1 tap, in place** |
| C · inlineTab | **565 px** | **29.4 %** | 3 | **none** |

**Recommended: B — and deliberately not on pixels.** C is tightest but leaves only a
symbol; A does the same *and* pushes the lesson title onto two lines. Only B states the
destination at **zero taps** («SAM gợi ý: Xem Đọc»), returns 186 px once dismissed, and
has three genuine states COLLAPSED → PEEK → EXPANDED with re-peek when the
recommendation moves to a different view. Space saved 820 → 712 px peeking (−13.2 %),
→ 634 px collapsed (−22.7 %); labels **7 → 4**; the duplicate CTA, the portrait and the
«Đã mở ● ○ ○» row are gone. AI discoverability is **better**, not traded away.

Pinned by test: no second recommendation engine (a source grep bans `LessonDocument` /
`WorkspaceTrace` / `nextActionFor` inside `assist_layer`), no option may hide the
recommendation in any of the three views, 48 dp targets and screen-reader labels.

**This is a Founder choice, not a lane's.** A / B / C are all built and measured.

### 10.2 Five defects the device found that no test did

**D1** the pinned card hid the mindmap's hub (48 % → 27 % chrome) · **D2** the «why»
said «bảng» while showing a mindmap · **D3** 54 «chưa có» rows buried the one SAM
lesson · **D4** a 21 dp badge floating between tabs · **D5** dismissing made SAM vanish
entirely. All five fixed and re-walked. Protocol held: idle checks compared
**per-pixel**, so a clock tick was distinguishable from the Founder picking up the
phone, and one frame that caught the profile sheet was deleted.

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
Measured per signal, and the answer separates cleanly. Full attribution in §11.5.

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

**8 · Bài 17 thật hơn ở đâu?**
In what it now *shows*, not in what it claims. Typed `SemanticData` renders as a real
**mindmap** (hub + four coloured branches + curved edges) and a real **process flow**
(nodes / edges / arrows) instead of a text stand-in, plus a source-grounded figure chip
that **fails closed**. The device walk used the real Bài 17 fixture with template match
error 0.0. Lane E2 independently compiled Bài 17's `process` family through the shared
`OrderedStepsRenderer` — so Bài 17 is now the lesson that proves a *general* renderer
rather than the lesson that has a bespoke one. Its trust status is unchanged: still
`WITHHELD`-heavy, still 0 trusted.

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

**10 · Trẻ nhìn thấy sản phẩm tốt hơn ở đâu?**
In three concrete places, all verified on a real Nokia 6.1 across 36 frames:
**Trực quan finally reached the board** (70–80 % → **85–90 %**) — a lesson's structure
renders as an actual mindmap and process flow rather than as text pretending to be a
diagram; **the workspace stops repeating itself** — first content moves from 820 px to
712 px (peek) or 634 px (collapsed), and six labels for three views become four; and
**five defects only the device could find** were fixed, including a pinned card that was
covering the very hub of the mindmap it was recommending.

**But the boundary must be stated exactly:** this is better *presentation of the same
data*. **No APK built on this Mac carries any of this round's accuracy corrections** —
the main checkout's packs are still the old ones, and nothing merges. Every accuracy
result in this report is about the pipeline and the corpus, not about what a child sees
today.

---

## 11.2 Semantic Graph → Visual Grammar (P0) — what the escalation actually produced

Lane E2, **PR #86**, CI pass on `bcaf373`, `flutter analyze` clean, **973 Dart tests
pass / 42 skipped**.

### §19 is proven — one renderer, three subjects, two independent semantic paths

| lesson | family | path into the renderer |
|---|---|---|
| KHTN 6 Bài 17 · tách chất | `process` | typed semantic layer (`tsl-enumerated-steps-v1`) |
| KHTN 7 p20 · nguyên tố hoá học | `sequence` | document structure |
| **Ngữ văn 9 p82 · nói và nghe** | `sequence` | document structure |
| **Vật lí 10 p88 · thực hành tổng hợp lực** | `sequence` | document structure |

A grade-6 chemistry procedure and a grade-9 literature speaking task share no
vocabulary, no layout and no pedagogy — only a **shape**, which is all the renderer
can see. That is the Founder's «một ngôn ngữ để 3.679 bài có thể được compile»,
demonstrated rather than asserted.

**The anti-pattern is now structurally blocked — but the first version of this claim
was false, and the correction is the more valuable result.** E2's original guards
checked that `VisualSpec` carries no `book` / `lessonNo` / `slotKey` field and that
`VisualRenderContext` carries no `LessonDocument`. **Both guards were green while every
element a renderer holds carried lesson identity inside a *value*.** Lane E1 found it
while adopting the same constraint: **a field-name guard does not catch identity inside
a value.**

Audited across all 5 built specs, every string, by JSON path: ids were clean
(`process-1`, `step-1`, `event-0`, `cell-0-0`, `derivationRule`, `family`, `kind`), but
**`ProvenanceRef.blockIds` leaked in every position** — nodes, edges, groups and
`titleProvenance` — carrying values like `06-sgk-khoa-hoc-tu-nhien-6:p062:synthetic:015`.
`if (n.provenance.primaryBlockId.startsWith('06-sgk-khoa-hoc-tu-nhien-6'))` was **one
line away.** The guarantee had been nominal.

**The fix is structural rather than another naming rule.** At the render boundary
`VisualRenderContext` replaces each `blockIds` value with an opaque handle (`h0`, `h1`,
…) and keeps the handle→ref map itself; `pageOf` / `openSource` resolve handles, so the
provenance chain is unchanged and **the artefact on disk keeps the real block ids** —
that chain must stay auditable. Only the renderer's view is redacted. A renderer no
longer *should not* read identity; **it has nothing left to read.** Verified by
mutation: disabling the redaction fails 2 of the 6 new tests, and the suite also pins
that the leak still exists *in the artefact*, so the guard cannot go vacuous.

A second latent channel was closed at the same time: `VisualSection.id` was copied
verbatim from `SemanticData.id` — today `process-1`, but an upstream
`khtn6-bai17-process` would have flowed straight through. Compiler-minted ids are now
constrained by **shape**.

**One channel stays open by necessity and is recorded rather than hidden:**
`title` / `label` / `detail` / `badge` carry the book's own words, which may say «Bài
22». That is content the child reads, not an identifier — redacting it would delete the
lesson from the screen.

E2 corrected the over-strong «untypable» wording in `VISUAL-SPEC-v1.md` in place rather
than leaving it standing. Measured on `tool/corpus/tc_gold/` — 54 human-annotated pages
across 10 subjects, **committed**, so a clean clone reproduces it.

### The counterweight, and it is the more important half

**A grammar validated on one lesson does not generalise — two lanes found this
independently, from opposite ends, in the same round.**

- **E2:** the sequence rule fires on **6 of 54** gold pages, **3 of them teacher
  books** (one a competency list whose order means nothing). Learner-facing precision
  **0.500**, gated on `docType` with the unfiltered count still printed. **Toán, Tiếng
  Việt and Tin học produce nothing at all** — no upstream structure exists, and
  inventing a rule there would be the visual layer deciding meaning.
- **Lane C:** LS&ĐL 5 prints **112 date mentions in eight forms**;
  `prose-dated-events-v1` accepts **one** form and extracts **3 events across 28
  lessons**. **A Bài-8 shape, not a History rule.**

Both were found only by counting real forms across many lessons. This is the direct
argument for the Founder's execution order §32 — the **P0.3 census must precede
broadening the grammar**, because a rule that looks universal on its origin lesson
reliably is not, and no test on that lesson can reveal it.

### Two provenance holes found by tests that existed to look for them

1. **A sentence that was true in type and false in content.** «vì sao SAM chọn sơ đồ
   này» was keyed on the **Dart type**, so every `ProcessSemantic` was told the book
   used «·» bullets — Bài 17's own rule asserted as universal. **No test caught it:
   the type is right, the widget renders, the sentence is false.** Fixed by keying
   explanations on the **rule id**. This is the exact failure mode the Founder named
   as `TRACE ≠ EVIDENCE`, appearing in the explanation surface.
2. **Evidence strengthened itself through a file write.** The §8 fix
   (`ComparisonValue{text, sourceBlockId, grounding}`) brought a regression test that
   caught a **save/load round trip upgrading a grounding from `inheritedFromEntity` to
   `cellStated`.** Serialisation is a provenance-laundering channel. Recommended as a
   general rule: every provenance-bearing type needs a round-trip test asserting
   grounding **never strengthens**.

Also found: the LS&ĐL fixture carries `charSpan` / `yearStart` that the model drops,
after which the app **re-parses the year from a string at render time**.

### Discipline that held

**0 runtime model calls**, enforced by an import-set test. 5 specs / 6 sections /
19,289 bytes precomputed; two builds byte-identical. Correction edits the claim, the
graph or the spec — **never pixels** — and a node cannot be added without a
`sourceRef`.

### One divergence raised, not resolved

E1's spec carries **lesson identity**, which would make `if (lessonId == BAI17)`
typable again and dissolve E2's structural guarantee. Filed in
`VISUAL-SPEC-E1-E2-RECONCILIATION.md` with three others, routed to E1, **not decided
by either lane.** E1's census makes **HIERARCHY** and **LABELED_FIGURE** the justified
next renderers.

**Device: not walked** — Lane B owns that loop; `VisualSpecView` is handed over as a
six-line mount, and the §27 checkpoint is substituted by a machine-generated
transcript of the real widget across three subjects.

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

---

## 11.4 Semantic foundation + K-12 census (P0.1 / P0.3) — Lane E1

**PR #85**, CI green, 285 tool tests OK. **Recommendation: GO WITH ARCHITECTURE
CHANGE** — explicitly *not* GO (holdout precision and inter-annotator agreement are
unmeasured, and `e1-definition-v1` over-fires: «68.8 % of lessons have a definition» is
not credible), and explicitly *not* MORE EVIDENCE (the load-bearing claims were checked
deterministically on real corpus data).

### How few primitives suffice — the answer to «one language, 3,679 lessons»

**6 primitives · 6 relations carried everything built across 224 lessons**, and 10
visual families are projections of them. `isA` may collapse into `hasPart`, so possibly
**5**. `Method`, `SkillCase`, `CurriculumEdge` and `ConceptMap` are **absent from the
core** — nothing needed them to represent what a lesson *contains*.

Verified rather than asserted: six compilers, and `compiler_audit()` records **at
runtime** that every one read only `nodes` / `relations` / `claims`. PROCESS and
TIMELINE compiled **from the same graph object across two subjects**.

### Domain extensions — 3 of 7 proven, 3 refuted

| Extension | Share of lessons | Verdict |
|---|---|---|
| **MATH_AST** | 66.3 % | necessary |
| **LIT_TEXT** | 14.9 % | necessary |
| **CHEM_REACTION** | 7.8 % | necessary |
| History · Geography · Science | — | **refuted — needed none.** `Event` + `atTime` already carried LS&ĐL at **7/7** |

**So `ToánGraph` / `HistoryGraph` / `ScienceGraph` are unnecessary.** What is genuinely
per-domain is **notation and literary form, not subject** — a distinction that removes
three planned subsystems.

### The census — denominators kept separate throughout

| Denominator | Count |
|---|---|
| canonical rows | **3,679** |
| **distinct lesson keys** | **3,240** |
| units-backed | 1,784 |
| TSL-backed | 224 |

Tiers: A 222 · B 368 · **C 1,384** · D 1,266.
REPRESENTABLE **1,654 / 1,784** · EXTRACTABLE **220 / 224** (191 multi-family) ·
VALIDATABLE **3 lessons / 1 family** · **LEARNER_READY 0**.

COMPARISON, CONCEPT_MAP, QUANTITY and SPATIAL show **0 because no extractor exists** —
emitted under `familiesWithNoExtractor` so the zero cannot be misread as «the corpus
has none».

### ⚠️ A challenge to the canonical denominator — Founder gate, not resolved

`all-lessons.csv` has **3,679 rows but 3,240 distinct lesson keys**: **154 keys are
duplicated across 439 rows.** The Founder's standing rule (2026-09-05) is that 3,679
canonical and 3,381 ranged are never collapsed. This finding does not collapse them —
it questions whether **3,679 is a lesson count or a row count.** Reported, **not
fixed**, and flagged here because every «/ 3,679» figure in every round depends on the
answer.

### Exception clusters — one pipeline problem, one grammar problem, a long tail

- **NO_SOURCE_AT_ALL — 1,384 lessons (42.7 %). No grammar change moves this.** It is a
  source-pipeline problem wearing a semantics costume.
- **NEEDS_MATH_AST — 1,096 (33.8 %).** One extension worth **9×** everything else, and
  blocked on two verified bridge defects.
- Ranks 3–7 together: 235.

### Source-structure gaps — what the corpus does not currently carry

**1,642 questions and 4 option blocks.** **20 table blocks and 0 with cells.** **0
blocks retaining fraction or exponent shape.** 3,864 figures, 33.6 % with a caption,
465 orphan «Hình N.M» labels. And **Ngữ văn / Tiếng Việt — the subjects where verse
matters — have no TSL at all, so they have never been measured.**

### Four findings worth the Founder's time

1. **The surface grammar decides generalisation, not rule quality.** Enumeration is a
   nearly closed form — **7 of 10 forms, coverage 0.992** — which is why PROCESS reaches
   **104 / 224** lessons. Date is wide open — **3 of 12 forms, 0.140**; LS&ĐL uses all
   twelve at 0.131, Địa lí 0.003 — which is **exactly** why TIMELINE reaches **3 / 224**.
   This generalises Lane C's «Bài-8 shape, not a History rule» **at 47× scale**, and
   E2's 6/54 sequence result sits on the same curve. `forms.py` runs in seconds.
   **Standing rule from here: count the real forms before writing a rule.**
2. **A pipeline rebuild can delete a visual family with no rule at fault.** 4 of 28
   LS&ĐL lessons **lost** a family and **none gained** — while `tc2-r5` had *more*
   trusted blocks. Accuracy work can silently destroy semantic yield. **Round 5 needs a
   semantic-yield gate**, and nothing currently has one.
3. **One tone slip deletes a family.** «Tiền hành» for «Tiến hành» → **0 Steps instead
   of 5.** The distance between a working visual lesson and none is one diacritic.
4. The duplicate-key finding above.

### Cross-lane: a leak that two independent guards both missed

E1 **adopted E2's identity constraint in full** — lesson identity left the
renderer-facing spec. Writing the guard test then found something neither lane had
seen: **element ids embedded the book and lesson number**, so a renderer could have
branched on lesson identity by *parsing a string* while every field-name guard stayed
green. **A field-name guard does not catch identity inside a value.** Routed back to
E2 to run the same check.

Also adopted and credited: **A2's no-`from_<presentation>` rule**, and **E2's
serialisation-laundering finding** — grounding strength is now ordered on four axes and
`from_json` is deliberately non-lenient, so a round trip cannot strengthen evidence.
Grounding integrity **0.952 → 1.000** across **4,681 spans**, with **226 real failures**
found and fixed — including «hình 1a» matching only «hình 1» at scale.

Five near-verbatim SGK test fixtures were replaced with invented text (D4). **No LLM
was called anywhere in this lane.**

### What E1 says must change, all of it outside the ontology

claim-bearing `SemanticData` (today the base carries **no `Provenance`**, so
`citableAsTextbookFact` is undecidable for everything on Trực quan) · a bridge carrier
for validated structured nodes **plus a per-block failure mode** · the four subtypes
move to the visual side · a **semantic-yield gate** · and `khtn6_bai17.dart`'s 122
hardcoded `const` lines become versioned data + compiled artefacts + a ~10-row rule
registry + a small curated overlay.

---

## 11.5 Multi-signal verification (Lane A4) — which signal earned its place

**PR #88**, CI PASS, Python **321 passed / 8 skipped**. Touches only
`tool/corpus/verify/**` plus tests and two docs — no `lib/**`, no `repair/**`, no
`mathfix/**`, no `legacy/**`.

### The signal × case matrix (detect / propose-right / verify)

| | A `3×10⁸` | B `Lý Thái Tổ` | C `bản sắc` | D `Cộng hoà` | E `cây ổi` | F `II` + watermark |
|---|---|---|---|---|---|---|
| deterministic `A.enumerator` | – | – | – | – | – | **Y / Y / Y** |
| specialised parser (A2) | Y / – / – | – | – | – | – | Y / – / – |
| Vietnamese lexical (A1) | – | – | – | – | – | – |
| page furniture | – | – | – | – | – | **Y / Y / Y** |
| **cross-corpus** | – | **Y / Y** / – | **Y / Y** / – | **abstains (correct)** | **Y / Y** / – | – |
| **LLM semantic** | **Y / Y** / – | – | **Y / Y** / – | – | – | – |
| external | appropriate | appropriate | not appropriate | appropriate | appropriate | not appropriate |

**Case F is the only one where a signal both proposes a repair and independently
verifies it — and no model is involved.** F is the `II` → `I1` + watermark row that
Lane D's blind judgement scored 0/1; the deterministic enumerator and page-furniture
signals close it end to end.

### Measured, with false correction as P0

| Signal | Detection recall | Correction precision | **False correction rate** | Proposals per 1,000 clean tokens |
|---|---|---|---|---|
| **Cross-corpus (strict)** | 0.500 | 0.938 | **0.063** | **0.92** |
| Cross-corpus (recall policy) | 0.644 | — | 0.092 | 2.90 |
| **LLM semantic** | **0.717** — best in lane | — | **1.000** | 13 proposals on 60 already-correct rows, **all wrong**; 26.7 % of rows flagged |

Proper-noun false correction is **0.000** at all three cross-corpus policies. Router
human-review rate **0.0900** over 1,200 real SDM blocks (LLM alone 0.416, cross-corpus
alone 0.993, external **0.000**).

**The LLM row is the strongest empirical statement of `LLM OUTPUT != TRUTH` this
project has produced.** It has the best detection recall in the lane and a
false-correction rate of 1.000 — it finds real trouble and is wrong about the fix every
single time. Verdict: **detector only, never a proposer.**

### The edge hypothesis — confirmed, and its refinement falsified

The bbox-edge pattern from the 0/1 restore was tested at scale: **line-end tokens carry
3–4× the interior unattested rate (n = 486,000)** — confirmed. The follow-on «runs into
the right margin» refinement is **falsified at 0.5×**. Both reported.

### «Cộng hoà» → «Cộng hoa» — the corpus writes the error 358× across ≥5 books

Every signal abstains, correctly, and this is now asserted as a test. It corroborates
Lane A1's independent finding from the other side (268 vs 303 pages). The doctrine it
establishes: **frequency is evidence about the corpus, not about the truth.** A
majority vote over a corpus that consistently mis-sets a diacritic will confidently
propose the error.

### The end-to-end result is a NEGATIVE, reported as one

Running Lane A1's engine with Lane A4's signals: **0 repairs, 0 false corrections** —
the independent-support rule held and nothing was rewritten. But **4 blocks moved
TRUSTED → SUSPECT, 1 rightly and 3 wrongly: demotion precision 0.250.**

**This produced the round's most useful methodological rule, and it is adopted here as
standing:**

> **`false_correction_rate` is the correct P0 for a *repairer* and is blind to a
> *detector*.** A lane that raises detection recall must report **false demotion rate**
> beside it — otherwise it scores perfectly by never repairing anything, while
> withdrawing correct content from children.

### Which signal earned a place

- **Earned it unreservedly:** `A.enumerator` + `D.section_sequence` — the only
  propose-and-verify pair; `B.page_furniture` (deletion-only); **edge position**.
- **Earned it conditionally:** `D.cross_corpus` — **on the holdout, but not on History
  prose.**
- **Detector only:** `G.llm_semantic`.
- **Did not earn a pipeline place:** `H.external` — consult rate **0.000**. The
  question a Trusted Corpus asks is **source-bound**: «what does *this page* say», which
  no external authority can answer.
- **Not re-opened:** `F.third_stack`.

**A measured negative kept with its evidence:** learning page furniture from repetition
**fails** — the fuzzy cluster containing `C SỐNG` also contained «đời sống.». The form
that works is a 3-string publisher registry plus a stray-single-letter guard.

### Denominators — A4 took R13 seriously

A4 measures over **OCR lines and SDM blocks, never the TSL**, so its router set still
contains the **77 `role=empty` blocks (6.4 %)** that vanish downstream. Index excludes
the 13 evaluated books.

### The correction workflow (schema and triage only, no UI)

`CorrectionRecord{record_id, source_block_id, original, proposed, reason, reporter_type,
source_evidence, evidence[], corpus_version, reported_at, status, validation, reviewer,
reviewed_at, resulting_corpus_version, prior_record_id}` →
`REPORTED → VALIDATING | NEEDS_SOURCE | ACCEPTED | REJECTED`. **A report without a page
reading is a detection, not a correction**, and users never overwrite canonical truth.

---

## 11.3 Does the round compose? — verified, with nothing merged

Because merging is a Founder gate, composition was verified in a **throw-away worktree**
built from `integration/round5-2026-09-06` with all nine lane branches merged into it.
No PR was touched, no branch pushed, and the worktree is disposable. Gitignored assets
(321 pack files, 24 fixtures) were synced from the main checkout first, so a
missing-asset failure could not be mistaken for a defect.

**Final result — the round composes:**

| Check | Result |
|---|---|
| Git merge, 9 lane branches | **0 conflicts** |
| `flutter analyze` | **No issues found** |
| Python suite | **623 tests OK** (19 skipped) |
| Dart suite | **1061 tests, All tests passed** (3 skipped) |

Heads verified: A3 `569dad6` · C `d241fdc` · A1 `6652d58` · A2 `465d235` · D `0113019`
· A4 `1733ff7` · E1 `ea6b0f8` · E2 `538715f` · B `6e5f6e7`.

### Three integration defects that no lane's CI could see

Getting there took three fixes, and the pattern across them is the finding.

**1 · Lane B × Lane E2 — a compatibility claim true for readers, false for
constructors.** E2's §8 provenance fix made `cells` required and kept `values` as a
**getter**. That covers every site that *reads* `values[i]` — genuinely true, and what
E2 checked — but a getter is not a constructor parameter. Lane B's new round-5 test held
the repo's only such constructors, and they did not exist when E2 measured. Fixed by
building those sites through **`SemanticData.fromJson`**, so the test now exercises the
same parser the real fixtures use and every cell inherits a checkable
`ValueGrounding.inheritedFromEntity` — deliberately **not** by adding a `fromStrings`
convenience to `lib/core`, which would have made an unsourced cell constructible again.

**2 · Lane A4 × Lane A2 — a loader that silently returned less than it was asked for.**
`verify.load_plugins()` registered by **module-import side effect**. Once A2's test
legitimately called `registry.reset()`, the modules were already in `sys.modules`, so
re-importing was a no-op and registration was never replayed. Minimal reproduction:
`test_verify_signals` alone → 42 OK; `test_mathfix_plugin test_verify_signals` → FAILED.
A4 then proved the old path directly rather than inferring it: **the old loader would
have returned `signals = []`** — worse than the diagnosis. The lone `G.llm_semantic`
survivor was the tell, being the one module first imported *inside* a test method.
Fixed with an explicit idempotent `register()` per module and a `load_plugins` that
**verifies its manifest against the registry afterwards and raises
`RegistrationIncomplete`**, refusing a module that has no `register()`. A4 also widened
the default to all five plugin modules, since the router names paths for `A.enumerator`
and `B.page_furniture` that are worthless if those signals are silently absent.

**3 · Lane E2 × Lane E1 — a guarantee that was nominal.** Covered in §11.2: two green
field-name guards while every element carried lesson identity inside a *value*.

**The pattern, and the recommendation.** None of the three was visible to the lane that
owned it. Each was found either by composing the round or by a second lane adopting the
same rule. Two of the three — the silent registry and the identity leak — are the same
species as this round's headline data findings (**R13**'s disappearance with no reason
code, and grounding **strengthening itself** through a file write): *a component quietly
delivering something other than what it promised, with nothing checking.*

**Recommendation: make the composition check standing procedure at the end of every
round.** Nine green CI badges did not mean the round worked; running them together is
what found out. It costs one throw-away worktree and roughly ten minutes.

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
| #85 | `e1/round5-semantic-foundation` | E1 semantic foundation + K-12 census | PASS |
| #86 | `e2/round5-visualspec-renderer` | E2 VisualSpec + cross-subject renderer | PASS |
| #87 | `lane-b/round5-experience` | B experience + workspace UX + Visual | PASS |
| #88 | `a4/round5-multi-signal-verification` | A4 multi-signal verification + router | PASS |

All nine are CI-green, and the nine composed together are green (§11.3).

**No standing merge authority. READY FOR FOUNDER REVIEW.**
