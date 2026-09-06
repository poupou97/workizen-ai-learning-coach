# 02 · PLAN vs ACTUAL

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

Plan of record: `docs/research/ROUND5-PLAN.md` (six lanes). Actual: **nine lanes**.
Allowed statuses: **DONE · PARTIAL · FAILED · FALSIFIED · BLOCKED · DEFERRED · NOT STARTED**.
No PARTIAL in this file has been rounded up to DONE.

---

## 1. Lanes: planned six, ran nine

| Lane | In the plan? | PR | Status | What actually happened |
|---|---|---|---|---|
| **A1** repair framework + Vietnamese text | yes | **#83** | **PARTIAL** | Framework, plugin registry, third-signal layer, Vietnamese repairers and the repair ledger all built and measured on the gold set. **But it is not wired into the path that produces a lesson** — see §3. |
| **A2** math / formula / number | yes | **#84** | **DONE** | Audit located the failure stage, canonical AST built, six deterministic validators, 10/10 restores (8/8 holdout), fabricated 2 → 0, physics false trust −3 at zero over-withhold cost. |
| **A3** role spec + trust-gate sensitivity | yes | **#80** | **PARTIAL** | SPEC v1 (20 roles × 8 fields) and the sensitivity curve delivered, no threshold chosen — as ordered. The **re-annotation is in-sample**, and the fresh blind re-annotation that would settle agreement **was not run**. |
| **B** experience | yes | **#87** | **DONE** | Trực quan reached the concept board; the workspace duplication complaint quantified two ways, three options built and measured, five device-found defects fixed and re-walked. |
| **C** History | yes | **#81** | **DONE (with its own rule FALSIFIED — the intended outcome)** | Bài 8 re-run; `prose-dated-events-v1` falsified as a Bài-8 shape rather than a History rule; a repair candidate correctly **rejected** by two independent signals. |
| **D** legacy + packs | yes | **#82** | **PARTIAL** | Pack rebuild under snapshot discipline complete and verified; legacy batch 2 scored with restore precision. **R13 and R15 discovered and left open**; defect 8 still open on the lesson path. |
| **A4** multi-signal verification | **NOT IN THE PLAN** — added mid-round | **#88** | **DONE** | Per-signal detection recall, correction precision and **false-correction rate**; the router; the LLM verdict; the edge hypothesis confirmed at n=486,000 and its refinement falsified. |
| **E1** semantic foundation + K-12 census | **NOT IN THE PLAN** — Founder P0 escalation | **#85** | **DONE (verdict: GO WITH ARCHITECTURE CHANGE)** | 6 primitives · 6 relations across 224 lessons; 3 domain extensions proven, 3 refuted; the form census; the lesson-identity challenge. |
| **E2** VisualSpec + cross-subject renderer | **NOT IN THE PLAN** — Founder P0 escalation | **#86** | **DONE (with one claim RETRACTED and re-proved)** | One renderer across three subjects and two semantic paths; the identity guarantee found **nominal**, then made structural. |

**Plan-vs-actual finding #1 — the round grew by half.** Three of the nine lanes (A4, E1, E2) are
not in `ROUND5-PLAN.md`. A4 is a legitimate split-out of A1's third-signal mandate; E1 and E2 came
from a Founder P0 escalation on Semantic Graph → Visual Grammar after the plan was written. All
three shipped CI-green work, and **two of the round's three integration defects were found only
because those lanes existed** (A4 × A2's plugin loader, E1 × E2's identity leak). *(INFERRED from
the plan's lane table vs the PR list — both in `reports/` and `evidence/`.)*

---

## 2. The five Founder directions — planned to move together

| Direction | Planned | Actual | Status |
|---|---|---|---|
| **FALSE TRUST ↓** | ↓ | 0.619 → **0.318** (batch 2, vs OLD); 10/13 of batch 1's false-trust rows no longer served as before | **DONE** |
| **TEACHING-CRITICAL ↓** | ↓ | 0.476 → **0.100** | **DONE** |
| **CORRECT SERVED ↑** | ↑ | as reported 221 → 239 served (**0.632**); **corrected for R13 silent loss it FELL to 0.589**, holdout **0.523** | **FAILED** |
| **OVER-WITHHOLD ↓** | ↓ | 12/30 = 0.400 → **19/30 = 0.633** | **FAILED — moved the wrong way** |
| **RESTORE PRECISION ↑** | ↑ | **measured for the first time**, and it splits by mechanism: guard relaxation **0/1 = 0.000**, verdicts transferred **3/6 = 0.500**, validated repair **10/10 = 1.000** (holdout 8/8) | **PARTIAL** — no round-4 baseline exists to raise it *from*; the mechanism-level answer is the finding |

**Plan-vs-actual finding #2 — the five directions did not move together, and the reason is
structural.** Three moved by *withholding better*; two failed because **the repair path that
would have moved them is not connected to the product**. This was not a shortfall of effort in
any lane — it is a wiring decision that belongs to the Founder.

---

## 3. What the plan assumed that turned out not to hold

| Plan assumption | What was found | Consequence |
|---|---|---|
| A1 builds the repair framework and the pipeline uses it | **No file outside `tool/corpus/repair/` and `tool/tests/` imports the `repair` package.** Verified structurally by the coordinator on Lane D's branch, not accepted on report. | "No served text changed anywhere" is a **certainty of the wiring**, not a measurement. Connecting it is a Founder decision. |
| `learning blocks = trusted + withheld` | **False.** A block whose role is `empty` reaches neither, with no reason code (**R13**). | Every published rate has the wrong denominator. Round 6 workstream A exists because of this. |
| The 97-row audit's OVER/SAFE labels are the Founder's opinion | They are **predictive**: 3 of 4 OVER-withheld regions restored **correct**; **both** SAFE refusals restored **wrong**. | A usable routing rule, and independent evidence that the 97-row set is a sound evaluation set. |
| Coverage can recover by relaxing a guard where the audit says the guard over-fires | **It cannot.** 1 of 19 recovered, at restore precision **0.000**. | The plan's own prohibition ("without loosening a guard") was empirically vindicated. |
| A rule validated on the golden lesson generalises | **Falsified three times independently** — Lane C (1 of 12 date forms), E1 (TIMELINE 3/224), E2 (sequence 6/54, learner-facing precision 0.500). | **FORMS BEFORE RULES** becomes a standing rule. |
| A field-name guard prevents lesson identity reaching a renderer | **Nominal.** Every element carried lesson identity inside a **value** while both guards stayed green. | Fixed structurally with opaque handles at the render boundary. |

---

## 4. Scope that was planned and **not** done

| Item | Status | Honest reason |
|---|---|---|
| Fresh blind two-annotator re-annotation of role on a **new** seed | **NOT STARTED** | A3 says so in its own document: the spec was written after reading the rows, so the result is in-sample and κ = 1.000 on decided rows "is arithmetic, not evidence". |
| Wiring A1's repairers into the lesson-producing pipeline | **BLOCKED — Founder gate** | Correct state given the standing prohibition on production trust thresholds. |
| Defect 8 (mutilated structure) closed on the path a child reads | **PARTIAL** | A1 measures 7 → 0 on the gold set; Lane D measures **9 → 9** and **13 → 13** on the lesson path. Both are right about their own population. |
| Lane E2 device walk | **DEFERRED** | Lane B owns the device loop; `VisualSpecView` handed over as a six-line mount, with a machine-generated widget transcript across three subjects substituted for the checkpoint. Recorded as a substitution, not as device evidence. |
| A third OCR stack (signal F) | **NOT STARTED — correctly** | The plan gated it on "evidence that it helps". A4 did not re-open it; the evidence pointed at recognition instead. |

---

## 5. Scope that was **not** planned and was done anyway

- **The composition check** (§11.3 of the consolidated report). Nine branches merged in a
  throw-away worktree. It found **three defects no per-lane CI could see**. It is now a
  standing procedure for every round.
- **The R13 silent-loss investigation.** Two lanes found the same hole from opposite ends.
- **The K-12 semantic census** (E1) — 224 TSL-backed lessons, 3 domain extensions refuted.
- **The workspace duplication study** (B) — the Founder's complaint quantified before anything
  was designed, three options built from one commit, one selected.

---

## 6. Timeline

| Date | Event | Source |
|---|---|---|
| 2026-09-05 | Round 4 accepted; round-5 plan committed; integration base PR **#79** opened against `main` | git log, `gh pr list` *(PROVEN)* |
| 2026-09-05 16:10 → 16:51 | Lane PRs **#80 (A3) · #81 (C) · #82 (D) · #83 (A1) · #84 (A2)** opened | PR metadata *(PROVEN)* |
| 2026-09-05 22:57 → 23:19 | Device iterations 1–3 on the Nokia 6.1 (frame mtimes) | `manifests/round5-device-MANIFEST.json` *(PROVEN — frame hashes recomputed)* |
| 2026-09-06 01:32 → 01:53 | Lane PRs **#85 (E1) · #86 (E2) · #87 (B) · #88 (A4)** opened | PR metadata *(PROVEN)* |
| 2026-09-06 01:47 | Device evidence manifest generated (36 frames, 28 steps, 0 downgraded) | manifest `generatedAt` *(PROVEN)* |
| 2026-09-06 | Composition verified in a throw-away worktree; consolidated report completed (`bab657a`) | git log *(PROVEN)* |
| 2026-09-06 | Round-6 base composed from `integration/round5` + all nine lane branches; round-6 plan committed | git log *(PROVEN)* |

**Round 5 ran in roughly 36 hours of wall-clock time across nine parallel lanes.** *(INFERRED
from PR creation timestamps and commit dates.)*
