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
| figure / caption (tagged) | 2 / 55 = 0.036 [0.010, 0.123] | 1 / 74 = 0.013 [0.002, 0.073] | **n too small to read — see §5a** |
| false trust (derived, 5 criteria) | 40 / 55 = **0.727** [0.598, 0.827] | 27 / 74 = **0.365** [0.264, 0.479] | better |
| false trust (annotator's own field) | 29 / 55 = 0.527 [0.398, 0.653] | 13 / 74 = 0.176 [0.106, 0.278] | better |

Denominators (D5): the two sides are **different block sets** — 55 OLD served blocks vs 74 NEW served blocks —
so what is comparable is the *share of served units that is wrong*, not a paired difference. Neither number
divides by 3,679 or 3,381; those denominators describe the historical corpus, not this batch.

### The other half of the ledger: what the withholding costs

The 30 NEW withheld regions were all reviewed, and each carries a judgement on whether the refusal was
*correct* as well as safe. Every one of the 30 is **safe** — no withheld region should have been served as it
stood. But **12 of 30 = 0.400 [0.245, 0.578] were judged OVER-withheld**: clean, simple text refused for a
reason that did not apply to it.

| over-withholding mechanism | rows | what was lost |
|---|---|---|
| `page_feature:color_heavy` — a **page-level** veto | 5 | stanzas of the Bài 25 poem and a paragraph of the Bài 1 reading passage: *the lesson's actual reading* |
| `agree_order` on short labels and titles | 4 | a section title, a rule box, plain instructions |
| `agree_text` on plain prose | 3 | a “Chuẩn bị:” sentence, a sidebar paragraph, a plain question |

The rest are correct refusals and several are exactly what the guard is for: flattened fraction items, a
common-denominator derivation, a watermark, and one `figure_dependent` question that genuinely cannot be read
without its figure.

**This is the finding that keeps the rescue honest.** The improvement in §5 is bought with withholding, and
two fifths of the sampled withholding is not damaged content being refused — it is a poem being refused
because the page around it is colourful.

### 5a. Figure/caption: a targeted quota sample, because the stratified one could not see it

Role-proportional sampling drew only 2 caption blocks out of 74, so the class the Founder named could not be
measured. A **quota sample of the `caption` role** was drawn separately (seed 20260907, 8 blocks — every
caption block of the batch's one figure-heavy lesson, KHTN 6 Bài 11) and annotated the same way. These rows
are *not* a random sample of what the pipeline serves: the rate below is a rate **within the caption class**
and is never pooled with §5.

| measure | result |
|---|---|
| caption blocks judged | 8 (KHTN 6 Bài 11, pdf p37–p40) |
| display fidelity WRONG | **2 / 8 = 0.250** [0.071, 0.591] |
| teaching-critical / reading order | NA on all 8 (captions carry no numbers or multi-line order here) |
| role fidelity WRONG | 0 / 8 |

The two defects are both *caption assembly*, and they are two different mechanisms:

- `…:p037:*:016` — the figure-number chip “Hình 11.1” is served as a caption block **on its own**; the caption
  text that follows it on the same printed line is a different block, so neither block carries the whole caption.
- `…:p039:*:020` — a caption **cut after its first line**, dropping the line that says what the experiment
  determines (the same block the stratified sample had already flagged).

A third finding has no verdict field to land in and is recorded here in words: **5 of the 8 caption blocks are
sub-panel labels** (“a) …”, “b) …”, “c) …”) served as standalone captions with **no reference to the figure
they label**. Each is character-perfect, so every fidelity field says OK — yet a child reading “a) Rác thải”
with no figure attached learns nothing. The audit protocol has no *figure–caption relation* verdict; that is a
protocol gap, not a clean result, and it is filed as a request rather than scored.

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

**What this second annotation does not establish:** it validates the round-3 sample, not batch 1. That gap is
addressed separately in §6a.

### 6a. A blind second annotation of the batch-1 rows themselves — by a different model

The §5 rates were produced by one annotator. A second annotation of **16 of the 74 NEW served rows (21.6 %)**
was drawn from the annotated file with a third seed (20260908), the first annotator's verdicts, notes and error
classes stripped, and judged from the page renders by a **different model** (Claude Fable 5.1 → Claude Opus 5),
in a different session.

| class | n both judged | agreement | **κ** | #1 WRONG | #2 WRONG | confusion (#1/#2) |
|---|---|---|---|---|---|---|
| display | 15 | 0.933 | **0.842** | 0.267 | 0.333 | OK/OK 10 · OK/WRONG 1 · WRONG/WRONG 4 |
| teaching-critical | 6 | 1.000 | **1.000** | 0.333 | 0.333 | OK/OK 4 · WRONG/WRONG 2 |
| reading order | 3 | 1.000 | — (κ undefined: no variance) | 0.000 | 0.000 | OK/OK 3 |
| role | 15 | 0.867 | **0.423** | 0.133 | 0.133 | OK/OK 12 · OK/WRONG 1 · WRONG/OK 1 · WRONG/WRONG 1 |
| attachment | 15 | 1.000 | **1.000** | 0.067 | 0.067 | OK/OK 14 · WRONG/WRONG 1 |
| **false trust** | 15 | **1.000** | **1.000** | 0.200 | 0.200 | OK/OK 12 · WRONG/WRONG 3 |

One sampled row (`n20260906-0089`) had already been judged by the second annotator in the caption quota sample
of §5a, so for that row the second annotation was not blind to *its own* earlier verdict. **The table above
excludes it.** Including it: display κ 0.714 (n = 16, agreement 0.875), role κ 0.429, false trust κ 1.000.

**The headline measure is annotator-independent here: false trust agreed on 15 of 15 rows, κ = 1.000, both at
0.200.** The disagreements are informative and all four are named:

- display, `n20260906-0016`: `46 125 × 3` served as `46 125 x 3`. #2 called the multiplication-sign
  substitution a display error; #1 did not. The numbers and the operation survive either way.
- display, `n20260906-0089` (the excluded row): a figure-number chip served as a caption on its own.
- role, `n20260906-0040`: a destroyed expression (`b) 10 +` for `b) 3/10 + 5/21`) served as `body`. #1 called
  the role wrong; #2 called the role acceptable for a bare expression and put all the damage on display and
  teaching-critical. Both marked it false trust.
- role, `n20260906-0071`: `(Theo Văn Thành Lê)` — the passage's attribution — served as `sidebar`. #2 called
  that a role error because the TSL vocabulary has an `attribution` role; #1 did not.

**Role is the unstable class in every measurement made so far** — κ 0.713 on the round-3 sample, κ 0.423 here.
Three of the four disagreements are about *what a role means*, not about what is on the page. Role rates in
this report should be read as annotator-dependent, and the role protocol needs sharper definitions before role
is used to gate anything.

---

## 7. Re-run on Lane A-pipeline's shipped build (`tc2-p2`, PR #77 @ `cb60cde`)

Batch 1 was re-run on the same spec and the same original source against Lane A-pipeline's shipped, CI-green
build — **called, never edited**. Their branch was merged into this one so the run records a real repository
sha (`af2245a`, whose `tool/corpus` is their `cb60cde`); the identical run had first been made from an exported
tree, and **all 62 outputs are byte-identical between the two**, which is also the determinism check.

Every step ran `rc=0`. Lane D's orchestrator drives their CLI with `TC_ROOT` pointed at a shadow root rather
than `--out`; both contain the run, and the shadow root additionally guarantees nothing outside the batch
directory can be written even by a step that ignores `--out`.

### 7.1 Coverage — what the improved build stops serving

| lesson | learning blocks | trusted (p1 → p2) | withheld (p1 → p2) | served share | new withhold reasons |
|---|---|---|---|---|---|
| Toán 4 Bài 61 | 19 → 19 | 9 → 4 | 10 → 15 | 47 % → **21 %** | `agree_numbers` |
| Toán 4 Bài 73 | 83 → 64 | 67 → 39 | 16 → 25 | 81 % → 61 % | `agree_numbers`, `agree_tones` |
| Toán 5 Bài 6 | 25 → 25 | 14 → 12 | 11 → 13 | 56 % → 48 % | `agree_numbers`, `agree_tones` |
| TV5-1 Bài 25 | 85 → 85 | 62 → 61 | 23 → 24 | 73 % → 72 % | `agree_tones` |
| TV5-2 Bài 1 | 57 → 57 | 50 → 40 | 7 → 17 | 88 % → 70 % | `agree_tones` |
| KHTN 6 Bài 11 | 95 → 95 | 85 → 65 | 10 → 30 | 89 % → 68 % | `agree_numbers`, `agree_tones` |
| **total** | 364 → 345 | **287 → 221** | **77 → 124** | **79 % → 64 %** | |

Bài 73's page range shrank from 117–122 to 117–121: **the back cover is no longer attached.** The imprint page
still is. Toán 4 Bài 61 now serves 4 of 19 learning blocks — most of a Toán lesson is withheld. **That is a
legitimate rescue outcome, not a failure**: the withheld blocks are the flattened fractions the round-3 audit
caught the product teaching. Withholding beats guessing. It also means the lesson is further from usable, not
closer.

### 7.2 Rescue — the 74 audited served rows of the base run, looked up in the re-run

A row counts as *no longer served as before* only when the re-run withholds it, unattaches its page, or does
not extract it. A row whose text merely changed would not count — and **no row changed text**: on these rows
`tc2-p2` is a pure withhold-more build, which is why the base verdicts transfer cleanly.

| failure class | base WRONG: n | of those, no longer served | base OK: n | of those, lost as collateral |
|---|---|---|---|---|
| display | 15 | 6 / 15 = 0.400 [0.198, 0.642] | 59 | 15 / 59 = 0.254 [0.161, 0.378] |
| teaching-critical | 5 | 2 / 5 = 0.400 [0.118, 0.769] | 19 | 8 / 19 = 0.421 [0.231, 0.637] |
| reading order | 0 | — | 26 | 10 / 26 = 0.385 [0.224, 0.575] |
| role | 16 | 9 / 16 = 0.562 [0.332, 0.769] | 58 | 12 / 58 = 0.207 [0.122, 0.328] |
| attachment | 8 | 5 / 8 = 0.625 [0.306, 0.863] | 66 | 16 / 66 = 0.242 [0.155, 0.358] |
| **false trust** | 13 | **7 / 13 = 0.538** [0.291, 0.768] | 61 | 14 / 61 = 0.230 [0.142, 0.349] |

Row outcomes: 53 still trusted and identical · 17 now withheld · 4 now unattached · 0 changed.

### 7.3 Over-withholding — the other half of the ledger

§5 found 12 of 30 reviewed withheld regions were over-withheld. The improved build **serves 7 of those 30
regions again**, and the recovery lands where the diagnosis said it would:

| base withhold reason | reviewed | served again |
|---|---|---|
| `page_feature:color_heavy` (the page-level veto) | 6 | **4** |
| `agree_order` on short labels | 8 | **3** |
| `agree_text` on plain prose | 15 | 0 |
| `math_guard` · `low_ocr_conf` · `figure_dependent` · `page_feature:diagram` | 4 | 0 |

The colour veto becoming block-level is what returns the Bài 25 poem and the Bài 1 reading passage. That is a
real fix to a real over-withholding mechanism, measured rather than claimed.

### 7.4 What the improved build newly claims — and one new defect

`tc2-p2` serves **11 blocks that `tc2-p1` did not**; every other trusted block carries text `tc2-p1` already
served identically. All 11 were judged fresh from page renders (they carry no transferred verdict):

- **7 OK**: the reading passage's opening paragraph, three verse lines, `(Trích)` served with the new
  `attribution` role, the section heading `CÂU ĐƠN VÀ CÂU GHÉP` (swallowed into a rule box on `tc2-p1`), and
  the stage label `Tiến hành:`.
- **1 role-WRONG**: a warm-up task served as `body`.
- **3 display-WRONG, and two of them are a new failure**: two blocks carry five and four **verse lines joined
  into a single prose run** — every character right, every line in order, no line breaks. *The poem of a poetry
  lesson served as prose.* A third is the Ghi nhớ rule served with its two lines rotated; a fourth block is a
  passage paragraph cut mid-sentence.

The verse-flattening is **caused by the fix**: those lines were withheld by the colour veto on `tc2-p1`, so the
defect could not be seen until the content came back. Filed as a pipeline request.

### 7.5 The three-way comparison

Rates are WRONG / (OK + WRONG) among **served** rows, Wilson 95 %, no threshold. Each column has its own
denominator and its own block set — the comparable quantity is *the share of what that side served that is
wrong*, always read beside *how much it served*.

| failure class | OLD (units + packs) | NEW `tc2-p1` | NEW `tc2-p2` (PR #77) |
|---|---|---|---|
| audited served rows | n = 55 | n = 74 | n = 64 |
| display fidelity | 0.709 [0.579, 0.812] | **0.203** [0.127, 0.308] | **0.203** [0.123, 0.317] |
| teaching-critical | 0.722 [0.560, 0.842] | 0.208 [0.092, 0.405] | **0.176** [0.062, 0.410] |
| reading order | 0.424 [0.272, 0.592] | **0.000** [0.000, 0.129] | 0.048 [0.008, 0.227] |
| role fidelity | 0.164 [0.089, 0.283] | 0.216 [0.138, 0.323] | **0.125** [0.065, 0.228] |
| lesson attachment | 0.036 [0.010, 0.123] | 0.108 [0.056, 0.199] | **0.034** [0.006, 0.172] |
| **false trust (derived, 5 criteria)** | **0.727** [0.598, 0.827] | **0.365** [0.264, 0.479] | **0.297** [0.199, 0.418] |
| false trust (annotator's field) | 0.527 | 0.176 | **0.141** |
| — and what each side served | 131 blocks, all of them | 287 of 364 = **79 %** | 221 of 345 = **64 %** |

The `tc2-p2` column mixes 53 verdicts carried over under a strict rule (identical text, same region, origin
stamped on every row) with 11 freshly judged new claims. It is therefore a **conditional** rate over the rows
that survived plus the rows that are new — not a fresh stratified sample of that build. Read it with §7.2.

### 7.6 These numbers are not Lane A-pipeline's numbers — do not compare them

Lane A-pipeline's own report measures `tc2-p1` → `tc2-p2` on **54 gold pages** with **their scorer against a
corrected gold**: FTR 0.0957 → 0.0734, coverage 0.683 → 0.551. This report measures **six legacy lessons** with
the **round-3 false-trust criteria on an audited sample of served blocks**: 0.365 → 0.297, coverage 0.79 →
0.64. The two false-trust numbers differ by a factor of four and **neither is wrong**:

- **Different populations.** Batch 1 was chosen adversarially — the two-column Toán, TV5 and KHTN pages the
  round-3 audit found failing. The gold set is a broader, mostly cleaner sample. A higher rate here is what a
  correctly chosen batch should produce.
- **Different definitions.** Their FTR is false-trusted blocks over trusted blocks under their scorer against a
  page-level gold; this is the derived five-criteria false trust of the round-3 protocol, judged by an
  annotator from page renders on a stratified sample.
- **What agrees is the direction and the trade.** Both measurements say the same two things: fewer wrong blocks
  delivered, and fewer blocks delivered. Coverage 0.683 → 0.551 there, 0.79 → 0.64 here.

Quoting one number in the other's place would be a denominator error (D5). They belong in the same report only
as two independent readings of the same direction.

**In blocks, with point estimates and wide intervals:** `tc2-p1` serves 287 blocks of which ≈ 105 are false
trust and ≈ 182 are not; `tc2-p2` serves 221 of which ≈ 66 are false trust and ≈ 155 are not. The improved
build delivers **≈ 39 fewer wrong blocks and ≈ 27 fewer right ones**. Against the OLD product — 131 served
blocks, ≈ 95 of them false trust, ≈ 36 not — `tc2-p2` delivers **roughly four times as much correct content
and about two thirds as many wrong claims**, which is the only comparison that answers the Founder's question.

## 8. Did the new pipeline rescue the legacy data? — **PARTIAL, and more than it was at the start of the day**

**Yes, on the classes that made the old data dangerous.** Reading order 0.424 → 0.000 → 0.048; display 0.709 →
0.203 → 0.203; teaching-critical 0.722 → 0.208 → 0.176; formula/number/unit 0.400 → 0.095; derived false trust
**0.727 → 0.365 → 0.297**. Every one of the 16 geometry-rebuilt Toán expressions — arithmetic the product
served that was never on the page — is withheld rather than reconstructed.

**Yes on the two classes that were worse, once Lane A shipped.** On the first reprocess, attachment was *worse*
than the old product (0.036 → 0.108: the new pipeline re-derived the back-cover mistake from headers rather
than inheriting it) and role was not better (0.164 → 0.216). On PR #77 both come back: **attachment 0.034,
role 0.125** — better than the old product on both. The back cover is unattached and the section headings,
attributions and stage labels the role layer used to swallow are now their own blocks.

**No, not completely.** Three defects survive identically across both builds and are named with block ids in
the pipeline requests: a book's **imprint page** is still served as Bài 73 body, the **lesson title** of Toán 5
Bài 6 is still served with tone slips that turn its key terms into other words, and two **fraction fragments**
(`b) 10 +` for `b) 3/10 + 5/21`) are still served as content. And the fix to the colour veto uncovered a defect
underneath it: the Bài 25 poem now comes back, but **its verse lines are joined into a single prose run** — the
poem of a poetry lesson served as prose.

**And not nearly enough to change anything about trust.** 0.297 false trust means roughly three served blocks
in ten are still wrong on the audited sample. No legacy lesson in this batch is trusted, none is eligible for
teaching, and **79 % → 64 % of learning blocks served** means the improvement is substantially *withholding*,
not repair — Toán 4 Bài 61 now serves 4 of its 19 learning blocks. Withholding beats guessing, and the
withheld blocks there are exactly the flattened fractions; but a lesson that shows a child four blocks is
further from usable, not closer.

**The trade, in blocks** (point estimates, small samples, wide intervals):

| | blocks served | ≈ false trust | ≈ correct |
|---|---|---|---|
| OLD (units + packs) | 131 | 95 | 36 |
| NEW `tc2-p1` | 287 | 105 | 182 |
| NEW `tc2-p2` (PR #77) | 221 | 66 | 155 |

Against the OLD product the reprocess delivers **roughly four times as much correct content and about two
thirds as many wrong claims**. Against its own first attempt, the improved build delivers **≈ 39 fewer wrong
blocks and ≈ 27 fewer right ones**. Whether that trade is the right one is a Founder decision, not a
measurement.

**Reprocessing made the legacy corpus safer and smaller. It did not make it teachable.**

---
## 9. Lessons learned

1. **The old and new pipelines share defects, so "new" is not a synonym for "fixed".** The back-cover
   attachment was not inherited from the packs — it was re-derived from headers. Rebuilding a component does
   not retire a failure class; only measuring it does.
2. **Withholding is what did most of the work — and a page-level guard is a blunt instrument.** The class-level
   improvements come almost entirely from the pipeline refusing regions, not from extracting them better — on
   `tc2-p2` not a single audited row changed its text. Any report of “false trust down” must be read with
   “served share down” beside it, and with the **over-withholding rate** (0.400 of reviewed withheld regions)
   beside that. A guard that vetoes a whole page because it is colourful refuses the poem the lesson is about.
3. **A row-level re-run delta beats re-annotating.** Because the improved build's trusted set was a near-subset
   of the base build's, 53 of 56 verdicts transferred exactly and only 3 rows needed fresh judgement. Checking
   subset-ness first turned a full re-annotation into three renders — but only because the transfer rule is
   strict (identical text, same region) and stamped on every row.
4. **OCR loss upstream disables a downstream layer.** Circled exercise numerals are dropped by OCR, so the role
   layer has no signal for "this is exercise n" and serves instructions as body. The role failure is not in the
   role code.
5. **Two annotators disagree about *applicability* more than about verdicts.** Teaching-critical had 7
   NA/UNSURE mismatches on 35 judged rows while κ was 0.826 — the protocol needs a sharper rule for when the
   class applies, not a better annotator. And **role is unstable in both second annotations** (κ 0.713 and
   0.423), always because the two annotators mean different things by a role — while false trust, the measure
   the report leans on, reached κ 1.000 across two different models on the batch rows.
6. **Role-proportional sampling cannot measure a rare role.** Only 2 of 74 NEW rows were caption-kind, so the
   figure/caption class was invisible until a **quota sample** was drawn for it (§5a) — which then found
   0.250 display-WRONG within the class and a defect the fidelity fields cannot express at all (a caption
   detached from its figure). A sampling design that is right for the *batch* can be blind to a *class*.
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

## 11. The one thing only the Founder can change

`trusted` and `eligible for teaching` are 0 not because the numbers came out badly but because **there is no
rule to compare them to.** `tool/corpus/legacy/scoreboard.py` reads
`docs/research/legacy-reprocess/THRESHOLDS.json`; the file does not exist, so both counts are 0 and the
scoreboard says why. `THRESHOLDS.example.json` in the same directory is a **template, not a decision** — it
documents exactly what setting the record would do and what it would not:

- With a record, a lesson counts as `trusted` when it is fully sourceable **and** independently audited **and**
  its audited false-trust rate is at or below `max_false_trust_rate`.
- `eligible_for_teaching` moves only if `teachingAuthorised` is also true — trust and permission to teach are
  two separate Founder acts.
- Setting it changes **no measurement**: every rate, sample and κ in this report is computed identically with
  or without the file.

For calibration, and not as a recommendation: on batch 1 the audited false-trust rate is 0.365 (`legacy-b1`)
and 0.268 (`tc2-p2`) with wide intervals, and **0 of 6 lessons reached full sourceability** — so any
`max_false_trust_rate` below ≈ 0.27 leaves the count at 0 whatever the audit sample had done.

## 12. What is still not measured

- **The second annotation of the batch-1 rows covers 16 of 74 NEW rows (21.6 %) and no OLD rows.** The OLD-side
  rates in §5 still rest on a single annotator.
- **Figure/caption is measured only within one lesson.** §5 has n = 2 per side and is unreadable; §5a's quota
  sample covers the batch's single figure-heavy lesson (8 blocks, KHTN 6 Bài 11) and no other book.
- **The audit protocol has no figure–caption *relation* field**, so a caption detached from its figure scores
  as fully correct. Batch 1 found 5 such blocks; they are described in §5a and cannot be counted.
- **The `tc2-p2` column is conditional, not a fresh sample.** 53 of its 64 rows carry verdicts transferred from
  the base run under a strict rule; 11 are freshly judged new claims. No fresh stratified sample of `tc2-p2`'s
  221 trusted blocks has been drawn, so its rate is an estimate over the rows that survived plus the rows that
  are new. §7.2 is the measurement that needs no such assumption.
- **`tc2-p2` is measured on PR #77's head (`cb60cde`), which is not merged.** If that PR changes before the
  Founder merges it, the delta must be recomputed.
- **Six lessons out of 243 in scope, out of 3,679 canonical.** Nothing here supports a claim about the corpus.
- **No teaching claim of any kind.** `eligible for teaching` is 0 and the pipeline cannot raise it.
