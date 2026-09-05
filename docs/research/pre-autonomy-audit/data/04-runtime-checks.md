# Data 04 — Runtime checks, test totals, skipped tests

## 1. `flutter analyze` / `flutter test` (evidence: `scripts/flutter-analyze-B-C.log`, `scripts/flutter-test-B-C.log`, `scripts/flutter-test-B-C-with-packs.log`)

| Run | Result |
|---|---|
| `flutter analyze` (worktree @ e5155f4) | **No issues found** (exit 0) |
| `flutter test --reporter expanded`, packs absent (clean-clone condition) | **633 passed · 14 skipped · 0 failed** (exit 0) |
| same, after copying the gitignored packs (`lesson-index-g1..12.json`, `sam-stories.db`, 301 covers) into `assets/pack/` | **647 passed · 0 skipped · 0 failed** (exit 0) |

The 14 skips (`scripts/skipped_tests.py` over the log) are all "pack chưa build trên máy này" — pack-gated tests that mark themselves skipped rather than green: `stories_store_test` ×3, `discovery_test` ×3, `lesson_duplicates_test`, `lesson_index_test` (FILE THẬT), `source_gallery_test` (FILE THẬT), `data_driven_lesson_test` ×2, `book_shelf_test`, `architecture_gate_test` ×2. All 14 **passed** when the packs were present. Per the clean-clone memory rule: CI without packs cannot see the Architecture Gate; it is only proven on a machine with packs.

## 2. `dart run scripts/runtime_checks.dart` (against production classes; output `scripts/runtime_checks.out`)

| Check | Result | Meaning |
|---|---|---|
| C1 TutorSession eventId unique across re-open of the same exercise | **FAIL** — both sessions produce `cur:05-sgk-toan-5-tap-mot:p20:b6#0`, `#1` | `eventId = '$exerciseId#$seq'` (`tutor_session.dart:88`); `seq` restarts per session. Any future de-duplication by id would drop real attempts (the exact failure `replay_audit_test:98` guards for `attributeEvidence`, but not for TutorSession/surfaces). |
| C2 `evidenceFor` keeps both sessions' events | PASS (4 events, 2 distinct ids) | No silent dedupe today ⇒ no data loss, but ids are not identifiers. |
| C3 identical session appended twice is not double-counted | **FAIL** — evidenceCount 2 from one real attempt | `appendSession` is not idempotent (`learner_store.dart:138`); `onFinished` firing twice or a retry would double mastery evidence. |
| C4/C4b `gradable=false` when `correctOption` null / out of range | PASS | `learning_activity.dart:81-83` |
| C4c `shortText` ⇒ `SurfaceKind.unsupported` | PASS | `learning_activity.dart:96` |
| C5 unknown case ⇒ `allowedMethods` empty | PASS | `pedagogical_boundary.dart:221-228` |
| C5b unpermitted/unknown methodId ⇒ `explainTeaching` null | PASS | `teaching_provenance.dart:81-84` |
| C5c unpermitted method ⇒ `buildTutorPrompt` null | PASS | `tutor_prompt.dart:45` |
| C5d hint on a case with no permitted method ⇒ null (event still logged) | PASS | `tutor_session.dart:150-155` |
| C6 validator with `support = workedStep` still mints `kind = independentAttempt` | CONFIRMED (latent mislabel) | `evidence_validator.dart:70` hard-codes the kind; `support` is copied but not consulted. |
| C6b such an event renders as 🔵 "Tự làm được" on the Learning Map | CONFIRMED | `learning_map_state.dart:41-46` keys on kind only, not on `correct`/`support`. |
| C6c `lookup` intent ⇒ no evidence | PASS | `evidence_validator.dart:64` |
| C7 Reader-style event (no lineage) ⇒ Learning Map badge `unseen` | CONFIRMED | Reader/Compose/Source/Tutor/Assessment events carry no `sourceDocumentId/lessonNo` (grep) ⇒ invisible to `learningMapStateFor` and `recentLessonTouches`. |
| C8 evidence keyed by `learnerId` (L2 sees nothing of L1) | PASS | `learner_store.dart:152,224-231` |
| C9 hand-edited JSONL (`correct` true→false) replayed without detection | CONFIRMED | no hash/signature; `fromJsonl` skips only malformed lines (`learner_store.dart:99-103`). |
| C10 `SliceCurriculum` registrations | INFO: grade 5 = 1, grade 6 = 0 | `slice_curriculum.dart:114-118` |

## 3. `flutter test scripts/pack_counts_test.dart` (production parser over the real packs; output `scripts/pack_counts.out`)

3,650 TOC lessons / 187 openable / 1 Deep-path lesson across the 12 packs (per-grade table in `data/03-two-paths-inventory.md`). Test passed (1 test).

## 4. LLM / network surface (Q7)

- `pubspec.yaml` dependencies: `cupertino_icons`, `sqlite3`, `sqlite3_flutter_libs`, `path_provider`, `camera`, `google_mlkit_text_recognition` — no HTTP client, no LLM SDK.
- `grep -rniE "anthropic|openai|gemini|claude|gpt|llm|http\.|HttpClient|dio|Uri\.parse|WebSocket|socket|api[_-]?key" lib` → comment lines only (`realization_contract.dart:1-9`, `tutor_prompt.dart:12`, `output_guard.dart:1`, `learning_context.dart:10-12` etc.); zero executable network/LLM code.
- `buildTutorPrompt` (`tutor_prompt.dart:39`) and `validateRealization` (`realization_contract.dart:88`): 0 callers in `lib/`. The only model invocation is the offline harness `tool/shadow/run_shadow.py` (`claude -p`), documented as SHADOW ONLY.
- `educationCapabilityPolicy['chat-generic'] = disable` (`education_safety_policy.dart:48`); `education_safety_policy_test:48` scans `lib/features` for a `chat` directory (TEST-PASSED).
- On-device ML present: ML Kit OCR (`mlkit_ocr_adapter.dart`) — output is a `PerceptionHypothesis`, type-gated by `ConfirmedProblem.confirm` (`perception_provenance.dart:76`) before it can become a problem.
