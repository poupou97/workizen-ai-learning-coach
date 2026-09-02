# KT-PSP-AUDIT — KT-PSP-25/StatusKT (paper) + Oia-10/PSKT (repo lân cận)

**Verify canonical (bắt buộc §9):** KT-PSP-25/StatusKT **KHÔNG có repo công bố** — chỉ paper
arXiv 2512.00311 (đã xác lập ở WAL-55; org UpstageAI/KT-PSP là đoán sai → 404).
Audit code thực hiện trên **PSKT** (ACM MM'24, cùng dòng «KT từ quá trình giải»).
**PSKT SHA:** c1aa722 · 2024-12-21 · **KHÔNG có LICENSE** ⇒ all-rights-reserved: ĐỌC ý tưởng, cấm dùng mã.
**Chạy được?** `NOT WORTH RUNNING`: `.cuda()` hardcode trong forward (Q4_model.py) — không chạy Mac/mobile; không license.

## Claim vs code

| Claimed | Evidence in code | Tests | Works? | SAM relevance |
|---|---|---|---|---|
| KT từ problem-solving process | Input thật = `user_id, problem_id, skill_id, correct, time_stamp` (README) — **KHÔNG có step/reasoning nào**; "process" = chuỗi thời gian + interval | không có test | mô hình train được (theo paper) | Ý tưởng CAO, code THẤP |
| Lý thuyết → kiến trúc | `problem-solving theory/Relationship….md` + gates trong forward: `ks` (knowledge state) / `ka` (knowledge acquisition) tách nhau; `Q_Diff`/`Q_alpha` = độ khó/độ phân biệt học từ embedding | — | — | pattern ĐÁNG HỌC: tách «đang biết» vs «vừa học thêm» thành 2 cổng |
| Forgetting | `TD = (TS[1:]−TS[:-1])//60`, clamp 1 tháng, embedding interval vào update | — | — | CAO: xác nhận hướng «thời gian là feature của update» — nhưng WAL đã QUYẾT tách F5 khỏi pMastery (Founder) ⇒ dùng cho REVIEW/retrievability, không trộn vào belief |

## Trả lời câu hỏi order
> *"SAM có thể suy yếu-khái-niệm từ steps/reasoning mà không cần model nặng không?"*

**CÓ — và SAM đang làm rồi bằng đường tất định**: chính dòng KT-PSP chỉ dùng
đáp-án+timestamp (không steps); trong khi WAL đã có lineage GIÀU HƠN mức event
(support/policy/prior + 7 EvidenceKind + attributeFailure/probe). Model nặng kiểu PSKT:
(a) cần dataset lớn (ASSIST/EdNet — EdNet CC-NC cấm sản phẩm), (b) CUDA, (c) không giải
thích được cho phụ huynh. **Kết luận: `REFERENCE`** — mượn 2 ý (ks/ka tách cổng; interval
là tín hiệu) làm giả thuyết cho policy tương lai, KHÔNG POC model.
