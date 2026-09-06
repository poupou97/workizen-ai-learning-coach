# RECOGNITION — targeted re-crop, measured · Workstream B · round 6 · 2026-09-06

**READY FOR FOUNDER REVIEW — nothing merged.** Branch `ws-b/round6-recognition`, base
`integration/round6-2026-09-06`. Companion: `RECOGNITION-FAILURE-CENSUS-2026-09-06.md` (the census
that decided what to build). Claim labels: **PROVEN · MEASURED · OBSERVED · INFERRED ·
HYPOTHESIS · UNKNOWN.**

**What is NOT claimed anywhere in this document.** No Math structure reaches a child. The bridge
still has no `formula` role, `LessonDocument` has no formula type, the app has no math renderer,
and a withheld page crop is **not** structured Math delivery. Everything below is measured **at
recognition level**, which is where the round asked for it.

---

## GATE B — met

> ≥1 previously unrecoverable OCR failure class materially improves **at recognition level**.

**PROVEN, on the class the Founder named and on the slice the Founder chose.**

`b) 3/10 + 5/21` on Toán 5 tập một p22 — the round-4/round-5 defect whose numerator `3` is
**absent from the whole-page OCR output entirely**, and which round 5 stated could be reached by
nothing but recognition on the printed region — is read correctly, both halves, by a targeted
re-crop: `3/10` and `5/21`, each confirmed at two independent scales and seen stacked in a third
observation.

**GOLDEN #2 · Toán 4 tập hai Bài 61 (p81–83):** 85 printed fraction regions, 47 of them
unreadable by the whole-page OCR. **17 recovered. 17 of 17 correct against the printed page**
(contact sheets `sheet-bai61-p081-082-recovered.png`, `sheet-bai61-p083-recovered.png`).
**0 disagreements on the 38 control regions.**

---

## 1. What was actually done, and what «high resolution» turned out to mean

`tool/ocr/ocr_pdf.swift` OCRs a whole page once, at scale 3, with Vietnamese language correction
**on**. That single observation is everything the corpus has. The round-6 lever was to ask Apple
Vision — the same engine, the one that also runs on iOS in the product — about **one printed
region at a time**.

**MEASURED, and it corrects the framing of the lever.** Every SGK page in this corpus is a
**100 ppi scan embedded in the PDF** (`05-sgk-toan-5-tap-mot` p22: one image, 1094 × 1536 px, on a
787.68 × 1105.92 pt page). Rendering a crop at scale 20 produces 830 × 1090 px from ~58 × 76
source pixels: **interpolation, not information.** `ocr_pdf.swift` says as much in its own comment
— *«Thử 6× cho kết quả Y HỆT»*.

So what a crop changes is not sharpness. It is:

* **context** — Vision no longer sees the prose around the expression, and language correction is
  switched off, so it stops resolving a digit into whatever fits the sentence;
* **the glyph-to-frame ratio** — the region fills the image instead of being 0.3 % of a page;
* **segmentation** — and this is the load-bearing one. The answer is **not monotonic in scale**.
  On the `3/10` region: scale 3 reads `-` and `10`; scale 6 reads `3`, `1`, `0`; scale 12 reads
  `10` alone; scale 20 reads `3` then `10`. Different scales land Vision's own line grouping in
  different places, which is exactly why several are asked and why **agreement between them is
  evidence rather than ceremony**.

Cost: **~0.46 s per region** for all twelve observations (three boxes × four scales), 18.4 s for a
40-region page. Pure Apple Vision plus PyMuPDF and numpy, all already present. **No dependency was
added.**

## 2. The rule that decides — fail-closed at every step

`tool/corpus/recognition/consensus.py`. A printed fraction is READ only when **all** of:

1. the **numerator box alone** returns exactly one bare digit run, the same one, at **≥2 distinct
   scales**, and **no scale returns a different one** (a conflict aborts);
2. the same for the **denominator box alone**;
3. the **whole-region crop** returns exactly those two digit runs, in that vertical order — an
   independent observation that they **stack**. Two boxes each holding a digit do not make a
   fraction; round 5's lesson is that completeness and honesty do not prove identity.

A scale that returns two digit runs in one half **abstains** rather than joining them: joining
fragments is reconstruction, and reconstruction from fragments is the round-3 failure this whole
lane exists to avoid. A refused reading never populates `value`; it goes to `candidate`.

## 3. The six metrics, reported separately and never combined

Five populations, never summed (the D5 denominator rule). **DEV** = round 5's own 16 tuned pages ·
**SDM** = all 113 Toán pages with both an SDM and a PDF, the population round 5's «274 of 336»
lives in · **HOLDOUT-1** = 24 Toán pages drawn at random across grades 2–12, seed 20260906 ·
**HOLDOUT-2** = 12 pages selected on **≥6 detected bar regions** in books never tuned on ·
**HOLDOUT-3** = 14 pages selected on **content** — the page's own text contains «phân số» — in
books never tuned on. All three holdout rules were fixed before the draw.

| | DEV | **SDM** | HOLDOUT-1 | HOLDOUT-2 | **HOLDOUT-3** | Bài 61 |
|---|---|---|---|---|---|---|
| pages | 16 | 113 | 24 | 12 | 14 | 3 |
| fraction regions | 204 | 784 | 68 | 127 | 212 | 85 |
| recovery population | 128 | 548 | 66 | 105 | 177 | 47 |
| **① DIGIT RECALL** (both halves read) | 0.500 | **0.403** | 0.061 | 0.038 | 0.181 | 0.532 |
| **③ STRUCTURAL EXACT MATCH** (halves read *and* seen stacked) | 0.344 | **0.259** | 0.000 | 0.010 | 0.130 | 0.362 |
| **⑥ RECOVERABLE FRACTION RATE** | 44/128 | **142/548** | 0/66 | 1/105 | **23/177** | **17/47** |
| control regions | 76 | 236 | 2 | 22 | 35 | 38 |
| control reproduced | 37 | 113 | 1 | 12 | 16 | 21 |
| control disagreements | 1 | 1 | 0 | 0 | 2 | 0 |

**② SYMBOL RECALL** — three classes, three very different answers (§5):

| class | population | read | correct | accepted after guards |
|---|---|---|---|---|
| destroyed exponent `10⁸ → 10°` | 171 | 21 | 17 | **16**, all correct |
| Roman section number `II → I1` | 106 | 8 | 7 | **3** with the sequence validator, all correct |
| ohm sign `Ω → S2` | 22 | **0** | — | **0 — the lever does not work here** |

**⑤ FALSE RECOGNITION RATE** — beside every recall figure, as the round requires:

| set | readings produced | wrong | rate | how established |
|---|---|---|---|---|
| DEV p22 + Bài 61 p81–83 | 28 recoveries | **0** | **0.000** | every tile read against the printed page |
| **HOLDOUT-3** | 41 (23 recovery + 18 control) | **2** | **0.049** | every recovery tile and both disagreements read |
| SDM control | 236 | 1 disagreement | 0.004 | hand-check: **the baseline is wrong, not the re-crop** |
| destroyed exponent, raw | 21 | 4 | 0.190 | contact sheet |
| destroyed exponent, guarded | 16 | **0** | **0.000** | contact sheet |
| Roman, ungated | 8 | 1 | 0.125 | contact sheet |

**④ EXPRESSION EXACT MATCH** — block level, on the 387 fraction-bearing SDM blocks:
**before 10 restored · after 10 restored · Δ = 0.** This is the round's honest negative and it has
its own section (§6).

### The two wrong readings on the holdout, named

* `06-sgk-toan-6-tap-hai` p17 — the page prints **7/9**, the whole-page OCR read `7/9`, the
  re-crop read **`7/6`** at two agreeing scales. A genuine digit misread that reproduced across
  scales. Nothing text-level can see it; **the control set is the only thing that caught it**, and
  that is what the control set is for.
* `08-sgk-toan-8-tap-hai` p22 — the page prints `3 / (x² − x)`. The denominator is **algebraic**,
  and the recogniser returned `3/1`. A denominator that is not a number should never have produced
  a digit run; the fix is a shape check on the denominator's ink width against its digit count,
  and it is **not built** (HYPOTHESIS).

---

## 4. The Founder's 274/336, before → after

Round 5: *«274 of 336 fraction-bearing blocks could not be repaired for one reason: the OCR never
read the digit.»*

**On the same kind of object.** On the 113-page SDM population there are **387** fraction-bearing
blocks, of which **281** carry `numerator_token_missing` or `denominator_token_missing` — round 5's
274, re-measured on this branch's larger page set.

| | before | after | Δ |
|---|---|---|---|
| blocks whose candidate is blocked by «the OCR did not read the digit» | **281** | **234** | **−47 (−16.7 %)** |
| blocks whose candidate reaches RESTORE | 10 | 10 | **0** |

**And the census says round 5's sentence was two sentences.** Of the 548 unreadable regions,
**312 (57 %) are DIGIT LOSS** — no OCR token of any kind over that half — and **196 (36 %) are
SEGMENTATION** — the ink *was* recognised and glued into another token, as in `b) 10 +.`. Both
respond to the re-crop, at different rates: DIGIT LOSS 76/312 = 0.244, SEGMENTATION 46/196 = 0.235,
FRACTION STRUCTURE 20/40 = 0.500.

---

## 5. The other two named defects — one recovered, one falsified

### 5.1 `3×10⁸ m/s → 3×10° m/s` — recovered on 16 of 171, including a block served TRUSTED today

**MEASURED.** Corpus-wide, 171 destroyed power-of-ten exponents. The crop recogniser reads 21;
the contact sheet says 17 are right and **4 are wrong**, so the raw false-recognition rate for this
class is **0.190** — an order of magnitude worse than the fraction class. The four are three forms:

* a match spanning **two lines** of the crop (`-35 -1` / `10` / `10` over two stacked fractions);
* `(2 + x)¹⁰⁰`, which is **not a power of ten at all**;
* `10⁻⁵` and `10⁻¹⁰` returned as `105` and `1010` — **the magnitude is right and the sign is gone.**
  Round 5's lesson with a different glyph, and no text-level check can see it.

Three guards were added, and the third is the interesting one. `superscript_sign` reads the pixels
**between the ten and the exponent** and refuses the reading when a detached horizontal bar sits
there. Two measurements about the guard itself, both worth keeping:

* its first version fired on **0 of 18** because `InkMask.row_runs` returns `(start, LENGTH)` and
  it was read as `(start, end)`;
* with the window over the whole match it fires on **9 of 18**, and what it finds is the printed
  **multiplication mark to the LEFT of the ten** (`152·10⁶ km`). A sign that changes an exponent is
  to its right, and the window now says so.

**Final: 16 recovered, 16 of 16 correct, false recognition 0.000**, at a cost of one correct
reading refused (`10²²`, whose digit base strokes read as a bar). **The guard is calibrated on
these same 18 rows and has no holdout — MEASURED on set, not PROVEN.**

Among the 16 is `08-sgk-khoa-hoc-tu-nhien-8` p66, `1 Bar = 10⁵ Pa` — **one of the three blocks
round 5 measured as TRUSTED and served today with a destroyed exponent.** The other two (the speed
of light, twice) are **STILL_BROKEN**: the crop returns `3.10°` at every scale.

`si_expected_exponent`, round 5's independent validator, **abstained on all 171** — the pages where
SI fixes the exponent (`1 MJ = 10ⁿ J`, `1 GW = 10ⁿ W`) are precisely the ones the recogniser could
not read. An independent validator that never fires is not yet an independent validator.

### 5.2 `II → I1` — recovered, and validated by the book's own sequence

**MEASURED.** 106 findings, 8 read, **7 correct**. The Founder's named line is among them:
`09-sgk-khoa-hoc-tu-nhien-9` p27 `I1 - Định luật khúc xạ ánh sáng` → **`II`**, at four scales out
of four, and the book's own section sequence **PASSES** it. So is p133, `Il - Glucose và
saccharose` → `II`. The one wrong reading is `10-sgv-toan-10` p94: the page prints **`Vì Â`** — the
Vietnamese word «because» — the census matched `V1`, the recogniser read `VI`, and **the sequence
validator refused it.**

`sequence_validator` is the signal round 5 named and nothing consulted: *«`I1` breaks a sequence
observable elsewhere in the same book. The corpus carries its own evidence and nothing consults
it.»* It is now consulted, and it works — with a **named false-alarm mode**: section numbering
restarts per lesson and the sequence is book-global, so it FAILs one correct `II`. Gated on PASS
it accepts 3 of 106 with 0 errors; ungated it accepts 8 with 1.

Note the cost: **`l` and `|` are mapped to `I`** (the same printed stroke, a case ambiguity of one
glyph) and **`1` is deliberately not mapped**, because that substitution is the confusion under
investigation and assuming it would make the recogniser conclude what it was asked to test.

### 5.3 `Ω → S2` — **FALSIFIED. The lever does not work for this class.**

**0 of 22.** At four scales, on every one of the 22 corrected findings, Apple Vision returns
`S2`, `22`, `U`, `Q`, `12`, `0` — never `Ω`. Including the Founder's line: `1 MS = 1 000 000 S2`
comes back as `U0`, `U0`, `0 0`, nothing.

This is the round's most useful generalisation, and it is a negative one:

> The targeted re-crop recovers a character the engine **could** read but did not isolate. It
> recovers nothing when the glyph is **not in the engine's repertoire** for this typeface at this
> resolution. Fractions and exponents are the first kind. Ω is the second, and no amount of scale,
> cropping or consensus reaches it.

The second kind needs a different instrument — Lane A2's **in-corpus template recogniser** is the
standing candidate, and Ω is a good first target for it because the corpus prints thousands of
correct Ω glyphs in the same books.

---

## 6. The honest negative: a recovered digit is not yet a repaired block

**MEASURED, and this is the result the Founder should read most carefully.**

The recovered digits were fed back through `mathfix`'s own extractor and validators — the same
projection round 5 ran, so the «before» numbers stay reproducible — as tokens carrying a new
`Token.engine = 'apple-vision-crop-v1'`, so a digit read from a crop can never present itself as a
whole-page OCR line.

**Block-level result: RESTORE 10 → 10. Nothing improved.** Five blocks gained a proposed value and
every one is malformed:

```
b) 10 +. 3/10          ← 05-sgk-toan-5-tap-mot p022
0) 1 3 8/14 2/7        ← 04-sgk-toan-4-tap-hai p083   (Bài 61)
```

The reason is precise and it is not a tuning problem. `math_line_candidate` assembles a line from
the tokens in x-order. The recovered `3/10` is **added**; the destroyed observation `b) 10 +.` —
which still contains the denominator glued to the item letter — is **still there**. Replacing a
source observation is not something a recogniser may do: it is a `RepairCandidate` crossing a
`Validator` into a `ValidatedRepair`, which is **Workstream C's contract**, and doing it inside
`mathfix` would have been a second provenance universe.

One measurement worth keeping from the attempt: with the crop box used as the recovered token's
box, `numerator_ambiguous` rose from **2 blocks to 27** and `prose_token_in_block` from 29 to 44 —
an over-wide token box reaches into the neighbouring fraction's strip and the detector correctly
refuses a strip holding two candidates. Shrinking the box to the recovered digit's own ink fixed
that (`study.tight_box`). **The geometry has to be honest before the reading is usable.**

**Request to Workstream C** — the shape, not the code: a recovered digit should arrive as a
`RepairCandidate` that **supersedes** the observation whose region it covers, carrying
`original_observation`, `engine`, `agreeing_scales` and the region-stacking evidence, so the
validator judges one expression rather than two overlapping ones.

---

## 7. Docling formula enrichment — run, measured, and not recommended

Round 5 recorded that `do_formula_enrichment` exists and is never set, and called it *«the cheapest
new candidate»*. It had never been run. It has now.

**Facts checked before running anything.** `PdfPipelineOptions.do_formula_enrichment` exists in the
installed Docling **2.126.0**, defaults `False`; `code_formula_options` points at
**`docling-project/CodeFormulaV2`**, **0.64 GB**, licence **CDLA-Permissive-2.0** — permissive, and
not the GPL-3 that disqualified Marker/Surya. Docling is already a dependency, so this is a model
download rather than a library. The latent trust hole round 5 warned about is **already closed** on
this base: `tc2_sdm.role_guards` emits `formula_unvalidated` for a `formula`-role block that does
not carry `formula_structured`, so enabling enrichment can no longer mint a trusted formula from a
label.

**MEASURED on the same crops, 15 regions of Bài 61 p83 before the run was stopped:**

| | CodeFormulaV2 | this lane's crop recogniser |
|---|---|---|
| seconds per region | **87.2** (min 69.3, max 117.3), MPS | **0.46** for twelve observations |
| correct on the 7 truth-labelled regions | **4 / 7 = 0.571** | 17 / 17 on the same page |
| failure mode | reads the digit **7** as `T`, `E`, `F` in this typeface | refuses (`UNREAD`, `CONFLICT`) |

**Verdict: NOT RECOMMENDED as the recogniser for this failure class.** 87 s/region is ~190× the
cost of the observation that already works and is in the same order as the Marker/Surya rejection
(129 s/page ≈ 94 days for the corpus). And it is a VLM: `LLM OUTPUT != TRUTH`, so even at zero cost
its output could only ever be a `RepairCandidate` behind the same deterministic checks. It stays a
**fallback for the class the crop lever cannot reach** (§5.3), where its cost would be paid on tens
of regions rather than thousands.

Marker/Surya (GPL-3, 129 s/page), local Qwen2.5-VL (measured and rejected for math in round 5) and
MinerU (Vietnamese OCR unusable) were **not re-run**; round 5's measurements stand.

---

## 8. Where the ceiling is now, and what would move it

Of the 548 unreadable regions on the SDM population, the re-crop reads 142 and refuses 406:

| refusal | regions | is it the right refusal? |
|---|---|---|
| `UNREAD` — nothing legible at any scale | 186 | mostly **yes**: a large share of these regions are not printed fractions at all (§9) |
| `INSUFFICIENT_AGREEMENT` — one scale read it, no second | 97 | **the largest addressable group.** More scales, or a second engine, would convert some of these; each conversion must be paid for in false-recognition rate |
| `REGION_UNCONFIRMED` — both halves read, never seen stacked | 79 | conservative by design; the check that catches the algebraic-denominator error |
| `CONFLICT` — two scales, two answers | 42 | **yes**, always |
| `AMBIGUOUS` — a half returned two digit runs | 2 | yes — joining them is reconstruction |

## 9. What the two failed holdouts actually measured — reported, not replaced

**HOLDOUT-1 (random, all grades): 0 of 66. HOLDOUT-2 (detector-dense, grades ≤6): 1 of 105.**
Both are reported as they came out. The contact sheets say the population was wrong, not the
recogniser:

* on a random Toán page across grades 2–12, an 18-tile sample contains ~7 **algebraic** fractions
  (`(3−2x)/(3+1/x)`, `n/360`), which this rule can never read — a half is named only by a **bare
  digit run**, by construction — and ~7 regions that are **not fractions at all**: a receipt's
  total rule, a column-addition rule, a speech-bubble tail, a photograph;
* HOLDOUT-2 selected on «≥6 detected bar regions» and therefore drew grades 1–3, whose dense bar
  regions are **column-arithmetic rules** — those books teach no fractions at all. **Selecting on
  the detector selected the detector's own errors.**

HOLDOUT-3 fixed the population with a content rule declared before the draw (the page's own text
contains «phân số»), and returns **0.130** with a hand-checked false-recognition rate of **0.049**.
All three numbers stand; none replaces another.

The honest reading of all three together: **the recogniser is scoped to numeric stacked fractions**,
its rate depends almost entirely on how many of the detected regions are that, and **its refusal
behaviour holds up where the population is wrong** — 95 of 105 UNREAD on HOLDOUT-2, with zero false
readings.

---

## 10. PLANNED vs ACTUAL

| # | Planned | Actual | Status |
|---|---|---|---|
| 1 | Failure census by class, counts + denominators + real examples | 5 line classes over 2 398 513 lines; 3 region classes over 784 regions; 4 classes named NOT MEASURED | **DONE** |
| 2 | Corpus/template-assisted recognition | not built — the crop lever reached GATE B without it; recommended for the Ω class | **DEFERRED** |
| 3 | Targeted high-resolution re-crop | built, measured on 5 populations, hand-checked | **DONE** |
| 4 | Alternative OCR observation | same engine, different parameters (crop, scale, language correction off) — measured | **DONE** |
| 5 | Multi-engine disagreement | not run; round 5 already measured that both stacks agree on the wrong character | **NOT STARTED** |
| 6 | Specialised Math/STEM recognition | CodeFormulaV2 run and measured head-to-head | **DONE** (verdict: not recommended) |
| 7 | Geometry-aware recognition | the raster superscript-sign guard is the only piece built | **PARTIAL** |
| 8 | Docling formula enrichment, licensing-safe | licence CDLA-Permissive-2.0 confirmed; run; cost and accuracy measured | **DONE** |
| 9 | Evaluate the 274/336 population | 281 → 234 blocks at recognition level; 0 change in restores | **PARTIAL** |
| 10 | Six metrics, separately | §3 | **DONE** |
| 11 | CI green without corpus | 50 new tests; 672 tool tests pass | **DONE** |
| 12 | Block-level repair from recovered digits | measured, and it does not work; diagnosis and hand-off in §6 | **FALSIFIED** |

### PROVEN
* A targeted re-crop recovers digits the whole-page OCR never read: `3/10`, `5/21`, and 17 of 17 on
  Bài 61, every one verified against the printed page.
* The failure the round-5 report called one class is two: DIGIT LOSS 57 %, SEGMENTATION 36 %.
* `II` is recoverable from the crop and confirmable from the book's own section sequence.

### FALSIFIED
* **The lever does not reach `Ω`** — 0 of 22, at every scale. The glyph is not in the engine's
  repertoire; scale cannot add it.
* **A recovered digit does not become a repaired block by itself** — RESTORE 10 → 10, and the five
  blocks that gained a value gained a malformed one.
* **The unigram diacritic self-contradiction rule** — 26 703 «candidates» whose top rows are
  ordinary Vietnamese words (census §3).
* **The first ohm census rule** — 586 findings, 60 of 60 probed with no ohm on the page.
* **«Higher resolution»** as a description of this lever — the sources are 100 ppi scans; what
  changes is context, framing and segmentation.

### STILL HYPOTHESIS
* That more scales would convert the 97 `INSUFFICIENT_AGREEMENT` regions without raising the false
  rate. Untested.
* That a denominator ink-width check would have refused `3/(x²−x)`. Not built.
* That the in-corpus template recogniser reaches Ω. Not built.
* That the bigram diacritic candidates are real recognition failures. Unchecked against the page.

---

## 11. Reproducing this

```
swiftc -O -o poc-out/bin/ocr_crop tool/ocr/ocr_crop.swift
python3 tool/corpus/recognition/study.py dev        # round 5's tuned pages, incl. Bài 61
python3 tool/corpus/recognition/study.py sdm        # 113 Toán pages: the 274/336 population
python3 tool/corpus/recognition/study.py holdout3 14
python3 tool/corpus/recognition/exponent.py         # then: exponent.py rescore
python3 tool/corpus/recognition/symbols.py roman
python3 tool/corpus/recognition/codeformula.py      # needs the venv with docling
```

Ledgers and every contact sheet that decided a correctness figure are under
`poc-out/round6/recognition/` (gitignored, corpus never enters the repo).

**CI, all three gates green on this branch:**
`flutter analyze` → **No issues found**; `flutter test` → **1019 passed, 45 skipped**;
`python3 -m unittest discover -s tool/tests` → **672 OK, 15 skipped**, of which **50 tests are new**
and none touches the corpus, PyMuPDF, numpy, Vision or the network — they run on ASCII rasters and
plain dictionaries, following round 5's mathfix pattern.

**NO MERGE. READY FOR FOUNDER REVIEW.**
