# STEM expression accuracy — POC results · Lane A2 · 2026-09-06

**READY FOR FOUNDER REVIEW — nothing merged.** Branch `a2/round5-math-formula-accuracy`, base
`integration/round5-2026-09-06`. Companion documents: `MATH-ACCURACY-AUDIT-2026-09-06.md` (where
each defect is born, stage by stage) and `MATH-ACCURACY-STRUCTURED-CONTRACT.md` (the schema, and the
two requests to Lane A1 and Lane B).

Founder's chain: `SOURCE REGION → preserve geometry → expression detection → specialised recognition
candidate → canonical structured representation → deterministic validation → source cross-check →
VALIDATED / WITHHELD → mobile rendering`. Everything up to and including **VALIDATED / WITHHELD** is
built and measured below. **Specialised recognition and the renderer are not built** — §6 says
exactly why, and what each would buy.

---

## 1 · The headline

| | |
|---|---|
| **Restored expressions** | **10** — every one hand-verified against the printed page |
| **Restore precision** | **10 / 10 = 1.000** [Wilson 95 %: 0.722 – 1.000] |
| **Restore precision on the HOLDOUT** | **8 / 8 = 1.000** — 8 of the 10 are on pages never opened while the rules were written |
| **False corrections produced** | **2** — both found by hand-check, both now refused (§4) |
| **False corrections surviving** | **0** |
| **Toán coverage** | 0.1686 → **0.1705** (+5 blocks eligible today; 4 more validate but are held by a reason this lane does not cover) |
| **Physics false trust** | **−3 blocks**, at **0** over-withhold cost, measured across 36 029 blocks |

Denominators, stated per the D5 rule and never summed: **97** Toán pages that have both an SDM and a
PDF (2 692 blocks, 993 learning, 454 TRUSTED, 2 238 WITHHELD) · **346** of those blocks contain at
least one printed fraction region · **36 029** blocks on **1 410** pages for the physics scan ·
**89** printed fractions hand-counted for detection recall.

---

## 2 · Detection — the region comes from the page, not from the text

A horizontal ink run is a vinculum only when the page shows *detached* ink above and below it inside
its own x-extent. That one geometric fact separates a fraction bar from a «+» (attached stroke), a
lone «−» (nothing either side), an underline (nothing below) and an «=» (its neighbour is another
bar). OCR tokens are consulted afterwards, only to name the halves, and only when exactly one bare
digit run sits on each side.

**Hand-checked against contact sheets of every detected region, tile by tile:**

| page | printed stacked fractions | detected | true positives | precision | recall |
|---|---|---|---|---|---|
| Toán 4 tập hai p83 | 43 | 40 | 40 | 1.000 | 0.930 |
| Toán 5 tập một p22 | 41 | 40 | 40 | 1.000 | 0.976 |
| Toán 5 tập một p23 | 5 | 5 | 5 | 1.000 | 1.000 |
| **pooled** | **89** | **85** | **85** | **1.000** [0.957–1.000] | **0.955** [0.890–0.982] |

**And the number that must be reported beside it.** On an *unbiased* 12-page random sample of
ordinary Toán pages (seed 20260906), 7 regions were detected and **4 were parts of illustrations** —
a grass band, a speech-bubble tail, the brim of a hat. Reading bars off a **neutral-ink layer** (a
press prints a rule in ink; illustrations are coloured) removed two at no cost to the 85 true
fractions; two remain, both black line art. So:

* **region precision ≈ 1.00 on fraction-dense pages, ≈ 0.6 on ordinary ones**;
* **extraction precision 14/14** on the values actually produced on those pages — because every
  illustration false positive was `extractable=False` and therefore proposed nothing.

The distinction matters: a false region costs nothing but a name; a false *value* is a wrong answer
served to a child.

**The recall that is not a failure.** Four printed fractions in 89 were missed. But the important
recall property is the opposite one: a region whose digits the OCR destroyed is still **found**. On
Toán 5 tập một p22 the printed `b) 3/10 + 5/21` — the round-4 defect — yields **two detected
regions**, both refused (`numerator_token_missing`), because the numerator `3` is not in the OCR
output at all. Today that page serves the fragment beside them, `b) 10 +`. A found-and-refused
region can be withheld *with its crop*; a region nobody detected cannot.

---

## 3 · The canonical object — structure survives the chain

`ADD(FRACTION(3,10), FRACTION(5,21))` — the AST is canonical; `latex` and `text` are computed
properties with no setter. `from_json` exists and **`from_latex` does not**: a rendering string
cannot become structure, so a model-generated or hand-edited LaTeX cannot launder itself into truth.
Schema and node kinds: `MATH-ACCURACY-STRUCTURED-CONTRACT.md` §2.

The grammar gives two refusals **no regex can express**, and both are named round-4 defects:

| printed | OCR gives | refused by | why the regex could not |
|---|---|---|---|
| `b) 3/10 + 5/21` | `b) 10 +` | *the expression ends on an operator* | the shipped `MATH` pattern requires a digit **after** the operator — precisely what is missing |
| `d) 20/18 − 2/5` | `20/18`, `2/5`, no operator token | *two operands with no operator between them* | there is no mark to match |

This is R2 requests (a) and (b) — `PIPELINE-REQUESTS-FROM-LEGACY.md:71-77`, OPEN·P0 since round 4 —
met structurally. An unknown mark aborts the whole block rather than being skipped, so prose cannot
leak into an expression and an unfamiliar glyph cannot be silently dropped from arithmetic.

Physics nodes are the same tree: `Unit('m', den=Unit('s'))` and `Unit('m', den=Unit('s', exp=2))`
are different **objects**, so `m/s` and `m/s²` are not two strings that differ by a character. And
`3×10° m/s` has **no representation at all** — there is no degree node — which is §6's «structurally
impossible transformation», made impossible rather than merely flagged.

---

## 4 · False correction — measured, and what it cost to find

The lane produced **two** wrong repairs. Neither was found by a metric; both were found by looking
at the printed page.

**① `d) 20/18 − 2/5` → `d) 20/18 2/5`.** The printed «−» was dropped. By area that sign is **3.75 %**
of the block's glyph ink — under any ceiling one would dare set. It is caught by *shape*: the widest
**unbroken** run of ink that no OCR token accounts for, 45 % of a bar length. Area says «rounding
error»; shape says «a printed mark nobody read».

**② `c) 16/21 × 3/5` → `16/21 - 3/5`.** Apple Vision returned a token whose text is `'-'` for the
printed `×`. Every check passed — the ink was accounted for (the token's box covers the ×), nothing
was invented (the «-» came from a real observation), the grammar parsed, both vinculums were real.
**Multiplication served as subtraction, with a clean audit trail.**

② is the more important finding, because it names a gap the whole design had:

> Ink-accounting proves **completeness** («nothing printed was dropped»). Provenance proves
> **honesty** («nothing was invented»). Neither proves **identity** — that the glyph on the page is
> the glyph the recogniser named. The same gap produces `3×10⁸ → 3×10°`.

`operator-raster-v1` closes it for operators by reading their own pixels and classifying the shape
(one bar / crossed bar / two bars / no bar) against the operator claimed. The printed `×` is refused;
the correct `b) 8/11 − 19/33` **on the same printed row** still restores — a guard that refused every
operator would be safe and useless. An unjudgeable glyph abstains, and abstention is never a pass.

The six checks, each an independent signal that did not produce the candidate it judges:

| validator | what it proves | layer |
|---|---|---|
| `vinculum-raster-v1` | the bar is one run and is drawn **longer** than the wider half — the typographic fact that makes a fraction a fraction | B |
| `ink-accounted-v1` | of the printed **glyph** ink in the region (the bar excluded from both sides of the ratio), how much did no OCR token read — by area **and** by widest unbroken run | B |
| `operator-raster-v1` | the printed operator is the operator the OCR named | B |
| `structure-grammar-v1` | the atoms form a whole printed expression | C |
| `digit-provenance-v1` | no character was invented (a multiset, so a value that reordered or duplicated printed digits fails) | C |
| `arith-selfcheck-v1` | where the book states both sides, the arithmetic is true. `NOT_APPLICABLE` is reported and never counts as a pass | C |

RESTORE requires ≥1 PASS and **no** FAIL. A candidate whose every validator abstained is withheld:
«nothing contradicted it» is not evidence.

---

## 5 · The five directions, before → after

Measured on the **97 Toán pages that have an SDM and a PDF** (2 692 blocks). Nothing was reprocessed
and no guard was loosened; this is a projection of what the repairer would do, block by block, with
the full ledger written to `poc-out/round5/mathfix/`.

| direction | before | after | note |
|---|---|---|---|
| **FALSE TRUST ↓** | — | **−3 physics blocks** | §7: three TRUSTED blocks carrying a destroyed exponent, including the speed of light twice |
| **TEACHING-CRITICAL ↓** | 2 fabricated expressions were produced | **0** | both refused by the shape and identity checks (§4) |
| **CORRECT SERVED ↑** | 454 trusted blocks | **459** | +5 eligible restores, all verified correct |
| **OVER-WITHHOLD ↓** | 346 fraction-bearing blocks withheld | **341** | and 4 more are validated but blocked by `empty_block` (§7 ②) |
| **RESTORE PRECISION ↑** | n/a (nothing was restored) | **10/10 = 1.000** | 8/8 on the holdout |

**Toán coverage: 0.1686 → 0.1705.** Small, and honestly so. The ceiling is not the validators —
only **1 restore in 10 was refused by a validator**; the other 336 fraction-bearing blocks never
reached one:

| why no candidate was proposed | blocks |
|---|---|
| a fraction region the OCR could not read (`numerator_token_missing` and kin) | **274** |
| every token in the block was consumed by the fractions, none left | 24 |
| the block mixes prose with the arithmetic | 23 |
| the block's tokens sit on more than one baseline | 4 |
| **refused by a validator after a candidate was built** | **9** |

**274 of 336 — 82 % — is one problem: the OCR did not read the digit.** That is the number that
decides what to build next, and it is why §6 recommends a recogniser rather than more rules.

---

## 6 · Specialised recognition — why it is not built, and what it would buy

The order's chain has a step this POC does not implement. That is deliberate and the evidence
points at it:

* the ceiling is **274 unreadable regions**, not validator strictness;
* on `b) 3/10 + 5/21` the numerator `3` is **absent from the OCR output entirely** — no text rule,
  no second stack and no lexicon can reach it;
* the gap is small and well-shaped: an isolated 1–3 digit glyph, in a known box, at 300 dpi, in one
  typeface family per book.

**Candidates, with cost / benefit / licence — measured on this corpus, not from benchmark claims:**

| candidate | evidence | verdict |
|---|---|---|
| **an in-corpus template recogniser** | the corpus supplies its own labels: every fraction where the OCR *did* read both halves is a labelled glyph in the same book, same typeface, same dpi. **85 hand-verified fractions already exist** as a test set. No new dependency. | **recommended first step** |
| **Docling formula enrichment** (`do_formula_enrichment`, `CodeFormulaV2`) | the option exists in the installed Docling 2.126 and is **never set** (`tool/corpus/tc_bakeoff_run.py:94-101`); Docling is already a dependency, so this is a model download, not a library. Older `ds4sd/CodeFormula` is **MIT**. | fallback only — and its output is a **VLM candidate**, never source truth: it may produce a `RepairCandidate` and must pass §4's checks |
| **Marker / Surya 2** | the only stack that scored formula **1.00** (`05-PARSER-BAKEOFF.md:32,46`); **129 s/page here ≈ 94 days** for the corpus (`16-COST-PERFORMANCE.md:24`); **GPL-3**; already rejected as a dependency (`19-RECOMMENDATIONS.md:20`) | not on this Mac; the licence is a Founder question |
| **local VLM (Qwen2.5-VL-3B)** | already installed; `18-PRODUCT-FEASIBILITY-VERDICT.md:15` — *«**not** for math (flattened the same way)»* | measured and rejected |
| **MinerU** | `16-COST-PERFORMANCE.md:10` — *«Vietnamese OCR unusable»* | rejected |
| **pix2tex / texify / nougat / mathpix / im2markup / unimernet** | **zero occurrences repo-wide** — never tried | untried, and all heavier than the problem |

**Performance of what is built:** 0.25–0.8 s per page end to end at 300 dpi (page raster 0.23 s,
bar detection 0.10 s, the rest under 0.1 s), pure Python plus PyMuPDF and numpy, both already
present. The library itself imports neither — the CI runner has no numpy and no PyMuPDF, and all
131 tests run there on ASCII rasters. **No dependency was added.**

---

## 7 · Physics — a false trust that is served today

**Stage: recognition.** Apple Vision reads the printed superscript `⁸` as a degree sign. No later
stage rewrites it, so there is nothing to normalise; and no guard covers scientific notation —
`MATH` needs a digit after an operator, `UNIT_EXP` covers only `m|cm|dm|km|mm` with exponent 2 or 3,
`CHEM` does not match, and `agree_numbers` cannot fire because **both stacks read the same «°»**.

Scanned **36 029 blocks on 1 410 SDM pages** (every SDM this machine holds):

| | |
|---|---|
| blocks carrying a destroyed power-of-ten exponent | **8** |
| of which **TRUSTED — served today** | **3** |
| already withheld (detecting them costs no coverage) | 5 |
| **false positives** | **0** |

The three served, verified against the printed page:

```
09-sgk-khoa-hoc-tu-nhien-9 p29 body     «c là tốc độ ánh sáng trong chân không (c = 3.10° m/s)»
09-sgk-khoa-hoc-tu-nhien-9 p30 sidebar  the same sentence
08-sgk-khoa-hoc-tu-nhien-8 p66 body     «- Bar: 1 Bar = 10° Pa.»   ← the page prints 1 Bar = 10⁵ Pa
```

`destroyed-exponent-v1` detects all 8 and **repairs none**, because the exponent's value is not in
the text — recovering it needs the recogniser of §6. The rule is pinned by regression tests against
both the defect strings and the readings it must never touch: `°C`, `°F`, `góc 30°`, `cồn 90°`,
`vĩ độ 21°`, `1 360 m2`.

`si_expected_exponent` is written as a **validator, never a generator**: where the page prints
`1 kJ = 10ⁿ J` or `1 MW = 10ⁿ W`, SI fixes n exactly (3, 6, 9), and that will check a recogniser's
reading rather than substitute for one. A value that came from a table rather than from an
observation is a guess with a nice pedigree.

---

## 8 · Two things the numbers do not show, and one that must not be lost

**① The exemption is safe by accident.** `tc2_sdm.py:290-291` gives a Docling-labelled FORMULA block
**confidence 0.95 on a label alone**, and `:674,676,678` exempt `formula`/`table` roles from all
three math guards. On the 38 gold pages Docling scored formula-role **0**, so the branch is dead —
but on the legacy batch-1 Toán pages Docling emitted **15** formula labels, and **14** were saved
only by the `empty` test firing first at `:276`. Enabling formula enrichment would silently mint
trusted formulas. → `formula_structured` (contract §1b): the exemption must be earned by a
validated structure.

**② «Empty — no letters» is where formulas go to die, and it is now measurable.** Of the 10
validated restores, **4 sit on blocks whose only withhold reason is `empty_block`** — regions
Docling correctly identified as formulas, whose OCR text was empty or pure arithmetic, filed as
role `empty` with the evidence string *«no letters»*. `c) 22/15 − 8/15`, `3/11 + 7/12`,
`b) 3 + 5/8` and `16/9 : 4` are all validated, all correct, and all held out by a reason that
misdescribes them. A fifth is held by `figure_text`. **Half of this lane's correct output is blocked
by a role decision, not by a math decision** — which is Lane A3's «FORMULA recall 0.000» seen from
the other end.

**③ The lane's floor must not fall.** A refused region still produces a `MathExpression` — named,
boxed, crop-bearing — and the app already renders that crop to the child
(`withheld_card.dart:182-201`). The printed formula survives as an image whether or not any of this
is adopted. That is the floor, and nothing here lowers it.

---

## 9 · What remains withheld, and why

| class | blocks | can it be reached? |
|---|---|---|
| a fraction whose digits the OCR never read | 274 | **only by specialised recognition** (§6) |
| block mixes prose with arithmetic | 23 | yes, with a sub-block split — not attempted; the risk is prose leaking into an expression |
| all tokens consumed, nothing left | 24 | probably a detection artefact on figure-heavy pages; unexamined |
| two baselines in one block | 4 | yes, by treating each baseline as a row — small, deferred |
| refused by a validator | 9 | **correctly** — 2 of them were real false corrections |
| validated but held by `empty_block` / `figure_text` | 5 | **yes, by a role decision** (§8 ②) |

## 10 · Requests

1. **`formula_structured`** — Lane A1, `tc2_sdm.py`: the guard exemption keys on a validated
   structure rather than a role name (contract §1b).
2. **Per-line geometry on the SDM block** — Lane A1, one additive `lines` field (contract §1); A2
   already reads it when present.
3. **`empty_block` on a formula-labelled region** is a different disposition from `empty_block` on
   a blank one. Four correct expressions are blocked by the conflation (§8 ②).
4. **The renderer** — Lane B, option A (image fallback only, zero app work, available today) or
   option B (a `FormulaBlock` drawn from the AST with Flutter primitives, no LaTeX engine, no new
   dependency). Contract §3.
5. **The recogniser** — approve the in-corpus template recogniser first (§6), with CodeFormulaV2 as
   a fallback, and confirm that a VLM's output stays a `RepairCandidate` behind the §4 checks.
6. **The pack path** — `rebuild_fractions.py` → `build_lesson_index.py` still ships geometrically
   reconstructed expressions with `status: INFERRED` stripped (audit §0 ①). Lane D is fixing it;
   noted here because it is the same failure family and a different code path.

**NO MERGE.**
