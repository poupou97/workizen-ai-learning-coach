# 03 — LEARNING EXPERIENCE BLUEPRINT SPEC (v0)

> WAL-129 · code: `lib/core/pedagogy/learning_blueprint.dart` + `blueprint_catalogue_v0.dart`
> (20 test xanh, 3 mutation killed trên luật vi phạm). Blueprint = **hợp đồng sư phạm**, không
> phải prompt: engine THI HÀNH được và QA KIỂM được.

## 1. Năm tầng tách bạch (§7)

| Tầng | Ở đâu | Blueprint chứa gì |
|---|---|---|
| SOURCE | `PedagogySource` | (doc, trang, bài, authority, extractionMethod) |
| KNOWLEDGE | curriculum (concept/case/method ids) | CHỈ CON TRỎ — không sao nội dung |
| PEDAGOGY | `sequence` + `assistanceCap` + `evidenceRequired` + misconceptions + transfer/reflection | phần thân blueprint |
| PRESENTATION | **KHÔNG CÓ FIELD NÀO** | hoãn WAL-132 — Concept không sinh UI trực tiếp |
| REALIZATION | **KHÔNG CÓ PROMPT NÀO** | LLM contract là việc WAL-131 |

## 2. Schema v0 (chỉ field có dữ liệu thật)

`LearningExperienceBlueprint{blueprintId, subject, grade, lessonId, conceptIds, skillCaseIds,
methodIds, sequence: [PatternStep{intent, allowedActs, minutes?, organization?}], assistanceCap:
AssistanceRung, evidenceRequired: [EvidenceKind], misconceptionIds, transferRequired,
reflectionRequired, source: PedagogySource, version}`.
Các field của order chưa có evidence/cơ chế (surfaceCandidates, presentationPolicy, agePolicy
chi tiết) **chưa có mặt** — thêm khi WAL-132/50 chứng minh, không bịa trước (F3).

## 3. Hợp đồng KIỂM ĐƯỢC — `blueprintViolations(bp, log)`

Đối chiếu MỘT PHIÊN THẬT với blueprint, trả vi phạm (mutation-guarded cả ba luật):
- `ASSISTANCE_OVER_CAP` — sự kiện mang support vượt `rungToSupport(assistanceCap)`;
- `CASE_OUT_OF_BLUEPRINT` — dạy chéo ca ngoài hợp đồng;
- `EVIDENCE_MISSING` — phiên CÓ TRẢ LỜI mà thiếu bằng chứng bắt buộc (vd không có
  independentAttempt = chỉ-xem-làm-mẫu); phiên bỏ dở trước khi trả lời KHÔNG bị đòi.

## 4. ⭐ Blueprint drive phiên THẬT (acceptance §36.3)

`bp:toan5:b6:quy-dong-khac-mau` (nguồn 05-sgv-toan-5 p36 — MỤC TIÊU nói thẳng «lấy mẫu số
chung là tích của hai mẫu số», khớp method slice WAL-108) chạy trên TutorSession thật:
- phiên sai→hint→đúng: **0 vi phạm** (test);
- phiên xin-hint-ngay rồi đúng: **EVIDENCE_MISSING independentAttempt** (test);
- phiên leo fullSolution đối chiếu blueprint Sử (cap strategicHint): **ASSISTANCE_OVER_CAP** (test);
- phiên Toán đối chiếu blueprint TV: **CASE_OUT_OF_BLUEPRINT** (test).

## 5. Catalogue v0 — 8 blueprint, 5 family, nguồn thật

| Blueprint | Nguồn | Sequence | Cap | Đặc thù |
|---|---|---|---|---|
| toan5:b6 quy-đồng | 05-sgv-toan-5 p36 | ACTIVATE→DISCOVER→PRACTICE→APPLY→CONSOLIDATE | workedSolution | transferRequired; drive WAL-108 |
| toan6:b15 bỏ-ngoặc | 06-sgv-toan-6 p84 | PRACTICE(5p)→DISCOVER(7p)→APPLY(5p) — CÓ PHÚT | demonstration | misconception nguồn gắn thẳng |
| toan3 chu-vi | 03-sgv-toan-3 p190 | ACTIVATE(contrast!)→DISCOVER→PRACTICE | workedSolution | mở bằng CONTRAST đúng cảnh báo SGV |
| tv1 âm-vần | 01-sgv-tv-1 p44 | ACTIVATE→CONSOLIDATE (đo ×20) | demonstration | misconception vùng miền |
| tv3 đọc-hiểu | 03-sgv-tv-3 p114 | ACTIVATE→PRACTICE | partialScaffold | askExplanation — recognize≠explain |
| su10 sử-liệu | 10-sgv-lich-su-10 p44 | DISCOVER→APPLY (đo ×5) | **strategicHint** | KHÔNG reveal/workedExample — SAM không kết luận hộ |
| khoa4 quan-sát | 04-sgv-khoa-hoc-4 p7 | DISCOVER→APPLY→REFLECT | partialScaffold | observeWait trước — learner observation ≠ source fact |
| nn3 listening | 03-sgv-ta-3-GS p8 | ACTIVATE→PRACTICE→REVIEW | demonstration | hint = REPLAY audio, không transcript |

Test giữ: ≥4 chuỗi intent KHÁC nhau (không rập khuôn — F2/F3); mọi blueprint đòi
independentAttempt; misconceptionIds không mồ côi; Sử không có act reveal.

## 6. Versioning & replay (§32)

`blueprintVersion='blueprint-v0'` + mỗi blueprint mang version riêng. Evidence không đổi nghĩa:
violation check đọc SupportLevel BẤT BIẾN từ log; đổi blueprint ⇒ chạy lại check, log nguyên vẹn
— cùng nguyên tắc replayMastery. Phiên cũ không bị reinterpret: check là hàm (bp, log) → report,
không ghi ngược vào log.

## 7. Giới hạn v0

sequence chưa được ENFORCE thứ tự trong TutorSession (session hiện tại là ladder ±1 — mapping
act↔session step là việc PED-D/E khi validate 5 môn); organization field mới có ở data pattern,
chưa dùng; agePolicy đang là hệ quả của grade, chưa policy hoá (WAL-50).
