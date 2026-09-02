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
