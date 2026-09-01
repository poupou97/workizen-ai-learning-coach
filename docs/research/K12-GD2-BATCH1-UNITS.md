# WAL-74 — GĐ2 batch ①+②: ContentUnit atomic từ corpus thật (3 cuốn Toán)

**Ngày:** 2026-09-01 · 0 LLM · `tool/extract/extract_units.py` · output ngoài git (ADR-002)

## Số đếm được

**220 unit / 29 bài** (142 trang OCR): **17 RULE · 127 EXERCISE · 4 EXAMPLE · 72 SECTION_TEXT**.
Offset trang-in↔PDF hiệu chỉnh bằng header «Bài N» thật: +1, khớp **24/24**.
6 bài TOC thiếu số trang (OCR cột trang) — LOẠI VÀ ĐẾM, không đoán.

## Chất lượng kiểm mắt thường

17 RULE = đúng bộ quy tắc chuẩn của cả cuốn («Muốn cộng (hoặc trừ) hai phân số khác mẫu
số…» Bài 6 tr.21 → «Muốn tính diện tích hình tròn…» Bài 27 tr.110), mỗi cái truy được
bài + trang in. Lexicon phân vai KIỂM TRƯỚC trên corpus (17 «Muốn», 34 «Luyện tập»,
12 «Khám phá») — không bịa marker.

## Leak test tri-thức-tương-lai — TRÊN CORPUS THẬT (kế thừa luật WAL-41)

Học sinh đang Bài 6 hỏi «cộng»: không trần → 3 RULE (bài 6, 19, 26); **trần bài 6 →
1 RULE đúng (bài 6)**; «Muốn cộng hai số thập phân» (Bài 19) và «diện tích hình thang»
(Bài 26) **bị chặn đúng**. Phản ví dụ thật, không phải fixture.

## Bytes tầng unit (đo)

Một cuốn 220 unit: **184.320 B SQLite / 35.948 B gzip** (thô 162.096 B — text unit trung
bình ~740 B vì gom cả thân đoạn). ⇒ SGK lõi (toán+TV, ~100 cuốn tương đương) cỡ ~4-20MB
tuỳ định dạng — khớp trần ngoại suy 30MB gzip toàn corpus của WAL-83.

## Lỗi ghi thật + residual

- Heuristic «Muốn» có FP trong lời giải mẫu: «Muốn tính diện tích phần lát gạch
  xanh…» (tr.110) là câu lời giải, không phải quy tắc — ~1-2/17. Cần nhận diện KHUNG
  (box) từ layout để tách; ghi cho batch ②.
- SECTION_TEXT (72) là «chưa phân vai được» — nói thật, không đoán; đa phần là dẫn
  truyện khám phá + lời thoại nhân vật.
- Công thức toán vỡ dòng trong OCR (đã biết từ WAL-33) — text EXERCISE chứa mảnh số;
  formula-index là việc riêng.
- Batch ②: Toán 4 (2 tập) + Tiếng Việt 5 (concept #3) + nhận diện box.


---

## Batch ② (2026-09-01, cùng ngày) — Toán 4 hai tập + mapping concept

### Số đếm được (extractor v2: RULE tách CANON/CANDIDATE lúc flush, lexicon theo môn)

| Cuốn | Unit | RULE | EXERCISE | Ghi chú |
|---|---|---|---|---|
| Toán 5 t1 | 244 | 16 (+1 CAND=FP đã biết) | 125 | batch ① re-run v2, không regression |
| Toán 4 t1 | 379 | 1 («Khi đổi chỗ các số hạng…» — khuôn «Khi X thì Y») | 313 | «Muốn» = 0 THẬT ở học kỳ số tự nhiên |
| Toán 4 t2 | 430 | 9 — TRỌN bộ quy tắc phân số (cộng/trừ cùng-khác mẫu, nhân, chia) | 365 | chương phân số |
| **Tổng** | **1.053** | **26 + 1 CAND** | **803** | |

### Ba phát hiện tri thức (không phải phát hiện kỹ thuật)

1. **B57 Toán 4 (quy đồng) KHÔNG có câu quy tắc đóng khung** — dạy thuần bằng ví dụ mẫu
   («b) Ví dụ: Quy đồng mẫu số hai phân số…»). Khớp độc lập với WAL-41 (method lớp 4
   take-larger dạy qua ví dụ). Hệ quả pack: unit EXAMPLE là carrier tri thức chính của
   bài này — RULE-recall không thể là metric duy nhất.
2. **Dạy-lại-xuyên-lớp đo được**: quy tắc cộng-khác-mẫu xuất hiện CẢ Toán 4 B60 tr.77
   («Muốn cộng hai phân số khác mẫu số, ta quy đồng…») LẪN Toán 5 B6 tr.21 (hợp nhất
   cộng-trừ) — bằng chứng corpus cho cạnh cross-grade remediation.
3. **TV5 cấu trúc KHÁC HẲN toán** — extractor fail-closed đúng thiết kế («LỖI TO: không
   hiệu chỉnh được offset — dừng, không đoán»): header «Bài»+số nằm HAI DÒNG tách nhau
   (tiêu đề chen giữa, p14), TOC t1 rỗng ở GĐ1, section là chữ HOA đứng lẻ (ĐỌC/VIẾT).
   Cần luật boundary riêng cho sách văn — batch ③, không nhồi heuristic vội.

### Mapping RULE → concept (tất định, mức tự tin được)

**25/27 mapped** (`rule-concept-map.json`): 2 unmapped chính đáng (1 FP lời-giải + 1 OCR
vỡ đầu câu «Muốn tìm 3 của 12»). KHÔNG map SkillCase từ text quy tắc — đó là việc của
applicability trên BÀI TẬP (WAL-33). Bug thật vá kèm: **'đ' (U+0111) không phân rã NFD**
— mọi từ khoá chứa «đ» từng trượt im lặng («quy đồng», «đổi chỗ»); thay tay đ→d.

### Bẫy kỹ thuật ghi sổ

zsh `set -- $b` không tách từ (lần 2 trong dự án) → OCR 0 trang, lỗi bị `>/dev/null`
nuốt — chạy lại tường minh không loop. Marker TV («Đọc/Viết») nuốt bài toán bắt đầu
bằng «Viết…» nếu trộn lexicon — tách SECTION_TOAN/SECTION_TV.
