# 01 — Executive assessment · Founder pre-autonomy checkpoint · 2026-09-05

## Core question
**«Hiện tại Học cùng SAM thật sự đã có dữ liệu đủ tin cậy, kiến trúc đủ coherent và UI/UX đủ gần concept Founder để bật autonomous development chưa?»**

**Answer: NO — verdict C, NOT READY, RESOLVE P0 FIRST** (`08`). Not D: the kernel that exists is real and proven (fail-closed method gating, raw-event evidence, replayable mastery, three-axis claims, provenance rendering — 647/647 tests with packs, 633 + 14 pack-gated skips without, `flutter analyze` clean). Not B: five P0 gaps are decisions or measurements an agent cannot make alone, and two of them touch what a child reads and what a parent is told.

## The four layers in one line each (evidence in 02–05)

| Layer | Rating | What is true today (MEASURED unless marked) |
|---|---|---|
| 1 · Data / trusted corpus | **RED** trusted · YELLOW wired | 62,729 OCR pages, 3,240 lessons browsable (/3,679 canonical). Trusted Structured Lessons exist for **238** Science lessons only (2 FULL / 236 PARTIAL; six repaired-ranged books) at false-trust ≈ 0.10–0.12 on hard pages; **0 elsewhere**. The 113 "proven" lessons are wiring, not truth: built by the naive extractor (FTR 0.321 on hard pages), 77 % of their pages hard; where TC-v2 overlaps, 21/32 contain withheld text and 3/32 sit in the wrong lesson; 2/113 keys are non-canonical; 0 device records on disk. Role Layer cannot ask (QUESTION P 0.83–0.89 < 0.95, ACTIVITY 0.00). The packs on this Mac are the WAL-206 *experiment* build (97 router entries) with no build provenance. |
| 2 · Learning architecture | **YELLOW** | Kernel coherent on **one** registered lesson; two parallel paths with **zero** convergence code (Deep = 1 lesson; Scale = 187 openable / 3,650 TOC lessons in the on-disk packs); four named concepts have no code (LearningView, TrustedLearningSource, SemanticBinding, PlannedAct-as-runtime); six forks open (`03` §B.6); docs disagree with code and Jira, incl. an unverifiable "Founder-approved convergence" sentence. |
| 3 · Product / runtime | **YELLOW** | Closed loop real for one lesson; fail-closed at the kernel; **but** four ungraded taps mint `independentAttempt` and the Learning Map / parent summary read it as "Tự làm được" (two truths); `eventId` collisions and non-idempotent append (C1/C3 FAIL); pedagogy runtime dormant (0 runtime callers); no LLM in the app (good) and no type-level cage if one were wired; verbatim SGK text shown under a licence enum that forbids it. |
| 4 · UI/UX vs approved concept | **RED** vs concept · YELLOW as a reduced product | Overall **20–30 %**; Learning-View concept **5–15 %** (no Lesson Workspace, Smart Book, Trực quan or in-lesson SAM); SAM Tutor 15–25 % (rules-only, one lesson, unreachable for the lớp-6 learner); visual tokens 55–65 %; navigation 35–45 %. Home tells a lớp-6 child SAM has no content while KHTN 6 lessons open; that card's "Bắt đầu" opens the camera; identical "Đọc bài" rows; provenance leaks raw ids and crosses grades. |

## What "113 / 3,679" and "555 / 3,381" mean now
- **113 / 3,679 canonical** = activities wired to a Surface and byte-stable (regression oracle). Not text trust, not lesson identity, not device validity (`02` §2).
- **≈555 (recomputed 559) / 3,381 ranged** = lessons with no page carrying an *unhandled* layout feature — a layout filter predicting what a cascade could source without withholding. Not trusted, not learnable, not measured on those lessons (`02` §3). Neither number may be divided by the other's denominator.
- **238 / 238 repaired-ranged (six Science books)** = the only measured trust today; 2 FULL.

## Five P0 gaps (full table `07`)
1. Self-reports become competence claims (Founder decision on the evidence contract).
2. Shipped text is untrusted and unmeasured; no false-trust audit on served blocks; 3/32 wrong-lesson attachments (gates G1–G3).
3. No build provenance — experiment packs indistinguishable from default (mechanical, agent may fix).
4. Evidence-store integrity — id collisions, double-counted mastery, whole-file rewrite, no tamper check (half mechanical).
5. Two architectures, zero convergence code, unverifiable approval (Founder locks six forks).

## What may run autonomously now (B-lane, PRs only, never merge)
Build-provenance manifest + test · unique ids + idempotent append · lineage threading · capped/header attachment + identity check in the pack build · chooser-label and Home-card defects · route-or-delete `QuizSelectScreen` · per-pack `knowledgeModelVersion` · refuse-to-grade instead of `'unknown-case'` · Role-Layer signal research. Everything else waits for Founder decisions D1–D6 (`09`).

## Process facts the Founder should know
- **Evidence loss:** every `HOC-CUNG-SAM-*.zip` bundle and last night's `wal206-final-*.png` device screenshots were removed from the Desktop at ~10:10 today, before this audit began (not by the audit agents — folder timestamps and transcripts checked; not in Trash; not found elsewhere in the home folder). Bundles were regenerated from `main` / PR #58 / `poc-out` into `~/Desktop/HOC-CUNG-SAM-BUNDLES/`; the 24 WAL-206 screenshots are not recoverable. This is why `02` rates device validation RED and gate G6 (evidence retention in the repo-adjacent bundle) is proposed.
- **Device:** the Nokia went to sleep during the UI walk after a camera-permission dialog; the auditor woke it twice and swiped once each time, saw the pattern grid, and stopped — no pattern drawn, no bypass. One KHTN 6 Bài 6 reading session was recorded for «Na»; camera permission denied once; the lock-screen frame with personal notifications was deleted. Protocol addition: after any system dialog, check `dumpsys power` before the next tap.
- **Method:** three parallel read-only audits (data; learning + runtime architecture with `flutter test`/`analyze` and a 10-check runtime script; UI on device vs the concept boards), synthesised here; every number carries a script or file:line; Jira was read, not edited; nothing merged; no product code changed. Two PRs remain open from the previous round (#58 TC-v2, KB #1) — unreviewed, so the Architecture Review's conclusions are still DOC-CLAIM for this checkpoint.
