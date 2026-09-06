# ACCURACY RECOVERY — multi-signal verification, measured (Lane A4, round 5, 2026-09-06)

**READY FOR FOUNDER REVIEW — nothing merged.** Base `integration/round5-2026-09-06` + Lane A1's
`a1/round5-repair-framework`. Audit: `ACCURACY-RECOVERY-AUDIT.md`. Code: `tool/corpus/verify/**`,
`tool/tests/test_verify_signals.py`. Python suite **321 passed / 8 skipped / 0 failed**.

**Scope claim, stated first because it bounds everything below.** Nothing in this lane is wired to the
product. Lane D verified structurally that nothing outside `tool/corpus/repair/` and `tool/tests/` imports
the repair package, and A4 registers *into* that package. So this lane's result is **signal quality and
escalation rate**, not served accuracy. No coverage number, no false-trust number and no product score
moves because of anything here, and none is claimed.

---

## 0 · Denominators — stated because Lane D's R13 makes them load-bearing

Lane D measured **silent loss**: a block whose role is `empty` reaches neither `blocks` nor `withheld` of
the TSL and carries **no reason code** (27/394 on its evaluation batch, 55/375 on its holdout, 32/51 on
Toán 4 tập hai Bài 61 — and the lost blocks are the printed arithmetic). Any recall computed over the TSL
is blind to those, and no over-withhold review can ever see them.

**A4's denominators are not the TSL.** They are:

| set | what a row is | n | truth |
|---|---|---|---|
| **H · injection holdout** | one **raw OCR line** from a held-out book | 480 rows / 6,554 tokens | the uncorrupted line |
| **H-clean** | the same rows, **uncorrupted** | 480 / 6,554 | «propose nothing», for every token |
| **L · Lane C Bài 8** | one **SDM block** (trusted *and* withheld) | 51 blocks / 15 token slips | a human reading the 150-dpi print |
| **R · POC cases** | one constructed or audited row | 6 | the Founder's / the audit's own label |
| **S · router set** | one **SDM block** with real role, guards, agreement | 1,200 | — (routing only) |

The router set contains **77 blocks with role `empty` (6.4 %)** — the silent-loss population, still
visible at SDM level. That is the concrete reason A4 measured at OCR-line and SDM level rather than at TSL
level, and it is checkable in `poc-out/round5/verify/matrix-report.json`.

**Index leakage is handled.** The corpus index and every context scan **exclude the 13 evaluated books**
(LS&ĐL 5 + the 12 holdout books), so no book verifies itself: 518 books / 61,075 pages / 93,762 forms,
against the full 531 / 62,729 / 94,787.

**The 97 rows are an evaluation set.** Every named defect is a regression test; nothing was tuned to make
a string pass. Every improvement is reported on the independent holdout *and* on the named cases, side by
side, below.

---

## 1 · Signal × case matrix

`detect` = flagged the defective span · `propose` = offered a replacement · `right` = the replacement is
what the print says · `verify` = an **independent layer** confirmed it (a signal never verifies itself).

### A — `3×10⁸ m/s` → `3×10° m/s` (STEM constant, superscript destroyed)

| signal | detect | propose | right | verify | false-correction risk |
|---|---|---|---|---|---|
| deterministic (`A.enumerator`) | no | no | no | no | none — fires only on a malformed enumerator |
| specialised parser (`C.numeric`, A2) | **YES** | no | no | no | A2 owns the repairer; A4 routes to it |
| Vietnamese lexical (`A.vi_lexicon`, A1) | – | – | – | – | 0.000 measured by A1, but recall 0.040 |
| page furniture | no | no | no | no | – |
| **cross-corpus** | no | no | no | no | correctly silent: not a word-level defect |
| **LLM semantic** | **YES** | **YES** | **YES** → `3×10⁸` | no | high as a proposer (see §3) |
| external authoritative | – | – | – | – | **APPROPRIATE**: a physical constant is a stable public fact |

The Founder's own worked example, reproduced: the model flagged `3×10°` in a Physics context and proposed
`3×10⁸`, with a reason. It is a `CorrectionCandidate`, and no layer confirmed it, so nothing would change.

### B — `Lý Thái Tổ` → `Lý Thái Tô` (proper noun, both variants common)

| signal | detect | propose | right | verify |
|---|---|---|---|---|
| **cross-corpus** | **YES** | **YES** | **YES** → `tổ` | no (layer D may not confirm itself) |
| LLM semantic | no | no | no | no |
| others | no | – | – | – |

Evidence: `thái tổ` **75×** in ≥5 books; `thái tô` **0×** in 61,075 pages. It fires **only** because the
context word is part of the name — see §2.

### C — `bản sắc` → `bán sắc` (common word, meaning inverted) — the hard one

| signal | detect | propose | right | verify |
|---|---|---|---|---|
| **cross-corpus** | **YES** | **YES** | **YES** → `bản` | no |
| **LLM semantic** | **YES** | **YES** | **YES** → `bản sắc` | no |
| others | no | – | – | – |

Two independent signals, from two different layers, reached the same answer for different reasons — which
is exactly the configuration in which A1's engine *would* validate. `bán` is a perfectly good word (to
sell) and no lexicon can decide; the context can.

### D — `Cộng hoà` → `Cộng hoa` — **every signal correctly ABSTAINS**

| signal | detect | propose | right |
|---|---|---|---|
| cross-corpus | **no — and this is the correct behaviour** | no | – |
| LLM semantic | no | no | – |
| external | – | – | **APPROPRIATE**: an official state name is a stable public fact |

**Measured reason, and it is the most important number in this document:** the corpus writes `cộng hoa`
**358×** across **≥5 books** and `cộng hòa` **745×**. The erroneous form is *systematically present in our
own corpus*. A majority rule would have proposed the right answer here **by luck**, at a 2:1 ratio that is
no evidence at all; the strict rule requires the observed form to be unattested and so abstains.

Lane A1 independently measured the same thing from the other side (268 vs 303 **pages**) and asserts the
same abstention as a test. Two lanes, two methods, one conclusion: **frequency is evidence about the
corpus, not about the truth.** Asserted here as `MeasuredAbstentionTests`.

The same mechanism explains a *miss*: Lane C's «Bạch Đăng» for printed «Bạch Đằng» is attested **28×**
against the correct form's 162×, so cross-corpus abstains there too. Systematic OCR errors are exactly
where cross-corpus consistency fails, and that failure mode is now measured rather than assumed.

### E — `cây ổi` → `cây ỗi` (valid-looking syllable, in fact a non-word)

| signal | detect | propose | right | verify |
|---|---|---|---|---|
| **cross-corpus** (recall policy) | **YES** | **YES** | **YES** → `ổi` | no |
| cross-corpus (strict/default) | **YES** | no — anomaly only | – | – |
| LLM semantic | no | no | – | – |

`ỗi` occurs **0 times in 62,729 pages**; `cây ổi` occurs 42× in ≥2 books. At the strict setting the
evidence clears the detection bar but not the proposal bar, so the output is an `AnomalySignal` →
`SUSPECT`. That is the intended shape: **detected, not guessed.**

### F — `II – Định luật khúc xạ ánh sáng` → `I1 - … , Ô C S ỐNG` (real audit row, KHTN 9 p27)

| signal | detect | propose | right | verify |
|---|---|---|---|---|
| **deterministic `A.enumerator`** | **YES** | **YES** | **YES** → `II` | **YES** (layer D) |
| **page furniture `B.page_furniture`** | **YES** | **YES** | **YES** → removes `Ô C S ỐNG` | **YES** |
| specialised parser (A2) | YES | no | no | no |
| cross-corpus | no | no | no | no |
| LLM semantic | no | no | no | no |
| external | – | – | – | **NOT APPROPRIATE** — source-bound |

**The only case in the set that a signal both proposes and independently verifies**, and it is the case
where no model was involved. `I1` is neither a Roman numeral nor a number (layer A, no corpus needed), and
the book itself prints `II` as a section enumerator **51×** (layer D). Both defects sit at the two edges of
one bounding box, and **agreement is useless on both** — the round's thesis, as a row.

---

## 2 · Cross-corpus — the numbers, three policies, never one tuned point

Index: 518 books / 61,075 pages / 93,762 forms (the 13 evaluated books excluded).

| policy | set | rows | tok | slips | prop | detect recall | corr. precision | corr. recall | **FCR** | prop/1k tok |
|---|---|---|---|---|---|---|---|---|---|---|
| **strict** | H-inj | 480 | 6,554 | 480 | 192 | 0.500 | **0.938** | 0.375 | **0.063** | 29.3 |
| | **H-clean** | 480 | 6,554 | 0 | **6** | – | – | – | – | **0.92** |
| | L-lanec | 51 | 1,209 | 14 | 4 | 0.071 | 0.250 | 0.071 | 0.750 | 3.3 |
| **default** | H-inj | 480 | 6,554 | 480 | 213 | 0.531 | 0.916 | 0.406 | 0.085 | 32.5 |
| | **H-clean** | 480 | 6,554 | 0 | **12** | – | – | – | – | **1.83** |
| | L-lanec | 51 | 1,209 | 14 | 6 | 0.143 | 0.333 | 0.143 | 0.667 | 5.0 |
| **recall** | H-inj | 480 | 6,554 | 480 | 295 | **0.644** | 0.909 | **0.558** | 0.092 | 45.0 |
| | **H-clean** | 480 | 6,554 | 0 | **19** | – | – | – | – | **2.90** |
| | L-lanec | 51 | 1,209 | 14 | 6 | 0.143 | 0.333 | 0.143 | 0.667 | 5.0 |

**Proper nouns, reported separately as required — false-correction rate 0.000 at every policy**
(6 proposals, 6 correct, 0 false, all three policies). Common words carry the whole error mass:
0.065 / 0.087 / 0.093.

### The three changes that produced those numbers, each from an observed failure

The first version of this signal scored **FCR 0.109** on the injection holdout and **18 proposals on 480
already-correct rows**. Three fixes, each forced by reading the actual false corrections on Lane C's real
blocks, not by tuning:

1. **Context, not token frequency.** The corpus writes `đầu` 30,232× and `đấu` 5,627×, so a majority rule
   rewrites the *correct* «cuộc đấu tranh». The unit of evidence is the n-gram in its context.
2. **Evidence is never read across punctuation**, and the corpus index counts bigrams **across line
   breaks** — because a block joins lines. «đồi mồi,...), phải» had been read as the bigram `mồi phải`,
   which the corpus of course never writes, so the correct «mồi» looked anomalous.
3. **Contradicting evidence vetoes.** «đã phất cờ» and «về hưởng ứng» are rare *left* bigrams and very
   common *right* ones. If any context of the observed token is well attested, the corpus knows this
   phrase and it is not an anomaly. This is the Founder's «store contradicting evidence» doing work rather
   than being a field nobody reads.

Result: clean-text proposals **18 → 6** and injected FCR **0.109 → 0.063**, at a cost of 0.04 detection
recall.

### Proper nouns get name-internal evidence only

Lane C's measured false correction («Đăng Khoa» → «Đặng Khoa») and the Founder's case B («Lý Thái Tô» →
«Lý Thái Tổ») are *both* proper nouns, and one must be corrected while the other must not. What separates
them is **where the evidence comes from**: «Thái —» is part of the name; «Theo —» is a preposition beside
it. So for a proper noun the context word must itself be informatively capitalised, and «(Theo Đăng Khoa,
…)» — block-initial, so its capital means nothing — cannot decide.

The proper-noun prior is measured from the corpus, not asserted, so it works inside an ALL-CAPS heading
where the surface says nothing: `đặng` **0.951** · `hán` **0.928** · `đằng` 0.468 vs `đấu` **0.015** ·
`đầu` **0.021**.

### Where cross-corpus is weak, stated plainly

`L-lanec` FCR 0.667–0.750 on 4–6 proposals. The denominators are tiny, but the direction is real and the
cause is known: Bài 8 is History prose full of rare, poetic and named phrases («người tà gian», «dài tạc
đá», «đã phất cờ»), which is the worst possible ground for a frequency signal. **On real book prose from a
book the index has never seen, cross-corpus proposes ~1–3 changes per 1,000 tokens and is right about
90 % of the time when the text is actually damaged; on a page of rare literary History it is wrong more
often than right.** Both numbers are the signal.

---

## 3 · LLM as a verifier — an excellent detector and a dangerous proposer

`claude -p`, model `haiku`, prompt `a4-verify-v1`, 181 rows, 113 calls + 67 cache hits, 1 error, 7
unparsable answers (counted as failures, never as «no findings»), 6 hallucinated spans dropped.

| set | rows | **detector recall** | rows falsely flagged | **proposer precision** | **proposer FCR** |
|---|---|---|---|---|---|
| H-inj (corrupted) | 60 | **0.717** | 0 / 60 | 0.822 | 0.178 |
| L-lanec (human print truth) | 51 | 0.400 | 6 / 51 (0.118) | 0.556 | 0.444 |
| R-poc (observed) | 5 | 0.400 | 0 | 1.000 | 0.000 |
| R-poc (the **correct** text) | 5 | – | **0** | – | – |
| **H-clean (already correct)** | 60 | – | **16 / 60 = 0.267** | **0.000** | **1.000 (13 proposals)** |

**Read those two bold rows together.** Detection recall **0.717** is the best of any signal in this lane —
better than cross-corpus at its most aggressive (0.644) and 18× A1's Vietnamese repairer (0.040). And on
sixty rows that were **already correct**, it proposed thirteen changes and **every single one was wrong**.

That is the Founder's stated failure mode, measured: *turning «OCR got it wrong» into «AI confidently got
it wrong differently»*. It is also the empirical case for the architecture — the model is worth having,
and it must never be allowed to write.

Encouraging detail: on the five **correct** POC sentences it flagged nothing at all. It is the ordinary
corpus prose, full of OCR noise it cannot distinguish from error, where it over-fires.

---

## 4 · Page furniture — a measured negative, then a working answer

The Founder's KHTN 9 row needed the watermark «KẾT NỐI TRI THỨC / VỚI CUỘC SỐNG» removed. Two approaches
were tried and **both results are reported**:

**Learning it from repetition — NEGATIVE, and kept in the code with its evidence.** The exact learner
finds solid-ink furniture reliably (running heads, «MỤC TIÊU» 50/230, «EM ĐÃ HỌC» 51/230, and in SGV books
the whole lesson-plan scaffold «a) Mục tiêu» / «b) Nội dung» at 229/230). But a faint watermark is read
**differently on every page it survives on**: `I TRI THƯC`, `Ố1 TRI THỨC`, `RI THỨC`, `KẾT NƠI TRỊ THỨC`,
`ỚI CUỘC SỐNG`, `C SỐNG`, `CUỘC SỘ` — each once or twice. No string repeats, so the exact learner returned
**zero fragments for the very book it was written for**. Clustering the rare variants by character
similarity then over-reached: transitively it produced one 2,260-variant «cluster» covering 230/230 pages
containing «MỤC TIÊU» and «Tiến hành:», and even non-transitively the cluster containing `C SỐNG` also
contained «đời sống.» and «VÀ ĐỜI SỐNG». **A learner that would delete «đời sống» from a biology lesson is
not a learner worth having.**

**What works: three strings.** The series slogans are a publisher fact, auditable by eye, needing no
threshold, covering every SGK page in Vietnam — and *validated against the corpus* rather than asserted.
Matched fuzzily against **leading/trailing** fragments only, because a watermark bleeds in at a bbox edge.

**And the guard that makes it safe.** Similarity alone is not enough: «cuộc sống» is an *exact substring*
of the slogan and two of the commonest words in Vietnamese, so a similarity-only rule deletes it out of
«Kể tên các nguồn năng lượng trong cuộc sống». What separates a watermark from prose is **how the ink was
read** — OCR crossing a faint diagonal shatters it into stray single letters. So: at least one one-letter
word, and a digit does not count («Bài 5» is a lesson number). Six negative cases are regression tests.

**The repair is deletion-only.** The words that remain are the observed words, untouched, so this signal
sits outside the false-correction risk the rest of the lane spends its budget bounding: subtracting
furniture cannot invent a wrong word.

---

## 5 · Edge risk — the coordinator's hypothesis, tested, and half of it falsified

*Does distance from the edge of a line predict OCR error?* Proxy for error: «the corpus has never written
this word» — noisy, but unbiased with respect to position, which is all a positional hypothesis needs.
486,325 tokens across the 12 held-out books (which the index excludes, so a token cannot attest itself).

| position | n | unattested rate | vs interior |
|---|---|---|---|
| **last token of a line** | 41,979 | **0.00324** | **3.8×** |
| **first token of a line** | 39,610 | **0.00268** | **3.2×** |
| interior | 406,715 | 0.00085 | 1× |
| last token of a line running into the right margin | 8,243 | **0.00061** | **0.5×** — *falsified* |
| everything else | 480,061 | 0.00121 | 1.4× |

**CONFIRMED:** the ends of a line carry 3–4× the interior error rate. One integer per token, no model, no
corpus lookup at query time — the cheapest usable signal measured in this lane, and it generalises to
every book.

**FALSIFIED:** the refinement that a line *running into the page's right margin* is riskier. It is
**safer** than average (0.00061 vs 0.00121), because those are full-width body lines — the cleanest text
on the page. The risk is positional **within the line**, not positional **on the page**. Worth stating
because the intuition is natural and wrong.

---

## 6 · The router — human review rate **0.0900**

Measured on **1,200 real SDM blocks** with their real roles, guards and agreement:

| set | rows | **human review rate** | LLM consulted | external consulted | cross-corpus consulted | mean cost |
|---|---|---|---|---|---|---|
| **S · SDM (the honest denominator)** | 1,200 | **0.0900** | 0.416 | **0.000** | 0.993 | 58.6 |
| L · Lane C Bài 8 | 51 | 0.0784 | 0.569 | 0.000 | 1.000 | 55.7 |
| H · holdout (clean & injected) | 480 | 0.0000 | 0.015 | 0.000 | 1.000 | 5.5 |

Content types on the SDM set: prose 840 · enumerated heading 147 · proper-noun phrase 89 · **STEM
expression 61** · heading 54 · table 9. Teaching-critical: **351 / 1,200 (0.293)**.

**Reported honestly:** the holdout's 0.0000 measures the *inputs*, not the router — those rows are raw OCR
lines carrying no role and no guard, so nothing can be teaching-critical. That is why the SDM set is the
denominator quoted.

**External is consulted 0.000 of the time**, and that is the router working. The truth a Trusted Corpus
needs is *what the printed page says*, and no external source knows that; `appropriate()` refuses every
source-bound class outright. Reaching outside is defensible for a physical constant or a historical name —
neither of which appears in this sample as a teaching-critical unresolved block.

Two routing rules are used rather than re-derived, both from other lanes' measurements:

* **Prior audit disposition** (Lane D): of the regions it restored, **3 of 4** labelled OVER-withheld came
  back correct and **both** labelled SAFE refusals came back **wrong**. A blind human label predicted the
  restore outcome, so it is a routing input.
* **Silent loss** (Lane D R13): a block with role `empty` and a numeric expression is routed as
  teaching-critical, because that population reaches neither `blocks` nor `withheld` and no over-withhold
  review can ever see it. 77 of the 1,200 router blocks (6.4 %) have role `empty`.

---

## 7 · The correction workflow

```
REPORTED → (triage) → VALIDATING | NEEDS_SOURCE | ACCEPTED | REJECTED
ACCEPTED → RepairCandidate in A1's engine → validated repair → a NEW corpus version
```

`CorrectionRecord` = `{record_id, source_block_id, original, proposed, reason, reporter_type,
source_evidence, evidence[], corpus_version, reported_at, status, validation, reviewer, reviewed_at,
resulting_corpus_version, prior_record_id}`. Append-only; a decision is a **new row** naming the one it
supersedes, so «what did we think on 6 September» stays answerable. `source_block_id` is byte-identical to
the SDM/TSL id (A1 verified 0 mismatches), so a report joins to the pipeline without a mapping table.

**The substantive claim: a report without a reading of the printed page is a DETECTION, not a
correction.** `triage()` returns `NEEDS_SOURCE` for a learner report however confident it is, `VALIDATING`
for a page reading **alone** — because humans are wrong too — and `ACCEPTED` only with an independent
layer. That is the same detector/proposer split the LLM turned out to have, for the same reason.

UX research note in `verify/human.py:UX_NOTE`: one tap on a **block**; span, proposal and photo all
optional; the app says «SAM sẽ kiểm tra lại với sách in» and **never «đã sửa»**; accepted corrections are
attributed to the print, never to the reporter; reports are **deduplicated, never counted as votes** —
frequency is not truth here either.

---

## 8 · Which signal earned its place, and which did not

| signal | verdict |
|---|---|
| **`A.enumerator`** (+ `D.section_sequence`) | **EARNED IT, unreservedly.** The only signal in the set that both proposed and independently verified a repair. No corpus, no model, ~120 lines, zero measured false-correction risk, and it closes half of a real audit row. |
| **`B.page_furniture`** (known-series registry) | **EARNED IT.** Deletion-only, so it cannot invent a wrong word; closes the other half of the same row; three auditable strings. Its *learned* form did **not** earn its place and is reported as a negative. |
| **`D.cross_corpus`** | **EARNED IT, with a stated boundary.** The only signal that catches B and E, and the only one that answers D correctly *for the right reason*. 0.92–2.90 proposals per 1,000 clean tokens, proper-noun FCR 0.000, common-word FCR 0.063–0.092. Weak on rare literary prose and blind to systematic corpus-wide OCR errors — both measured. |
| **`G.llm_semantic`** | **EARNED ITS PLACE AS A DETECTOR ONLY.** Recall 0.717 is the best in the lane; 13/13 wrong proposals on already-correct text is disqualifying for anything else. The router calls it to detect. |
| **`H.external`** | **DID NOT EARN A PLACE IN THIS ROUND'S PIPELINE.** Consulted 0.000 of the time on 1,200 real blocks, and the audit says why: the question a Trusted Corpus asks is source-bound. Kept as a schema and a routing rule, with no network client, because when it *is* appropriate (a constant, a historical name) the evidence discipline has to already exist. |
| **`E.human`** | **STRUCTURALLY NECESSARY, NOT YET MEASURABLE.** Lane C's Bài 8 result already shows a human read deciding both for and against machine corrections in one block. A4 ships the schema and the triage rule; the review-capacity commitment is a Founder decision. |
| **edge position** | **EARNED IT.** 3–4× interior risk, one integer per token, n = 486k. Its page-position refinement is falsified. |
| **`F.third_stack`** | **NOT RE-OPENED.** A1 measured the reasons (both stacks share Apple Vision; local tesseract has no `vie`). A4 accepted that and spent nothing on it. |

### The gap this lane was asked to close

A1's Vietnamese repair: precision 1.000, false-correction 0.000, **detection recall 0.040 (6/152)**. Judged
on *detection recall gained per unit of false-correction risk added*, on the independent holdout:

| signal | detection recall | clean-text proposals per 1,000 tokens |
|---|---|---|
| A1 Vietnamese repair (published) | 0.040 | 0 |
| **cross-corpus, strict** | **0.500** | **0.92** |
| cross-corpus, recall | 0.644 | 2.90 |
| **LLM, as a detector** | **0.717** | flags 26.7 % of clean rows — detection only |

The strict cross-corpus policy is the honest recommendation: **12.5× the detection recall for slightly
under one proposal per thousand clean tokens**, with proper-noun false corrections at zero — and every one
of those proposals still has to clear A1's independent-support rule before anything is repaired.

---

## 9 · What the Founder is asked to decide

1. **Is external verification worth any budget at all?** Measured consult rate 0.000. A4's recommendation:
   keep the schema, spend nothing, revisit only if a STEM-constant or historical-name class becomes a
   measured error mass.
2. **Detection without repair — what happens to a `SUSPECT` block?** The lane can now detect ~12× more
   than it can repair. Those blocks are not served and not repaired. Whether they are withheld, queued for
   human review at 9 % of blocks, or shown with a caution is a product decision, not a pipeline one.
3. **Human review capacity.** A 9 % escalation rate on 1,200 blocks is 108 reviews. At corpus scale that
   is not a queue anyone can staff without a stated budget, and a queue nobody reads is worse than none.
4. **Is the LLM allowed to run offline at all,** given that it is the best detector measured and its
   proposals are never usable? A4 has wired it as detector-only; the standing limit forbids it in the app,
   and nothing here changes that.

## 10 · Reproduce

```
python3 tool/corpus/verify/run_xcorpus.py      # index + context scan + cross-corpus, 3 policies (~5 min)
python3 tool/corpus/verify/run_llm.py --offline  # re-score from the cache; drop --offline to call claude
python3 tool/corpus/verify/run_furniture.py    # furniture learners + the edge-risk table
python3 tool/corpus/verify/run_matrix.py       # the signal × case matrix + router rates
python3 tool/corpus/verify/probe.py "<text>" --pairs "thái tổ" "cộng hòa"
python3 -m unittest discover -s tool/tests -p 'test_*.py'
```

Outputs (gitignored): `poc-out/round5/verify/{xcorpus-index*.json, xcorpus-report.json,
xcorpus-decisions.jsonl, llm-report.json, llm-decisions.jsonl, llm-cache/, furniture-report.json,
matrix-report.json}`. No crop, no TSL and no verbatim SGK text is committed.
