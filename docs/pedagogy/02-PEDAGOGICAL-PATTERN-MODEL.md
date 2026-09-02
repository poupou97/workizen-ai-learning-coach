# 02 — PEDAGOGICAL PATTERN MODEL (v0)

> WAL-128 · code: `lib/core/pedagogy/` (analyze sạch, 11 test, 3 mutation killed) ·
> data: `poc-out/pedagogy/patterns-v0.json` (12 instances từ nguồn thật).
> Nguyên tắc: field nào chưa có evidence từ WAL-127 thì CHƯA CÓ MẶT trong schema — prototype
> rồi falsify, không hard-code «đủ mọi field» (§5 Founder Order).

## 1. PedagogicalIntent — taxonomy ĐO ĐƯỢC, không phải 18 mục lý thuyết

8 intent VN xuất hiện thật trong sample (ACTIVATE, DISCOVER, PRACTICE, APPLY, GAME,
CONSOLIDATE, REFLECT, REVIEW) — enum `PedagogicalIntent`. 10 candidate còn lại của order
(OBSERVE, NOTICE_PATTERN, COMPARE, CLASSIFY, MODEL, TRANSFER, ARGUE_FROM_EVIDENCE, REVISE,
CREATE, PERFORM, INVESTIGATE, VERIFY) **chưa có marker đo được trong SGV KNTT sample** —
sẽ thêm KHI PED-D chứng minh cần (một phần nằm ở tầng TeachingAct: askVerification,
contrastCases ≈ COMPARE).

## 2. TeachingAct — 15 act, mỗi act một dòng prior art (WAL-67)

`TeachingAct` enum: observeWait · pumpRecall · diagnosticProbe · smallHint · strategicHint ·
contrastCases · explainConcept · demonstrateStep · workedExample · askExplanation ·
askVerification · reflect · stepBack · revealStep · revealAnswer.
Phân tầng đã falsify M:N (WAL-67): **outer** LearningGoal (decide() giữ nguyên) / **inner**
TeachingAct / **domain** TeachingMethod = tham số TUỲ CHỌN (`PlannedAct{act, methodId?}`) —
act thuần sư phạm (observeWait, diagnosticProbe, reflect, stepBack) không cần method.

**Bất biến ghi-evidence** (`supportLevelOf`, mutation-guarded): act không đưa nội dung → none;
đưa nội dung định hướng (kể cả pumpRecall — BẢO THỦ) → hint; làm mẫu/giảng/lộ một bước →
workedStep; revealAnswer → fullSolution. Evidence 4 nấc BẤT BIẾN — pedagogy map XUỐNG,
không bao giờ reinterpret ngược (§32).

## 3. AssistancePolicy — thang 7 nấc §17 nối vào kernel có sẵn

`AssistanceRung`: independent → prompt → smallHint → strategicHint → partialScaffold →
demonstration → workedSolution. `rungToSupport` ĐƠN ĐIỆU TĂNG (mutation-guarded — đảo một
nấc là «đúng sau demonstration» lẻn xuống hint; «đúng sau prompt» KHÔNG BAO GIỜ là độc lập).
Escalate/step-back/reset per-blueprint là việc WAL-129; kernel WAL-68/87 (±1 Wood) và
WAL-104 (supportCap theo assignment) giữ nguyên vai trò — không nhân khái niệm.

## 4. Misconception — SourceMisconception TÁCH KHỎI ErrorHypothesis

Hai khuôn, hai thẩm quyền, không đường nối tự động:
- `SourceMisconception` (MỚI): SGV nói thẳng, tồn tại trước mọi learner; seed v0 = **4 mục
  giám tuyển từ 39 candidate** (Toán 3 p190 chu-vi-HCN=3×chu-vi-HV; Toán 3 p84 đếm cạnh;
  Toán 6 p84 bỏ-ngoặc-dấu-trừ; TV1 p110 phụ-âm-vùng-miền l–n/v–d/x–s). observablePattern là
  PARAPHRASE — nguyên văn ở poc-out (WAL-43). skillCaseId để null khi chưa map — không bịa.
- `ErrorHypothesis` (WAL-27, giữ nguyên): runtime, proposed→confirmed qua probe.
Hypothesis được TRÍCH DẪN SourceMisconception làm prior; chiều ngược bị cấm bằng cấu trúc.
Nguồn tách nhãn đủ 5 mức: SOURCE_EXPLICIT/SOURCE_DEMONSTRATED/SAM_INFERRED/EXTERNAL_RESEARCH/
EXPERIMENTAL (`PedagogyAuthority`, §21 — không gắn tất cả «Theo SGK»).

## 5. TransferCheck & Retention — dùng kernel Done, blueprint chỉ THAM CHIẾU

TransferProbe (WAL-103) + ReviewSchedule (WAL-23) + evidence taxonomy independent/transfer/
retention đã tồn tại và có test. Pattern model KHÔNG định nghĩa lại — blueprint (WAL-129)
khai `transferRequirement`/`reflectionRequirement` trỏ vào các cơ chế đó. (§19: mastery ưu
tiên INDEPENDENT + TRANSFER + RETENTION; completion không phải mastery.)

## 6. PresentationPreference — HOÃN sang WAL-132

Sample WAL-127 đo được organization (nhóm/cặp/lớp) và ResponseKind (WAL-97) nhưng CHƯA đủ
evidence để schema-hoá preference per-pattern. Ghi nhận, không bịa field. (K/P/P tách tầng
— Presentation là tầng riêng.)

## 7. Provenance — PedagogySource

`PedagogySource{authority, extractionMethod, sourceDocumentId?, page?, lesson?}` — assert
compile-time: thẩm quyền từ nguồn thì PHẢI trỏ được về nguồn; externalResearch/experimental
được phép không có doc (nhưng phải khai extractionMethod `research:<ref>`).

## 8. Pattern instances từ nguồn thật (12, poc-out/pedagogy/patterns-v0.json)

Top: TOAN 3-5 `ACTIVATE→DISCOVER` ×43 (03-sgv-toan-3 p33) · TV 1-2 `ACTIVATE→CONSOLIDATE`
×20 · TOAN 10-12 `PRACTICE→APPLY` ×6 · SU 10-12 `DISCOVER→APPLY` ×5 · **TOAN 6-9
`PRACTICE(5p)→APPLY(5p)→DISCOVER(7p)→PRACTICE(5p)→APPLY(5p)` — CÓ PACING PHÚT từ bảng cấu
phần** (06-sgv-toan-6 p22). Limitation: NN 1-2 instance degenerate (lesson-attribution EN
chưa chuẩn — Unit≠LESSON N); intent per-family khác nhau rõ — mỗi family một khuôn.

## 9. Falsifications (challenged bằng dữ liệu)

- **F4 một Concept một cách dạy — SAI**: WAL-38 đo được quy-đồng dạy 2 method khác nhau ở
  lớp 4 vs lớp 5 (take-larger vs by-product) cho CÙNG concept.
- **F5 một Method một presentation — SAI**: WAL-67 §2 — method «lấy tích hai mẫu» chở 6 act
  khác nhau (EXPLAIN/DEMONSTRATE/WORKED_EXAMPLE/SMALL_HINT/ASK_EXPLANATION/CONTRAST_CASES),
  mỗi act một hình thức trình bày.
- **F7 hint escalation tuyến tính — KHÔNG LUÔN**: REVEAL gate hiện tại đã đứng-yên (phi
  tuyến); chuỗi đo được có vòng lặp `ACTIVATE→CONSOLIDATE→ACTIVATE→CONSOLIDATE` (TV1) và
  `PRACTICE→APPLY→DISCOVER→PRACTICE` (Toán 6) — quay lại là nước đi bình thường.
- **F15 cùng lỗi cùng misconception — SAI**: cùng «đọc sai» nhưng l–n (Bắc) ≠ v–d (Nam) ≠
  x–s — khác nguồn gốc vùng miền (TV1 p110); cùng «kết quả sai» Toán nhưng sai-dấu-bỏ-ngoặc
  (procedural) ≠ chu-vi-lẫn-diện-tích (conceptual).

## 10. Versioning

`pedagogyModelVersion = 'pedagogy-model-v0'` — mọi pattern/misconception mang version.
Evidence cũ không bị reinterpret: SupportLevel không đổi nghĩa, mapping là hàm MỘT CHIỀU.
