# ROUND 7 — TRUST GATE CALIBRATION + FIRST TRUSTED SLICE
## Consolidated Founder report — 2026-09-06

> **North Star: TRUSTED CONTENT REACHES THE LEARNER WITHOUT LOWERING THE EVIDENCE BAR.**
>
> **CALIBRATION BEFORE ACTIVATION.** The round stops at the trust-activation Founder gate.
> **No threshold was activated. Nothing was merged.** Every number here was verified by the
> coordinator against the repository, an artefact, or by running the suites — not relayed.

---

## 0 · The one-paragraph answer

**We cannot yet call any content trusted, and the reason is not the threshold.** All twelve
teaching-critical errors in the served set fall into exactly two mechanisms — digit corruption
and a non-question served as a question — and **neither is visible to any signal a gate can
read.** Three of the six digit corruptions survive **character-exact agreement between two
independent OCR stacks** plus every other clause. No signal combination bounds teaching-critical
error below **≈0.021**; at the 30 trusted blocks a real lesson delivered in round 6, that is
**about half of all lessons carrying one**. The gate was built correctly, frozen honestly, and
**the answer it returns is a truthful zero** — the blocker is **recognition and role
disambiguation, not calibration.**

---

## 1 · Acceptance gates — fixed before the round, graded after

| Gate | Requirement | Verdict |
|---|---|---|
| **A · METRIC TRUTH** | No ambiguous major metric; critical totals re-derivable from leaf records | **PASS** |
| **B · TRUST CALIBRATION** | Threshold and bound frozen **before** admitted lessons are inspected | **PASS — provable by artefact** |
| **C · BLIND VALIDATION** | Audit machinery exists, proven on a dry run admitting nothing | **PASS** |
| **D · TRUST DELIVERY** | Not attemptable this round by design | **PREPARED, UNACTIVATED** |
| **E · NO REGRESSION** | Round-6 invariants intact | **PASS** (one item hardware-unverified) |

---

## 2 · §12 CHECKPOINT — what the Founder must decide

### Candidate policy and the evidence behind it

**C2 · PROSE under BOUND-2** — 90 % of lessons clean ⇒ per-block teaching-critical ≤ 0.0035,
audit ≥ 1,092 rows. Derived from Lane A3's round-5 trade-off curve, round 5's 97-row evaluation
set, and round 6's accounting. **The recommendation carries its own predicted outcome: a
TRUTHFUL ZERO — and that prediction is sealed inside the frozen payload, so it cannot be revised
after the result is known.**

**BOUND-4 is the only passable bound**, and its consequence — **45 % of lessons carrying a
teaching-critical error** — is **not sayable to a parent**. If a non-zero result is required,
the only honest route is **BOUND-5: per-lesson certification of a bounded slice. That is not a
threshold and must never be reported as one.**

### The order is enforced, not asserted — I tried to break it

```
seq 1  policy      0dfc5032…
seq 2  population  dbadf4ad…   (BLIND-CORE)
seq 3  population  69d1cacc…   (BLIND-TEACHING)
```

Chain verified intact. **No `approval` entry. No `admitted` entry.** Adversarially, an
`admitted` write with no recorded approval is **refused with a `PermissionError`**, not merely
discouraged. **Zero lesson or book identities appear in any of the three calibration documents**,
enforced at freeze time and by a committed test.

### Trade-offs, stated without lesson identities

- Tightening role confidence to a 0.70 floor moves false trust 0.0734 → 0.0593 but **teaching-critical 0.0339 → 0.0407 — the wrong way** — and removes *every* block of continuous prose.
- **Teaching-critical is not a subset of false trust:** 5 of 354 served rows are teaching-critical without counting as false trust. **A bound on false trust alone misses them.**

### Design guarantee

`TRUST = SERVED ∩ admit(...)` with SERVED unchanged, so **`trusted ⊆ served` by construction**.
Activation **cannot serve one new block**; round 6's byte-identical served set survives it; no
waiver can manufacture trust. Property-tested.

---

## 3 · The three-way status distinction the Founder asked for

| Claim | Status |
|---|---|
| Silent-loss conservation, repair projection, `trusted = 0` invariant, freeze-chain ordering, metric re-derivation, 118-block analysis | **TECHNICALLY VALIDATED** |
| **R-1 — the 17 lesson gaps now carry page crops** | **HARDWARE UNVERIFIED.** The artefact passes all eight lineage checks including L5b (17/17) — but **no device walk was performed.** The Nokia was in personal use when WS-R reached it, and on Founder instruction the device was not touched. |
| **The 5 recovered SGK figure crops + all 22 page crops in Golden #1** | **LICENSING-DISTRIBUTION BLOCKED.** Verbatim SGK page images, INTERNAL / RESEARCH ONLY under D4. Fine for internal validation; **not distribution-ready.** «TECHNICALLY POSSIBLE != DISTRIBUTION RIGHT.» |

---

## 4 · Plan vs Actual

**WS-M · METRIC TRUTH (PR #94)** — permanent rule enforced in code · registry of **18 metrics, 18/18 re-derive** · «total activities» **DEPRECATED** (248 SUPERSEDED · 217 and 161 deprecated) · regression lint + baseline. **GATE A MET.**

**WS-T · TRUST CALIBRATION (PR #96)** — policy and two blind populations frozen and hashed · audit machinery dry-run proven · recommendation with sealed prediction. **GATES B and C MET; D deliberately not attempted.**

**WS-S · STRUCTURED CONTENT GAP (PR #95)** — recommends a servable type for **ZERO of the 118** · nothing became servable, proven by **238 byte-identical documents** · defect 8 measured on the lesson path for the first time. **S5 PARTIAL** — machinery built and inert, not DONE until a Founder throws a switch.

**WS-R · ROUND-6 DEBT (PR #97)** — 30-row triage, nothing silently dropped · R-1/R-2/R-3 done · R-4 answered with 2 defects fixed · **R-5 DEFERRED** (no recognition workstream this round) · device **BLOCKED**.

**Nothing was promoted from PARTIAL to DONE.**

---

## 5 · PROVEN

- **All 12 teaching-critical errors reduce to two mechanisms**, neither visible to any gate-readable signal; 3 of 6 digit corruptions survive character-exact two-stack agreement.
- **A servable type is recommended for zero of the 118 blocks.** 114 belong to **no structural group at all** — exactly one group across 238 lessons contains a gap block.
- **The real lever is the all-or-nothing sibling rule: 31 mutilated structures → 0**, at a cost of 72 blocks. Adding all three types removes **1 of 31**.
- **The option letters «A.»–«D.» are restored *after* `agreement()` runs.** **The one part that identifies the answer is the part no agreement measurement covers.**
- **Four published lesson denominators are one leaf population under four grouping keys** — 3,679 rows · 3,240 `(doc,no)` · 3,650 `(doc,no,pageStart,title)` · 3,381 with `pageStart`. Re-derived by me from the packs, independent of WS-A's CSV.
- **PRESERVE SOURCE VERBATIM implemented and measured on the real population.** 2,623 titles / 2,382 unique; multi-word ALL-CAPS = **108**, the Founder's figure exactly. The candidate normalisation strips capitals from **107 of 107**; `displayTitle` changes **0 of 2,382**. Named casualties it would have caused, from the shipping pack: `ASEAN AND VIET NAM` → `Asean and viet nam`, `BÁC HÔ VỚI THIÊU NHI` → `Bác hô với thiêu nhi`, `… THẾ KỈ XX` → `… thế kỉ xx` — **an acronym, a person's name and a Roman numeral.** The activation precondition is **a function, not a promise**: `titlesLosingCapitals(transform, titles)` must return empty on the real population before any normalisation may be proposed. The cost is stated plainly: **«MỞ ĐẦU» now reads «MỞ ĐẦU» on screen.**
- **Golden #1 regenerated with 17/17 crops**, 5 recovered image blocks, `validatedRepairs 9 · trusted 0 · 0 served blocks carrying a repair`, all eight lineage checks PASS.

---

## 6 · FALSIFIED — including three of my own statements

- **«The cheapest win on the board»** — I relayed round 6's phrase to the Founder without measuring it. It is not a win at all (§5). **It was never re-derived from leaf records**, which is exactly what this round's own rule exists to catch.
- **«DIGIT LOSS 312 (57 %)»** — I published a rate **without its denominator (548)**, against a standing Founder rule.
- **My first re-derivation of the denominators** used field `number`; the field is `no`. I got 238 and 3,497 and was wrong.
- **Tightening role confidence buys safety** — false, it moves teaching-critical the wrong way.
- **Teaching-critical ⊆ false trust** — false.
- **The `held_out` flag marks a usable holdout** — A3's published curve **pooled all 643 rows including the 181 held-out**. **No pre-existing blind population existed in the repo.**
- **«`si_expected_exponent` abstained on all 171»** — it was **never asked**; the metric could not distinguish «no relation printed» from «nothing to check».
- **A vacuous gate:** `fixture_lineage` L5 counted crop *references*, so a document with none printed **`0/0 present · PASS`**. **The gate was green because the thing it guards was absent.**
- WS-T withdrew **its own** clustering claim; WS-S withdrew **its own** first anchor count (22 → 10).

---

## 7 · The systemic finding — two rounds running

Round 6 found three tests encoding synthetic-era optimism. Round 7 found the same shape in
**four more places**, and they are not tests:

1. `len()` on a keyed container — **three independent occurrences across three rounds**.
2. **A gate green because its subject was absent** (L5 `0/0 PASS`).
3. **A metric that could not distinguish «not applicable» from «not asked»** (`si_expected_exponent`).
4. **Tests whose populations contained only their own precondition** — the `titleCase` tests were fed only ALL-CAPS strings; a mixed-case title had never been put in front of the rule. **The tests were not missing; the populations were.**

**A number that is the right type and the wrong quantity passes every check that is not a
re-derivation.** That is now enforced in code, not doctrine.

---

## 8 · PRODUCT REALITY

**What can a CHILD use now that they could not before this round? — NOTHING.**

Round 7 activated nothing. Golden #1's 17 gaps now carry page crops in the artefact, but that is
**hardware unverified** and the crops are **licensing-blocked for distribution**. The «Về mục lục»
contradiction and the lowercased proper noun are fixed in code and **not proven on a device**.

**PARENT: nothing new. SAM: nothing new.**
**INTERNAL / RESEARCH ONLY:** the metric registry, the frozen calibration, the audit machinery, the 118-block analysis, the debt triage, the regenerated Golden artefact.

---

## 9 · Reality Scoreboard — never averaged

| Dimension | Round 6 | Round 7 |
|---|---|---|
| SOURCE REALITY | 97 | **97** |
| SOURCE TRUST | 0 / 97 | **0 / 97 — and now measured as unreachable by calibration alone** |
| RECOGNITION REALITY | 17/47 on Bài 61 | **unchanged — no recognition workstream** |
| REPAIR REALITY | 9 validated · 6 crossed · 0 trusted | **unchanged + 17/17 crops restored** |
| PEDAGOGY REALITY | 7 / 17 | **7 / 17** |
| EVIDENCE REALITY | 0 of 0 | **0 of 0** |
| PRODUCT DELIVERY REALITY | 1 real lesson, minus its timeline | **unchanged — nothing new reached a child** |

---

## 10 · Regressions and historical corrections

Recorded in `ROUND7-HISTORICAL-CORRECTIONS.md` (C1–C5). Round 6's report and
`HOC-CUNG-SAM-ROUND-06-2026-09-06-v2.zip` are **unchanged**.

New this round: the **round-3 census scripts were repaired**, so **the published round-3 census
outputs are no longer reproducible from the fixed code** — recorded as a live assertion in
`REPAIRED_FINDINGS`, not a note, on the principle that **a repair is also a change to what old
numbers mean**. One consequence needs checking before anything leans on it: that census's
`pack_wiring['toanExercises']` column was **0 for every candidate** — a column of zeroes that
looked like absence of data and was absence of flattening. **Any candidate ranked or dismissed on
that column was ranked on a wrong input.**

---

## 10.1 · Composition CI — the round composes

Verified in a throw-away worktree from `integration/round7-2026-09-06`, all four workstream
branches merged. **The Golden #1 fixture was REGENERATED inside the composed tree, never
rsynced** — on the Founder's instruction and on WS-R's finding that rsyncing
`assets/fixtures/` silently re-introduces the crop-less artefact whose lineage fields all read
as current. Packs were rsynced (they are the verified rebuild: `verify` 12/12, `toanExercises` 0).

| Check | Result |
|---|---|
| Git merge, 4 branches | **0 conflicts** |
| Fixture regeneration inside the tree | **L5b 17/17 · VERDICT PASS · placed +22 crops** |
| `flutter analyze` | **No issues found** |
| Python suite | **866 tests OK** (18 skipped) |
| Dart suite | **1106 tests — All tests passed** |

Heads: WS-M `a6cae3b` · WS-T `5e706c9` · WS-R `7d37521` · WS-S `36e4c50`.

**It did not compose on the first attempt, and the failure was the best possible one.** WS-M's
anti-rot guard — *«a baselined finding that has disappeared must be removed in the same commit»*
— fired on its first real encounter and **caught me**: I had repaired the two round-3 census
defects that its baseline still asserted were live. We had worked in parallel.

The resolution improved on both of our positions. WS-M had deliberately *not* repaired those
scripts, reasoning that the census outputs were published and changing the code would change
what a reader finds. It then verified my fix **behaviourally rather than by reading the diff**,
withdrew the weaker half of its own argument — *«a live defect in a script that will run again
is worse than a reproducibility gap in a dated artefact»* — and pointed out that a broken
committed command is, by the round's own Gate A rule, a metric that **was never re-derivable**.

But it kept the concern **as a live assertion rather than a note**: entries were **moved** to a
new `REPAIRED_FINDINGS` record, not deleted, on the principle that **a repair is also a change
to what old numbers mean.** Three new guards, all mutation-checked, make a repaired defect's
return fail *by name*.

**And that surfaced a consequence nobody had looked for:** the round-3 second-golden-lesson
census had `pack_wiring['toanExercises'] = 0` **for every candidate** — a column of zeroes that
looked like absence of data and was absence of flattening. **Any candidate ranked or dismissed
on that column was ranked on a wrong input.** Round 7 does not lean on that ranking (the Founder
chose the Golden lessons directly), but round 8 must not.

**Two process failures recorded rather than tidied away**, both the same one: WS-M and, in round
5, Lane E2 each destroyed uncommitted work with `git checkout --`. The mutation protocol's
cp-backup rule exists for exactly this, and it has now been skipped twice. WS-M's second attempt
also verified each mutation had actually landed before reading its result — **a mutation that
«survives» because it never applied is not evidence.**

---

## 11 · Merge debt

**MERGE #79 · CLOSE #73 AS SUBSUMED · HOLD the rest.** Re-verified: #73 is still an ancestor of
#79, `main` has not moved, and the delta is still 16 commits of documentation. **The stack is now
four layers and 254 commits deep**, and `integration/round7` composes on top of it — exactly what
§10 said must not happen again.

---

## 12 · Next bottleneck — ONE

**Recognition and role disambiguation.** Round 7 measured it rather than assumed it: no threshold
can bound teaching-critical error below ≈0.021 because the two mechanisms that produce it leave
no signal a gate can read. **Calibration is finished and it is not the answer.**

---

## 13 · Round 8 — proposed

**NORTH STAR: MAKE THE TWO TEACHING-CRITICAL MECHANISMS VISIBLE TO A GATE.**

| | |
|---|---|
| **WHY NOW** | Round 7 proved calibration cannot reach them; the gate is built and waiting on evidence it cannot currently get. |
| **PROBLEM** | Digit corruption survives character-exact two-stack agreement; a non-question served as a question is a role error no confidence score separates. |
| **OBJECTIVE** | A signal — recognition-level or structural — that separates each mechanism from correct content. |
| **MEASURABLE TARGET** | Teaching-critical error bounded **below 0.0035 on the frozen blind population**, or a measured statement that it cannot be. |
| **DEPENDENCIES** | The frozen populations exist. **No Founder decision needed to start.** |
| **RISKS** | Building a signal that fits the 12 known errors. Mitigation: the blind populations are already frozen and hashed. |
| **STOP CONDITION** | If no signal separates them, report it and **the trust gate stays unactivated** — a truthful zero, again. |
| **FOUNDER GATE** | Activation, still. Unchanged. |

Secondary: the all-or-nothing sibling rule (31 → 0, cost 72 blocks) · defect 6 on the lesson path
(**22 imprint blocks reach children today**) · the hardware verification R-1 still needs.

---

## 14 · Pull requests — all open, none merged

| PR | Branch |
|---|---|
| #94 | `ws-m/round7-metric-truth` |
| #95 | `ws-s/round7-structured-gap` |
| #96 | `ws-t/round7-trust-calibration` |
| #97 | `ws-r/round7-debt` |

Plus #89–#93 (round 6), #79–#88 (round 5), #73 (round 4).

**NO THRESHOLD ACTIVATED. NOTHING MERGED. READY FOR FOUNDER REVIEW.**
