# SAM Concept ↔ Data Capability Matrix

STATUS: **PROPOSAL research artifact** — extends, does not replace,
`docs/design/06-38-CONCEPT-PRODUCTION-MAP.md` (the existing source of truth
for concept→production ownership, Founder Order 2026-09-02 #3 §19). This
file adds the explicit DATA_CONNECTED/PARTIAL/BACKEND_ONLY/SHELL_ONLY/
MISSING/SUPERSEDED classification the current Master Task Order + Addendum
requires, cross-referenced against `docs/research/
SAM-EDUCATION-DATA-ARCHITECTURE-REVIEW.md` and `docs/research/
BREADTH-DEPTH-UX-MATRIX.md`.

Per Founder instruction: do not re-implement 38 screens, do not invent a
competing source of truth. Where the existing map's Data column (R/RE/B)
and Reuse column already answer the question, this file cites them rather
than re-deriving. Where this session's own device-verified findings
(WAL-190/192/193) or the architecture-review audit add information the
2026-09-02 map didn't have, that's marked **[fresh]**.

Classification definitions:
- **DATA_CONNECTED** — reads/writes real data, wired end-to-end, no known gap.
- **PARTIAL** — real data path exists but is narrower than the concept's
  full scope (enrichment pending, breadth limited, or only reaches a subset
  of lessons).
- **BACKEND_ONLY** — the data model/logic is proven but has no UI consumer,
  or the UI is deliberately deferred pending a design decision.
- **SHELL_ONLY** — UI exists, data is thin/absent/decorative.
- **MISSING** — neither data nor UI exists yet.
- **SUPERSEDED** — the original concept was replaced by a different,
  shipped capability (merge, or a newer pattern superseding it).

---

| # | Concept | Prior verdict/data (06-map) | Classification | Why (this session's evidence, where fresh) |
|---|---|---|---|---|
| 01 | Onboarding | KEEP, R, WAL-95 ✓ | **DATA_CONNECTED** | `LearnerProfile` real, grade≠mastery invariant test-enforced |
| 02 | Learner Profile | MODIFY, R | **DATA_CONNECTED** | — |
| 03 | Subject Setup | MODIFY, R, WAL-136 | **DATA_CONNECTED** | Registry-driven, no hardcoded subject list (confirmed in repo audit) |
| 04 | Timetable | MODIFY, R | **DATA_CONNECTED** | Store-backed; deliberately no lesson field (F4 invariant) |
| 05 | Home | MERGE→home1, R, MissionCenter ✓ | **DATA_CONNECTED** | Reads `NextBestLearningAction`/`LearnerProfile`/`StoriesStore` — confirmed live on Nokia this session (WAL-193 walk) |
| 06 | Subjects | MODIFY, R | **DATA_CONNECTED** | — |
| 07 | Subject Home | KEEP-MODIFY, R | **DATA_CONNECTED** | Most-audited screen this session (WAL-189/191 fixes) |
| 08 | Camera | KEEP, R, WAL-108 ✓ | **DATA_CONNECTED** | Fail-closed perception boundary (WAL-64), verified S24 |
| 09 | Camera Confirm | KEEP, R | **DATA_CONNECTED** | `ConfirmedProblem` is the sole gate into evidence-eligible problems |
| 10 | Tutor Start | MODIFY, R, TutorScreen ✓ | **PARTIAL** [fresh] | Real, but only reaches the **1** lesson `SliceCurriculum` has registered (Toán 5 Bài 6) — architecture-review §0 finding |
| 11 | Diagnostic | REPLACE, R | **PARTIAL** [fresh] | `ErrorHypothesis` module is real and structurally isolated from ground truth, but this audit could not confirm a Surface actually consumes it — needs a follow-up trace, not asserted either way |
| 12 | Problem Workspace | KEEP-MODIFY+, R, TutorSession ✓ | **PARTIAL** | Drawing mode still object-model-only (WAL-116), no render engine — matches prior map's own note |
| 13 | Hint | MODIFY, R | **DATA_CONNECTED** | `interventionId` format `policyId/methodId@level` traces every hint given |
| 14 | Your Turn | KEEP, R | **DATA_CONNECTED** | — |
| 15 | Success | MODIFY, R | **DATA_CONNECTED** | 4-axis feedback (correctness/assistance/evidence/affect), `bannedAbilityPraise` test-enforced |
| 16 | Why This Method | KEEP khung, R, explainTeaching ✓ | **PARTIAL** [fresh] | Strongly proven where reachable (6 red-tests, WAL-114) but reachable only via the SliceCurriculum path — same breadth limit as #10 |
| 17 | Source | REPLACE, RE | **BACKEND_ONLY** [fresh] | **The architecture review's headline finding lands here directly**: the graph-guided retrieval pipeline that should power this screen (`sam-units.db`, WAL-81, benchmarked 0 leaks/0 violations) has no confirmed Dart consumer. This screen is the natural UI destination for the review's proposed "smallest V1" wiring |
| 18 | Review | REPLACE, R, reviewStateOf ✓ | **DATA_CONNECTED** | WAL-184's REVIEW_DUE≠STRUGGLING fix lives exactly here |
| 19 | Learning Map | MODIFY, R | **PARTIAL** [fresh] | Richer 6-level `ConceptClaim` badge only where a `SkillCase` model exists (~1 lesson at audit time); all other lessons show the coarser 3-state `LearningMapState` badge only — both are real, honest, but different depths |
| 20 | Quiz | KEEP-MODIFY, R, WAL-97 ✓ | **DATA_CONNECTED** | — |
| 21 | Assessment | SPLIT, R | **DATA_CONNECTED** | No hint/reveal UI exists in the widget tree at all under assessment mode — structural, not a toggle |
| 22 | Result | MODIFY, R | **DATA_CONNECTED** | — |
| 23 | Vietnamese | KEEP, R, WAL-98 ✓ | **PARTIAL** [fresh] | TV5 (grade 5) is DATA_CONNECTED and Nokia-verified; Ngữ văn (grades 6-12) raw-OCR extraction is **FALSIFIED** this session — same concept, split breadth |
| 24 | Essay | MODIFY+, R, Compose-lite ✓ | **DATA_CONNECTED** | — |
| 25 | Physics | KEEP-MODIFY, RE | **PARTIAL** | Grade 10 confirmed in WAL-190's expanded Experiment breadth this session |
| 26 | Chemistry | KEEP-MODIFY, RE | **PARTIAL** | Same — grade 10 Hoá học confirmed via WAL-190 |
| 27 | History | MODIFY, RE | **PARTIAL** | `SourceReader` real and shipped (WAL-113); enrichment (RE) still open for broader source-asset coverage |
| 28 | Geography | KEEP-MODIFY, RE | **PARTIAL** | `MapReaderScreen` real, uses cropped `SourceAsset`; broader map coverage still enrichment-gated |
| 29 | AI Learning | REPLACE→DEFER, B(design) | **BACKEND_ONLY** | Data model is real and substantial (`AiCurriculum`, 267 QĐ2422 outcomes, ADR-008) — UI is *deliberately* deferred pending a non-generic-chat design, not blocked by missing data |
| 30 | History Sessions | KEEP-MODIFY, R | **DATA_CONNECTED** | Reports `maxSupportIn` honestly per session (no inflated claims) |
| 31 | Progress | REPLACE, R, ConceptSummary ✓ | **DATA_CONNECTED** | — |
| 32 | Parent Home | MODIFY, R, WAL-109 ✓ | **DATA_CONNECTED** | Single recommendation, no dashboard, no mascot in the claim zone (deliberate) |
| 33 | Parent Detail | MODIFY, R, explainConcept ✓ | **DATA_CONNECTED** | — |
| 34 | Multi-child | MODIFY, R | **DATA_CONNECTED** | No sibling ranking — structurally omitted (`ClassConceptState` has no "average" field), not policy-hidden |
| 35 | SAM Voice | MODIFY+, B(WAL-117) | **MISSING** | Blocked on the English-adapter ticket; no code path confirmed in this session's audit |
| 36 | Library | REPLACE, RE | **PARTIAL** [fresh] | `discovery_library_screen.dart` is real and DATA_CONNECTED for what it does (Knowledge Stories browse, WAL-152) — but it delivers the Stories capability, not the originally-conceived 5-zone Library vision. Real and honest, narrower than the concept |
| 37 | Notifications | MODIFY, R | **DATA_CONNECTED** | Not freshly re-verified this session — carried from prior map |
| 38 | Settings | MODIFY, R | **DATA_CONNECTED** | Entry point to Discovery library confirmed this session |

**Tally**: DATA_CONNECTED 24 · PARTIAL 10 · BACKEND_ONLY 2 · MISSING 1 ·
SHELL_ONLY 0 · SUPERSEDED 0 (the one true merge, #05→home1, is tracked as
DATA_CONNECTED under its merged identity, not double-counted).

**No SHELL_ONLY concept was found** — every screen this audit could verify
reads real data, even where narrow. **No fully orphaned concept exists**,
consistent with the prior map's own "38/38 have an owner" finding.

---

## Reading this against the other two matrices

- **Breadth×Depth×UX Matrix** (`docs/research/BREADTH-DEPTH-UX-MATRIX.md`)
  answers "how mature is this *capability*" (Experiment, Reading, Tin học
  Assessment...) — capability-shaped, not screen-shaped.
- **This matrix** answers "where does the child/parent actually meet this
  capability" — screen-shaped, not capability-shaped.
- **Architecture Review** (`docs/research/
  SAM-EDUCATION-DATA-ARCHITECTURE-REVIEW.md`) answers "how does the
  learning OS relate internally" — model-shaped, not product-shaped.

Per addendum §10, these three deliberately stay separate views rather than
collapsing into one artifact. The one finding that shows up identically in
all three is the retrieval-pack wiring gap: BACKEND_ONLY here (#17 Source),
"proven but not connected" in the Breadth×Depth×UX matrix's Discovery row
analog, and the headline finding in the Architecture Review.
