# WAL-74 — GĐ2 batch ①: ContentUnit atomic từ Toán 5 tập một (corpus thật)

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

Một cuốn 220 unit: **~103KB SQLite / ~14KB gzip** (thô 44KB) ⇒ ~SGK lõi cấp 1 (toán+TV
~50 cuốn) cỡ vài MB — khớp ngoại suy 30MB toàn corpus của WAL-83.

## Lỗi ghi thật + residual

- Heuristic «Muốn» có FP trong lời giải mẫu: «Muốn tính diện tích phần lát gạch
  xanh…» (tr.110) là câu lời giải, không phải quy tắc — ~1-2/17. Cần nhận diện KHUNG
  (box) từ layout để tách; ghi cho batch ②.
- SECTION_TEXT (72) là «chưa phân vai được» — nói thật, không đoán; đa phần là dẫn
  truyện khám phá + lời thoại nhân vật.
- Công thức toán vỡ dòng trong OCR (đã biết từ WAL-33) — text EXERCISE chứa mảnh số;
  formula-index là việc riêng.
- Batch ②: Toán 4 (2 tập) + Tiếng Việt 5 (concept #3) + nhận diện box.
