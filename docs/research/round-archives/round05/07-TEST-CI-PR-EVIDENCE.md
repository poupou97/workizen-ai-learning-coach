# 07 · TEST · CI · PR EVIDENCE

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

Raw evidence for this file: `evidence/round5-pull-requests.json`,
`evidence/round5-ci-status.txt`, `evidence/round5-branch-heads.txt`,
`evidence/round5-git-log-integration-branch.txt`, `evidence/structural-spot-checks.md`.

---

## 1. INDIVIDUAL CI — ten PRs, all green, none merged

*(**PROVEN** — re-read from the GitHub API by the archive builder on 2026-09-06.)*

| PR | Branch | Head *(re-resolved)* | Head *(as reported)* | Match | CI check | `mergedAt` | State |
|---|---|---|---|---|---|---|---|
| **#79** | `integration/round5-2026-09-06` → `main` | `bab657a` | `bab657a` | ✔ | `Analyze & Test = SUCCESS` | `null` | OPEN |
| **#80** | `lane-a3/round5-role-spec-trust-gate` | `569dad6` | `569dad6` | ✔ | SUCCESS | `null` | OPEN |
| **#81** | `lane-c/round5-history` | `d241fdc` | `d241fdc` | ✔ | SUCCESS | `null` | OPEN |
| **#82** | `lane-d/round5-legacy-packs` | `0113019` | `0113019` | ✔ | SUCCESS | `null` | OPEN |
| **#83** | `a1/round5-repair-framework` | `6652d58` | `6652d58` | ✔ | SUCCESS | `null` | OPEN |
| **#84** | `a2/round5-math-formula-accuracy` | `465d235` | `465d235` | ✔ | SUCCESS | `null` | OPEN |
| **#85** | `e1/round5-semantic-foundation` | `ea6b0f8` | `ea6b0f8` | ✔ | SUCCESS | `null` | OPEN |
| **#86** | `e2/round5-visualspec-renderer` | `538715f` | `538715f` | ✔ | SUCCESS | `null` | OPEN |
| **#87** | `lane-b/round5-experience` | `6e5f6e7` | `6e5f6e7` | ✔ | SUCCESS | `null` | OPEN |
| **#88** | `a4/round5-multi-signal-verification` | `1733ff7` | `1733ff7` | ✔ | SUCCESS | `null` | OPEN |

**9 of 9 lane heads match the consolidated report. 10 of 10 PRs are OPEN with a green check and
`mergedAt: null`.**

**PR creation window:** #79 2026-09-05T15:35Z → #88 2026-09-06T01:53Z.

---

## 2. COMPOSITION CI — the check that individual CI cannot replace

**Individual PR green ≠ integrated product green.** Because merging is a Founder gate, composition
was verified in a **throw-away worktree** built from `integration/round5-2026-09-06` with all nine
lane branches merged into it. No PR was touched, no branch pushed, the worktree is disposable.
Gitignored assets (**321 pack files, 24 fixtures**) were synced from the main checkout first, so a
missing-asset failure could not be mistaken for a defect.

| Check | Result |
|---|---|
| Git merge, 9 lane branches | **0 conflicts** |
| `flutter analyze` | **No issues found** |
| Python suite | **623 tests OK** (19 skipped) |
| Dart suite | **1061 tests, All tests passed** (3 skipped) |

*(**MEASURED** by the coordinator. The archive builder did **not** re-execute the suites — see
`evidence/structural-spot-checks.md`, "What was NOT re-run".)*

### The three defects composition found that nine green badges did not

Summarised here; full detail in `04-FAILURES-AND-FALSIFICATIONS.md` §7.

| # | Lanes | Defect | Why no lane's CI could see it |
|---|---|---|---|
| 1 | **B × E2** | A compatibility claim **true for readers, false for constructors** — `values` kept as a getter covers every read site, but a getter is not a constructor parameter | The constructors that broke **did not exist** when E2 measured; they arrived with Lane B's new round-5 test |
| 2 | **A4 × A2** | `verify.load_plugins()` registered by **module-import side effect**; after a legitimate `registry.reset()` the modules were already in `sys.modules`, so registration was never replayed — **the old loader would have returned `signals = []`** | Reproduces only when two lanes' test modules run in the same process, in that order: `test_verify_signals` alone → 42 OK; `test_mathfix_plugin test_verify_signals` → FAILED |
| 3 | **E2 × E1** | Lesson identity leaking inside a **value** while two field-name guards stayed green | A field-name guard cannot see identity inside a value; it took a second lane adopting the same rule to find it |

**Adopted as standing procedure: run the composition check at the end of every round.** It costs
one throw-away worktree and roughly ten minutes.

---

## 3. TEST COUNTS PER LANE

*(MEASURED, as recorded in each lane's report and PR.)*

| Lane | PR | Suite result | Analyze |
|---|---|---|---|
| A1 | #83 | regression tests incl. `tool/tests/test_repair_vi_defects.py :: FormulaTrustHole` (4 tests) | — |
| A2 | #84 | `tool/tests/test_mathfix*` | — |
| A3 | #80 | **25** unit tests (`tool/tests/test_thresholds.py`) | — |
| A4 | #88 | Python **321 passed / 8 skipped / 0 failed** | — |
| B | #87 | Dart **995 passed / 1 skipped**, CI 2m16s | clean |
| C | #81 | Dart 928 passed / 42 skipped / 0 failed; Lane C Python 31 passed / 2 skipped | clean |
| D | #82 | Dart **948 pass / 15 skipped**; Python **348 OK** | clean |
| E1 | #85 | **285** tool tests OK | — |
| E2 | #86 | Dart **973 pass / 42 skipped** | clean |
| **Composed** | — | **Python 623 OK · Dart 1061 pass · 0 conflicts** | **clean** |

**A note on the skip counts.** Lane C's 42 skipped tests need the gitignored real fixtures, absent
in a worktree. This is recorded rather than hidden: a green suite in a worktree is not the same
population as a green suite in the main checkout.

---

## 4. TESTS THAT EXIST TO PREVENT A SPECIFIC FUTURE FAILURE

These are worth listing separately because they are the round's most durable output — each one
encodes a finding so that it cannot silently return.

| Test | What it pins |
|---|---|
| `test_repair_vi_defects.py :: FormulaTrustHole` (4 tests) | A `FORMULA` **label** alone does not buy confidence; an unvalidated formula block is `WITHHELD` with reason `formula_unvalidated`; a formula label does **not** waive the math/unit/chem guards; the exemption is earned by a **validated structure**, not by a role name. The class states its own purpose: dormant today, so that switching Docling formula enrichment on **cannot silently turn formula recognition into trusted content**. |
| E2's redaction mutation tests (6 new; 2 fail if redaction is disabled) | The identity redaction at the render boundary is real, **and** the leak still exists in the on-disk artefact — so the guard cannot go vacuous |
| E2/E1 grounding round-trip test | A save/load round trip **must never strengthen** a grounding (`inheritedFromEntity` → `cellStated` was caught this way). **Serialisation is a provenance-laundering channel.** |
| `load_plugins` manifest check → `RegistrationIncomplete` | A plugin loader must **fail loudly** rather than silently return fewer signals than asked for |
| E2 import-set test | **0 runtime model calls** in the visual layer |
| E2 source-grep ban inside `assist_layer` (`LessonDocument` / `WorkspaceTrace` / `nextActionFor`) | **No second recommendation engine** may be created by the assistant surface |
| A4 abstention assertions | «Cộng hoà» → «Cộng hoa» — every signal must **abstain**, because the corpus writes the error 358× across ≥5 books |
| A3 evidence extractor | Reproduces the published baseline **page by page** and **raises** rather than reports if the two drift |
| D's `packs.py` snapshot rules | A snapshot never overwrites; a rebuild refuses unless a snapshot matches by sha256; a restore re-checks every hash |

---

## 5. STANDING LIMITS — all seven held

| Limit | Held? | Evidence |
|---|---|---|
| No production trust threshold | **YES** | `THRESHOLDS.json` does not exist; A3 built the curve and chose no point; Source Trust stays 0/97 *(MEASURED)* |
| No mass corpus reprocess | **YES** | Lane D reprocessed **batch 2 = six lessons**; Lane C re-ran **one book** reusing round-4 raw candidates |
| No public SGK distribution | **YES** | D4 enforced — E1 replaced five near-verbatim SGK fixtures with invented text; Lane C's ledger records verdicts and single differing tokens only |
| No unrestricted LLM | **YES** | A4 measured the LLM and confined it to **detector only**; E1 called **no LLM at all**; E2 enforces 0 runtime model calls by test |
| No major architecture fork | **YES** | E1's verdict is GO WITH ARCHITECTURE **CHANGE**, filed as a recommendation, not executed |
| No destructive migration | **YES** | D's fail-closed drop deletes nothing upstream; every drop counted and logged with a reason |
| **No merge** | **YES** | 10 PRs open, `mergedAt: null` on all ten *(PROVEN)* |

---

## 6. WHAT THE CI EVIDENCE DOES **NOT** SHOW

- **It does not show that the product is correct.** Every suite in this round runs against the
  pipeline, the tooling and the widget tree. **No test in this repository measures whether the
  text a child reads matches the printed page** — that is what the human audits and the page
  renders do, and they are the only source of the false-trust and restore-precision numbers.
- **It does not show that the round is safe to merge.** Composition proves the branches combine
  and the suites pass. It does not prove R13's denominators are fixed, R15 reproduces, or the
  repair path is connected.
- **A green suite in a worktree is not a green suite in the main checkout** — 42 of Lane C's
  tests skip in a worktree for want of gitignored fixtures.
- **UNAVAILABLE:** per-PR CI run durations for #79–#86 and #88 were not recorded; only Lane B's
  (2m16s) appears in a lane report.
