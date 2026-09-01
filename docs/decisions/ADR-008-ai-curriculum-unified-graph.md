# ADR-008 — AI Curriculum (QĐ 2422) là DOMAIN trong graph hợp nhất + cạnh `aiIntegration`

**Ngày:** 2026-09-01 · **Trạng thái:** PROPOSED (L2 — hướng kiến trúc; chốt ACCEPTED sau
khi tầng ingestion Dart đầu tiên chạy trên dữ liệu này) · **Nguồn:** WAL-89/90/91/92

## Bối cảnh
QĐ 2422/QĐ-BGDĐT ban hành khung giáo dục AI lớp 1–12 với hệ mã chính thức tự-định-nghĩa
(NLa-d/A-D, 13 chủ đề, 267 YCCĐ dạng `<lớp>.<chủ đề>.<MR?><stt>`). Trích xuất tất định đã
chạy: 265 SOURCE_EXPLICIT + 2 INFERRED_OCR_CORRECTED. Câu hỏi: kiến trúc nào chứa nó?

## Quyết định (falsify 4 phương án — chi tiết ở QD2422-CV5588-AI-CURRICULUM.md §5)
1. **KHÔNG dựng graph AI riêng** (phương án A — FALSIFIED: hạ tầng đôi không mua được gì;
   cấu trúc 2422 đẳng cấu concept→SkillCase→LearningStage hiện có).
2. **AI = một domain trong curriculum graph hợp nhất**: outcome 2422 là node mang MÃ CHÍNH
   THỨC first-class (giữ NGUYÊN VĂN mã — không rename); mạch/chủ đề là cấu trúc domain.
3. **Ngữ nghĩa hybrid của Founder giữ ở tầng CẠNH** (MODIFY, không ADOPT nguyên trạng):
   loại `CurriculumEdge` mới **`aiIntegration`** nối outcome AI ↔ objective môn học,
   citable chỉ khi có nguồn. **Không có cạnh = không tích hợp** — bất biến "không ép AI
   vào bài" (nguyên văn CV 5588 §2.2) được thi hành bằng cấu trúc, không bằng lời dặn.
4. **Mã là ĐỊNH DANH, không phải thứ tự dạy** (chính văn bản nói) — cấm sinh prerequisite
   từ mã; prerequisite AI (nếu có) phải có nguồn riêng như mọi cạnh khác.
5. Versioning: nguồn mới của khung = sourceId mới; evidence cũ giữ mã cũ (bake-at-write-time
   WAL-72 đã bảo đảm REPLAY MUST NOT SILENTLY REINTERPRET). Không thêm trường version mới.

## Bằng chứng đã đo
POC truy vấn local (query_ai_curriculum.py): 6 dạng câu hỏi trả lời kèm mã+trang; trần-lớp
giữ F8 (phản ví dụ: bỏ trần lộ 12 outcome lớp 3–12); cả khung = 135KB thô / **27KB gzip**
⇒ nằm trong SAM KNOWLEDGE PACK cục bộ dư 3 bậc độ lớn (ADR-006), KHÔNG cần embeddings
(chưa đo thấy retrieval fail — luật ADR-006 giữ nguyên).

## Hệ quả
- Ingestion Dart: outcome 2422 → curriculum layer, provenance = sourceId `vn-moet-qd2422-2026`
  + trang; status SOURCE_EXPLICIT/INFERRED giữ nguyên vào model.
- LearningEvidence/TeachingAct KHÔNG đổi (gap analysis §6–7 doc nghiên cứu: gap ở CONTENT,
  không ở kiến trúc).
- LEGAL: extraction ở ngoài git tới khi WAL-43 xác nhận quyền tái sử dụng văn bản hành chính
  (Điều 15 Luật SHTT — LEGAL INTERPRETATION / REVIEW PENDING, không tự chứng nhận).
