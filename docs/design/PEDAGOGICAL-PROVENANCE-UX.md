# PEDAGOGICAL PROVENANCE UX (Task Order §6, §21.I)

**Chuỗi end-to-end (mọi mảnh ĐÃ TỒN TẠI trong kernel — UI chỉ render):**
Source(unit trang in) → Method(catalogue 29, trang nguồn) → TutorScope(APPLICABLE ∩
ALLOWED) → explainTeaching() → TeachingProvenance{WHAT/WHERE/SOURCE/HOW/WHY/AUTHORITY/
PERMISSION} → UI 3 tầng:

1. **Inline mọi TeachingAct** (F22: NO show-cuối): dòng nguồn nhỏ dưới mỗi lời dạy —
   `sourceLineForChild` (mutation-guarded): «Theo SGK Toán 5, trang 21» (stated) /
   «SAM làm theo ví dụ trong SGK…» (demonstrated) / «Đây là cách của SAM…» (inferred).
2. **Màn 16 Why This Method** — render whyLineForChild + PERMISSION («con đã học nó
   trong chương trình lớp 5, bài B6») + trực quan; nội dung method từ catalogue (tích
   hai mẫu), không bịa.
3. **Màn 17 Source** — tuổi-thích-ứng: nhỏ = 3 icon mức (📖/🧭/✨); lớn/parent =
   source → trang → ContentUnit id → Method → SkillCase → version (mapping version
   qmap-v1 đã nướng trong evidence).

Fail-closed hiển thị: scope rỗng/method không phép ⇒ KHÔNG có TeachingAct để render
⇒ màn «SAM chưa chắc về bài này — mình hỏi cô/thử bài khác nhé» (không có nhánh
«dạy đại»). Voice cùng luật: câu nói sinh ra từ cùng TeachingProvenance + output_guard.


## WAL-114 (2026-09-02) — LINEAGE END-TO-END ĐÃ CODE HOÁ

- `lib/core/knowledge/lineage.dart`: `lineageFor(event, catalogue, scope)` —
  từ MỘT LearningEvent truy về ĐÚNG TRANG IN của sách nguồn, trả trace 7 chiều
  WHAT/WHERE/WHY/HOW/SOURCE/AUTHORITY/PERMISSION (JSON in được), hoặc FAIL
  CLOSED với mã: noTeachingIntervention · methodUnknown (provenance mismatch) ·
  methodNotAllowed · missingSource · futureKnowledge · curriculumConflict.
- Authority levels: SOURCE_EXPLICIT (sourceStated) / SOURCE_DEMONSTRATED
  (sourceDemonstrated) / SAM_INFERRED (mọi thứ còn lại — kể cả sourceSequence:
  mục lục không phải lời sách). Mint qua `explainTeaching` duy nhất.
- Mọi evidence mới mang CẶP VERSION: `policyId` (tutor policy) +
  `knowledgeVersion` (knowledge model — `knowledgeModelVersion`), sống qua
  JSONL round-trip. Dữ liệu cũ `null` = trước WAL-114, fail-closed khi truy.
- KHÔNG FABRICATE CITATION: `validateTutorOutput` chặn LLM tự nói
  «SGK/trang N/sách nói/theo sách» (CITATION_FABRICATION) — trích dẫn chỉ
  render tất định từ `Provenance.sourceLineForChild`.
- Tests: test/core/knowledge/lineage_test.dart (7 chiều + 5 fail-closed + 
  authority table + round-trip) · test/core/tutor/citation_guard_test.dart.
