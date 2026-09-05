# Round 4 · Lane D — legacy reprocess, batch 1 report

**Status: measurement. Nothing merged, nothing deployed, nothing promoted to trusted.**
Six legacy lessons were reprocessed from the ORIGINAL SOURCE through the existing TC-v2 pipeline, compared
block by block against what the product used to serve, and independently audited from page renders. This
document reports what was measured. It sets no threshold and issues no PASS/FAIL.

Founder rules this report is written under: legacy content is **never** a trusted teaching source ·
**REPROCESSED ≠ TRUSTED** · nothing is deleted · no manual prettifying of old outputs · no mass reprocess ·
what the pipeline cannot process is **WITHHELD, never guessed** · every number carries its denominator (D5) ·
verbatim SGK stays internal (D4) — this document quotes only fragments needed to name a defect.

Companion documents: [`LEGACY-REPROCESS-SCOREBOARD.md`](LEGACY-REPROCESS-SCOREBOARD.md) (the standing counts)
and [`PIPELINE-REQUESTS-FROM-LEGACY.md`](PIPELINE-REQUESTS-FROM-LEGACY.md) (what batch 1 asks Lane A-pipeline for).

---

## 1. The scoreboard in one line

| in scope | pending | reprocessed | independently audited | trusted | partial | withheld | rejected | **eligible for teaching** |
|---|---|---|---|---|---|---|---|---|
| **243** | 237 | 6 | 6 | **0** | 6 | 0 | 0 | **0** |

243 = the 113 baseline-learnable lessons ∪ every lesson with rows in the grounding store (`sam-units.db`) —
6.6 % of the 3,679 canonical historical lessons, 7.2 % of the 3,381 ranged ones. `trusted` is 0 because no
Founder threshold record exists; the scoreboard computes it from `docs/research/legacy-reprocess/THRESHOLDS.json`
and prints the reason when the file is absent. `eligible for teaching` additionally requires a Founder teaching
authorisation, so it is 0 twice over.

---

## 2. Method

**Reprocess from the original source, never from the old output.** The chain is the existing pipeline, called
as-is (Lane D owns `tool/corpus/legacy/**` and never edits pipeline code):

```
PDF page + Apple-Vision OCR lines
  → tc2_run    (Docling + XY-cut + naive raw candidates)
  → tc2_sdm    (agreement gate · guards · role layer)
  → tc2_attach (header-based lesson identity)
  → tc2_tsl    (Trusted Structured Lesson: trusted blocks + withheld regions)
  → tsl_to_lesson_document (bridge, auditStatus=notAudited, licence=internalResearchOnly)
```

**Containment.** `run_batch.py` points the pipeline at a *shadow* `TC_ROOT` under
`poc-out/round4/legacy/batch-1/tcroot/`, with read-only symlinks to the corpus. Every byte the pipeline writes
lands inside the batch directory; the main `poc-out/` is untouched and the old outputs stay in place. A second
run of the same batch id refuses to overwrite its manifest — a re-run is a new versioned directory.

**Provenance on both sides.** The run manifest records the commands, exit codes, timings, tool versions
(Docling 2.126.0 · ocrmac 1.0.1 · PyMuPDF 1.28.2 · Python 3.11.12 · macOS 26.5), the pipeline code sha, the
Lane D code sha, and the sha256 of all 62 outputs. The compare records, per lesson, the OLD hashes (units file,
`sam-units.db`, pack version + content hash) and the NEW hashes (TSL, LessonDocument, `sourceHash`, pipeline
version).

**Audit is page-render based.** The annotator judges each sampled block from a crop of the printed page with
the block's bbox outlined, not from the served text alone. Withheld regions are reviewed too — the question
there is whether the refusal was a *safe* refusal.

Run result: 37 pages, every step `rc=0`, Docling 37/37 pages, SDM 37/37, no missing raw, 6 LessonDocuments.

---

## 3. Why these six lessons

Chosen by **failure class from the round-3 false-trust audit**, not for convenience — the P0 risk classes the
Founder named, each with a concrete round-3 row behind it.

| lesson | risk classes | why this one |
|---|---|---|
| Toán 4 tập hai **Bài 61** | toan, two-column, formula, order | round-3 rows 0130–0133 were 4/4 teaching-critical: fractions lost, speech bubbles spliced across the column gap |
| Toán 4 tập hai **Bài 73** | + attachment, geometry-rebuilt expression | the fabricated-expression case (an item assembled from two different printed items); an MCQ whose answer flips; **the back cover served as an exercise of Bài 73** |
| Toán 5 tập một **Bài 6** | toan, two-column, formula, geometry-rebuilt expression | an expression served with the wrong operator; derivations and a)–d) items flattened; a role error |
| TV5 tập một **Bài 25** | tv5, two-column, order, attachment | a two-column poem interleaved line by line; a counted key word served with three different tone marks; the TV5 TOC `pageStart` offset |
| TV5 tập hai **Bài 1** | tv5, two-column, attachment, role | a Ghi nhớ definition corrupted into another word; a watermark spliced into a passage; a task served as a comprehension question |
| KHTN 6 **Bài 11** | khtn, two-column, figure/caption, role | figure labels served as experiment steps; also a determinism check, since tc2-p1 already covers these pages |

All six are `in_113`; five are also in the grounding store. Three subjects, three grades, five books.

---

## 4. OLD vs NEW — mechanical compare

Every OLD served block (units + pack activities, linked back to its OCR lines) is aligned **geometrically** to
the NEW output on the same page and classified. This is arithmetic on regions, not a judgement.

**131 OLD served blocks across the six lessons:**

| fate in the new output | blocks |
|---|---|
| now trusted, same text | 36 |
| now trusted, changed text | 8 |
| now withheld (the pipeline refuses the region) | 44 |
| mixed (partly trusted, partly withheld) | 23 |
| absent (not extracted at all) | 20 |
| attached to another lesson | 0 |

By family, the single most important line:

> **`toanExercises`: 16 of 16 → now_withheld.** Every geometry-rebuilt Toán expression — the class where
> round 3 found the product serving arithmetic that *is not on the page* — is refused by the new pipeline
> rather than reconstructed. None of them re-appears verbatim in a trusted block.

New side, same six lessons: **287 trusted blocks, 77 withheld** (learning blocks 364; served share 79 %).
Withhold reasons: text disagreement between extractors, order disagreement, the math guard, low OCR
confidence, page-feature flags (colour-heavy / diagram), figure dependence. Every lesson came out
`sourceability = PARTIAL`; none was FULL, none was NONE.

---

## 5. Independent audit — OLD vs NEW rates per failure class

Samples (seed 20260906, stratified, deterministic): **55 OLD served blocks**, **74 NEW trusted blocks +
30 NEW withheld regions**. Contact sheets at 170 dpi; 159 rows judged. Rate = WRONG / (OK + WRONG) among
**served** rows — the share of what each side actually showed a child that is wrong. `NA`/`UNSURE` excluded and
counted beside. Wilson 95 %. No threshold applied.

| failure class | OLD (units + packs) | NEW (`legacy-b1` TSL) | direction |
|---|---|---|---|
| display fidelity | 39 / 55 = **0.709** [0.579, 0.812] | 15 / 74 = **0.203** [0.127, 0.308] | better |
| teaching-critical | 26 / 36 = **0.722** [0.560, 0.842] | 5 / 24 = **0.208** [0.092, 0.405] | better |
| reading order | 14 / 33 = **0.424** [0.272, 0.592] | 0 / 26 = **0.000** [0.000, 0.129] | better |
| formula / number / unit (tagged) | 22 / 55 = **0.400** [0.281, 0.532] | 7 / 74 = **0.095** [0.047, 0.183] | better |
| role fidelity | 9 / 55 = **0.164** [0.089, 0.283] | 16 / 74 = **0.216** [0.138, 0.323] | **not better** |
| lesson attachment | 2 / 55 = **0.036** [0.010, 0.123] | 8 / 74 = **0.108** [0.056, 0.199] | **worse** |
| figure / caption (tagged) | 2 / 55 = 0.036 [0.010, 0.123] | 1 / 74 = 0.013 [0.002, 0.073] | **n too small to read** |
| false trust (derived, 5 criteria) | 40 / 55 = **0.727** [0.598, 0.827] | 27 / 74 = **0.365** [0.264, 0.479] | better |
| false trust (annotator's own field) | 29 / 55 = 0.527 [0.398, 0.653] | 13 / 74 = 0.176 [0.106, 0.278] | better |

Denominators (D5): the two sides are **different block sets** — 55 OLD served blocks vs 74 NEW served blocks —
so what is comparable is the *share of served units that is wrong*, not a paired difference. Neither number
divides by 3,679 or 3,381; those denominators describe the historical corpus, not this batch.

The 30 NEW withheld regions were all reviewed: each carries a note on whether the refusal was safe. None was
judged a wrong refusal of clean, simple text.

**The two classes that did not improve are the finding, not a footnote.**

- **Attachment (8/8 WRONG rows are one mechanism):** the imprint page and the **back cover** of Toán 4 tập hai
  are attached to Bài 73 — the book's last lesson — and served as trusted `body`/`heading`/`activity`. The old
  pipeline had the *same* defect (round 3 found the back cover served as an exercise of Bài 73); the new
  pipeline did not inherit it from the packs, it re-derived it. A book's non-lesson tail has no header, so a
  header-based attachment with no upper bound hands it to the last lesson.
- **Role:** exercise instructions are served as `body` rather than question/instruction. The signal that marks
  them — the circled exercise numeral — is dropped by OCR (three audited rows say so explicitly), so the role
  layer has nothing to key on.

---

## 6. Second annotation and inter-annotator agreement

The ≥ 10 % blind second annotation was run on the **original round-3 sample** (`annotated-20260905.jsonl`,
sha256 `f11911ab9e81…`, 484 rows). Seed 20260906 — a *different* seed from round 3 — stratified to
over-sample the risky strata the Founder named: Toán · two-column · math rows first.

**58 rows = 12.0 % of the round-3 sample** (12.1 % of its 480 served rows). Annotator #1's verdicts, notes and
error classes were **stripped from the sample file** before annotation; annotator #2 judged from the page
renders only. Strata picked: Toán·two_col·math 12, TV·two_col·text 8, Toán·two_col·text 6, Toán·single·math 6,
TV·single·text 6, Science·two_col·text 4, TSL 4, and 12 more across the smaller strata.

| class | n both judged | agreement | **κ** | #1 WRONG | #2 WRONG | confusion (#1/#2) | NA/UNSURE mismatch |
|---|---|---|---|---|---|---|---|
| display | 58 | 0.948 | **0.877** | 0.690 | 0.707 | OK/OK 16 · OK/WRONG 2 · WRONG/OK 1 · WRONG/WRONG 39 | 0 |
| teaching-critical | 35 | 0.914 | **0.826** | 0.543 | 0.571 | OK/OK 14 · OK/WRONG 2 · WRONG/OK 1 · WRONG/WRONG 18 | 7 |
| reading order | 38 | 0.974 | **0.943** | 0.342 | 0.368 | OK/OK 24 · OK/WRONG 1 · WRONG/WRONG 13 | 6 |
| role | 58 | 0.931 | **0.713** | 0.103 | 0.172 | OK/OK 48 · OK/WRONG 4 · WRONG/WRONG 6 | 0 |
| attachment | 57 | 1.000 | **1.000** | 0.035 | 0.035 | OK/OK 55 · WRONG/WRONG 2 | 0 |
| false trust | 58 | 0.948 | **0.891** | 0.379 | 0.397 | OK/OK 34 · OK/WRONG 2 · WRONG/OK 1 · WRONG/WRONG 21 | 0 |

κ is computed only on rows both annotators judged OK/WRONG; NA/UNSURE mismatches are counted separately and
never folded into agreement.

**How to read this.** The round-3 rates survive an independent second reading: on every class the two
annotators' WRONG rates differ by ≤ 0.07, and κ ≥ 0.71 everywhere, ≥ 0.83 on the classes that carry the
headline claims. The weakest class is **role (κ 0.713)** — annotator #2 called four rows WRONG that annotator
#1 called OK, and none the other way, i.e. #2 is *stricter* about role. That asymmetry means role rates should
be read as annotator-dependent, and it is exactly the class where the OLD vs NEW comparison above says the new
pipeline is not better. **Teaching-critical carries 7 NA/UNSURE mismatches on 35 judged rows** — the two
annotators disagree about *when the class applies* more often than about the verdict, which is a definition
gap in the protocol, not noise.

**What this second annotation does not establish:** it validates the round-3 sample, not batch 1. The batch-1
OLD/NEW rows in §5 were judged by a single annotator (the same one, as annotator #2). The Lane D successor
independently re-checked 8 of those rows against their page renders and agreed with all 8 — that is a
spot-check, not a second annotation. A blind second annotation of the batch-1 rows is listed as remaining work.

---

## 7. Re-run on Lane A-pipeline's improved build (`tc2-p2`) — preview

Batch 1 was re-run on the same spec and the same original source against Lane A-pipeline's branch
(`origin/lane-a/round4-pipeline-failure-classes` @ `206a103`), exported as a tree and **called, not edited**
(`run_batch.py --corpus … --corpus-ref …`; the manifest records both). That commit is an **unreviewed WIP
snapshot**, and Lane A's PR was not open at the time — so this is a *preview*, to be repeated on their merged
build. Every step ran `rc=0`; re-running the cheap steps a second time reproduced identical outputs
(determinism check).

**Coverage — the price paid:**

| lesson | trusted (p1 → p2) | withheld (p1 → p2) | served share | new withhold reasons |
|---|---|---|---|---|
| Toán 4 Bài 61 | 9 → 4 | 10 → 15 | 47 % → 21 % | `agree_numbers` |
| Toán 4 Bài 73 | 67 → 39 | 16 → 25 | 81 % → 61 % | `agree_numbers`, `agree_tones` |
| Toán 5 Bài 6 | 14 → 12 | 11 → 13 | 56 % → 48 % | `agree_numbers`, `agree_tones` |
| TV5-1 Bài 25 | 62 → 55 | 23 → 30 | 73 % → 65 % | `agree_tones` |
| TV5-2 Bài 1 | 50 → 38 | 7 → 19 | 88 % → 67 % | `agree_tones` |
| KHTN 6 Bài 11 | 85 → 65 | 10 → 30 | 89 % → 68 % | `agree_numbers`, `agree_tones` |
| **total** | **287 → 213** | **77 → 132** | **79 % → 62 %** | |

Bài 73's page range shrank from 117–122 to 117–121: **the back cover is no longer attached.** The imprint page
still is.

**Rescue — the 74 audited served rows of the base run, looked up in the re-run.** A row counts as *no longer
served as before* only when the re-run withholds it, unattaches its page, or does not extract it. A row whose
text merely changed would not count — and in fact **no row changed text**: `tc2-p2` on this batch is a pure
withhold-more build, which is why the base verdicts transfer cleanly.

| failure class | base WRONG: n | of those, no longer served | base OK: n | of those, lost as collateral |
|---|---|---|---|---|
| display | 15 | 6 / 15 = 0.400 [0.198, 0.642] | 59 | 15 / 59 = 0.254 [0.161, 0.378] |
| teaching-critical | 5 | 2 / 5 = 0.400 [0.118, 0.769] | 19 | 8 / 19 = 0.421 [0.231, 0.637] |
| reading order | 0 | — | 26 | 10 / 26 = 0.385 [0.224, 0.575] |
| role | 16 | 9 / 16 = 0.562 [0.332, 0.769] | 58 | 12 / 58 = 0.207 [0.122, 0.328] |
| attachment | 8 | 5 / 8 = 0.625 [0.306, 0.863] | 66 | 16 / 66 = 0.242 [0.155, 0.358] |
| false trust | 13 | 7 / 13 = 0.538 [0.291, 0.768] | 61 | 14 / 61 = 0.230 [0.142, 0.349] |

Row outcomes overall: 53 still trusted and identical · 17 now withheld · 4 now unattached · 0 changed.

**Scoring `tc2-p2`.** Its trusted set is almost exactly a subset of `tc2-p1`'s: of 213 trusted blocks, **210
carry text `tc2-p1` already served identically, and only 3 are new claims** — all 3 were judged fresh from
page renders (2 OK, 1 WRONG: a Ghi nhớ rule served with its two lines rotated and a tone slip). Verdicts were
therefore carried over only where the build serves identical text in the same region, and every carried row is
stamped with where its verdict came from.

| measure (derived false trust, 5 criteria) | OLD | `tc2-p1` | `tc2-p2` |
|---|---|---|---|
| false-trust rate among served rows | 0.727 [0.598, 0.827] · n = 55 | 0.365 [0.264, 0.479] · n = 74 | **0.268** [0.170, 0.396] · n = 56 |
| annotator's own false-trust field | 0.527 · n = 55 | 0.176 · n = 74 | **0.125** · n = 56 |
| display | 0.709 | 0.203 | **0.179** |
| role | 0.164 | 0.216 | **0.125** |
| attachment | 0.036 | 0.108 | **0.037** |

The `tc2-p2` column is a **conditional** rate over the rows that survived the base sample, not a fresh
stratified sample of that build. Read it beside the rescue table, not instead of it.

**What the trade buys, in blocks (point estimates, small samples, wide CIs):** `tc2-p1` serves 287 blocks of
which ≈ 105 are false trust and ≈ 182 are not; `tc2-p2` serves 213 of which ≈ 57 are false trust and ≈ 156 are
not. So the re-run removes roughly **48 false-trust blocks at the cost of roughly 26 correct ones** — a good
trade for legacy data under a fail-closed rule, and a bad one for coverage. Which side of that trade is right
is a Founder decision, not a measurement.

---

## 8. Did the new pipeline rescue the legacy data? — **PARTIAL**

**Yes, on the classes that made the old data dangerous.** Reading order goes 0.424 → 0.000; display 0.709 →
0.203; teaching-critical 0.722 → 0.208; formula/number/unit 0.400 → 0.095; derived false trust 0.727 → 0.365
→ 0.268 on the improved build. Every one of the 16 geometry-rebuilt Toán expressions — content the product
served that was never on the page — is now withheld rather than reconstructed.

**No, on attachment and role.** Attachment got *worse* than the old product (0.036 → 0.108) because the new
pipeline re-derives the same back-cover mistake from headers; `tc2-p2` fixes the back cover (5 of 8 rows) but
still serves a book's imprint page as Bài 73 body. Role is not better (0.164 → 0.216 on `legacy-b1`, 0.125 on
`tc2-p2`, and the annotator known to be stricter on this class judged both sides).

**And not enough to change anything about trust.** 0.268 false trust means roughly one served block in four is
still wrong on the audited sample. No legacy lesson in this batch is trusted, none is eligible for teaching,
and 79 % → 62 % of learning blocks served means the rescue is substantially *withholding*, not repair: of the
131 OLD served blocks, 44 are now withheld and 20 are not extracted at all. **Reprocessing made the legacy
corpus safer and smaller. It did not make it teachable.**

---

## 9. Lessons learned

1. **The old and new pipelines share defects, so "new" is not a synonym for "fixed".** The back-cover
   attachment was not inherited from the packs — it was re-derived from headers. Rebuilding a component does
   not retire a failure class; only measuring it does.
2. **Withholding is what did most of the work.** The class-level improvements come almost entirely from the
   pipeline refusing regions, not from extracting them better — on `tc2-p2` not a single audited row changed
   its text. Any report of "false trust down" must be read with "served share down" beside it.
3. **A row-level re-run delta beats re-annotating.** Because the improved build's trusted set was a near-subset
   of the base build's, 53 of 56 verdicts transferred exactly and only 3 rows needed fresh judgement. Checking
   subset-ness first turned a full re-annotation into three renders — but only because the transfer rule is
   strict (identical text, same region) and stamped on every row.
4. **OCR loss upstream disables a downstream layer.** Circled exercise numerals are dropped by OCR, so the role
   layer has no signal for "this is exercise n" and serves instructions as body. The role failure is not in the
   role code.
5. **Two annotators disagree about *applicability* more than about verdicts.** Teaching-critical had 7
   NA/UNSURE mismatches on 35 judged rows while κ was 0.826 — the protocol needs a sharper rule for when the
   class applies, not a better annotator.
6. **The figure/caption class was not really measured.** Only 2 of 74 NEW rows were caption-kind. Role-stratified
   sampling under-samples a rare-but-important role; the next batch must sample that class explicitly.
7. **Shadow-root containment worked.** Two full pipeline runs wrote nothing outside their own batch directories,
   and the old outputs are still byte-identical beside them.

---

## 10. Next batch proposal (by risk, not by convenience)

Batch 1 covered the P0 classes on 6 lessons. Batch 2 is proposed at **8–10 lessons**, chosen to attack what
batch 1 either failed at or failed to measure:

| priority | what | how many | why |
|---|---|---|---|
| P0 | **Last lessons of books** (`last_lesson_of_book` risk flag; 67 lessons carry `attachment_suspect`) | 3 | the one class where NEW is worse than OLD; the imprint page still survives on `tc2-p2` |
| P0 | **Figure/caption-heavy Science lessons** (KHTN 7/8/9, Khoa học 4/5) | 2 | the class batch 1 could not measure (n = 2); sample caption-kind blocks explicitly, not proportionally |
| P1 | **Toán 4 tập một** (37 lessons in scope, none touched) | 2 | the largest untouched book in scope; checks whether the Toán findings generalise beyond tập hai |
| P1 | **TV5 unranged / offset lessons** (5 unranged lessons in scope) | 2 | attachment without a TOC range — the mechanism the registry flags but batch 1 only met indirectly |
| P2 | **A repeat of Bài 61 and Bài 73** on Lane A's merged build | 2 | the batch-1 rows are the only ones with a full audited baseline; re-running them is the cheapest way to measure the next pipeline |

Sampling changes for batch 2: (a) sample the figure/caption class by role quota, not proportionally;
(b) add a **blind second annotation of the batch rows themselves**, not only of the round-3 sample;
(c) keep the re-run delta as the primary instrument for pipeline comparisons — it needs no re-annotation when
the trusted set is a subset.

---

## 11. What is still not measured

- **No second annotator on the batch-1 rows.** §5 rests on one annotator plus an 8-row successor spot-check.
- **Figure/caption: n = 2 per side.** The rates in §5 for that class are unreadable and are marked as such.
- **`tc2-p2` was previewed on an unreviewed WIP snapshot.** The re-run must be repeated on Lane A-pipeline's
  merged build before the delta is quoted anywhere outside this document.
- **Six lessons out of 243 in scope, out of 3,679 canonical.** Nothing here supports a claim about the corpus.
- **No teaching claim of any kind.** `eligible for teaching` is 0 and the pipeline cannot raise it.
