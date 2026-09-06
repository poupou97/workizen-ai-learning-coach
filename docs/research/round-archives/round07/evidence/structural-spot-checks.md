# Structural spot-checks re-run by the archive builder — round 7

The round-7 consolidated report states that its coordinator verified every number first-hand. This
file records the **archive builder** verifying independently, on **2026-09-06**, against `origin`
and against the artefacts on the Founder's Desktop.

A claim is **PROVEN** here only where the command shown produced the stated result.

---

## 1. GATE E / R-1 — the regenerated Golden #1, verified at the artefact — **PROVEN**

`~/Desktop/wal-evidence/round7-artefacts/fixtures-real/lesson-05-sgk-lich-su-va-dia-li-5-b8.json`,
archived here at `evidence/round7-artefacts/`, parsed directly:

```
sha256(bytes) = 1862f27b2282a4bb7694719a839c78fadc275bc89ed279c50dea299a7ab150f0
```

| measured | round 6 fixture | **round 7 fixture** |
|---|---|---|
| blocks | 52 | **57** |
| block types | withheld 17 · paragraph 18 · activity 6 · heading 4 · question 3 · caption 3 · sourceRef 1 | **the same, plus `image` 5** |
| **withheld regions** | 17 | **17 — id set IDENTICAL** |
| **withheld regions carrying a `crop`** | **0** | **17 of 17** |
| **served text blocks** | 35 | **35 — id set IDENTICAL** |
| `image` blocks | 0 | **5** |
| do the `image` blocks carry text? | — | **no** |
| any withheld block carrying `text` | 0 | **0** |
| blocks carrying a repair record | 6, all withheld | **6, all withheld** |
| repair dispositions | 6/6 `VALIDATED_REPAIR` | **6/6 `VALIDATED_REPAIR`** |
| `repair.servable` | 6/6 `false` | **6/6 `false`** |
| `provenance.repair.trusted` | 0 | **0** |
| `provenance.repair.validatedRepairs` / `onBlocks` / `capped` | 9 / 6 / — | **9 / 6 / 0** |
| `semantic` · `tutorSteps` | 0 · 0 | **0 · 0** |
| title | «… thời kì **B**ắc thuộc» | **«… thời kì Bắc thuộc»** |
| crop files beside the fixture | 0 | **22** |

**This is GATE E's no-regression invariant proved from the bytes, not from a report:** the withheld
id set and the served-text id set are **identical** between rounds 6 and 7, and the five new blocks
are images that carry **no text**. **Nothing became servable; 17 gaps gained a page image.**

*(The `crop` key is present on all 17 withheld blocks — the archive builder checked the key set
directly, rather than trusting the L5b count.)*

## 2. GATE B — the freeze chain, read from the ledger — **PROVEN**

`metrics/frozen-calibration/LEDGER.jsonl`, three lines and no more:

| seq | kind | sha256 | binds |
|---|---|---|---|
| 1 | **policy** | `0dfc5032…` | — |
| 2 | **population** (BLIND-CORE) | `dbadf4ad…` | policy `0dfc5032…` |
| 3 | **population** (BLIND-TEACHING) | `69d1cacc…` | policy `0dfc5032…` |

**No `approval` entry. No `admitted` entry.** The policy is `seq 1`; both populations carry
`binds_policy` naming the policy hash, so **the order is provable from the artefact** rather than
asserted. Frozen at `2026-09-06T06:41:54Z` and `06:47:21Z`, on commits `1e31512` and `8b75a30`.

## 3. The identity claim — **PROVEN, and it needs its exact wording**

```
$ grep -cE '[0-9]{2}-sgk-|Bài [0-9]+|p0[0-9]{2}|lessonNo'  TRUST-CALIBRATION-*.md
TRUST-CALIBRATION-BLIND-PROTOCOL-v1.md : 0
TRUST-CALIBRATION-POLICY-v1.md         : 0
TRUST-CALIBRATION-ROUND7-REPORT.md     : 0
```

**Zero identity-shaped strings in all three calibration documents.**

**And the distinction that a careless reading would lose:** the frozen **payloads** *do* name
lessons — `BLIND-POPULATION-v1.json` holds **120 lessons across 84 books**, `-TEACHING-v1.json`
**120 across 72** — with `sourceDocumentId`, `lessonNo` and `pageStart` present and the **title
hashed** (`title_sha256`, no raw title). That is not a contradiction: a blind *evaluation frame*
must say which lessons are in it, and it was frozen **before** anything could be admitted. The
claim is «no identity in an **admission** context», and it holds. **«Zero lesson identities
anywhere» would be false, and this archive does not say it.**

The population's own `universe` block re-derives **3,679 lessons / 3,381 page-anchored / 238 books
with lessons**, records that both are HISTORICAL BASELINE, and states that **neither is used as a
denominator for any rate in the workstream**.

## 4. Merge debt — re-verified, with a measurement-point correction — **PROVEN**

| check | result |
|---|---|
| Is #73 an ancestor of #79? | **YES** |
| Is `main` an ancestor of #79? | **YES** — `main` is still `61dbfdb` |
| Delta #73 → #79 | **16 commits, 3 files, all `docs/research/`** — `ROUND5-PLAN.md`, `ROUND5-CONSOLIDATED-REPORT-2026-09-06.md`, `ROUND5-AUDIT-97-EVALUATION-SET.md` |
| `main..integration/round4` | **73** commits |
| `main..integration/round5` | **89** |
| `main..integration/round6` | **208** |
| **`main..integration/round7`** | **259** |

**The report says «254 commits»; at the round's final head it is 259.** Measured at the re-audit's
own commit `457a970` it is **255**. The difference is the **four documentation commits that closed
the round** (`1e31512`, `2caafe5`, `2d7c97e`, `74d9db6`). **Same stack, later measurement point —
not a disagreement.** Recorded because a reader re-running the count today will get 259 and should
know why.

## 5. Branch heads and PR state — **PROVEN**

`round7-branch-heads-and-merge-debt.txt`: **4 of 4** workstream heads match §10.1.
`round7-ci-status.txt`: PRs **#94–#97 all OPEN**, `Analyze & Test = SUCCESS`, `mergedAt: null` —
**and every PR from #73 through #93 re-checked in the same pass is still OPEN and unmerged.**

## 6. What was NOT re-run by the archive builder

- **The suites were not re-executed.** Composition CI (0 conflicts · `flutter analyze` clean ·
  **866 Python** · **1106 Dart** · fixture regenerated in-tree with L5b 17/17) is **MEASURED by the
  coordinator**, not re-PROVEN here.
- **No calibration figure was recomputed.** The teaching-critical rates, the ≈0.021 floor, the
  12-error decomposition and the ~0.48 lesson-level probability are **MEASURED by WS-T** on the
  round-5 evidence rows; re-deriving them needs `poc-out/`, which is gitignored and excluded.
- **The 118-block census, the 31 mutilated structures and the title measurement were not
  recomputed** — they need the 238 canonical TSLs and the shipping packs.
- **The device was not touched by the archive builder** — see `08-DEVICE-EVIDENCE.md`. **No frame
  exists to verify.**
