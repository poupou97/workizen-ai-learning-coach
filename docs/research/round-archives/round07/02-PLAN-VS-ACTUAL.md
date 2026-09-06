# 02 · PLAN vs ACTUAL

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

Plan of record: `ROUND7-PLAN.md` (`1e31512`). Allowed statuses: **DONE · PARTIAL · FAILED ·
FALSIFIED · BLOCKED · DEFERRED · NOT STARTED**. **Nothing was promoted from PARTIAL to DONE.**

---

## 1. Workstreams: four planned, four ran

| WS | PR | Head *(verified)* | CI | Status |
|---|---|---|---|---|
| **M · METRIC TRUTH** | **#94** | `a6cae3b` | PASS | **DONE** — GATE A met |
| **S · STRUCTURED CONTENT GAP** | **#95** | `36e4c50` | PASS | **DONE, with S5 PARTIAL** |
| **T · TRUST CALIBRATION** | **#96** | `5e706c9` | PASS | **DONE** — GATES B and C met; D deliberately not attempted |
| **R · ROUND-6 DEBT** | **#97** | `7d37521` | PASS | **DONE, with one DEFERRED and one BLOCKED** |

*(**PROVEN** — 4 of 4 heads re-resolved from `origin` match §10.1; CI and `mergedAt: null` re-read
from the GitHub API.)*

---

## 2. WS-M · METRIC TRUTH — PR #94

| Planned | Status | Actual |
|---|---|---|
| Permanent rule: no derived metric accepted unless re-derivable from leaf records | **DONE** | Enforced **in code**, not doctrine — `tool/metrics/**`, plus a container lint and a regression baseline |
| Metric Definition Registry, nine fields per metric | **DONE** | **18 metrics, 18/18 re-derive** to their recorded values on the 2026-09-06 artefacts |
| Resolve or **formally deprecate** «total activities» | **DONE** | §3 below |
| `toanExercises` incident as a regression example with a test | **DONE** | The container-shape defect is now a named, tested regression |

### «Total activities» — resolved by deprecation, which is the honest resolution

| value | what it actually counts | verdict |
|---|---|---|
| **248** | seven-family activity **leaf rows** on the pack build *before* the Founder §3 fail-closed change — i.e. `207 + 41`. A correct earlier **value of `ACTIVITY_LEAF_COUNT`**, not a different metric | **SUPERSEDED** — still valid as the historical value of a named metric on a named build |
| **217** | `207` activity leaf **rows** `+ 10` `toanExercises` container **KEYS** — **a sum of two different units** | **DEPRECATED** — it counts no population and answers no question anyone can state |
| **161** | `tvReadings 66 + tvWritings 54 + toanExercises 41` — leaf rows of **three of seven families**, published under a whole-corpus name, **silently dropping 87 of the rows it purports to total** | **DEPRECATED as a total** — the aggregation is sound; the family set is arbitrary and was never declared |

> **The phrase «total activities» is itself DEPRECATED and must not enter round-7 metrics.**

**This closes the item the round-6 archive raised and could not settle.** It was right that the
metric was undefined; **WS-M's answer is that it was never one metric.** *(The 217 was the archive
builder's own error — see `04-FAILURES-AND-FALSIFICATIONS.md` §7.)*

---

## 3. WS-T · TRUST CALIBRATION — PR #96

| # | Planned | Status | Actual |
|---|---|---|---|
| 1 | Candidate policy + bound from **pre-existing evidence only** | **DONE** | 5 candidates, 6 bound options, frozen `0dfc5032…`. **Every clause carries the prior finding it comes from. Nothing new was extracted, annotated or measured.** |
| 2 | Frozen blind population, hashed, disjoint from tuning data | **DONE, with a declared weakness** | Two populations (`dbadf4ad…`, `69d1cacc…`), **120 lessons each**, from 2,536 eligible after excluding 44 contaminated books. **Disjointness from the 97-row set is argued, not proven — its rows do not exist as data.** |
| 3 | Audit + measurement machinery, ready to run, **not run** | **DONE** | `apply.py` (inert) · `audit_sheet.py` (worklist + sealed key) · `measure.py`. **52 tests.** Dry run shows one PASS and **three refusal modes**. |
| 4 | Trade-offs **without lesson identities** wherever possible | **DONE** | **No book id, lesson number or page appears in any artefact or document this workstream produced.** Enforced by `identity_leaks` at freeze time **and** by a test over the documents. *(PROVEN — 0 identity-shaped matches in all three.)* |
| 5 | Bound options with consequences, and a recommendation | **DONE** | Six options, each with audit cost and **predicted outcome**. Recommendation **C2 · PROSE under BOUND-2**, expecting a truthful zero. |
| — | Apply / audit / measure / allow a slice (C–G) | **NOT STARTED — correctly** | Requires Founder approval. **The machinery refuses without it.** |

**Item 2 is DONE *with a declared weakness*, and the weakness is in the artefact, not only in a
table** — which is the difference between a caveat and a record.

---

## 4. WS-S · STRUCTURED CONTENT GAP — PR #95

| # | Planned | Status | Actual |
|---|---|---|---|
| S1 | Re-derive the 118 from leaf records | **DONE** | 118 = footnote 64 · activity 50 · option 4, exactly |
| S2 | Inspect the 4 `option` blocks **first and with most care** | **DONE** | Three independent reasons **not** to add the type |
| S3 | Decide `footnote` (64) | **DONE — RECOMMEND AGAINST** | Only **10 of 64** have a machine-resolvable referent in text a child can see |
| S4 | Decide `activity` (50) — genuine gap or mapping gap? | **DONE — it IS a mapping gap, and still DEFER** | 5 of the 50 are the publisher's colophon |
| S5 | Bounded model change improving truthful representation | **PARTIAL** | `BlockGroup` + group machinery, **both inert by default**. **PARTIAL because it is built and not applied — and it is not DONE until a Founder throws the switch** |
| S6 | Confirm nothing became servable | **DONE** | **238 / 238 documents byte-identical**; `ROLE_MAP` untouched; guarded by tests |
| S7 | Defect 8 measured on the lesson path | **DONE — and worse than the option count suggested** | **31 mutilated structures** |

> **«Never turned PARTIAL into DONE: S5 is PARTIAL and stays PARTIAL.»** — WS-S's own words.

---

## 5. WS-R · ROUND-6 DEBT — PR #97

| item | Status | Actual |
|---|---|---|
| **R-1** 17 gaps with no page crops | **ROUND7-P0 · DONE** at the artefact · **[HU]** on the device | 17/17 crops, 22 placed, +5 figure images; **root cause was structural, not an oversight** |
| **R-2** the «Về mục lục» contradiction | **ROUND7-P0 · DONE** · **[HU]** | R5 now yields `keepGoing` and **never instructs leaving**; 128 cases **swept, not sampled** |
| **R-3** lowercased historical proper noun | **ROUND7-P0 · DONE** · **[HU]** | One casing rule where there were seven call sites; a source test forbids a second |
| **R-3b** the ALL-CAPS residue | **ROUND7-P1 · PARTIAL — Founder decision** | 108 multi-word ALL-CAPS titles still lose proper nouns; **pinned by a test so nobody reads this as fixed** |
| **R-4** `si_expected_exponent` abstaining | **ROUND7-P0 · ANSWERED; 2 defects fixed** | The premise was wrong: **it was never asked.** Still 0 PASS / 0 FAIL — **firing it needs recognition** |
| **R-5** recognition generalisation | **ROUND7-P1 · DEFERRED** | **No recognition workstream exists this round.** Deferred **with a population contract**, not an intention |
| Device walk | **BLOCKED** | §4 of the triage; `08-DEVICE-EVIDENCE.md` |

**The triage's own rule, and it held:** *«Nothing vanishes from the roadmap without an explicit
deferral and a reason.»* **30 rows**, every round-6 carried item, each with a verdict and an owner.

---

## 6. What the plan assumed that turned out not to hold

| Plan assumption | What was found |
|---|---|
| A trust threshold is the thing standing between the pipeline and a trusted slice | **FALSIFIED.** The gap between what any threshold achieves (≈0.021) and what a 90 %-clean promise needs (0.0035) is **a factor of six**, and the residual errors are **invisible to every signal a threshold can read** |
| A3's round-5 curve is a menu of trust thresholds to pick a point on | **FALSIFIED.** It is a curve over **guard waivers** — an axis of *loosening*. A trust threshold moves along the **opposite** axis. **Reading it as a menu would have produced a policy that serves new content in the name of trusting it** |
| The `held_out` flag marks a usable holdout | **FALSIFIED.** The published curve **pooled all 643 rows including the 181 held-out**. **The repository contains no pre-existing blind population** |
| Tightening role confidence buys safety | **FALSIFIED.** A 0.70 floor moves false trust 0.0734 → 0.0593 but teaching-critical **0.0339 → 0.0407 — the wrong way** — and removes **every block of continuous prose** |
| Teaching-critical error ⊆ false trust | **FALSIFIED.** Of 354 served rows: 7 both, 19 false-trust only, **5 teaching-critical only.** A bound on false trust alone misses them |
| The 118 blocks are «the cheapest win on the board» | **FALSIFIED.** A servable type is recommended for **zero**; adding all three removes **1 of 31** mutilations |
| Adding the types would at least be safe | **FALSIFIED for `option`** — it converts a **loud** mutilation into a **quiet** one |
| Rsyncing `assets/fixtures/` is the standing composition procedure | **DANGEROUS this round** — it silently re-introduces the crop-less artefact **whose lineage fields all read as current** |

---

## 7. Timeline

| Time (UTC, 2026-09-06) | Event | Source |
|---|---|---|
| — | Round-7 plan committed `1e31512`, **gates fixed before any work** | git log *(PROVEN)* |
| **06:41:54Z** | **Policy frozen** — `0dfc5032…`, `seq 1` | `LEDGER.jsonl` *(PROVEN)* |
| **06:47:21Z** | **Both blind populations frozen** — `dbadf4ad…`, `69d1cacc…`, `seq 2` and `seq 3`, each binding the policy hash | `LEDGER.jsonl` *(PROVEN)* |
| — | WS-R read-only device check: **third-party media app in the foreground, unchanged over 8 s** ⇒ disconnected | triage §4 *(MEASURED)* |
| — | Coordinator's later read-only check: device **appeared free**; **the Founder's instruction stood regardless** ⇒ disconnected | coordinator *(OBSERVED)* |
| — | PRs #94–#97 opened, all CI green | GitHub API *(PROVEN)* |
| — | Composition verified; **fixture REGENERATED in-tree, never rsynced**; the anti-rot guard fired and caught the coordinator | consolidated §10.1 *(MEASURED)* |
| — | `457a970` merge-debt re-audit · `2caafe5` corrections · `2d7c97e` consolidated report · `74d9db6` composition CI | git log *(PROVEN)* |

**The freeze timestamps are the round's most important five minutes:** the policy exists **six
minutes before** the populations, and both populations name the policy's hash. **That ordering is
Gate B, and it is provable from a file rather than from a promise.**
