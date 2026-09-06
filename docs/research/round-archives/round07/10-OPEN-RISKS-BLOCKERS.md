# 10 · OPEN RISKS AND BLOCKERS

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

Ordered by **what they block**.

---

## 1. THE BLOCKER CHANGED THIS ROUND

Round 6 said the blocker was **the trust decision**. **Round 7 measured that and it is not.**

| # | Blocker | Status | Owner |
|---|---|---|---|
| **1** | **Recognition and role disambiguation.** All 12 teaching-critical errors reduce to **digit corruption** and **a non-question served as a question**, and **neither is visible to any signal a gate can read** — 3 of 6 digit corruptions survive **character-exact two-stack agreement**. **No signal combination bounds teaching-critical error below ≈0.021; a 90 %-clean promise needs 0.0035. A factor of six.** | **OPEN — and it has no owner in round 7** | round 8 (engineering) |
| **2** | **Activation is still a Founder gate** — but activating it now **would not fix the content.** `TRUST = SERVED ∩ admit(…)` means activation **cannot serve one new block**; it can only mark some served blocks trusted, at a teaching-critical rate no bound makes acceptable. | **BLOCKED — Founder** | **FOUNDER** |

> **That reordering is the round's product.** Calibration is finished; it was never the thing in the
> way.

---

## 2. THE OPEN ENGINEERING ITEMS

| # | Item | Status | Note |
|---|---|---|---|
| **3** | **31 mutilated structures served today**, incl. **2 of 2 multiple-choice groups** | **OPEN — the rule is built and OFF** | **31 → 0 at 72 blocks.** *Founder decision: the same shape of trade as round 6's lost timeline.* |
| **4** | **The option letters are outside the agreement measurement** | **OPEN** | `agreement()` at `:1193`, enumerator restored at `:1221`. **The one part that identifies the answer is the part no agreement measurement covers.** **Prerequisite for ever adding the `option` type.** |
| **5** | **22 imprint blocks reach children today** (`heading` 17 · `body` 5) | **OPEN — defect 6 on the lesson path** | A **pipeline lesson-boundary** fix, and the **precondition for `ActivityKind.activity`**. *Does not contradict round 6's «absent (0 of 207)» — that measured the **pack** surface.* |
| **6** | **108 multi-word ALL-CAPS titles lose their proper nouns** | **PARTIAL — Founder decision** | **A** show verbatim (108 shouted titles, nothing false) · **B** keep sentence-casing (readable; asserts 108 times that a proper noun is not one). A third path is **data, not display**. **Pinned by a test so nobody reads R-3 as fixed.** |
| **7** | **`si_expected_exponent` at 0 PASS / 0 FAIL** | **ANSWERED, not fixable here** | Firing it needs a digit recovered on one of 5 lines **that round 6 measured unreadable at every scale** → **recognition**. |
| **8** | **The `unknown_role:*` reason code still lies** | **OPEN, deliberately** | Renaming it without changing the child-facing wording makes that wording **less** truthful. **One coordination item, wording drafted.** |
| **9** | **HO-1 `titleCase` · HO-2 `NextAction.label` · HO-3 `rederive_trust` · N-1 `--doc` · N-3 two hash methods** | **OPEN, each with a named owner** | *Recorded rather than reached across a workstream boundary for.* |
| **10** | **`tool/evidence/**` and `tool/corpus/repair/**` had no round-7 owner** | **N-2, flagged** | WS-R changed both to execute R-1. **An unowned directory that a workstream must edit is a governance gap, not a code gap.** |

---

## 3. RISKS THAT ARE NOT YET FAILURES

| Risk | Evidence | Why it matters |
|---|---|---|
| **No rate measured this round is known to transfer to the corpus** | every calibration figure is on **54 deliberately hard pages** | **This is exactly what the blind population exists to test, and it has not been tested.** A plan sized on these numbers is sized on a hard sample. |
| **The blind population's disjointness is argued, not proven** | the 97-row set's rows **exist only as a summary table** | Declared **in the artefact**, not only in a table. If the sets overlap, the first real measurement is contaminated. |
| **The 30-blocks-per-lesson planning figure comes from one lesson** | round 6's Golden #1 | The ≈0.48 lesson-level probability inherits it — **and an independence assumption that is stated, not demonstrated**. |
| **The 97-row evaluation set has an ambiguous leaf population** | TRUSTED 67, false trust 6/67; separately teaching-critical 5 · display 11 · role 10 — **summing to 26 against 6** | **A published headline metric whose denominator is not stated; the two readings differ by ~1.4×.** Referred to WS-M; **deliberately not used as a bound anchor.** |
| **`procedure_steps` 29 is a LOWER BOUND** | a withheld region carries no text, and a step is recognised by its enumerator **in the text** | **A procedure whose missing step was withheld cannot be seen at all.** Demonstrated by a test rather than papered over. |
| **The group rule does not fully repair the MCQ** | the trailing directive «Hãy chọn đáp án đúng nhất.» sits **after** the options, outside the group | Even with the rule, a child reads *«choose the most correct answer»* **with nothing above it.** **The group definition is incomplete, and extending it is doctrine WS-S declined to write alone.** |
| **The round-3 census ranking rested on a wrong input** | `pack_wiring['toanExercises'] = 0` **for every candidate** — *a column of zeroes that looked like absence of data and was absence of flattening* | **Any candidate ranked or dismissed on that column was ranked on a wrong input.** Round 7 does not lean on it; **round 8 must not.** |
| **Published round-3 census outputs are no longer reproducible from the fixed code** | the scripts were repaired | Filed as a **live assertion**, not a note: **a repair is also a change to what old numbers mean.** |
| **The cp-backup mutation rule has now been skipped twice** | WS-M, and Lane E2 in round 5 — both destroyed uncommitted work with `git checkout --` | *And: a mutation that «survives» because it never applied is not evidence.* |

---

## 4. THE MERGE DEBT IS NOW THE STRUCTURAL RISK

**Four stacked unmerged integration layers. `integration/round7` is 259 commits ahead of `main`.**
*(PROVEN — recomputed; the report's 254 was measured four documentation commits earlier.)*

```
main (61dbfdb)
 └─ #73  integration/round4    73 commits   ACCEPTED, unmerged
     └─ #79  integration/round5    89        (+16, documentation only)
         └─ integration/round6    208
             └─ integration/round7  259
```

| Risk | Why it is not theoretical |
|---|---|
| **No CI ever builds what the Founder would merge** | Per-PR CI builds each branch against its own base; **only the disposable composition builds the whole.** Round 6 proved the gap: three stale test premises and a plugin-registry defect were **invisible to per-PR CI**. |
| **Bisect is compromised** | A regression introduced in round 5 and surfacing in round 7 must be bisected across **259 commits containing four merge fronts.** |
| **Rebase cost compounds** | Round 6 already paid it once — WS-C carried WS-A's commit, `patch-id` proved a duplicate, a rebase was required to make PR #90 reviewable. |
| **`main` is ~4 rounds stale** | Any hotfix would branch from a tree predating silent-loss accounting, the repair framework, recognition, and the honest Bài 8 fixture. |

**The recommendation is unchanged and re-verified: MERGE #79 · CLOSE #73 AS SUBSUMED · HOLD the
rest.** #73 **is** an ancestor of #79, `main` **has not moved**, the delta is **16 commits / 3 files
/ documentation only** *(PROVEN)*. **Merging #79 carries exactly the code risk of #73 — already
Founder-ACCEPTED — plus a report, and changes no APK.**

> **If the Founder prefers integration branches to stay permanently unmerged, that is legitimate —
> but it should be stated as policy**, because at four layers they no longer function as a delivery
> path.

---

## 5. THE DEVICE GAP

**Three fixes are finished, tested, mutation-checked — and unproven where it counts.** R-1, R-2 and
R-3 are all **[HU]**, and **round 7 captured no frames at all.**

Rounds 5 and 6 each closed with a real-device walk that found defects **no test had**. **Round 7
fixed two of round 6's device-found defects and could not check its own work the same way.**

The walk is **five specified steps** (`08-DEVICE-EVIDENCE.md` §3), plus one this archive adds:
**confirm `L5b … 17/17` before building**, because rsyncing `assets/fixtures/` silently restores the
crop-less artefact **whose lineage fields all read as current.**

---

## 6. LARGE / EXTERNAL DATA — recorded, not copied

Inventory: `manifests/large-data-inventory.txt`.

| What | Path | Size | In this archive? |
|---|---|---|---|
| SGK PDF source | `nguon-chi-thuc/` | **9.8 GB** | **NO** — copyright |
| All derived artefacts | `poc-out/` | **14 GB** | **NO** |
| Round-7 artefact trees | `poc-out/round7/` | **18 MB** | **NO** — inventory only |
| Rounds 5–6, still referenced | `poc-out/round5`, `round6` | 341 MB · 150 MB | **NO** |
| **The regenerated fixture + 22 crops** | `~/Desktop/wal-evidence/round7-artefacts/` | ~5.8 MB | **YES** — `evidence/round7-artefacts/`, **[LB]** |
| **The frozen calibration payloads** | `tool/corpus/thresholds/frozen/` | ~134 KB | **YES** — `metrics/frozen-calibration/` |
| **Device frames** | — | — | **NONE EXIST.** `screenshots/NO-DEVICE-FRAMES-THIS-ROUND.md` |

### How to reproduce round 7's numbers

1. Check out the workstream branch (heads in `evidence/round7-branch-heads-and-merge-debt.txt`).
2. Restore the SGK source at `nguon-chi-thuc/` — **the Founder's local copy is the only one.**
3. **Metrics:** `tool/metrics/` — the registry carries **a runnable re-derivation command per
   metric**; `verify` should return **18/18**.
4. **Calibration:** the frozen payloads in `metrics/frozen-calibration/` **carry the derived
   figures**, so §3 of the policy document is re-derivable **without `poc-out/`**. `measure.py
   --dry-run` demonstrates one PASS and three refusal modes. **Steps C–G refuse without an approval
   artefact — do not attempt to bypass that; it is the gate.**
5. **Structured gap:** `python3 tool/corpus/structured_gap_census.py --lessons
   poc-out/trusted-corpus/tc-v2/tc2-p1/lessons`.
6. **Golden #1:** the two commands in `reports/ws-r-round6-debt/ROUND6-DEBT-TRIAGE.md` §1 —
   `tsl_projection` then `golden_delivery … --require-repair --place`. **Check `L5b … 17/17`.**
   **Regenerate; do not rsync.**

**Clean-clone warning, sharpened again.** Round 5: gitignored files make tests pass falsely. Round
6: three real defects were green **on a clean clone** and visible only in a composed tree with real
assets. **Round 7 adds a third mode — rsyncing a gitignored asset can silently restore a *fixed*
defect, with the stale artefact's lineage fields all reading as current.** Reproduce all three ways.

---

## 7. WHAT IS **NOT** A RISK

- **`trusted = 0` and nothing reaching a child are not failures this round.** The plan declared in
  advance that a truthful zero is the acceptable outcome, and the recommendation **predicts its own
  zero and seals that prediction in the frozen payload.**
- **Gate D being unattempted is not a shortfall.** The plan fixed it as **not attemptable**.
- **A workstream withdrawing its own claim** (WS-T twice, WS-S once) is the most valuable thing it
  can do.
- **The composition failing on the first attempt** is the anti-rot guard working — **on its author.**
