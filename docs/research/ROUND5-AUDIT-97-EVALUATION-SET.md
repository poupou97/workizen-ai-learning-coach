# Round 5 — the 97-row independent audit as an EVALUATION SET (Founder, 2026-09-06)

**Status: evaluation/regression set, NOT a tuning set.** Founder instruction, binding on every lane:
> «97-row audit này trở thành regression/evaluation set. **Không tune trực tiếp để pass riêng sample này**; phải kiểm tra generalization trên **independent holdout**.»

So: you may *measure* on these rows as often as you like, and each named defect below must become a regression test. You may **not** tune a rule so that it happens to fix these strings, and every improvement must be re-measured on a **holdout the lane did not look at** — report both numbers side by side. A fix that moves only these 97 rows is a fix that did not generalise.

## Measured state (independent audit, 97 rows)

| | count | note |
|---|---|---|
| TRUSTED | **67** | of which **false trust 6/67 = 0.090** |
| teaching-critical WRONG | **5** | |
| display WRONG | **11** | |
| role WRONG | **10** | |
| WITHHELD | **30** | **SAFE 11 · OVER-withheld 19** |

**Over-withhold is now the larger pool: 19 of 30 withheld rows (0.633) were withheld wrongly.** This is consistent with round 4's own measurements (12/30 = 0.400 on a different sample; Lane A3's over-withhold rate 0.846; `agree_tones` alone = 60 sole withholds of which 58 clean).

## Named defects — each must become a regression case

| # | Defect | Class | Owner |
|---|---|---|---|
| 1 | **`3×10⁸ m/s` → `3×10° m/s`** | STEM: superscript destroyed — a physical constant becomes nonsense | A2 (+A1 detection) |
| 2 | **Lý Thái Tổ → Lý Thái Tô** | Vietnamese tone (proper noun) | A1 |
| 3 | **bản sắc → bán sắc** | Vietnamese tone (meaning inverted) | A1 |
| 4 | **Cộng hoà → Cộng hoa** | Vietnamese tone | A1 |
| 5 | **cây ổi → cây ỗi** | Vietnamese tone | A1 |
| 6 | **imprint / back matter → lesson heading** | attachment: end-matter still leaking into a lesson after round 4's cover fix | A1 (`tc2_attach`) |
| 7 | **`chem_guard` blocks a Physics heading** | guard false positive → over-withhold | A1 (+A2 for the structured exemption) |
| 8 | **Incomplete multiple-choice because a sibling block was withheld** | **withholding is not always safe** | A1 + A3 |

### Defect 8 changes the doctrine — read this
Withholding one option of a multiple-choice question leaves the *served* question **wrong**, not merely smaller. So «withhold» is not a universally safe default: for blocks with sibling/structural relationships (OPTION ⊂ QUESTION, a caption bound to its figure, a table row, a step in an enumerated procedure), **withholding one member must withhold the whole group or restore the group** — never serve a mutilated structure. This is a *teaching-critical* failure produced by the safety mechanism itself, and it means over-withholding can raise the teaching-critical error rate rather than only lowering coverage.

## Round 5 objective, restated by the Founder — five directions at once

Not just `FALSE TRUST ↓`, but simultaneously:
**FALSE TRUST ↓ · TEACHING-CRITICAL ERROR ↓ · CORRECT SERVED ↑ · OVER-WITHHOLD ↓ · RESTORE PRECISION ↑**

## New P0s (added to the round-5 plan)
- **STEM EXPRESSION ACCURACY.** Audit the code first to establish **at which stage** the error appears — `OCR → normalization → structured model → serialization → renderer`. **Do not assume a new architecture is needed.** If the repo lacks a structured STEM representation, run a bounded POC: `source region → specialized recognition → LaTeX candidate → Math/Science AST → deterministic validation → source cross-check → VALIDATED / WITHHELD → mobile renderer`.
- **VIETNAMESE FIDELITY / THIRD SIGNAL** (already lane A1's priority; defects 2–5 are its evaluation cases).
