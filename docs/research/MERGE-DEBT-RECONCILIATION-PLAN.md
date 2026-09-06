# MERGE-DEBT RECONCILIATION PLAN
## Round 7 closeout · Founder task order 43 · deliverable 3

> **NOTHING WAS MERGED IN PRODUCING THIS.** No branch was pushed to, no PR was merged, no PR
> was closed, no branch was deleted. Every claim below is a command that was run and an output
> that was read. **This is a plan, not an action.**

**Verdict — and it differs from the two audits that preceded it.**

> **The prior recommendation — «merge #79 → close #73 → hold the rest» — is verified as
> internally correct and is nonetheless the wrong action, because it does not answer the
> question the Founder asked.** It clears 2 of 20 PRs, leaves 175 commits and 18 PRs stacked in
> two layers above `main`, and would put on `main` a round-5 report that cites code `main` would
> not contain. **It does not stop a fifth layer.** The action that does is to finish round 7 into
> its own base and merge that base once. See §9 and §11.

**Evidence pinned at 2026-09-06T08:36Z.** All statements below were computed against these
exact objects. `integration/round7-2026-09-06` **moved twice while this audit was running**
(§2.3) — a later reader must re-verify rather than assume.

| ref | SHA | ahead of `main` |
|---|---|---|
| `origin/main` | `61dbfdbc92cf` | — |
| `origin/integration/round4-2026-09-05` (#73) | `05a0927e26a3` | **73** |
| `origin/integration/round5-2026-09-06` (#79) | `bab657a639c3` | **89** |
| `origin/integration/round6-2026-09-06` | `d5a9946e4db4` | **208** |
| `origin/integration/round7-2026-09-06` | `b15bb1eaec88` | **264** |

---

## 1 · The commit-depth number, verified

**`integration/round7-2026-09-06` is 264 commits ahead of `main`** — not 254, not 259, not 262.

```
git rev-list --count origin/main..origin/integration/round7-2026-09-06   →  264
```

The number in the task order was 259 at `74d9db6`. It was **262** when this audit opened its
worktree at `79984f9`, and **264** forty minutes later at `b15bb1e`. Of the 264, **239 are
non-merge commits and 25 are merge commits** — twenty-five merge fronts to bisect across.

**The number is not a static fact. It is a rate.** That is the finding, not the integer.

---

## 2 · Three structural facts that decide everything below

### 2.1 · The stack is a strict chain, not four divergent branches

```
git merge-base --is-ancestor origin/main   origin/integration/round7-…  → true
git merge-base --is-ancestor <round4> <round5> → true
git merge-base --is-ancestor <round5> <round6> → true
git merge-base --is-ancestor <round6> <round7> → true
```

`main ⊂ round4 ⊂ round5 ⊂ round6 ⊂ round7`. There is **no divergence anywhere in the stack**.
Nothing needs reconciling in the sense of resolving two answers to one question about *code* —
the code question has exactly one answer, and `round7` is it. This is why selective/cherry-pick
strategies are not merely unnecessary here but harmful: they would fork a lineage that is
currently provably linear.

### 2.2 · Eighteen of the twenty open PRs are already inside `integration/round7`

This is the finding that changes the recommendation, and **neither prior audit tested for it.**

```
for each PR head:  git merge-base --is-ancestor <head> origin/integration/round7-2026-09-06
```

| in `round7`? | PRs |
|---|---|
| **YES — fully contained** | **#73 · #79 · #80 · #81 · #82 · #83 · #84 · #85 · #86 · #87 · #88 · #90 · #91 · #92 · #93** (15) |
| **NO — real outstanding work** | **#89** (1 commit of residue) · **#94 · #95 · #96 · #97** |
| …and of those, **#97 ⊂ #95** | `is-ancestor ws-r/round7-debt ws-s/round7-structured-gap` → **true** |

So the genuine outstanding delta is **four PRs' worth of work** (#94, #95+#97, #96, and one
commit of #89) — not twenty.

**The consequence for the prior plan.** Round 6 recommended *holding* #80–#88 and #89–#93
because they were «unreviewed, and three touch code WS-A is currently changing». Those branches
are **already merged into the branch every round-7 workstream targets and builds on**. Holding
their PRs open isolates nothing; it only leaves twenty rows in a PR list. The isolation the
round-6 audit was buying does not exist and has not existed since the round-6 base was composed.

### 2.3 · Research truth is strictly additive — zero documentation was ever deleted

```
git log --diff-filter=D --name-only origin/main..origin/integration/round7-… -- 'docs/**'
  → (empty)
```

**Across all 264 commits, not one file under `docs/` was deleted.** No measured result, negative
finding, FALSIFIED verdict, PARTIAL status, historical decision or provenance record has been
removed by a later round. Rounds correct each other **beside** the original
(`ROUND7-HISTORICAL-CORRECTIONS.md`), never on top of it.

**This is the single most important safety property in this document.** It means merging
`round7` cannot lose research truth, because there is no research truth in an ancestor that
`round7` does not still carry.

---

## 3 · Per-PR classification

Taxonomy per round 6: **SAFE FOUNDATION · REQUIRED · NEEDS REWORK · SUPERSEDED · OBSOLETED ·
CAN WAIT.** «SUPERSEDED» here means **superseded by containment** — the PR as a *review unit* is
redundant because a descendant carries every one of its commits. It never means the work was
replaced or discarded. **No row in this table converts a PARTIAL into a DONE.**

| # | branch | round | contains | class | depends on | lost if never merged | risked if merged |
|---|---|---|---|---|---|---|---|
| **73** | `integration/round4-2026-09-05` | 4 | Round-4 base: LessonDocument + fail-closed parser, Learning Views/Smart Book/workspace, tc2 SDM + role layer + guards, `pack_provenance` honest-FAIL fix. 164 files | **SUPERSEDED** (by containment in #79 and `round7`) | — | **Nothing** — every commit is in `round7`. Only the PR row is redundant | Nil beyond #79; Founder **ACCEPTED** this content |
| **79** | `integration/round5-2026-09-06` | 5 | #73 **+ 16 commits touching 3 files, all `docs/research/`** — `ROUND5-PLAN`, `ROUND5-CONSOLIDATED-REPORT`, `ROUND5-AUDIT-97-EVALUATION-SET`. **No round-5 lane code** | **SAFE FOUNDATION**, and **SUPERSEDED by containment** in `round7` | #73 (ancestor) | Round-5 plan + consolidated report + the 97-row evaluation set | **Merged ALONE: a documentation-code inversion on `main`** — see §5.1 |
| **80** | `lane-a3/round5-role-spec-trust-gate` | 5 | ROLE DEFINITION SPEC v1, trust-gate sensitivity curve. Research only, **no threshold set** | **CAN WAIT** (content) · **SUPERSEDED** (unit) | #79 | Role taxonomy + the curve that later bounds WS-T | None — in `round7`, and it sets nothing |
| **81** | `lane-c/round5-history` | 5 | Bài 8 re-run, verbatim gate, repair→restore, `TimelineValidator` verdict **DO NOT REGISTER, Evidence Reality stays 0** | **CAN WAIT** (rules **PROPOSED**, History-only, **falsified as a general rule** — 3 events / 28 lessons) | #79 | The falsification, and the DO-NOT-REGISTER verdict | None — the verdict is negative and travels with it |
| **82** | `lane-d/round5-legacy-packs` | 5 | Pack rebuild §13, legacy batches by failure class, REPAIRED stage scored from outside, `silent_loss.py`. **41 INFERRED expressions stopped shipping**; R15 filed for Founder; **R7c corrected FIXED → PARTIAL** | **REQUIRED** (content) · **SUPERSEDED** (unit) | #79, #83 | The silent-loss discovery; the 41-expression fail-closed; **R7c's demotion to PARTIAL** | None — in `round7`; the demotion is preserved verbatim |
| **83** | `a1/round5-repair-framework` | 5 | DETECT/REPAIR/VALIDATE/RESTORE framework + plugin registry, Vietnamese text accuracy. Coverage 0.551→0.577, **false trust unchanged** | **REQUIRED** — every later repair plugs into this registry | #79 | The framework every round-6/7 repair depends on | None — in `round7` |
| **84** | `a2/round5-math-formula-accuracy` | 5 | STEM audit, canonical AST, **10 restores at precision 1.000**, 2 false corrections found and closed | **REQUIRED** | #79, #83 (registers against A1) | The AST and the two caught false corrections | None — in `round7` |
| **85** | `e1/round5-semantic-foundation` | 5 | SemanticClaim, SourceGrounding, provenance bridge, VisualSpec contract. Grounding integrity 0.952→1.000 across 238 TSL lessons | **REQUIRED** | #79 | Semantic foundation + the identity-leak retraction | None — in `round7` |
| **86** | `e2/round5-visualspec-renderer` | 5 | VisualSpec + one renderer proven across three subjects, six subjects in the §19 proof | **CAN WAIT** (renderer families bounded, deliberately not expanded) · **SUPERSEDED** (unit) | #85 | The one-renderer generalisation proof | None — in `round7` |
| **87** | `lane-b/round5-experience` | 5 | Trực quan → concept frame; Workspace density A/B/C on a real Nokia; two real-device defects fixed | **REQUIRED** (content) · **SUPERSEDED** (unit) | #79 | Device evidence manifest + the density comparison | None — in `round7` |
| **88** | `a4/round5-multi-signal-verification` | 5 | Cross-corpus, LLM-as-verifier, external evidence, router with measured escalation. **Edge risk half confirmed, half falsified** | **REQUIRED** (content) · **SUPERSEDED** (unit) | #79, #83 | The signal matrix **and its negative results** | None — in `round7` |
| **89** | `ws-archive/round5-retrospective` | 5→6 | Reusable per-round archive builder. **3 of its 4 commits are already in `round7`; 1 is not** (`42e28ec`, 2 files: `tool/reporting/README.md`, `examples/round07-archive-spec.json`). Verdict on its own subject: **PARTIAL — capability proven, nothing delivered to a child** (8 PASS · 1 PARTIAL · 1 FAIL) | **SUPERSEDED in part** — one commit of residue | branch is ~118 commits **behind** `round7` | The NOT-CAPTURED-note rule and the round-7 archive spec | Nil — merges clean, 2 files, verified §7 |
| **90** | `ws-c/round6-repair-integration` | 6 | ValidatedRepair crosses into TSL + LessonDocument **and does not become trusted**. Historical correction to round 5's dispose-row verdict. **«no carrier for structured content» = PARTIAL; a servable structured kind = DEFERRED** | **REQUIRED** (content) · **SUPERSEDED** (unit) | round-5 lanes | The repair→product wire and the round-5 correction | None — in `round7`. **Its PARTIAL/DEFERRED rows must stay PARTIAL/DEFERRED** |
| **91** | `ws-a/round6-accounting` | 6 | R13 zero silent loss (UNACCOUNTED 27→0, 55→0, both Golden slices→0), canonical lesson identity, ledger that **exits non-zero** | **SAFE FOUNDATION** — corrects denominators every later metric uses | round-5 lanes | The R13 correction; every later metric's denominator | None — in `round7` |
| **92** | `ws-b/round6-recognition` | 6 | Recognition failure census + targeted re-crop (GATE B met). **Ω→S2 FALSIFIED, 0 of 22 at every scale; unigram diacritic rule falsified (26,703 false candidates)** | **REQUIRED** (content) · **SUPERSEDED** (unit) | round-5 lanes | **Two falsifications** — the most expensive kind of finding to re-earn | None — in `round7` |
| **93** | `ws-d/round6-golden-delivery` | 6 | Workspace OPTION B, GOLDEN #1 on a real Nokia, learning-view census. **Golden #2 DEFERRED; visual grammar POC NOT STARTED** | **REQUIRED** (content) · **SUPERSEDED** (unit) | #90, #91, #92 | Real-device evidence + the census that says *do not build one yet* | None — in `round7`. **DEFERRED and NOT STARTED must not become DONE** |
| **94** | `ws-m/round7-metric-truth` | 7 | **NOT in `round7`.** Metric Definition Registry, container-shape lint, `len()`-on-a-mapping blocked, «total activities» deprecated, the `toanExercises` incident as a committed regression, **the two round-3 findings are REPAIRED not GONE** | **REQUIRED** | `round7` | The registry that makes «a number with no denominator» a lint failure | Low — no `lib/` change; adds a guard. Verified clean + green §7 |
| **95** | `ws-s/round7-structured-gap` | 7 | **NOT in `round7`.** The 118 answered: **add a servable type for ZERO of them**; BlockGroup makes mutilated structure countable and **NOT switched on**; **implements Founder order 42 — preserve source verbatim, `titleCase` deleted**. **Carries all 7 commits of #97** | **REQUIRED** | `round7`; **supersedes #97** | The 118 measurement, the falsification of «cheapest win on the board», **and the Founder's title-fidelity decision** | Low — the group rule is built and **not activated**. Verified green §7 |
| **96** | `ws-t/round7-trust-calibration` | 7 | **NOT in `round7`.** Candidate trust policy frozen + hashed, two blind evaluation populations, STEP C machinery **inert**. **Withdraws its own clustering claim — the second derivation dissolved it** | **REQUIRED but INERT** | `round7` | The frozen policy, the blind populations, **and the self-withdrawn claim** | **Verified zero `lib/` files touched** — cannot activate anything in the app. `trusted` stays 0 |
| **97** | `ws-r/round7-debt` | 7 | **NOT in `round7`, but ⊂ #95 — proven.** Round-6 debt triage (30 rows, nothing dropped) + four P0 fixes: crop gate counted references not population, SAM's leave-the-lesson string, lowercased proper noun, `si_expected_exponent` never abstaining. **R-1 DONE (artefact) / PARTIAL (no device walk); R-5 DEFERRED** | **SUPERSEDED by #95** (containment) | `round7` | The triage register — the one document that guarantees nothing vanished | None — merging #95 delivers it exactly once |

**OBSOLETED: none.** Consistent with round 6's finding, and re-verified: each round *added to*
its predecessor. Nothing in rounds 4–7 has been rendered obsolete by a successor.

---

## 4 · Conflicting conclusions — which answer is current

Where two rounds reached different answers, the later one governs **and the earlier one is still
on disk**. This register exists so no merge is mistaken for a silent overwrite.

| # | earlier claim | corrected by | current answer | recorded at |
|---|---|---|---|---|
| C1 | Round 6 §12: the 118 gap blocks are «a model gap, not a data gap, **and the cheapest win on the board**» | **#95** (WS-S), measured | **Not a win at all.** A servable type is recommended for **ZERO** of 118. 114 gain nothing (exactly one structural group across 238 lessons contains a gap block). The real lever is the sibling rule: **31 → 0** mutilated structures at a cost of 72 blocks | `ROUND7-HISTORICAL-CORRECTIONS.md` C1 |
| C1b | Round 6: «these blocks passed every trust gate» | **#95** | **FALSIFIED.** They passed the **TSL** gate → `trustedStructuredLesson`, which is a **schema label, not a trust grant** | same |
| C2 | Round 6 §4: «DIGIT LOSS 312 (57 %) vs SEGMENTATION 196 (36 %)» | **#94** (WS-M) | Percentages correct; **the denominator 548 was missing**. Reads 312/548 = 0.569 and 196/548 = 0.358 | same, C2 |
| C3 | Round 3 census: «some packs carry bare ids (e.g. `toanExercises`)» — a comment written into the code | **#94** | **A misdiagnosis of a bug, recorded as a property of the data.** `len()` on a keyed container returns keys, not leaves. Three independent occurrences across three rounds. **Fixed forward; published round-3 outputs NOT rewritten** | same, C3 |
| C4 | WS-T's own clustering claim (round 7, mid-round) | **#96**, second derivation | **Withdrawn by its author.** «The second derivation dissolved it» | `TRUST-CALIBRATION-ROUND7-REPORT.md` |
| C5 | Round 5 R7c: «FIXED» | **#82** blind audit | **PARTIAL.** A stanza was served as one prose run on that build | PR #82 |
| C6 | Round 6 audit: hold #80–#88 because «three touch code **WS-A is currently changing**» | **this audit** | **Expired.** WS-A changed it (#91), round 6 merged it, round 7 sits on top. The premise was true when written and is false now | §2.2 |
| C7 | Round 6 + round 7 audits: «**MERGE #79**» | **this audit** | **Superseded.** Correct arithmetic, wrong scope — it clears 2 of 20 PRs, does not stop a fifth layer, and creates a doc/code inversion on `main` | §5.1, §11 |

**Round 5's own scorecard, which no merge may soften: 8 PASS · 1 PARTIAL · 1 FAIL.**
Criterion 4 (*correct served / coverage begins to recover*) is **FAIL** — corrected for R13 the
served share **fell**, over-withhold worsened 0.400→0.633, and the only coverage that recovered
came from loosening a guard and was wrong (0/1). Criterion 5 (*role taxonomy clearer and
agreement up*) is **PARTIAL** — re-annotation was in-sample, the settling blind measurement was
never run, and pipeline role error moved the wrong way 0.116→0.151. **Merging round-5 code is
not a claim that round 5 passed. It did not, on two of ten criteria.**

---

## 5 · Duplicate work

### 5.1 · The `patch-id` sweep across the whole stack

```
git rev-list --no-merges origin/main..origin/integration/round7-…      → 239 commits
… | git patch-id --stable | sort | uniq -d                             → 1 duplicate group
```

**Exactly one duplicated change in 239 commits**, and it is:

| patch-id | SHAs | change |
|---|---|---|
| `051f42ca…` | `657192a` · `2abb4bf` (46 seconds apart) | **`docs(round6): merge debt audit — recommend B, merge #79 which subsumes #73`** |

**The only duplicated commit in the entire stack is the merge-debt audit document itself.**
Both blobs hash identically to the version in `round7`
(`6259c316c7bb153d`), so the duplication is benign provenance noise, not a defect — but it is
worth stating plainly that the document recommending the merge is the one thing in the stack
that got committed twice.

**The round-6 duplicate is gone.** The task order cites WS-A's R13 fix existing as two SHAs on
two branches; that pair does **not** appear in this sweep, which confirms the round-6 rebase
that resolved it worked and did not leave a residue.

### 5.2 · The near-miss that composition testing caught

`#94` and `#96` both appear to touch `tool/research/lane_c/second_lesson_candidates.py` and
`subject_family_census.py` — the two files of correction C3. A naive read says «overlap, expect a
conflict or a silent revert». Verified instead:

| file | merge-base | `round7` | `#96` | composed result |
|---|---|---|---|---|
| `second_lesson_candidates.py` | `ed479159447d` | `c2f61a098045` | `ed479159447d` | **`c2f61a098045`** ✅ |
| `subject_family_census.py` | `de388cbe9206` | `9a1e78f347aa` | `de388cbe9206` | **`9a1e78f347aa`** ✅ |

`#96` is **byte-identical to the merge base** on both files — it never modified them, it is
merely behind. Git correctly keeps `round7`'s fixed version. **The C3 fix survives composition.**
A false alarm, but a *verified* false alarm: this is precisely the shape of defect that would
otherwise revert a correction silently.

---

## 6 · The documentation-code inversion — a specific harm of merging #79 alone

Neither prior audit tested this. `#79`'s entire delta over `#73` is three research documents.
`ROUND5-CONSOLIDATED-REPORT-2026-09-06.md` **cites code paths that `#79` does not contain**:

| path cited in #79's report | mentions | files present in `#79`'s tree |
|---|---|---|
| `tool/corpus/repair` | 2 | **0** |
| `tool/corpus/verify` | 1 | **0** |

Merging `#79` alone therefore publishes to `main` a consolidated report describing a repair
framework and a verification layer **that `main` would not have**. A later reader — or a hotfix
author branching from `main` — finds documentation for absent code. That is a new instance of
exactly the hazard the workspace `CLAUDE.md` opens with: doctrine on `main` that the code on
`main` cannot support. **The prior recommendation would create it.**

---

## 7 · Testing evidence — composed and run, not asserted

Composed in a **throw-away worktree** (`/private/tmp/merge-compose`, branch
`throwaway/compose-r7`), never in the shared checkout.

**Asset handling, per the round-6 trap (`ROUND6-DEBT-TRIAGE.md` §4.1).** `assets/pack/**.png`
was rsynced from the main checkout. **`assets/fixtures/real/` was NOT rsynced — it was
regenerated**, because rsyncing re-introduces round 6's crop-less Golden #1 whose lineage fields
all read as current. Regeneration needs **PyMuPDF (`fitz`)**, present only in
`.venv-bakeoff`, plus the 14 GB gitignored `poc-out/`.

```
python3 -m tool.corpus.repair.tsl_projection --tsl …/bai-08.tsl.json \
    --ledger …/repair-ledger.jsonl --out …/lsdl5-bai08.tsl.json \
    --lesson-document …/lsdl5-bai08.lesson.json          → 22 crops rendered
python3 tool/evidence/golden_delivery.py --doc …/lsdl5-bai08.lesson.json --history-rules \
    --verbatim-ledger … --toc-title "…" --require-repair --place
```

**Lineage gate reproduces the round-7 P0-1 fix from source:**

```
PASS  L5   every referenced crop exists
PASS  L5b  every croppable withheld region has a page crop     17/17 have a crop
PASS  L6   D4 distribution marker intact
VERDICT PASS        trusted=0   productionTrustThreshold=None   validatedRepairs=9
```

### Results

| state | `flutter analyze` | Python (`unittest discover -s tool/tests`) | `flutter test` |
|---|---|---|---|
| `integration/round7` **alone** | **clean** | **748 OK**, 18 skipped | **1042 passed / 44 skipped / 0 failed** |
| `round7` **+ #94 + #95 + #96 + #89** | **clean** | **866 OK**, 33 skipped | **1074 passed / 48 skipped / 0 failed** |

**Merge mechanics — every combination is conflict-free:**

| merge | result |
|---|---|
| each of #89, #94, #95, #96, #97 → `round7` (`git merge-tree`) | **clean, individually** |
| all four composed together, sequentially | **clean, 0 conflicts** |
| `round7` → `main` (`git merge-tree`) | **clean** |

**Two defects the prior rounds reported are confirmed fixed by round 7, by running them:**
PR #90 and PR #93 both reported `flutter test … 1 failed` — `timeline_history_test.dart`. On the
composed round-7 state **with the regenerated fixture present**, that file is **9 passed / 0
failed**, and the whole Dart suite is 0 failed.

### 7.1 · What the green does NOT prove — and CI cannot see it

`test/features/lesson_workspace/golden1_history_test.dart` holds the **six highest-value
assertions in the repository** — that a validated repair stays withheld and carries no text,
that no repaired value reaches the Đọc screen, that the «chưa kiểm định» chip survives. Without
`assets/fixtures/real/`:

```
00:00 +0 ~6: All tests skipped.
   Golden #1 chưa sinh trên máy này — chạy tool/evidence/golden_delivery.py (cần poc-out/)
```

**Six silent skips, and the suite still says «All tests passed».** `assets/fixtures/real/` is
gitignored (Founder D4), and regenerating it needs PyMuPDF **and** the 14 GB `poc-out/` corpus
**and** the SGK PDFs — **none of which exist in CI**. Therefore:

> **A green «Analyze & Test» on a PR to `main` does not prove the Golden #1 delivery chain.
> It never has, and it cannot.** With the fixture, all six pass (verified above, on this Mac).
> This is the Founder's own standing rule — **ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION** —
> presenting itself in the test suite, not in the corpus. It is filed as **GAP-1** in §12.

---

## 8 · What the merge would and would not deliver

**It would deliver nothing to a child.** `assets/pack/*.png` and the pack JSONs are gitignored
build artefacts. **Merging changes no APK.** Any device still carries whatever packs were last
built on that machine. This must be stated in the merge commit so «round 7 merged» is never
read as «round 7 shipped».

**It cannot activate a trust threshold.** Verified: `#96` touches **zero files under `lib/`**;
its entire footprint is `tool/corpus/thresholds/**`, `tool/research/lane_c/**` and docs. `#95`'s
group rule is built and **not switched on**. The golden run reports `trusted=0` and
`productionTrustThreshold=None`. Founder order 43's «không activate trusted threshold» is
structurally satisfied, not merely promised.

**Licensing is unchanged.** `L6 D4 distribution marker intact` passes; the 22 regenerated crops
are **INTERNAL / RESEARCH ONLY** and stay outside git. Merging moves no restricted evidence into
the repository.

---

## 9 · The ordered sequence

**Design rule for this sequence: PR count is a *consequence*, never a *reason*.** Each step below
is justified by a structural property (linear ancestry, additive-only history, a green composed
suite), and the step that closes fifteen PRs closes them because a single `is-ancestor` proof
makes each one redundant — not because twenty is a big number.

### STEP 1 — land WS-M (#94) into `integration/round7-2026-09-06`
- **Preconditions:** none. `#94` targets `round7`; CI `SUCCESS`; `merge-tree` clean.
- **Verification that proves it safe:** `git merge-tree` clean (done); after merge
  `unittest discover -s tool/tests` and `flutter analyze`. The container-shape lint is a *guard*:
  it can only make a wrong number fail, never make a right one pass.
- **What could go wrong:** the new lint fails a metric elsewhere in the tree. That is the lint
  working; fix the metric, do not relax the lint.
- **Rollback:** `git revert -m 1 <merge>`. Branch untouched.
- **Gate:** **mechanical.**

### STEP 2 — land WS-S (#95) into `round7`; close #97 as subsumed
- **Preconditions:** Step 1. Founder order 42 (title fidelity) is already decided — `#95`
  *implements* it, it does not re-open it.
- **Verification:** `git merge-base --is-ancestor origin/ws-r/round7-debt
  origin/ws-s/round7-structured-gap` → **true**. Paste that command and its output into the
  comment closing `#97`. Then `flutter test` — `#95` adds
  `proper_noun_title_test.dart` and `next_action_contradiction_test.dart`, both of which must be
  **green**, and both of which were shown to go **red under mutation** by WS-R.
- **What could go wrong:** closing `#97` without the ancestry proof would look like discarding
  the round-6 debt triage — the one register guaranteeing nothing vanished. **The proof is the
  whole safeguard.** Do not close `#97` before `#95` is actually merged.
- **Rollback:** revert the merge; reopen `#97`.
- **Gate:** **mechanical.**

### STEP 3 — land WS-T (#96) into `round7`
- **Preconditions:** Steps 1–2.
- **Verification:** `git diff --name-only round7..ws-t | grep '^lib/'` must return **empty**
  (verified: it does). Confirm `tool/research/lane_c/*.py` in the merged tree hash to
  `c2f61a098045` / `9a1e78f347aa` — the C3-fixed versions, per §5.2. Re-run the Python suite.
- **What could go wrong:** a reader mistakes a frozen candidate policy for an activated one.
  The merge commit must say **«STEP A + B only; inert; `trusted` remains 0»**.
- **Rollback:** revert the merge.
- **Gate:** **mechanical** — *because* it is inert. Had it activated a threshold it would be
  Founder-only.

### STEP 4 — land #89's residue
- **Preconditions:** Steps 1–3.
- **Detail:** `#89` is ~118 commits **behind** `round7` and 3 of its 4 commits are already in.
  **Merge the branch** (verified clean, and composed green) **or** cherry-pick `42e28ec` alone.
  Prefer the merge: it is proven, and cherry-picking would create the second duplicate patch-id
  in the stack's history.
- **Verification:** after merge, `tool/reporting/README.md` and
  `examples/round07-archive-spec.json` present; Python suite green.
- **Rollback:** revert.
- **Gate:** **mechanical.**

### STEP 5 — verify the composed base (no merge; this is a check)
- Rsync `assets/pack/**.png`; **regenerate** — never rsync — `assets/fixtures/real/` with the two
  commands in §7, using the `fitz`-capable interpreter.
- **Must observe, and record in the PR body:** `flutter analyze` clean · Python **866 OK** ·
  Dart **1074 passed / 0 failed** · lineage `L5b … 17/17 have a crop` · `VERDICT PASS` ·
  `trusted=0`.
- **What could go wrong:** rsyncing the fixture re-introduces the crop-less Golden #1 with
  lineage fields that all read as current. `L5b` goes **FAIL** (`0/17`) — but **do not rely on
  noticing.** Regenerate.
- **Gate:** **mechanical.**

### STEP 6 — 🔴 **FOUNDER GATE** — merge `integration/round7-2026-09-06` → `main`
- **Preconditions:** Steps 1–5 green. Open **one new PR** `round7 → main` (no existing PR has
  this pair — `#73` and `#79` target `main` from older heads).
- **Verification already in hand:** `main` is an ancestor of `round7`; `merge-tree` clean;
  branch protection is satisfiable (`strict: true`, and `main` has not moved from `61dbfdb`);
  the required check is `Analyze & Test`, which will run because `paths-ignore` applies only to
  `push:main`, not to `pull_request`.
- **The PR body must state, in these words:** that this delivers **no APK change**; that
  round 5 scored **8 PASS · 1 PARTIAL · 1 FAIL** and criterion 4 is **FAIL**; that `trusted = 0`
  and `eligible for teaching = 0`; that hardware is **UNVERIFIED**; that Golden SGK crops are
  **INTERNAL / RESEARCH ONLY** under D4; and that **CI green does not prove the Golden #1 chain**
  (§7.1).
- **What could go wrong:** «round 7 merged» gets read as «round 7 shipped», or as round 5
  having passed. The wording above is the mitigation, and it is the reason this step is
  Founder-gated rather than mechanical — the risk is one of **meaning**, not of code.
- **Rollback:** `git revert -m 1 <merge>` on `main`. The revert is clean because the merge is a
  fast-forwardable linear chain, and **no branch is deleted at this step**, so nothing is
  unrecoverable.
- **Gate:** 🔴 **FOUNDER-ONLY.** Merge to `main` is a Founder gate under AI Workforce V1 and
  order 43. **Agents open the PR; they do not merge it.**

### STEP 7 — close the fifteen subsumed PRs, **after** Step 6 (mechanical, with a proof each)
- For **#73 · #79 · #80–#88 · #90–#93**, close each with the literal output of
  `git merge-base --is-ancestor <head> <merged-main-sha>` in the comment, plus the sentence
  **«Subsumed by containment — every commit in this PR is in `main` at `<sha>`. No work was
  discarded, no status was changed.»**
- **⛔ DO NOT DELETE ANY BRANCH.** Branch deletion is the *only* mechanism in this whole plan by
  which research truth could actually be lost. Closing a PR loses nothing while its branch and
  its reflog exist. Deleting a branch whose commits are in `main` is still safe — but deleting
  one whose commits are **not** (e.g. if Step 6 is deferred) destroys work.
- **Gate:** **mechanical**, but strictly **after** Step 6. Closing them first would strand the
  work with no PR pointing at it.

---

## 10 · Testing option D («hold everything») rather than repeating round 6's argument

Round 6 asserted option D «is not neutral». That is a claim, so it gets tested, not restated.
Three of its four supporting arguments hold; one is now much stronger; and one **new** cost was
found that round 6 did not identify.

| round-6 claim | test | result |
|---|---|---|
| «No CI ever builds what the Founder would merge» | Read `.github/workflows/ci.yml`: `on: push: branches: [main]` + `pull_request:` | **TRUE, and sharper than stated.** A PR builds *its head merged into its own base*. `#94`'s check builds `round7 + #94` — a **two-way** composition. **No CI run anywhere has ever built the four-way composition**, nor `round7` against `main`. Both were built here, by hand |
| «Bisect is compromised» | `git rev-list --merges --count` | **TRUE** — **25 merge fronts** across 264 commits |
| «Rebase cost compounds» | `patch-id` sweep, §5.1 | **TRUE but paid down.** The round-6 duplicate is gone; only the audit document itself is duplicated. This cost was real and has been *worked off*, not avoided |
| «`main` is ~4 rounds stale» | `git diff --name-only main..round7 \| wc -l` | **TRUE** — **491 files** differ; `main`'s tip is `61dbfdb` (2026-09-05 16:27) |
| — *(not identified by round 6)* | §6 | **NEW COST: the prior recommendation itself creates a documentation-code inversion on `main`** |
| — *(not identified by round 6)* | §1 | **NEW COST: the depth is a rate, not a number** — 254 → 259 → 262 → 264, the last two increments **during this audit** |

**Verdict on option D: round 6 was right, and understated it.** Holding is not a decision to
keep things as they are, because things do not stay as they are — the stack grew twice while
this document was being written. Each layer is composed only in a throw-away worktree that no CI
reproduces and that is deleted afterwards.

**But the important correction is this:** option D's cost is *not* an argument for the prior
recommendation. **Merging `#79` is 87 % of option D.** It moves `main` 89 commits forward,
leaves 175 commits and 18 PRs in two layers, and leaves round 8 composing on an unmerged
round 7 — which is the precise outcome §10 of the order forbids.

**Answer to «what is the minimum action that stops the stack growing a fifth layer»:**

> **Round 8 must be able to branch from `main`.** That is true only when `round7` is *in*
> `main`. Steps 1–6 are the minimum set that achieves it — four small merges into `round7`, one
> verification, one Founder-gated merge. **No smaller action works**, because any action leaving
> `round7` unmerged leaves the fifth layer to be composed on top of it.

**What the project loses by continuing to defer:** `main` stays 491 files and four rounds behind,
so any hotfix branches from a tree predating silent-loss accounting (#91), the repair framework
(#83), recognition (#92) and the honest Bài 8 fixture (#97); bisection stays 25 merge fronts
deep and deepens; and the integration branches keep being treated as a delivery path while
functioning as none.

---

## 11 · Where this contradicts the prior recommendation, and why

`ROUND6-MERGE-DEBT-AUDIT.md` and `ROUND7-MERGE-DEBT-REAUDIT.md` both conclude **«MERGE #79 ·
CLOSE #73 · HOLD the rest»**. Every fact they assert was re-verified here and **every one is
correct**:

- `#73` is an ancestor of `#79` — **confirmed**;
- `main` is an ancestor of `#79` — **confirmed**;
- the `#73 → #79` delta is 16 commits, 3 files, **all `docs/research/`** — **confirmed exactly**;
- `#79` does not contain round-5 lane code — **confirmed**;
- option D is not neutral — **confirmed and strengthened (§10)**.

**The disagreement is about scope, not about facts.** Three reasons:

1. **The premise for «hold» has expired.** «Three of them touch code WS-A is currently
   changing» was true when written. WS-A finished (#91), round 6 merged it, round 7 composed on
   top. **All nine round-5 lane branches and all four round-6 workstreams are already inside the
   branch round 7 is built on** (§2.2). Holding their PRs isolates nothing. This is the failure
   mode the workspace `CLAUDE.md` warns about in its own preamble — *stale doctrine blocks as
   hard as a real gate, and no test catches it* — reproduced here inside a merge audit.

2. **Neither audit tested containment of #80–#97 against `round7`.** Both tested `#73 ⊂ #79` and
   stopped. One `--is-ancestor` loop over twenty PR heads reduces the problem from twenty units
   to four. That loop is §2.2, and it is what changes the answer.

3. **Merging `#79` has a cost neither audit identified** — it publishes to `main` a round-5
   report citing `tool/corpus/repair` and `tool/corpus/verify`, **neither of which `#79`
   contains** (§6).

**Both prior documents remain on disk, uncorrected and unrewritten**, per the standing rule that
corrections are recorded beside the original. This section *is* that record.

---

## 12 · Gaps and open items this plan does not close

| id | gap | status |
|---|---|---|
| **GAP-1** | The six Golden #1 delivery-chain assertions **skip silently** wherever `assets/fixtures/real/` is absent — which is CI, and every clean clone. The suite reports «All tests passed» having tested none of them | **OPEN.** Not a merge blocker; a **reporting-honesty** defect. Minimum fix: make the *absence* of the fixture print a loud UNVERIFIED banner rather than a skip, per **ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION** |
| **GAP-2** | **Round 5 has no explicit Founder acceptance verdict.** Rounds 4, 6 and 7 do (order 41, order 43). Round 5's conclusions were *consumed* by order 39 («Round 5 established / proved / evidence») but never accepted in their own right, and round 5 scored **1 FAIL + 1 PARTIAL** | **FOUNDER DECISION.** Step 6 merges round-5 lane code. This is the one place in the sequence where a Founder may reasonably want to look before merging |
| **GAP-3** | Hardware **UNVERIFIED**. No device walk for round 7 — the Nokia is in the Founder's personal use. R-1 is **DONE (artefact) / PARTIAL (device)** | **OPEN by Founder constraint.** Must not become DONE |
| **GAP-4** | Regenerating Golden #1 needs PyMuPDF + 14 GB `poc-out/` + SGK PDFs. Reproducible **only on this Mac** | **OPEN.** Provenance is recorded; the evidence body cannot enter git under D4 |
| **GAP-5** | `#89` is ~118 commits behind `round7`; its own subject verdict is **PARTIAL** (capability proven, nothing delivered to a child) | Handled by Step 4. **The PARTIAL stands** |

---

## 13 · Single clear recommendation

> **Execute steps 1–5 (mechanical), then open one PR `integration/round7-2026-09-06 → main` and
> stop for the Founder.**
>
> Do **not** merge `#79` on its own. It is the safest-looking action and the least useful one:
> it clears 2 of 20 PRs, leaves two stacked layers and 175 commits, publishes a report to `main`
> citing code `main` will not have, and leaves round 8 composing on an unmerged round 7 —
> the exact outcome order 43 §10 forbids.
>
> The reason to merge `round7` is **not** that it closes fifteen PRs. It is that
> `main ⊂ round4 ⊂ round5 ⊂ round6 ⊂ round7` is a **proven strict chain**, that **no `docs/`
> file was deleted in any of its 264 commits**, that the composed tree is **green on suites run
> for this audit** (748/1042 alone, 866/1074 with the four outstanding PRs), and that the merge
> is **conflict-free into `main`**. The PR-count reduction is arithmetic that follows from those
> proofs, not a goal that motivated them.
>
> **One Founder gate: step 6.** Everything before it is mechanical and reversible by
> `git revert -m 1`. **Nothing in this plan deletes a branch.**

**Status semantics preserved throughout: DONE · PARTIAL · FAILED · FALSIFIED · BLOCKED ·
DEFERRED · NOT STARTED. Nothing in this document promotes a PARTIAL to DONE.**
