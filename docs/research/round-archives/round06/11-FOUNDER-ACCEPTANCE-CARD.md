# 11 · FOUNDER ACCEPTANCE CARD — round 6's original gates, graded

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

**The gates below were fixed before the round, in the repository, and are not redefined here.**

---

## 0. THE PROVENANCE PROBLEM ROUND 5 HAD IS GONE

Round 5's archive had to mark its ten criteria **RECONSTRUCTED**, because §16 of the round-5 master
order had only ever existed in the conversation that issued it.

**Round 6 has no such problem.** `docs/research/ROUND6-PLAN.md` was committed as `1a75d24` **before
any result existed**, and it carries the five gates verbatim. Everything graded below is graded
against a file a later reader can check. *(PROVEN — the commit predates every workstream PR.)*

**And round 6 closed the round-5 gap retrospectively:** `ROUND5-ACCEPTANCE-CRITERIA.md` is now
committed. See §5.

---

## 1. THE FIVE GATES — graded independently

| Gate | Requirement *(verbatim from `ROUND6-PLAN.md`)* | Coordinator | **Archive builder** | Evidence |
|---|---|---|---|---|
| **A · ACCOUNTING** | Zero unexplained silent loss on Golden + holdout | PASS | **PASS** | §2.1 |
| **B · RECOGNITION** | ≥1 previously unrecoverable OCR failure class materially improves **at recognition level** | PASS | **PASS** | §2.2 |
| **C · REPAIR** | A `ValidatedRepair` crosses the production-shaped pipeline | PASS | **PASS** | §2.3 |
| **D · TEACHING** | ≥1 real lesson honestly eligible for teaching, target >0. **Do not lower trust/safety gates to achieve >0. A truthful zero is acceptable if evidence demands it.** | TRUTHFUL ZERO | **TRUTHFUL ZERO — correct under the gate's own terms** | §2.4 |
| **E · DEVICE** | ≥1 Golden lesson on a real device visibly consuming validated/repaired real data, traceable `UI → LessonDocument → TSL → ValidatedRepair → Source` | PASS | **PASS** | §2.5 |

### TALLY — **4 PASS · 1 TRUTHFUL ZERO**

**The archive builder's independent grading agrees with the coordinator on all five.** Unlike round
5, there is no criterion this archive could not see.

---

## 2. THE GRADING, GATE BY GATE

### 2.1 GATE A — **PASS**

The requirement is *zero unexplained silent loss on Golden + holdout*, and the round exceeded it on
both axes:

- **Golden slices:** UNACCOUNTED **38 → 0** across both.
- **Holdout:** **62 → 0**.
- **And beyond the requirement:** the evaluation set (33 → 0) plus **five lessons nobody selected**.
  **Total 138 → 0 across 29 ledgers / 1,878 input regions.**
- Enforced by a check that **exits non-zero** *(PROVEN — the exit path was read)*, not by a report.
- **And the served set is byte-identical before and after in every population.** No guard was
  weakened and no coverage was bought — *the one way this gate could have been met dishonestly, and
  it was not.*

**Why it is not a PARTIAL:** the round's own HYPOTHESIS section states the fix has **not** been run
over the whole corpus. But the gate asks for Golden + holdout, and **redefining a gate upward after
seeing the results is the same error as redefining it downward.** The generalisation risk is
recorded in `10-OPEN-RISKS-BLOCKERS.md` §3, where it belongs.

### 2.2 GATE B — **PASS**

*«≥1 previously unrecoverable OCR failure class materially improves at recognition level»* — the
gate is explicitly scoped to **recognition level**, and it is met three times over:

- `b) 3/10 + 5/21`, whose numerator `3` is **absent from the whole-page OCR entirely** — the exact
  case round 5 said only recognition could reach — **is now read correctly.**
- **GOLDEN #2 Bài 61: 17 of 47 recovered, 17/17 correct, 0 disagreements on 38 controls.**
- **Blocks blocked by «the OCR did not read the digit»: 281 → 234 (−16.7 %).**
- On a **holdout drawn by a rule fixed before the draw**: digit recall **0.181**, false recognition
  **0.049**, hand-checked tile by tile.

**Why the honest negatives do not reduce it.** `Ω` was **falsified** (0/22) and a recovered digit
**does not become a repaired block** (RESTORE 10 → 10). Both are real and both are reported — but
**the gate asks for improvement at recognition level, not at restore level**, and the negatives are
about the *next* stage. The lane also refused to bank an easy +41 % because **the holdout said the
false rate rose 0.049 → 0.083**. *A lane that meets a gate and then reports the price is meeting it
honestly.*

### 2.3 GATE C — **PASS**, and the only gate this archive could verify entirely first-hand

**9 validated · 6 crossed · `trusted: 0` · violations 0.**

**PROVEN by the archive builder from the artefact that was on the phone**, not from a report:
6 repair-bearing blocks, **6/6 `VALIDATED_REPAIR`, 6/6 `servable: false`, 6/6 on type `withheld`,
0 carrying a `text` field, 0 carrying any forbidden value key** — and `p039:000`, the block with all
seven dated events, present, withheld, text-less, `changed: false`.

**And `CONNECT ≠ TRUST` is enforced structurally rather than by discipline** — `disposition` is a
**class attribute**, there is no promotion mechanism at all, the bridge **refuses rather than
sanitises**, and the app's `repair` field exists **only on `WithheldBlock`** *(all PROVEN)*.

**The capping demonstration is what turns this from an assertion into a mechanism:** on a second
artefact the laboratory said TRUSTED and what crossed was `VALIDATED_REPAIR` +
`trust_gate:founder_decision_absent`. *The cap is not merely available; it fires.*

### 2.4 GATE D — **TRUTHFUL ZERO**, and it is the correct outcome

**`eligible for teaching` = 0. `SOURCE TRUST` = 0 / 97.**

**This is not an engineering failure, and this archive states that as a finding rather than as a
kindness.** The gate has three clauses and the round satisfied the second and third:

| clause | outcome |
|---|---|
| «≥1 real lesson honestly eligible for teaching, target >0» | **not met — 0** |
| «**Do not lower trust/safety gates to achieve >0**» | **honoured** |
| «**A truthful zero is acceptable if evidence demands it**» | **this is that zero** |

**The evidence that no gate was lowered to avoid the zero — which is the part that matters:**

- The served set is **byte-identical** before and after the accounting fix.
- `trusted: 0` is **asserted in code**, not measured — there is **no code path in any round-6 branch
  that could implement a threshold**.
- **The round let a timeline disappear from a child's screen rather than serve an untrusted
  repair.** A round optimising for the appearance of delivery would have shipped those seven events.
- WS-C **falsified its own first design** for the mirror-image sin — keeping a block served against
  a fail-closed ruling *to protect coverage*.

> **A round that could have reached >0 by relaxing one number, and instead let its flagship lesson
> lose its timeline, has met the spirit of Gate D exactly.**

**Why this archive does not grade it PASS.** The target was `>0` and the result is `0`. Calling that
a PASS would be redefining a gate after seeing results — the precise error this archive exists to
prevent. **TRUTHFUL ZERO is its own verdict, written into the gate in advance, and it is the honest
one.**

**What would move it:** a **Founder-set trust threshold**. Nothing else. See `12-NEXT-ROUND-PLAN.md`.

### 2.5 GATE E — **PASS**

A Golden lesson ran on a **real Nokia 6.1**, consuming **real repaired data**, with the chain
traceable by hash from source to screen:

```
SGK source (pdf 38–41) → SDM sdm-v3 · TSL tc2-r5  c9d2cf1f…
  → lane-c ledger → ValidatedRepair ×9 on 6 blocks
  → projected TSL  d7825280…  → LessonDocument  fb5dbfa8…  → fixture  a904d005…
  → WorkspaceCatalog real path → three Learning Views → device
```

`fixture_lineage.py --require-repair` → **VERDICT PASS**, and **the archive builder recomputed the
final hash and it matches** *(PROVEN)*.

**Why the one FAIL does not sink it.** Step 09 — the 17 gaps have no page crops (**G1**) — is a
*quality* gap in the withheld presentation, not a failure of the gate's requirement. The gate asks
that the device **visibly consume validated/repaired real data, traceably**. It did. **The FAIL is
recorded as a FAIL and returned to WS-C**, not softened.

**One reporting difference, stated:** the manifest's own tally is **7 PASS · 1 FAIL · 1 UNVERIFIED
(downgraded)**, because step 08 produced no frame and the retention rule downgrades a frameless
PASS. This archive reports the manifest. See `08-DEVICE-EVIDENCE.md` §4.

---

## 3. THE STANDING RULES — all held

| Rule | Held? |
|---|---|
| **FORMS BEFORE RULES** | **YES, and it changed a decision** — WS-D had a licence to build a bounded visual POC and the census (`conceptMap` 0, `timeline` 0) said **do not**. WS-B's census caught two of its own rules as false positives. |
| **Composition check before closure** | **YES** — 5 branches, real assets synced; it found the conflict and the three stale premises |
| **False demotion reported beside false correction** | **YES** — Golden #1: 2 demotions, published apart from the restores |
| **Never turn PARTIAL into DONE** | **YES** — the structured-content carrier stayed PARTIAL; Golden #2 stayed DEFERRED; the visual POC stayed NOT STARTED |
| **Never silently rewrite history** | **YES** — round 5's figures unchanged and reproducible; two corrections placed **beside** them, marked |
| **`3,679` = HISTORICAL BASELINE ONLY** | **YES** — `3,650` is published as a **MEASUREMENT** pending four Founder rulings |
| **`LLM OUTPUT != TRUTH`** | **YES** — no LLM in the corpus path; a VLM run **as a measured candidate** and rejected |
| **DO NOT MERGE** | **YES** — 16 PRs open across rounds 4–6 *(PROVEN)* |

---

## 4. THE ARCHIVE BUILDER'S RECOMMENDATION TO THE FOUNDER

**ACCEPT round 6. Merge #79 and close #73 as subsumed. Hold #80–#88 and #89–#93. Then make the
trust decision — it is now the only thing in the way.**

**Reasoning in one paragraph.** Round 6 did what round 5 could not: it put verified accuracy in
front of a child, end to end, on a real device, with the chain provable by hash. It met four gates
and reported the fifth as the truthful zero the Founder had authorised in advance — **and it earned
that zero by letting its flagship lesson lose its timeline rather than serve an untrusted repair.**
The engineering that remains is cheap and well-specified (three block types, one re-run for page
crops, two runtime defects). **What is expensive is a decision, and only the Founder can make it.**

**On the merge debt**, unchanged and still checkable: #73 is a strict **ancestor** of #79, `main` is
an ancestor of both, and the whole delta is **16 commits touching 3 files, all documentation**. So
merging #79 carries exactly the code risk of #73 — **already Founder-ACCEPTED** — plus a report, and
ships **none** of round 5's or round 6's unreviewed code. **It changes no APK.** Holding is not
neutral: round 7 would compose a composition.

**One process observation worth keeping.** Round 6's gates were committed with its plan and this
card graded them without reconstructing anything. **That is the whole difference between this
document and round 5's, and it cost one file.**

---

## 5. A CLOSED LOOP FROM ROUND 5 — recorded because it validates the archive process

Round 6 committed `ROUND5-ACCEPTANCE-CRITERIA.md`, the Founder's §16, for the first time.

| | tally |
|---|---|
| The coordinator's summary line to the Founder in round 5 | «7 đạt · 1 nửa · 2 không đạt» |
| The coordinator's own per-criterion table in the same message | **8 PASS · 1 PARTIAL · 1 FAIL** |
| **The round-5 archive, grading independently without §16 in hand** | **8 PASS · 1 PARTIAL · 1 FAIL** |
| **The settled tally now committed** | **8 PASS · 1 PARTIAL · 1 FAIL** |

The coordinator's correction, in its own words: *«The summary line was **wrong** … The archive
agent, grading independently and without §16 in hand, reached 8 · 1 · 1 and was right.»*

**Two things this settles.** First, the round-5 archive's reconstruction of §16 was sound — its
criterion 4 (correct served / coverage) is the FAIL and criterion 5 (role taxonomy + agreement) the
PARTIAL, exactly as the committed text says. Second, the round-5 archive's guess at how the tallies
might reconcile — *that over-withholding might be a separate criterion* — was **wrong**, and the
committed file says so explicitly: over-withholding *«sits inside criterion 4, which is already
graded FAIL. It must not be counted twice.»*

**Recorded here rather than quietly dropped**, because that is the doctrine both rounds run on.
