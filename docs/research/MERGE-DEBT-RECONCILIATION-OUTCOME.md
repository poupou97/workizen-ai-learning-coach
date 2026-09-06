# Merge-debt reconciliation — OUTCOME

**Executed 2026-09-06 under Founder order 44.** Rounds 4–7 are on `main`.

| | |
|---|---|
| **`main` HEAD** | **`14df3ec`** — «Rounds 4-7 → main: merge-debt reconciliation (Founder order 44)» |
| Commits added | **306** (previous `main` was `61dbfdb`) |
| Stacked unmerged layers | **4 → 0.** `integration/round7` residual depth vs `main`: **0** |
| Open PRs | **20 → 0** |
| Branches deleted | **none** — 33 preserved for provenance |
| CI on `main` | **success** |

## What this action was

**An integration and governance action.** Explicitly **not**:

- not a retroactive research acceptance
- not a change to what the product may serve
- not a delivery

`trusted = 0` and `eligible for teaching = 0` are unchanged and remain type invariants. **Packs are
gitignored, so no APK changed.** This cleared governance debt.

## Round 5 — no retroactive acceptance

Round 5 **never received a Founder acceptance verdict** (rounds 4, 6 and 7 did). It scored
**8 PASS · 1 PARTIAL · 1 FAIL**, criterion 4 («correct served / coverage begins to recover») being
the FAIL. Its lane code is now on `main`. **That does not make round 5 accepted**, and no document
in this repository claims it does.

## Safety evidence gathered before merging

| Check | Result |
|---|---|
| Ancestry | `main ⊂ round4 ⊂ round5 ⊂ round6 ⊂ round7` — strict chain, no divergence |
| **`docs/` deletions across the whole range** | **zero** — research history is strictly additive, so no FALSIFIED / PARTIAL / negative finding could be lost by merging |
| `patch-id` over the range | one duplicate, and it is the round-6 merge-debt audit *document* |
| Containment | 15/20 PRs already inside round 7; #94, #95, #96, #89, #98, #99 merged in; **#97 ⊂ #95** |
| D4 material tracked | **none.** Only `.gitkeep` under `assets/fixtures/real/`; the 5 tracked PNGs are `synthetic/`; the real fixture is gitignored at `assets/fixtures/.gitignore:7` |
| `flutter analyze` | No issues found |
| Python | **866 OK**, 18 skipped |
| Dart, fixture present | **1106 passed**, 16 skipped |

## ⚠️ SKIPPED / UNVERIFIED — stated, not smoothed over

**CI GREEN != GOLDEN CHAIN VERIFIED.**

The real Golden #1 fixture is gitignored under D4, so CI never has it. Measured directly:

| | passed | skipped |
|---|---|---|
| with the fixture (local) | **1106** | 16 |
| **without it (CI's actual state)** | **1097** | **25** |

**Nine tests skip on CI**, and the suite still prints «All tests passed». Among the skipped are the
repo's highest-value assertions: *a validated repair stays withheld* · *no repaired text reaches a
child*. Verified locally instead, with the fixture **regenerated, never rsynced**:
`L5b 17/17 crops · VERDICT PASS · trusted 0`.

**ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION.**

Also still true and unchanged by this merge:

- **R-1 (17 lesson gaps now carrying page crops) — HARDWARE UNVERIFIED.** No device walk. The Nokia was in personal use; on Founder instruction it was not touched.
- **Golden #1's 22 SGK page crops and 5 figure images — LICENSING-DISTRIBUTION BLOCKED** under D4. INTERNAL / RESEARCH ONLY.
- **TECHNICALLY VALIDATED != HARDWARE VERIFIED != DISTRIBUTION RIGHT.**

## Canonical record status

Closed during this task: **45 round-archive documents** that existed only inside review ZIPs and a
session-scoped scratchpad (`docs/research/round-archives/`) · **44 Founder task orders**, verbatim
(`docs/founder-orders/`) · the round-6 GATE E device manifest · the D4 classification of archive
identities · the Desktop-only rounds index.

Governance now canonical: `docs/governance/REPOSITORY-SOURCE-OF-RECORD.md`.

## Next bottleneck

**Recognition + role disambiguation** — see `NEXT-RESEARCH-DIRECTION.md`. **No Round 8 was opened
by this task.**
