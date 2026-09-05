# Round-4 runtime contracts — lane A-runtime (PROVE) · 2026-09-05

**Status of every item: PROPOSED.** Nothing here is doctrine and nothing is "Founder-approved";
each item is the smallest mechanism that makes one Founder order (§4 STRICT EVIDENCE, §5
PEDAGOGY RUNTIME) *provable by a test*, on the golden slice **KHTN 6 (KNTT) Bài 17** and the
existing Toán 5 Deep path. Base branch: `integration/round4-2026-09-05` (= main @ 61dbfdb + plan).

Companions: `ROUND3-RUNTIME-CONTRACTS.md` (A3–A8, still valid unless superseded below),
`B-LANE-CONTRACTS-2026-09-05.md`, `EVIDENCE-DURABILITY-AND-INTEGRITY-OPTIONS.md`.

## 0. What changed in one paragraph

Strict validation is now the **default** read rule for every competence claim: mastery/BKT,
`LearningMapState.independentEvidence`, the parent line, `StudentLessonState` and Next Action
consume only events that carry a **registered, competence-granting validator stamp**
(`fraction-check-v1`). Graded events without a stamp — pre-contract history and the two
unstamped emitters that remain in Lane B files — are classified **read-side** as
`historicalUnvalidated`: they stay in the log verbatim, appear in history with the label
«ghi nhận trước hợp đồng mới», and are never «Tự làm được». **No data migration, no rewrite, no
deletion.** Camera lineage stays `null/null` unless an explicit `LearningContext` resolves a
lesson (now also enforced at the candidate-evidence gate). The pedagogy runtime gained one real,
deterministic capability (verbatim «…» quote verification against the lesson's own blocks); on
the real Bài 17 script it changes **0** of 17 steps — measured, not set. **No validator was
registered** for Bài 17 (none of its questions has an SGK-stated answer set).

## 1. Contract table

| # | Contract | Where | Definition | Held by |
|---|---|---|---|---|
| R4.1 | **`EvidenceReadClass`** — read-side classification, one class per event | `lib/core/student/learning_evidence.dart` → `LearningEvent.readClass` | `validatedCompetence` (correct ≠ null ∧ stamp registered ∧ grantsCompetence) · `participation` (kind participation, or legacy independentAttempt + correct null, incl. `candidate-gate-v1`) · `historicalUnvalidated` (correct ≠ null ∧ validation == null) · `rejectedValidation` (stamp present, not registered / not competence) · `unscored` (hint events). `historyLabel` per class; `historicalUnvalidatedLabel = 'ghi nhận trước hợp đồng mới'`. Not persisted — the JSON codec is unchanged. | `validated_evidence_doctrine_test` §5, `learning_map_state_test` (ROUND 4 group) |
| R4.2 | **`isValidatedIndependentSuccess` is strict** | same file | = (independentAttempt ∨ selfCorrection) ∧ correct == true ∧ `hasApprovedValidation`. `isLegacyUnstampedSuccess` = same shape ∧ validation == null — for the explicit legacy read only. | doctrine test §5, `self_report_doctrine_test` §3 |
| R4.3 | **Map state default = strict** | `learningMapStateFor(requireValidation: true)` | Unstamped graded history ⇒ 🟢 `engaged` (never 🔵). `requireValidation: false` = explicit legacy read (#63) — audit/compare only; no screen may pass it. The four `LearningMapState` values are unchanged (Lane B switch statements compile as before). | `learning_map_state_test`, doctrine test §3 |
| R4.4 | **BKT default = `ValidatedOnlyBktPolicy`** | `replayMastery(policy: defaultEvidencePolicy)`, `defaultEvidencePolicy` const | Unstamped graded events ⇒ `noOp` (no belief move, no evidenceCount). `ConservativeBktPolicy` keeps **both its id and its legacy behaviour** (`conservative-bkt-v1`) — changing behaviour under the same policyId would be REPLAY SILENTLY REINTERPRET; it is now the explicit legacy/audit policy, never a screen default. `masteryFromStore` (Lane B) inherits the strict default with no code change. | `evidence_replay_test` (ROUND 4 test), doctrine test §3, `evidence_integrity_test` (old on-disk line) |
| R4.5 | **`StudentLessonState` counts + standing** | `lib/core/student/student_lesson_state.dart` | `participationCount`, `historicalUnvalidatedCount`, `validatedSuccessCount`; `standing ∈ {none, participatedUnverified, validated}` (`LessonEvidenceStanding`); `evidenceNote` = one honest sentence for the three unverified cases (participation / historical / engaged) or `null`. Same lineage filter as Map/Parent. | `lesson_next_action_test` |
| R4.6 | **Parent line for historical data** | `RecentLessonTouch.hasHistoricalUnvalidated`, `parentLineFor` | engaged + historical ⇒ `'Con đã học <Bài N> — có lần làm được ghi nhận trước hợp đồng mới; SAM chưa kiểm lại nên chưa tính là tự làm được.'` — never starts with «Con đã tự làm được»; plain engaged ⇒ `'… chưa có lần nào tự làm được được kiểm ghi lại.'` | `parent_session_summary_test`, doctrine test §4 |
| R4.7 | **Next Action under strict state** | `nextBestLessonAction` / `NextBestLearningAction.forLesson` | R0–R5 order unchanged; every action carries `standing` + `evidenceNote`; **R1 (next lesson) only from an approved stamp** (unchanged); R5 has three explicit unverified outcomes: historical («ghi nhận trước hợp đồng mới, chưa kiểm lại nên chưa tính là tự làm được»), participation («đã tham gia, chưa chấm»), engaged («chưa có lần tự làm được nào được kiểm»). No minutes/percent/mastery (scanned). `basis` records `standing=… historicalUnvalidated=n participation=n`. | `lesson_next_action_test` |
| R4.8 | **Candidate-evidence gate: no half stamp** | `validateCandidateEvidence` | Lineage `(sourceDocumentId, lessonNo)` copied **iff** `context.hasLesson`; a Book-tier context (book, no lesson) previously produced a book-only stamp — found by the new lineage test, fixed to the A5 rule. Events from unresolved contexts are still minted (participation) with `null/null`. | `test/core/context/lineage_from_context_test.dart` |
| R4.9 | **Camera lineage — core-level proof** | same test | For Global / Subject / Book / lesson-without-book contexts: `LessonRef.fromContext == null`, `TutorSession.lineageFromContext == (null, null)`, `validateCandidateEvidence` stamps `null/null`. `CanonicalProblem` (perception path) has **no** `sourceDocumentId`/`lessonNo` fields (structural scan); no file under `core/perception` or `core/curriculum` assigns `lessonNo` outside `LessonRef.fromContext`. Complements `tutor_lineage_a5_test` (widget-level). | same |
| R4.10 | **`SourceQuoteIndex`** — one real pedagogy capability | `lib/core/pedagogy/source_quote_index.dart`; `PedagogyRuntime.planForScript(quoteIndex:)` | Every `«…»` span in a hint / feedbackMatched / scaffold must be a **verbatim substring** (after `normalizeAnswer`: lowercase, whitespace collapse, edge punctuation) of a text block of the *same lesson*; the matched block becomes the step's `sourceBlockId` (blocks in the question's `headingPath` section are preferred). Refusal codes: `HINT_UNSOURCED` (no quote), `QUOTE_ELIDED:<span>` («…»/`...` inside a quote is not verbatim), `QUOTE_NOT_IN_SOURCE:<span>`. **No paraphrase check, no OCR repair of the source, no fragment matching.** A hint leaves prototype only if: all quotes verify ∧ guard clean ∧ allowed (sourceStated) method ∧ plan bound. Feedback/scaffold keep `KEY_NOT_VALIDATED` (the prototype key has no validator — A3) but record the verified block for the «Sách viết» card. Without a `quoteIndex` nothing changes (fail closed). | `source_quote_index_test`, `pedagogy_runtime_test` (ROUND 4 groups incl. a positive control that flips a hint, a leak control, and the real-fixture measurement) |
| R4.11 | **`PlannedStepMode.samMode`** | `pedagogy_runtime.dart` | Maps to `SamMode.runtimeGuided` / `SamMode.prototypeScripted` (the enum Lane A-data added in round 3) — one enum for the per-step label. `pedagogyRuntimeVersion = 'pedagogy-runtime-v1'`. | `pedagogy_runtime_test` |
| R4.12 | **Validator registry unchanged** | `approvedEvidenceValidators` | Still exactly `{fraction-check-v1 (competence), candidate-gate-v1 (participation)}`. **No `sgk-stated-set-v1`** — see §3. | doctrine test §1 |

## 2. Pedagogy Reality on Bài 17 — before → after (measured)

Real fixture (`assets/fixtures/real/lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.json`, gitignored;
test skips when absent; synthetic fixture 4/12 → 4/12):

| Step | before | after | why (capability / refusal) |
|---|---|---|---|
| e1 explain | runtime | runtime | source block resolved + allowed method (round 3) |
| q1 / q2 / q3 ask | runtime ×3 | runtime ×3 | prompt verbatim = SGK question block (round 3) |
| n1 next | runtime | runtime | anchor block «Em đã học» resolved (round 3) |
| q1 hint#0, q2 hint#0, q3 hint#0 | proto | proto | `HINT_UNSOURCED` — no «…» quote at all |
| q1 hint#1 | proto | proto | `QUOTE_ELIDED` (quote contains «…») **and** `GUARD:CITATION_FABRICATION:trang 62` (page cite embedded in text) |
| q2 hint#1 | proto | proto | `QUOTE_NOT_IN_SOURCE` — script quotes «…bề mặt khoá thì vặn khoá lại»; the TSL block reads «khóa … vặn **khoa** lại» (OCR fidelity defect in the source — A-pipeline class, not fixed by the runtime) |
| q3 hint#1 | proto | proto | first quote «tách chất rắn không tan ra khỏi chất lỏng» **found** (block `p064:tc2-p1:004`, recorded as `sourceBlockId`); second quote drops «các» twice vs. the book ⇒ `QUOTE_NOT_IN_SOURCE` |
| feedbackMatched ×3 | proto | proto | `KEY_NOT_VALIDATED` (pronounces «khớp» from a prototype key); q2 also `QUOTE_NOT_IN_SOURCE` |
| scaffold ×3 | proto | proto | `KEY_NOT_VALIDATED` + `OVER_CAP_WITHOUT_VALIDATOR`; q1/q3 quotes («cô cạn», «Em đã học») verified and recorded |
| **Total** | **5 / 17** | **5 / 17** | **0 newly real steps.** Capability is real (positive control in the test flips a hint that quotes a block verbatim without leaking the key); the shipped script's quotes are not faithful to the source. |

What would make hints real without hard-coding (for Lane B / A-pipeline, not done here): q3#1 —
quote the book verbatim («tách **các** chất khó bay hơi ra khỏi **các** chất dễ bay hơi»); q1#1 —
remove «trang 62» and quote a contiguous span; q2#1 — the source OCR must be repaired
(`khoa` → `khoá`) by the pipeline, then the quote verifies as-is.

## 3. Validators registered: **none — honest**

Bài 17 has no SGK-stated answer set for any scripted question. The only rule the book states is
the «Em đã học» classification (Lọc / Lắng / Cô cạn / Chiết with their "dùng để tách" clauses,
blocks `p064:tc2-p1:003–007`). q1 («làm muối từ nước biển … phương pháp nào?») requires a
two-fact inference (salt-making = evaporation, p061:016 / p063:004; cô cạn = evaporating the
solvent, p063:005 / p064:006) — the book never prints «cô cạn» as *the answer to q1*
(`answer_keys_included: false`). q2 is a free-text «why»; q3 is a multi-step design question. A
`sgk-stated-set-v1` that encoded my inference would be an invented validator; a set-membership
validator ("names one of the four methods") would grant nothing and only inflate Evidence
Reality. Evidence Reality for Bài 17 stays **0** interactions with validator-permitted evidence.

## 4. Per-screen consequences of the strict default

All screens below read mastery through `masteryFromStore` → `replayMastery` (default now strict)
and map state through `learningMapStateFor` (default now strict). Deep-path sessions recorded by
`TutorSession` since round 3 carry `fraction-check-v1` and are **unaffected**.

| Screen | What changes | Lane B action needed |
|---|---|---|
| **Home** (`buildMissionFromStore`) — review chip, agenda, «Hôm nay mình thử dạng mới nhé» | Only stamped Deep sessions feed mastery/review. Pre-contract history and Assessment sessions no longer move the chip. **Demo domain** (`buildDemoDomain` in `mission_data.dart`, also used by `camera_demo_flow` result screen and `buildDemoParentTonight`) builds *unstamped* synthetic events ⇒ under strict it yields `insufficientEvidence`, no review chip, no `caseTransitionGap`. | One line in `mission_data.dart`: stamp the demo events with `fraction-check-v1` (they simulate Deep answers); the doctrine allowlist then shrinks. Until then two tests in `test/widget_test.dart` are **skipped with this reason**. |
| **Progress** | Session counts («TỰ LÀM trọn vẹn N phiên») unchanged (they read `maxSupportIn`, not mastery). The claim card (`ConceptSummary`) sees only stamped evidence; a learner whose only graded events are unstamped shows «chưa có bằng chứng học nào». | Optionally render `historicalUnvalidatedLabel` next to sessions whose events are `historicalUnvalidated` (`LearningEvent.readClass`). |
| **Learning Map** (`learning_map_screen`, subject tiles) | 🔵 «Tự làm được» only from stamped success; unstamped graded history shows 🟢 «Đã học cùng SAM». Badge/ordering logic unchanged. | none required; optional label as above. |
| **Parent** («Gần đây», Tonight) | `recentLessonTouches` now reports `hasHistoricalUnvalidated`; `parentLineFor` says «ghi nhận trước hợp đồng mới … chưa tính là tự làm được» instead of «Con đã tự làm được». Tonight demo (`buildDemoParentTonight`) is affected like Home demo. | same one-line demo stamp. |
| **Sessions / history** | Nothing is hidden or rewritten. | Show `readClass.historyLabel` per session/event («ghi nhận trước hợp đồng mới», «tự báo — không chấm», «đã kiểm (validator)»). |
| **Assessment** (`assessment_screen.dart`, unstamped, in the round-3 allowlist) | Answers are recorded but read as `historicalUnvalidated` ⇒ they no longer move mastery or the result screen's claim until the emitter stamps. | One line: `validation: FractionCheckValidator(fp).validation` (it already grades with `FractionProblem.checkAnswer`). |
| **Reader / Quiz-select** (Scale option keys, allowlisted) | Same as today: no validator ⇒ `historicalUnvalidated`; `session_recorder_test` asserts both readings. | Founder decision on `pack-option-key-v1` (returned since round 3). |
| **Lesson Workspace / SAM đề xuất** | `runtime_plan.dart` passes `StudentLessonState.unseen` (workspace emits nothing) — unchanged. When Lane B wires real events: `LessonNextAction.evidenceNote` and `.standing` are available; `PlannedStep.quotes`, `sourceBlockId` on hints/scaffolds, `PlannedStepMode.samMode`. | wire `quoteIndex: SourceQuoteIndex.fromLessonDocument(doc)` (one line) to get the quote refusals per step. |

**Migration note:** none. On-disk JSONL is byte-identical; the `validation` key stays optional;
absent ⇒ `historicalUnvalidated` at read time. Re-reading the same store with
`ConservativeBktPolicy` / `requireValidation: false` reproduces the pre-round-4 numbers exactly
(tested) — the legacy rule is preserved for audit, not deleted.

## 5. APIs for Lane B (Lesson Workspace and screens)

```dart
// read-side classification of any event (history labels)
final cls = event.readClass;            // EvidenceReadClass
final label = cls.historyLabel;         // e.g. 'ghi nhận trước hợp đồng mới'

// per-lesson state under the strict default
final state = StudentLessonState.fromEvents(ref, allEvents);
state.standing;                          // none | participatedUnverified | validated
state.evidenceNote;                      // honest sentence or null
state.historicalUnvalidatedCount; state.participationCount;

// Next Action — unchanged call, richer result
final next = NextBestLearningAction.forLesson(state: state, context: ctx, lesson: summary, viewsSeen: seen);
next.rule; next.reason; next.standing; next.evidenceNote;

// Pedagogy runtime — add the quote index
final plan = PedagogyRuntime.planForScript(
  script: doc.tutorScript!, binding: binding, studentState: state, context: ctx,
  blockText: (id) { final b = doc.blockById(id); return b == null ? null : LessonDocument.textOf(b); },
  quoteIndex: SourceQuoteIndex.fromLessonDocument(doc),          // NEW
);
step.mode.samMode;      // SamMode.runtimeGuided | prototypeScripted
step.sourceBlockId;     // now also set on hints/feedback/scaffold whose quotes verify
step.quotes?.refusals;  // QUOTE_ELIDED / QUOTE_NOT_IN_SOURCE / HINT_UNSOURCED (internal note, never to the child)
plan.runtimeGuidedIn(PlannedStepPhase.hint);

// Parent
final touches = recentLessonTouches(sessions); touches.first.hasHistoricalUnvalidated; parentLineFor(t);
```

Lane B must not pass `requireValidation: false` or `policy: ConservativeBktPolicy()` from any
screen; those are audit-only reads. Lane B still never constructs `PlannedStep` or
`EvidenceValidation`.

## 6. Returned for Founder review

1. **Two Lane B one-liners** that the strict default now makes visible: (a) `mission_data.dart`
   demo events unstamped (two Home widget tests skipped with the reason); (b)
   `assessment_screen.dart` unstamped — Assessment answers no longer count until stamped. Both
   shrink the round-3 doctrine allowlist once done. This lane did not edit `lib/features/**`.
2. **Lane B test fixtures touched by this lane** (fixture stamps only, no assertion changed;
   each file carries a header comment): `learning_map_test`, `knowledge_state_screen_test`,
   `parent_area_test`, `profile_screen_test`, `progress_screen_test`, `subjects_screen_test`;
   `session_recorder_test` now asserts both the strict reading (0) and the explicit legacy
   reading (1) for the unstamped quiz-select event; `test/widget_test.dart` two skips.
3. **Half stamp at the candidate-evidence gate** (R4.8): behaviour change for any surface that
   calls `validateCandidateEvidence` with a Book-tier context — such events are now `null/null`
   instead of book-only. No current caller passes a Book-tier context (Experiment passes a
   Lesson-tier context), but it is a rule change.
4. **Script/source defects surfaced by the quote rule** (§2): q1#1 fabricated page citation +
   elided quote (Lane B script); q3#1 dropped «các» (Lane B script); q2#1 OCR `khoa`/`khóa` in
   the TSL block `p063:tc2-p1:019` (A-pipeline fidelity class). Also the source block
   `p062:tc2-p1:003` reads «lặng gió … lăng xuông» (tone-mark defects visible on the Đọc view).
5. **`pack-option-key-v1`** (Reader/Quiz) and the **assessment stamp** — unchanged from round 3.
6. **Tone-mark placement normalisation** («khoá» ≡ «khóa») for quote matching — deliberately
   *not* applied (it would not have rescued q2#1 anyway because of «khoa», and normalising the
   source hides fidelity defects). Founder may decide otherwise.
7. **Legacy read policy retention**: `ConservativeBktPolicy` / `requireValidation: false` are
   kept as audit-only reads. Option: remove them entirely in a later round once no report needs
   the before/after comparison.
