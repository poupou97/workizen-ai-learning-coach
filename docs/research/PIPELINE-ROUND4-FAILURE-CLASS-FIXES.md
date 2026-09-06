# Pipeline — round 4 failure-class fixes (MEASUREMENT + CHANGE LOG)

Round 4 · Lane A-pipeline (PROVE) · 2026-09-05 · branch `lane-a/round4-pipeline-failure-classes` → `integration/round4-2026-09-05`
· input: `docs/research/FALSE-TRUST-AUDIT-RESULT-2026-09-05.md` (the 484-row shipped-content sample, seed 20260905) and
`docs/research/lane-c/05-GOLDEN-SLICE-2-GATE.md` (PR #75).

**Status: MEASUREMENT + CODE. No acceptance threshold is set, no trust threshold was lowered, no guard was loosened, no
coverage claim is made.** Every number carries its denominator (D5); Wilson 95 % intervals where a rate is claimed. Verbatim
SGK text, crops, TSL and packs stay in the gitignored `poc-out/` (D4) — this document quotes anchors and single numbers only.

The lane inherited a work-in-progress snapshot (commit `206a103`) whose classes 1, 2, 2b and 3 were implemented and whose
classes 4 and 5 existed only as failing tests (13 errors, 1 failure). Those are finished here.

---

## 0. Headline — the gold set, same 54 pages, same scorer, before → after

`tc2-p1` (as shipped) vs `tc2-p2` (this branch), both scored by `tool/corpus/tc2_score.py` against the **corrected** gold
(§5 errata), so the two columns are comparable:

| measure (54 gold pages · 643 learning blocks) | tc2-p1 | tc2-p2 | direction |
|---|---|---|---|
| trusted blocks (coverage) | 439 (0.683) | 354 (0.551) | **↓ deliberate** — more withheld |
| TLSR | 0.617 | 0.510 | ↓ |
| false-trusted blocks | 42 | 26 | **↑ better** |
| FTR (false trusted / trusted) | 0.0957 [0.0716, 0.1268] | **0.0734 [0.0506, 0.1054]** | ↑ better (intervals overlap) |
| safe rejections | 188 | 273 | ↑ |
| trusted blocks whose digits differ from the gold | 12/115 = 0.1043 [0.061, 0.174] | **6/89 = 0.0674 [0.031, 0.139]** | ↑ better |
| meaning-changing order inversions | 44 | 33 | ↑ better |
| CTE (critical teaching errors) | 79 on 23 pages | 68 on 21 pages | ↑ better |
| **lesson attachment (header) correct** | **45/54** | **48/54** | **↑ better** |
| attachment (TOC range) correct | 38/54 | 38/54 | = |
| text accuracy / found / fidelity / splices | 0.969 / 0.979 / 1.000 / 0 | 0.970 / 0.979 / 1.000 / 0 | = |
| QUESTION precision / recall | 0.882 / 0.776 | 0.877 / 0.802 | recall ↑, precision ≈ |

**The trade is explicit and is the point:** the pipeline now withholds 85 more blocks of 643 and delivers 16 fewer wrong ones.
Coverage is not a goal of this lane; a block the two OCR stacks disagree about is withheld rather than taught.

Evidence (internal, gitignored): `poc-out/round4/pipeline/tc2-p2/metrics/gold-scores-BEFORE-tc2-p1-errata-gold.{json,md}` and
`gold-scores-c5-final.{json,md}`; staged runs of the inherited classes in `gold-scores-c1-order`, `-c2-numbers`, `-c3-roles`.
Baselines of each stage are kept under `poc-out/round4/pipeline/tc2-p2/baseline-c1|c2|c3|c3b-tones/`.

`flutter test`: **861 passed, 36 skipped, exit 0** — the bridge's output *shape* is unchanged (§6.5), and the real fixture the
app loads was **not** overwritten (§9).

---

## 1. Class 1 — two-column reading order (inherited, verified)

**Mechanism** (audit §4.3): Docling's reading order interleaves side-by-side boxes line by line, so a two-column definition
becomes a false statement. 78 % of the audit's order errors and *every* attachment error sat on `two_col` pages.

**Fix** (commit `7140c35`, predecessor): reading-order agreement between the primary (Docling) and the verifier (XY-cut) is
computed as a longest increasing subsequence; a block the verifier places elsewhere is re-sequenced **only** when the move is
justified by geometry, otherwise the block is withheld with `agree_order`.

**Measured** (54 gold pages): meaning-changing inversions **44 → 33**; order score 0.985 → 0.988; `agree_order` withholds
15 → 41. Tests: `tool/tests/test_tc2_order.py`.

**What got worse, stated:** on the KHTN 6 Bài 17 gold stratum, which had **0** order errors in the audit, re-sequencing
introduces **1** meaning-changing inversion (p063 gold block `b07`; CTE 3 → 4). Re-sequencing cannot help a page that was
already right, and here it cost one block. Not tuned away — reported.

## 2. Class 2 — formula / number / unit / chemistry fidelity (inherited, verified)

**Mechanism** (audit §4.1): flattened fractions, exponents and chemical subscripts produce **false data** — `1/5 giờ` → `5 giờ`
flips an answer; `9 dm = 9/10 m` → `9 dm = 9 m` inside the definition of decimals; `AgNO₃` → `AgNO,`.

**Fix** (commit `84f54e6`): `agree_numbers` (the two stacks deliver different digit sequences) and `chem_guard` (a chemical
formula whose subscript cannot be confirmed) **withhold, never guess or repair**.

**Measured** (54 gold pages): trusted blocks whose digit sequence differs from the gold **12/115 → 6/89**
(0.104 [0.061, 0.174] → 0.067 [0.031, 0.139]). New withholds: `agree_numbers` 19, `chem_guard` 7. Tests:
`tool/tests/test_tc2_guards.py`.

## 3. Class 2b — tone-mark agreement, and the falsified assumption A26

**Mechanism:** a block with `text_sim = 100` can still be non-verbatim. Two independent OCR stacks make the *same* display-font
tone slip, so agreement certifies a word the book does not print.

**Fix** (commit `9d9816d`): `agree_tones` withholds a block when the two stacks' tone-stripped token keys match but the tones
differ. **Nothing is repaired** — normalising tones before comparing would hide the defect, which is exactly what the audit is
measuring.

**Measured on the Bài 17 stratum** — the audit named ten tone-mark non-words in the 60 TRUSTED blocks
(`không khi`, `lăng xuông`, `thủỷ`, `phẫu`×3, `Tiền hành`×2, `bế/bấn`, `Em cô thể`, `vặn khoa`, `phếu`). Scanning those 60
blocks for the audit's own strings:

| | blocks |
|---|---|
| tc2-p1 TRUSTED Bài 17 blocks | 60 |
| …carrying at least one audit-named tone slip | 11 |
| …**now WITHHELD** by `agree_tones` | **7** (0.636 [0.354, 0.848]) |
| …still TRUSTED | 4 |

The four survivors are the structural limit, not a threshold: `phẫu`/`phếu` for `phễu` changes the **base vowel**
(keys `phau`/`pheu` ≠ `pheu`) so it is a text disagreement, not a tone one — and it passes the text gate because *both* stacks
read it the same way; `Tiền hành:` for `Tiến hành:` has the same stripped key but **both stacks agree on the slip**, so an
agreement guard is blind to it by construction. **A26 stands falsified: agreement ≠ verbatim, and no agreement guard can close
the gap.** Catching these needs a signal outside the two stacks (a lexicon, a third stack, or a human) — a Founder decision, not
a threshold.

## 4. Class 3 — role layer (inherited, verified)

**Fix** (commit `76633ee`): a numbered item continuing a `?`-box is a `question`, not a sidebar; icon / box-tint signals stay
behind a flag (`--role-signal`, default off).

**Measured**: on the Bài 17 gold stratum QUESTION recall **0.889 → 1.000** and precision 0.727 → 0.750; SIDEBAR precision
0.800 → 1.000; on the 54 gold pages QUESTION recall 0.776 → 0.802. Tests: `tool/tests/test_tc2_roles.py`.

Concretely, this fixes **one of the two role errors the audit found in Bài 17**: block `p061:019`
(«2. Lấy một số ví dụ về quá trình tách chất …») moves `sidebar` → `question`. The other is fixed by class 5 (§7.2).

---

## 5. Gold errata — LS&ĐL 5 p041 and p080 (Lane C request 1) · DONE

Lane C's independent second reviewer found the gold's lesson numbers wrong on two pages and the pipeline right. This lane
verified it separately by scanning the printed banner of **all 123 pages** of the book:

| gold page | printed | gold said | printed banners | corrected to |
|---|---|---|---|---|
| PDF 41 | 39 | Bài **9** | «BÀI 8» PDF 38 (printed 36) · «BÀI 9» PDF 42 (printed 40) | **Bài 8** |
| PDF 80 | 78 | Bài **17** | «BÀI 18» PDF 78 (printed 76) · «BÀI 19» PDF 84 (printed 82) | **Bài 18** |

Both files already carried the *right lesson's* TOC title beside the wrong number. The correction is **not silent**: each file's
`lesson.errata` records `id`, `date`, `was`/`now`, who reported it, who verified it, why, and the effect; a test
(`tool/tests/test_lane_c_requests.py::GoldErrataTests`) fails if it is reverted.

**Effect on previously reported attachment scores:** these two pages were counted as attachment errors against a pipeline that
was right, so **every attachment number reported before this errata undercounts by two**. On the round-4 gold set the tc2-p1
baseline moves **43/54 → 45/54** with no pipeline change at all; this branch's own figure moves 47/54 → 49/54 before the
regression fix of §6.1, and stands at **48/54** after it. No other metric uses the lesson number, so text / role / trust /
digit figures are unaffected.

---

## 6. Class 4 — lesson attachment / identity · DONE

### 6.1 The back cover (8 of the audit's 11 wrong attachments)

**Mechanism**: nothing marked a book's back cover as end matter, so the publisher's book list, ISBN, barcode and price were
attached to the book's **last lesson** and served as an exercise (audit sample 0150: «8. Mĩ thuật 4 Website: … ISBN …» served
as an exercise of Bài 73).

**Fix**: `tc2_attach.page_info` recognises a cover by its *furniture*, never by position alone — ISBN, `Website:`, `Giá:`,
`BỘ SÁCH GIÁO KHOA`, `HUÂN CHƯƠNG`, `NHÀ XUẤT BẢN GIÁO DỤC`, an EAN-13 digit run — and requires **two independent marks**
inside the last 12 % of the book (or the first three pages, for a front cover). `back_cover` ends the book: the page carries no
lesson and every page after it is end matter.

**Measured on the audit's own rows** (`poc-out/round3/ft-audit/annotated-20260905.jsonl`, the same seed and sample):

| | before | after |
|---|---|---|
| audit attachment error, per activity | **11 / 396 = 0.0278 [0.0156, 0.0490]** | — |
| of those 11, page verdict now correct | — | **10** (8 back-cover rows become `kind=back_cover, lesson=None`; the LS&ĐL 5 map page reads Bài 2 where the registry says 1; the Toán 5 exercise page reads Bài 35 where the key says 29) |
| of those 11, still wrong | — | **1** — sample 0177, Toán 4 tập một PDF 76: Bài 22's «khám phá» starts mid-page and no header is detected on that page, so the page stays Bài 21 |
| of the **473** rows the audit judged attachment-OK, rows now on a non-lesson page | — | **0** — the cover rule breaks nothing on this sample |

Across the **42** books this branch attached, **42 / 42** now detect a back cover; of the 35 that also have a tc2-p1 attach
file to compare against, that page had previously been **inside a lesson in 20**.

**Caveat, stated plainly:** this measures the page verdict of `tool/corpus/tc2_attach.py`. The shipped pack is built by
`tool/ui/lesson_attach.py`, which consumes that verdict (`HEADER_NO_LESSON`). Packs are not rebuilt in this lane, so the
*shipped* attachment rate is unchanged until someone rebuilds them.

### 6.2 The TV5 «+2» offset

**Mechanism** (audit §2): TV5 books print the lesson badge 1–3 printed pages **before** the TOC's `pageStart`, so a
header-versus-TOC comparison conflicted on nearly every lesson and the TOC won.

**Fix**: a per-book **systematic TOC offset**, measured from the headers themselves — when ≥ 5 detected headers carry a TOC
start and ≥ 60 % of them share one non-zero (header − TOC) difference, every TOC start is shifted by it before it confirms
anything. Implemented in both `tc2_attach` (`_systematic_toc_offset`) and the pack builder (`lesson_attach.systematic_toc_offset`,
rule id bumped `capped-toc-v1` → **`capped-toc-v2`**; every v1 decision is otherwise unchanged).

**Measured** over the 42 books this branch attached: a non-zero offset is found in **3** of them, all −2 —
**TV5 tập hai** (headers 26 → 30, **18 pages newly attached**), **TV2 tập một** (30 headers, 3 pages newly attached) and
**TV2 tập hai** (headers 28 → 29, 4 pages newly attached). It is **not** found in TV5 tập một or TV4 tập một (offset 0):
the audit's «+1…+3 on the TV5 books» is a real pattern in TV5 tập hai and the TV2 pair, and the rule fires only where the
evidence is there (≥ 5 headers with a TOC start, ≥ 60 % sharing one non-zero difference) — it does not fire on a hunch.
Tests: `tool/tests/test_tc2_attach.py` (`SystematicOffsetTests`, `LessonAttachOffsetTests`).

### 6.3 A regression this lane found in its own inherited code, and removed

The inherited TOC-range fallback ran **before any header had been seen**, taking `max(due)` — the highest lesson number whose
TOC start is at or before the page. On KHTN 9 the book's *second* TOC page is not detected as a TOC (it prints no «MỤC LỤC»),
so the fallback fired there and put it, and the eight lesson pages that continue from it, into **Bài 26 instead of Bài 1**.
`max(due)` before the first header is a guess, not a fallback, and was removed.

Cost, measured: attachment on the gold set was **49/54 with one page actively wrong**; it is **48/54 with none wrong**. Two
pages the branch had guessed right now carry no lesson at all (Toán 12 p020), and Tin học 6 / Toán 12 attach 11 and 8 fewer
pages. Withholding beats guessing.

### 6.4 Gold-set attachment, per page

| page | tc2-p1 | tc2-p2 |
|---|---|---|
| `04-sgv-toan-4` p054 | Bài 10 ✗ | **Bài 11 ✓** |
| `06-sgk-tin-hoc-6` p021 | Bài 4 ✗ | **Bài 5 ✓** (`toc_range`) |
| `09-sgk-toan-9-tap-mot` p029 | Bài 3 ✗ | **Bài 4 ✓** |
| `05-sgk-lich-su-va-dia-li-5` p041 / p080 | ✓ (was scored ✗ — gold errata, §5) | ✓ |
| all others | unchanged | unchanged |

**45/54 → 48/54**; error rate 0.1667 [0.090, 0.287] → 0.1111 [0.052, 0.222]. Three pages fixed, **zero regressed**.

### 6.5 A versioning defect found while running the slice

A TSL block id embeds the **pipeline name** (`…:p063:tc2-p1:005`). The Bài 17 tutor script hard-codes the six ids it quotes, so
rebuilding the lesson as `tc2-p2` lost the entire scripted tutor with the message «TSL thiếu block» — blaming withholding for
what was a naming mismatch. Lookup is now pipeline-agnostic (`block_key`) while the ids **emitted as provenance are still the
real ones**: the tc2-p1 document hash is byte-identical before and after the fix (`7419cd60…`).

Also fixed while running the slice: `render_crops` assumed a figure's `labels` was a list of ids (the TSL stores a **count**),
and `chapters_from_toc` returned `[]` silently when the bridge could not see `poc-out` at all (it derives ROOT from `__file__`,
so a git worktree finds nothing) — it now says so and names `TC_ROOT`.

---

## 7. Class 5 — figure / caption relation · DONE

### 7.1 `caption_of` association — geometry instead of reading order

**Mechanism**: tc2-p1 linked a `caption` block to a picture by **reading-order distance** (`abs(order − rank) ≤ 2`). On a page
with several pictures, badges and mascots that is a coin flip. A wrong caption is worse than none: the child is told the picture
shows something it does not.

**Fix**: `tc2_sdm.caption_for_picture` — a caption belongs to a picture when it **overlaps it horizontally** and either sits
just **below** it (≤ 2.5 median line heights, the printed convention), **inside its lower band** (Docling grows a picture box
over its own caption), or just **above** it (≤ 1 median line height, held much tighter because a body line above is common and a
caption above is rare). Nearest qualifying caption wins; **no geometric fit ⇒ no caption**. One caption may serve side-by-side
pictures and is not consumed by the first of them.

**Measured** by replaying both rules and asking, of each link `tc2-p1` actually stored, whether that caption could belong to
that picture at all:

| set | pictures | tc2-p1 links | tc2-p2 links | tc2-p1 links **geometrically impossible** |
|---|---|---|---|---|
| 54 gold pages | 180 | 41 | 29 | **17 / 41 = 0.415 [0.278, 0.566]** |
| KHTN 6 Bài 17 (PDF 61–64) | 19 | 7 | 9 | **3 / 7 = 0.429 [0.158, 0.750]** |
| KHTN 6 Bài 15 (PDF 53–56) | 28 | 17 | 17 | **16 / 17 = 0.941 [0.730, 0.990]** |
| LS&ĐL 5 Bài 8 (PDF 38–41) | 14 | 4 | 3 | **1 / 4** |
| LS&ĐL 5, whole book (123 pages) | 390 | 175 | 141 | **64 / 175 = 0.366 [0.298, 0.439]** |

Bài 15 is the worst case and the clearest: a page of small side-by-side food photographs, where the order rule mislinked
16 of 17 captions.

**The O5 mislink Lane C reported is reproduced and fixed.** LS&ĐL 5 PDF 40: caption «Hình 2. Đền thờ Lý Nam Đế (tỉnh Phú Thọ)»
(bbox x 0.361–0.675, y 0.664) was linked both to the real photograph (bbox y 0.385–0.656, directly above it — correct) **and**
to a small badge at bbox x 0.079–0.285, y 0.708–0.785, which sits *below* the caption in the left margin with **no horizontal
overlap at all**. tc2-p2 keeps the first link and drops the second.

**Note on the scorer's `caption_assoc` column**: it fell 0.714 → 0.627 in this branch, and that is **not** this fix. That metric
asks whether a gold caption's matched block has role CAPTION *and lies within ±2 reading-order positions of some figure block* —
it is an order-adjacency proxy that never reads `figures[].caption`. It dropped at the class-1 re-sequencing stage
(`gold-scores-c1-order`, before any class-5 code existed) because re-sequencing moved figure blocks. The table above measures
the association itself.

### 7.2 The caption-like paragraph

**Mechanism** (audit §3.2): «Hình 17.1» and its sentence are printed as two blocks on one line; tc2-p1 gave the label `caption`
and served the sentence as lesson prose. This is one of the two role errors the audit found in Bài 17.

**Fix**: `tc2_sdm.caption_continuation_pass` — a block becomes the continuation of a caption label when the label is a bare
«Hình/Bảng/Sơ đồ/… N», the candidate starts on the **same printed line** (centre within ½ a line height) within 3 line heights
to its right, is short (≤ 90 chars), carries no enumerator and does not end a sentence. Deterministic; no text is repaired.

**Measured**: fires on **2 of 311 pages scanned** — KHTN 6 p061 («Một số hiện tượng tách chất khỏi hỗn hợp») and p062
(«Bộ dụng cụ lọc đơn giản»), i.e. **exactly the audit's Bài 17 caption-as-body error, and nothing else**. A narrow rule that hits
what it was written for and stays silent elsewhere. Tests: `tool/tests/test_tc2_captions.py`.

**Both of the audit's two Bài 17 role errors are now fixed** (this one and §4).

### 7.3 Crop bbox bleed

**Mechanism**: every crop was padded by a fixed 0.012 of the page on all four sides. On a dense page that pulls the neighbouring
paragraph's first line into the picture, and the child reads it as part of the figure.

**Fix**: `tsl_to_lesson_document.crop_pads` — each side is padded by at most the free distance to the nearest neighbouring block
**on that side** (a block counts only if it also overlaps on the perpendicular axis), minus a 0.003 gap, never below 0. A crop
can lose padding; it can never gain foreign content. A figure's own caption never clips its padding.

**Measured** (a crop "bleeds" when its padded box overlaps a block the region itself does not touch):

| set | crops | bled before | bleeds now |
|---|---|---|---|
| KHTN 6 Bài 17 (tc2-p1 regions) | 12 | **7 = 0.583 [0.320, 0.807]** | **0** |
| KHTN 6 Bài 17 (tc2-p2 regions) | 21 | 15 = 0.714 | **0** |
| KHTN 6 Bài 15 | 33 | **16 = 0.485 [0.325, 0.648]** | **0** |
| LS&ĐL 5, all 23 lessons | 379 | **214 = 0.565 [0.514, 0.614]** | **1 = 0.0026 [0.0005, 0.0148]** |

The single residual is a **diagonal** neighbour: padding two adjacent sides expands the corner, and the per-side rule only
measures axis-aligned neighbours. Known, 1 in 379, left as is rather than papered over.

---

## 8. Lane C's cross-lane requests (PR #75)

| # | request | status | measured |
|---|---|---|---|
| 1 | gold errata, LS&ĐL 5 p041 / p080 | **DONE** | §5 — corrected with a recorded `errata` block; tc2-p1 baseline 43/54 → 45/54 with no code change |
| 2 | `LESSON_HDR` lacks `Ã` — the banner OCRs «BÃI» | **DONE** | LS&ĐL 5 headers **23 → 28 of 28**; **17 pages moved** between lessons (+1 detached as back cover) — exactly Lane C's probe. Bài 3, 7, 11, 13, 23 are now ranged |
| 3 | page-level `color_heavy` is too coarse | **DONE** | `colour_heavy_withholds`: the page flag still selects which pages are examined; inside them the block's **own** colour share decides against the census's same 0.25; no mask ⇒ withholds as before. LS&ĐL 5 **p038: 7/22 → 13/22 learning blocks trusted** (0.318 → 0.591), `color_heavy` withholds on that page **14 → 4**; whole book **23 → 11**. The «Âu Lạc (179 TCN)» anchor's page is no longer blanket-withheld |
| 4 | `figure_dependent` misses «quan sát các hình …» | **DONE** | `FIG_REF` also matches a look-verb followed within a clause by a figure noun with no number. LS&ĐL 5 `figure_dependent` withholds **39 → 58** |
| 5 | no `attribution` role; dash sub-questions as body | **DONE** | new fine role `attribution` (coarse BODY, bridge type `paragraph`, so gold scores and the LessonBlock shape are unchanged and only `sourceRole` differs): **51 blocks** in LS&ĐL 5, including the gold-p041 «(Theo …)» block. A «… em hãy:» lead is a question, and a dash sub-item is read without its bullet **only** under such a lead: LS&ĐL 5 `question` **134 → 215**, of which **77** carry the dash evidence. Fail closed: a parenthesised proper name alone («(Hồ Chí Minh …)») stays body — a recorded gap |
| 6 | chapters are «Chủ đề», not «Chương» | **DONE** | `toc-ocr-chapters-v2` reads Chủ đề / Chương / Phần, tolerates the tone slip the TOC itself prints («CHỦ ĐẾ 6»), and strips dot leaders and the trailing page number. LS&ĐL 5 **0 → 6 chapters** (Chủ đề 1–6, 4+3+10+4+4+3 lessons); KHTN 6 unchanged at 10 (Chương I–X) |
| 7 | fold `prose-dated-events-v1` and `story-attribution-v1` into the bridge | **DEFERRED — Founder gate** | Lane C's own document marks both **PROPOSED, nothing Founder-approved**, and folding them changes what the bridge emits (`semantic[]`), which Lane B and Lane A-runtime consume. Not a decision this lane may take (CLAUDE.md rule 5). The Python rules stay in `tool/research/lane_c/`; when the Founder accepts them the fold is small — they already run on trusted blocks only and keep block ids |

Tests for 2–6: `tool/tests/test_lane_c_requests.py` (17 tests).

**Cost of request 3 + 5, stated:** LS&ĐL 5 whole-book coverage falls **0.850 [0.831, 0.867] → 0.689 [0.665, 0.711]**
(1281/1507 → 1041/1512 trusted learning blocks). The colour fix *adds* trust on opener pages (−12 colour withholds book-wide);
the round-4 fidelity guards subtract far more (`agree_tones` +184, `agree_order` +48, `agree_numbers` +23,
`figure_dependent` +19). Lane C's slice will see fewer trusted blocks than in their PR #75 run.

---

## 9. Golden slice re-run — Bài 17 as `tc2-p2`

Versioned under `poc-out/round4/pipeline/tc2-p2/`; **`tc2-p1` was never written to.** Raw Docling/XY-cut candidates are reused
from tc2-p1 (they are deterministic per page and independent of everything this lane changed), so the re-run is seconds, not
minutes.

### 9.1 TSL diff (KHTN 6 Bài 17, PDF 61–65)

| | tc2-p1 | tc2-p2 |
|---|---|---|
| boundary | 61–65, confidence 0.95, header found | **identical** |
| sourceability | PARTIAL | PARTIAL |
| trusted blocks | 60 | **51** |
| withheld blocks | 4 | **13** |
| withheld reasons | `page_feature:diagram` 3, `math_guard` 1 | `agree_tones` **8**, `page_feature:diagram` 3, `agree_order` **1**, `math_guard` 1 |
| figures with a caption | 7 / 19 | **9 / 19** |
| provenance bbox present | 60/60 | 51/51 |

- **9 blocks moved TRUSTED → WITHHELD; 0 moved the other way.** Eight are tone disagreements (§3), one is an order disagreement.
- **0 blocks changed their text.** Nothing was repaired, normalised or rewritten.
- **2 role changes, both the audit's own Bài 17 role errors**: `p061:019` sidebar → question, `p061:015` body → caption.
- 2 blocks changed reading-order position.

### 9.2 LessonDocument diff (through the bridge)

| | tc2-p1 | tc2-p2 |
|---|---|---|
| blocks | 73 (69 trusted + 4 withheld) | 73 (**60 trusted + 13 withheld**) |
| by type | heading 13 · activity 12 · question 11 · paragraph 16 · image 8 · caption 8 · withheld 4 · sourceRef 1 | heading 12 · activity 8 · question 11 · paragraph 11 · image 8 · **caption 9** · **withheld 13** · sourceRef 1 |
| chapters | 10, chapter «Chương IV» | 10, «Chương IV» |
| semantic | process ×2 + comparison | **process ×1** + comparison |
| tutorScript | present | **absent** |
| hash | `7419cd60…` | `0c50527f…` |

**Two regressions, reported not worked around:**

1. The `process` «Lọc nước từ hỗn hợp nước lẫn đất» disappears: its enumerated steps include `p062:012`
   («Chuẩn bị: … cốc **thủỷ** tinh, … **phẫu** lọc … **Tiền** hành:»), now withheld by `agree_tones`.
2. The Bài 17 **tutor script disappears** because **exactly one** of the six blocks it quotes is withheld: `p063:005`
   («Phương pháp cô cạn dùng để tách chất tan rắn ra khỏi dung dịch»), withheld by `agree_order`. Five of six survive.
   After the fix in §6.5 the diagnostic names the block (`co_can`) instead of blaming the pipeline version.

This is the honest shape of the trade at document level: a scripted tutor and one process diagram are lost rather than built on
blocks whose two readings disagree. **Whether that is the right trade is a Founder decision, not this lane's.**

### 9.3 Bài 17 gold stratum (4 pages, 53 learning blocks)

| | tc2-p1 | tc2-p2 |
|---|---|---|
| trusted (coverage) | 50 (0.943 [0.846, 0.981]) | 44 (0.830 [0.708, 0.908]) |
| TLSR | 0.887 | 0.774 |
| false trusted | 3 | **3** |
| FTR | 0.0600 | **0.0682** |
| safe rejections | 3 | 9 |
| meaning-changing inversions | 0 | **1** |
| CTE | 3 (`nonquestion_as_question` ×3) | 4 (+ `order_changes_meaning` ×1) |
| QUESTION P / R | 0.727 / 0.889 | **0.750 / 1.000** |
| SIDEBAR precision | 0.800 | **1.000** |

**On this stratum the guards did not remove a single one of the 3 blocks the gold calls false-trusted**, so FTR gets *worse*
(the numerator is unchanged, the denominator shrank) and one order inversion is introduced. The improvements here are in the
role layer. Bài 17 was the pipeline's best case in the audit (0 teaching-critical errors in 60 blocks); there is little for a
fidelity guard to win and something for re-sequencing to lose.

---

## 10. What remains

1. **The audit's last attachment error** (sample 0177): a lesson that starts **mid-page** with no detected header.
   `lesson_for_block` already splits a page at a *detected* mid-page header; here none is detected.
2. **Tone slips both stacks agree on** (§3): unreachable by an agreement guard. Needs a signal outside the two stacks.
3. **Circled section numerals** (`I` → `·`, `II` → `I`, 2 of the audit's 12 Bài 17 display errors): no guard has a signal for
   them.
4. **`attribution` for a bare parenthesised name** («(Hồ Chí Minh …)»): deliberately not promoted.
5. **The one diagonal crop bleed** in 379 (§7.3).
6. **Packs are not rebuilt.** The class-4 gains are measured on the page verdict; the shipped rate moves only when packs are
   rebuilt against `WAL_TC2_ATTACH_DIR`.
7. **Lane C's two PROPOSED rules** (§8 row 7) await a Founder decision.
8. **Second annotator.** The audit protocol still requires ≥ 10 % re-annotation before any bar is called met; nothing here
   changes that.

---

## 11. Stable CLI (for Lane D)

`TC_ROOT` names the checkout that holds `poc-out/` (default: the main checkout; **required** when running from a git worktree).
`--out DIR` is the pipeline directory itself and is what makes a run versioned — a `tc2-p2` run never writes into `tc2-p1`.

```bash
R=/Users/alexnguyen/projects/workizen-ai-learning-coach
OUT=$R/poc-out/round4/pipeline/tc2-p2          # or poc-out/round4/legacy/<batch> for Lane D

# 0. name a bounded batch  →  $OUT/pages-<request>.json
python3 tool/corpus/tc2_run.py --pipeline tc2-p2 --out $OUT \
        --make-pages 06-sgk-khoa-hoc-tu-nhien-6:61-64      # or <book> for the whole book, or `slice`

# 1. raw candidates. Docling needs the bake-off venv; xycut/naive do not.
#    Raw files of an EARLIER pipeline version are reused automatically (--no-reuse-raw to force a fresh run).
python3 tool/corpus/tc2_run.py --pipeline tc2-p2 --out $OUT --pages $OUT/pages-<request>.json --fast
$R/.venv-bakeoff/bin/python tool/corpus/tc2_run.py --pipeline tc2-p2 --out $OUT \
        --pages $OUT/pages-<request>.json --workers 2

# 2. SDM (roles, guards, trust)          --force to rebuild, --gold for the 54 gold pages → sdm-gold/
python3 tool/corpus/tc2_sdm.py --pipeline tc2-p2 --out $OUT --pages $OUT/pages-<request>.json

# 3. lesson attachment, per book          --gold-books for every book that has a gold page
python3 tool/corpus/tc2_attach.py --pipeline tc2-p2 --out $OUT <book>…

# 4. Trusted Structured Lessons, per book → $OUT/lessons/<book>/bai-NN.tsl.json
python3 tool/corpus/tc2_tsl.py --pipeline tc2-p2 --out $OUT <book>…

# 5. LessonDocument (+ crops)             --no-crops to skip rendering
TC_ROOT=$R python3 tool/corpus/tsl_to_lesson_document.py \
        --tsl $OUT/lessons/<book>/bai-NN.tsl.json --out $OUT/lesson-document

# 6. score against the gold set           --gold-dir tool/corpus/tc_gold_bai17 for the Bài 17 stratum
python3 tool/corpus/tc2_score.py --pipeline tc2-p2 --out $OUT \
        --json $OUT/metrics/gold-scores.json --md $OUT/metrics/gold-scores.md

# packs (not this lane): point the pack builder at the run in hand
WAL_TC2_ATTACH_DIR=$OUT/attach <pack build command>
```

There is **no** `--book/--pages a-b/--version` interface; the versioning axis is `--pipeline` + `--out`, and the batch axis is
a pages JSON file. Steps 2–6 are deterministic and idempotent: re-running writes the same bytes.

---

## 12. Denominators (D5)

Gold-set rates are `k / n` over the **54 hard gold pages** (643 learning blocks) of `tool/corpus/tc_gold`, dev 38 / held-out 16.
Bài 17 gold rates are over its **4 pages / 53 learning blocks** (`tool/corpus/tc_gold_bai17`); the Bài 17 *TSL* stratum of the
false-trust audit is a different denominator — **60 TRUSTED blocks of `tc2-p1`** — and is labelled as such. Audit rates are
`k / n` over the 484-row sample of seed 20260905 (attachment: 396 judged activities). LS&ĐL 5 figures are over that one book
(123 pages / 23 TSL lessons / 390 picture regions). Caption and crop rates are over picture regions and crop regions, not blocks.
Nothing here is divided by 3,679 or 3,381, and no rate on this page is a coverage claim.

---

## 13. Independent correctness review of this branch — findings, fixes, re-measurement

An independent correctness review of the branch diff (posted in full as a comment on PR #77) reported
**14 findings**; Lane D's measured re-run of legacy batch 1 added a fifteenth (**R7c**). Every finding was
treated as a claim: reproduced with a failing test first, and only then fixed. This section records what
each one turned out to be and what it moved. **No threshold was lowered and no guard was loosened.**

Evidence (internal, gitignored): `poc-out/round4/pipeline/tc2-p2-review/` — a complete parallel run
(attach · sdm · sdm-gold · lessons · lesson-document · metrics) built with the fixed code, and
`poc-out/round4/pipeline/tc2-p2-before/` — the same 1 361 pages built from commit `cb60cde`, so every
number below is a before/after on identical input. `tc2-p1` and `tc2-p2` were never written to.

### 13.1 Headline numbers, restated

| measure (54 gold pages · 643 learning blocks) | branch (§0) | after the review fixes |
|---|---|---|
| trusted blocks (coverage) | 354 (0.551) | **354 (0.551)** |
| TLSR | 0.510 | **0.510** |
| false-trusted blocks · FTR | 26 · 0.0734 | **26 · 0.0734** |
| safe rejections | 273 | **273** |
| CTE (pages) | 68 (21) | **68 (21)** |
| trusted blocks whose digits differ from the gold | 6/89 | **6/89** |
| meaning-changing inversions | 33 | **33** |
| QUESTION precision / recall | 0.877 / 0.802 | **0.877 / 0.802** |
| **lesson attachment (header) correct** | 48/54 | **49/54** |
| attachment (TOC range) correct | 38/54 | **38/54** |

Of the **192 numeric aggregate keys** the scorer emits for the gold set, exactly **one** moved:
`attach_header_ok` 48 → 49 (dev 33 → 34). The page fixed is `11-sgk-vat-li-11` p105, which had **no lesson
at all** and is now Bài 24, correct. **Zero pages regressed.**

| other headline | branch | after |
|---|---|---|
| Bài 17 TSL: trusted / withheld | 51 / 13 | **52 / 12** |
| Bài 17 LessonDocument: trusted / withheld / caption blocks | 60 / 13 / 9 | **61 / 12 / 10** |
| Bài 17 gold stratum (4 pages, 53 blocks) | 44 (0.830) · FTR 0.0682 · CTE 4 | **identical** |
| LS&ĐL 5 coverage (whole book, 1512 learning blocks) | 1041 = 0.6885 | **1040 = 0.6878** |
| LS&ĐL 5 headers · chapters · pages with a lesson | 28/28 · 6 · 116 | **28/28 · 6 · 116** |
| chapters over all 525 books with a units TOC | — | **0 books change** |
| `flutter test` | 861 passed, 36 skipped | **861 passed, 36 skipped, exit 0** |

**Effect on Lane C's Golden Slice #2, stated explicitly:** LS&ĐL 5's attachment file is unchanged (same 28
headers, same 116 pages with a lesson, same single back cover), and its chapter list is unchanged (6
«Chủ đề», same titles, same lessonNos). **One** learning block changes: the folk verse on p048 is now
withheld as `line_structure` (§13.4), so whole-book coverage moves 0.6885 → 0.6878.

**What got worse, stated:** six blocks move TRUSTED → WITHHELD across the 1 361 measured pages — five are
line-break-significant text that was being served joined into prose (R7c), one is an SGV «(B)» fragment
that was a `heading` and is now `teacher_text`. Eleven move the other way (F3). The Bài 17 tutor script is
still absent for the same single reason as before (`p063:005`, `agree_order`); nothing here changes that.

### 13.2 P0 — wrong data delivered or silently lost

| # | verdict | mechanism → fix | measured |
|---|---|---|---|
| **F13** | REPRODUCED + FIXED | `back_cover` set `ended = True` for the rest of the book, so ONE false positive deleted the tail. Three of the seven marks are ordinary content («Giá:», «Website:», «HUÂN CHƯƠNG»). Marks split into strong/weak (a cover needs ≥ 1 strong AND ≥ 2 total); the cover verdict runs LAST, after front/back/TOC classification and header detection; **ending a book is now reversible** — a page printing a plausible lesson banner re-opens it (`resumed_after_end`) | 42 books / 6 573 pages: **page kinds unchanged everywhere**, 42/42 back covers kept (the 7 SGV covers print «BỘ SÁCH GIÁO VIÊN», now a strong mark), no page classified a cover carries a header, **0 resumes fire** — the guarantee is that one page can no longer delete a tail |
| **F14** | REPRODUCED + FIXED | the «never skips more than 4 lessons» bound was applied to `max(due)`, so a legitimate `current+1` beside a far outlier vetoed the whole fallback and the page silently kept the wrong lesson. It is now a clamp on the candidates | see the row below — this fix could not land alone |
| **(found while fixing F14)** | NEW | on **every** page where the clamp changed the verdict the OCR footer digit was a misread (104 on a 123-page book; 210; 303; 132), which makes every remaining TOC start «already due». A footer digit that disagrees with the book's own measured printed offset by more than a page is refused in favour of `pdf − offset` | **157 / 6 573 = 0.024** of pages carried such a digit. Without this, F14's clamp jumped LS&ĐL 5 four lessons forward and then rejected two real printed headers. With it: **83 pages change**, all improvements — Vật lí 11 pages-with-a-lesson **31 → 100** and headers **8 → 26** (headers after a theme opener are accepted again once `printed` is trustworthy), Tin học 6 11 pages off a single +7 jump onto Bài 11/12/13, TN&XH 1 3 pages. Gold attachment **48/54 → 49/54**, zero regressions |
| **F7** | REPRODUCED + FIXED | `CHAPTER_HDR`'s numeral group had no trailing boundary: «PHẦN VĂN HỌC» → «Phần V» + «ĂN HỌC», «CHƯƠNG VIỆT NAM …» → «Chương VI», «HUÂN CHƯƠNG I» matched. Boundary required; the medal phrase excluded by name | real-corpus evidence: Khoa học 5's TOC prints «… THÀNH PHẦN VÀ VAI TRÒ …» and the old pattern read «PHẦN V» out of it. **0 of 525 books' chapter lists change** — the downstream `Bài N.` requirement was already suppressing the phantoms |
| **F8** | REPRODUCED + FIXED | `clean_toc_title` let the separator run be EMPTY, so it ate the tail of a longer digit run: «… TỪ 1858 ĐẾN NĂM 1945» → «… ĐẾN NĂM 1». The separator is now required | **0** chapter titles in the corpus currently end in a year before a `Bài N.`, so nothing moves today. A latent child-facing wrong title removed |
| **F2** | REPRODUCED + FIXED | the `attribution` role was unreachable for UPPERCASE — the two `upper_ratio >= 0.7` heading rules run earlier — and `heading` is COLOUR_HEAVY_EXEMPT and becomes the `heading_path` of every following block. The test moved before them; a `caption`-labelled line, a line ending in «?» and SGV prose are all left alone; and a line that opens with a bracket is never a section heading | 1 361 pages: **3 role changes**, all OCR fragments opening with a bracket that were poisoning `heading_path`; 1 trust change (an SGV «(B)» now correctly withheld). The 54 gold pages carry no uppercase attribution — which is why the branch's own numbers did not catch this |

### 13.3 P1 — recall lost, or a guard reason that no longer applies

Denominator for this table: **1 361 pages · 21 books · 34 822 blocks · 5 002 picture regions** — every page
whose raw candidates already exist, rebuilt from `cb60cde` and from the fixed tree into two separate roots.

| # | verdict | measured |
|---|---|---|
| **F1** | REPRODUCED + FIXED | the three branches tested different measurements, leaving a dead zone where a caption straddles the picture's edge (centre 0.545 → `None` while 0.540 and 0.550 linked). The side is now decided by the centre and the gap floored at 0. **Figures with a caption 1 362 → 1 380** (0.2723 → 0.2759); 6 change which caption. No distance limit relaxed |
| **F3** | REPRODUCED + FIXED | the re-derivation recomputed only 3 of the 11 role-dependent guards. One authority now (`role_guards`), used by `build_page` and by `rederive_trust`. **11 blocks WITHHELD → TRUSTED**, every one a figure caption still citing `page_feature:diagram` after promotion («Sơ đồ lò nung vôi», «Cách gấp giấy lọc», «Hiện tượng nhật thực» …); `page_feature:diagram` withholds 324 → 301. **Deliberately not re-derived:** `agree_order` is waived for FLEX_ROLES in the first pass only — re-deriving it here would ADD trust to promoted blocks, so it stays fail-closed. Recorded, not quietly changed |
| **F5** | REPRODUCED + FIXED | `num_directive` tested `ENUM.match` on the un-stripped text while `core` was dash-stripped. The bullet is now stepped over only when an enumerator follows it, so a bare dash line still needs a question lead and dialogue in a reading is untouched. **Exposure 0**: 0 of 29 505 measurable text blocks carry the shape — it lives in primary Toán/Tiếng Việt, of which only 96 pages have raw candidates |
| **F4** | REPRODUCED IN PART + FIXED | «Đọc bảng chia 3 …» — an arithmetic table a child recites — matched the look-verb clause; excluded by naming the idiom (`bảng chia/nhân/cộng/trừ`), not by weakening the clause. **NOT reproduced as a defect:** «Xem bảng bên dưới» — there IS a table below it, so that match is correct and was left alone. **Exposure 0** in the measurable corpus |
| **F10** | REPRODUCED + FIXED | `caption_of` is keyed by caption id, so the LAST figure overwrote the first. Every ImageBlock already carries its own `captionBlockId`, so the figure→caption direction was never lost; `captionOf` is a single id in `lib/core/lesson_model` (not this lane's to change), so it now names the FIRST figure deterministically, and a figure the document DROPS never wins over one it keeps |

### 13.4 R7c — verse served as prose (Lane D, measured)

The block-level colour fix (§8 request 3) serves four previously colour-vetoed regions again, and one of
them is a poem: a block's text is ONE string, so its verse lines arrive joined —
«Trên sông Đà Một đêm trăng chơi vơi Tôi đã nghe tiếng ba-la-lai-ca như thế …». Reproduced directly on
Lane D's own SDM for TV5 tập một Bài 25.

Preserving line breaks would change the LessonBlock shape, which belongs to `lib/core/lesson_model` and to
Lane B, so the rule is the one used everywhere else here: **fail closed**. `tc2_sdm.verse_layout()` is
deterministic geometry plus the printed convention — ≥ 3 OCR lines, ≥ 0.8 of them starting with a capital,
the longest line ≤ 0.95 of the page's own text-column width, ≤ 1/3 of the non-final lines ending in
sentence punctuation — and a block it recognises is **withheld with reason `line_structure`, never
reflowed and never repaired.** The withheld region still carries its crop, so the printed verse survives
as an image instead of arriving as mangled prose. Roles whose line breaks are typography (heading, stage
label, running head, page number, figure text, table) are exempt; unknown page geometry fails OPEN.

| | measured |
|---|---|
| blocks the guard fires on (1 361 pages, 14 546 non-typographic text blocks) | **25 = 0.0017** |
| …that were already withheld for another reason | 20 |
| …that move **TRUSTED → WITHHELD** | **5**, every one genuinely line-break-significant: LS&ĐL 5 p048 (a folk verse), TV5 p065 («Mầm non») and p123 («Tiếng đàn ba-la-lai-ca»), KHTN 9 p089 ×2 (a two-column comparison, nonsense once joined) |
| prose blocks withheld anywhere in the set | **0** |
| on Lane D's own Bài 25 pages | 7 blocks now carry `line_structure`, **2 of them were TRUSTED and served as joined prose** — exactly the two they reported |
| 54 gold pages | unchanged in every figure |

The 0.85–0.97 width band was inspected **before** the threshold was set: over the whole measurable corpus
it holds exactly two blocks, both genuinely line-structured. The threshold follows that measurement, and
it moves coverage down, never up.

**Residual, stated:** one stanza of that poem (p123 block 016, «Cả công trường say ngủ cạnh dòng sông …»)
has a longest line that reaches the full column width, so a width test cannot see it, and it is still
served joined. Catching it needs a signal this lane does not have. Not tuned away — reported.

**On Lane D's «12 of 30 reviewed withheld regions were clean text refused wrongly»:** nothing here loosens
a guard to answer that. Two of the review's findings (F1, F3) give trust back where the *mechanism* was
wrong — 11 captions un-withheld, 18 figures newly captioned — and R7c withholds 5 more where the delivered
text was wrong. Over-withholding is measured against a mechanism, never against a target.

### 13.5 P2 — comment / spec mismatches and dead code

**F9** the chapter tone class did not match its own comment (`Ề` twice, four of six Ê-family forms missing,
`Ù` missing from `CH`); it is now literally the lesson banner's class — **5 real «CHỦ ĐỂ N» banners in 3
books are now read**, markers matched over the corpus 275 → 279, chapter lists unchanged. · **F12**
`_systematic_toc_offset`'s docstring said «Median»; the code takes the mode and the `min_share` gate only
makes sense for a mode — the comment was wrong, not the code. · **F6** `rank_of_native` / `p_rank` were
assigned and never read: **removed**, and the re-sequenced figure ordering they hinted at is **not** wired
— figures are placed by geometry (bbox centre y), which is what §7.1 measured. · **F11** `render_crops`
built its neighbour set from blocks + withheld only, so two adjacent figure crops could still bleed by the
full pad: **fixed** — `crop_neighbours()` includes figures, which can only reduce a crop's padding. ·
**Doc strings** `build_lesson_index.py` (×4) and `lesson_attach.py` (×2) still said `capped-toc-v1`. ·
**Import-time freeze** `lesson_attach.TC2_ATTACH_DIR` was frozen into default argument values at `def`
time; `tc2_attach_dir()` now reads it at call time, so `WAL_TC2_ATTACH_DIR` works without
`importlib.reload`.

**Found, NOT fixed — outside this lane's ownership:** `tool/ui/pack_provenance.py` hard-codes
`ATTACHMENT_RULE = 'capped-toc-v1'` and its verifier rejects any pack stamped otherwise, so **every pack
built today records the wrong attachment rule in its provenance**, and `test_pack_provenance.py` pins it
there. Reported for whoever owns the pack builder.

### 13.6 Tests

`tool/tests/test_round4_correctness_review.py` (new, one class per finding: F7, F9, F8, F2, F1, F5, F4,
F3, F10, R7c, F11, the import-time freeze and the rule id) and `tool/tests/test_tc2_attach.py` (F13, F14 —
beside the cover rule they are about, including a whole synthetic book run end to end through
`attach_book`). **188 tests, green**; 54 of them are new and every one failed before its fix.
