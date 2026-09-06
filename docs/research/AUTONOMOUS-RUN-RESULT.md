# AUTONOMOUS RUN — RESULT
## Root cause → fix → trusted slice · 2026-09-06 · Founder order 47

> **WHAT A CHILD CAN USE NOW THAT THEY COULD NOT BEFORE: NOTHING.**
>
> That is the honest answer and it is stated first, because the order forbids substituting
> commit counts, test counts or issue counts for a product outcome.

---

## 1 · START STATE

`main = 6fd728d` · CI success · 0 open PRs · WAL-213 DONE · E24 = WAL-211 · WAL-214/215 Ready ·
WAL-216/217 Ideas · WAL-218 Ready · **`trusted = 0`** · **`eligible for teaching = 0`** ·
`toanExercises` shipped = 0.

**End state:** `main = 06d5470` · CI success · 0 open PRs · every invariant above **unchanged**.

---

## 2 · ROOT CAUSE OF THE 12 ERRORS

**The hypothesis this run was launched to test — «segmentation/geometry is the bottleneck» — is
FALSIFIED. It is 1 of 12.** That hypothesis was mine; I put it to the Founder before Phase A
measured it.

| Root cause | rows |
|---|---|
| **ROLE DISAMBIGUATION** | **5** |
| **CHARACTER / DIGIT RECOGNITION** | **4** |
| **BLOCK BOUNDARY / SEGMENTATION** | **1** |
| **NOT A PIPELINE ERROR** | **2** |
| COMPOSITION · PIPELINE ORDERING · UNKNOWN | **0 each — tested, not omitted** |

**And the count itself was wrong.** Two of the twelve are not errors in the served output: one is
an **evaluation-matcher artefact** (the printed unit *is* served, correctly, TRUSTED, by another
block — `tc_score.match` attached the gold box to an unrelated one on a 1-token anchor, IoU
**0.000** against **0.581** for the right block); one differs from print by **a single space**
around an operator, CER 0.0056.

Then Phase B's adjudication overturned a third: the Vật lí 10 row is the *statement* of a worked
example, which `ROLE-DEFINITION-SPEC-v1` names as QUESTION in as many words. **The served role
there is correct.**

**Honest baseline: 11 teaching-critical errors on 9 served blocks — not 12 on 12.**

---

## 3 · WHAT WAS FIXED

**Phase B — role layer.** A narrowed question-promotion veto. P1 reads `native_label`; P3 fixes
`SIDEBAR_LABEL`, whose vowel classes omitted tone-marked forms so it missed **10 of 19** labels and
fired mainly where the OCR was already wrong. **Phase A's own P2 was falsified and replaced** — it
vetoed the row just adjudicated correct, and on the same pages demoted a real task where the same
verb governs an object.

**Phase E — WAL-218, CI false-green.** Nine Golden-chain obligations (`GC-01`…`GC-09`) declared
once; a ledger records **UNVERIFIED** when the D4-gated fixture is absent. `golden_chain_verdict.py`
exits `1` on a false claim of Golden verification and `2` when the ledger can support no statement
at all. CI runs it twice — once to report, once making the claim on purpose and requiring the answer
to match the filesystem, **so the gate going quiet is itself red**.

**Phase F — the narrow slice harness.** A pre-registered gate that judges every candidate and
never picks one.

---

## 4 · BEFORE → AFTER

On the adjudicated 54-page plane, rebuild against rebuild, **re-derived three ways**:

| | before | after |
|---|---|---|
| **teaching-critical** | **11** | **7** |
| as-question | 5 | **1** |
| false trust | 25 | **22** |
| served | 356 | 356 |
| withdrawn | — | **0** |
| correct questions broken | — | **0 of 66** |
| coarse role wrong | 57 | **51** |

By class, no double-counting: segmentation 1→1 · recognition 4→4 · **role 4→1** · artefacts 2→1.

**CI verdict semantics**, measured on `main`:

| configuration | before | after |
|---|---|---|
| fixture present | 1108 passed / 33 skipped · `All tests passed!` | **1126/33 · VERIFIED 9/9, claim exits 0** |
| **fixture absent (CI's real state)** | 1084/57 · **`All tests passed!`** | **1102/57 · UNVERIFIED 0/9, claim exits 1** |

**The skipped count did not move. That is the point.**

### The half that does not generalise, stated plainly

**The teaching-critical gain is IN-SAMPLE and does not reproduce out of sample — because no
labelled plane in this repository holds the failure class.** The 16 held-out gold pages contain
**zero** as-question errors; Bài 17's two are `ACTIVITY → QUESTION`, which no rule here addresses;
and **`BLIND-CORE` / `BLIND-TEACHING` carry no role annotation at all**, so the blind measurement
Phase A asked for is **impossible without an annotation pass**.

**What does carry is the role correction:** four independent role changes, **two on held-out
pages**, **4 of 4 correct, 0 regressions** — one of them a block the spec already names in print as
a `SIDEBAR → OBJECTIVE` error. Blast radius over 1,124 unlabelled pages / 28,542 blocks: 197 blocks
(**0.69 %**) change role, **31 question demotions, 0 promotions**, 6 withdrawals, all fail-closed.

---

## 5 · WAL ISSUES COMPLETED / REFRAMED

- **WAL-218** — DONE, merged (PRs #106, #108).
- **WAL-224** — created under E24 for Phase F, closed DONE.
- **WAL-223** — created: the `0/0 · PASS` shape found in **10** places, remediation **NOT STARTED**.
- **WAL-215** — **REFRAMED, not closed.** P0 dropped: as-question now explains **1 of 7**;
  recognition dominates. Its own acceptance criterion is recorded as **unreachable without a role
  annotation pass**. Left at `Ready` — *promoting it to Done would be the PARTIAL→DONE the order
  forbids.*
- **WAL-214** — premise partially preserved: recognition is 4 of 12 and now **6 of the 7 remaining**.
- **WAL-216** (pipeline ordering) — Phase A measured **PIPELINE ORDERING = 0 rows**. Its P0 framing
  is not supported by the evidence and should not be run on the old premise.

---

## 6 · TRUSTED SLICE RESULT

**Selection rule pre-registered and provable.** `docs/research/PHASE-F-SELECTION-RULE.md` is commit
`aadaa13`; the harness is `4e8b87b`, **464 seconds later**. The branch
`origin/phase-f/narrow-trusted-slice` was deliberately **not deleted** so the ordering survives the
squash. All four pre-registered predictions held. There is **no selection among candidates** — the
harness enumerates every unit on every gold page of both gold sets and reports all 236.

Over the 95 units a child acts on:

```
SOURCE 39 → STRUCTURE 19 → RECOGNITION 5 → ROLE 4 → VALIDATION 2 → TRUST POLICY 0
```

**Two survivors** — a section heading and one question, on Ngữ văn 6 p.20 and Ngữ văn 9 p.66.
Character-exact against gold (`cer 0.0`, `edits 0`), correctly roled, served by the unchanged gate
with **no guard raised**.

**They are refused by a clause, not a number.** C1/C2/C4 refuse the `question` role *by name*; C3
refuses at role confidence **0.78** and **0.85** against a required **0.90**. A pinned test sweeps
0.70 / 0.85 / 0.90 / **0.99** — **the verdict never changes. There is no point on any frozen curve
at which a complete question section is admissible.** One survivor is refused a second time by
`two_stack_exact` at `text_sim 98.0` **while being character-exact against gold**.

**And neither book has a delivery path** — zero TSLs, zero LessonDocuments, no fixture slot for
Ngữ văn anywhere. *The slice that measures best is in a book the pipeline has never processed; the
two books that are delivered fail earlier.*

**The zero is readable, not vacuous:** `test_a_perfect_unit_qualifies` builds the unit the bar
describes and the gate prints `QUALIFIES_GATE_CLOSED`. **The zero is a fact about the corpus, not
about the bar.** Six guard provocations all exit non-zero, including the bar mutated to pass
everything.

---

## 7 · WHAT A CHILD CAN USE NOW

**NOTHING.**

Parent: nothing. SAM: nothing. Everything this run produced is INTERNAL / RESEARCH ONLY.

This is the **third** truthful zero the project has recorded, and the **first with a
pre-registered selection rule in front of it** — which is the only thing that makes it a
measurement rather than an outcome.

---

## 8 · CI / DEVICE / D4 STATUS

**CI** — `main` green. And CI can now say what it cannot prove: on the runner,
`🎉 1102 tests passed, 57 skipped.` is immediately followed by
`VERDICT: GOLDEN CHAIN UNVERIFIED — 0/9 exercised`. **48 of the 57 skips remain the same family
with no ledger — nine accounted-for skips is not fifty-seven.**

**DEVICE** — **not used.** The Founder is offline and the Nokia was not touched.
**TECHNICALLY VALIDATED ≠ HARDWARE VERIFIED.** R-1 remains **HARDWARE UNVERIFIED**.

**D4** — clean. `assets/fixtures/real/` holds **two `.gitkeep` files and nothing else**, asserted
by a test using `git ls-files` rather than trusting `.gitignore`. Phase B's own D4 self-scan found
printed corpus text in its comments and one test literal **and removed it before committing**.
No licensing or distribution status changed.

**No threshold activated** — there is no `THRESHOLDS.json`; the frozen calibration payload is
untouched.

---

## 9 · REMAINING TRUE BLOCKERS

1. **No labelled plane holds the as-question failure class**, and the two blind populations carry
   **no role annotation**. Generalisation of any role rule is unmeasurable until an annotation pass
   exists.
2. **On Bài 17 — the only lesson-wide gold set — recognition cannot be measured at all.** 73
   blocks, zero verbatim text, `evidence.py` returns `digits_wrong = None` → teaching-critical
   `False`. **The digit half — 6 of the 7 remaining errors — reads a silent zero there.** Another
   instance of absence satisfying an obligation.
3. **The trust policy refuses complete question sections by clause**, at every threshold tried.
4. **Ngữ văn has no delivery path at all.**
5. **The `0/0 · PASS` shape survives in 10 places** (WAL-223), including `.github/workflows/ci.yml`
   itself: the *Pack provenance verify* step exits 0 when the packs it guards are absent, arguing in
   its own comment that printing «bỏ qua» keeps it honest — **the identical argument
   `All tests passed!` was making.** Composed with `pack_provenance.py:181`, **there is no input for
   which that pair reports a problem about absence.**
6. **Every piece of ground truth in this repo is model-produced.** `FALSE-TRUST-AUDIT-PROTOCOL`'s
   second-annotator requirement has never been run, so **«certified» is unavailable to any content
   at any measurement.**
7. **Three contradictions inside `ROLE-DEFINITION-SPEC-v1`** (Q-ROLE-6/7/8) — reported, unresolved.
8. **A contested lesson boundary on Golden #1**: LS&ĐL 5 Bài 8 is `(38,39,40,41)` in ten lane-C
   TSLs and `(41,)` in four legacy TSLs. Reading the generous span produced a false positive inside
   Phase F's own harness, caught and fixed by ruling that a contested boundary is not a boundary.

---

## 10 · FOUNDER DECISIONS REQUIRED

See **`docs/research/FOUNDER-DECISION-PACK.md`**. Four decisions, none of which an agent may take:
the **denominator grouping key** · **ratifying D-135…D-138** (WAL-196 — the gate holding
`trusted = 0` structurally) · **whether to activate a trust threshold and under which bound** ·
**WAL-43 licensing**.

---

## 11 · NEXT SINGLE BEST ACTION

**M1 — one unit-level trust candidate, hashed and frozen beside C0–C4, evaluated by re-running the
existing gate.** One file, one candidate, one re-run. It **activates nothing**: `policy.admits()`
returns a refusal list and cannot write.

It answers the one question Phase F could not: **whether any trust-policy shape can admit a
complete question section, or whether the refusal is structural.** If structural, that is the
finding that redirects the project — and it is cheap to learn.

**M2 stays outstanding regardless:** one **non-model** reading of one two-block slice. Until a
second annotator exists, no content can be certified at any bar, and every number in this document
inherits that limit.
