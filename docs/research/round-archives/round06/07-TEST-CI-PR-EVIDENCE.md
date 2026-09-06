# 07 · TEST · CI · PR EVIDENCE

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

Raw evidence: `evidence/round6-pull-requests.json` · `evidence/round6-ci-status.txt` ·
`evidence/round6-branch-heads.txt` · `evidence/round6-git-log.txt` ·
`evidence/structural-spot-checks.md`.

---

## 1. INDIVIDUAL CI — five PRs, all green, none merged

*(**PROVEN** — GitHub API, 2026-09-06.)*

| PR | Branch | Head *(re-resolved)* | Head *(as reported)* | Match | CI | `mergedAt` |
|---|---|---|---|---|---|---|
| **#89** | `ws-archive/round5-retrospective` | `73a5321` | `73a5321` | ✔ | `Analyze & Test = SUCCESS` | `null` |
| **#90** | `ws-c/round6-repair-integration` | `4193c50` | `4193c50` | ✔ | SUCCESS | `null` |
| **#91** | `ws-a/round6-accounting` | `02e28dc` | `02e28dc` | ✔ | SUCCESS | `null` |
| **#92** | `ws-b/round6-recognition` | `371b6b0` | `371b6b0` | ✔ | SUCCESS | `null` |
| **#93** | `ws-d/round6-golden-delivery` | `eeb38c1` | `eeb38c1` | ✔ | SUCCESS | `null` |

**5 of 5 heads match §10.1 of the consolidated report.** And re-checked in the same pass: round 5's
**#79–#88** and round 4's **#73** are **all still OPEN with `mergedAt: null`**.

**PR #90 is a declared *stacked* PR on WS-A** — see §2.

---

## 2. COMPOSITION CI — and why it is not optional

**Individual PR green ≠ integrated product green.** Composition was verified in a **throw-away
worktree** from `integration/round6-2026-09-06` with all five branches merged **and the real
gitignored assets synced in** (packs + fixtures) — so a missing asset could not be mistaken for a
defect and, more importantly, **so the stale premises of §4 could not hide**.

| Check | Result |
|---|---|
| Git merge, 5 branches | **0 conflicts** |
| `flutter analyze` | **No issues found** |
| Python suite | **748 tests OK** (23 skipped) |
| Dart suite | **1084 tests — All tests passed** |

*(**MEASURED** by the coordinator. The archive builder did **not** re-execute the suites — see
`evidence/structural-spot-checks.md`, "What was NOT re-run".)*

### It did not compose on the first attempt

**1 · A conflict that was the downstream cost of a shared-checkout collision.** WS-C's branch
carried WS-A's `47247dd` while WS-A had rebased the same change as `24f6136`. **`git patch-id`
proved them byte-identical with different SHAs**, so git could not dedupe. None of WS-C's own
commits touched either file, so WS-A's newer version won and nothing was lost. WS-C rebased onto
WS-A's branch, dropping both borrowed commits — turning a 17-commit mixed chain into a **declared
stacked PR**.

**2 · Three stale test premises** — §4.

> **Recommendation stands, for the second round running: the composition check is standing
> procedure.** Five green CI badges did not mean the round worked.

---

## 3. TEST COUNTS

| Scope | Suite result | Analyze |
|---|---|---|
| **Composed round** | **Python 748 OK** (23 skipped) · **Dart 1084 — all passed** | **clean** |
| WS-B (#92) | Dart **1019 passed / 45 skipped** · Python **672 OK / 15 skipped**, **50 new** — none touching corpus, PyMuPDF, numpy, Vision or the network | clean |
| WS-C (#90) | Python **672 passed / 14 skipped**, **30 new** · Dart **1073 passed / 2 skipped / 1 failed** | clean |
| WS-D (#93) | 16 lineage tests + corrected workspace / no-machine-ids suites | — |
| WS-A (#91) | `test_accounting_ledger.py`, `test_lesson_identity.py` | — |

**WS-C's single Dart failure is recorded rather than hidden:**
`test/features/subjects/lesson_index_test.dart` compares two files that are **not in git at all** —
`assets/pack/lesson-index-g*.json` against `poc-out/units/exercise-case-map.json`. No tracked change
on that branch can affect it, and it reproduces identically in a clean isolated worktree.
**Reported as pre-existing and left alone** — and §4 explains why it was red at all.

---

## 4. THE THREE STALE TEST PREMISES — the round's systemic finding

| test | layer | premise formed when… | on a clean clone |
|---|---|---|---|
| `lesson_index_test.dart` | **packs** | the packs still carried the INFERRED expressions | **passes/skips** |
| `timeline_history_test.dart` | **`lib/core`** | seven timeline events came from an older build | **passes/skips** |
| `no_machine_ids_test.dart` | **UI** | seven events came from the `[MẪU]` fixture | **passes/skips** |

> **Only a composed tree with real assets present surfaces them. Individual per-PR CI is
> structurally blind to this class of defect.**

Each was corrected by **fixing the premise, never loosening the gate or adding a skip**, and
mutation-checked. **The new rule reads the published artefact, not the parsed model:**

> **If any region is a `VALIDATED_REPAIR` that is not yet trusted, there must be no timeline —
> neither in the data nor on the screen.** Condition: `VALIDATED_REPAIR` + `servable != true`.

**Mutation results:** serving `p039:000` as a paragraph with text → **RED** · injecting a
`TimelineSemantic` into the artefact → **RED** (`Expected: empty · Actual: [TimelineSemantic]`) ·
removing the real fixture entirely → **GREEN** (the synthetic route still walks its old path).
**The fixture was restored afterwards to the exact hash `a904d005…`.**

### The correction WS-D made to its own first fix

Its first rewrite asserted an **equivalence** — *the timeline appears iff the document carries a
`TimelineSemantic`* — which is satisfied by the app faithfully drawing whatever the data says.
**Injecting a `TimelineSemantic` made a timeline appear and the test stayed green.**

> The property that matters is not «does this lesson have events» but **«has anyone been granted
> trust»**.

**And one test WS-D deliberately did not touch:** `test/core/lesson_model/timeline_history_test.dart`
is WS-C's file. It expects seven events and the old title, so it is **red on this machine** — *a real
signal belonging to WS-C, not litter to sweep up.* It **skips on a clean clone**, so CI is
unaffected.

---

## 5. TESTS THAT EXIST TO PREVENT A SPECIFIC FUTURE FAILURE

| Test / mechanism | What it pins |
|---|---|
| `ledger.py audit` (non-zero exit) | **A silent loss must fail the build.** Round 5's survived precisely because nothing failed. |
| the honesty rule in `no_machine_ids_test.dart` | **A timeline may not reappear without a Founder trust decision.** Both mutations kill it. |
| the structural `WithheldBlock` count | The number of withheld blocks the app builds must **equal** the number the artefact declares — *no region may quietly become text.* |
| `ValidatedRepair.disposition` as a class attribute | **No argument, flag or setter can produce `TRUSTED`** *(PROVEN)*. |
| `repair_of()` refusals in the bridge | A record claiming `TRUSTED`/`servable`, missing its validator, or carrying any value key is a `BridgeRefusal`. **A served block carrying a repair is itself a refusal** — that is the shape of an ungated restore. |
| `check_document` | Searches the **whole serialised document** for each proposed value — so a future field or a careless `**record` cannot open the door quietly. |
| `repair` field only on `WithheldBlock` (Dart) | A served block **has nowhere to put** a repair *(PROVEN)*. |
| `assert_repair_not_strengthened` + `ValidatedRepairRef.notStrengthened` | A round trip may not raise a disposition, flip `servable`, or **drop a cap** — *dropping a cap drops the reason a repair was held back.* Delegates the grounding half to E1's own implementation: **one implementation, not two.** |
| `from_text`/`from_latex`/`from_summary`/`from_string`/`from_display` **must not exist** | A2's *no constructor from a presentation form* rule, asserted. |
| 16 lineage tests + `--require-repair` | A fixture must name the TSL it was built from, and **re-hash to it**. |
| WS-B's 50 corpus-free tests | The recogniser's rules are checkable **without the corpus**, on ASCII rasters. |
| the pinned unigram-diacritic test | A **falsified** rule stays in the code with a test **so nobody re-adopts it by accident.** |
| `assist_layer` source grep | **No second recommendation engine** — the layer may not touch `LessonDocument` / `WorkspaceTrace` / `nextActionFor` / `founderNextAction`. |
| each view name appears **exactly twice** | Not «count 6» — *counting could not catch the two-word-set defect; it only made the number slip.* |

---

## 6. STANDING LIMITS — all held

| Limit | Held? | Evidence |
|---|---|---|
| **No production trust threshold** | **YES** | `trusted: 0` is asserted **in code**, not measured; the timeline was allowed to disappear rather than be served |
| No mass corpus reprocess | **YES** | measured populations are 29 lesson ledgers, 113 Toán pages, 238 canonical TSLs — never the whole corpus |
| No public SGK distribution | **YES** | D4 enforced; frames and artefacts are marked INTERNAL and are **not committed** |
| **No unrestricted LLM** | **YES** | WS-A called none; WS-C calls none, proposes with none, lets none rule; WS-B ran a VLM **as a measured candidate** and rejected it |
| No major architecture fork | **YES** | the servable structured kind was **deferred**, not forced |
| No destructive migration | **YES** | round-5 figures preserved and reproducible; corrections placed **beside** them |
| **No merge** | **YES** | 16 PRs open across rounds 4–6, `mergedAt: null` on every one *(PROVEN)* |

---

## 7. WHAT THE CI EVIDENCE DOES **NOT** SHOW

- **It does not show the product is correct.** No test in this repository measures whether the text
  a child reads matches the printed page — that is what human audits and page renders do.
- **It does not show the round is safe to merge.** Composition proves the branches combine and the
  suites pass. It does not settle the trust threshold, canonical identity, or G1.
- **A green suite in a worktree is not a green suite in the main checkout** — and round 6 proved the
  converse too: **three real defects were green on a clean clone and only visible with real
  assets.**
- **UNAVAILABLE:** per-PR CI run durations for #89–#93 were not recorded.
