# 05 — PEDAGOGICAL QA & LLM REALIZATION CONTRACT (v0)

> WAL-131 · code: `lib/core/pedagogy/realization_contract.dart` + rule LEARNER_FIRST trong
> `learning_blueprint.dart` · tests: `test/core/pedagogy/` (subject_validation +
> realization_contract). Kế thừa và LẮP các mảnh đã mutation-guarded: output_guard (WAL-30),
> buildTutorPrompt cage, eval L1+L2 (WAL-101), blueprintViolations (WAL-129).

## 1. Pedagogy scenarios — 15 loại §9, hiện trạng phủ

| # | Scenario | Cơ chế kiểm | Trạng thái |
|---|---|---|---|
| 1 | đúng độc lập | blueprintViolations + evidence taxonomy | test (5 môn) |
| 2 | sai lần đầu | TutorSession wrong→retry | test WAL-86 |
| 3 | misconception xác định | SourceMisconception (prior) + ErrorHypothesis (proposed-only) | model + seed; probe-confirm là WAL-49 gate |
| 4 | đúng sau small hint | interventionId lineage + independent=false | test e2e slice |
| 5 | xin đáp án | REVEAL gate (revealAllowed) | test + mutation WAL-86 |
| 6 | method chưa học | TutorScope RỖNG (leakage test lớp 4) | test WAL-130 |
| 7 | provenance thiếu | explainTeaching null ⇒ không prompt nào tồn tại | test WAL-30 |
| 8 | LLM đề xuất ngoài scope | METHOD_NAME guard (BCNN) | test + shadow 50-run |
| 9 | conceptual đúng, procedural sai | ErrorHypothesisType.procedural | model WAL-27 |
| 10 | đã thành thạo | decide()→executionError + stepBack | test adaptive |
| 11 | sai liên tục | ladder cap + không auto-escalate vượt trần | blueprint cap test |
| 12 | self-correct | EvidenceKind.selfCorrection (bằng chứng mạnh) | test + mutation |
| 13 | bỏ giữa chừng | recordSession ghi; blueprint KHÔNG đòi evidence | test WAL-129/130 |
| 14 | transfer | transferRequired + TransferProbe | model WAL-103; enforce runtime = P1 |
| 15 | assessment | tutoringViolationsInExam + EXAM_TUTORING guard | test + mutation |

Violation vocabulary hợp nhất: ASSISTANCE_OVER_CAP · CASE_OUT_OF_BLUEPRINT · EVIDENCE_MISSING ·
LEARNER_FIRST_VIOLATED (mới — trả nợ WAL-130 #1) · METHOD_NAME · PRAISE · EXAM_TUTORING ·
ESCALATION · REVEAL · ACT_OVER_RUNG (mới).

## 2. LLM input contract — RealizationRequest

Engine quyết TOÀN BỘ trước khi model thấy gì: `{act, rung, scope (APPLICABLE∩ALLOWED),
methodId, grade, facts (DerivedFacts — số dẫn xuất của bài), kind, examMode,
childStatedFacts}`. Prompt lắp bằng `buildTutorPrompt` (chuồng WAL-30): method duy nhất,
từ vựng đóng theo stage, nguồn nguyên văn sourceLineForChild, thang ±1 + REVEAL + luật khen.
LLM trả REALIZATION (wording) — không trả quyết định nào.

## 3. Output validate + fallback

`validateRealization(text, request)`:
1. **ACT_OVER_RUNG** — act nặng hơn rung là lỗi ENGINE ⇒ fail closed (không tin cả engine);
2. guard tất định `validateTutorOutput` với `maxAllowed = rungToSupport(rung)` — chặn
   METHOD_NAME/PRAISE/EXAM_TUTORING/ESCALATION/REVEAL (childStatedFacts miễn phạt lời trẻ tự nêu).
Vi phạm ⇒ **fallback deterministic** (`hintTextFor` — nội dung rule-based sẵn có), KHÔNG
retry-đến-khi-lọt, không hiển thị tạm. Giới hạn L3 GHI THẬT (từ output_guard): guard chưa chặn
mô-tả-phép-tính thuần lời — một lý do KEEP SHADOW còn nguyên hiệu lực.

## 4. Deterministic vs generative per act (§23)

| Policy | Acts | Lý do |
|---|---|---|
| DETERMINISTIC | revealAnswer, revealStep, demonstrateStep, workedExample | tính được từ bài — sai một số là sai bài; COGS 0 |
| TEMPLATE | observeWait, stepBack, askVerification, reflect | câu cấu trúc cố định |
| RETRIEVAL-BASED | contrastCases, explainConcept | cần nội dung nguồn có provenance |
| GENERATIVE-GUARDED | pumpRecall, diagnosticProbe, smallHint, strategicHint, askExplanation | wording tự nhiên có giá trị; TOÀN BỘ ≤ hint nên guard số học đủ chặn rò |

Bất biến giữ bằng test: nhóm generative ⊆ nhóm ≤hint — không act generative nào được lộ bước giải.
COGS: generative-guarded $0.012/lượt (đo 50-run); deterministic/template $0.

## 5. interventionKind (trả nợ WAL-130 #2)

`InterventionKind{textHint, replayAudio, slowAudio, transcript, visual}` + id mở rộng
`policy/method@rung#kind` — «phát lại chậm» ≠ «lộ transcript» phân biệt được trong data.
Evidence cũ không hậu tố đọc là textHint (tương thích, không reinterpret).

## 6. Versioning & replay

pedagogy-model-v0 · blueprint-v0 (+rule LEARNER_FIRST = v0.1 behaviour, constructor-compatible)
· tutor-session-v1 · knowledgeModelVersion slice. Mọi check là hàm (contract, log) → report;
log bất biến. Đổi contract ⇒ chạy lại check trên log cũ, kết quả MỚI mang version MỚI.

## 7. Trạng thái gate

Model call THẬT vẫn KEEP SHADOW (WAL-30) — contract này là hạ tầng để khi Founder mở canary
(P2-E/WAL-124), mọi lời sinh ra đã có chuồng + guard + fallback + eval L1/L2 đo được.
