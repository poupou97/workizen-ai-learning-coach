# TUTEUR-IA-AUDIT — (không tồn tại) → thay bằng Open-TutorAi/open-tutor-ai-CE

**Verify canonical:** «Tuteur IA» và «Open Alpha» — **KHÔNG tìm được repo canonical** (2 vòng
search có chủ đích). Theo luật §9: KHÔNG clone thứ không verify được. Thay thế gần nhất có
thật: **open-tutor-ai-CE** (SHA 196c547 · 2026-06-26 · có LICENSE; arXiv 2602.07176).
**Chạy được?** `NOT WORTH RUNNING` (stack lớn UI+gateway+devops; câu hỏi trả lời được bằng đọc model).

## Claim vs code

| Claimed | Evidence in code | Tests | Works? | SAM relevance |
|---|---|---|---|---|
| «interfaces for learners, educators, and parents» (paper/marketing) | modules thật: `learners/ teachers/ classrooms/ courses/ sessions/ supports/` — **grep "parent" trong .py = 0 file domain** | test_contract_coverage | learner/teacher CÓ; **parent KHÔNG có trong code** | ⭐ phát hiện quan trọng |
| family/multi-child model | không tìm thấy | — | không | — |

## Kết luận — trả lời «Parent View hữu ích vs surveillance dashboard?»
Không trả lời được từ repo này — VÀ ĐÓ CHÍNH LÀ DATA POINT: cả shortlist lẫn thay thế đều
**không có parent model thật trong OSS**. «Parent AI coach» đến nay chủ yếu là marketing
(đúng nghi vấn order đặt cho Open Alpha). ⇒ **Parent Coach của SAM (claim-gated + citation
+ MỘT-khuyến-nghị, đã BUILT) đang đi trước OSS** — differentiation thật, và không có mẫu để
chép: phải tự xây trên evidence (EEF parental engagement) + WAL-49. Phân loại: `REFERENCE`.
