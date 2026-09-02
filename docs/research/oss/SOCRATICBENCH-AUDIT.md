# SOCRATICBENCH-AUDIT — GiovanniGatti/socratic-bench

**SHA:** 5bf0f8f · 2025-10-21 · LICENSE: có · Python, pydantic, kiến trúc sạch
**Chạy được?** `PARTIAL` — cần API key LLM cho pipeline; datasets đọc được ngay (đã đọc).

## Claim vs code

| Claimed | Evidence in code | Tests | Works? | SAM relevance |
|---|---|---|---|---|
| Sinh hội thoại Socratic (teacher×student đều LLM) | `stages.py`: `SeedStage → ChatStage(max_interactions=16) → EvaluationStage` — pipeline stage có `counters()` đếm được | có thư mục tests | có | CAO |
| Judge hiệu-chỉnh | `agents.py:509 class Judge(ABC)` — system_prompt + rubric + `evaluate() → (feedback, pass/fail | None)`; **None = undecidable là giá trị hợp lệ** | — | — | RẤT CAO — «không phân xử được» là first-class, trùng doctrine UNKNOWN của WAL |
| Human-eval | `datasets/human-eval/`: expert-1 (990KB) + expert-2 (911KB) + agreement.json (338KB) + seed-dataset | — | dữ liệu THẬT trong repo | κ≈0.50 giữa 2 expert (paper) — «dạy tốt» khó đồng thuận NGAY GIỮA NGƯỜI |

## Kết luận — trả lời «copy gì làm METHODOLOGY, không phải product code»
**`ADOPT PATTERN` (methodology):**
1. **Pipeline 3 tầng tách rời** Seed→Dialogue→Judge với counters — SAM Tutor Eval nên cùng khung.
2. **Judge trả về `None/undecidable`** — đừng ép nhị phân.
3. **Calibrate judge với human labels TRƯỚC khi tin** — và công bố κ. Với SAM: label bởi giáo viên VN.
4. Seed từ dataset có metadata (chuẩn bị: seed từ corpus SGK + QĐ2422 outcome — SAM có sẵn).

**Rủi ro ghi thẳng:** LLM-as-judge lệch hệ thống; student mô phỏng ≠ trẻ VN lớp 2 (ngôn ngữ,
kiên nhẫn, bàn phím); κ=0.50 nghĩa là mọi con số eval PHẢI mang khoảng tin cậy, không phải điểm tuyệt đối.
