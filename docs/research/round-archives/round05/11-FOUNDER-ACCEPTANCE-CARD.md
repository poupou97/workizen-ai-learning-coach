# 11 · FOUNDER ACCEPTANCE CARD — round 5's original gates, graded

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

**The gates below were fixed before the results were known and are not redefined here.**

---

## 0. A PROVENANCE PROBLEM, STATED FIRST

**The text of the round-5 master order — including its §16 — is NOT IN THE REPOSITORY.**
*(Searched: `docs/**` for `§16`, "success criteria", "acceptance", "master order", "tiêu chí
thành công". The only acceptance-gate list committed anywhere is round **6**'s, in
`ROUND6-PLAN.md`.)* The master order was issued to the agents conversationally; what was committed
is `ROUND5-PLAN.md` (lane ownership + the North Star + standing limits) and
`ROUND5-AUDIT-97-EVALUATION-SET.md` (the five directions + the eight named defects + the two added
P0s).

**Consequence, stated rather than papered over.** The ten criteria in §1 below are a
**RECONSTRUCTION** — assembled from the two committed round-5 objective documents plus the two
criteria the Founder named by number when commissioning this archive (**criterion 4** = *correct
served / coverage begins to recover*; **criterion 5** = *role taxonomy + agreement*). Each is
labelled with the committed source it comes from. **They are marked INFERRED as a set**, and any
mismatch with the original §16 wording should be resolved in the Founder's favour, not the
archive's.

**What is *not* reconstructed:** every grade below is argued from evidence that is in this
archive, and the **five Founder directions in §2 are quoted verbatim from a committed file** —
that table needs no reconstruction at all and is the more reliable of the two.

**This gap is itself a finding.** The workspace root `CLAUDE.md` warns that stale or missing
doctrine "blocks as hard as a real gate, and no test catches it". A round's acceptance criteria
should be committed with its plan. **Round 6 already does this** — `ROUND6-PLAN.md` carries five
named gates (A–E) in the repository. Recommend making that permanent.

---

## 1. THE TEN CRITERIA — RECONSTRUCTED — graded

| # | Criterion *(reconstructed)* | Source it is reconstructed from | Verdict | Evidence |
|---|---|---|---|---|
| **1** | **The repair framework exists and is exercised.** `DETECT → REPAIR candidate → VALIDATE → RESTORE or WITHHOLD`, with a plugin registry, a repair ledger, and the seven data-version dispositions. **A repair is never trusted by default.** | `ROUND5-PLAN.md` North Star + lane A1 | **PASS** | `tool/corpus/repair/**` built (A1, #83); A2 registered a **repairer** plugin; A4 registered **five signal** plugins; Lane C ran the loop to a correct **WITHHOLD** when two signals objected to a candidate. Data versioning held: no source observation overwritten; OLD baseline reproduced three times. |
| **2** | **The third-signal layer is built and each signal's contribution is measured, including false-correction rate.** | `ROUND5-PLAN.md` lane A1 ("measure precision, recall and **false-correction rate** per signal") | **PASS** | A4 (#88): per-signal detection recall / correction precision / **false correction rate** / proposals per 1,000 clean tokens; an 8-signal × 6-case matrix; router human-review **0.0900** over 1,200 real blocks; explicit verdicts on which signal earned a place, including **two negatives kept with their evidence**. |
| **3** | **Vietnamese fidelity: the Founder-named tone defects become evaluation cases and are measured with a holdout.** | `ROUND5-AUDIT-97…` defects 2–5 + the added P0 | **PASS** | Defects 2, 3, 5 detected and correctly proposed by cross-corpus (strict FCR **0.063**, proper-noun FCR **0.000**); defect 4 «Cộng hoà» **correctly abstained** and the abstention asserted as a test — the corpus writes that error **358× across ≥5 books**. Injection holdout = **480 rows / 6,554 tokens from a held-out book**. A1's own gold-set measure: coverage **0.551 → 0.577 with false trust unchanged**. |
| **4** | **CORRECT SERVED ↑ — coverage begins to recover, *without loosening a guard*.** | `ROUND5-PLAN.md`, verbatim: "Coverage must begin to recover **without loosening a guard**"; direction 3 of the five | **FAIL** | As reported, 221 → **239 served**. **Corrected for R13 silent loss it FELL**: 0.632 → **0.589** (evaluation set), 0.613 → **0.523** (holdout), **0.211 → 0.078** on Toán 4 tập hai Bài 61. The only coverage that did recover came from **loosening a guard**, and it was **wrong (0/1 = 0.000)**. **Clear FAIL on both halves of the criterion.** |
| **5** | **Role taxonomy written (20 roles × 8 fields) and inter-annotator agreement re-measured.** | `ROUND5-PLAN.md` lane A3, §7 §8 | **PARTIAL** | Spec **delivered** in full, plus four holes in the pipeline's role map it exposes; re-annotation run. **But: the result is in-sample** — the spec was written after reading the rows, and A3 says so: «κ = 1.000 on decided rows … is arithmetic, not evidence». The settling measurement (**fresh seed, blind, two annotators given only the spec**) **was not run**. Meanwhile the pipeline's own role error moved **the wrong way, 0.116 → 0.151**, and applying the spec **would raise** the measured rate further. Three questions go unanswered to the Founder. |
| **6** | **A trust-gate sensitivity analysis producing a trade-off curve — never a chosen point.** | `ROUND5-PLAN.md` lane A3, §8, verbatim: "a **trade-off curve**, never a chosen point" | **PASS** | `tool/corpus/thresholds/**` + **25 unit tests** + `THRESHOLDS.example.json`; three planes measured; the extractor **reproduces the published baseline page by page and raises if it drifts** (643 blocks · 354 served · coverage 0.5505 · FTR 0.0734). **No threshold was set** and `THRESHOLDS.json` was deliberately not created. |
| **7** | **STEM expression accuracy: establish at which stage the error is born *before* proposing architecture; then a bounded validated POC.** | `ROUND5-AUDIT-97…` new P0, verbatim: "**Do not assume a new architecture is needed**" | **PASS** | The audit came first and **located the defect at OCR recognition**, not normalisation — the raw OCR line already reads `c = 3.10° m/s` and **no downstream step rewrites it**. Then the bounded POC: canonical AST, **six deterministic validators**, detection precision **1.000** / recall **0.955**, **10/10** restores (**8/8** holdout), fabricated **2 → 0**, physics false trust **−3 at zero over-withhold cost**. |
| **8** | **Legacy packs rebuilt under snapshot discipline: snapshot first, OLD baseline stays reproducible, `verify` PASSes after, a representative delta audited — and RESTORE PRECISION measured on legacy batches by failure class.** | `ROUND5-PLAN.md` lane D, §9 §13 | **PASS** | `verify` **0/12 FAIL → 12/12 PASS**; OLD baseline reproduced **three times**, field for field; content delta **exactly zero** (248/248, 12/12 hashes), byte-compared **independently of the tool**; blind badge audit **27/27**, with the unjudgeable rows reported as **unmeasurable rather than as 0.964**; restore precision measured and **separated by mechanism**. Snapshot discipline is **enforced in code**. *(R15 is a discovery this criterion surfaced, not a failure of it — it is graded as an open risk, §10.)* |
| **9** | **History stays bounded: continue LS&ĐL 5, keep the rules PROPOSED and History-only, keep falsifying.** | `ROUND5-PLAN.md` lane C, §11, verbatim: "**PROPOSED/bounded**, never universal K-12 rules" | **PASS** | Bounded to one book. Both rules stayed **PROPOSED**; **nothing entered the universal bridge**. The lane **falsified its own round-4 rule** — 112 date mentions in 8 forms, the rule accepts 1, extracting 3 events across 28 lessons: *a Bài-8 shape, not a History rule*. Bài 8 ledger: false trust **8 → 6**, correct served **26 → 30**, false withheld **14 → 10**. |
| **10** | **Experience: Visual Learning reaches the concept board; walk the real device; report the five product scores separately, never averaged.** | `ROUND5-PLAN.md` lane B, §12 | **PASS** | Trực quan **70–80 % → 85–90 % — reached the board**. Real Nokia 6.1: **5 iterations, 36 frames, 28 steps, 0 downgraded**, **5 device-found defects fixed and re-walked**. Five scores reported separately and **not averaged**; four are honestly flat, with the structural reason named. |

### TALLY — **8 PASS · 1 PARTIAL · 1 FAIL**

**Failed:** criterion **4** (correct served / coverage recovery). **Partial:** criterion **5**
(role taxonomy + agreement). Both match the Founder's own reading.

### Reconciling with the Founder's tally of **7 PASS · 1 PARTIAL · 2 FAIL**

The archive builder's independent grading agrees on the two the Founder named and differs by
**one criterion it cannot see**, because §16 is not in the repository.

**The most likely reconciliation, and it is a real FAIL either way:** if §16 grades
**OVER-WITHHOLD ↓** as a criterion of its own — it is one of the Founder's five stated directions
and it **moved the wrong way, 0.400 → 0.633** — then that is the second FAIL, and one of the
capability criteria above (most plausibly criteria **1 and 3**, which §16 may have carried as a
single "repair framework + Vietnamese fidelity" criterion) collapses into one. **That gives
exactly 7 PASS · 1 PARTIAL · 2 FAIL.**

**The archive does not adopt the Founder's tally by assertion.** It records both, states the
one grade it could not verify, and grades the five directions verbatim in §2 — where
over-withhold is unambiguously a **FAIL**.

---

## 2. THE FIVE FOUNDER DIRECTIONS — verbatim from a committed file, graded

> «Not just `FALSE TRUST ↓`, but simultaneously: **FALSE TRUST ↓ · TEACHING-CRITICAL ERROR ↓ ·
> CORRECT SERVED ↑ · OVER-WITHHOLD ↓ · RESTORE PRECISION ↑**»
> — `docs/research/ROUND5-AUDIT-97-EVALUATION-SET.md` *(committed — no reconstruction)*

| Direction | Result | Verdict |
|---|---|---|
| **FALSE TRUST ↓** | 0.619 → **0.318** vs OLD on batch 2; **10 of 13** of batch 1's false-trust rows no longer served as before (was 7/13); Bài 8 false trust **8 → 6**; two fabricated math expressions → **0**; physics false trust **−3 blocks**; 41 geometry-rebuilt expressions stopped shipping as if printed | **PASS** |
| **TEACHING-CRITICAL ERROR ↓** | 0.476 → **0.100** [0.043, 0.214]; 2 of 5 closed | **PASS** — *but 9 and 13 mutilated structures are unchanged on the lesson path* |
| **CORRECT SERVED ↑** | as reported 0.632 · **corrected 0.589**; holdout **0.523**; Bài 61 **0.078** | **FAIL** |
| **OVER-WITHHOLD ↓** | 12/30 = 0.400 → **19/30 = 0.633** [0.455, 0.781] | **FAIL — moved the wrong way** |
| **RESTORE PRECISION ↑** | **measured for the first time**, and it splits by mechanism: guard relaxation **0/1 = 0.000** · verdicts transferred **3/6 = 0.500** · **validated repair 10/10 = 1.000** (holdout **8/8**) | **PARTIAL** — there is no round-4 baseline to raise it *from*; the mechanism-level answer is the finding |

**Five directions: 2 PASS · 1 PARTIAL · 2 FAIL.**

---

## 3. THE STANDING LIMITS — all seven held

*(See `07-TEST-CI-PR-EVIDENCE.md` §5 for the evidence per limit.)*

no production trust threshold ✔ · no mass corpus reprocess ✔ · no public SGK distribution ✔ ·
no unrestricted LLM ✔ · no major architecture fork ✔ · no destructive migration ✔ ·
**no merge ✔** *(PROVEN — 10 PRs open, `mergedAt: null` on all ten)*.

---

## 4. THE ARCHIVE BUILDER'S RECOMMENDATION TO THE FOUNDER

**ACCEPT the round as research; hold the nine lane PRs (#80–#88); clear the governance debt
separately as round 6's Part II audit recommends; decide the six items in `00-START-HERE.md`.**

The reasoning in one paragraph: round 5 delivered the capability it was asked for and produced a
decisive negative result on the alternative. Three of the five directions moved the right way and
two did not — **and the two that did not are the two that a connected repair path would move.**
Merging the **lane** work today would ship a laboratory that cannot reach the product, on
denominators R13 has shown to be wrong, with pack machinery whose attach provenance does not
reproduce, and three of the nine branches touch code round 6's workstream A is changing right now.
None of that argues for discarding the work; all of it argues for round 6 answering it first —
which is exactly what `ROUND6-PLAN.md` sets out to do.

**On the merge debt specifically, this archive endorses round 6's Part II audit**
(`reports/ROUND6-MERGE-DEBT-AUDIT.md`, produced after round 5 closed): **merge #79, close #73 as
subsumed, hold #80–#88.** #73 is a strict **ancestor** of #79 and the whole delta is
documentation — 16 commits, 3 files, all under `docs/research/`, **zero code, zero tests, zero
assets** — so merging #79 carries exactly the code risk of #73, which the Founder has already
accepted. It also **changes no APK**: packs are gitignored build artefacts. It clears governance
debt and delivers nothing. **The archive did not act on this. Merging is a Founder gate.**

**One process change worth making permanent regardless:** commit the round's acceptance criteria
with the round's plan. Round 6 already does. Round 5's did not, and this file had to reconstruct
them.
