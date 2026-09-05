# STEM EXPRESSION ACCURACY — code audit before building · Lane A2 · 2026-09-06

**READY FOR FOUNDER REVIEW — nothing merged.** Branch `a2/round5-math-formula-accuracy`, base
`integration/round5-2026-09-06`. Founder order: *«Audit code trước để xác định `OCR → normalization
→ structured model → serialization → renderer` — lỗi phát sinh ở stage nào. Không mặc định cần kiến
trúc mới.»* This document answers that first. The POC proposal is §7 and nothing in it is built yet.

Classifications: **EXISTS AND USED · EXISTS BUT NOT WIRED · PARTIAL · RESEARCH ONLY · MISSING**.

---

## 0. The three findings that change what to do

**① A second system already exists, and it is the one that ships.** The Founder's order forbids
reconstructing expressions speculatively from geometry. `tool/extract/rebuild_fractions.py:31-127`
does exactly that — it pairs vertically stacked digit tokens, joins two of them across an operator,
and writes `expr: "a/b op c/d"` with `method: 'geometric-fraction-rebuild-v1'` and
`status: 'INFERRED'` (`:119-124`). The round-4 fix that «all 16 geometry-rebuilt Toán expressions
are now withheld» applies to the **tc2/TSL path**. The **pack** does not use that path:
`tool/ui/build_lesson_index.py:53-62` reads `exercise-case-map.json` and copies forward `expr`,
`skillCaseId`, `page`, `book` — **dropping `status: 'INFERRED'` and `method`**. So the shipped
`toanExercises` payload carries geometrically fabricated arithmetic with no marker that it was
inferred, and `rebuild_fractions.py:57-59` documents the failure mode in its own comment: two
adjacent exercises glued into one phantom expression («10/15 + 11/8»).
→ **The first action in this lane is not to build. It is to stop that, or to carry the flag.**
`tool/ui/build_lesson_index.py` is Lane D's file under the round-5 plan; this is reported, not
touched.

**② There is no structured STEM representation at any stage — pipeline, bridge, app or pack.**
Not «partial», not «unwired». MISSING everywhere (§1). So the answer to *«không mặc định cần kiến
trúc mới»* is: an architecture change **is** required, but it is not a new one. There is exactly one
line of prior design — `docs/research/trusted-corpus/11-STRUCTURED-DOCUMENT-MODEL.md:19`, *«text
NFC; for FORMULA/TABLE also a structured payload (**latex** / cells)»*. The `cells` half was built
(`tool/corpus/tc2_sdm.py:131,1141`); the `latex` half never was. **The POC finishes that line rather
than opening a second design.**

**③ The two named defects are born at two different stages, and only one of them is a model
problem.** `3×10⁸ → 3×10°` is born in **recognition** — Apple Vision reads the superscript as a
degree sign, and the pipeline never touches it again. `b) 3/10 + 5/21 → b) 10 +` is born in
**layout/serialisation** — the numerator `3` is never read at all, and the 2-D geometry that would
prove something is missing is discarded one function before the guards run. Different stages,
different fixes (§4, §5).

---

## 1. A · Is there a structured expression model? — **MISSING at every stage**

| Layer | Evidence | Class |
|---|---|---|
| SDM block | `tool/corpus/tc2_sdm.py:1136-1141` — a block carries `text`, `text_docling`, `bbox`, `cells`. No `latex`, no AST, no line array. | MISSING |
| TSL | `tool/corpus/tc2_tsl.py:78-82` — `text` + `bbox` + provenance. | MISSING |
| Bridge | `tool/corpus/tsl_to_lesson_document.py:70-81` — `ROLE_MAP` has no `formula` key; `:211` turns an unmapped role into a `WithheldBlock` with reason `unknown_role:<role>`. **A TSL formula role becomes a withheld region by design.** | EXISTS AND USED (as withholding) |
| App model | `lib/core/lesson_model/lesson_document.dart:154` — `sealed class LessonBlock` with nine subclasses; `:210-345` `fromJson` accepts `heading｜paragraph｜image｜caption｜table｜question｜activity｜withheld｜sourceRef` and `default: return null` (`:343`). A block of `"type": "formula"` is **rejected, taking the whole document with it**. | MISSING |
| App expression type | `lib/core/curriculum/canonical_problem.dart:110` — `final String expression;` An opaque string. | PARTIAL |
| App fraction type | `lib/core/curriculum/fraction_problem.dart:11-13` — `FractionProblem(a, b, op, c, d)`, `int a,b,c,d`, `op ∈ {+,−}`. One hard-coded shape; no nesting, no precedence, no other operators, no decimals, no variables. Sole implementation of `SolvableProblem`. | PARTIAL |
| Pack | `tool/ui/build_lesson_index.py:58-60` — `expr` (a string), `skillCaseId`, printed page, book. **No bbox, no crop, no pdf page, no status, no method.** | MISSING |

Grep over `lib/**` for `MathBlock｜FormulaBlock｜MathExpression｜Ast｜LaTeX｜MathML｜TeX｜Numerator｜
Denominator｜superscript｜subscript｜Equation｜ChemicalFormula｜Reaction`: **zero class or field hits.**
The single occurrence of the token `formula` in the whole app is a substring match on a machine
reason code at `lib/features/lesson_workspace/widgets/withheld_card.dart:23,31` — it selects a
Vietnamese sentence to show the child and carries no content.

---

## 2. B · How does the app render a formula? — **plain `Text`. No math renderer, no rich text.**

- `pubspec.yaml:35-42` declares `flutter`, `cupertino_icons`, `sqlite3`, `sqlite3_flutter_libs`,
  `path_provider`, `camera`, `google_mlkit_text_recognition`. **No** `flutter_math_fork`, `catex`,
  `flutter_markdown`, `flutter_html`, `flutter_svg`, `webview_flutter`. **MISSING.**
- `grep -rn 'RichText\|TextSpan\|WidgetSpan\|Text.rich' lib/` → **zero matches across 147 files.**
  There is no inline-span machinery to hang a fraction, a superscript or a subscript on. **MISSING.**
- The block dispatch is a `switch` producing bare `Text`:
  `lib/features/lesson_workspace/smart_book_view.dart:430-493`; a paragraph containing arithmetic is
  `Text(text, style: _bodyStyle())` at `:440`. **EXISTS AND USED.**
- The tutor draws the expression string at display size:
  `lib/features/tutor/tutor_screen.dart:141` — `3/4 + 2/5` is rendered literally, with a slash. There
  is no vinculum. Same at `lib/features/learning_session/slice_flow.dart:184`.
- **Which widget renders a `formula`-role block? None exists.** Such a block never reaches the
  switch: the bridge already converted it to a `WithheldBlock`, which renders as `WithheldCard`.

**The one thing that does work end to end is the image fallback.** `WithheldBlock` has `crop`
(`lib/core/lesson_model/lesson_document.dart:532`) and deliberately **no text field** — `fromJson`
refuses to read `text` even when present (`:328-338`), and `textOf` returns `null` for it (`:927`).
`withheld_card.dart:144` gates a button on `b.crop != null` and `:182-201` renders
`Image.asset('${doc.assetBase}${b.crop}')` under the caption «Ảnh chụp trang sách — chỉ để con đối
chiếu, không phát hành.» So **a withheld formula already survives to the child as a page image, one
tap away.** That is the Founder's fallback, already implemented. **EXISTS AND USED.**

---

## 3. C · Where is a formula flattened? — three places, and one of them is irrecoverable

**C1 · Docling (the served text).** `tool/corpus/tc2_sdm.py:116-118` takes the item's text verbatim;
the flattening happened inside Docling and no line array survives in the raw JSON. Unrecoverable
from this repo. `docs/research/trusted-corpus/05-PARSER-BAKEOFF.md:45` records the cost: *«formulas
flattened (31 corrupted-data events, mostly Toán/Vật lí)»*.

**C2 · XY-cut.** `tool/corpus/layout_extract.py:302,307` — `text = ' '.join(b['texts'])`, emitted
with a **union bbox only**. A three-line stacked fraction becomes prose; only the line *count*
survives.

**C3 · The irrecoverable point, and the one that matters.** `tool/corpus/tc2_sdm.py:1060` computes
`under` — the OCR lines whose centre falls inside the block bbox — passes it to `verse_layout` at
`:1110` **for a single boolean**, and then discards it. The emitted block (`:1136-1141`) has no
`lines` field. **The 2-D geometry that proves a fraction is a fraction is read, used to decide
whether a poem is a poem, and thrown away one step before the guards run.** Everything downstream —
`tc2_tsl.py:78`, `tsl_to_lesson_document.py:167,201`, the app — sees one flat string.
This is why R2's request (c) (*«fewer numeric tokens than the stacked-fraction regions its bbox
overlaps»*, `docs/research/legacy-reprocess/PIPELINE-REQUESTS-FROM-LEGACY.md:71-77`) cannot be
implemented where the guards live. **MISSING — and it is a structural gap, not a regex gap.**

### C4 · What actually happens to a Docling `formula` region — measured, not assumed

`tool/corpus/tc2_sdm.py:262-291`, `assign_role`, in order:

```
:274   if b['role'] == 'FIGURE':            → figure
:276   if not t or not LETTERS.search(t) and not DIGITS.match(t):
:277       return 'empty', 'native', 1.0, ['no letters']      ← a formula dies HERE
...
:290   if b['role'] == 'FORMULA':           → formula          ← never reached
```

`DIGITS` is `^\d{1,3}$`. So a formula region whose OCR text is empty **or is pure arithmetic with no
letters** is classified `empty`, evidence `['no letters']`, guard `empty_block`, `WITHHELD`.

Measured on the 16 legacy batch-1 Toán pages (`poc-out/round4/legacy/batch-1-rerun-tc2-p2`):

| Docling `native_label == 'formula'` blocks | 15 |
|---|---|
| became role `empty`, reason `empty_block` | **14** |
| reached role `formula` | 1 (withheld, `agree_text`) |

One of the 14 was not even textless — `'7 8 2 8 7 - 2 8 5 8'` (the printed `7/8 − 2/8 = 5/8`) was
filed as **«empty — no letters»**. This corroborates Lane A3's independent measurement (FORMULA
recall 0.000; 8 of 19 gold formulas withheld as empty blocks) and sharpens it: **the reason code
misstates what was lost.** The pipeline does not withhold a formula *as a formula*; it records that
there was nothing there. Nothing downstream can know a formula was refused.

### C5 · The exemption is keyed on a role name, and its safety is accidental

`tool/corpus/tc2_sdm.py:674,676,678` — all three guards read
`if role not in ('formula', 'table', 'figure', 'empty')`. A block that reaches role `formula` gets
confidence 0.95 with method `native` and **no verification of any kind** (`:290-291`), is a
`LEARNING_ROLE` (`tc_sdm.py:39`), is not `FURNITURE` (`tc2_tsl.py:43,72`) — and is **exempt from
`math_guard`, `unit_guard` and `chem_guard` while carrying a flat OCR string.**

That is the most dangerous branch in the file. It is currently dead only because Docling scored
formula-role **0** on the 38 gold pages (`05-PARSER-BAKEOFF.md:32`) — but it is *not* dead on the
Toán pages, where Docling emitted 15 formula labels; they were saved by the `empty` test firing
first, at `:276`. **The exemption is safe by accident.** → this is exactly Lane A3's
`formula_structured` request, and §7.4 answers it.

---

## 4. Defect ① `3×10⁸ m/s` → `3×10° m/s` — born in **RECOGNITION**, served as TRUSTED

**Stage: OCR.** Apple Vision reads the printed superscript `⁸` as a degree sign. Raw evidence,
`poc-out/graph/ocr-body/09-sgk-khoa-hoc-tu-nhien-9/p029.json`:

```
'Trong đó, c là tốc độ ánh sáng trong chân không (c = 3.10° m/s);'
```

Not a normalisation bug: no step in the pipeline rewrites it. Not a model bug either, in the sense
that there is no model that could have carried it — but the digits `3` and `10` survive, so this is
**not** the «flattened to text» story. The mantissa lives; the exponent's *value* dies at
recognition.

**Then nothing stops it.**
`MATH` (`tool/corpus/tc_cascade.py:113`) does not match — there is no `digit operator digit`.
`UNIT_EXP` (`tc2_sdm.py:245`) covers only `m|cm|dm|km|mm` + `2|3`, not `m/s`, not a power of ten.
`CHEM` does not match. `agree_numbers` cannot fire: **both stacks read the same `°`** — round 4's
falsified assumption, live. So `role_guards` returns `[]` and `trust_status` returns **TRUSTED**.

**Measured prevalence** (`10` glued to `°`/`′` and followed by a unit or digit — scientific
notation, excluding `°C`/`°F` and genuine angles):

| | |
|---|---|
| OCR lines across the KHTN / Vật lí / Khoa học books | **79** |
| blocks in the round-4 tc2-p2 review SDM set carrying one | 7 |
| of which **TRUSTED — served today** | **3** |

The three served: the speed of light on two pages
(`09-sgk-khoa-hoc-tu-nhien-9` p29 `body`, p30 `sidebar`) and `1 Bar = 10° Pa`
(`08-sgk-khoa-hoc-tu-nhien-8` p66 `body`). **A physical constant is being served as nonsense with no
guard between it and a child.** This is false trust, not over-withholding — the opposite direction
from the Toán failure, in the same lane.

**And it is deterministically decidable in a large share of cases.** The same scan shows the shape
of the corpus: `1 kJ = 10°J`, `1 MJ = 10°J`, `1 MW = 10° W`, `1 GW = 10° W`, `1 Bar = 10° Pa`. The
**SI prefix on the left fixes the exponent on the right** — k⇒3, M⇒6, G⇒9. That is an independent
deterministic validator that does not exist anywhere in the repo today (§7.3).

---

## 5. Defect ② `b) 3/10 + 5/21` → `b) 10 +` — born in **RECOGNITION + SERIALISATION**, unrepairable from text

The OCR lines of `05-sgk-toan-5-tap-mot` p22 in that row, verbatim:

```
 x       y       w       h   text
0.3469  0.7645  0.0878  0.0363  'b) 10 +.'      ← enumerator + DENOMINATOR + operator, one token
0.4388  0.7631  0.0224  0.0218  '5'
0.4306  0.7820  0.0347  0.0203  '21'
0.1796  0.7805  0.0245  0.0203  '11'
0.2082  0.7762  0.0204  0.0116  '+'
```

**The numerator `3` of `3/10` does not exist in the OCR output at all**, and the denominator `10`
was glued into the enumerator token. So:

- **no text-level rule can repair this.** Not a better regex, not a second stack, not a lexicon.
  The digit was never read. Only recognition on the printed region can recover it.
- **no text-level rule can even detect it** — `MATH.search('b) 10 +')` is `False` (the pattern needs
  a digit *after* the operator, and its operator class omits ASCII `-`). The block is `TRUSTED`,
  role `body`, and both blind annotators marked it false trust
  (`docs/research/legacy-reprocess/ROUND4-BATCH-1-REPORT.md:258-260`).
- the detection *is* possible from the page: my detector finds both printed fraction regions here
  (§6) and refuses both, `numerator_token_missing`. But the geometry that makes that possible was
  discarded at `tc2_sdm.py:1060` before the guards run (§3 C3), which is why R2 is still OPEN · P0.

**This is the case that decides the POC.** It is not a validation problem and not a normalisation
problem: `3/10` requires **specialised recognition on the source region**, then validation. Nothing
else reaches it.

---

## 6. What Lane A2 has already measured (before the audit order)

Built and pinned by 69 tests on `tool/corpus/mathfix/**` — a **detector**, not a reconstructor: a
horizontal ink run is a vinculum only when the page shows *detached* ink above and below it inside
its own x-extent, and the OCR tokens are consulted afterwards, only to name the halves.

**Detection, hand-checked against the printed page from contact sheets of every detected region:**

| page | printed stacked fractions | detected | true positives | precision | recall |
|---|---|---|---|---|---|
| Toán 4 tập hai p83 | 43 | 40 | 40 | 1.000 | 0.930 |
| Toán 5 tập một p22 | 41 | 40 | 40 | 1.000 | 0.976 |
| Toán 5 tập một p23 | 5 | 5 | 5 | 1.000 | 1.000 |
| **pooled (fraction-dense)** | **89** | **85** | **85** | **1.000** [Wilson 0.957–1.000] | **0.955** [0.890–0.982] |

On an **unbiased 12-page random sample** of ordinary Toán pages (seed 20260906) precision is very
different and must be reported as such: 7 regions, of which **4 were parts of illustrations** — a
grass band, a speech-bubble tail, the brim of a hat. Reading bars off a **neutral-ink layer** (a
press prints a rule in ink; illustrations are coloured) removed two of the four at no cost to the 85
true fractions. The remaining two are black line art. **All false positives were `extractable=False`
and therefore proposed no repair** — the honest split is *region precision* ≈ 0.6 on ordinary pages
versus *extraction precision* 14/14 on the values actually produced.

**The one restore this lane produced, and then refused.** On p22 the block `d) 20/18 − 2/5` passed
every check and was restored as `d) 20/18 2/5` — **the printed «−» was dropped.** By area the sign is
3.75 % of the block's glyph ink, under any ceiling one would dare set. It was caught by measuring
the *shape* instead: the widest **unbroken** run of ink that no OCR token accounts for, 45 % of a bar
length. With that rule the restore count on those five pages is **0** and restore precision is
undefined rather than 0/1. Reported as it happened, because it is the exact failure the Founder
named: *«a wrong restored formula is worse than a withheld one»*, and it took a second, shape-based
validator to see it.

**Extraction candidates evaluated so far** (cost / benefit / licence in §7.5).

---

## 7. Proposal — the smallest bounded POC

### 7.1 What must NOT be built
A second reconstruction system. One exists (`rebuild_fractions.py`) and ships. A second
architecture is not the problem; **an unvalidated one is.**

### 7.2 The canonical object — finishing `11-STRUCTURED-DOCUMENT-MODEL.md:19`

`MathExpression`, produced only by `tool/corpus/mathfix/`, carried as the SDM/TSL structured payload
the spec already reserved:

```
MathExpression {
  sourceBlockId, book, page_pdf, page_printed, bbox, crop        # provenance & fallback
  observations[]        # every OCR line / raster bar that contributed — never overwritten
  ast                   # ADD(FRACTION(3,10), FRACTION(5,21)) — the machine/pedagogy form
  latex                 # rendering form, DERIVED from the ast, never parsed back into it
  recognition[]         # each candidate + which recogniser produced it (all untrusted)
  validations[]         # ValidationResult per deterministic check
  disposition           # REPAIRED_CANDIDATE | VALIDATED_REPAIR | WITHHELD  (Lane A1's vocabulary)
}
```
The AST is primary and LaTeX is derived, so a rendering choice can never become the truth. Markdown
and plain text are not representations of it.

### 7.3 Two failure classes, two recognisers, two independent validators

| | Toán · `formula_flattened` | Physics · `destroyed_exponent` |
|---|---|---|
| canonical case | `b) 3/10 + 5/21` → `b) 10 +` | `3×10⁸ m/s` → `3×10° m/s` |
| today | withheld with crop (tc2 path) / **fabricated (pack path)** | **TRUSTED and served** |
| detect | raster vinculum + detached ink (built, precision 1.000 on dense pages) | `10` glued to `°`/`′` before a unit — a shape rule, no world knowledge |
| recognise | **the gap**: a bounded digit recogniser on the numerator/denominator crop, for the digits OCR never read | the same recogniser on the superscript crop |
| validate ① | `ink-accounted` + `vinculum-raster` + `digit-provenance` (built) | **SI-prefix consistency**: `1 kJ = 10ⁿ J` ⇒ n=3; `MW/W` ⇒ 6; `GW/W` ⇒ 9. Independent of the recogniser. |
| validate ② | `arith-selfcheck` where the book states both sides (built) | raster superscript geometry: the glyph sits above the baseline ⇒ it is an exponent, not a degree |
| fallback | withhold + keep crop (already reaches the child, §2) | same |

Step one for Physics costs nothing and moves false trust immediately: **detect and withhold** the 3
served blocks. Restoration follows only where a validator confirms the exponent.

### 7.4 `formula_structured` — Lane A3's request, answered

The guards' exemption at `tc2_sdm.py:674,676,678` must stop keying on the role *name*. Proposal: the
exemption is earned by a `MathExpression` whose disposition is `VALIDATED_REPAIR` — a **structure**,
not a label. Until then a `formula`-role block is guarded like any other, which closes the latent
hole in §3 C5 and makes A3's «FORMULA recall 0.000» safe to fix without opening a trust door.
`tc2_sdm.py` is Lane A1's file: this is a request, not a change.

### 7.5 Recognisers — cost / benefit / licence, and what is already known

| candidate | evidence | verdict |
|---|---|---|
| **Marker / Surya 2** | the only stack that scored formula **1.00** (`05-PARSER-BAKEOFF.md:32,46`); **129 s/page on this Mac ≈ 94 days for the corpus** (`16-COST-PERFORMANCE.md:24`); **GPL-3**; already rejected as a dependency (`19-RECOMMENDATIONS.md:20`) with an open «get a GPU box» recommendation (`:10`) | not on this Mac, and the licence question is the Founder's, not mine |
| **Docling formula enrichment** (`do_formula_enrichment` + `CodeFormulaV2`) | never enabled: `tool/corpus/tc_bakeoff_run.py:94-101` sets only OCR/table options. The option **does** exist in the installed Docling 2.126, and the model repo is `docling-project/CodeFormulaV2`; the older `ds4sd/CodeFormula` is **MIT**. Docling is already a dependency, so this adds a model download, not a library | the cheapest *new* candidate — but it is a VLM, so its output is an **LLM candidate**, never source truth, and may only ever produce a `RepairCandidate` validated by §7.3's deterministic checks |
| **local VLM (Qwen2.5-VL-3B)** | already on this machine; `18-PRODUCT-FEASIBILITY-VERDICT.md:15` — *«**not** for math (flattened the same way)»* | measured and rejected for math |
| **MinerU** | `16-COST-PERFORMANCE.md:10` — *«Vietnamese OCR unusable»* | rejected |
| **pix2tex / texify / nougat / mathpix / im2markup / unimernet** | **zero occurrences repo-wide** — never tried | untried; all are heavy, and none is needed for the *digit* problem |
| **a bounded digit recogniser on the crop** | the actual gap is small: an isolated 1–3 digit glyph in a known box, at 300 dpi, in one typeface family | **the recommended POC** — smallest thing that reaches `3/10`, no new library if template matching on the page's own confidently-read digits suffices; measurable against the 85 hand-checked fractions |

The last row is the proposal: **do not add a heavy dependency to read a digit.** The corpus supplies
its own training data — every fraction where the OCR *did* read both halves is a labelled glyph in
the same book, same typeface, same dpi. Measure a template/nearest-neighbour recogniser against
those first, and only if it fails go to CodeFormulaV2 with the deterministic validators in front of
it. Either way the recogniser is a candidate producer, never a source of truth.

### 7.6 Renderer
`MathExpression.latex` needs a renderer the app does not have (§2: no rich text at all). Two
options, in order of cost: **(a)** keep the image fallback that already works and add the AST only
for machine use — zero renderer work, no new dependency; **(b)** a `FormulaBlock` rendered from the
AST with Flutter primitives (a `Column` of numerator / rule / denominator is enough for K-9
arithmetic) — no LaTeX engine, no `flutter_math_fork`. `lib/features/**` is Lane B's; nothing here
is written without them.

### 7.7 Metrics the POC reports — all five directions, plus a holdout
`FALSE TRUST ↓ · TEACHING-CRITICAL ↓ · CORRECT SERVED ↑ · OVER-WITHHOLD ↓ · RESTORE PRECISION ↑`,
each **before → after**, plus expression exact-match, structural accuracy, number/operator accuracy
and **false repair rate**. The 97 audit rows are the evaluation set; every named defect becomes a
regression test, and every number is reported twice — on those rows and on an **independent holdout
this lane has not looked at** (candidate: the Toán 4 tập hai batch-1 pages and a fresh seeded sample
of KHTN/Vật lí pages, drawn after the rules are frozen).

---

## 8. Remaining answers, compactly

**D · specialised math OCR/parser: MISSING (never tried), RESEARCH ONLY (evaluated and rejected).**
See §7.5. Zero repo occurrences of pix2tex, texify, nougat, mathpix, im2markup, unimernet,
`do_formula_enrichment`, CodeFormula.

**E · bbox / crop / provenance end-to-end: EXISTS AND USED on the tc2 path, MISSING on the pack path.**
`tc2_sdm.py:1137` → `tc2_tsl.py:78-82` → `tsl_to_lesson_document.py:236,246-247`; crops rendered at
`:756-770,788-800` with withheld regions **first** (`:797`), padding clamped so a crop *«can lose
padding, never gain foreign content»* (`:721-753`). App side: `SourceRef` carries
book/pagePdf/pagePrinted/bbox/blockId/extraction/ocrConf/pipeline
(`lib/core/lesson_model/lesson_document.dart:18-46`) and is **required** (`:199-201`). Two caveats:
`bbox` is never used geometrically — its only read site in the app is a debug string
(`lib/features/lesson_workspace/widgets/source_sheet.dart:64`) — and every crop is
`licence = 'internalResearchOnly'` (`tsl_to_lesson_document.py:37,790`), gated on OQ8/D4. The pack
carries none of it (§1).

**F · structural validation: MISSING.** Every guard is a regex that **withholds** —
`tc2_sdm.py:667`, verbatim: *«Deterministic; withholds only, never repairs.»* No arithmetic is ever
evaluated: zero hits for `Fraction(`, `sympy`, `eval(`, `numexpr` in `tool/**`. Two structural gaps
worth naming: `tc_cascade.math_guard()` (the *function*) is **EXISTS BUT NOT WIRED** — production
imports only the regex (`tc2_sdm.py:237`); and the page-level `formula` census feature is computed
(`tc_layout_census.py:197`) and stored (`tc2_sdm.py:1171`) but **never read by any guard**, although
`09-CRITICAL-TEACHING-ERRORS.md:41` prescribes exactly that.

**G · Physics Quantity/Unit semantics: MISSING.** No unit table, no dimensions, no SI registry, no
conversion, in `tool/**` or `lib/**`. The entire surface is `UNIT_EXP` (`tc2_sdm.py:245`): five
length units × exponent 2 or 3, withhold-only. It does not cover `s²`, `kg`, `N`, `J`, `°C`, `m/s`,
`A`, `V`, `W`, `mol`, `Pa`. On the app side `unit_guard` has no handler and falls through to the
generic child message (`withheld_card.dart:19-26`).

**H · Chemistry: PARTIAL detection, MISSING structure — and the detector is a shape rule that
misfires badly.** `CHEM` (`tc2_sdm.py:246`) matches any capital-letter run glued to a digit; it
never checks that the letters name an element. Measured on the round-4 review + gold SDM sets:
**173 blocks carry `chem_guard`**, and the matched token is plainly not chemistry in a large share —
`VD2`/`VDI` (a teacher's-book «Vận dụng» cross-reference, 9), `S2` (the ohm sign **Ω** mis-read, 12,
all physics), `I1` (Roman **II** mis-read, 4), `A3`/`A1`/`A0` (paper sizes and labels, 5), `E5`
(«xăng E5», 3), `R2`/`V1`/`U2`/`I,R` (physics symbols, 7). **≥40 of 173 ≈ 23 % are non-chemical.**
The Founder's named defect is in there verbatim:

```
09-sgk-khoa-hoc-tu-nhien-9 p27  heading  WITHHELD  match='I1'
   'I1 - Định luật khúc xạ ánh sáng'          ← printed «II», a Physics section heading
08-sgk-khoa-hoc-tu-nhien-8 p107 heading  WITHHELD  match='I1'
   'I1 - Khái niệm năng lượng nhiệt'
09-sgk-khoa-hoc-tu-nhien-9 p57  heading  WITHHELD  match='S2'
   '1 MS = 1 000 000 S2'                      ← printed «1 MΩ = 1 000 000 Ω»
```

Note what the third one shows: the *same* block is both a guard false positive **and** a destroyed
symbol (Ω → `S2`). The guard withholds it for the wrong reason and the right reason at once.
`CHEM` is Lane A1's; the fix that generalises is the same as §7.4 — key on structure, not on shape.

**I · accessibility / export: MISSING for formulas.** Two `Semantics(` widgets in the whole app, both
on chrome (`lesson_workspace_screen.dart:257`, `fixture_chip.dart:80`); zero `semanticsLabel`; the
withheld crop image at `withheld_card.dart:186` has no alt text. No TTS implementation — only a
policy entry `'tts': CapabilityDecision.ageGated`
(`lib/core/platform/education_safety_policy.dart:44`). Export is learner-event JSONL
(`lib/main.dart:352-360`), not content; no PDF/HTML/share path. **So there is no export or
accessibility surface that needs MathML today** — which is an argument for AST-primary + rendered
fallback, and against adopting MathML now.

**J · answered in §5.**

---

## 9. What I am asking the Founder to decide

1. **The pack path.** `rebuild_fractions.py` → `build_lesson_index.py` ships geometrically
   reconstructed arithmetic with the `INFERRED` flag stripped. Stop it, or carry the flag through
   and mark it in the UI? (Lane D's files; A2 reports only.)
2. **Physics `destroyed_exponent`: detect-and-withhold now?** 3 blocks in the review set are served
   TRUSTED today, including the speed of light. Withholding them is a pure false-trust reduction and
   costs 3 blocks of coverage.
3. **The recogniser.** Approve the bounded in-corpus digit recogniser first (§7.5 last row), with
   CodeFormulaV2 (MIT for the older `ds4sd/CodeFormula`) as the fallback only if it fails — and
   confirm that a VLM's output stays a `RepairCandidate` under the deterministic validators.
4. **The renderer.** §7.6 option (a) image-fallback-only, or (b) an AST-rendered `FormulaBlock`
   built with Lane B. (a) needs no app work at all.
5. **`formula_structured`** (§7.4) — the guard exemption keys on a validated structure rather than a
   role name. Needs Lane A1 to change `tc2_sdm.py`.

**NO MERGE. Nothing in §7 is built.**
