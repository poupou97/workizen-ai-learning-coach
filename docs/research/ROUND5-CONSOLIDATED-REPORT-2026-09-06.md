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
| A `FORMULA` role buys trust 0.95 and waives the math/unit/chem guards | `tool/corpus/tc2_sdm.py:290-291` | Latent: enabling Docling formula enrichment would silently mint trusted formulas. Regression tests ordered by Founder §4 **[PENDING — Lane A1/A3 confirmation]** |
| Bridge has no `formula` role | `tool/corpus/tsl_to_lesson_document.py:71-82` | A validated `MathExpression` cannot reach the app |
| Provenance dropped on the pack path | `tool/ui/build_lesson_index.py:53,58,366` | 41 geometrically-rebuilt expressions marked `status: INFERRED` / `method: geometric-fraction-rebuild-v1` ship to g4 and g5 carrying only `['book','expr','page','skillCaseId']` — the "not verbatim" warning is stripped. **[PENDING — Lane D fix]** |

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

**[PENDING — Lane D REPAIRED stage + Lane A4 router]**

## 9. Legacy Reprocess Scoreboard

**[PENDING — Lane D]**

## 10. The five product scores

**[PENDING — requires Lane B device evidence and Lane D packs]**

## 11. Answers to the Founder's ten questions

**[PENDING]**

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
