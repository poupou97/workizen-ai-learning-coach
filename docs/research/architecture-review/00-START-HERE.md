# HỌC CÙNG SAM — Founder Architecture Review (after the TC-v2 Science Slice) — START HERE

**What this is.** The ONE review the Founder asked for after the Science Slice (decision 2026-09-05, item 9): *Source Architecture + Learning Views + Runtime Semantics*, organised by the Founder's A–J. Everything measurable was measured on the slice (six Science SGK books, 1,049 pages, + 75 SGV pages) and on a 54-page gold set (38 TC-v1 + 16 new held-out); everything else is labelled HYPOTHESIS or OBSERVED-IN-CODE. Nothing was merged, no Dart was changed, no page image was delivered to a learner, no LLM output is source truth.

**Read in this order (30 minutes):** `01-FOUNDER-SUMMARY.md` → `I-MEASURED-TRUST-AND-COVERAGE.md` → `ROLE-LAYER-AND-SHORT-ANSWER-GATE.md` → `DECISIONS-REQUESTED.md` → `H-NEXT-ACTION.md`. The rest is reference.

## The Founder's A–J → files

| letter | file | one line |
|---|---|---|
| A | `A-SOURCE-ARCHITECTURE.md` | Source → SDM → block trust → Role Layer → guards → attachment → TSL, each stage with gold + slice numbers and what was falsified |
| B | `B-TRUSTED-STRUCTURED-LESSON.md` | the per-lesson document: 238 built, 2 FULL / 236 PARTIAL, shape and invariants |
| C | `C-HYBRID-SMART-BOOK.md` | two projections of the same sequence — `with_images` (gated) and `no_images` (functional now); counts per mode |
| D | `D-VISUAL-LEARNING.md` | typed / source-grounded / fail-closed: what the source side gives, what is not started |
| E | `E-SAM-TUTOR.md` | SAM Tutor ≠ Chat: permitted acts vs measured trust; the LLM realises, never decides |
| F | `F-LEARNINGCONTEXT-VS-LEARNINGVIEW.md` | runtime semantics — what `lib/` has (file:line), what the docs propose, four options; **LearningSession kept OPEN** |
| G | `G-EVIDENCE-FLOW.md` | provenance chain today vs the block-id chain the slice validated |
| H | `H-NEXT-ACTION.md` | ranked bounded next steps with the number each must move; nothing started |
| I | `I-MEASURED-TRUST-AND-COVERAGE.md` | every number with its denominator (3,679 canonical · 3,381 ranged · per-book repaired) |
| J | `J-LEGAL-PRODUCT-GATES.md` | page-image licensing = open LEGAL GATE; seven other gates |
| — | `ROLE-LAYER-AND-SHORT-ANSWER-GATE.md` | the six roles, per role, with numbers; Short-Answer verdict (I, extended) |
| — | `DECISIONS-REQUESTED.md` | every decision the Founder must make, options + evidence (H/J, extended) |
| — | `RISKS.md` | residual risks after the slice, ranked |
| — | `JIRA-STATUS.md`, `MANIFEST.md` | tickets/PRs; file inventory, the 00–09 → A–J mapping, how to reproduce |
| — | `tables/` | copies of the measured tables (`gold-scores.md`, `slice-report.md`, `sgv-report.md`) |

## Conventions

- **MEASURED** = computed by a script in `tool/corpus/tc2_*.py` on the slice or the gold set and reproducible from `poc-out/trusted-corpus/tc-v2/tc2-p1/` + MANIFEST.md · **OBSERVED-IN-CODE** = read from `lib/` with a file:line · **ESTIMATED** = extrapolation, always labelled · **HYPOTHESIS** = a proposal, not evidence.
- Metrics are never collapsed: text ≠ order ≠ roles ≠ attachment ≠ false trust ≠ critical errors; denominators are always stated.
- Trust > coverage: a withheld block is a safe failure; a trusted wrong block is the failure counted. The coverage gain (funnel) is reported as a measurement, not as the success criterion.
- **Governance:** branch → PR → CI → Jira Code Review → READY FOR FOUNDER REVIEW. No merge authority was granted or used.
