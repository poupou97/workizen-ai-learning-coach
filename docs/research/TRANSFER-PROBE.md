# TransferProbe — verify transfer, không tuyên mastery từ cùng-template (WAL-103)

**Trạng thái:** POC theo Founder Directive 2026-09-02 §H. Gap thật duy nhất được
phép thêm khái niệm mới sau audit 18-capability.

## 1. Vấn đề

Chuỗi đúng liên tiếp trên bài CÙNG KHUÔN (same template) là bằng chứng của
*thuộc khuôn*, chưa phải *hiểu kỹ năng*. BKT hiện tại không phân biệt — 5 lần
đúng «3/4 + 1/5» dạng trần đẩy pMastery lên như 5 lần đúng trên 5 bề mặt khác
nhau. Claim gate (coverage) chặn theo **ca chưa quan sát**, nhưng trong MỘT ca
vẫn mù về **bề mặt**.

## 2. Ngữ nghĩa 4 loại bằng chứng — KHÔNG phải 4 điểm số

Acquisition (học lần đầu, sau worked-example) · Practice (luyện có/không hỗ
trợ) · Retrieval (tự làm sau khoảng cách thời gian — đã có qua
`lastIndependentEvidenceAt` + ReviewSchedule) · **Transfer** (tự làm trên bề
mặt CHƯA GẶP của cùng kỹ năng). Chúng là **ngữ cảnh của sự kiện**, suy được từ
cấu trúc sẵn có (thời điểm so với hint/worked-example; bề mặt bài so với các
bài đã làm) — KHÔNG thêm trường mastery nào. Một `LearningEvent` độc lập trên
bề mặt mới = bằng chứng transfer; kernel không lưu «transferScore».

## 3. Taxonomy bề mặt (đo được từ corpus, không bịa)

`SurfaceFamily`: `bareExpression` («3/4 + 1/5 = ?») · `comparison` («phân số
nào lớn hơn») · `visualModel` (hình/băng giấy — rebuild_fractions bbox) ·
`wordProblem` (đề lời văn). **Near transfer** = cùng family, khác template.
**Far transfer** = khác family; `wordProblem` xa nhất (evidence map đã ghi
retrieval-practice ÂM TÍNH với word-problem — Agarwal 2019 — nên far-probe
không bao giờ là bước bắt buộc để claim, chỉ là bằng chứng bổ sung).

## 4. Luật kích hoạt — tất định, hà tiện

Chỉ probe khi CẢ BA: ① ca sắp chạm claim mạnh (pMastery ≥ strongAt) — vì
transfer-probe là *gate của claim*, không phải bài luyện thường; ② toàn bộ
bằng chứng độc lập gần đây nằm trên MỘT bề mặt/khuôn (đa dạng rồi thì không
cần); ③ có bài cùng-ca khác-bề-mặt trong pool. Thiếu ① hoặc ② → không probe
(không biến mọi bài thành kiểm tra). Thiếu ③ → **fail closed**: trả `null`,
claim GIỮ mức hiện tại kèm sự thật «chưa thử bề mặt khác» — không đoán.

## 5. Chọn bài — kiểu `nextProbe` (WAL-70)

Cùng SkillCase; near trước far (khoảng cách family theo bảng cố định); trong
cùng khoảng cách: bài đơn-kỹ-năng trước (không nhiễm ca khác — luật ② của
nextProbe); hoà → id từ điển. Mọi lựa chọn kèm `reason` đọc được (F4).

## 6. Giới hạn ghi thật

- Surface tag của bài đến từ NGƯỜI SOẠN POOL (corpus extraction đã phân
  RULE/EXAMPLE/PRACTICE; word-problem nhận diện được bằng lexicon) — POC nhận
  tag làm input, KHÔNG tự đoán từ text bài.
- templateId v1 = chuỗi chuẩn hoá của expression skeleton; đủ cho bare
  expression, chưa đủ cho word problem (cần NLP — RESEARCH LATER).
- Chưa nối vào QuizSelect/Agenda — Agenda đã chừa `AgendaActionKind.transfer`;
  nối là bước riêng sau khi Founder thấy POC.
