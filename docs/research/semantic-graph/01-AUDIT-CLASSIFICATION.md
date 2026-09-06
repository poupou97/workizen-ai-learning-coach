# Lane E1 · REUSE BEFORE ADDING — the audit, and §10 KEEP / EVOLVE / ADAPT / DEPRECATE

All paths absolute-from-repo-root; line numbers from the checkout at
`integration/round5-2026-09-06`.

Classification key: **EXISTS AND USED** (constructed and consumed outside tests, reachable from a
screen) · **EXISTS BUT NOT WIRED** (declared, tested, no non-test consumer) · **PARTIAL** (real but
fixture-scale or one-lesson) · **RESEARCH ONLY** (document, no code) · **MISSING**.

---

## 1. The inventory

### 1.1 Semantic model

| Thing | Where | Status | Note |
|---|---|---|---|
| `SemanticData` (sealed base) | `lib/core/lesson_model/semantic_data.dart:14` | **PARTIAL** | Never `new`'d in Dart. The **only** production construction path is `SemanticData.fromJson` at `lesson_document.dart:1024`; the data is authored by Python. |
| `ProcessSemantic` | `semantic_data.dart:185` | **EXISTS AND USED** | Real corpus data, 2 instances, one lesson. Producer `tool/corpus/tsl_to_lesson_document.py:356` (`tsl-enumerated-steps-v1`). |
| `ComparisonSemantic` | `semantic_data.dart:219` | **PARTIAL** | 1 instance, one lesson. Producer `tsl_to_lesson_document.py:395` — which **hardcodes Bài 17's title and its single dimension** (`:419`, `:424`) for any book fed through it. |
| `ConceptMapSemantic` | `semantic_data.dart:257` | **EXISTS BUT NOT WIRED** | Renderer at `visual_view.dart:609`; **zero producers**. Only construction in the repo is a test. |
| `TimelineSemantic` | `semantic_data.dart:296` | **PARTIAL** | Learner-visible data is **synthetic only** (`assets/fixtures/synthetic/lesson-05-…-b8.synthetic.json:628`). The real LS&ĐL fixture does not exist on disk. |
| `ProcessStep` / `ComparisonEntity` / `ConceptRelation` / `TimelineEvent` | `semantic_data.dart:140 / :205 / :247 / :285` | EXISTS | Each carries a **bare `sourceBlockId`** — a block id, not a span, not a page. |
| **`ComparisonDimension`** | `semantic_data.dart:213` | **PROVENANCE HOLE** | `name` + `values` and **no `sourceBlockId` at all**. The actual comparison content — the cell values a child reads — is unattributed. |
| `SemanticData` provenance | — | **MISSING** | The base class carries `id, title, trust, derivation` and **no `Provenance`, no page, no span, no bbox**. `semantic_data.dart:9` claims «Mỗi nút/hàng/bước mang `sourceBlockId`» — true of leaves, false of the object, and false of `ComparisonDimension`. |

### 1.2 Curriculum / knowledge

| Thing | Where | Status |
|---|---|---|
| `SemanticBinding` + `resolveBinding` | `lib/core/curriculum/semantic_binding.dart:87 / :172` | **PARTIAL** — machinery generic, **exactly one instance** (`khtn6_bai17.dart:107`) |
| `SemanticBindingRegistry` | `semantic_binding_registry.dart:10` | **PARTIAL** — a 1-row closed constant: `bindings = [khtn6Bai17TutorBinding]` (`:13`) |
| `Concept` | `concept.dart:43` | **PARTIAL** — **one instance in the whole repo**; its query surface `remediationFor` (`:101`) has no non-test caller |
| `CurriculumEdge` / `prerequisiteEdges` | `curriculum_edge.dart:29` / `prerequisite_edges.dart:20` | **EXISTS BUT NOT WIRED** — one hardcoded edge, no non-test consumer |
| `LearningObjective` | `learning_objective.dart:14` | **EXISTS BUT NOT WIRED** — producer is Python, no Dart consumer |
| `AiCurriculum` / `AiOutcome` | `ai_curriculum.dart:97 / :46` | **EXISTS BUT NOT WIRED** — never constructed outside tests |
| `SkillCase` | `skill_case.dart:17` | PARTIAL — 5 instances, 3 hardcoded sites (2 duplicated verbatim between `slice_curriculum.dart` and `mission_data.dart`) |
| `khtn6_bai17.dart` | `lib/core/curriculum/khtn6_bai17.dart` | **PARTIAL / lesson-specific** — 122 lines, 100 % `const`, one lesson, zero functions. Includes a hand-written page offset: `pageStart: 63, // trang IN (PDF 64; lệch −1 …)` (`:92`) |

⚠️ **Name collision worth fixing whoever touches it:** two unrelated `LessonRef` types —
`semantic_binding.dart:31` (`{sourceDocumentId, lessonNo}`) and `lesson_index.dart:14`
(`{no, title, pageStart}`).

### 1.3 Provenance — **two disconnected worlds**

| World | Types | Where |
|---|---|---|
| **content** | `SourceRef`, `ContentTrust`, `BlockRelations`, `derivation` (a string) | `lesson_document.dart:18, :86`; `content_trust.dart:21` |
| **knowledge / pedagogy** | `Provenance`, `KnowledgeOrigin`, `TeachingProvenance`, `LineageTrace` | `knowledge/provenance.dart:15, :43`; `tutor/teaching_provenance.dart:25`; `knowledge/lineage.dart:59` |

**Nothing joins them.** No `SemanticData`, `LessonBlock` or `LessonDocument` holds a `Provenance`;
no `Concept` or `TeachingMethod` holds a `SourceRef`. Consequence:
`Provenance.citableAsTextbookFact` (`provenance.dart:83`) — the rule that decides whether SAM may
say «sách viết…» — is **undecidable for anything on the Trực quan tab**. §6 of
`02-SEMANTIC-FOUNDATION.md` is the minimal bridge.

### 1.4 Structure carried by `LessonDocument`

| Structure | Status | Where |
|---|---|---|
| table rows/cols | **EXISTS** — the only genuinely structured node | `TableBlock.rows`, `headerRows` (`lesson_document.dart:446`) |
| figure ↔ caption | **PARTIAL** — a block-id reference, not a composition | `ImageBlock.captionBlockId:404` ↔ `BlockRelations.captionOf:104` |
| question stem + options | **MISSING** | `QuestionBlock` is `text` only (`:472`). Options/answers exist only on `LearningActivity` (`tutor/learning_activity.dart:35`), which is **never built from a `LessonDocument`** |
| list items / nesting | **MISSING** | survives only as the boolean `enumeratorRestored` (`:108`) plus the literal bullet left in `text` |
| fraction / exponent / any math | **MISSING BY DESIGN** — math is *withheld*, not modelled (`math_guard`) | — |
| poetry line / stanza, dialogue speaker+utterance | **MISSING** | — |

### 1.5 Rendering

| Thing | Status | Where |
|---|---|---|
| `VisualView` dispatch | **EXISTS AND USED** — data-driven, fail-closed, tabs computed from data | `lib/features/lesson_workspace/visual_view.dart:33, :64, :180, :260` |
| Process renderer | EXISTS AND USED, real data | `visual_view.dart:396` |
| Comparison renderer | EXISTS AND USED, real data | `visual_view.dart:540` |
| Timeline renderer | EXISTS, **synthetic data only** | `views/timeline_view.dart:22` |
| Concept-map renderer | **EXISTS BUT NOT WIRED** — no producer; layout is fixed geometry (`hub at w*0.22`), non-hub relations degrade to text cards (`:691`) | `visual_view.dart:609` |
| `CustomPainter`s | 3 in all of `lib/`, all straight lines | `visual_view.dart:787, :816`; `timeline_view.dart:348` |
| **any image in Trực quan** | **MISSING** | the only two `Image.asset` calls on the tab are mascot PNGs (`visual_view.dart:184, :315`). Round 4's «Trực quan is still text» is **confirmed in code**. |
| `VisualSpec` / pattern selector | **MISSING in `lib/`** | zero hits for `VisualSpec|PatternRouter|VisualPattern` |
| `tool/ui/pattern_router.py` | EXISTS, **gated off** | routes *text* activities only; `WAL-204` result = FAIL, 0 device-valid lessons |
| `drawing_model.dart` | **EXISTS BUT NOT WIRED** | `lib/core/drawing/drawing_model.dart:1` — object model, no renderer, sole reference is its test |
| Activity Pattern registry | **RESEARCH ONLY** | `docs/research/K12-ACTIVITY-PATTERN-REGISTRY.md`; 27 patterns; no code registry exists |

### 1.6 Lane C prior art — audited as candidate primitives, not duplicated

| Thing | Where | Verdict |
|---|---|---|
| `TimelineDate` / `dateEvents` | `lib/core/lesson_model/timeline_date.dart:22, :83` | **REUSE AS-IS.** Fail-closed era/range parsing with a `childLabel`. E1 needs exactly this and does not reimplement it. |
| `prose-dated-events-v1` | `tool/research/lane_c/history_rules.py:286` | **PROMOTED TO CORE.** E1's `e1-prose-dated-events-v1` is the same shape lifted out of History; it reaches the same **7/7** on LS&ĐL 5 Bài 8 while also running on Science. The rule was never a History rule — it is the core TIMELINE rule History happens to exercise. |
| `story-attribution-v1` / `StoryAttribution` | `lib/core/lesson_model/timeline_sources.dart:19, :78` | **KEEP, DOMAIN-SCOPED.** Science pages have no «(Theo …)» lines at all, so this could not have been found on Science. It is a genuine **LIT_TEXT extension**, not core. |
| `TimelineValidator` | `lib/core/lesson_model/timeline_validator.dart:55` | **PROMOTE THE SHAPE.** See §2. |

---

## 2. §10 — KEEP / EVOLVE / ADAPT / DEPRECATE

**Hypothesis under test:** `ProcessSemantic` / `ComparisonSemantic` / `TimelineSemantic` are better
understood as **compiled visual projections** than as canonical knowledge semantics —
`SemanticGraph → compileProcess() → ProcessVisualSpec → ProcessRenderer`.

**Measured, not asserted.** `tool/semantic/visualspec.py` implements six compilers and records at
runtime which graph fields each one read (`compiler_audit()`). Result: **every compiler read only
`nodes`, `relations` and `claims`** — none needed a field existing solely for its own family. A
test fails the build if that stops being true. On the checkpoint pair, PROCESS and TIMELINE were
compiled **from the same graph object**, across two subjects, with no family-specific data model.

> **Verdict: the hypothesis holds at n = 3 lesson-builds.** The four `SemanticData` subtypes are
> *shapes a renderer wants*, not *shapes knowledge has*. They belong on the VISUAL side of
> `SEMANTIC ≠ VISUAL`, which is where the current code does **not** put them.
>
> The strongest single piece of evidence is negative: `ConceptMapSemantic` has existed as a
> canonical semantic type for a whole round and produced **nothing**, because as a *semantic* type
> it has no extraction rule of its own. As a *projection* it is trivial — it is what you get when
> you draw typed relations that a graph already has.

| Artefact | Verdict | Why, and what it becomes |
|---|---|---|
| `ProcessSemantic` | **ADAPT** | Keep the shape, move it behind `compileProcess()`. It is a projection of `Step` + `next`. Its own type stops being the thing extraction targets. |
| `ComparisonSemantic` | **ADAPT + fix the hole first** | Same, but `ComparisonDimension` (`semantic_data.dart:213`) must gain grounding before anything else happens: its `values` are the cells a child reads and they are currently unattributed. Its producer also hardcodes Bài 17's title and dimension (`tsl_to_lesson_document.py:419, :424`) — that is generation, not data, and must move to §3. |
| `TimelineSemantic` | **ADAPT** | Projection of `Event` + `atTime`. The type needs no field added — Lane C already proved that. What must change is the **source** of its data: synthetic today, corpus-derived on the E1 path. |
| `ConceptMapSemantic` | **DEPRECATE as a semantic type; EVOLVE as a projection** | Zero producers for a whole round. Do not build an extractor for it. It should appear only when a lesson's graph already carries ≥2 typed relations over ≥3 entities — and the learning-views research already rejects "a generic mindmap of the lesson". |
| `TimelineValidator` (`timeline-order-v1`) | **KEEP, and generalise the SHAPE** | The one real validator in the repo. Its lesson is not chronology: it is *«a validator exists exactly where the SGK states the fact»*. In the E1 foundation that is `SemanticClaim.status='validated'` requiring a named `validatorId`. Keep the implementation; promote the pattern. |
| `VisualView` dispatch | **KEEP** | Exhaustive switch on data shape, tabs computed from data, fail-closed empty state. This is the right architecture and should be preserved as the VisualSpec consumer. |
| Per-type explanation strings (`visual_view.dart:295-311`) | **DEPRECATE** | Hardcodes Bài 17's story — «Sách viết hoạt động này thành các bước đánh dấu «·» theo thứ tự» — for **every** `ProcessSemantic`, and never reads `s.derivation`. A Process derived by a future rule would be described with the wrong rule's prose. Replace with a rendering of the actual `derivation` + claim status. |
| Concept-map layout (`visual_view.dart:625-689`) | **DEPRECATE** | Fixed geometry, not layout; non-hub relations silently degrade to text cards. |
| `drawing_model.dart` | **KEEP AS RESEARCH** | Dead but tested, and honest about it ("ĐÂY LÀ OBJECT MODEL, KHÔNG PHẢI RENDER ENGINE"). Do not wire it; do not delete it. |
| `SemanticData` base | **EVOLVE** | Must gain claims/grounding (§6). It is the object the whole trust story hangs on and it currently carries none. |
| `khtn6_bai17.dart` + one-row registry | **DEPRECATE as a pattern** | See `04-BAI17-REPLACEMENT.md`. |

---

## 3. The two bridge gaps that block validated structure

Both verified in the checkout:

1. **`ROLE_MAP` has no `formula` key** — `tool/corpus/tsl_to_lesson_document.py:70-81`. A block
   with role `formula` falls through `:210` to `withheld_block(..., ['unknown_role:formula'])`.
   So even a **fully validated** `MathExpression` from Lane A2 has no path from the corpus into a
   `LessonDocument`.
2. **The consumer fails closed on the whole lesson, not the block** — `lesson_document.dart:154` is
   a sealed union with no formula member, and `fromJson`'s `default: return null` (`:343`)
   propagates to `:1018`, where one unparseable block nulls the entire document. So the *first*
   attempt to add a formula block does not degrade — it deletes the lesson.

**Consequence for §10 and §24:** the semantic layer needs a **carrier for validated structured
nodes**, and the bridge is where it is missing. E1's `Formula` primitive (`ontology.py`) is that
carrier on the research side; the AST behind it is Lane A2's (`tool/corpus/mathfix/`) and E1 does
not duplicate it. Note also A2's measurement that **4 validated math restores are blocked by
`empty_block` alone** — the role layer refuses a block for having "no letters" before any math
signal is consulted. Any semantic foundation that assumes the role layer already decided correctly
inherits that; E1's rules therefore read `heading_path`, enumerators and connectives (which
survive role error) rather than trusting `role` alone — with one exception, `_is_procedural`'s
fallback to `role in {instruction, activity}`, which is recorded as a known dependency in
`05-KNOWN-DEFECTS.md`.

---

## 4. §25 — the boundary this lane must not cross

| | Semantic Graph (E1) | Pedagogy Runtime (existing) |
|---|---|---|
| answers | *what knowledge and relationships exist in this lesson* | *what SAM may teach, how, and what counts as evidence* |
| output | claims with support + status + grounding | permitted methods, refusals, evidence verdicts |
| may say «sách viết…» | only via `citableAsTextbookFact`, which it **computes but does not act on** | yes, and it owns that decision |
| fails | open (a missing claim is an absent visual) | **closed** (`resolveBinding` refusal codes, `EvidencePolicy.none`) |

The graph never becomes pedagogy truth. `provenance_of()` deliberately projects **into** the
existing `Provenance` shape and stops there: it hands the pedagogy layer a value in the pedagogy
layer's own vocabulary and lets that layer keep its gates. E1 adds no path by which a `proposed`
claim can reach a learner.
