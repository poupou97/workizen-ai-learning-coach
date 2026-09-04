# SAM Education Data Architecture — AS-IS Review

STATUS: **PROPOSAL — NOT AN ARCHITECTURE DECISION.** Review gate: Founder + GPT
approval required before any adoption. Nothing in this document authorizes
implementation.

Founder Master Task Order 2026-09-04 ("Education Data Architecture, Deep
Research Method & UI/UX Connection") + Addendum ("Empirical Baseline First:
AS-IS → Theory → TO-BE → Product Experience"). Per the addendum, this
document reconstructs AS-IS from real evidence *before* comparing to theory —
it does not start from an idealized graph/ontology.

Sources: direct repo audit (179 tool calls across `lib/`, `tool/`, `docs/`,
`poc-out/`) + full read of every architecture-relevant Jira ticket (WAL-2,
WAL-3, WAL-19, WAL-21, WAL-22, WAL-28, WAL-29, WAL-33, WAL-54, WAL-61,
WAL-67, WAL-69, WAL-73, WAL-75, WAL-77, WAL-79, WAL-80, WAL-81, WAL-83,
WAL-84, WAL-85, WAL-89, WAL-91, WAL-92, WAL-108, WAL-113, WAL-114, WAL-118,
WAL-119, WAL-128, WAL-129, WAL-147, WAL-151, WAL-159–161, WAL-168, WAL-172,
WAL-178, WAL-180, WAL-181, WAL-184, WAL-189, WAL-192, WAL-193) + all 10 ADRs
+ every doc under `docs/architecture/`, `docs/design/`, `docs/decisions/`.
Every claim below is traceable to a file:line or a ticket comment quoted at
audit time — nothing here is inferred without a citation.

---

## 0. The headline finding

**Two parallel curriculum architectures currently coexist in production, not
one.** (1) The rich, deeply-modeled path — `Concept`/`SkillCase`/
`CurriculumEdge`/`TutorScope`/`TutorSession` — has exactly **one** lesson
registered (`SliceCurriculum._toan5Bai6`, Toán 5 Bài 6). (2) The lighter
`LessonIndex` + `LearningActivity` + `CandidateEvidence`/`EvidenceValidator`
path is what WAL-190 (Experiment, 113 lessons across 7 grades), WAL-192
(Tin học), and WAL-193 all actually live in, and never touches the Concept/
SkillCase graph at all. **Neither path is wrong** — (2) is precisely why
Breadth grew this session while the graph didn't move — but the TO-BE
proposal (§8) must decide, with evidence, whether and how these converge.

**Second finding, same shape**: the "graph-guided RAG" retrieval doctrine
(WAL-61) — Source → Content → Curriculum Graph → BM25 → Evidence Pack →
Pedagogical Filter → SAM — is fully **built and empirically measured** at
the tool/Python level (WAL-81's benchmark: 8/8 source recall, 0
future-knowledge leaks, 0 method-permission violations, and critically a
**no-filter control on the identical index showed leak=5,
violation=2** — proving the pedagogical filter is load-bearing, not
decorative). But `sam-units.db` (the content pack this produces) has **no
confirmed Dart consumer anywhere in `lib/`**. Only `sam-stories.db`
(Discovery/trivia, WAL-151) is actually wired into the running app. This is
the concrete "backend proven, invisible to child" case the Founder's
principle warns against — found in the architecture itself, not just in one
UI screen (contrast WAL-193, which was a UI-level instance of the same
failure mode).

---

## 1. AS-IS: the proven chain, stage by stage

Per the addendum's requested decomposition (not forced where evidence
disagrees — noted where it splits into two paths).

| Stage | What exists (file:line) | Status |
|---|---|---|
| **SOURCE** | `tool/corpus/content_node.py` `ContentNode` (role ∈ BOOK/UNIT/THEME/WEEK/CHAPTER/TOPIC/LESSON/ACTIVITY) — explicitly "SOURCE STRUCTURE ≠ PEDAGOGY." 531/531 books OCR'd, 62,729 pages. | PROVEN, structural only |
| **STRUCTURE** | `poc-out/graph/curriculum-structure.json`, 7,626 lessons via `tool/corpus/toc_health.py` flags. WAL-172 fixed a 2-column TOC merge bug: usable TOCs 122/531→184/531. | PROVEN, ~34% of books clean |
| **KNOWLEDGE (deep)** | `Concept`/`SkillCase`/`CurriculumEdge` (`lib/core/curriculum/`) — real types, real invariants (WAL-54, WAL-91), but `SliceCurriculum` has **1** registered lesson; `crossgrade-graph.json` has 14 concept-nodes; hand-vetted `prerequisiteEdges` has **1** entry total. | PROVEN model, ~1% corpus coverage (Toán 4-5 + TV5 only) |
| **KNOWLEDGE (structural/generic)** | `tool/ingest/extract_units_generic.py` — 126,552 generic-GDPT2018 units, 306 books, 70% lesson-attached. Not concept/case-typed. | PROVEN extraction, not semantically deep |
| **PEDAGOGY** | `PedagogicalIntent` (8 values), `TeachingAct` (15 values, WAL-67, literature-cross-referenced), `AssistancePolicy` (4 modes), `LearningExperienceBlueprint` (8 instances, 5 subject families, all source-cited, WAL-128/129). | PROVEN, narrow catalogue |
| **ACTIVITY/EXPERIENCE** | `LearningActivity`/`resolveSurface` (ADR-009, one resolver) OR `PlannedAct{act, methodId}` (pedagogy layer, first wired WAL-178 into Experiment only). | PROVEN, two co-existing shapes |
| **SAM/TOOL/SURFACE** | 21 screens under `lib/features/` (§ full table in the repo audit) — each reads real data, most emit no evidence (browse), 8 emit via one of two evidence patterns (§3). | PROVEN, per-screen |
| **LEARNER ACTION** | `PerceptionHypothesis`→`ConfirmedProblem` (camera path, WAL-64) or direct text/tap response (Reader/Compose/Quiz). | PROVEN, fail-closed on camera |
| **CANDIDATE EVIDENCE** | `CandidateEvidence` (`evidence_validator.dart`) — "một CLAIM, không phải một sự thật," explicit in doc-comment. | PROVEN for 4/many screens |
| **EVIDENCE VALIDATION** | `validateCandidateEvidence()` — single fail-closed gate, `null` on `lookup` intent or empty response. | PROVEN, narrow adoption (see §3 gap) |
| **LEARNER STATE** | BKT (`mastery.dart`, ADR-001) → `ConceptSummary` 3-axis (mastery≠coverage≠confidence, ADR-004, supersedes ADR-001's min/mean). | PROVEN, well-tested (48+ tests) |
| **ADAPTATION/NEXT ACTION** | `ReviewUrgency` (SM-2/FSRS/Leitner-family, ADR-005), `ChallengeSignal` (hysteresis, WAL-183), `resolveReviewCandidates` (6-rule cascade, WAL-164/184). | PROVEN, un-tuned constants (explicitly flagged) |
| **PRODUCT EXPERIENCE** | Home/Bookshelf/LearningMap/Parent screens read the above. WAL-193 found a real gap: build-time content verification ≠ product-experience validity. | PARTIAL — see WAL-193 case |

---

## 2. Four gold-reference cases (addendum §3)

Each scored on **three independent dimensions**, never collapsed (addendum §4):
**Epistemic status** (PROVEN/PARTIAL/HYPOTHESIS/FALSIFIED/MISSING) ×
**Capability maturity** (DATA_ONLY/BACKEND_ONLY/SURFACE_EXISTS/CONNECTED/
PRODUCT_VALIDATED) × **Decision** (SCALE/IMPLEMENT/RESEARCH_MORE/DEFER/STOP).

### Case A — WAL-190 (Experiment)
```
SGK "Chuẩn bị/Tiến hành" typography (source, self-encodes pedagogy)
  → deterministic regex recognition (tool/ui/build_lesson_index.py)
  → LessonIndex.khoaExperiments entry
  → ExperimentScreen (PlannedAct-driven, PREDICT gate)
  → learner records prediction, then observation
  → CandidateEvidence → validateCandidateEvidence → LearningEvent
  → EvidenceLog → replayMastery (BKT) → ConceptSummary
  → ChallengeSignal / ReviewUrgency → Home/LearningMap
```
**Epistemic: PROVEN** (gold-set validated, 2 residual quality gaps known and
named, not hidden). **Maturity: PRODUCT_VALIDATED** (shipped, tested,
partially Nokia-verified). **Decision: SCALE** (this pattern generalized
cleanly from 2→7 grades in one bounded pass because the pedagogy was already
encoded in source typography — no free-form inference needed). This is the
**gold reference** for what "connected learning capability" looks like
end-to-end.

### Case B — Ngữ văn (raw-OCR falsification)
```
Raw OCR text -X→ Trusted Reading Passage   [FALSIFIED]
```
Missing capability, explicitly named rather than patched around:
```
PDF Layout (not yet extracted)
  → Content Region (main text / sidebar / footnote — column-aware)
  → trusted semantic extraction
```
**Epistemic: FALSIFIED** (specific scope: raw-OCR-line-only extraction for
Ngữ văn passage isolation — not "Ngữ văn is impossible"). **Maturity:
DATA_ONLY** (a POC tool exists, deliberately not wired to production, kept
as a documented negative result). **Decision: STOP** (per Founder's own
rule: "if it requires accumulating many per-book heuristics → STOP" — the
sidebar-box-content problem has no natural stopping point with line-level
OCR). Layout-aware extraction remains a real, un-started future capability.

### Case C — WAL-192 (Source-Grounded Assessment, Tin học)
```
SGK Question (no in-body pedagogical-role header — verified absent)
  + Pedagogical Role (recoverable ONLY from SGV structure)
  + SGV Answer (format varies by grade — 4/10 grades share one clean format)
  → deterministic SGK↔SGV linkage (page-range keyed by PRINTED "Bài N",
    not the internal lesson counter, which was found to drift between
    documents)
  → Source-Grounded Assessment [NOT YET WIRED — no Surface built]
```
**Epistemic: PROVEN, narrowly** (2/9 candidate lessons HIGH_CONFIDENCE, 0/2
false trusted answers on deep spot-check — genuinely safe when it fires).
**Maturity: BACKEND_ONLY** (no Surface, no Evidence Validator wiring — the
existing `ReaderScreen` MCQ mode could host it but hasn't been connected).
**Decision: DEFER** (yield too small — 2 lessons — to justify the
engineering cost right now; the blockers are specific and bounded, unlike
Case B). **This is the explicit proof that PROVEN ≠ SCALE and PROVEN ≠ BUILD
NOW** — architecture truth, capability maturity, and product priority are
three different questions with three different answers for the same case.

### Case D — WAL-193 (Product Experience defect)
```
SGK source sentence (VERIFIED, correct)
  → build-time story-title generator (deterministic, passes §28 gate)
  → Home "Bạn có biết?" card
  → BACKEND PROVEN + UI EXISTS ≠ PRODUCT EXPERIENCE VALID
```
A PERSON-type title lacking birth-years rendered as bare phonetic
syllables ("Hen Krit-chừn Gioa-chim G-ram") — meaningless to a child despite
passing every upstream gate. **Epistemic: the underlying fact was PROVEN
(correct, sourced) the whole time** — the defect was never in truth-value,
it was in **whether truth was legible to its actual audience**.
**Maturity: was SURFACE_EXISTS, is now PRODUCT_VALIDATED** (found and fixed
by walking the real device, not by auditing the pipeline; Nokia-verified
before/after). **Decision: IMPLEMENT** (shipped same session, WAL-193). The
generalizable lesson: **content-verification gates test truth, not
legibility** — a distinct QA dimension not currently checked anywhere else
in the pipeline. Worth a systemic look (§9), not just this one instance.

---

## 3. A structural gap this audit found, not previously ticketed

**Two parallel evidence-minting patterns exist**, per `evidence_validator.dart`'s
own doc-comment (quoted): Reader/Compose/SourceReader/Experiment go through
`CandidateEvidence`→`validateCandidateEvidence()` (one shared fail-closed
gate); `TutorSession`/`QuizSelect` (the Toán/quiz flows — ironically the
*original*, most deeply-modeled path) mint `LearningEvent`s directly with
their own inline lookup-guards, never touching the shared validator. This
was a deliberate, documented decision at WAL-178 time ("Reader/Compose có
nhiều EvidenceKind... khác hẳn mô hình một-phát-luôn-null của Science" — not
an oversight) but it means **the fail-closed evidence gate is not actually
universal** — a future contributor adding a new evidence-emitting screen has
two patterns to choose from, with no single guard preventing a third,
inconsistent one. Flagged here as a real architecture-hygiene question for
the TO-BE proposal, not asserted as a bug.

---

## 4. Negative Knowledge Registry (preserved, not deleted)

Per addendum §5 — falsifications are cumulative architecture results, kept
permanently:

| Relationship | Status | Source |
|---|---|---|
| Raw OCR text → Trusted Ngữ văn Passage | **FALSIFIED** | This session, Ngữ văn gold-set |
| A/B/C/D shape → Automatically Gradable Question | **FALSIFIED** | WAL-192 ("Hoạt động 1" discussion prompt looked identical to a real MCQ; SGV disagreed) |
| Browsable Lesson → Learnable Lesson | **FALSIFIED** | C-013: Browsable moved 843→3,679, Learnable moved by exactly 0 |
| Trace → LearningEvidence | **FALSIFIED (by design)** | `LearningIntent.lookup` must never mint evidence — WAL-175/178/189 |
| Activity Exists (JSON non-null) → Valid Evidence | **FALSIFIED** | Explicit Founder warning, WAL-192's "Hoạt động 1" case is the concrete instance |
| ONE Learning OS + current AgePolicy → supports K-12 pedagogy | **FALSIFIED** | `WalBandDensity` audit: 4 cosmetic fields only, grades 1-2 and 3-5 literally identical |
| WAL-188 learner-switcher bug | **FALSIFIED** (self-correction) | Coordinate-measurement error in manual testing, not a product bug — kept as the evidence-discipline standard |
| Separate AI-domain graph (Option A, WAL-91) | **FALSIFIED** | "Hạ tầng đôi không mua được gì" — QĐ2422 structure is isomorphic to existing concept→SkillCase→LearningStage |
| Pure overlay, no first-class AI nodes (Option C, WAL-91) | **FALSIFIED** | Can't contain 267 codes of an independent progression |
| Method↔Case conjunctive (AND-gate) combination as universal rule | **FALSIFIED** | WAL-54: 3 corpus counter-examples; downgraded to per-map assumption |
| Concept↔SkillCase cardinality (1:1 vs M:N) | **INSUFFICIENT EVIDENCE** — neither confirmed nor denied | WAL-54 |
| ECD deliberate implementation (vs organic convergence) | **OPEN QUESTION**, not resolved either way | This session's theory-comparison research |

---

## 5. Theory comparison — AS-IS first, then classify

Per addendum §6: the question is "what problem in CURRENT SAM does theory X
solve better," not "how would SAM adopt X." Classification per addendum §7:
RETAIN / FORMALIZE / EXTEND / REPLACE / REJECT / HYPOTHESIS.

| Theory | Problem it solves | SAM's current equivalent | Classification | Why |
|---|---|---|---|---|
| **Bayesian Knowledge Tracing** | Real-time P(mastery) from a response sequence | `bktPosterior()`, ADR-001, `SkillCase`-level | **RETAIN** | Already the adopted, tested, cited model. pyBKT's `Model`/`Roster` split (batch-fit vs. live per-student state) is a clean pattern SAM's `mastery.dart` already approximates informally — worth a naming/structure pass, not a replacement. |
| **Evidence-Centered Design** | Auditable claim→evidence→task inference chain | `CandidateEvidence`/`EvidenceValidator`, ADR-004's `ConceptClaim` | **FORMALIZE** | SAM's own code already uses "claim"/"evidence"/"student model" vocabulary, but the research agent found it used in an **inverted sense** vs. ECD's technical meaning, with no explicit citation anywhere. Worth an explicit decision: cite ECD deliberately and align vocabulary, or explicitly document the divergence so it isn't mistaken for a spec implementation later. Not a structural change either way — SAM's actual claim→evidence→task-model shape is sound. |
| **Knowledge Space Theory** (fringes, surmise relation) | "What should this learner do next" as a structural, not scalar, computation | `ReviewUrgency` + `ChallengeSignal` (both scalar/threshold-based, not structural) | **HYPOTHESIS** | Nothing in SAM currently computes an outer fringe. The `vanderbilt-data-science/knowledge-spaces` schema (real, inspected, MIT-licensed) is close to a ready-made target — but SAM's own prerequisite data is far too thin to test this against (**1** hand-vetted `prerequisite`-kind `CurriculumEdge` in the entire repo). Classify as HYPOTHESIS, not EXTEND: there isn't enough real prerequisite data yet to know if KST would even change SAM's recommendations, let alone whether it's worth the complexity. |
| **Competence-Based KST** | Explains *why* prerequisites exist via a latent competence layer | `SkillCase` under `Concept` (a real 2-level split, but undocumented as a competence/performance duality) | **FORMALIZE, weakly** | The `SkillCase` split (e.g. `quy-dong` → chia-hết / không-chia-hết cases) is structurally a competence-layer idea already, discovered empirically from corpus evidence exactly as CbKST prescribes — worth naming this correspondence explicitly, not restructuring code to match academic terminology (addendum §7 explicit warning). |
| **Knowledge Components / Q-matrix** | Treats "what counts as a unit of knowledge" as an empirical, fittable hypothesis, not an a priori taxonomy | `ExerciseSkillMap`/Q-matrix (WAL-79, ADR-005) — **already exists, already empirical** | **RETAIN** | SAM's Q-matrix is conjunctive with an `attributionUnresolved` escape valve — already close to the DataShop/KLI framing. The one gap: SAM has never authored *competing* KC models for the same exercise set to compare fit (DataShop's core practice) — not needed at current data volume. |
| **Prerequisite discovery from data (COMMAND, causal methods)** | Validates/discovers prerequisite edges from real student performance logs, rather than hand-authoring | Manual corpus reading only — **1** hand-vetted edge in the whole repo | **HYPOTHESIS, blocked on volume** | SAM does not yet have enough real student attempt logs to run any of these techniques meaningfully. Correctly out of scope until Breadth (more Learnable lessons, more real usage) produces the data these methods need. |
| **Educational Knowledge Graphs (general)** | Represents curriculum connectivity queryably | `CurriculumEdge`/`EdgeKind` (4 kinds) | **RETAIN, narrow** | No canonical ontology exists in the field either (confirmed by research) — SAM's small, typed, evidence-gated edge set is defensible as-is. MOOCCubeX's empirical prerequisite-edge definition ("if A helps understanding B") is a useful *test*, not a schema to adopt. |
| **1EdTech CASE** | Standardized, resolvable cross-system competency exchange | Nothing — SAM has no need to exchange curriculum data with external systems today | **REJECT (for now)** | CASE is graph-shaped (confirmed by inspecting the real schema) with typed associations, closest fit `precedes` for sequencing — genuinely well-designed, but it solves an interoperability problem SAM doesn't have. Revisit only if/when SAM needs to import/export standards data across systems. |
| **Vanderbilt Knowledge Spaces (repo)** | Reference schema unifying KST fringes + CbKST + Bloom/DOK/SOLO | Nothing unified — SAM's cognitive-level tagging is scattered (`PedagogicalIntent`, `ObjectiveKind`) | **HYPOTHESIS** | Small (22 stars), young (~7 months), not battle-tested — a reference implementation, not infrastructure to depend on. Worth reading as a design sketch when/if KST work is greenlit; not worth integrating as a dependency. |
| **Learning Commons Knowledge Graph** | Pre-built, licensed standards+curriculum data at national scale | N/A — SAM is Vietnam-specific, this dataset is US-standards-specific | **REJECT** | Wrong domain entirely. The one transferable *pattern* — typed alignment edges carrying their own sub-properties (`alignmentType: "teaches"`) instead of a proliferating edge-label enum — is **already how SAM's `ExposureRole` works**, independently arrived at. Noted as validation, not adoption. |

**Cross-cutting theory finding**: SAM's architecture converges with several
of these theories' vocabulary *organically*, through corpus-driven,
falsification-tested iteration — not through deliberate academic adoption.
This is evidence the underlying design instincts (evidence-gated claims,
typed provenance, fail-closed defaults) are sound independent of theory, but
it also means some naming (`CandidateEvidence`'s "claim") may mislead a
future reader who assumes ECD-spec intent. Recommendation in §8.

---

## 6. Real query walkthroughs (addendum §12)

**Query 1 — "What is this child learning right now?"**
`LearnerProfile` (grade, no mastery — WAL-95 invariant) + `LearningContext`
(learner/grade/subject?/sourceDocumentId?/lessonNo?/intent?, WAL-182) →
`LessonIndex.loadForGrade` OR `SliceCurriculum.curriculumForLesson`
(whichever of the two parallel paths, §0/§3). **Answerable today**, but the
answer's *richness* depends entirely on which path — Toán 5 Bài 6 gets full
Concept/SkillCase context; everything else gets `LearningActivity`-level
context only.

**Query 2 — "What is this child allowed/expected to learn here?"**
`TutorScope`/`eligibilityForProblem` = `APPLICABLE_TO_PROBLEM ∩
PEDAGOGICALLY_ALLOWED` (`pedagogical_boundary.dart`) — fail-closed, tested
(BCNN blocked at grade 5 despite being mathematically valid). **Answerable,
PROVEN, but only reachable via the SliceCurriculum path** (1 lesson).
Outside that path, "allowed" is implicit in which `LearningActivity` exists
for the lesson, not an explicit permission query.

**Query 3 — "What should SAM do now?"**
`PlannedAct{act: TeachingAct, methodId?}` — 15-value act taxonomy,
literature-cross-referenced (WAL-67). **Answerable, PROVEN, narrowly wired**
(Experiment only, per WAL-178's own comment noting 0 callers before that
ticket). Does not delegate to unrestricted LLM reasoning anywhere in this
path — confirmed by grep, no LLM call sits between context and act.

**Query 4 — "Why is the child wrong?"**
`LearnerAction` → `CandidateEvidence` → `EvidenceValidator` → `LearningEvent`
(`correct: null` always at mint time — validator never grades) →
`ErrorHypothesis` (`careless`/`procedural`/`conceptual`, WAL-27) —
structurally guaranteed not to leak into ground truth ("module không
nhận/trả CaseMastery ghi được"). **Answerable, PROVEN**, but
`ErrorHypothesis` is a separate, thin module — not yet visibly consumed by
any Surface found in this audit (a candidate gap, not confirmed either way
without further tracing).

**Query 5 — "What should the child learn next?"**
BKT (`ConceptSummary.claim`) + `ReviewUrgency` (SM-2-family) +
`ChallengeSignal` (hysteresis) → `resolveReviewCandidates` (6-rule cascade)
→ Home/LearningMap. **Answerable, PROVEN, well-tested** (WAL-184's own
fix is visible in the exact lines the audit cites) — but this is entirely
threshold/heuristic-based, not a structural Knowledge-Frontier computation.
Whether KST's outer fringe would answer this *better* is unproven (§5) —
current data volume (1 prerequisite edge) cannot support the comparison yet.

**Query 6 — "Why is SAM teaching this?"**
`PlannedAct` → `explainTeaching()` (sole mint point for `TeachingProvenance`)
→ `sourceLineForChildOf(Provenance)` (sole render function, exact 3-way
wording rule enforced by a `CITATION_FABRICATION` guard that blocks an LLM
from inventing "SGK trang N" citations, WAL-114). **Answerable, PROVEN,
strongly guarded** — one of the most rigorously fail-closed paths in the
whole codebase (6 dedicated red-tests, WAL-114).

**Query 7 — "What should the parent know?"**
`LearningEvent`s → `ConceptSummary` → `explainConcept()` (deterministic, one
branch per `ConceptClaim`, `EvidenceCitation` per claim) → `ParentTonight`/
`FamilyManager`. Explicitly reuses `learningMapStateFor` rather than a
separate parent-facing computation ("ONE EVIDENCE TRUTH, MULTIPLE
PROJECTIONS," WAL-180) — though WAL-184 found this projection-sharing
principle had one real gap (Home review card vs. lesson-detail mastery
saying contradictory things about the same SkillCase in the same session).
**Answerable, PROVEN**, coverage≠mastery is structurally enforced
(`ConceptClaim.mastered` requires full coverage, not just high pMastery —
ADR-004 Decision 1). No sibling ranking anywhere (`ClassConceptState` has no
"class average" field by omission, WAL-105).

**Cross-cutting**: all 7 queries are answerable *somewhere* in the current
architecture. The variance is in *which path* answers them (rich
SliceCurriculum path vs. lighter LessonIndex path) and *how much of the
corpus* that path reaches (1 lesson vs. 3,679 lessons-on-shelf vs. 113
Learnable). No query requires unrestricted LLM reasoning to answer — every
one of these traces to deterministic code with test coverage.

---

## 7. Retrieval architecture — as-is, and the wiring gap

WAL-61's doctrine, confirmed **built and measured**, not just designed:
```
LearningContext
  → Curriculum/Knowledge boundary (LearningStage.visible() scope rule)
  → BM25/FTS5 (sam-units.db, SQLite FTS5, no vector search anywhere —
    "chưa có failure nào vector giải," repeated across WAL-61/81/83/92)
  → exact SGK/SGV passage + provenance
  → Pedagogical Filter (proven load-bearing: leak=0/violation=0 WITH
    filter vs. leak=5/violation=2 on a no-filter control, same index)
  → PlannedAct → SAM
```
**Graph decides WHERE** (scope), **BM25 decides WHAT** (within scope) — the
doctrine's own framing, empirically validated, not aspirational.

**The gap**: `sam-units.db` (this pack) has no confirmed Dart consumer.
`KnowledgeContentProvider` (the abstract interface meant to wire this in,
`lib/core/knowledge/knowledge_content_provider.dart`) has zero
implementations found. The production app's actual retrieval path today is
`SliceCurriculum`'s hand-registered 1-lesson lookup table — not a query
through this proven pipeline. **RETRIEVED ≠ PERMITTED is proven at the tool
level; it has never been asked to prove itself against a real Dart runtime
query.**

---

## 8. Counterarguments — Claude must challenge its own read

**Is graph actually useful here, or is this architecture theater?**
The *evidence* says: a typed, small, provenance-gated edge model
(`CurriculumEdge`, 4 kinds) has been useful exactly where it's been applied
(WAL-91's `aiIntegration` edge kind structurally enforces "no edge = no
integration" — a real invariant a flat list couldn't enforce as cheaply).
But the graph is currently **~1% deep** relative to corpus size, and one of
its two production consumers (`SliceCurriculum`) reaches one lesson. Calling
the *current* graph "architecture" is defensible; calling it a *load-bearing
part of the product* today would be an overclaim — its load-bearing proof
(WAL-81's benchmark) lives in a POC never wired to the app.

**Should graph be a generated view rather than a source of truth?**
Current reality already answers this: `CurriculumEdge` entries ARE the
source of truth (hand-authored/extracted with provenance), and
`crossgrade-graph.json`/pack FTS indexes are *generated* from them. This
matches the addendum's preferred hypothesis (§9: typed registry → generated
graph views) — but only because that's already what exists, not because
this review is recommending it fresh. Worth stating plainly: **SAM already
made this choice, correctly, years before this research order existed.**

**Are Concept/SkillCase/Method the right abstractions?**
WAL-54's own falsification says: partially unproven. Method↔Case is M:N for
applicability (proven, 3 counter-examples) but 1:1 for taught-for semantics;
Concept↔Case cardinality is **explicitly unresolved** ("INSUFFICIENT
EVIDENCE," not confirmed or denied) — a real open hypothesis, honestly
carried for over 30 tickets without being forced to a premature answer. This
review does not resolve it either; more corpus depth is needed first.

**Does KST fit Vietnam K-12, or does it conflict with current BKT/mastery?**
No conflict found — they answer different questions (BKT: P(mastery) of one
skill from a response sequence; KST: which *combination* of skills is
structurally reachable next). They could compose. But SAM's prerequisite
data (1 edge) is far too thin to test whether KST's fringe computation would
change any real recommendation SAM currently makes. Classified HYPOTHESIS,
not EXTEND, specifically because "we don't have enough data to know" is a
different, more honest answer than either RETAIN or REPLACE would claim.

**Does CASE add useful semantics, or unnecessary complexity?**
For SAM's current, single-country, single-app scope: complexity, not
semantics — CASE exists to solve cross-system exchange, which SAM doesn't
need yet. REJECT stands, but flag for revisit if a Confluence/multi-product
integration need appears (the workspace's own `workizen-knowledge-base` may
eventually want this).

**What belongs in graph vs. relational/JSON/BM25?**
AS-IS already answers this empirically: curriculum *relationships* → typed
edges (small, provenance-gated); curriculum *content* → JSON/JSONL +
FTS5 (not a graph database); learner *evidence* → append-only event log,
never a graph. No case was found in this audit where a relational/JSON
structure was straining against graph semantics it actually needed.

**How do we prevent stale data? How does curriculum versioning work?**
`knowledgeVersion` is baked into `LearningEvent` at write time (ADR-006's
local-first "build once, distribute, retrieve locally" model +
`pack_delta.py`'s proven replay-safety: WAL-85 showed replaying old events
through an UPDATED pack, even one that DELETED units, reproduces identical
results). This is a genuinely strong answer, already proven — not a gap.

**Can inferred prerequisites become dangerous?**
The one real prerequisite edge in the repo is `sourceStated` (SGK
Toán 5 tập hai p.54) — hand-vetted, not inferred. `sourceSequence` edges
(table-of-contents order) are explicitly typed differently and **cannot** be
cited as a dependency (`citableAsDependency` requires `sourceStated`
specifically) — "mục lục không phải lời sách" is enforced by type, not
convention. No `llmInferred` prerequisite edge exists anywhere. This is a
real, working safety boundary — worth preserving exactly as-is in any TO-BE.

**Can this scale without creating 50k+ meaningless nodes?**
Not tested — current graph is far below that scale (14 concept-nodes). The
real risk this audit found is the opposite direction: the graph may be
**too small to be useful**, not at risk of runaway proliferation. If Breadth
work (WAL-190-style extractors) continues generating `LessonIndex` entries
without also feeding the Concept/SkillCase graph, the gap between "lessons
on shelf" and "lessons the deep model understands" will keep widening, not
narrowing — worth naming as a trend, not just a snapshot.

**Does the architecture actually improve learner experience?**
Where it's connected (Experiment, Case A) — yes, provably (WAL-190's
measured Learnable delta, plus Nokia device verification). Where it's built
but not connected (retrieval pack, Case at §7; deep curriculum graph beyond
1 lesson) — no product effect yet, by definition. The architecture's value
is real but currently concentrated in a small, specific slice.

---

## 9. Open hypotheses (unproven, carried forward honestly)

1. Would KST's outer-fringe computation change any real "what's next"
   recommendation SAM currently makes? — Blocked on prerequisite-data volume.
2. Is `CandidateEvidence`'s "claim" vocabulary a deliberate ECD echo or
   organic convergence? — Genuinely unresolved from code alone.
3. Should the two evidence-minting patterns (§3) converge, or is the
   split correct because Toán/Quiz genuinely have different shape needs?
4. Does content-verification (WAL-193's §28 gate) need a second,
   independent "legibility" check, or was this a one-off?
5. Should the SliceCurriculum (deep) and LessonIndex (broad) paths
   converge, extend independently, or stay deliberately separate?

---

## 10. Risks

- **Wiring debt**: a fully-proven retrieval pipeline (§7) sitting unused is
  a maintenance/understanding risk — future contributors may not know it
  exists, or may build a second, worse version not realizing one is proven.
- **Graph shallowness**: 1% corpus coverage means most "Learnable" lessons
  (WAL-190-style) currently bypass the deep model entirely — any TO-BE
  decision that assumes graph-backed reasoning for all content would be
  building on evidence that doesn't exist yet for 99% of the corpus.
- **Two evidence patterns**: real but currently contained (§3) — risk grows
  only if a third pattern is added without resolving which is canonical.
- **Legibility gate gap**: WAL-193's class of bug (true content, illegible
  presentation) has no dedicated automated check anywhere in the pipeline —
  only found by manually walking the device.

---

## 11. Smallest V1 (if Founder approves any action from this review)

Not a recommendation to build — a statement of what the *smallest* next
step would be if evidence-based prioritization were applied: **wire
`sam-units.db` into one real Dart query path** (even for the single
`SliceCurriculum`-registered lesson, as a proof the proven pipeline reaches
the app at all), rather than starting any new theoretical work (KST,
CASE, etc.) — because it converts an already-proven, already-measured
capability from BACKEND_ONLY to CONNECTED at near-zero new research cost,
which is a stronger Breadth×Depth×UX move than any of the HYPOTHESIS-tier
theory items in §5.

---

## 12. Jira TODO status

See `WAL-195` (epic) for the full backlog. This document satisfies the
"[ARCH] Reverse-engineer AS-IS" and "[ARCH] Reconstruct WAL-190/Ngữ văn/
WAL-192/WAL-193 cases" child-issue requirements, plus the theory-comparison
requirement (§5) and falsification registry (§4). Remaining backlog items
(TO-BE proposal validation, concept-matrix, visual review, Founder review
gate) are tracked separately — see `docs/architecture/
SAM-EDUCATION-DATA-ARCHITECTURE-PROPOSAL.md` and
`docs/design/SAM-CONCEPT-DATA-CAPABILITY-MATRIX.md`.
