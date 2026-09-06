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

---

## 7. The sweep — the same shape, nine more places

WAL-218's scope asked for a sweep: *"wherever an existence obligation is checked by
consistency alone."* Run 2026-09-06 across `tool/**/*.py`, `.github/workflows/ci.yml` and the
gate-like Dart tests. Ten instances, four of them in gates that run on CI today. Each was
read at the source before being listed; **none is fixed by this branch.**

### HIGH — live CI gates

| # | where | how absence reads as success |
|---|---|---|
| S1 | `test/features/subjects/scale_lineage_test.dart:414` | the gate exists to prove the pack carries `packVersion` build lineage; **the one condition it should fail on — lineage absent — is a `markTestSkipped`.** The surviving assertion is "if there is a packVersion it is non-empty". No ledger row anywhere |
| S2 | `test/features/subjects/default_build_guard_test.dart:90` | twelve grade tests must prove every pack on the machine is a non-experimental default build with zero router activities. On CI all twelve skip; on a machine whose pack parsed to zero activities, `every(...)` is vacuously true |
| S3 | `.github/workflows/ci.yml` — *Pack provenance verify (only when packs exist)* | the shell skips the gate whenever the artefacts it guards are absent, and exits 0. The step's own comment argues this is «không xanh giả … bước in rõ là bỏ qua» — **that is exactly the argument `All tests passed!` was making**, and it is wrong for the same reason: printing that you skipped is not a record anything downstream can read |
| S4 | `tool/ui/pack_provenance.py:181` (`router_sources`, `:69`) | `for e in pack.get(fam) or []` over every family: a pack with no activity families yields `srcs == []`, `problems == []`, and the tool prints `OK … verified as DEFAULT builds`. **A pack that shipped no content at all is certified as a good default build** |

S3 and S4 compose: the CI step skips when there is no pack, and the tool passes when the pack
is empty. There is no input for which that pair reports a problem about absence.

### MEDIUM — hand-run gates and helpers

| # | where | how absence reads as success |
|---|---|---|
| S5 | `tool/extract/verify_corpus_gates.py` G5–G8 (`:121`, `:134`, `:149`, `:160`) | four of nine gate families vanish when their artefact is not on the machine, and the script still prints `🟢 SCALE GATE: TẤT CẢ XANH` and exits 0. The verdict is computed from `FAILS` alone — a check that never ran is indistinguishable from a check that passed |
| S6 | `tool/extract/verify_corpus_gates.py:52` | the future-knowledge leak gate passes whenever the fraction-rule population is empty. An extraction regression producing zero `RULE` units makes every leak gate green. The same file already knows the fix — `:72` uses `len(same_den) > 0 and all(...)` |
| S7 | `tool/extract/verify_corpus_gates.py:137`, `:152` | "every edge carries origin" and "no `BUILDS_ON` claims `sourceStated`" are both vacuously true for a graph with zero edges — which is also what a broken graph builder produces |
| S8 | `tool/metrics/cli.py:75` | `NO_RECORD` is not counted as `bad`, and `verify` returns 0. **Deleting a recorded value is a way to make the metric gate green.** This is the ticket's "cannot distinguish *not applicable* from *never asked*", verbatim |
| S9 | `tool/research/lane_c/repair_plugin.py:160` | on a failed framework import `register()` returns `[]` instead of raising, and the caller at `:305` discards the return. A run with zero repairers registered reports "no repair candidates" — indistinguishable from "the repairers ran and found nothing". The ticket's "plugin loader" shape |
| S10 | `tool/shadow/guard_check.dart:32` | prints `GUARD: chặn 0/0 transcript` and exits 0 on an empty run directory; `catch (_) { continue; }` drops unparsable transcripts without incrementing either counter. Literally the `0/0 · PASS` print |

### Two notes, not counted

- `tool/evidence/fixture_lineage.py:283` still prints `0/0 present` with `PASS` — the round-7
  row itself is unchanged. It is *mitigated* by L5b (`:295`), which measures the population
  and returns `UNKNOWN` when withheld regions exist but none is croppable. Mitigated is not
  removed: the literal string can still appear.
- `tool/reporting/build_round_archive.py:337` derives three distinct YES claims from one
  `not problems` flag — a report generator, not a merge gate, but the same shape.

### Status

**The sweep is DONE. The remediation is NOT** — filed separately, and deliberately not folded
into this branch: WAL-218 asked CI to stop reporting success while a D4-gated assertion is
skipped, and that is what shipped. Fixing ten unrelated gates under the same ticket would have
made the before→after numbers above unreadable.
