# WAL-41 — RAG retrieval POC: kết quả đo + 2 falsification (§6, §2 review Founder)

**Ngày:** 2026-09-01 · **Công cụ:** `tool/poc/rag_retrieval_poc.py` (tất định, tái lập)
**Corpus:** 12 ContentUnit tay-biên từ trang ĐÃ ĐỌC (Toán 4 tr.62 · Toán 5 tr.11,20,38-40 ·
TV5 tr.65-66 · Toán 9 tr.119 làm bẫy tương lai) · 6 query có ground truth stage-aware,
gồm 2 bẫy tri-thức-tương-lai THẬT (mục tr.40 với học sinh đang ở tr.39; glossary lớp 9 với lớp 5).

## Kết quả

| Variant | Source Recall | Future Leak | Top-1 đúng |
|---|---|---|---|
| metadata (không rank) | 6/6 | 0 ⚠️ **may mắn thứ tự** | 3/6 |
| **metadata + BM25** | 4/6 | **1 💥 RÒ** | 2/6 |
| **graph (scope mục)** | **6/6** | **0 (thật)** | 3/6 |
| graph + BM25 + ngưỡng | 4/6 | 0 + fail-closed đúng | 2/6 |

## Bốn kết luận đo được

1. **"Graph quyết ĐÂU" SỐNG SÓT falsification — bằng số, không tu từ.** `metadata+bm25` rò
   ngay bẫy #1: query "so sánh 76,3 và 76,30" → BM25 xếp t5-40-rule (mục CHƯA HỌC) hạng nhất
   vì khớp text nhất. Metadata-không-rank "0 leak" chỉ nhờ MAY thứ tự chèn (t5-40 nằm trong
   scope, rớt top-3 do order — không phải do chính sách). Chỉ scope theo graph (bài đã dạy +
   prerequisite, mịn tới MỤC) chặn thật.
2. **Xuyên lớp là bắt buộc:** query "quên dạng chia hết" @lớp 5 cần unit LỚP 4 tr.62 —
   scope "bài hiện tại" chết; graph prerequisite (t5-bai6 → t4-bai57, cạnh ĐÃ CÓ trong domain)
   trả đúng. Thesis không mất bằng chứng hữu ích *khi graph chứa đủ láng giềng tiên quyết*.
3. **Fail-closed bằng ngưỡng HOẠT ĐỘNG nhưng CÓ GIÁ — nay đo được:** "căn bậc hai" @lớp 5 →
   `[]` (đúng: NO_EVIDENCE thay vì trả unit không liên quan như biến thể không-ngưỡng);
   nhưng MIN_SCORE=2.0 làm rớt 2 unit thật (t5-39-rule, tv5-66-rule). Ngưỡng là tham số cần
   khớp bằng dữ liệu — KHÔNG chốt hằng số; corpus 12 unit quá nhỏ để tune.
4. **Granularity (§2 review): "Mục" là CONTAINER, KHÔNG phải đơn vị tối thiểu.** Hàng rào
   chống rò #1 hoạt động CHÍNH vì tr.39 và tr.40 là unit RIÊNG (atomic theo vai trò
   RULE/EXAMPLE/EXERCISE, gắn mục làm container). Nếu unit = cả bài 11 thì hoặc rò tr.40
   hoặc mất trọn bài. Citation precision + Method-permission filter cũng cần vai-trò-mức-atomic.
   ⇒ SỬA kết luận RAG doc §2: đơn vị truy xuất tối thiểu = **atomic pedagogical unit
   (role-level)**; Mục/Section = container + ranh giới taught/untaught.

## Giới hạn nói thẳng
Corpus 12 unit/6 query — đủ cho HƯỚNG, không đủ cho số tinh (đặc biệt tune ngưỡng). BM25
tokenize whitespace tiếng Việt — chưa xử lý từ ghép. Vector: CHƯA thêm — chưa có failure nào
mà vector giải quyết (đúng luật "chỉ thêm khi giải một lỗi đo được"); failure hiện tại
(threshold-recall) là bài của NGƯỠNG, không phải của biểu diễn.
