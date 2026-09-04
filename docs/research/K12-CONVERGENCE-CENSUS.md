# K-12 Convergence Coverage Census

Founder-approved architecture convergence direction (2026-09-04), merging
the two curriculum paths WAL-196 found (Deep Intelligence:
Concept→SkillCase→CurriculumEdge→Pedagogy→retrieval→PlannedAct; Scale:
Corpus→LearningActivity→Surface→Evidence). Full findings, all 22 Founder
questions answered, and CSV exports: `~/Desktop/
HOC-CUNG-SAM-K12-CONVERGENCE-REVIEW-LATEST.zip` (Desktop-only, not
committed — corpus-derived, per this repo's data doctrine). This file is
the permanent, versioned summary.

Source script: `tool/corpus/k12_convergence_census.py`. Source data:
`poc-out/k12-convergence-census.json` (gitignored, regeneratable).

## The headline number

Of 3,679 canonical SGK lessons (Grade 1-12, reconciled fresh against
`curriculum-structure.json` — same denominator this session's
Learnable-coverage work already used, confirmed with no drift):

- **40 lessons (1.09%) CONVERGENCE_READY** — real activity AND real
  semantic/pedagogy structure to bind it to.
- **1,366 (37.13%) PARTIAL** — has one but not the other.
- **1,457 (39.60%) NOT_READY** — neither yet (850 lack any activity
  structure at all; 607 are blocked on broken TOC/layout extraction).
- **816 (22.18%) EXTERNAL_MODALITY** — GDTC/Âm nhạc/Mĩ thuật/HĐTN/
  HĐTN-HN/GDQP, physical/performance subjects the text-based architecture
  isn't built for, regardless of extraction quality.

A small, honest, measured number — deliberately not inflated. Full
funnel: `structured` 2,520 (68.5%) → `activityPresent` 111 (3.02%) →
`semanticMappable` 2,079 (56.51%) → `pedagogyMappableVerified` 37 (1.01%,
lesson-level, conservative) → `deepIntelligenceReady` **1** (0.03%,
exact — `SliceCurriculum`'s single registered lesson) →
`uxConnected` 111 (3.02%).

## What this does NOT claim

Not full manual annotation — a census from already-computed pipeline
outputs (toc_health.py, compiled lesson-index packs, the generic
units-k12 extractor), no new extraction performed. Not every subject's
activity taxonomy was classified to lesson-level confidence — only 5
patterns (Experiment 37 lessons/7 grades, Reading 61, Writing 41, Problem
Solving 10, Source Reasoning 4) plus 1 deferred (Tin học Source-Grounded
Assessment, 2 lessons) were measured this pass; Founder's longer seed
list (Comparison/Classification/Process/Map-Spatial/Data-Chart/
Listening/Speaking/Project-Group) was left honestly unmeasured rather
than guessed.

## Concept/SkillCase and Prerequisite scale verdict

**FORMALIZE**, not REPLACE — the model is sound where tested (1 lesson,
real invariants) but reaching further requires deliberate binding work,
not a redesign. Concretely: 10 Toán lessons already have a
`skillCaseId` string on their activity record but no validated join
against the `SkillCase` registry — the cheapest, highest-confidence next
unlock (MEASURED, not estimated).

Prerequisite evidence: **1 hand-vetted `sourceStated` edge in the entire
repo.** Confirms WAL-196's HYPOTHESIS classification of Knowledge Space
Theory — not enough data to test whether an outer-fringe computation
would change any real recommendation. WAL-202 (KST re-evaluation) stays
blocked.

## Pedagogy scale (SGK vs SGV, separated)

SGV's "MỤC TIÊU" (objective) marker is present in 204/220 books (92.7%,
book-level signal) — the convention is nearly universal. But lesson-level
extraction has only been built and verified for 3 narrow slices: Toán
objectives (WAL-76), Science Chuẩn bị/Tiến hành (WAL-190, 37 lessons,
SGK not SGV), Tin học answer-keys (WAL-192, 2 lessons). The gap between
"marker present" and "lesson-level extraction built" is the largest
measured pedagogy opportunity, ranked P1 behind the Toán binding fix.

## Thin Convergence Bridge (design proposed, not implemented)

```
LearningActivity (unchanged)
      ↓ optional, zero-or-one
SemanticBinding
      ├─ activityRef
      ├─ conceptId? / skillCaseId?   (nullable — most lessons won't have these yet)
      ├─ pedagogicalRole?             (ExposureRole/PedagogicalIntent/TeachingAct — kept separate, not merged)
      ├─ sourceSignal                 (GENERIC_SEMANTIC_UNIT | VERIFIED_PEDAGOGY | HUMAN_CURATED)
      ├─ confidence
      └─ provenance                   (existing Provenance type, reused)
```

**Fail-closed guarantee, non-negotiable**: no binding ⇒ the activity works
exactly as it does today. Convergence is additive — it must not turn any
of the 111 currently-UX_CONNECTED lessons into fewer. No mass-generation
of Concept/SkillCase entities; binding only happens where a real signal
(generic unit or verified pedagogy) supports it, incrementally.

## Representative gold set (11 lessons, selected, not yet validated)

Spans grade 4/6/10 happy-path Experiment lessons, a Source Reasoning
lesson, the one DEEP_INTELLIGENCE_READY lesson (regression check), a
Toán PARTIAL lesson (the P0 target), a known-falsified Ngữ văn lesson, both
Tin học edge cases (the 2 safe HIGH_CONFIDENCE lessons and the
"Hoạt động 1" false-trusted-answer trap), a GDTC EXTERNAL_MODALITY
control, and a NO_TOC grade-1/2 LAYOUT_EXTRACTION_BLOCKED control. Full
rationale per lesson: Desktop bundle `18-GOLD-SET-VALIDATION.md`.

## Next steps (WAL-200)

1. Bind the 10 measured Toán lessons first (cheapest, tests the bridge
   design against real data before extending further).
2. Validate the bridge against the 11-lesson gold set.
3. Implement one bounded vertical slice reusing an existing Surface.
4. Only then consider the ~87-lesson ESTIMATED extension to
   Khoa học/KHTN/Hoá học/Vật lí, and separately, SGV pedagogy extraction
   at scale (P1, sequenced after Toán, not before).
