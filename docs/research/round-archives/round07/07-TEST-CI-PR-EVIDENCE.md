# 07 · TEST · CI · PR EVIDENCE

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

Raw evidence: `evidence/round7-pull-requests.json` · `evidence/round7-ci-status.txt` ·
`evidence/round7-branch-heads-and-merge-debt.txt` · `evidence/round7-git-log.txt` ·
`evidence/structural-spot-checks.md`.

---

## 1. INDIVIDUAL CI — four PRs, all green, none merged

*(**PROVEN** — GitHub API, 2026-09-06.)*

| PR | Branch | Head *(re-resolved)* | Head *(as reported)* | Match | CI | `mergedAt` |
|---|---|---|---|---|---|---|
| **#94** | `ws-m/round7-metric-truth` | `a6cae3b` | `a6cae3b` | ✔ | `Analyze & Test = SUCCESS` | `null` |
| **#95** | `ws-s/round7-structured-gap` | `36e4c50` | `36e4c50` | ✔ | SUCCESS | `null` |
| **#96** | `ws-t/round7-trust-calibration` | `5e706c9` | `5e706c9` | ✔ | SUCCESS | `null` |
| **#97** | `ws-r/round7-debt` | `7d37521` | `7d37521` | ✔ | SUCCESS | `null` |

**4 of 4 heads match §10.1.** And re-checked in the same pass: **#89–#93, #79–#88 and #73 are all
still OPEN with `mergedAt: null`.** *Sixteen open PRs across four rounds.*

---

## 2. COMPOSITION CI — third round running, and the one that must not be skipped

Verified in a throw-away worktree from `integration/round7-2026-09-06`, all four branches merged.

| Check | Result |
|---|---|
| Git merge, 4 branches | **0 conflicts** |
| **Fixture regeneration inside the tree** | **L5b 17/17 · VERDICT PASS · placed +22 crops** |
| `flutter analyze` | **No issues found** |
| Python suite | **866 tests OK** (18 skipped) |
| Dart suite | **1106 tests — All tests passed** |

*(**MEASURED** by the coordinator. The archive builder did **not** re-execute the suites — see
`evidence/structural-spot-checks.md` §6.)*

### The composition procedure changed this round, and the change is load-bearing

**The Golden #1 fixture was REGENERATED inside the composed tree, never rsynced.**

`assets/fixtures/` is gitignored, so the fixed artefact **does not travel with the branch**, and the
main checkout still held round 6's crop-less copy. **Rsyncing it — the standing procedure —
re-introduces the defect this round fixed, and the fixture reads as current because its lineage
fields are all intact.** Round 5's stale-fixture trap wearing a new hat.

**L5b now goes FAIL on the stale copy (`0/17`), so it cannot pass silently — but the instruction is
stronger than the guard: regenerate rather than rsync, and check `L5b … 17/17` before building any
APK.** *(Packs were rsynced: they are the verified round-6 rebuild, `verify` 12/12,
`toanExercises` 0.)*

### It did not compose on the first attempt — and the failure caught the coordinator

**WS-M's anti-rot guard** — *«a baselined finding that has disappeared must be removed in the same
commit»* — **fired on its first real encounter**, because the coordinator had repaired the two
round-3 census defects its baseline still asserted were live. **They had worked in parallel.**

The resolution improved on both positions: WS-M **verified the fix behaviourally rather than by
reading the diff**, **withdrew the weaker half of its own argument**, and noted that a broken
committed command is — by the round's own Gate A rule — **a metric that was never re-derivable.**
It then kept the concern **as a live assertion rather than a note**: entries were **moved** to a new
`REPAIRED_FINDINGS` record, on the principle that **a repair is also a change to what old numbers
mean.** Three new guards make a repaired defect's return **fail by name**.

---

## 3. TEST COUNTS

| Scope | Result |
|---|---|
| **Composed round** | **Python 866 OK** (18 skipped) · **Dart 1106 — all passed** · analyze clean |
| WS-T (#96) | Python **800 OK** — 748 before + **52 new** |
| WS-R (#97) | Dart **1,100 passed / 2 skipped** · Python **756 OK / 15 skipped** · analyze clean |
| WS-M (#94) | registry `verify` **18 / 18 re-derive** |
| WS-S (#95) | **238 / 238 documents byte-identical**; 4 Dart mutation checks |

---

## 4. TESTS THAT EXIST TO PREVENT A SPECIFIC FUTURE FAILURE

| Test / mechanism | What it pins |
|---|---|
| **the freeze chain's write-time refusals** | A population **cannot** be frozen before a policy; an admitted set **cannot** be frozen before an approval; **an `admitted` write with no approval raises `PermissionError`.** *A refusal, not a discouragement.* |
| `identity_leaks` at freeze time **+ a test over the documents** | **No lesson or book identity may appear in a calibration document.** *(PROVEN — 0 matches in all three.)* |
| property test on `TRUST = SERVED ∩ admit(…)` | **`trusted ⊆ served` by construction** — activation **cannot serve one new block**. Asserted again on `apply.py`'s output. |
| the round-5 baseline asserted as a test | 643 rows · 354 served · coverage 0.5505 · FTR 0.0734 — **so candidates are re-decisions of a published scoreboard, not a new measurement.** |
| **`CropCoverageTest`** | Rebuilds the very document round 6 placed and asserts **L5 PASS `0/0` and L5b FAIL `0/17` on the same document** — *the gap that shipped, and the assertion that notices if L5b is removed.* |
| **L5b CROP COVERAGE** | Measures the **population**, not the references; `--allow-missing-crops` downgrades to **UNKNOWN, never to PASS**. |
| **L2b** | A cross-method hash match is accepted **only when both sides are digests recomputed this run from the file at `tslPath`**, and the row **names which method each side used**. |
| the R-2 sweep | **4 lesson shapes × 4 evidence standings × all 8 subsets of `viewsSeen` = 128 cases, swept not sampled** — *no combination may propose leaving a lesson without a validated, approved success.* |
| the on-screen «Đã mở» test | **Counts ●/○ marks against the number of available ways** — structural, not a keyword match, because round 6 established a keyword canary fires on real book text and guards nothing. |
| the one-casing-rule source test | **Forbids a second casing rule** anywhere; the R-3 test reads the **rendered text** and asserts *«every uppercase letter of the book's string survives»* rather than *«the function returns string X»*. |
| the ALL-CAPS residue test | **Pins the 108 remaining losses so nobody reads R-3 as fixed.** |
| `titlesLosingCapitals(transform, titles)` | **An activation precondition that is a function, not a promise** — it must return empty on the real population. |
| the **container lint** (WS-M) | Makes `len()`-on-a-keyed-container **fail by name** — the defect that occurred three times across three rounds. |
| the **anti-rot guard** (WS-M) | A baselined finding that has disappeared **must be removed in the same commit**. It fired on its first real encounter. |
| `test_role_map_still_has_no_carrier_for_the_three_roles` | **Nothing became servable** — 238/238 byte-identical, `ROLE_MAP` untouched. |
| the honesty guards, re-verified | Injecting a `TimelineSemantic` into the **published artefact** → **RED**; serving `p039:000` as a paragraph with text → **RED (7 failures)**. |

---

## 5. STANDING LIMITS — all held

| Limit | Held? | Evidence |
|---|---|---|
| **No production trust threshold activated** | **YES** | No `approval` and no `admitted` entry in the ledger *(PROVEN)*; `apply.py` inert; the machinery **refuses** without an approval artefact |
| **Stop at the Founder gate** | **YES** | Steps C–G **NOT STARTED — correctly** |
| No mass corpus reprocess | **YES** | populations are 643 rows, 238 TSLs, 2,623 titles, 120+120 frozen lessons |
| No public SGK distribution | **YES** | crops marked **[LB]**, D4, **not committed** |
| No unrestricted LLM | **YES** | no LLM in any round-7 path |
| No destructive migration | **YES** | round-6 report and its v2 archive **unchanged**; corrections placed **beside** them (C1–C5) |
| Never turn PARTIAL into DONE | **YES** | S5 PARTIAL · R-3b PARTIAL · R-5 DEFERRED · D **not attemptable** |
| **No merge** | **YES** | 16 PRs open across four rounds *(PROVEN)* |

---

## 6. WHAT THE CI EVIDENCE DOES **NOT** SHOW

- **It does not show anything reached a child.** Nothing did.
- **It does not show the fixes work on hardware.** R-1, R-2 and R-3 are **[HU]**. **Widget tests and
  lineage gates are not real-device evidence** — and round 7 has **no device frames at all**
  (`screenshots/NO-DEVICE-FRAMES-THIS-ROUND.md`).
- **It does not show the calibration transfers.** Every rate is on **54 deliberately hard pages**;
  **the blind population exists precisely to test that, and it has not been tested.**
- **A green composition is not a green merge.** No CI anywhere builds what the Founder would merge —
  see `10-OPEN-RISKS-BLOCKERS.md` §4.
- **UNAVAILABLE:** per-PR CI durations for #94–#97 were not recorded.
