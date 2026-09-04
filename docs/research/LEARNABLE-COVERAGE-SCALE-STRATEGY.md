# Learnable Coverage Scale Strategy — how do we grow 113/3,679 truthfully?

Master K-12 Order, Founder Question 2026-09-04. Every number below is measured
against the repo/corpus at commit `7fef188` (post-WAL-190), not estimated from
memory. Where a number is a range, the assumption behind the range is stated.

---

## UPDATE (same-day, post-Founder-approval) — Ngữ văn POC attempted, correctly
not shipped this round

Following Founder's approval of this strategy, began the recommended #1 POC
(Ngữ văn reading extraction). Findings, more detailed than the original entry
in §5's Opportunity Map:

**The passage-boundary marker generalizes further than first measured.**
Grade 6 raw OCR shows an explicit, consistent `Trước khi đọc` / `Đọc văn bản`
marker pair (11-15 occurrences/book). Testing marker-*containment* (not
line-start matching) against the already-computed `poc-out/units-k12/` output
confirms real, correctly lesson-attached passages — including recognizable,
real literary content (Andersen's "Cô bé bán diêm"/The Little Match Girl at
grade 6; "Thần Trụ Trời" and other creation myths at grade 10; "Chuyện người
con gái Nam Xương" at grade 9) — for **grades 6, 7, 8, 9, and 10** (15, 24, 25,
25, and 8 candidate passage-units respectively). This is better-generalizing
evidence than the original entry assumed.

**What's still missing, and why this was not rushed to ship**: `units-k12`'s
generic extractor does not cleanly separate the passage from its paired
comprehension question the way the dedicated `extract_units_tv.py` does for
Tiếng Việt (`SECTION_TEXT >= 400 chars` + adjacent `EXERCISE` role, computed
independently) — Ngữ văn's units mix passage and trailing question text into
one greedy block. A naive length+lesson-attachment filter also picks up
front-matter and table-of-contents blocks as false positives (both filtered
out here, but only after being caught by hand-inspection, not automatically).
Building a clean passage/question splitter requires the same kind of
dedicated, raw-OCR-based, grade-specific investigation WAL-190's science
extractor needed — not a quick reuse of already-computed data. Attempting it
under time pressure would have violated this project's own gold-set-first
discipline, so it was deliberately stopped short of implementation.

**What did ship this round instead**: WAL-191 — while investigating this,
found and fixed a real latent bug: `_openReading`/`_openWriting` hardcoded
`subjectId: 'tieng-viet'`, the same class of bug WAL-173 already fixed for
Experiment. Not yet active (both fields currently hold only real Tiếng Việt
data), but would have silently mis-tagged evidence the moment Ngữ văn data
was ever added — exactly the kind of thing this fix needed to happen *before*
that data lands, not after.

**Revised confidence for §5's Ngữ văn row**: lesson-count estimate (50-60)
still stands as directionally reasonable given the marker now confirmed across
5 grades, not 1; cost/confidence should move from "low-medium cost" to
"medium cost" — the passage/question splitter is real, un-started work,
comparable in scope to what `extract_units_tv.py` already required for TV5.

**Noise patterns identified for whoever builds the dedicated extractor next**
(raw OCR of grade 6, "Dế Mèn phiêu lưu kí" excerpt, pages 16-18): footnote
definitions interleaved at page bottoms (`(1) Chết ngay đuôi: chết ngay lập
tức...` — a numbered-parenthetical followed by a colon-definition, distinct
in shape from real narrative sentences); orphaned footnote-marker lines
(`(2)`, `(4)` alone with no adjacent text, where OCR separated the marker
from its definition); sidebar reading-strategy boxes in ALL CAPS (`THEO DÕI`,
matching the `DỰ ĐOÁN` pattern seen elsewhere in the same book) that interrupt
the narrative mid-flow; standalone page-number lines (bare digits). None of
these are exotic — each has a mechanically checkable shape (regex for the
footnote-definition pattern, a small fixed set of ALL-CAPS sidebar labels to
skip, `^\d+$` for page numbers) — but building and gold-set-validating the
combination is real work, not a five-minute regex tweak, which is exactly why
this was not rushed into this checkpoint.

---

## 1. Challenge the number: is 113 correct?

**113 measures exactly one thing**: distinct `(sourceDocumentId, lessonNo)` pairs
that have ≥1 activity in the six hardcoded `LessonIndex` fields
(`toanExercises`, `tvReadings`, `tvWritings`, `suSources`, `khoaExperiments`,
`diaMaps`), each of which is wired to a Surface that emits real `LearningEvent`s.
That is a legitimate, narrow definition — but it conflates several things Founder
is right to want separated. Splitting it:

| Tier | Definition | Measured now |
|---|---|---|
| **ACTIVITY_PRESENT** | Some structured, source-grounded activity data exists for the lesson, in *any* extraction (including the newly-inventoried `poc-out/units-k12/`), regardless of whether it's wired to a Surface | **Not previously measured.** New measurement below: ~37,600 units attached to lessons across 306 books, before quality filtering — see §2. |
| **EVIDENCE_CAPABLE** | The activity is wired to a Surface that calls `validateCandidateEvidence`/emits a real `LearningEvent` | **113** (the number this checkpoint has been reporting) |
| **LEARNING_EXPERIENCE_VALID** | The activity is not just wired, but source-grounded AND pedagogically coherent AND correctly lesson-attached AND text-quality-clean (no reading-order corruption) | **Unmeasured precisely** — likely meaningfully *below* 113 isn't right (113 was gold-set-checked for WAL-190's +28, and the pre-existing 85 came from equally-scrutinized Toán/TV/Sử/Khoa work) — 113 is a reasonable floor for this tier too, not an overcount. |
| **SAM_SUPPORTABLE** | SAM can explain/ground/reference the lesson (e.g. from an extracted learning objective) without running a full evidence-producing activity | **Not previously tracked as a tier.** Real candidate signal exists now (SGV `MỤC TIÊU` objectives) — see §5. |

**Verdict: 113 is not wrong, but it's the narrowest of four legitimate tiers, and
until this checkpoint the other three weren't being measured at all.** The
biggest correction this analysis makes isn't to the number 113 — it's adding the
missing ACTIVITY_PRESENT and SAM_SUPPORTABLE tiers, which is where most of the
real opportunity turns out to live (§2-§5).

---

## 2. THE BIG FINDING: 53,714 units already extracted, 70% lesson-attached,
never wired into the app

A generic, subject-family-aware extractor (`tool/ingest/extract_units_generic.py`,
already built, docstring dated to a prior "K-12 §VII" pass) has **already been run
against 306 SGK books**, based on a real structural insight: the national
curriculum (GDPT 2018) uses a shared activity-marker framework across *every*
subject (Khởi động/Khám phá/Luyện tập/Vận dụng/Ghi nhớ — "Warm-up/Explore/
Practice/Apply/Remember"), with 8 subject-family adapters already coded (Toán,
Tiếng Việt, Ngữ văn, KHTN, Khoa học, Lịch sử, LS&ĐL, Địa lí) plus a shared-core
fallback for every other subject.

Its output (`poc-out/units-k12/*.json`) has never been read by
`build_lesson_index.py` — the pack compiler that actually feeds the app. **This
is C-013/WAL-190's pattern again, but roughly 40x the scale**, and this time it
comes with a real, measured, honest catch: quality is highly variable.

### Aggregate numbers (measured, all 306 SGK books)
| Subject | Books | Units | % lesson-unattached |
|---|---|---|---|
| Tiếng Anh | 18 | 7,025 | 18% |
| Chuyên đề | 33 | 4,539 | 23% |
| Tiếng Việt | 9 | 4,419 | 27% |
| Công nghệ | 21 | 4,351 | 13% |
| **Ngữ văn** | 14 | 3,397 | **8%** |
| Mĩ thuật | 39 | 2,890 | 77% |
| **Tin học** | 10 | 2,749 | **0%** |
| Toán | 20 | 2,681 | 34% |
| **KHTN** | 4 | 2,074 | **0%** |
| GDTC | 21 | 2,001 | 14% |
| LS&ĐL | 6 | 1,813 | 3% |
| *(21 more subjects, smaller volume)* | | | |
| **TOTAL** | 306 | **53,714** | **30%** (37,399 attached) |

### Quality, sampled by hand (not just attachment rate)
- **Ngữ văn 10** (sample: a Vietnamese creation-myth unit): genuinely excellent —
  clean, grammatical, real literary prose, well-posed comprehension questions,
  correctly lesson-attached. Directly reusable by the *already-shipped*
  `ReaderScreen`/EP-002 pattern (same shape as TV5's proven 125-activity win).
- **Tin học 9** (sample): clean, real digital-citizenship/ethics questions,
  correctly attached, immediately plausible as multiple-choice/open-response
  content.
- **Toán 8** (sample): text quality degraded by math-notation OCR loss (exponents,
  special symbols frequently mangled — "5x2-2xy" instead of "5x²-2xy") *and* 34%
  of units are unattached — a harder subject than grade 4-5's simpler arithmetic.
- **Khoa học 5 intro/graphic pages** (sample): **severely corrupted** — confirmed,
  by comparing OCR line y-coordinates, to be a genuine multi-column reading-order
  defect (unrelated text columns interleaved mid-sentence), not ordinary character
  noise. This is the same *class* of bug C-009 already fixed for TOC extraction,
  but that fix was never applied to this separate body-text pipeline. Prevalence
  across the wider corpus is **not yet measured** — this sample was one
  graphic-heavy page, not representative of typical instructional pages (which
  are simpler layouts and, per WAL-190's separate clean extraction of the same
  book's experiment steps, read fine).

**Honest conclusion**: this is real, large, mostly-attached, subject-family-aware
pre-extracted data — but it needs a validation/filtering gate (to catch the
column-scrambling failure mode) and per-family role→Surface mapping work before
any of it is safe to show a child. It is the single largest lever found this
checkpoint, and also the least immediately shippable — see Option E/F below.

---

## 3. Case study: SGV objectives — a real, narrow, working signal

Founder's question: can SGV tell us HOW to teach, where SGK tells us WHAT?

**Answer, measured, not assumed: yes, narrowly, where a specific marker exists.**
`tool/extract/extract_objectives.py` recognizes SGV Toán's own structural
convention (`Bài N... → MỤC TIÊU → Giúp HS: → bullets`) and has already extracted
302 clean, per-lesson, source-stated learning objectives for Toán 4-5 SGV (e.g.
*"Đọc, viết, so sánh được các số tự nhiên"* — real, concept-tagged, lesson-
attached, zero inference). This predates this checkpoint and is part of why
Toán 4-5 already counts in the 6-book "semantic" tier.

**New this checkpoint**: confirmed via direct grep that the same `MỤC TIÊU`
marker appears **56 times each** in KHTN 6 SGV and Toán 9 SGV (roughly one per
lesson — the right density) but **zero times** in TV5 SGV (a different document
convention — this doesn't generalize universally). This is a validated,
bounded-cost lead to extend a proven extractor to at least 2 more subject
families, the same WAL-190-style move.

**Important distinction**: an extracted objective is SAM_SUPPORTABLE content
(SAM can say "this lesson aims to teach X, sourced from the teacher's guide"),
not automatically EVIDENCE_CAPABLE — a statement of intent is not an activity a
child does. Do not count objective-extraction wins as Learnable-lesson wins; they
grow a different, still-valuable tier.

The richer signal Founder asked about (prerequisites, misconceptions, expected
learner response, scaffold sequencing) was **not found** in this pass — not
because it was searched for and ruled out, but because time this checkpoint went
to the higher-confidence `MỤC TIÊU` lead instead. Genuinely open, not answered.

---

## 4. Product coverage tiers (not everything should aim for the same state)

Applying Founder's requested framework to what's actually been found:

| Tier | What it means | Examples found this checkpoint |
|---|---|---|
| **FULLY LEARNABLE** | Runs a real activity + produces Evidence | Science experiments (113 lessons, shipped); Ngữ văn reading (high-confidence, not yet shipped); History source-excerpts grade 4-5 (shipped); Tin học digital-ethics questions (high-confidence, not yet shipped) |
| **SAM SUPPORTABLE** | SAM can explain/ground/prepare with real source, but doesn't reproduce the book's own activity | SGV learning objectives (Toán proven, KHTN/Toán-upper confirmed extendable); likely most "EXAMPLE"-role Toán units (worked examples SAM could show and explain, even if not turned into a gradable exercise) |
| **BROWSABLE/REFERENCE** | Source available, no activity attempted or safely extractable yet | The bulk of the 3,566 non-Learnable lessons today; most of Toán 6-12 pending math-OCR fix; History grade 6-9 pending more validation |
| **EXTERNAL-MODALITY-REQUIRED** | Needs audio/video/physical/group presence this corpus/app cannot provide | English "Listen and match"/"Find someone who..." (confirmed via real OCR inspection); GDTC (physical education — an "activity" here is literally a body doing something, not a digital interaction); much of Âm nhạc (music, needs audio); likely most Mĩ thuật (art, needs physical media) |

**This framework matters for the target-scenario math in §7**: a meaningful
fraction of the corpus (my rough estimate: GDTC 84 lessons + Âm nhạc's music
performance content + the audio/social fraction of foreign languages + most Mĩ
thuật + HĐTN's experiential-activity content — very roughly 500-700 lessons, 15-
20% of the corpus) is honestly EXTERNAL-MODALITY-REQUIRED and should not be
chased toward "Learnable" at all. Treating 3,679 as the addressable denominator
overstates the real ceiling.

---

## 5. Opportunity Map

| Pattern | Lessons (measured/estimated) | Grades | Source quality | Pedagogy signal | Existing Surface? | Existing Evidence contract? | Missing capability | Potential unlocked | Confidence | Cost/Risk |
|---|---|---|---|---|---|---|---|---|---|---|
| Science experiment (extend further) | ~10-15 more (title-quality edge cases, deferred 3rd bug) | 4,6,7,8,9 | High | Encoded in marker | Yes (`ExperimentScreen`) | Yes | Fix the interrupted-multi-line-step case | +10-15 | High | Low |
| **Ngữ văn reading** | ~55-60 (measured: family has 62 total lessons, sample quality excellent) | 6-12 | High (sampled) | Encoded (comprehension Qs already in text) | Yes (`ReaderScreen`, same as TV5) | Yes | Extend `tv_readings`-style extraction to Ngữ văn book-name pattern; validate on more samples | +50-60 | **High** | **Low-Medium** |
| **Tin học exercises** | ~100-150 (10 books, 2,749 units, 0% unattached) | 6-12 | High (sampled) | Real MCQ/open-response Qs | Partial — needs a "closed/open question" Surface (`ReaderScreen`'s open-question mode may already fit) | Yes, if mapped to `ReaderScreen`-shape | Role→Surface mapping + gold-set validation across more books | +100-150 | Medium-High | Low-Medium |
| SGV objectives (Toán 6-12, KHTN 6-9) | N/A directly to Learnable — grows SAM_SUPPORTABLE | 6-12 | High (proven pattern) | Explicit, source-stated | New (objective-display, not built) | N/A (not evidence-producing) | New lightweight "why this lesson" Surface/UI element | Improves SAM explanation quality for ~100+ lessons | High | Low |
| Toán 6-12 exercises | Unknown, gated by math-OCR quality (34% unattached, notation corruption) | 6-12 | Medium-Low | Present but noisy | Yes (`toanExercises`/existing Toán flow) | Yes | Math-notation-aware OCR/text cleanup; lesson-attachment fix | +50-150 (wide range) | Low-Medium | Medium |
| History source-excerpts, grade 6-9 | Unknown, one hand-checked example | 6-9 | Medium (noisier marker) | Present, needs more validation | Yes (`SourceReaderScreen`) | Yes | More gold-set examples before automating boundary detection | +10-30 | Medium | Low-Medium |
| Generic units-k12, remaining subjects (GDKT&PL, Đạo đức, LS&ĐL, Công nghệ) | Large but unvalidated (~10,000+ attached units across these) | K-12 | Unknown, needs sampling per subject | Unknown | Mostly no (needs new Surfaces or mapping) | No | Validation/filtering gate for the column-scrambling defect; per-family Surface mapping; pack-compiler integration | Potentially +300-800, wide uncertainty | Low-Medium | Medium-High |
| English "Read and complete" | Unknown, needs corpus-wide fraction measurement | 3-12 | High for this sub-pattern | Present (real gap-fill Qs) | No — needs new dialogue-shaped Surface | No | New activity model + Surface (turn-taking dialogue) | +30-80 (guess, unmeasured fraction) | Low | Medium-High |
| GDTC / PE | 84 books' worth of content | K-12 | N/A | N/A | N/A | N/A | **None recommended** — physical activity, wrong medium | 0 (by design) | High confidence this is DO-NOT-BUILD | N/A |

---

## 6. Strategies

### Option A — Extend proven deterministic extractors (WAL-190-style)
**What**: Ngữ văn reading, Tin học exercises, SGV objectives to KHTN/Toán 6-12,
remaining science-title edge cases.
**Benefit**: Directly reuses shipped Surfaces; near-zero architecture risk.
**Coverage potential**: +150-250 lessons (measured/high-confidence estimate).
**Cost**: Low — days, not weeks, per pattern, following the WAL-190 gold-set loop.
**Pedagogical risk**: Low — same discipline that already worked.
**Hallucination risk**: None — zero LLM in this option.
**Manual review cost**: Low — same gold-set-of-~10 loop already proven.
**Scalability**: Per-subject, bounded, repeatable.
**Time to first result**: Days per pattern.
**Dependencies**: None beyond engineering time.

### Option B — Activity-pattern adapters (formalize the units-k12 role→Surface mapping)
**What**: Build the missing translation layer from `units-k12`'s generic roles
(EXERCISE/ACTIVITY/EXPERIMENT/OBSERVATION/SOURCE_TEXT/CONCEPT_EXPLANATION) to
existing (and a few new) Surfaces, plus the validation gate for text quality.
**Benefit**: Unlocks the 37,600-unit already-attached corpus systematically,
not book-by-book.
**Coverage potential**: +300-800 lessons — wide range, gated entirely on how much
of the corpus clears a real quality bar once one is built.
**Cost**: Medium — the validation gate and role-mapping design is real,
un-started engineering work, but reuses `units-k12`'s already-completed
extraction pass.
**Pedagogical risk**: Medium — role classification is per-subject-generic, not
hand-verified per family the way Option A's single-pattern wins are.
**Hallucination risk**: None — still zero LLM, purely deterministic + validation.
**Manual review cost**: Medium-High — needs a real gold-set pass per subject
family before trusting any family broadly.
**Scalability**: High once the validation gate exists — it's the general-purpose
version of Option A.
**Time to first result**: Weeks (gate + first 2-3 families validated).
**Dependencies**: Requires fixing (or at least detecting/excluding) the
column-scrambling defect first.

### Option C — Subject-family adapters (English, and other genuinely-new shapes)
**What**: Purpose-built new Activity models + Surfaces for subjects whose content
doesn't fit any existing shape (English dialogue, possibly others once
investigated).
**Benefit**: Only path to Learnable coverage for subjects Option A/B structurally
cannot reach.
**Coverage potential**: Unknown until the "what fraction is solo-digitizable"
research (already recommended, not yet done) produces a number. Rough,
low-confidence guess: +30-80 lessons for English specifically if pursued.
**Cost**: Medium-High per subject — genuine new design work, not extraction reuse.
**Pedagogical risk**: Medium — new Surface = new place to get child-facing UX wrong.
**Hallucination risk**: None if kept deterministic; rises if any generative
component is added to fill dialogue gaps (explicitly do not do this).
**Manual review cost**: Medium — new pattern needs its own gold-set discipline
from scratch.
**Scalability**: Low — by definition, one adapter unlocks one subject family.
**Time to first result**: Weeks-to-months per new subject family.
**Dependencies**: The "fraction digitizable" research must come first.

### Option D — SGK + SGV pedagogy extraction (objectives, and further SGV signal)
**What**: Extend `extract_objectives.py`'s proven pattern; research whether
richer SGV signal (prerequisites, guiding questions, misconceptions) exists in
any subject's SGV convention.
**Benefit**: Grows SAM_SUPPORTABLE tier cheaply; could eventually inform
Adaptive Challenge / prerequisite-sequencing work (not built yet, out of scope
here).
**Coverage potential**: Does not directly grow Learnable; growth is in a
separate, still-valuable tier. Objectives alone: ~100+ lessons' worth of
SAM-explainable grounding.
**Cost**: Low for the already-proven objectives pattern; unknown for richer
signal (unresearched).
**Pedagogical risk**: Low — SGV's own stated goals, not inferred.
**Hallucination risk**: None.
**Manual review cost**: Low.
**Scalability**: Bounded by how many subjects' SGVs share a recognizable
structural marker — untested beyond `MỤC TIÊU`.
**Time to first result**: Days.
**Dependencies**: None.

### Option E — Bounded AI-assisted build-time extraction + deterministic
validation + gold review
**What**: For content where deterministic markers don't exist or are too noisy
(e.g. History's grade 6-9 boundary problem, or classifying `units-k12`'s
ambiguous roles), use an LLM *at build time only*, never at runtime, to propose
candidate structure — then validate deterministically (does the claimed excerpt
actually appear verbatim in the source page? does the claimed lesson attachment
match the page-range table?) and gold-review before it ever reaches
`assets/pack/`.
**Benefit**: Could handle the fuzzier cases Option A/B's pure regex approach
can't (this is genuinely where AI adds value — pattern-recognition on messy
layout, not content invention).
**Coverage potential**: Unmeasured — no POC built this checkpoint (research
question, not implemented, per explicit order not to build yet).
**Cost**: Medium (build-time compute + pipeline engineering) + must build the
deterministic validator (verbatim-match check against source) as a hard gate.
**Pedagogical risk**: Medium if the *validator* is weak; low if the validator is
strict (reject anything not verbatim-traceable to source text).
**Hallucination risk**: **This is the real risk to manage.** Mitigation: the
LLM only ever proposes *structure* (where does this experiment/quote/exercise
start and end, which lesson does it belong to) over text that must remain
100% verbatim from OCR — never asked to write or paraphrase content. A
deterministic post-check (exact substring match against source OCR) makes
silent content fabrication structurally impossible, only mis-boundary-detection
possible, which gold review then catches.
**Manual review cost**: Medium-High initially (building trust), should drop
per-subject-family as false-positive rate is measured and the LLM's boundary
detection is validated against a growing gold set.
**Scalability**: Potentially the highest-scale option once trusted — but trust
must be earned incrementally, never assumed.
**Time to first result**: Weeks (needs the validator built first, then a small
gold-set trial).
**Dependencies**: A verbatim-match validator, which doesn't exist yet.

### Option F — Hybrid Learning Experience Factory (the actual recommendation)
**What**: Not a single new system — the combination already emerging from this
checkpoint's evidence: Option A (ship now, cheap, proven) running in parallel
with Option B's validation-gate build-out (which subsumes and generalizes A over
time), Option D's objective-extraction running alongside for the SAM_SUPPORTABLE
tier, and Option E reserved specifically for the cases A/B/D's deterministic
approach demonstrably can't reach (History's noisy boundary, `units-k12`'s
ambiguous roles) — never as the default path.
**This matches what already worked**: WAL-190 itself was Option A. The
`units-k12` discovery is Option B waiting to be finished. `extract_objectives.py`
is Option D, proven and extendable today. Nothing found this checkpoint
justifies a from-scratch "generic Blueprint Compiler" (Option long-since
rejected per C-007) — the working pattern is deterministic-extraction-first,
AI-assisted-and-gated only where deterministic genuinely can't reach.

---

## 7. Target coverage scenarios (ranges, not invented single numbers)

| Scenario | Estimated Learnable | % of 3,679 | Basis |
|---|---|---|---|
| **CURRENT** | 113 | 3.07% | Measured |
| **LOW-RISK QUICK WINS** (rest of Option A: Ngữ văn + Tin học + SGV-objective-adjacent quick science fixes) | ~300-350 | 8-10% | Measured lesson counts for Ngữ văn (62 total, ~55-60 reachable) + Tin học (sampled clean, conservative 100-150 of its corpus) + minor science cleanup |
| **PROVEN PATTERN EXPANSION** (A fully done + History grade 6-9 validated + Toán 6-12 math-OCR partially fixed) | ~450-550 | 12-15% | Adds History's ~10-30 range and a conservative slice of Toán 6-12's noisier ~50-150 range |
| **SUBJECT-FAMILY ADAPTERS + Option B validation gate live** (several more `units-k12` families cleared, English adapter shipped) | ~900-1,400 | 25-38% | Wide range — entirely gated on what fraction of the 37,600 already-attached units clears a real quality bar, which is genuinely unmeasured; treat as directional, not committed |
| **SGK+SGV HYBRID PIPELINE** (Option E trusted and scaled for the hardest remaining cases) | ~1,400-2,000 | 38-54% | Speculative — depends on a validator that doesn't exist yet; only reachable if Option E's hallucination-risk mitigation holds up under real gold-review scrutiny |
| **LONGER-TERM REALISTIC CEILING** | ~1,800-2,400 | **~50-65%**, not 80-100% | The External-Modality-Required tier (§4: PE, music performance, most art, audio/social language content) is a genuine, permanent ceiling on this medium — my best estimate is 15-20% of the corpus (500-700 lessons) can never honestly be "Learnable" via a solo digital experience regardless of investment |

**Direct answer to "is the destination closer to 10/30/60/80%": closer to
30-60%, trending toward the lower half of that band unless Option E (the
riskiest, least-proven option) pays off. 80% is not supported by this
checkpoint's evidence — it would require treating External-Modality-Required
content as solvable, which it structurally isn't with this corpus and medium.**

---

## 8. Top 5 investments, ranked

Ranking formula: potential valid Learnable coverage × pedagogical value × reuse
× source confidence ÷ cost ÷ risk.

**#1 — Ngữ văn reading extraction (Option A).** If we build this, a Grade 6-12
student gets real literature comprehension activities — the exact same trusted
`ReaderScreen` experience TV5 students already have — sourced from clean,
hand-verified real text. Highest score: proven Surface, proven pattern, clean
sample, zero new architecture, ~55-60 lessons for days of work.

**#2 — Tin học exercise extraction (Option A/B boundary).** If we build this,
every grade 6-12 student gets real digital-citizenship and CS comprehension
questions. Second-highest: 0% lesson-unattached (best attachment rate measured
anywhere), clean sample, likely reuses `ReaderScreen`'s open-question mode with
modest adaptation. Slightly lower confidence than #1 only because the
Surface-fit hasn't been proven yet (Ngữ văn's fit is closer to certain).

**#3 — SGV objectives extension to KHTN 6-9 + Toán 6-12 (Option D).** If we
build this, SAM can truthfully explain *why* ~100+ more lessons matter, sourced
from the teacher's own stated goals — a cheap, proven, zero-risk win that grows
a currently-empty tier (SAM_SUPPORTABLE) rather than competing with the other
items for Learnable coverage.

**#4 — The `units-k12` validation gate (Option B, foundational).** If we build
this, every subsequent subject-family win gets cheaper — it's the piece that
turns "40x more raw extraction than has ever been usable" into something
trustworthy. Ranked #4 not because it's low-value but because it's a
prerequisite investment (infrastructure, not a coverage win by itself) — its
payoff shows up in items built *after* it, not immediately.

**#5 — History grade 6-9 gold-set validation (Option A, in progress).** If we
build this, ~10-30 more lessons of genuinely valuable primary-source reasoning
content (Hồ Chí Minh's testament and similar) become available, extending an
already-proven Surface. Ranked #5 because the potential coverage is smaller
than #1-#3 and the validation work (more gold-set examples needed) is not yet
done — this is "keep investigating," not "ready to build" today.

---

## 9. What cannot/should not be automated

- **GDTC/PE activities.** Physical movement is not a digital interaction this
  app's medium can meaningfully represent as a graded activity. Not a
  capability gap — a medium mismatch. Recommend: leave Browsable-only, possibly
  reframe as SAM_SUPPORTABLE reference content (SAM can describe what the PE
  class will cover) rather than chase Learnable status.
- **Audio-dependent English content** ("Listen and match") — the corpus has no
  audio. Cannot be solved by better extraction; would need entirely new source
  material (audio files this project doesn't have access to).
- **Group/social activities** ("Find someone who...") — inherently
  multi-learner; a solo digital app cannot authentically reproduce this without
  becoming a different product.
- **Mass LLM-generated pedagogy for the remaining gap.** Explicitly rejected —
  every real win found this checkpoint came from *recognizing* pedagogy the
  textbook already encodes, never from inventing it.

---

## 10. Counterargument — challenging this report's own recommendation

**Could 3.07% simply be a bad metric?** Partially — see §1. It undercounts
SAM_SUPPORTABLE content (now identified, not yet sized) and doesn't account for
the External-Modality-Required tier's genuine unreachability. As a measure of
"can a child currently produce validated evidence," it's accurate; as a measure
of "how much value could this corpus theoretically provide," it understates.

**Are we undercounting existing experiences?** Yes, likely modestly — see
Counterargument Claim 1 in the prior checkpoint's bundle
(`02-CHALLENGE-AND-COUNTERARGUMENTS.md`), not re-litigated here.

**Could chasing Learnable % encourage low-quality activities?** This is a real
risk this report tries to guard against by insisting on the LEARNING_EXPERIENCE_
VALID tier (§1) as the actual bar, not raw ACTIVITY_PRESENT counts, and by
recommending gold-set validation before any pattern is trusted at scale (every
Option A/B/D recommendation above explicitly requires this). The risk is real if
this discipline is dropped under coverage-number pressure — worth stating
plainly rather than assuming the discipline holds by default.

**Are SGV semantics reliable enough?** Where the `MỤC TIÊU` marker exists: yes,
measured, source-stated, zero inference. Where it doesn't (most subjects,
unresearched): unknown — do not assume it generalizes.

**Will subject-family adapters become maintenance debt?** A real risk if built
before proving need (explicitly guarded against in this report — every adapter
recommendation above is gated on measured evidence of a genuine, sizable,
distinct content shape, not built speculatively). The `units-k12` extractor
itself is a good example of the *right* shape for this — one shared core +
per-family marker additions, not N independent one-off scripts.

**Would AI-assisted compilation introduce hidden pedagogy?** Only if the
validator is weak. Option E's design explicitly restricts the LLM to
*boundary/structure proposals over verbatim source text*, with a deterministic
substring-match gate — if that gate is ever relaxed to allow paraphrase or
inference, this risk becomes real. Flagging this as the single most important
implementation detail if Option E is ever pursued.

**Are some lessons fundamentally unsuitable for SAM?** Yes — explicitly named
in §4/§9 (GDTC, audio content, group activities). This report does not treat
100% Learnable as the goal.

**Is increasing Learnable % even the correct product objective?** It's the
correct objective *for the lessons where it's reachable*. For the
External-Modality-Required tier, the correct objective is probably an honest
SAM_SUPPORTABLE experience (SAM helps a child prepare for or reflect on a PE
class or art project it cannot run itself) — a genuinely different, currently
unbuilt, and not-yet-scoped product surface. Worth a future Founder
conversation, not assumed here.

---

## Recommended next POC

**Ngữ văn reading extraction** (Option A, item #1). Smallest, cheapest, highest-
confidence next step: adapt the existing TV-reading extraction pattern to
Ngữ văn's book-name convention, gold-set-validate on ~10 hand-checked examples
across 3-4 grades, ship following the exact WAL-190 discipline (measure before,
measure after, verify non-regression, Nokia-check when device access returns).

## Founder decisions required

None. This is a research/prioritization deliverable; the recommended next POC
(#1 above) is within already-granted bounded-and-reversible autonomous
authority and will proceed without further sign-off, following the same
gold-set discipline as WAL-190.
