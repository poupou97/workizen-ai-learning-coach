# CI VERIFICATION SEMANTICS — WAL-218

**CI GREEN ≠ GOLDEN CHAIN VERIFIED.**
What this repository's CI can prove, what it cannot, and what it now says out loud.

- Branch `wal-218/ci-false-green` · base `main` = `6fd728d` · measured 2026-09-06
- Governing rule: **ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION**
- Unchanged by this work: `trusted = 0`, `eligible for teaching = 0`, no threshold activated

---

## 1. The defect, measured

The Golden #1 fixture — `assets/fixtures/real/lesson-05-sgk-lich-su-va-dia-li-5-b8.json` —
is the only artefact where the whole delivery chain is pinned end to end:

```
source → SDM → repair ledger → ValidatedRepair → projected TSL → LessonDocument
  → assets/fixtures/real/ → WorkspaceCatalog picks the REAL path → three Learning Views
```

It is gitignored under **Founder D4** (verbatim SGK text and page crops are INTERNAL /
RESEARCH ONLY). So CI never has it, nine assertions turn into `markTestSkipped`, and the
suite's last line is the same either way.

Measured on `main` (`6fd728d`), whole suite:

| configuration | passed | skipped | last line |
|---|---:|---:|---|
| Golden #1 present (local dev machine) | 1108 | 33 | `All tests passed!` |
| Golden #1 absent | 1099 | 42 | `All tests passed!` |
| both real fixtures absent — **the runner's true state** | 1084 | 57 | `All tests passed!` |

**Nine tests, and nothing in the output distinguishes the runs.** Identified exactly by
diffing the per-test JSON reporter output between the two configurations:

| id | test | claim |
|---|---|---|
| GC-01 | `golden1_history_test.dart` | catalog loads the REAL path, does not fall back to the synthetic one |
| GC-02 | `golden1_history_test.dart` | all five version fields declared; repair provenance with `trusted = 0` |
| GC-03 | `golden1_history_test.dart` | **every repaired region stays WITHHELD and carries no `text` key** |
| GC-04 | `golden1_history_test.dart` | withheld regions reach the app model as reasoned gaps |
| GC-05 | `golden1_history_test.dart` | three Learning Views open; the «chưa kiểm định» chip stays |
| GC-06 | `golden1_history_test.dart` | **no repair record carries a text-bearing key; no pipeline vocabulary reaches the Read screen** |
| GC-07 | `timeline_history_test.dart` | **no timeline exists while its source carries a non-servable `VALIDATED_REPAIR`** |
| GC-08 | `timeline_history_test.dart` | document repair accounting is honest: 6 regions repaired, 0 trusted |
| GC-09 | `timeline_history_test.dart` | story attributions derive only from blocks still served |

The three in bold are the repo's highest-value assertions — the ones that say a validated
repair does **not** reach a child. They were the ones CI never ran.

---

## 2. What was built

Nothing here commits book content. **D4 stands**: no version of this task ends with SGK
material in git, and `test/ci/golden_chain_registry_test.dart` asserts it by asking `git
ls-files`, not by trusting a `.gitignore` line.

| piece | what it does |
|---|---|
| `tool/ci/golden-chain-obligations.json` | the nine obligations, declared once, shared by the Dart and Python sides |
| `test/support/golden_chain_ledger.dart` | `goldenChainGate(id)` records **UNVERIFIED** and skips when the fixture is absent; `recordGoldenChain(id, exercised: true)` is called at the **end** of a body, so a body that throws leaves no record |
| `tool/ci/golden_chain_verdict.py` | reads `build/golden-chain/`, prints the coverage block, gates the claim |
| `.github/workflows/ci.yml` | resets the ledger, prints coverage, then **proves the gate is live** |
| `golden_chain_synthetic_test.dart` | nine corpus-free mirrors of the same invariants |
| `golden_chain_registry_test.dart` | locks registry ↔ tests ↔ CI floor together |
| `tool/tests/test_golden_chain_verdict.py` | fifteen mutation checks, run by the existing `unittest discover` step |

What the runner now prints:

```
GOLDEN CHAIN COVERAGE (WAL-218)
-------------------------------
  real fixture            : ABSENT  (assets/fixtures/real/lesson-05-…-b8.json)
  obligations declared    : 9
  exercised on REAL       : 0
  UNVERIFIED (no fixture) : 9
  synthetic mirrors       : 9/9 exercised   [SYNTHETIC PASS != GOLDEN VERIFIED]

  not verified by this run:
    - GC-01  WorkspaceCatalog loads the REAL path …
    …
VERDICT: GOLDEN CHAIN UNVERIFIED — 0/9 exercised — this run does NOT verify the
Golden chain. `flutter test` being green says nothing about it.
```

…plus the same table in the GitHub step summary, so it survives past the log scroll.

### Exit codes

| | |
|---|---|
| `0` | the run is honest about what it did and did not verify |
| `1` | the run **claimed** Golden verification (`--require-verified`) and the claim is false |
| `2` | the ledger cannot support any statement at all — missing ledger, an obligation with no record, a shrunken registry, a contradiction |

### Why the claim gate is not opt-in ceremony

CI runs the verdict twice. The second run *makes the claim on purpose* and requires the
answer to match the filesystem:

```
fixture ABSENT  ⇒ a Golden-verified claim must FAIL   (measured: exit 1) ✔
fixture PRESENT ⇒ a Golden-verified claim must pass   (measured: exit 0) ✔
```

If the gate ever stops refusing, that step goes red instead.

---

## 3. Mutation results

A gate that passes because the shape changed rather than because the property holds is worth
very little. Every mutation below was run; every one goes red.

### Against the ledger (`tool/tests/test_golden_chain_verdict.py`, 15 checks, permanent)

| mutation | result |
|---|---|
| delete a Golden test (obligation leaves no record) — **even with the fixture present** | exit 2 |
| shrink the registry to 2 obligations, both exercised | exit 2, `floor is 9` |
| …the same registry with `--min-obligations 0` | VERIFIED — **the floor is what does the work** |
| empty registry (`0/0`) | UNVERIFIED; a claim exits 1 |
| gate rewritten to record `exercised: true` with no fixture | exit 2, contradiction |
| stale ledger from a machine that had the fixture | exit 2, `stale ledger is not coverage` |
| record with `exercised: true, fixturePresent: false` | exit 2 |
| no ledger at all | exit 2, `has not verified anything` |
| an id no registry row declares | exit 2 |
| duplicate obligation ids | exit 2 |
| nine synthetic mirrors green, zero Golden obligations exercised | still UNVERIFIED; claim exits 1 |

### Against the properties (Dart, run by hand)

| mutation | result |
|---|---|
| **MUT-A** timeline NOT removed while its source is withheld | SYN-07 red — the "no timeline" assertion is not vacuous |
| **MUT-B** repaired region keeps its `text` | SYN-03 red |
| **MUT-C** repair record declares `servable: true` | document rejected by `fromJson`; 7 red |
| **MUT-D** gate records `exercised` with no fixture, end to end | `flutter test` printed **`All tests passed!`**; verdict exit 2 |
| **MUT-E** `trusted` asserted as `1` on the real fixture | GC-02 red — with the fixture present the real assertions **execute**, they do not merely record |

MUT-D is the one worth keeping in mind: the suite stayed green. The suite was never the
thing that could catch this.

---

## 4. Before → after

| configuration | before (`6fd728d`) | after | Golden verdict |
|---|---|---|---|
| Golden #1 present | 1108 passed / 33 skipped | **1126 / 33** | `VERIFIED — 9/9`, claim exits 0 |
| Golden #1 absent | 1099 / 42 | **1117 / 42** | `UNVERIFIED — 0/9`, claim exits 1 |
| both real fixtures absent (**CI**) | 1084 / 57 | **1102 / 57** | `UNVERIFIED — 0/9`, claim exits 1 |

+18 passing tests everywhere: 9 synthetic mirrors + 1 mirror-provenance check + 7 registry
checks + 1 fixture-path drift check. **The skipped count did not move, and that is the
point** — the nine still skip on CI; they simply can no longer be silent about it.

---

## 5. What CI can and cannot prove

### CAN, on every run, without any corpus
- the app model **rejects** a document that lets a repaired region carry text, or a repair
  record declare itself servable (`MUT-B`, `MUT-C` are rejected at `fromJson`);
- a withheld region carrying a non-servable `VALIDATED_REPAIR` yields **no timeline**;
- no repair record carries a text-bearing key; no pipeline vocabulary reaches the Read screen;
- `WorkspaceCatalog` prefers the real path and does not mix two generations;
- `trusted = 0` and `productionTrustThreshold = null` survive the whole path;
- the Golden fixture is **not** in the git tree;
- and — new — **how much of the Golden chain this run actually exercised.**

### CANNOT, and by construction never will
- that **the document generated from the book** goes through that path. Synthetic input,
  synthetic conclusion. `SYNTHETIC PASS ≠ GOLDEN VERIFIED`;
- anything about SDM output, OCR agreement, tone corroboration, or the real repair ledger —
  those live in `poc-out/`, which is machine-local;
- anything about the real crops, page boundaries, or `pageStart` fidelity;
- hardware. No device runs in CI: **TECHNICALLY VALIDATED / HARDWARE UNVERIFIED**.

### Remains UNVERIFIED on CI and is **out of WAL-218's scope**
The runner also lacks `assets/pack/` and the KHTN 6 Bài 17 real fixture. 57 tests skip in
total on a clean runner; **nine of them are now accounted for by name**. The other 48 —
pack provenance, lesson-index, discovery, stories, scale lineage — are skips of the same
family and have no ledger. The machinery here generalises to them; extending it was not
this task.

---

## 6. Honest statement of what this changes

It changes **nothing** about how much of the product is trusted. `trusted = 0`,
`eligible for teaching = 0`, no threshold was activated, no repair became servable, and no
child can read a word more than yesterday.

What it changes is that a reader — or a future agent — can no longer look at a green CI run
and conclude the Golden chain was verified. Before this branch, the only evidence available
was `All tests passed!`, and that sentence was identical in a run that verified nine things
and a run that verified none of them.

> Stale doctrine blocks as hard as a real gate, and no test catches it. The same is true of
> a stale claim of verification. This is that check, for one specific claim.
