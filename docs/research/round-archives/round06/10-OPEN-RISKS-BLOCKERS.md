# 10 · OPEN RISKS AND BLOCKERS

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

Ordered by **what they block**.

---

## 1. THE SINGLE BLOCKER

| # | Blocker | Status | What it blocks | Owner |
|---|---|---|---|---|
| **1** | **No production trust threshold.** `THRESHOLDS.json` does not exist; `trusted` computes to **0 by construction**. | **BLOCKED — Founder gate** | **Everything that is left.** `SOURCE TRUST 0/97` · `eligible for teaching 0` · `PEDAGOGY REALITY 7/17` · the servable structured-content carrier · **and the seven dated events on Golden #1**, which are repaired, validated and still withheld. *The pipeline can now detect, account, recognise, repair, validate and carry — and it may not serve.* | **FOUNDER** |

**No amount of further engineering moves any of those.** That is the round's own conclusion and
this archive agrees with it independently: the six `VALIDATED_REPAIR` regions on the shipped fixture
are all `servable: false`, and the code has **no path** that could set otherwise *(PROVEN)*.

---

## 2. THE OPEN ENGINEERING ITEMS, IN COST ORDER

| # | Item | Status | Note |
|---|---|---|---|
| **2** | **The 118-block model gap** — `footnote` 64 · `activity` 50 · `option` 4, withheld **because the app has no matching type** | **OPEN** | **A model gap, not a data gap** — three block types in `lib/core/lesson_model/**`. **The cheapest win on the table.** The 4 `option` blocks are exactly **defect #8** from the 97-row audit: a **mutilated multiple-choice set**, the shape where withholding is *not* the safe move. Changes what a child reads ⇒ needs a wording decision first. |
| **3** | **G1 — the 17 gaps on Golden #1 carry no page crops** | **OPEN** | The device walk's **one FAIL**. WS-C's document was built `--no-crops`; **WS-D's own bridge builds 20 crops from the same TSL.** A one-line re-run, returned to WS-C. |
| **4** | **G2 — long `bookTitle`/`subject` strings** | **OPEN** | `curriculum-structure.json` did not resolve in WS-C's sandbox. **Not wrong, just long.** |
| **5** | **The Next Action runtime tells a child to leave a lesson they just opened** | **OPEN** | «SAM gợi ý: Về mục lục» with reason «Con đã đi qua các cách học của bài này», while «Đã mở» shows one view opened. Born in `lib/core/agenda/**`; **returned to its owner, not patched.** |
| **6** | **The lesson title is lowercased at the display layer** | **OPEN** | «thời kì **b**ắc thuộc» — a sentence-case rule applied to a **historical proper noun** in an app for children. *(PROVEN to be a display defect: the data says **B**.)* |
| **7** | **13 regions carry three reasons**, the third being a pre-existing agreement-stage `empty` code with an unhelpful name | **OPEN** | **Not renamed** — it is an agreement guard, not a role guard, and renaming touches thresholds tooling. Recorded for the agreement layer's next owner. |
| **8** | **`rederive_trust` does not pass `formula_structured`** | **OPEN, fail-closed** | It can only *add* a withhold, never remove one. Pre-existing, **not changed**, recorded. |
| **9** | **`repair/run_gold.py::PERMISSION_REASONS` lacks the new `unread:*` codes** | **OPEN** | Arguably correct — *a lost arithmetic expression is a fidelity failure, not a permission one* — but it is a behaviour change in another workstream's file and was **left for WS-C to decide.** |

---

## 3. RISKS THAT ARE NOT YET FAILURES

| Risk | Evidence | Why it matters |
|---|---|---|
| **The R13 fix may not generalise past the 29 ledgers measured** | 1,878 regions, three independent populations, one a holdout, two loss profiles, five unselected lessons — **but not the whole corpus** | Every rate the project publishes depends on conservation holding **everywhere**, not on 29 lessons. **HYPOTHESIS**, and the round says so. |
| **Recognition's holdout number is far below its development number** | digit recall **0.181** (HOLDOUT-3) vs **0.500** (DEV) | *The honest expectation for the corpus is much lower than the development figure.* Any plan sized on 0.500 is sized wrong. |
| **`3,650` is a measurement, not an approved denominator** | 63 books contribute **zero** rows; 291 identities are unanchored | Until the Founder rules, **`3,679` stays HISTORICAL BASELINE ONLY** and must be labelled beside every use. |
| **Over-withhold rates are no longer comparable across the fix** | withheld 135→144, 124→147, 30→37 | The base grew because always-refused regions became **visible**. **Comparing a post-fix rate with a pre-fix rate without saying so would manufacture a regression.** |
| **False demotion is a real, measured exposure** | Golden #1: **2 blocks demoted**; round-5 prior **demotion precision 0.250** on 4 | A ledger-honouring projection **cannot serve anything wrong, but it can withdraw something right.** Published beside the restores, never folded in. |
| **Two of four renderer families have no real data** | `conceptMap` **0** · `timeline` **0** instances across 238 lessons | Building a fifth family before a census would repeat exactly what round 5 was told not to repeat. |
| **SAM's teaching reach is one lesson in 238** | 0.004 | The tutor path is effectively unmeasured at corpus scale. |
| **165 of 238 lessons open Trực quan to «Chưa có sơ đồ»** | 0.693 | Honest, and a large share of the product surface is currently an empty state. |
| **`si_expected_exponent` abstained on all 171 rows** | WS-B | *An independent validator that never fires is not yet an independent validator.* |
| **The merge debt is compounding** | #73, #79 open; round 6's base is a synthetic composition of nine round-5 branches | **Round 7 would compose a composition.** |

---

## 4. THE NEAR-MISS THAT MUST NOT RECUR

**The round's deliverables existed only inside an ephemeral scratchpad worktree.**

`assets/fixtures/real/` and `assets/pack/` are **gitignored**. The Golden #1 fixture, the Bài 17
fixture and the 12 rebuilt packs — *the exact artefacts the GATE E device walk consumed* — were not
in git and not on the Desktop. The coordinator copied them to
`~/Desktop/wal-evidence/round6-artefacts/` **before that worktree was removed.**

> **Had the worktree been cleaned first, GATE E's artefacts would have been unrecoverable.** The
> seven frames would have shown a lesson nobody could re-derive, and the fixture hash in the
> manifest would have pointed at nothing.

This archive contains them *(PROVEN — the fixture's sha256 matches the device manifest exactly, and
all 12 pack hashes match)*. **Recommendation: an evidence artefact that a gate depends on must be
copied out of an ephemeral worktree at the moment the gate is claimed, not afterwards** — the same
discipline round 5's lineage gate applies to hashes, applied to file *survival*.

---

## 5. THE PACK REBUILD — settled, with one derived metric still undefined

**`toanExercises` 41 → 0 is PROVEN**, recomputed by the archive builder from the two pack sets
archived in `evidence/round6-artefacts/`:

| | `packs-STALE-before` | `packs` (GATE E) | delta |
|---|---:|---:|---:|
| **`toanExercises`** | **41** (g4 **26** · g5 **15**) | **0** | **−41** |
| every other family | 66 / 54 / 46 / 36 / 4 / 1 | **unchanged, to the item** | 0 |
| **total activities** | **248** | **207** | **−41** |

**248 − 41 = 207.** WS-D's figures were right throughout.

### A correction of the archive builder's own

A first draft of this archive reported **217 → 207** and **`toanExercises` 10 → 0**, and raised it
as an unresolved discrepancy. **It was a counting error, not a discrepancy.** `toanExercises` is a
**dict keyed by lesson number whose values are lists of expressions**; `len()` on it returns
**keys**, so 10 *lessons* were reported as 10 *expressions*. Command, working and the corrected
one-liner are in `evidence/structural-spot-checks.md` §8.

**Recorded here rather than silently fixed**, because that is the doctrine every round in this
project runs on — and because *the failure mode is worth naming*: **a metric read off a container
without checking the container's shape.** It is the same family as the round-6 findings it sits
beside — `empty_block` misstating what was lost, a dispose row merging the wrong candidate's
verdict, a field-name guard blind to identity inside a value. **A number that is the right type and
the wrong quantity passes every check that is not a re-derivation.**

### The one figure that is still not settled

**«Total activities» is a derived metric with no written definition**, and at least three sums are
in circulation over the *same twelve files*:

| sum | value | how it is obtained |
|---|---:|---|
| leaf items across all seven families | **248 → 207** | the definition used here, and the one that reconciles with 41 |
| container keys | 217 → 207 | the archive builder's first draft |
| a third naive sum | **161** | reported by the coordinator over the same files |

**`toanExercises` does not depend on the choice; the activities total does.** Nothing in the
repository defines it. **Status: UNRESOLVED — a definition, not a measurement**, and one line in a
doc fixes it. Flagged in `12-NEXT-ROUND-PLAN.md` §3 as an item round 7 does not currently carry.

### The provenance observation stands — and now points the other way

The archived backup identifies itself as the **2026-09-05T04:37Z** build
(`packVersion g4-20260905T0437Z-07a24504`, `attachmentRule capped-toc-v1`) — **the same build round
5's device walk used**, per the round-5 device manifest.

With the count corrected this is no longer a caveat against the 41. **It is a finding:** the APK a
child was shown in round 5 **carried all 41 fabricated expressions**, and round 6's GATE E build is
where they stopped shipping. *That is the round-5 archive's prose claim — «no APK built on this Mac
carries any of this round's accuracy corrections» — turned into a dated, hashed fact.*

**What matters to a child, unchanged by any of the above:** the packs that shipped carry **zero
`toanExercises`**, and the 41 that vanished were **the fabricated ones**.

---

## 6. LARGE / EXTERNAL DATA — recorded, not copied

**This archive contains no corpus bytes.** Inventory: `manifests/large-data-inventory.txt`.

| What | Path | Size *(measured 2026-09-06)* | In this archive? |
|---|---|---|---|
| SGK PDF source | `nguon-chi-thuc/` | **9.8 GB** | **NO** — copyright |
| All derived artefacts | `poc-out/` | **14 GB** | **NO** — derivative works |
| Round-6 artefacts | `poc-out/round6/` | **144 MB** | **NO** — inventory only |
| ↳ golden · legacy · recognition · accounting · ws-c · ws-d | | 31 / 103 / 9.1 MB / 172 KB / 324 KB / 876 KB | **NO** |
| Round-5 artefacts, still referenced | `poc-out/round5/` | 341 MB | **NO** |
| **Device frames** | `~/Desktop/wal-evidence/round6-ws-d/` | ~1.6 MB | **YES — all 7**, `screenshots/` |
| **The GATE E packs + the stale set + both real fixtures** | `~/Desktop/wal-evidence/round6-artefacts/` | ~1.3 MB | **YES** — `evidence/round6-artefacts/` |

### How to reproduce round 6's numbers

1. Check out the workstream branch for the number you want (heads in
   `evidence/round6-branch-heads.txt`).
2. Restore the SGK source at `nguon-chi-thuc/` — **the Founder's local copy is the only one, and it
   must never be committed.**
3. **Accounting:** `python3 tool/corpus/accounting/ledger.py audit` (exits non-zero on any
   UNACCOUNTED region); `--historical` measures a round-5 artefact without pretending its numbers
   changed. Populations are declared in `metrics/golden-slices.json`. Run the **determinism
   control** first — re-running SDM+TSL with unchanged code must produce a byte-identical ledger.
4. **Canonical identity:** `python3 tool/corpus/accounting/lesson_identity.py report`.
5. **Recognition:** build `ocr_crop` (`swiftc -O -o poc-out/bin/ocr_crop tool/ocr/ocr_crop.swift`),
   then `study.py dev` · `study.py sdm` · `study.py holdout3 14` · `exponent.py` · `symbols.py
   roman`. Contact sheets — *which are what decided every correctness figure* — land beside the
   ledgers under `poc-out/round6/recognition/`.
6. **Repair projection:** the exact `python3 -m repair.tsl_projection` invocation is in
   `reports/ws-c-repair-integration/REPAIR-INTEGRATION-ROUND6.md` §3.
7. **Lineage:** `tool/evidence/fixture_lineage.py --require-repair`. **Hash both ways** — the
   committed bridge hashes file bytes, the repair path hashes canonical JSON; `shasum -a 256` alone
   will disagree and look like tampering.

**Clean-clone warning, and round 6 sharpened it.** Round 5's lesson was that gitignored files make
tests pass falsely. **Round 6 found the opposite failure: three real defects were green *on a clean
clone* and visible only in a composed tree with real assets synced in.** Reproduce **both** ways.

---

## 7. WHAT IS **NOT** A RISK

- **`eligible for teaching = 0` is not an engineering failure.** It is the Founder's gate working,
  and the Founder wrote the escape hatch in advance: *«a truthful zero is acceptable if evidence
  demands it».*
- **Coverage falling because wrong content was removed is a correctness gain** — 41 (or 10)
  fabricated expressions and a fabricated timeline, with the counts named.
- **A workstream falsifying its own rule** (WS-B twice, WS-C once, WS-D once) is the most valuable
  thing it can do.
- **Withheld counts rising** is the accounting fix working, not a regression — *provided nobody
  compares the rate across the change without saying so.*
