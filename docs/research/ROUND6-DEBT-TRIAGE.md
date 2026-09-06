# ROUND 6 DEBT — TRIAGE
## WS-R · round 7 · 2026-09-06

> **The rule this document exists to enforce: NOTHING VANISHES FROM THE ROADMAP WITHOUT AN
> EXPLICIT DEFERRAL AND A REASON.** Every item round 6 carried forward — its own PARTIAL /
> DEFERRED / NOT STARTED rows, its STILL HYPOTHESIS list, its named regressions, the two gaps
> WS-D handed back to WS-C, and the recognition report's own hypothesis list — appears in the
> table below with a verdict. An item is allowed to be deferred. It is not allowed to disappear.
>
> **Classification:** `ROUND7-P0` executed this round · `ROUND7-P1` should be done this round by
> its owner · `DEFERRED` with a reason · `REASSIGNED` to a named workstream.
>
> Round 7 has four workstreams (M · T · S · R). Anything needing a fifth is `DEFERRED`, and the
> reason says so rather than pretending an owner exists.

---

## 0 · The one-paragraph answer

Of the five items the Founder named, **four are done and one is answered rather than fixed.**
The 17 missing page crops were not a missing feature: the **only pipeline path that stamps the
full repair chain rendered no crops at all**, so a repaired Golden lesson could have its lineage
or its page images, never both — and the lineage gate read `0/0 crops present · PASS` because it
counted references instead of the population. Both are fixed and the fixture is re-placed with
**17/17**. The Next Action contradiction and the lowercased proper noun were **both reachable by
a test** — the tests that existed had never been shown data that could make them red, which is a
test-population failure, not a strictness failure; both now have tests that go red under
mutation. `si_expected_exponent` was **never abstaining**: on 166 of 171 lines no SI relation is
printed, and on the 5 where one is, the recogniser produced nothing to check. Recognition
generalisation is **not executable this round** — round 7 has no recognition workstream — and is
deferred with a protocol rather than an intention. **No device walk was possible: the Nokia is in
active personal use.**

---

## 1 · The five items the Founder named

### R-1 · 17 lesson gaps with no page crops — **ROUND7-P0 · DONE**

**What a child saw.** LS&ĐL 5 Bài 8 on a real Nokia, round 6, step 09: seventeen cards saying
«Phần này SAM chưa đọc được — con xem SGK trang N nhé» with **no page image**. The card already
knows how to show one (`withheld_card.dart` renders «Xem ảnh chụp trang sách» whenever
`crop != null`). The data never carried a crop.

**Root cause — MEASURED, and it is structural, not an oversight.**

`tool/corpus/repair/tsl_projection.py --lesson-document` is the **only** path that stamps the
full repair chain onto a document (`sourceTslSha256` · `projectedTslSha256` · `ledgerRun` ·
`sourceTslPath` · `ledgerPath` · `generation`). It called `bridge.convert()` with **no `crops=`
argument**, and its own `--help` said so: *«also emit the LessonDocument through the ONE bridge …
No crops.»* The other path, `golden_delivery.py --tsl`, renders 20–22 crops and stamps **no**
repair chain. So round 6 faced a forced choice and chose lineage — correctly. The cost was
seventeen empty gaps, and it was not visible as a choice from inside either tool.

**Second cause, and the one worth keeping.** `fixture_lineage.py` L5 checks *«every crop a block
REFERENCES exists»*. A document that references none has none absent, so it printed
`0/0 present · PASS`. **The gate was green precisely because the thing it guards was missing** —
the same shape as the timeline test round 6 had to correct one layer up.

**Fixed.**

| change | file |
|---|---|
| crops rendered from the **projected** TSL — the same object the document is built from, so a crop cannot belong to another generation | `tool/corpus/repair/tsl_projection.py` |
| `--no-crops` / `--dpi`; `book_meta` defaults to the curriculum structure (closes WS-D's **G2**: `bookTitle` «Lịch sử và Địa lí 5» → «LS&ĐL 5») | same |
| **L5b CROP COVERAGE** — every withheld region carrying `sourceRef.pagePdf` + bbox must carry a crop. FAIL when missing; `--allow-missing-crops` downgrades to UNKNOWN and prints the waiver, never to PASS | `tool/evidence/fixture_lineage.py` |
| **L2b** premise corrected (below) | same |
| `--doc`'s round-6 justification marked EXPIRED — on the integration branch the bridge stamps `provenance.repair` too | `tool/evidence/golden_delivery.py` |

**L2b, corrected not loosened.** L2 had already recorded (round 6 §4.2a) that two hash methods
legitimately coexist — the committed bridge stamps file **bytes**, the repair path stamps
**canonical JSON**. L2b still compared one string to one string, so `golden_delivery --tsl`
(expectation = `canonical or bytes`) **FAILED on a document built from exactly the TSL demanded**:
`recorded=6dc506bc…` vs `expected=d7825280…`, same file. A cross-method match is now accepted
**only when BOTH sides are digests this run recomputed from the file at `tslPath`**, and the row
names which method each side used. One byte of that TSL moves both digests, so no substituted
generation can slip through.

**Verified on the re-placed artefact.**

| | round 6 | round 7 |
|---|---|---|
| withheld regions | 17 | **17** — id set identical |
| withheld regions with a page crop | **0** | **17** |
| crops present beside the fixture | 0 | **22** (17 withheld + 5 figures) |
| figure `ImageBlock`s | 0 (`imagesWithoutCrop: 5`) | **5** (`imagesWithoutCrop: 0`) |
| served **text** blocks | 35 | **35** — no new text |
| withheld blocks carrying `text` | 0 | **0** |
| blocks carrying a repair record | 6, all withheld | **6, all withheld** |
| `provenance.repair.trusted` | 0 | **0** |
| `repair.servable` | all `false` | **all `false`** |
| lineage verdict `--require-repair` | PASS (with L5 vacuous) | **PASS** (L5 22/22, L5b 17/17) |

The projection re-run **reproduces WS-C's round-6 hashes exactly** — `sourceTslSha256`
`c9d2cf1f…`, `projectedTslSha256` `d7825280…` — so this is the same generation, re-derived, not a
new one.

**Reproduce:**

```
python3 -m tool.corpus.repair.tsl_projection \
  --tsl poc-out/round5/lane-c/tc2-lsdl5/v1/root/poc-out/trusted-corpus/tc-v2/tc2-r5/lessons/05-sgk-lich-su-va-dia-li-5/bai-08.tsl.json \
  --ledger poc-out/round5/lane-c/tc2-lsdl5/v1/report/repair-ledger.jsonl \
  --out poc-out/round7/ws-r/golden1/lsdl5-bai08.tsl.json \
  --lesson-document poc-out/round7/ws-r/golden1/lsdl5-bai08.lesson.json
python3 tool/evidence/golden_delivery.py \
  --doc poc-out/round7/ws-r/golden1/lsdl5-bai08.lesson.json \
  --history-rules --verbatim-ledger docs/research/lane-c/data/lsdl5-bai8-verbatim-ledger.json \
  --toc-title "Đấu tranh giành độc lập thời kì Bắc thuộc" --require-repair --place
```

**The test that would have caught it.** `CropCoverageTest` builds the very document round 6
placed — 17 croppable withheld regions, no crops — and asserts **L5 PASS `0/0` and L5b FAIL
`0/17` on the same document**. That gap is what shipped, and if L5b is ever removed the assertion
is what notices. Mutations killed: L5b forced to PASS (3 failures), coverage computed from
references rather than the population (3), L2b accepting any expectation once the TSL is on disk
(5).

**NOT PROVEN: on hardware.** See §4.

---

### R-2 · The Next Action contradiction — **ROUND7-P0 · DONE**

**What a child saw.** LS&ĐL 5 Bài 8: open the lesson, tap 📖 Đọc, and SAM says

> «Con đã đi qua các cách học của bài này. Con có thể xem lại, hoặc về mục lục chọn bài khác.»

directly above

> «Đã mở: ● Đọc ○ Trực quan ○ Học với SAM»

**Two sentences on one screen contradicting each other**, and the upper one tells the child to
leave the lesson they opened one tap ago.

**Root cause — one mistake wearing two faces: a trace of what was OPENED read as evidence of
what was LEARNED.**

1. R5's only evidence is `viewsSeen`, and `WorkspaceTrace.markView` sets it **the instant a tab is
   entered**. This lesson's timeline block is honestly withheld, so it has no `SemanticData` and
   no tutor script — **one** available way of learning. Opening it covered the set, R5 fired on
   the first tap, and R5 concluded *«đã đi qua»* and advised leaving. The file's own header
   already said `viewsSeen` is *«DẤU VẾT UI … không phải bằng chứng»*. The rule read it as
   evidence anyway. `OPENED != OPENED-AND-UNDERSTOOD`.
2. The «Đã mở» row walked `WorkspaceView.values` **unconditionally**, drawing «○» for two ways
   the lesson does not have — inviting a child to hunt for what is not there. The «Vào bài học»
   screen has told the truth since round 3 («Chưa có sơ đồ cho bài này»). This row had not caught
   up.

**Fixed.** R5 now yields `LessonNextKind.keepGoing` («Xem tiếp bài này»), says «đã **mở**» rather
than «đã **đi qua**», states plainly that opening is not understanding, and **never instructs
leaving**. Going back is still one tap on the ← the header always carries — a child's choice, not
SAM's advice. **The only path on which SAM proposes another lesson remains R1,
`hasApprovedValidatedSuccess`** — evidence that has been marked. The «Đã mở» row marks only the
ways this lesson has and **names** the ones it lacks; availability comes from
`LessonSummary.availableViews`, the same source the rule counts, so the two cannot disagree again.

`founderNextAction` now returns `LessonNextAction` instead of flattening to `NextAction`. That
flattening dropped `kind`, and `NextAction.label` has exactly two outcomes — a view, or
«Về mục lục» — which is why «stay in the lesson» was not expressible and the assist layer printed
**«SAM gợi ý: Về mục lục»**. `lib/core/lesson_model/` is WS-S's this round and is untouched.

**Could a test have caught this? YES — and the honest reason none did is a test-population gap,
not a strictness gap.** §6.7's round-4 test pins the exact string
`Đã mở: ● Đọc ○ Trực quan ○ Học với SAM` — but it runs on the **synthetic** fixture, where the
lesson HAS all three ways. The string is correct there, so the test is green forever. **A
one-way lesson had never been put in front of these rules.** It is now.

The load-bearing new test is **structural, not a keyword check** — round 6 established that a
keyword canary fires on real book text and guards nothing. Across **4 lesson shapes × 4 evidence
standings × all 8 subsets of `viewsSeen` = 128 cases, swept not sampled**, no combination may
propose leaving the lesson without a validated, approved success. The on-screen test **counts
●/○ marks against the number of available ways** rather than matching a sentence. Mutations
killed: R5 restored to `backToContents` (3 failures), the row restored to
`WorkspaceView.values` (1).

---

### R-3 · Lowercased historical proper noun — **ROUND7-P0 · DONE**

**Confirmed a display defect, not data.** The fixture's `title` is
«Đấu tranh giành độc lập thời kì **B**ắc thuộc», taken verbatim from the printed TOC by
`lesson-title-v1`. The screen showed «**b**ắc thuộc».

**Root cause.** `LessonDocument.titleCase` lowercases the **whole string** and then re-capitalises
sentence starts. It was written for titles mined IN CAPS («HỖN HỢP. TÁCH CHẤT…», Nokia n1 D1) and
**its precondition was never checked**. A title that already carries lowercase is already
correctly spelled, and lowering it destroys information Vietnamese cannot infer back: «Bắc
thuộc», «Ngô Quyền», «Bạch Đằng» survive only if nothing touches them.

**The correct rule already existed in the repo, in one of seven places.**
`source_sheet._humanCase` guarded on `s == s.toUpperCase()` before casing. Six other display sites
called `titleCase` directly. `lib/core/display/lesson_title.dart` now holds **one** rule; all seven
use it; a source-inspection test forbids a second one.

`document_sequence_rule` no longer builds a presentation at all — it was passing `titleCase`
through the **spec** layer, which `no_presentation_constructor_test` exists to forbid, and whose
import allowlist I deliberately did **not** widen. The casing happens in `visual_view`.

**Why no test caught it.** The existing `titleCase` tests fed it only ALL-CAPS strings — i.e. only
the precondition the transform assumes. A whole-string lowercaser is always green when its input
has no lowercase left to destroy. **Same class as round 6's two failed holdouts: the population
was wrong.** The new test feeds the real title and reads the **rendered text on screen**, and its
invariant is «every uppercase letter of the book's string survives», not «the function returns
string X». Mutation: restoring the round-6 transform turns the on-screen test red.

**Two test premises corrected in place, each saying why.** The synthetic fixture's chapter title
carries a lowercase «(mẫu)» annotation, so it is a mixed-case string and is now shown verbatim —
fail-closed. Real chapter titles are pure caps and still case correctly.

---

### R-3b · The ALL-CAPS residue — **ROUND7-P1 · PARTIAL, Founder decision needed**

**Stated, not hidden.** Where the source is genuinely ALL-CAPS the case information is gone
**before the app sees it**, and sentence-casing it asserts something false about the book's
orthography. On data that ships today:

- `assets/pack/lesson-index-*.json`: **175 of 2,623 titles (6.7 %) are ALL-CAPS.**
- Of those, **67 carry only one letter-bearing word** — «GDTC 5», «GDKT&PL 10», «TN&XH 1». The
  old rule rendered them **«Gdtc 5»**: an acronym destroyed. **Fixed** (a single ALL-CAPS word is
  an acronym and is left alone); it costs «ECOTOURISM» staying loud, which is the cheaper error.
- The remaining **108 multi-word ALL-CAPS titles still lose their proper nouns.** LS&ĐL 5's own
  chapter list is among them: «ĐẤT NƯỚC VÀ CON NGƯỜI VIỆT NAM» renders «… **v**iệt **n**am», and
  the lesson's own pipeline title «THỜI KĨ BẮC THUỘC» renders «Thời kĩ **b**ắc thuộc». Pinned by a
  test so nobody reads this as fixed.

**Two options, both real, and the choice is not mine:**

| option | cost |
|---|---|
| **A** — show an ALL-CAPS source verbatim | 108 shouted titles; nothing false |
| **B** — keep sentence-casing | readable; asserts, 108 times, that a proper noun is not one |

A third path is data, not display: a sourced proper-noun lexicon, or preferring the printed TOC
title (`lesson-title-v1`) wherever one exists — which is exactly what rescued *this* lesson.
**Founder call.**

---

### R-4 · `si_expected_exponent` abstains — **ROUND7-P0 · ANSWERED; two defects fixed; the gap it names is DEFERRED**

Round 6 wrote: *«`si_expected_exponent`, round 5's independent validator, abstained on all 171 …
An independent validator that never fires is not yet an independent validator.»* **Re-derived from
the leaf rows of `exponent.json`, that sentence names the wrong cause.**

| population | count | what it is |
|---|---|---|
| lines printing **no** SI prefix relation | **166** | inapplicable — the correct answer, and not an abstention |
| lines printing one, where the recogniser read **nothing** | **5** | `1 kJ = 10ⁿ J` · `1 MJ` · `1 MW` · `1 GW` · `1 mêgaoát = 1 MW` — all `STILL_BROKEN` at all four scales. **Nothing to check. The validator was never asked.** |
| lines printing a **negative** relation | **1** | `1 nm = 10⁻⁹ m`. Declined **on purpose**: a reading is reported as bare digits and cannot carry a minus, so comparing `9` to `−9` would refuse a correct reading or pass a wrong one |

**Two real defects, both fixed.**

1. `_PREFIXED` was anchored at `^\s*1\s*` while its own docstring promised *«where the page itself
   states the prefix relation»*. **«1 mêgaoát = 1 MW = 10° W» states it** — SI fixes n = 6 — and
   the anchor discarded it, along with a mid-sentence `1 nm = 10 ° m`. Now searched with
   `(?<!\w)`, which keeps exactly the guard the anchor was providing: «21 kJ» and «110°» still
   cannot match. **Applicable rows 4 → 5.** A line stating two *different* relations abstains
   rather than choosing one.
2. `run` recorded `NOT_APPLICABLE` whenever the recogniser produced **no candidate**, whatever the
   line said. So `by_validator {'NOT_APPLICABLE': 171}` **conflated «no relation printed» with
   «nothing to check»** — one bucket carrying two causes, which is exactly how the round-6
   sentence went wrong. `validate` is four-valued now (`NOT_APPLICABLE` · `NO_CANDIDATE` · `PASS`
   · `FAIL`) and every row carries `si_applicable`, the denominator the rate must be read against.

**Should it still abstain?** On the 166, yes — that is correctness. On negative exponents, yes,
until a reading carries its sign. On a mid-line relation, **no**, and that was the bug.

**It remains at 0 PASS and 0 FAIL, and nothing here moves that.** Firing it needs a digit
recovered on one of those five lines, and round 6 measured all five as unreadable at every scale.
**That is a recognition gap → R-5, DEFERRED.** Mutations killed: restoring the `^` anchor (3
failures), folding `NO_CANDIDATE` back into `NOT_APPLICABLE` (6).

---

### R-5 · Recognition generalisation — **ROUND7-P1 · DEFERRED (no owner this round); protocol specified**

**Reason for deferral, stated plainly:** round 7 has four workstreams and **none of them is
recognition**. The work needs the Apple Vision crop harness against the 9.8 GB PDF corpus (hours
of compute, `swiftc` build, `poc-out/` present) and it would overlap WS-M's metric registry. An
item with no owner and no budget is deferred, not scheduled.

**What round 6 actually measured, and why «generalisation» is not yet a measurable word:**

| set | digit recall | why it came out that way |
|---|---|---|
| DEV (tuned) | 0.500 | — |
| SDM | 0.403 | — |
| HOLDOUT-1 (random, grades 2–12) | **0.061** | ~7 of 18 sampled regions are **algebraic** fractions the rule can never read, ~7 are **not fractions at all** |
| HOLDOUT-2 (≥6 detected bar regions) | **0.038** | selected on the detector, so it selected **the detector's own errors** — grades 1–3, column-arithmetic rules, books that teach no fractions |
| HOLDOUT-3 (page text contains «phân số») | **0.181** | the population rule was about **content**, and it is the only one that measured the recogniser |

**The finding is not «recall is low». It is that four of those five numbers have a denominator
containing regions the recogniser is defined to refuse.** A rate whose denominator includes the
out-of-scope population is not a generalisation measure; it is a measure of how the detector was
pointed.

**What would make it measurable — a POPULATION CONTRACT, frozen before the draw, the same
discipline WS-T is applying to the trust bound this round:**

1. **Two denominators, never one.** `DETECTED` (every region the detector emitted) and
   `APPLICABLE` (every detected region that satisfies the recogniser's declared scope — for the
   fraction rule: a numeric stacked fraction). Report recall against **both**, always. Round 6's
   own §9 already reached this conclusion in prose; it was never made a rule.
2. **The scope predicate is code, declared and hashed before the draw**, not a sentence in a
   report. It must be decidable from the crop alone, and it must be able to say `UNKNOWN` — a
   region no rule can classify counts in `DETECTED` and in neither of the other two.
3. **The draw rule, the seed, and the scope predicate's hash are written to an artefact before any
   page is read**, and the scorer refuses a study whose contract file post-dates its readings.
   HOLDOUT-3's rule was fixed before the draw and is the only one that produced a usable number;
   make that structural rather than a habit.
4. **A control set in every draw** — round 6's control sets are what caught the two false
   readings (`7/9 → 7/6`, and `3/(x²−x) → 3/1`). A recall figure without a hand-checked false-
   recognition figure beside it is not reportable.
5. **`APPLICABLE` is established by hand on a sample of the draw, before scoring**, so the
   denominator is not itself a product of the thing under test.

**Under that contract, «generalisation» becomes a falsifiable statement:** *recall on APPLICABLE
regions in an unseen population is within X of DEV's*. Today the honest statement is only:
*measured 0.181 on HOLDOUT-3 against DEV's 0.500, with the applicable denominator unknown.*

**Related items carried with it** — see table rows R-5a … R-5f.

---

## 2 · Full carried-item table

Every row round 6 carried, plus what this round found. **Nothing is dropped.**

### From round 6 §2 — Plan vs Actual

| # | Item | Verdict | Reason / owner |
|---|---|---|---|
| C-1 | Servable structured carrier — `no_carrier:formula` replaces the false `unknown_role:formula`; a **servable** structured kind still deferred | **REASSIGNED → WS-S** | §9 of the round-7 plan is exactly this; needs rendering **and** a Founder trust decision |
| C-2 | Per-block failure mode DONE **scoped**: version skew only; integrity violations still reject the document | **DEFERRED** | Scope is deliberate and fail-closed. Widening it means letting a document with an integrity violation partially load — a trust decision, not an engineering one |
| C-3 | Rich text ACCEPTED AS IS; the page crop is the honest path | **DEFERRED** | Round 7 makes the crop path actually work (R-1). Revisit only if a measured need appears |
| D-1 | Golden #2 Toán Bài 61 | **DEFERRED** | Reassigned by the Founder to WS-A/WS-B in round 6; neither exists in round 7. Blocked on the same trust gate as Golden #1 |
| D-2 | Bài 17 regression: L2 PASS, **L4 UNKNOWN** (no repair in it) | **DEFERRED** | UNKNOWN is truthful — that lesson has no repair to prove. It becomes a real check only when a repair reaches Bài 17 |
| D-3 | Visual grammar bounded POC | **DEFERRED** | Round 6's own 238-lesson forms census says **do not build one yet**. Deferring on evidence, not on capacity |
| D-4 | **G1** — Golden #1 built without crops | **ROUND7-P0 · DONE** | R-1 |
| D-5 | **G2** — long `bookTitle`/`subject` because `poc-out/graph/` was unresolvable in WS-C's sandbox | **ROUND7-P0 · DONE** | Fixed in the same change: `book_meta` defaults to the curriculum structure. «Lịch sử và Địa lí 5» → «LS&ĐL 5» |
| D-6 | **GATE E step 09 FAIL** — 17 gaps with no page image on the device | **PARTIAL** | Data fixed and gated; **hardware re-check not performed** — §4 |

### From round 6 §5 — STILL HYPOTHESIS

| # | Item | Verdict | Reason / owner |
|---|---|---|---|
| H-1 | The R13 rule-order fix generalises past 29 ledgers / 1,878 regions | **DEFERRED** | Whole-corpus run; no accounting workstream in round 7 |
| H-2 | Targeted re-crop generalises past the measured slices (holdout 0.181 vs DEV 0.500) | **ROUND7-P1 · DEFERRED** | R-5 |
| H-3 | `3,650` is the right canonical denominator | **REASSIGNED → WS-M** | Denominator semantics are the metric registry's subject; four Founder rulings still open in `TRUTH-ACCOUNTING-ROUND6.md` |

### From round 6 §9 — regressions and metrics discovered wrong

| # | Item | Verdict | Reason / owner |
|---|---|---|---|
| G-1 | Withheld counts rise (135→144, 124→147, 30→37); over-withhold rates **not comparable** across rounds without saying so | **REASSIGNED → WS-M** | A comparability rule belongs in the Metric Definition Registry, not in prose |
| G-2 | The child loses the timeline on the flagship slice | **DEFERRED — by design** | It returns only with a Founder trust decision on `p039:000`. **This round did not make it servable and must not.** Guarded: injecting a `TimelineSemantic` into the published artefact turns the guard RED (re-verified §3) |
| G-3 | `thresholds/gate.py ALL_GUARDS` was missing `formula_unvalidated` — added | **CLOSED in round 6** | Recorded so it is not re-opened |
| G-4 | `rederive_trust` does not pass `formula_structured` — pre-existing, fail-closed | **REASSIGNED → WS-T** | `tool/corpus/thresholds/**` is WS-T's; fail-closed, so no urgency, but it must not be forgotten |
| G-5 | Engine defect: dispose row's `validation` merged over every candidate; 12/317 round-5 rows read `rejected` where the ruling was `validated` | **CLOSED in round 6** | Fixed forward with a marked historical correction; no published metric changed |
| G-6 | Round-5 corrected served shares are a **lower bound** | **CLOSED in round 6** | Recorded as a historical correction beside the round-5 report |
| G-7 | §16 of the round-5 order was never committed | **CLOSED in round 6** | Now `ROUND5-ACCEPTANCE-CRITERIA.md`; settled tally 8 PASS · 1 PARTIAL · 1 FAIL |

### From the recognition report §10 — its own carried list

| # | Item | Verdict | Reason / owner |
|---|---|---|---|
| R-5a | Corpus/template-assisted recognition (recommended for the Ω class) | **DEFERRED** | No recognition workstream. Ω is **FALSIFIED for the crop lever** (0/22), so this is the only remaining idea and it is unbuilt |
| R-5b | Multi-engine disagreement | **DEFERRED** | Round 5 already measured that both stacks agree on the wrong character. Low expected value, stated |
| R-5c | Geometry-aware recognition — PARTIAL, only the raster superscript-sign guard exists | **DEFERRED** | And note R-5d |
| R-5d | The superscript-sign guard is **calibrated on the same 18 rows and has no holdout** — MEASURED on set, not PROVEN | **ROUND7-P1 · DEFERRED** | This is a *known-unmeasured guard shipping as if measured*. It owes a holdout; folded into R-5's population contract |
| R-5e | 274/336 population: 281 → 234 blocks at recognition level, **0 change in restores** | **PARTIAL, carried** | Round 6's honest negative; the diagnosis is in its §6 |
| R-5f | Block-level repair from recovered digits | **FALSIFIED in round 6** | Recorded, not retried. A recovered digit *adds* an observation where the destroyed one must be *superseded* |
| R-5g | Four unbuilt hypotheses: `ink-accounted-v1` into consensus · «a half crop must hold a number and nothing else» · denominator ink-width check · bigram diacritic candidates unchecked against the page | **DEFERRED** | All four are refusal-side improvements, i.e. they can only *lower* recall and *lower* false recognition. None is safety-critical because the pipeline is fail-closed. Listed so they are not lost |
| R-5h | The two named wrong holdout readings (`7/9 → 7/6`; `3/(x²−x) → 3/1`) | **DEFERRED with R-5g** | The control set is what caught them; keep control sets mandatory (R-5 protocol item 4) |

### Explicitly not mine

| # | Item | Verdict |
|---|---|---|
| X-1 | «Total activities» — 248 / 217 / 161 | **REASSIGNED → WS-M** (round-7 plan §2 §3). Not taken. |
| X-2 | Merge debt — #73/#79, #80–#88, and round 6's five PRs | **REASSIGNED → coordinator** (round-6 report §11). Not taken. |
| X-3 | 118 blocks withheld for want of an app type (`footnote` 64 · `activity` 50 · `option` 4) | **REASSIGNED → WS-S** (round-7 plan §9) |
| X-4 | Production trust threshold | **REASSIGNED → WS-T**. **Nothing in this workstream made withheld content servable.** |

---

## 3 · GATE E — round 6's invariants, re-verified on the re-placed artefact

| invariant | result |
|---|---|
| served set unchanged | **HOLDS** — 35 served text blocks before and after; withheld id set identical; the 5 new blocks are figure `ImageBlock`s carrying **no text**, only a page crop |
| repair records only on withheld blocks | **HOLDS** — 6 of 6 |
| `trusted = 0` | **HOLDS** — `provenance.repair.trusted = 0`, `productionTrustThreshold = null`, every `repair.servable = false` |
| no withheld block carries `text` | **HOLDS** — 0 of 17 |
| honesty guard: inject a `TimelineSemantic` into the **published artefact** | **RED** — `timeline_history_test` and `no_machine_ids_test` both fail |
| honesty guard: serve `p039:000` as a paragraph with its text | **RED** — 7 failures across `timeline_history_test` and `golden1_history_test` |
| honesty guard: stale packs / lesson index | untouched this round; green in the full suite |
| `UNACCOUNTED = 0` | **NOT RE-RUN** — the conservation audit needs a batch of SDM artefacts and belongs to the accounting lane. Nothing in this workstream changes region dispositions: the withheld set is byte-identical and the served set is unchanged, which is the property the audit measures |

**CI:** `flutter analyze` clean · Dart **1,100 passed, 2 skipped** · Python **756 OK, 15 skipped**.

---

## 4 · What is NOT proven — the device

**No device walk was performed, and no frame was captured.**

Read-only check, `192.168.1.3:5555`, Nokia 6.1 (`Plate2_00WW`, Android 10),
`ai.workizen.learningcoach` present alongside `com.workizen.tongtai`:

```
mCurrentFocus = com.ss.android.ugc.trill/…SplashActivity     ← a third-party media app
mWakefulness  = Awake
mHoldingDisplaySuspendBlocker = true
foreground unchanged across an 8 s re-poll
```

**The phone is in active personal use.** The idle check that could have cleared it is a per-pixel
screenshot comparison, and screenshotting a third-party media app captures personal content that
the device protocol forbids retaining. So the honest position is: **no input injected, no APK
installed, no screenshot taken, and R-1 is PROVEN at the artefact and PARTIAL at the device.**

**Widget tests are not real-device evidence.** What remains unproven on hardware is exactly
round 6's GATE E step 09: that a child opening LS&ĐL 5 Bài 8 sees «Xem ảnh chụp trang sách» on a
withheld card and that tapping it shows the printed page. When the device is free:

1. re-check the foreground read-only, then the per-pixel idle check;
2. **rebuild the packs before building the APK** — stale packs shipped 41 fabricated expressions
   in round 5;
3. `adb install -r` (never uninstall — the Founder's «Na» profile must survive);
4. open the lesson, tap a withheld card's «Xem ảnh chụp trang sách», capture to
   `~/Desktop/wal-evidence/round7-ws-r/`;
5. confirm the header reads «Bài 8 · Đấu tranh giành độc lập thời kì **B**ắc thuộc» (R-3) and
   that the «Đã mở» row reads `Đã mở: ● Đọc · Bài này chưa có Trực quan, Học với SAM` with no
   «Về mục lục» suggestion above it (R-2).

---

## 4.1 · ⚠ A TRAP FOR WHOEVER COMPOSES THIS ROUND

`assets/fixtures/` is gitignored, so **the fixed Golden #1 does not travel with this branch.**
The main checkout still holds round 6's crop-less copy. Rsyncing `assets/fixtures/` from it — the
standing procedure for composition — **re-introduces the defect this workstream fixed**, and the
fixture will read as current because its lineage fields are all intact. That is round 5's stale-
fixture trap wearing a new hat.

It cannot pass silently any more: **L5b goes FAIL on the stale copy** (`0/17 have a crop`). But do
not rely on noticing. **Regenerate rather than rsync**, with the two commands in §1, and check the
line `L5b … 17/17 have a crop` before building any APK.

---

## 5 · Hand-offs — changes another workstream must make

| # | Change | Owner | Why it is not made here |
|---|---|---|---|
| HO-1 | `LessonDocument.titleCase` still lowercases whole strings. It is now **unused outside its own file** and guarded by a source test, but it should delegate to `displayTitle` or go. One line | **WS-S** | `lib/core/lesson_model/**` is WS-S's this round |
| HO-2 | `NextAction.label` returns «Về mục lục» whenever `view == null` — the string that reached the child. The workspace no longer uses it; the prototype `nextActionFor` still does | **WS-S** | same file |
| HO-3 | `rederive_trust` does not pass `formula_structured` (round 6 §9) | **WS-T** | `tool/corpus/thresholds/**` |
| HO-4 | Metric comparability rule for withheld/over-withhold rates across generations (G-1), and the `si_applicable` denominator introduced in R-4 | **WS-M** | `tool/metrics/**`; both are registry entries |
| HO-5 | The 5 figure `ImageBlock`s recovered by R-1 mean the Golden lesson now renders 5 SGK figure crops. **INTERNAL / RESEARCH ONLY (Founder D4)** — they must never be distributed | **coordinator** | Noted so the licensing gate sees it |

## 6 · New debt this round created or discovered

| # | Item | Status |
|---|---|---|
| N-1 | `golden_delivery.py --doc` still renders no crops of its own; it now merely **refuses to place** a crop-less document (L5b). The clean design is one path — `tsl_projection --lesson-document` — and `--doc` should probably be retired | **ROUND7-P1**, not done: retiring a flag mid-round while other workstreams may use it is worse than the flag |
| N-2 | `tool/evidence/**` and `tool/corpus/repair/**` have **no round-7 owner**. I changed both to execute R-1 | **flagged to the coordinator** |
| N-3 | The two hash methods (bytes vs canonical JSON) still coexist. L2b now reconciles them **for the same file**; nothing has decided which is canonical | **ROUND7-P1 → WS-M**, a version-identity question |
| N-4 | 108 multi-word ALL-CAPS titles still lose proper nouns (R-3b) | **Founder decision** |

---

**DO NOT MERGE. READY FOR FOUNDER REVIEW.**
