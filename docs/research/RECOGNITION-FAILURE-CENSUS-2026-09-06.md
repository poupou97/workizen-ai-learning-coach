# RECOGNITION — failure census · Workstream B · round 6 · 2026-09-06

**READY FOR FOUNDER REVIEW — nothing merged.** Branch `ws-b/round6-recognition`, base
`integration/round6-2026-09-06`. Companion: `RECOGNITION-RECROP-RESULTS-2026-09-06.md`, which
measures what can be recovered. This document only **counts**, because that is the round's
standing rule and because two of the five classes counted here turned out to be mostly noise —
which is precisely what a census is for.

Claim labels used throughout: **PROVEN · MEASURED · OBSERVED · INFERRED · HYPOTHESIS · UNKNOWN.**

---

## 0. The three findings that change what to build

**① Round 5's «274 of 336: the OCR never read the digit» is two failures, not one.** MEASURED on
784 printed fraction regions across 113 Toán pages: of the 548 the whole-page OCR could not read,
**312 (57 %) are DIGIT LOSS** — no OCR token of any kind sits over that half of the bar — and
**196 (36 %) are SEGMENTATION** — a token *is* there, and the digit is glued into it, as in
`b) 10 +.` where the page prints `b) 3/10 +`. The remaining 40 (7 %) are structure. The two need
different answers: one needs a recogniser, the other needs a splitter, and reporting them as one
number hid a third of the population.

**② Two of my own five line-level rules were mostly false positives, and the census caught both.**
The ohm rule returned **586** findings; probing the first 60 with the recogniser showed
`52 - 20 = ?` and `520 = 250` from Toán 1 and Toán 2 — **60 of 60 with no ohm on the page**. Keyed
properly it returns **22**, in 11 books, and every example is a real one. The subscript rule
returns **6 168**; hand-checked on a seeded 16-tile sample its precision is **5/16**. Neither
number was wrong by a little.

**③ A failure form nobody had named turned up inside another class's false positives.** On
`11-sgv-toan-11` p74 the page prints `−√2 / 2` and the OCR returns `V2`: **the radical sign is
read as the letter V.** My subscript rule counted it as a flattened index. There are **687**
`V`-shaped subscript candidates corpus-wide — an upper bound on this form, not a count of it,
because `V₂` (a physics symbol with an index) has the same shape in text and only the raster can
tell them apart.

---

## 1. Denominators — three, never summed

| Denominator | Size | What it makes observable |
|---|---|---|
| **LINE** — one Apple Vision OCR line, `poc-out/graph/ocr-body` | **531 books · 62 729 pages · 2 398 513 lines** | a character-level failure |
| **REGION** — one printed stacked-fraction region found from the page raster by `mathfix.detect` | **784** on the 113 Toán pages that have both an SDM and a PDF | «the digit was never read» |
| **BLOCK** — one SDM block | **387** fraction-bearing blocks on those pages | a role/trust decision |

The LINE census is the whole corpus this machine holds; the REGION and BLOCK censuses are the Toán
SDM population, which is where round 5's 274/336 lives.

---

## 2. The census · LINE level

Corpus-wide, over 2 398 513 OCR lines. **These are candidate counts.** Where precision has been
measured it is stated; where it has not, the row says so, because an unmeasured precision is not
a precision of 1.

| Class | Findings | Books | Precision | Representative real example |
|---|---|---|---|---|
| **SUBSCRIPT** (a subscript flattened onto the baseline) | 6 168 | 388 | **5/16** hand-checked, seeded sample | `Khí O2 chiếm…` (prints `O₂`); `nhánh D1)` (prints `D₁`); `= Q3` (prints `Q₃`) |
| **SYMBOL CONFUSION** (Ω read as a capital + digit) | **22** | 11 | not formally sampled; all 12 inspected rows are real | `1 MS = 1 000 000 S2` — the page prints `1 MΩ = 1 000 000 Ω` |
| **SUPERSCRIPT** (a power-of-ten exponent destroyed) | 171 | 47 | 0 false positives in 21 hand-checked readings | `c = 3.10° m/s` (prints `3×10⁸ m/s`); `1 Bar = 10° Pa` (prints `10⁵`) |
| **ROMAN NUMERAL** (a Roman section number broken) | 106 | 59 | 7/8 on the readings that were re-read | `I1 - Định luật khúc xạ ánh sáng`; `Il - Glucose và saccharose` |
| **SEGMENTATION** (enumerator + number + operator fused) | 24 | 10 | all 24 inspected are the same real shape | `b) 10 +.` — the page prints `b) 3/10 +` |
| **DIACRITIC** | see §3 | — | unigram rule **FALSIFIED**; bigram rule = candidate list | `thong tin` 16 × against `thông tin` 262 × in one book |
| OPERATOR LOSS · MATH REGION · FORMULA · TABLE/STRUCTURE | **NOT MEASURED at line level** | — | — | see §4 |

Sub-form worth naming inside SUBSCRIPT: **`V` + digit — 687 candidates**, of which an unknown
share are `√n` misread (OBSERVED on two tiles), and the rest are genuine physics indices `V₁`,
`V₂`. Shape cannot separate them; the raster can (a radical has a diagonal and an overbar).

### 2.1 The two corrections, stated as corrections

| Rule | First version | Corrected | What the first version was actually counting |
|---|---|---|---|
| `ohm-lost-v1` | **586** findings / 101 books | **22** / 11 books | `52`/`92` were in the alternation and a bare `=` counted as a unit context, so primary-school arithmetic matched: `52 - 20 = ?`, `52 + 3 = 55.`, `520 = 250` |
| `subscript-flattened-v1` | 6 168 | 6 168, **precision 5/16** | spreadsheet cell references (`B5`, `C6`), keyboard keys (`F4`), paper sizes (`A0`), language levels (`C1`), Lewis-structure labels (`N3`) — and `√2` read as `V2` |

Neither was found by review. The ohm rule was found by handing its first 60 findings to the
recogniser and reading what came back; the subscript rule was found by cropping 16 of its findings
and looking at the printed page. **Probing a census is cheap and it is not optional.**

---

## 3. DIACRITIC — a rule measured and refused

The intended evidence was the book contradicting itself: a press does not set `Cộng hoà` 350 times
and `Cong hoa` twice on purpose.

**Unigram form — FALSIFIED.** Over 2 398 513 lines it returns **26 703 forms in 529 books,
159 444 bare occurrences**, and its highest-ranked rows are `qua`/`quá`, `cung`/`cũng`,
`nay`/`này`, `thu`/`thủ`. Every one of those bare forms is an ordinary Vietnamese word. The test
cannot separate a lost tone mark from a different word without a lexicon it does not have, so its
output is a **denominator, not a count**. It is kept in the code, and pinned by a test, so that
nobody re-adopts it by accident.

**Bigram form — a candidate list, not a finding.** Requiring an adjacent pair to match after
stripping cuts it to **2 778 forms in 450 books, 4 498 bare occurrences**, and the top rows are
collocations: `thong tin` 16 × against `thông tin` 262 × in one book, `phat trien` 4 × against
`phát triển` 656 ×. That is the right shape of evidence, and it is still **OBSERVED**, not proven:
no sample of these has been checked against the printed page. Lane A4 measured the same family
independently in round 5 (`Cộng hoà` → `Cộng hoa`, 358 × across ≥5 books).

---

## 4. Classes this census cannot observe, and why

Honest gaps, listed rather than estimated.

| Class | State | Why |
|---|---|---|
| **OPERATOR LOSS** | NOT MEASURED at line level; measurable at region level only | a printed `−` that no token covers is invisible in text. Round 5's `ink-accounted-v1` finds it from the raster inside a block; a corpus-wide count needs a raster pass over 62 729 pages, which was not run |
| **MATH REGION** | MEASURED by round 5, not re-measured here | 14 of 15 Docling `formula` blocks on the legacy Toán pages die as role `empty`, reason «no letters» (`tc2_sdm.py:276-277`). That is a ROLE decision, WS-A/WS-C territory |
| **FORMULA** | MEASURED by round 5 | FORMULA recall 0.000 (Lane A3); 8 of 19 gold formulas withheld as empty blocks |
| **TABLE/STRUCTURE** | NOT MEASURED | no table ground truth exists on this branch; inventing one to fill a census row would be worse than the gap |
| **OTHER** | NOT MEASURED | by definition |

---

## 5. The census · REGION level — where round 5's 274 actually splits

113 Toán pages with both an SDM and a PDF; **784** printed fraction regions found from the raster,
of which the whole-page OCR read both halves on 236 and could not on 548.

| Failure class | Regions | Share of the unreadable population | What it means |
|---|---|---|---|
| **DIGIT LOSS** | **312** | 0.569 | no OCR token of any kind lies over that half of the bar. Nothing was recognised there |
| **SEGMENTATION** | **196** | 0.358 | a token *is* there and is not a bare digit run — the ink was recognised and glued to something else |
| **FRACTION STRUCTURE** | 40 | 0.073 | two candidates in one strip, or a digit claimed by two fractions; the detector fails closed |

DEV pages (round 5's own 16) split the same way: DIGIT LOSS 72 · SEGMENTATION 45 ·
FRACTION STRUCTURE 11 of 128.

**Why this matters for what gets built.** Round 5 recommended a recogniser on the strength of
«274 of 336 — the OCR did not read the digit». That is right for 57 % of the population. For the
other 36 % the digit *was* read, and a token splitter — cheap, deterministic, no recogniser —
could reach it. Neither of those two things is a reason to build the other.

---

## 6. Reproducing every number here

```
python3 tool/corpus/recognition/cli.py lines --books-glob '*' --diacritics --suffix=-all-v2
python3 tool/corpus/recognition/study.py sdm        # region + block census, and the re-crop
```

Outputs under `poc-out/round6/recognition/` (gitignored): `line-census-all-v2.json`,
`study-sdm.json`. The contact sheets that decided every precision figure are beside them:
`sheet-subscript-sample16.png`, `sheet-p022-recovered.png`, `sheet-bai61-p083-recovered.png`,
`sheet-exponent-recovered.png`, `sheet-roman-recovered.png`.

Tests that run without the corpus: `tool/tests/test_recognition_census.py` (20),
`test_recognition_consensus.py` (14), `test_recognition_exponent.py` (16).

**NO MERGE.**
