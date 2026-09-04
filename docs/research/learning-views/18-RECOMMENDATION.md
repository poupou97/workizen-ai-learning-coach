# 18 — Recommendation

**Status:** RESEARCH + ARCHITECTURE HYPOTHESIS. This file recommends; it does not decide. Any
decision the Founder takes from it must be recorded per `canonical/KNOWLEDGE_UPDATE_PROTOCOL.md`
(this package records none). Corpus-dependent answers are tagged PENDING TRUSTED-CORPUS FINDINGS;
no Trusted-Corpus bundle existed on the Desktop when this was written — apply §5 when it does.

## 1. Overall

**B — ADOPT WITH CHANGES.**

*Adopt:* ONE TRUSTED LESSON → MULTIPLE LEARNING VIEWS as the product framing; Learning View ≠
Learning Source; deterministic, provenance-bearing Views; SAM Tutor (not chat); Activity Patterns
as capabilities inside Views; source page always reachable.

*Changes required:* (1) define Views **inside `LearningContext`, after intent** — never as a
"mode" layer (Convergence struck LEARNING MODE); (2) Mode 1's first honest form is **Trusted
Fragments over a Source Page**, not a re-typeset book — Image/Table/Formula blocks are HYPOTHESIS
until the Trusted Corpus study rules; (3) Mode 2 is a **renderer family gated by typed data**
(two shapes exist); (4) Mode 3 is the **existing Pedagogy Runtime** plus the Short-Answer Surface,
with the board's graded MCQ made fail-closed; (5) View recommendation stays a **hypothesis**
reusing existing signals; (6) no generic renderer, no graph DB, no LLM composition, no unification
of Deep/Scale by decree.

## 2. Per Mode

| Mode | Verdict | Reason |
|---|---|---|
| **MODE 1 — Smart Book / Đọc như sách** | **B** | Text roles with per-block trust exist (6 books); no image/table/formula/activity blocks; tableLike pages untrusted; nearest real board lesson has 0 trusted units — ship "fragments + page image" first, fail closed, TRACE only. PENDING TRUSTED-CORPUS FINDINGS for the full block model. |
| **MODE 2 — Visual Learning / Trực quan** | **B** | Founder's deterministic hypothesis is right and partially PROVEN (Process, Spatial); Timeline/Concept-map/Comparison are blocked on extraction, not UI; renderers dispatch by data shape; interactions on visuals may mint evidence through the existing gate. |
| **MODE 3 — SAM Tutor / Học với SAM** | **B** | Runtime exists (`PlannedAct`, `RealizationRequest`, guard, blueprint); LLM shadow (WAL-30); reach = 1 lesson on the Deep path; Short-Answer Surface is the measured bottleneck (+76 lessons); grading only with SGV key. Adopt the name and the session framing; not a chat. |

## 3. Per architecture idea

| Idea | Verdict | One-line reason |
|---|---|---|
| Trusted Structured Lesson (one lesson-scoped document) | **B** | FORMALIZE existing pieces (LessonKey, layout blocks, LessonActivity, SemanticBinding, one SourceRef) into a document with boundary confidence and no keys inside; do not use it to merge Deep/Scale paths. |
| Multi-View Renderer | **B** | One document → three Views is sound; the dispatch is the existing activity/surface seam (ADR-009), not a new generic engine or second resolver. |
| Visual Renderer Family | **B** | Build a member only when a typed shape with provenance exists on ≥1 gold-validated lesson (rule that produced WAL-185); reject "generic mindmap". |
| SAM Tutor Runtime | **A** | Already built and guarded; the concept renames it — extend reach and add the missing Surface. |
| View Recommendation / Next Action | **C** | Deterministic mapping from existing signals is cheap and reasoned, but no evidence a *view* proposal changes behaviour; test like U1 before building; never show a row without a signal; no time estimates. |
| PDF-as-Reference | **A** | The page raster/region is the provenance anchor and the fail-closed fallback for every View; required, not optional; licensing (OQ8) to confirm. |
| Structured Content Delivery (tải theo sách/bài) | **B** | ADR-006 already; MEASURED ≈10× smaller for text per book, but images dominate — savings depend on a page-raster/figure policy that must be measured (ADR-006 storage benchmark), not asserted. |

## 4. The 25 research questions — explicit answers

1. **Are three top-level Learning Views the right abstraction?** Yes as *product-level* Views
   defined inside `LearningContext` after intent; they correspond to three epistemic relations
   (fidelity · representation · pedagogy). Not as modes, not as 27 patterns. HYPOTHESIS to test:
   children may not switch (OQ3).
2. **Chat or SAM Tutor?** SAM Tutor — doctrine (Convergence §5/§23), the act-driven runtime, and
   ITS prior art (AutoTutor EMT, Cognitive Tutors) all say state-machine-with-language, not chat.
   Chat is a mechanism inside Surfaces only.
3. **One renderer or a family?** A family dispatched by data shape; two members exist; add the
   third only under the WAL-185 re-activation triggers.
4. **Can all three consume one canonical Trusted Lesson?** Yes for Modes 1–2 by construction; Mode
   3 needs two side-joins that must stay outside the document (SGV keys, learner state).
5. **Common data:** `lessonKey`, chapter, boundary, pages (image refs), blocks with `sourceRef`/
   `trusted`, version, provenance wording rule.
6. **View-specific data:** Mode 1 reading order/page rasters/display trust/annotations; Mode 2
   `typedData` + representation explanation; Mode 3 activities, bindings, blueprint, keys, state.
7. **Can Mode 1 replace the PDF Viewer?** There is no PDF viewer today; Mode 1 as fragments-over-
   page *is* the reading view because it contains the page; text-only reconstruction cannot
   replace the page yet. PENDING TRUSTED-CORPUS FINDINGS per subject.
8. **When should the original PDF remain accessible?** Always as a page region inside Mode 1 —
   for every untrusted/tableLike/figure region, for provenance drill-down from any View or SAM
   line, for parents.
9. **How should provenance survive transformation?** Keep `sourceDocumentId · pagePdf/pagePrinted ·
   blockId · bbox` on every block and datum (one `SourceRef`, one bbox convention — two coexist
   today), add chapter and `layoutVersion` to packs, forbid rendering unreferenced content, render
   citations only via `sourceLineForChildOf`.
10. **How does Visual Learning remain source-grounded?** Typed data only, extracted at build time
    with provenance and a gold set (stories-pipeline pattern); nodes/edges verbatim; renderer
    refuses untyped input; SAM commentary guarded; build-time diff against the document.
11. **Which visualisation types are genuinely useful by subject?** Evidence-backed: concept/
    knowledge maps (Nesbit & Adesope 2006, stronger when constructed); process views for
    experiments (corpus-native); maps for Địa (asset-native). Timeline for Sử is plausible but the
    registry shows source reasoning/observe dominate Sử 4–5 — HYPOTHESIS. Comparison/Data need
    tables (PENDING).
12. **Deterministic vs AI-generated?** Structure and facts deterministic always; AI at most for
    guarded commentary; never for nodes/edges/dates/answers. Reference systems that generate
    visuals ship them unanchored (DeepTutor `source_anchors=[]`).
13. **Activity Patterns vs Learning Views?** Patterns are capabilities inside Views through
    Surfaces; Mode 3 hosts nearly all, Mode 2 the structural six (+Experiment), Mode 1 only reading/
    source/inline checks (`14`).
14. **How does Student Evidence move between Views?** It doesn't need to: evidence is keyed by
    SkillCase/concept + lesson lineage, not by View; display Views emit TRACE; Surfaces mint through
    one validator; View id is not on the event.
15. **Can learning started in Mode 1 continue in Mode 3?** Yes via an anchored `LearningContext`
    (`anchorBlockId` — HYPOTHESIS) and Surface push from an inline question; intent is never re-asked.
16. **Can SAM recommend a Learning View as Next Action?** Mechanically yes with existing signals
    (`proposeIntent`, `LearningAgenda`) and a small deterministic table; whether it *helps* is
    untested (C). Show only with a reason; no fabricated durations.
17. **Offline/download/cache?** Per ADR-006: book packs (documents, typed data, keys), page
    rasters per lesson range, curated assets, grade retrieval index; learner data device-local;
    every View offline; LLM (shadow) independent of retrieval.
18. **Could structured content materially reduce size?** For text yes (≈2.7 MB layout JSON vs 20 MB
    PDF per book, MEASURED, uncompressed); for images unproven (4 MB per curated map; page rasters
    approach PDF size without a compression policy). Measure per ADR-006 item 3. PENDING
    TRUSTED-CORPUS FINDINGS (image policy).
19. **Learn from DeepTutor:** the lesson-document *shape* (Chapter → Page → Block{type, status,
    payload, anchors}), per-reader overlay separation, page-scoped "ask" carrying context, the
    guided-learning block vocabulary. Not its content generation or anchors.
20. **From Mathigon:** textbook + tutor coexistence at step granularity; goal-gated progression;
    deterministic keyed hints (= `RealizationPolicy.template`); inline blanks as a keyed pattern;
    glossary links.
21. **From Oppia:** `Misconception{feedback, must_be_addressed}` as the shape for SAM's missing
    model; ordered hints then solution; `labelled_as_correct` as an authored key (same fail-closed
    rule); `missing_prerequisite_skill_id` as a typed reason for `diagnosePrerequisite`.
22. **From H5P:** the typed Timeline model as the target for `HistoricalEvent[]`; composition of
    reusable blocks applies to Surfaces, not to the source; "viewed = progress" is the anti-pattern.
23. **Scaffold / OpenMAIC useful ideas:** Scaffold — learner projection structurally without answer
    keys; contracts ≠ grading ≠ UI boundaries enforced by tooling. OpenMAIC — a versioned,
    validated scene/action DSL as a shape for compiling a blueprint sequence into a deterministic
    session script; frozen exhaustive unions (= SAM `sealed`).
24. **What NOT to copy:** LLM-written blocks; unanchored visuals/quizzes; AI grading without keys;
    chat-/agent-first tutoring; hand-authored lessons at scale; random praise; "viewed = progress";
    GPL/AGPL code; generic layout engines; any block type without extractor or key (`11` §F).
25. **Strengthen or complicate the Learning OS?** **Strengthens** if implemented as a presentation
    policy over the existing seven planes with one lesson document and the existing seams;
    **complicates** (anti-principle #5) if it adds a mode layer, a second resolver, a layout engine,
    a graph DB, or runtime generation. The concept's own §12 trust rule is what keeps it on the
    right side.

## 5. Reconciliation checklist — when the Trusted Corpus Feasibility bundle lands

- [ ] Re-issue the Mode 1 verdict per subject family using the study's fidelity/feasibility tables.
- [ ] Re-classify Image/Table/Formula in `12` §2 and update answers 7, 9, 18 above.
- [ ] Replace the 3,679 denominator and boundary semantics where the study re-derives them.
- [ ] Adopt the study's structured-document model as the base for `12` §3 if one is proposed.
- [ ] If the study contradicts any MEASURED claim here (e.g. role accuracy, trusted-page ratios),
      the study wins; mark this file's claim superseded rather than editing it silently.

## 6. If the Founder accepts B — research-only next steps (no implementation implied)

1. **Measurement on one real lesson** (KHTN 6 Bài 16 or 17, device-valid in WAL-206): list
   trusted blocks by role, what a Trusted-Fragments Mode 1 would show/hide, and which typed data
   Mode 2 could consume. Output: one page, numbers only.
2. **Decision memo** (Founder): Views inside `LearningContext`; "Đọc" stays `lookup`; no mode
   vocabulary in code. Record per the knowledge-update protocol.
3. **Consume the Trusted Corpus study** and apply the four reconciliation checklists.
4. Only then consider a ticket for the Short-Answer Surface (already WAL-205's first item) — it
   is the one build that Mode 3 needs and that is independent of this concept.
