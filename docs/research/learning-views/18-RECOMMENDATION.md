# 18 — Recommendation

> **Reconciled with TC-v1 (2026-09-05).** `TC-nn` = `docs/research/trusted-corpus/nn-….md` (WAL-208). Changes: §1 change (2) and new (7); §2/§3 reasons re-issued with measured numbers (verdicts unchanged); **new §3a classification re-evaluation**; answers 4, 5, 7, 9, 11, 18 updated; §5 applied with the superseded-claims list; §6 updated.

**Status:** RESEARCH + ARCHITECTURE HYPOTHESIS. This file recommends; it does not decide. Any
decision the Founder takes from it must be recorded per `canonical/KNOWLEDGE_UPDATE_PROTOCOL.md`
(this package records none). Corpus-dependent answers were tagged PENDING TRUSTED-CORPUS FINDINGS
at writing; §5 was applied on 2026-09-05.

## 1. Overall

**B — ADOPT WITH CHANGES.**

*Adopt:* ONE TRUSTED LESSON → MULTIPLE LEARNING VIEWS as the product framing; Learning View ≠
Learning Source; deterministic, provenance-bearing Views; SAM Tutor (not chat); Activity Patterns
as capabilities inside Views; source page always reachable.

*Changes required:* (1) define Views **inside `LearningContext`, after intent** — never as a
"mode" layer (Convergence struck LEARNING MODE); (2) Mode 1's first honest form is **Trusted
Fragments over a Source Page**, not a re-typeset book — TC-v1 confirms the shape and fixes the
block model: Figure regions as images (EXTEND), Table objects only on a GPU path, Formula never as
text (`12` §2); (3) Mode 2 is a **renderer family gated by typed data** (two shapes exist); (4)
Mode 3 is the **existing Pedagogy Runtime** plus the Short-Answer Surface, with the board's graded
MCQ made fail-closed; (5) View recommendation stays a **hypothesis** reusing existing signals;
(6) no generic renderer, no graph DB, no LLM composition, no unification of Deep/Scale by decree;
**(7) — added by TC-v1 —** the trust unit is the **block** (Structured Document Model, TC-11) and a
**role layer** measured at ≥ 0.95 question precision precedes any auto-labelled prompt (TC-07);
"One Trusted Lesson" means the lesson's TRUSTED-block subset with page images for the rest
(TC-18 verdict; Founder decision, `17` §5 C11).

## 2. Per Mode

| Mode | Verdict | Reason |
|---|---|---|
| **MODE 1 — Smart Book / Đọc như sách** | **B** | Text roles exist (6 books) but their trust is page-gated (TC-02 §3): TLSR 0.193 / FTR 0.119 on hard pages (TC-08 §1); no image/table/formula/activity blocks; nearest real board lesson has 0 trusted units — ship "fragments + page image" first, fail closed, TRACE only. **TC-v1 confirms the shape** (TC-19 #7 image-first; TC-18 Q5 prose/questions/sidebars/boxes trustworthy under a cascade) and adds: `question`-role blocks as plain text until the role layer measures ≥ 0.95 (TC-07); formula / speech-bubble / colour-heavy / table / diagram-map-timeline pages → page image only (TC-05 §3, TC-06). |
| **MODE 2 — Visual Learning / Trực quan** | **B** | Founder's deterministic hypothesis is right and partially PROVEN (Process, Spatial); Timeline / Concept-map / Comparison are blocked on extraction, not UI — **now with measured reasons**: timeline order wrong in every parser (TC-06); tables as objects only on the GPU path (TC-07); relations available today are structural (`caption_of` 0.90–0.95, `options_of`) (TC-07, TC-11). Renderers dispatch by data shape; interactions on visuals may mint evidence through the existing gate. |
| **MODE 3 — SAM Tutor / Học với SAM** | **B** | Runtime exists (`PlannedAct`, `RealizationRequest`, guard, blueprint); LLM shadow (WAL-30); reach = 1 lesson on the Deep path; Short-Answer Surface is the measured bottleneck ("+76 lessons" — a WAL-206 old-extractor count, to recompute per TC-15); grading only with SGV key, now via `answer_of` + answer-leak guard (TC-14); no auto-labelled question as a graded prompt until role precision ≥ 0.95 (TC-07 §Consequence). Adopt the name and the session framing; not a chat. |

## 3. Per architecture idea

| Idea | Verdict | One-line reason |
|---|---|---|
| Trusted Structured Lesson (one lesson-scoped document) | **B** | FORMALIZE existing pieces onto TC-11's SDM: `TrustedLessonDocument` = the per-lesson projection of `TrustedLearningSource` (tri-state trust, 20 roles, relations, one bbox convention, per-block lesson attachment) with no keys inside; do not use it to merge Deep/Scale paths. |
| Multi-View Renderer | **B** | One document → three Views is sound; the dispatch is the existing activity/surface seam (ADR-009), not a new generic engine or second resolver. TC-11 §2: "projections carry block ids" — same rule. |
| Visual Renderer Family | **B** | Build a member only when a typed shape with provenance exists on ≥1 gold-validated lesson (rule that produced WAL-185). TC-v1: extractable now = captions, option order, `heading_path`; withheld = formulas, tables (Mac), timelines, maps, diagrams (`05` §2). Reject "generic mindmap". |
| SAM Tutor Runtime | **A** | Already built and guarded; the concept renames it — extend reach and add the missing Surface. Not in TC-v1's scope. |
| View Recommendation / Next Action | **C** | Deterministic mapping from existing signals is cheap and reasoned, but no evidence a *view* proposal changes behaviour; test like U1 before building; never show a row without a signal; no time estimates. |
| PDF-as-Reference | **A** | The page raster/region is the provenance anchor and the fail-closed fallback for every View — and, after TC-v1, the **delivery path** for math/diagram/table content (TC-19 #7); required, not optional; licensing (OQ8) to confirm. |
| Structured Content Delivery (tải theo sách/bài) | **B** | ADR-006 already; MEASURED ≈10× smaller for text per book and, per page, SDM ≈ 30–40 KB vs 200-dpi render ≈ 330 KB (TC-16) — images dominate; savings depend on a reader-raster policy that is STILL UNMEASURED after TC-v1 (ADR-006 storage benchmark), not asserted. |

## 3a. Classification re-evaluation against TC-v1 (2026-09-05)

Rule applied: change a classification **only if the evidence forces it**.

| Item | Before | After | Changed? | Why (one line) |
|---|---|---|---|---|
| Concept: One Trusted Lesson → Three Views | B | B | no | TC-18 supports the framing but reframes the promise: trusted subset (555/3,381 fully, ≈ 2,800 partially), not the whole lesson — a change *inside* B, for the Founder to word (`17` §5 C11). |
| Mode 1 Smart Book | B | B | no | "prose/question part trusted, math/diagram/elementary withheld" (TC-18 Q5, Q15–16) *is* Trusted Fragments over a Source Page; TC-v1 adds block-level trust and a role gate, it does not change the class. |
| Mode 2 Visual Learning | B | B | no | Two shapes still real; TC-v1 shows the others are further away (timeline order fails every parser, TC-06; tables GPU-only, TC-07). |
| Mode 3 SAM Tutor | B | B | no | Runtime untouched by TC-v1; "role layer ≥ 0.95 before auto-labelled prompts" (TC-07) fits the existing fail-closed rule. |
| Trusted Structured Lesson | B | B | no — base changed | FORMALIZE onto TC-11's SDM as a per-lesson projection. Inside `12` §2 five classes changed: **Question** FORMALIZE → HYPOTHESIS (precision 0.69, TC-07); **Activity label** FORMALIZE → HYPOTHESIS (0.45, TC-07); **Image/Figure** HYPOTHESIS → EXTEND as image region (TC-11, TC-07); **Table** HYPOTHESIS → EXTEND on GPU path / REJECT as text on Mac path (TC-07, TC-14); **Formula** HYPOTHESIS → REJECT as text, RETAIN as withholding trigger (TC-09, TC-19 #7). |
| Multi-View Renderer | B | B | no | TC-11 §2 "projections carry block ids" is the same rule. |
| Visual Renderer Family | B | B | no | Extractable now: captions (`caption_of` 0.90–0.95), MCQ options in order, `heading_path`; withheld: formulas, tables (Mac), timelines, maps, diagrams (TC-06, TC-07, TC-10). |
| SAM Tutor Runtime | A | A | no | Not in TC-v1's scope. |
| View Recommendation | C | C | no | Not in TC-v1's scope. |
| PDF-as-Reference | A | A | no (strengthened) | TC-19 #7 makes the page crop the delivery path for math/visual content, not only the fallback. |
| Structured Content Delivery | B | B | no | Per-page bytes now measured (TC-16); reader raster policy still unmeasured. |

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
   3 needs two side-joins that must stay outside the document (SGV keys, learner state). TC-11: the
   document is a projection of `TrustedLearningSource`; the serializer refuses WITHHELD/CONFLICT blocks.
5. **Common data:** `lessonKey`, chapter (`heading_path`), per-block lesson attachment, pages
   (image refs + `layout_features`), blocks with `sourceRef`/`trust.status`, figures, version,
   provenance wording rule.
6. **View-specific data:** Mode 1 reading order/page rasters/display trust/annotations; Mode 2
   `typedData` (+ tables on the GPU path) + representation explanation; Mode 3 activities, bindings,
   blueprint, keys, state.
7. **Can Mode 1 replace the PDF Viewer?** There is no PDF viewer today; Mode 1 as fragments-over-
   page *is* the reading view because it contains the page; text-only reconstruction cannot
   replace the page yet. **TC-v1, per layout feature:** plain prose / question / sidebar pages —
   fragments trustworthy under a cascade (FTR 0–0.09, TC-05 §3); formula, speech-bubble,
   colour-heavy elementary, table, diagram / map / timeline pages — page image only (TC-05 §3,
   TC-06). Per subject: Toán 4/554, KHTN 4/145, Vật lí 1/82 lessons fully sourceable (TC-18 Q17);
   per-subject text fidelity STILL UNMEASURED after TC-v1.
8. **When should the original PDF remain accessible?** Always as a page region inside Mode 1 —
   for every untrusted/tableLike/figure region, for provenance drill-down from any View or SAM
   line, for parents; and for every formula (TC-19 #7).
9. **How should provenance survive transformation?** Keep `sourceDocumentId · pdf_page/printed_page ·
   blockId · bbox` on every block and datum — **resolved by TC-11 §2: one `SourceRef`, bbox
   `[x, y, w, h]` normalised, block id `<doc>:p<NNN>:<parser>:<n>`** — add chapter (`heading_path`)
   and pipeline ids (`provenance.extraction_method`, run id — TC-12) to packs, forbid rendering
   unreferenced content, render citations only via `sourceLineForChildOf`.
10. **How does Visual Learning remain source-grounded?** Typed data only, extracted at build time
    with provenance and a gold set (stories-pipeline pattern); nodes/edges verbatim; renderer
    refuses untyped input; SAM commentary guarded; build-time diff against the document.
11. **Which visualisation types are genuinely useful by subject?** Evidence-backed: concept/
    knowledge maps (Nesbit & Adesope 2006, stronger when constructed); process views for
    experiments (corpus-native); maps for Địa (asset-native). Timeline for Sử is plausible but the
    registry shows source reasoning/observe dominate Sử 4–5 — HYPOTHESIS, and timeline order fails
    every parser (TC-06). Comparison/Data need table objects — **GPU path only** (TC-07).
12. **Deterministic vs AI-generated?** Structure and facts deterministic always; AI at most for
    guarded commentary; never for nodes/edges/dates/answers. Reference systems that generate
    visuals ship them unanchored (DeepTutor `source_anchors=[]`); TC-11 §6 forbids LLM/VLM re-guessing.
13. **Activity Patterns vs Learning Views?** Patterns are capabilities inside Views through
    Surfaces; Mode 3 hosts nearly all, Mode 2 the structural six (+Experiment), Mode 1 only reading/
    source/inline checks (`14`). Counts to recompute on a role-labelled SDM (TC-15).
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
    PDF per book, MEASURED; SDM ≈ 30–40 KB/page, TC-16); for images no at full resolution (4 MB per
    curated map; a 200-dpi page render ≈ 330 KB → a ~118-page book ≈ 39 MB of rasters, more than its
    20 MB PDF — derived from TC-16 and TC-03). Reader-dpi/webp policy STILL UNMEASURED after TC-v1;
    measure per ADR-006 item 3. Licensing (OQ8) is a Founder decision.
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
    GPL/AGPL code (TC-05: MinerU/PyMuPDF AGPL, Marker GPL); generic layout engines; any block type
    without extractor or key (`11` §F).
25. **Strengthen or complicate the Learning OS?** **Strengthens** if implemented as a presentation
    policy over the existing seven planes with one lesson document and the existing seams;
    **complicates** (anti-principle #5) if it adds a mode layer, a second resolver, a layout engine,
    a graph DB, or runtime generation. The concept's own §12 trust rule is what keeps it on the
    right side.

## 5. Reconciliation checklist — APPLIED 2026-09-05

- [x] Mode 1 verdict re-issued per layout feature (answer 7); per subject as fully-sourceable counts (TC-18 Q17); per-subject fidelity STILL UNMEASURED after TC-v1.
- [x] Image/Table/Formula re-classified in `12` §2 (§3a above); answers 7, 9, 18 updated.
- [x] Denominator: 3,381 ranged of 3,679 canonical (TC-03 §5); boundary = per-block attachment (`12` §3); the two numbers are kept apart (`17` §5 C1).
- [x] TC-11's SDM adopted as the base of `12` §3.
- [x] Contradicted MEASURED claims — **superseded, not edited silently**: (a) `04` §2 heading "0.90 role accuracy" → 0.81 / 0.51 on hard pages (TC-07); (b) `04` §2 question "AVAILABLE" → precision 0.69, not a usable role (TC-07); (c) `03` F2 reading order "0.99" → 0.976 XY-cut on hard pages (TC-05); (d) `04` §1 / `18` §2 "per-block trust exists" → page/region-gated (TC-02 §3); (e) `04` §2 "30.6 % of pages two-column" ↔ TC-03's 29.5 % side-by-side regions — the same measurement, reconciled not contradicted (TC-03 §6); (f) passage fidelity 0.86 ↔ 0.847 — consistent across different gold sets.

## 6. If the Founder accepts B — research-only next steps (no implementation implied)

1. **Measurement on one real lesson** (KHTN 6 Bài 16 or 17, device-valid in WAL-206 and inside
   the Science slice TC-19 #6 names): list trusted blocks by **SDM role** on both sources (XY-cut
   vs Docling ▸ XY-cut + math guard, TC-13 pattern), what a Trusted-Fragments Mode 1 would show/hide
   under the page-feature guard, and which typed data Mode 2 could consume. Output: one page, numbers only.
2. **Decision memo** (Founder): Views inside `LearningContext`; "Đọc" stays `lookup`; no mode
   vocabulary in code. Record per the knowledge-update protocol.
3. **Consume the Trusted Corpus study** — **done 2026-09-05** (this reconciliation). Remaining for
   the Founder: `17` §5 C1, C5, C6, C11, C12.
4. Only then consider a ticket for the Short-Answer Surface (already WAL-205's first item) — it
   is the one build that Mode 3 needs and that is independent of this concept.
5. **File the four ecosystem decisions TC-19 #11 names as PROPOSED** (SDM-as-source, block-level
   trust, image-first for math/visual, "trusted subset, not whole corpus") — they are the same
   decisions this concept depends on; neither study decides them.
