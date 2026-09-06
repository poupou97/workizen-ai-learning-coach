# 01 · ROUND OBJECTIVE

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

**Round 5 · DATA ACCURACY: REPAIR → VALIDATE → RESTORE · opened after the Founder accepted
round 4 · closed 2026-09-06.**

Primary source: `docs/research/ROUND5-PLAN.md` (committed) and
`docs/research/ROUND5-AUDIT-97-EVALUATION-SET.md` (committed). Both are reproduced in full in
`reports/`.

---

## 1. The North Star, in the Founder's own framing

> **Priority #1: raise data accuracy.** The long-term strategy `WRONG → WITHHOLD → DONE` is
> **rejected**. Every failure class must move to
> **`DETECT → REPAIR candidate → VALIDATE → RESTORE or WITHHOLD`**.
> **A repair is never trusted by default.**
> **Coverage must begin to recover *without loosening a guard*.**
>
> — `docs/research/ROUND5-PLAN.md`, verbatim *(PROVEN — committed file)*

The rejected strategy is worth naming precisely, because round 4 had made it look attractive:
round 4 bought a false-trust reduction by **withholding 85 more blocks to deliver 16 fewer wrong
ones** (gold coverage 0.683 → 0.551). That trade cannot be repeated indefinitely — at the limit
it serves nothing and is perfectly accurate. Round 5 existed to find the other lever.

## 2. What round 4 falsified, and what that forced

**Binding on every round-5 lane** *(from `ROUND5-PLAN.md`, MEASURED in round 4)*:

> `OCR_A == OCR_B` does **not** imply `TEXT == TRUE` — two stacks make the same error
> («Tiền hành», «vặn khoa lại», «phẫu/phễu»).

Hence the **third-signal layer**, ordered by the Founder: (A) Vietnamese lexicon/orthography ·
(B) layout/context constraints · (C) deterministic number/unit/formula checks · (D) cross-page /
heading / TOC consistency · (E) human review for high-risk cases · (F) a third OCR stack **only
on evidence that it helps**. Each signal's contribution had to be **measured separately**.

**The LLM rule, set before the round started:** an LLM may only ever produce a
**RepairCandidate**, validated by an independent signal — **never TrustedText**, and never wired
into the app.

## 3. The five directions, simultaneously

The Founder restated the objective as five directions that must move **at the same time** — not
one at the expense of another *(verbatim from `ROUND5-AUDIT-97-EVALUATION-SET.md`)*:

**FALSE TRUST ↓ · TEACHING-CRITICAL ERROR ↓ · CORRECT SERVED ↑ · OVER-WITHHOLD ↓ ·
RESTORE PRECISION ↑**

This is the round's real difficulty. Four of the five are easy to move alone and impossible to
move together by any single mechanism: withholding more improves the first two and destroys the
third and fourth; serving more does the reverse. Only a **validated repair** moves all five.

## 4. The 97-row audit — an evaluation set, not a tuning set

The Founder's independent 97-row audit became a **regression / evaluation set**, with a binding
constraint *(verbatim)*:

> «97-row audit này trở thành regression/evaluation set. **Không tune trực tiếp để pass riêng
> sample này**; phải kiểm tra generalization trên **independent holdout**.»

Measured state of those 97 rows: **TRUSTED 67** (of which false trust **6/67 = 0.090**) ·
teaching-critical WRONG **5** · display WRONG **11** · role WRONG **10** · **WITHHELD 30**, split
**SAFE 11 · OVER-withheld 19**.

**Over-withholding was already the larger pool: 19 of 30 withheld rows (0.633) were withheld
wrongly.**

### The eight named defects — each had to become a regression case

| # | Defect | Class | Owner |
|---|---|---|---|
| 1 | `3×10⁸ m/s` → `3×10° m/s` | STEM: superscript destroyed; a physical constant becomes nonsense | A2 (+A1 detection) |
| 2 | Lý Thái Tổ → Lý Thái Tô | Vietnamese tone (proper noun) | A1 |
| 3 | bản sắc → bán sắc | Vietnamese tone (meaning inverted) | A1 |
| 4 | Cộng hoà → Cộng hoa | Vietnamese tone | A1 |
| 5 | cây ổi → cây ỗi | Vietnamese tone | A1 |
| 6 | imprint / back matter → lesson heading | attachment leak surviving round 4's cover fix | A1 |
| 7 | `chem_guard` blocks a Physics heading | guard false positive → over-withhold | A1 (+A2) |
| 8 | Incomplete multiple-choice because a sibling block was withheld | **withholding is not always safe** | A1 + A3 |

**Defect 8 changed the doctrine.** Withholding one option of a multiple-choice question leaves
the *served* question **wrong**, not merely smaller. For blocks with sibling/structural
relationships (OPTION ⊂ QUESTION, a caption bound to its figure, a table row, a step in an
enumerated procedure), **withholding one member must withhold the whole group or restore the
group** — never serve a mutilated structure. Over-withholding can therefore *raise* the
teaching-critical error rate, not merely lower coverage.

## 5. Data versioning — binding on all lanes

Every value carries a disposition: **ORIGINAL OBSERVATION · REPAIRED CANDIDATE · VALIDATED
REPAIR · TRUSTED · WITHHELD · LEGACY · SUPERSEDED**. **Never overwrite a source observation.**
Every repair must trace `source → observation → failure → repair rule → supporting signals →
validation → final disposition`.

## 6. The new scoreboard the round had to produce

**DATA ACCURACY SCOREBOARD**, reported **BEFORE → AFTER**, never averaged into a single number:
false trust · teaching-critical · display fidelity · reading order · role · attachment ·
formula/number/unit · correct served · wrong served · withheld · **false withheld** ·
**restored** · **restore precision** · coverage.

Kept alongside it, unchanged: the **five product scores** (Experience Fidelity · Source Reality ·
Source Trust · Pedagogy Reality · Evidence Reality — never averaged) and the **legacy reprocess
scoreboard**.

## 7. Standing limits for the round

No production trust threshold · no mass corpus reprocess · no public SGK distribution · no
unrestricted LLM · no major architecture fork · no destructive migration · **no merge**.

*(All seven held. See `07-TEST-CI-PR-EVIDENCE.md` and `09-ARCHITECTURE-DATA-CHANGES.md`.)*

## 8. The two P0s added mid-objective

- **STEM EXPRESSION ACCURACY.** Audit the code **first** to establish *at which stage* the error
  appears — `OCR → normalization → structured model → serialization → renderer`. **Do not assume
  a new architecture is needed.**
- **VIETNAMESE FIDELITY / THIRD SIGNAL.** Defects 2–5 are its evaluation cases.

Both were answered. The first produced the round's most useful attribution result: the named
STEM defects are **born in OCR recognition**, not in normalisation — which is why round 6's
North Star is recognition. See `04-FAILURES-AND-FALSIFICATIONS.md` §2.
