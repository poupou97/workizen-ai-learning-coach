# 00 · START HERE — Round 7 in five minutes

> **HỌC CÙNG SAM — ROUND 7 RETROSPECTIVE ARCHIVE**
> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.** This archive contains **22 verbatim SGK page
> crops** and a lesson fixture built from SGK text, under Founder rule **D4**. See the status
> legend below: some of it is **LICENSING-DISTRIBUTION BLOCKED** even internally-onward.

| | |
|---|---|
| **ROUND** | 7 — *TRUST GATE CALIBRATION + FIRST TRUSTED SLICE* |
| **DATE CLOSED** | **2026-09-06** (consolidated report dated 2026-09-06; final commit `74d9db6`; PRs #94–#97 all opened and CI-green the same day; calibration frozen 06:41:54Z / 06:47:21Z) |
| **NORTH STAR** | **TRUSTED CONTENT REACHES THE LEARNER WITHOUT LOWERING THE EVIDENCE BAR** → **not reached — and the round proved *why*, which is the result** |
| **GATES** | **A METRIC TRUTH PASS · B TRUST CALIBRATION PASS · C BLIND VALIDATION PASS · D TRUST DELIVERY — PREPARED, UNACTIVATED (by design) · E NO REGRESSION PASS** — graded independently in §11 |
| **VERDICT (archive builder)** | **THE GATE IS BUILT, AND THE ANSWER IS THAT CALIBRATION WAS NEVER THE BLOCKER** |
| **MERGE STATUS** | **NOTHING MERGED. NO THRESHOLD ACTIVATED.** #94–#97 open and CI-green; **every PR from #73 to #93 also still open** *(PROVEN — GitHub API)* |

---

## THE STATUS LEGEND — three ways a claim can be true, and they are not interchangeable

Every claim in this file and in `06-PRODUCT-REALITY.md` carries one:

| Label | Meaning |
|---|---|
| **[TV] TECHNICALLY VALIDATED** | Measured, re-derivable, and verified in an artefact or by a committed command. |
| **[HU] HARDWARE UNVERIFIED** | True in the artefact; **no device walk happened.** Widget tests and lineage gates are **not** real-device evidence. |
| **[LB] LICENSING-DISTRIBUTION BLOCKED** | Verbatim SGK page imagery. Fine for internal validation; **not distribution-ready**, under D4. *«TECHNICALLY POSSIBLE ≠ DISTRIBUTION RIGHT.»* |

---

## WHAT REACHED THE CHILD: **NOTHING**

**Round 7 activated nothing.** No threshold was applied, no content was admitted, `trusted` is
still **0**, and **not one block changed on any screen.**

The three things that *would* have reached a child are each blocked by a different wall:

| | Status | Why it did not reach a child |
|---|---|---|
| The 17 lesson gaps now carry **page crops** | **[HU]** | The artefact passes all eight lineage checks including **L5b 17/17** *(PROVEN — the archive builder re-verified 17 of 17 from the bytes)*. **But no device walk happened**, so nobody has seen a child's screen show «Xem ảnh chụp trang sách». |
| The 22 page crops + 5 recovered figure images | **[LB]** | Verbatim SGK page images. **Internal validation only.** |
| The «Về mục lục» contradiction and the lowercased proper noun | **[HU]** | Fixed in code, mutation-tested — **not proven on a device.** |

### PARENT: **NOTHING NEW.** SAM: **NOTHING NEW.**

---

## THE ROUND'S REAL RESULT — and it is a measurement, not a shortfall

> **All twelve teaching-critical errors in the served set reduce to exactly two mechanisms —
> digit corruption (6) and a non-question served as a question (6) — and neither is visible to
> any signal a gate can read.** **[TV]**

- **Three of the six digit corruptions survive character-exact agreement between two independent
  OCR stacks**, plus the role-confidence floor, the figure refusal, the order check and the
  subject exclusion. **They pass everything.**
- **No combination of available signals bounds teaching-critical error below ≈0.021** at any
  coverage. The strictest principled stack reaches 0.0233 at 36 % of served; the best reaches
  **0.0213 at 53 %**.
- At that rate and the **30 trusted blocks** a real lesson delivered in round 6,
  **P(a lesson carries ≥1 teaching-critical error) ≈ 0.48** — *about half of all lessons* — under
  an **assumption of independence** that is stated, not hidden.
- The gap between what any threshold achieves (**≈0.021**) and what a 90 %-clean-lesson promise
  requires (**0.0035**) is **a factor of six**.

> **THE BLOCKER IS RECOGNITION AND ROLE DISAMBIGUATION, NOT CALIBRATION.** Round 7 built the
> trust gate correctly and then measured that the gate was never the thing in the way.

---

## TOP COMPLETED ITEMS

1. **The order is provable by artefact, not asserted.** An append-only hash chain: `seq 1` policy
   `0dfc5032…`, `seq 2` population `dbadf4ad…`, `seq 3` population `69d1cacc…`, both populations
   binding the policy hash. **No `approval` entry. No `admitted` entry.** *(PROVEN — the archive
   builder read the ledger: three lines and no more.)* **[TV]**
2. **And it refuses, rather than discourages.** An `admitted` write with no recorded approval is
   **refused with a `PermissionError`** — confirmed adversarially by the coordinator. **[TV]**
3. **`TRUST = SERVED ∩ admit(…)`.** `trusted ⊆ served` holds *by construction*, so **activation
   cannot serve one new block**; round 6's byte-identical served set survives it and no waiver can
   manufacture trust. Property-tested. **[TV]**
4. **Zero lesson or book identities in any of the three calibration documents** *(PROVEN — 0
   identity-shaped matches in all three)*. The frozen **populations** do name their 120 lessons
   each, with titles hashed — that is the evaluation frame, frozen before anything could be
   admitted, and §3 of `05-METRICS` states the distinction exactly. **[TV]**
5. **GATE A: 18 metrics, 18/18 re-derive** from leaf records by committed command. **«Total
   activities» is resolved by deprecation** — 248 SUPERSEDED (a correct earlier value of
   `ACTIVITY_LEAF_COUNT`), **217 DEPRECATED** (a sum of two different units), **161 DEPRECATED**
   (three of seven families under a whole-corpus name, silently dropping 87 rows). **[TV]**
6. **A servable type is recommended for ZERO of the 118 blocks**, and **114 of them gain nothing**
   — exactly one structural group across 238 lessons contains a gap block. **The real lever is the
   all-or-nothing sibling rule: 31 mutilated structures → 0, at 72 blocks.** Adding all three types
   removes **1 of 31**. **Built and deliberately not switched on.** **[TV]**
7. **Golden #1 regenerated with 17/17 crops and 5 recovered figure images**, `validatedRepairs 9 ·
   trusted 0 · 0 served blocks carrying a repair`, all eight lineage checks PASS — and the
   **withheld id set and served-text id set are byte-identical to round 6** *(PROVEN)*. **[TV]** /
   **[HU]** on the device / **[LB]** for the crops.
8. **The round composes:** 4 branches, **0 conflicts**, `flutter analyze` clean, **866 Python**,
   **1106 Dart** — with the Golden fixture **regenerated inside the composed tree, never rsynced.**

---

## TOP FAILURES AND DISCOVERIES

1. **The option letters «A.»–«D.» are restored *after* `agreement()` runs.** `text_sim = 100.0`
   certifies «Kim loại và phi kim» and says **nothing about the «A.»**. **On a multiple-choice
   question the letter *is* the answer's identity, and it is precisely the part no agreement
   measurement covers.** *(PROVEN from the artefact and the source order.)*
2. **Every multiple-choice group in the canonical corpus is mutilated. There are two, and both are
   broken.** One is mutilated **by the type gap itself** — a served question whose four answers are
   blank cards, followed by «Hãy chọn đáp án đúng nhất.»
3. **Adding the `option` type would convert a LOUD mutilation into a QUIET one** — today four blank
   cards are visibly wrong; with the type, the day a threshold withholds one option the app serves
   **a three-option question that looks complete.** *The type does not remove the danger; it removes
   the evidence of it.*
4. **22 imprint blocks reach children today** as `heading` (17) and `body` (5) — **defect 6 is open
   on the lesson path.** This does **not** contradict round 6's «absent (0 of 207)»: Lane D measured
   the **pack** surface, WS-S the **lesson/TSL** surface. **Both true; neither may be quoted without
   naming its surface.**
5. **The title decision, measured rather than argued.** 2,623 titles / 2,382 unique · **108
   multi-word ALL-CAPS** — the Founder's figure exactly · the candidate normalisation strips
   capitals from **107 of 107** · `displayTitle` changes **0 of 2,382**. Named casualties from the
   shipping pack: `ASEAN AND VIET NAM` → `Asean and viet nam`, `BÁC HÔ VỚI THIÊU NHI`, `… THẾ KỈ XX`
   → `… thế kỉ xx` — **an acronym, a person's name and a Roman numeral.** The precondition is **a
   function, not a promise**. The cost is stated plainly: **«MỞ ĐẦU» now reads «MỞ ĐẦU» on screen.**
6. **A gate was green because the thing it guards was absent.** `fixture_lineage` L5 counted crop
   *references*, so a document with none printed **`0/0 present · PASS`**. Round 6 shipped through
   it. Fixed by **L5b**, which measures the *population*.
7. **Three of the coordinator's own statements falsified** — «the cheapest win on the board» (never
   re-derived); «DIGIT LOSS 312 (57 %)» published **without its denominator, 548**; and a first
   re-derivation that used field `number` instead of `no` and returned 238 / 3,497.
8. **Two workstreams withdrew their own claims** — WS-T its clustering finding (a second derivation
   showed the disagreement did not exist: 0.0975 expected vs 0.1026 observed), WS-S its first
   anchor count (22 → **10**; footnotes were anchoring each other).
9. **The repository contains no pre-existing blind population.** A3's published curve **pooled all
   643 rows including the 181 marked `held_out`**. Pooling them spent them. **[TV]**
10. **`si_expected_exponent` was never abstaining** — on 166 of 171 lines no SI relation is printed,
    and on the 5 where one is, the recogniser produced nothing to check. **The validator was never
    asked.** Two real defects fixed; **it remains at 0 PASS / 0 FAIL, and nothing here moves that.**

---

## KEY METRICS

| Dimension | Round 6 | Round 7 |
|---|---|---|
| SOURCE REALITY | 97 | **97** |
| **SOURCE TRUST** | 0 / 97 | **0 / 97 — and now measured as unreachable by calibration alone** |
| RECOGNITION REALITY | 17/47 on Bài 61 | **unchanged — no recognition workstream** |
| REPAIR REALITY | 9 validated · 6 crossed · 0 trusted | **unchanged + 17/17 crops restored** |
| PEDAGOGY REALITY | 7 / 17 | **7 / 17** |
| EVIDENCE REALITY | 0 of 0 | **0 of 0** |
| **PRODUCT DELIVERY REALITY** | 1 real lesson, minus its timeline | **unchanged — nothing new reached a child** |
| Teaching-critical error, best achievable bound | not measured | **≈0.021** (needed: 0.0035) |
| Metrics re-deriving from leaf records | — | **18 / 18** |
| Mutilated structures served today | not measured | **31** (2 of 2 MCQs) → **0** under the unswitched rule, at 72 blocks |
| Merge debt | 208 commits | **259 commits, four stacked layers** |

---

## NEXT BOTTLENECK — **RECOGNITION AND ROLE DISAMBIGUATION**

Round 7 **measured** it rather than assuming it. Calibration is finished, and it is not the answer.

## NEXT ROUND NORTH STAR

**Round 8 — MAKE THE TWO TEACHING-CRITICAL MECHANISMS VISIBLE TO A GATE.** Target:
teaching-critical error **below 0.0035 on the frozen blind population, or a measured statement that
it cannot be.** **Dependencies: none — the populations are already frozen. No Founder decision
needed to start.** Stop condition: if no signal separates them, **report it and leave the gate
unactivated — a truthful zero, again.**

---

## MERGE RECOMMENDATION

**Unchanged and now more urgent: MERGE #79 · CLOSE #73 AS SUBSUMED · HOLD the rest.**

Re-verified first-hand: #73 **is** still an ancestor of #79, `main` **has not moved** (`61dbfdb`),
and the delta is still **16 commits across 3 files, all `docs/research/`**. *(PROVEN.)*

**The stack is now four layers deep and 259 commits ahead of `main`** — *(the report says 254;
that was measured four documentation commits earlier. Same stack, later measurement point.)*

- **No CI ever builds what the Founder would merge.** Only the disposable composition builds the
  whole, and round 6 proved that gap is not theoretical.
- **Bisect is compromised** across 259 commits and four merge fronts.
- **`main` is ~4 rounds stale** — it predates silent-loss accounting, the repair framework,
  recognition and the honest Bài 8 fixture.

**If the Founder prefers integration branches to stay permanently unmerged, that is legitimate —
but it should be stated as policy**, because at four layers they no longer function as a delivery
path.

## FOUNDER DECISIONS REQUIRED

| # | Decision | Why it blocks |
|---|---|---|
| **1** | **Approve a calibration candidate and bound — or decline and keep the truthful zero.** Recommendation: **C2 · PROSE under BOUND-2**, whose **own predicted outcome is a truthful zero, sealed inside the frozen payload so it cannot be revised after the fact.** | **BOUND-4 is the only passable bound, and its consequence — 45 % of lessons carrying a teaching-critical error — is «not sayable to a parent».** If a non-zero result is required, the only honest route is **BOUND-5: per-lesson certification of a bounded slice — which is not a threshold and must never be reported as one.** |
| **2** | **The all-or-nothing sibling rule: switch it on?** | **31 mutilated structures → 0**, at the cost of **72 blocks a child reads today.** The same shape of trade as round 6's lost timeline, and the same person's decision. |
| **3** | **ALL-CAPS titles (R-3b): show verbatim, or keep sentence-casing?** | **A** — 108 shouted titles, nothing false. **B** — readable, but asserts 108 times that a proper noun is not one. A third path is data, not display. |
| **4** | **Canonical lesson identity — choose a grouping key.** | Now a **definition** decision, not a data conflict: 3,679 rows · 3,240 `(doc,no)` · **3,650** `(doc,no,pageStart,title)` · 3,381 with `pageStart` are **one leaf population under four keys**. `3,240` **deletes 410 real lessons**. |
| **5** | **Merge debt** — merge #79, close #73? Or state the no-merge policy? | Four layers, 259 commits. |
| **6** | **Defect 6 on the lesson path** — 22 imprint blocks reach children today. | A pipeline lesson-boundary fix, and the precondition for `ActivityKind.activity`. |
| **7** | **When may the device be walked?** | R-1, R-2 and R-3 are all **[HU]** and cannot be closed without it. |

---

### How to read this archive

`01`–`05` are the record; `06`–`09` the reality; `10`–`14` forward-looking; `15` the file manifest
with a SHA-256 per file.

**Claim labels:** **PROVEN** = re-verified first-hand by the archive builder · **MEASURED** = an
instrument's number in a committed report the coordinator verified · **OBSERVED** = seen on a real
device or a page render · **INFERRED** · **HYPOTHESIS** · **UNKNOWN / NOT CAPTURED / UNAVAILABLE**.
These sit *alongside* the three-way status legend above: a claim can be **PROVEN** and still be
**[HU]**, and R-1 is exactly that.
