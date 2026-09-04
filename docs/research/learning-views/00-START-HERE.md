# 00 — START HERE · Learning Views Concept & Reference Research

**Track:** P0 Research / Product Concept · **Status:** RESEARCH + ARCHITECTURE HYPOTHESIS ONLY — **nothing here authorises implementation.**
**Date:** 2026-09-04 · **Model:** Fable 5.1 · **Branch:** `research/learning-views-concept` · **Jira:** see `19-JIRA-CONFLUENCE-STATUS.md`
**Founder order:** "HỌC CÙNG SAM — LEARNING VIEWS CONCEPT & REFERENCE RESEARCH" (ONE TRUSTED LESSON → Đọc / Trực quan / Học với SAM).
**Founder concept board:** `concept/concept-ai-first/learning-view.png` in the main checkout (untracked Founder file — described in `03` and `16`, never copied here).

## What this package is

A bounded Founder Review package answering one question: *should «Học cùng SAM» converge on
ONE TRUSTED LESSON → THREE LEARNING VIEWS (Mode 1 Smart Book · Mode 2 Visual Learning · Mode 3
SAM Tutor), and if so on what data contract?* It reconstructs the AS-IS lesson experience from
code, studies six reference systems (DeepTutor, Mathigon, Oppia, H5P, Scaffold, OpenMAIC) plus a
small set of standards and learning-science prior art, tries to **falsify** the proposed
architecture, and ends with an explicit A/B/C/D recommendation per Mode and per architecture idea.

## Read in this order

| # | File | Who | Minutes |
|---|---|---|---|
| 01 | `01-LEARNING-VIEWS-FOUNDER-SUMMARY.md` | Founder — page 1 is non-technical | 8 |
| 18 | `18-RECOMMENDATION.md` | Founder — A/B/C/D verdicts + the 25 numbered answers | 15 |
| 17 | `17-OPEN-QUESTIONS-AND-RISKS.md` | Founder — incl. "what the concept board assumes that evidence does not yet support" | 8 |
| 02 | `02-CURRENT-LESSON-EXPERIENCE-AS-IS.md` | PM / Dev — every AS-IS claim cites a file path | 10 |
| 03–06 | Concept · Smart Book · Visual Learning · SAM Tutor | PM / Dev | 25 |
| 07–11 | Reference comparison and per-repo findings | Dev / Architect | 25 |
| 12–15 | Structured Lesson contract · data flow · Activity Patterns · trust & provenance | Architect | 25 |
| 16 | `16-UX-CONCEPT.md` | Design — ASCII/mermaid wireframes on the existing design language | 8 |
| 19, MANIFEST | Tracking | — | 2 |

## Evidence labels used everywhere

- **MEASURED** — a number produced by running a script/query on the corpus or packs during this track (read-only), or previously measured in a cited WAL result doc.
- **OBSERVED-IN-CODE** — read directly in `lib/`, `tool/`, `assets/`, `pubspec.yaml`, ADRs (file path cited).
- **FROM-REFERENCE** — read in a reference repository (shallow-cloned to scratch for reading only) or a fetched document/standard; URL cited. If a reference could not be fetched, the failure is stated.
- **HYPOTHESIS** — a claim this package proposes but has not verified.
- **PENDING TRUSTED-CORPUS FINDINGS** — a claim that depends on the parallel *Trusted Corpus Feasibility Study* (`poc-out/trusted-corpus/`, `~/Desktop/HOC-CUNG-SAM-TRUSTED-CORPUS-FEASIBILITY-LATEST.zip`). **That study's evidence takes precedence over this package.** At the time of writing (2026-09-04 23:5x) the LATEST bundle did **not** exist on the Desktop, so `12`, `13`, `15` and `18` carry a *Reconciliation checklist* the Founder can apply when it lands.

## Hard boundaries respected

- No product code, schema, or UI was implemented. No parsers, OCR, or heavy compute were run.
- `poc-out/` was read only for AS-IS facts; nothing derived from it is committed. `poc-out/trusted-corpus/` was not read or touched.
- Reference repositories were cloned to the session scratch directory only, never into the SAM repo.
- Canonical Knowledge (`workizen-knowledge-base/canonical/README.md`, `02_PRINCIPLES.md`) was read first; this package creates **no new ecosystem doctrine** and records **no decision** — it proposes candidates for the Founder.

## One-line answer

**B — ADOPT WITH CHANGES.** The concept is right as a *product* framing (one source of truth, many ways to understand) and already matches most of SAM's existing architecture; it is **not yet supported by the corpus** for native block-level Smart Book or for History/Concept-map visuals, and it must be defined as *representations chosen inside a LearningContext*, not as a fourth "mode" layer that competes with LEARNING INTENT. Details in `01` and `18`.
