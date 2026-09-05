# VIETNAMESE REPAIR — precision, recall, false correction, and the DATA ACCURACY SCOREBOARD

Round 5 · Lane A1 · 2026-09-06 · **MEASUREMENT. Nothing merged. No production trust threshold. No guard
loosened.** Denominators are stated on every number and never summed (D5).

Sets used, and what each is for:

| set | size | role |
|---|---|---|
| gold **dev** | 38 pages · 462 learning blocks · 365 with human-verified text | every threshold was calibrated here |
| gold **held-out** | 16 pages · 181 blocks · 164 with text | **blind**: informed one rule, disclosed in §5 |
| gold **all** | 54 pages · 643 blocks · **529 with text** | the scoreboard |
| **Bài 17** | KHTN 6, PDF 61–64 · 64 learning blocks | §6, the tc2-p3 candidate |
| Founder **97-row audit** | 97 rows | **evaluation set, never a tuning set** — §7 |

---

## 1. The four variants measured

| pipeline | what it is |
|---|---|
| `tc2-p2` | round 4, as accepted. The baseline every number is compared against |
| `tc2-p3-base` | + `chem_guard` precision fix only (§4) |
| `tc2-p3-nogroup` | + Vietnamese repair/validate/restore |
| **`tc2-p3`** | + the structural-group rule (Founder defect 8) |
| **`tc2-p3-lin`** | + `column-linearisation-v1` (Lane C's technique, generalised) — **the strongest variant** |

Everything is under the gitignored `poc-out/round5/pipeline/<name>/`; `tc2-p2` was never written to.

## 2. DATA ACCURACY SCOREBOARD — the scorer, 54 gold pages / 643 learning blocks

`tool/corpus/tc2_score.py`, unchanged, same gold, same errata.

| measure | **tc2-p2** | tc2-p3-base | tc2-p3-nogroup | tc2-p3 | **tc2-p3-lin** |
|---|---|---|---|---|---|
| trusted blocks (**coverage**) | 354 (0.551) | 356 (0.554) | 359 (0.558) | 352 (0.547) | **371 (0.577)** |
| TLSR | 0.510 | 0.513 | 0.516 | 0.507 | **0.537** |
| **false trusted** | **26** | 26 | 27 | 26 | **26** |
| **FTR** | 0.0734 | 0.0730 | 0.0752 | 0.0739 | **0.0701** |
| safe rejections | 273 | 271 | 268 | 275 | 256 |
| **teaching-critical (CTE)** | 68 | 68 | 68 | 68 | **68** |
| meaning-changing inversions | 33 | 33 | 33 | 33 | 33 |
| **mutilated structures served** | **7** | 7 | 7 | **0** | **0** |
| display fidelity / text acc / CER-no-tone | 1.000 / 0.970 / 0.026 | = | = | = | = |
| reading order | 0.988 | = | = | = | = |
| attachment (header / TOC) | 48/54 · 38/54 | = | = | = | = |
| formula/number/unit — trusted digit blocks wrong | 6/89 | 6/89 | 6/91 | 6/91 | 6/97 |
| role — QUESTION P/R | 0.877 / 0.802 | = | = | = | = |
| trusted-QUESTION precision | 0.903 | 0.903 | — | — | 0.903 |

**`tc2-p3-lin` moves coverage 0.551 → 0.577 while false trust stays at 26 and FTR *falls* 0.0734 → 0.0701.**
That is the round's target shape — coverage recovering without trading accuracy — and it is the first time
in two rounds that coverage has moved up rather than down.

### Block-level, against the human-verified gold text (529 blocks with text)

| | **before (tc2-p2)** | tc2-p3 | **tc2-p3-lin** |
|---|---|---|---|
| served | 339 | 335 | **353** |
| **correct served** | 264 | 267 | **282** (+18) |
| **wrong served** | **41** | **37** | **40** (−1) |
| served, not judgeable | 34 | 31 | 31 |
| withheld | 190 | 194 | 176 |
| …withheld **by permission** (SGV teacher text, answer leak, figure-dependent, page feature) | 48 | 48 | 48 |
| …withheld **by a fidelity guard** | 142 | 146 | 128 |
| **false withheld** (fidelity guards only, text is clean) | **81** | 80 | **65** (−16) |
| **restored** | — | 10 | **28** |
| **restore precision** | — | 0.889 (8/9) | **0.852 (23/27)** [0.675, 0.941] |
| newly withheld | — | 14 (5 clean, 5 wrong, 4 unjudgeable) | 14 |

**Fidelity and permission are kept apart** (Lane A3's point, adopted): 48 of the 190 withholds are *faithful
but forbidden* — SGV teacher text a child may not read. Counting those as «false withheld» would inflate the
pool by 39 blocks and misdirect the work. The `false_withheld` row above excludes them; the run reports both.

### The five directions the Founder asked for, `tc2-p2 → tc2-p3-lin`

| direction | before | after | |
|---|---|---|---|
| FALSE TRUST ↓ | 26 (FTR 0.0734) | 26 (**FTR 0.0701**) | count flat, rate down |
| TEACHING-CRITICAL ↓ | 68 CTE + **7 mutilated structures** | 68 CTE + **0 mutilated** | ✅ on the class the scorer cannot see |
| CORRECT SERVED ↑ | 264 | **282** | ✅ +18 |
| OVER-WITHHOLD ↓ | 81 | **65** | ✅ −16 |
| RESTORE PRECISION ↑ | — | **0.852** | 23 of 27 judgeable restores are verbatim-clean |

## 3. Vietnamese repair — precision, recall, and false correction

Token-level, against the gold text. Definitions are fixed once in `tool/corpus/repair/measure.py`:
*in-scope error* = an aligned token whose gold and observed readings differ only in diacritics or one vowel
quality; *repair precision* = changed tokens now equal to gold / all changed; **false-correction rate** =
changed tokens that were **already correct** and are now wrong / all changed. Tone *placement*
(hoá/hóa, thuỷ/thủy) is normalised on both sides, as `tc_score` does.

| | dev (38 pages) | **held-out (16 pages)** | all (54) |
|---|---|---|---|
| in-scope errors present | 121 | 31 | 152 |
| tokens changed | 5 | 1 | 6 |
| repaired to the gold form | 5 | 1 | 6 |
| **repair precision** | **1.000** | **1.000** | **1.000** |
| **false corrections** | **0** | **0** | **0** |
| **false-correction rate** | **0.000** | **0.000** | **0.000** |
| changed wrong→differently wrong | 0 | 0 | 0 |
| **detection recall** | 0.041 | 0.032 | **0.040** |

**The honest reading.** Precision is perfect and the false-correction rate is zero — the number the Founder
said matters most — and **recall is very low: 6 of 152 in-scope errors**. This lane repairs the errors it can
*prove*, and proves very few. It is not a spell-checker and it must not become one; every 1 % of recall
bought by lowering the bar would be bought with false corrections, which is the failure mode the round
exists to prevent.

### The two sub-classes are different problems, and are reported separately

| sub-class | example | what decides it | outcome |
|---|---|---|---|
| **invalid / unattested syllable** | «thủỷ» (two tone marks — illegal), «cây ỗi» («ỗi» attested on **0** of 62,729 pages) | deterministic: phonotactics, or «the corpus has never seen this» | repaired, `A.vi_syllable` decisive |
| **valid word, wrong word** | «Tiền hành» → «Tiến hành», «bán sắc» → «bản sắc», «Lý Thái Tô» → «Lý Thái Tổ» | context only: collocation + the document | repaired **only when the document agrees** |
| **proper noun** (a sub-case of the above) | «Đăng Khoa», «Bạch Đằng», «Lý Thái Tổ» | corpus frequency is **never** allowed to carry it | repaired only on in-document/in-page/in-block evidence, or when the observed spelling is illegal |
| **the corpus is itself fooled** | «Cộng hoà» → «Cộng hoa» (cộng·hoa **268** pages vs cộng·hoà **303**) | nothing available today | **abstains — reported as a limit, not tuned away** |

Proper-noun repairs on the gold set: **0 of 6 changed tokens**, so the sub-class's false-correction rate is
undefined (0/0) rather than zero — stated plainly rather than reported as a success.

## 4. `chem_guard` — a guard's *precision*, measured and fixed (audit defect 7)

On the 54 gold pages `chem_guard` fired **5 times and was wrong all 5**: «A4» (a paper size), «B1» (a
vitamin), «D0» / «S0» / «NA1» (map labels). Guard precision **0/5**. The audit's «blocks a Physics heading»
is the same shape — a capital next to a digit.

The fix makes the mechanism discriminate; it does **not** switch it off. Three facts about chemical
notation, no thresholds: every letter run must be a real **element symbol**; a printed subscript is never 0
or 1; a single-element formula needs a real subscript, anything else needs ≥ 2 element symbols. Measured
effect on the gold set: coverage **354 → 356**, false trusted **26 → 26**, FTR **0.0734 → 0.0730** — two
blocks released, nothing broken. Tests: `tool/tests/test_repair_vi_defects.py::ChemGuardPrecision`.

**A pre-existing gap left as it was, not a regression:** «AgNO,» for «AgNO₃» is not matched by the `CHEM`
pattern at all (the comma branch needs a capital or a percentage after it), and was not matched before this
change either. Widening it would fire on «HN,», «TP,» — reported for A2 rather than guessed at.

## 4b. Audit defect 6 — the imprint page, reproduced at scale and fixed

**Reproduced:** **26 of the 42 attached books** attach their **imprint page** (the colophon — «Chịu trách
nhiệm xuất bản», «Số ĐKXB», «In xong và nộp lưu chiểu», ISBN) to the book's **last lesson**, by
`continuation`. TN&XH 1 p125 → Bài 28, Toán 2 tập hai p141 → Bài 75, KHTN 6 p197 → Bài 55, and 23 more.

**Why round 4's cover fix could not catch it, precisely.** The imprint page *is* in the tail and *does*
carry a strong mark (ISBN) — but only **one**. `COVER_MIN_MARKS = 2` needs a second, and the three weak
marks («Website:», «Giá:», «HUÂN CHƯƠNG») are *back-cover* furniture. An imprint page is not a back cover,
so the rule refused it — correctly, for a cover.

**The fix** is a mark family of its own in the same shape as the cover rule (≥ 2 marks · no lesson banner ·
tail of the book), with the vocabulary an imprint page actually prints. In the first three pages the same
evidence yields `front_matter`, which ends nothing — a false positive there would delete the book.

**Measured over all 42 books:** every one of the 42 now detects its imprint page (30 that previously carried
a lesson, 12 already `back_matter`), and **0 other pages lost a lesson**. Tests:
`test_repair_vi_defects.py::ImprintPageIsEndMatter`.

**A separate finding, reported rather than acted on.** Re-running `tc2_attach` over the 42 books reproduces
the stored `tc2-p2/attach/*.json` on every page *except* 83, **with the imprint rule switched off** — the
stored attach files were written by an earlier state of `tc2_attach.py` than the code round 4 finished with
(Tin học 6 p051–057 read Bài 11–12 rather than Bài 14; TN&XH 1 p055 reads Bài 13 rather than 12). So the
shipped attach verdicts are **stale relative to their own code**, exactly as the packs are stale relative to
their provenance rule (round 4 §«a versioning defect»). With a fresh re-attach the gold-set header
attachment moves **48/54 → 49/54**. Every number elsewhere in this document was measured against the
**stored** tc2-p2 attach so the comparison stays like-for-like; re-attaching is a pack-rebuild decision for
the coordinator and Lane D, not a change this lane makes silently.

## 5. What the held-out set changed, disclosed

The held-out split exposed **one** defect and it was fixed: a *local* signal (the page's own spelling) was
allowed to overrule positive corpus evidence for the observed reading, and rewrote **«Đề xuất» → «để xuất»**
because that page happened to print «để» elsewhere, while the corpus had «đề xuất» on 1,270 pages. The rule
added is general — *a local signal may break a tie the corpus could not, but may never overrule the corpus
speaking **for** what the page actually printed* — and it is a `_place`-keyed candidate-identity fix, not a
string fix.

Held-out numbers **before** that fix: repair precision 0.667, false-correction rate 0.333 (n=3), restore
precision 0.875. **After**: 1.000 / 0.000 / 1.000. Both are reported; the held-out split is no longer fully
blind for that one rule, and it stayed blind for every threshold.

## 6. The tc2-p3 candidate on Bài 17 (§10)

| | trusted | withheld | withhold reasons |
|---|---|---|---|
| `tc2-p2` | 51 | 13 | `agree_tones` 8 · `page_feature:diagram` 3 · `agree_order` 1 · `math_guard` 1 |
| `tc2-p3-base` (guard fix) | 52 | 12 | `agree_tones` 8 · diagram 2 · order 1 · math 1 |
| **`tc2-p3-nogroup`** | **54** | **10** | `agree_tones` **6** · diagram 2 · order 1 · math 1 |
| `tc2-p3` / `tc2-p3-lin` | 51 | 13 | `agree_tones` 6 · diagram 2 · **`group_incomplete:procedure_steps` 3** · order 1 · math 1 |

**Verdict: the §10 target — accuracy ≥ p2 and coverage > p2 without loosening a guard — is met by
`tc2-p3-nogroup` (54 > 51, two blocks repaired and restored, zero guards changed).**

Two blocks were restored: `p063:003` («làm **thể** nào» → «làm **thế** nào», a real text repair, layers
A+B+D) and `p064:008` (arbitrated in favour of the primary, no text change). Both were withheld by
`agree_tones` in p2.

**And the group rule takes it back to 51, for a reason worth reading.** Enforcing «serve the whole group or
none of it» reveals that Bài 17's «Lọc nước từ hỗn hợp nước lẫn đất» procedure was **already mutilated in
tc2-p2**: the lead block `p062:012` («Chuẩn bị: … cốc thủỷ tinh, … phẫu lọc … Tiền hành:») is withheld while
its three steps are served. A child was being shown three steps of a procedure with its materials list and
its «Tiến hành:» heading missing. Round 4 recorded that the *process diagram* disappeared; it did not record
that what remained was being served incomplete. tc2-p3 withholds the whole procedure instead.

So on Bài 17 the choice is explicit: **54 blocks with one mutilated procedure, or 51 blocks with none.**
That is a Founder decision, not this lane's.

Residual on Bài 17, unrepaired and named: `p062:012` still carries «thủỷ», «phẫu» and «Tiền hành» — the
block has three issues at once and the fail-closed rule («repair a block only if *every* issue in it
resolves») keeps it withheld. It is row 1 of the human queue.

## 7. Against the Founder's 97-row audit (evaluation set — measured, not tuned)

| # | defect | status |
|---|---|---|
| 2 | «Lý Thái Tổ → Lý Thái Tô» | **repairable** — collocation thái·tổ 53 pages vs thái·tô 0; as a **proper noun** it also requires the book to print «Thái Tổ», which a Lịch sử volume does. Regression test present |
| 3 | «bản sắc → bán sắc» | **repairable** — bản·sắc 301 pages vs bán·sắc 0, plus in-document evidence. Regression test present |
| 4 | «Cộng hoà → Cộng hoa» | **NOT repairable by layer A, and the repairer abstains** — the corpus carries the same slip (268 vs 303). Asserted as a test, so a future change that «fixes» it by lowering the bar fails loudly |
| 5 | «cây ổi → cây ỗi» | **repairable** — «ỗi» is attested on 0 of 62,729 pages; an unattested reading is treated like an illegal one |
| 6 | imprint / back matter → lesson heading | **DONE** — §4b |
| 7 | `chem_guard` blocks a Physics heading | **DONE** — §4, guard precision 0/5 → the five gold-set false positives all cleared |
| 8 | incomplete multiple choice because a sibling was withheld | **DONE** — §8 |

Every one of 2–5, 7 and 8 is a regression test in `tool/tests/test_repair_vi_defects.py` (25 tests). None of
the rules was written against these strings: each is stated generally and each was re-measured on the 16-page
held-out split (§3).

## 8. Defect 8 — «withholding is not always safe», measured

The group is now the unit of disposition (`tool/corpus/repair/groups.py`): OPTION ⊂ QUESTION, a caption
bound to its figure, consecutive table rows, an enumerated procedure under an INSTRUCTION lead.

**On the 54 gold pages, tc2-p2 serves 7 mutilated structures** — 5 questions served with an option missing
(TV4 p028 ×2, KHTN 7 p032, Tin học 9 p020 ×2) and 2 procedures missing a step (SGV Toán 4 p054, KHTN 9
p046). Each is a teaching-critical error *produced by the safety mechanism*, and the current scorer cannot
see any of them. `tc2-p3` serves **0**, at a cost of **20 blocks withheld by the group rule**.

## 9. What got worse — stated

1. **`tc2-p3-nogroup` adds one false-trusted block** (26 → 27) on `09-sgk-toan-9-tap-mot` p029: the repair
   «CHỮA» → «CHỨA» is *correct*, but restoring a correct block onto a page whose reading order is already
   wrong (8 of that page's 9 trusted blocks are order-class false trusts) creates one more inverted pair.
   Repairing text does not repair order. `tc2-p3` and `tc2-p3-lin` do not have this because the group rule
   withholds it. No guard exists that would have caught it — the page's `agree_order` count is **0**.
2. **Coverage falls on Bài 17 with the group rule** (51 vs 54) — §6, and it is the correct outcome.
3. **`tc2-p3` withholds 5 clean blocks it should not have** (of 14 newly withheld, 5 were clean, 5 were
   genuinely wrong, 4 unjudgeable). The agreed-error detector is not free.
4. **Restore precision is 0.852, not 1.000, while repair precision is 1.000.** The four bad restores are
   blocks where the flagged token was repaired *correctly* and the block carried a **second** diacritic
   error the detector never saw. A whole-block lexicon sweep (`A.vi_sweep`) was added to catch exactly this
   and caught none of them on dev — a measured negative result, kept because it costs nothing.
5. **Detection recall is 0.040.** 146 of 152 in-scope errors are still there, withheld or served.
6. **`column-linearisation-v1` is off by default.** With it, coverage 0.577 and FTR 0.0701 — better on both.
   Without it, 0.547 / 0.0739. It restores blocks on the strength of *the two stacks agreeing*, and §0 of
   `THIRD-SIGNAL-LAYER.md` says what that agreement is worth. It is enabled by `--linearisation`, measured
   above, and the choice is the Founder's.

## 10. Reproducing every number

```
python3 tool/corpus/repair/vi/lexicon_build.py --out poc-out/round5/lexicon          # ~6 min, 62,729 pages
python3 tool/corpus/tc2_sdm.py --gold --pipeline tc2-p2 --out poc-out/round5/pipeline/tc2-p3-base --force
python3 tool/corpus/repair/run_gold.py --split dev|heldout|all [--no-group-rule] [--linearisation] \
        --baseline-out poc-out/round5/pipeline/tc2-p3-base --out poc-out/round5/pipeline/<variant>
python3 tool/corpus/tc2_score.py --pipeline <variant> --out poc-out/round5/pipeline/<variant> --md …
python3 -m unittest discover -s tool/tests -p "test_*.py"        # 279 tests, green
```

Artefacts per variant (gitignored, internal): `repair-ledger.jsonl` (append-only, every step),
`repair-dispositions.jsonl` (block id → disposition, for Lane A3's simulator),
`human-review-queue.jsonl` (layer E), `repair-report.json` (scoreboard, per-signal contribution, token rows,
per-block census), `metrics-gold-scores.{json,md}`, and `sdm/` + `sdm-gold/` with `text_original` preserved
on every block a repair touched.
