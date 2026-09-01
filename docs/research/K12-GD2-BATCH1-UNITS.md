# WAL-74 — GĐ2 batch ①→④: ContentUnit + EXERCISE→SkillCase + SCALE GATE tự động

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


---

## Batch ③ (cùng ngày) — Tiếng Việt 5 hai tập, extractor RIÊNG theo cấu trúc đã đo

`extract_units_tv.py` — viết SAU khi đo (69 header «Bài» 2-dòng, 5 section chữ-HOA-đứng-lẻ,
16 «Ghi nhớ»); trang in lấy từ số chân trang (GĐ1 không có TOC dùng được cho sách này);
header mồ côi + trang thiếu số in ĐẾM VÀ BÁO (7 + 46), không đoán.

| Cuốn | Unit | RULE (Ghi nhớ) | EXERCISE | header ghép được |
|---|---|---|---|---|
| TV5 t1 | 589 | 3 | 469 | 32 (mồ côi 3) |
| TV5 t2 | 560 | 13 | 434 | 30 (mồ côi 4) |

**16 RULE = đúng tri thức ngữ pháp/tập làm văn lớp 5**: đại từ, câu đơn/câu ghép, nối vế
bằng kết từ/cặp từ, liên kết câu (lặp từ · kết từ · đại từ), viết hoa danh từ/tên nước
ngoài, cấu trúc đoạn văn (cảm xúc/tán thành/phản đối). **Chuỗi «liên kết câu» (b9→b11→b13)
chính là nguyên liệu concept #3 xuyên-domain** (SKILLCASE-CONCEPT-3) — tiến trình case
tự nhiên: lặp-từ → kết-từ → đại-từ.

**TỔNG CORPUS GĐ2 sau 3 batch: 2.202 unit / 5 cuốn** (42 RULE · 1.706 EXERCISE).
Residual: 2 RULE TV thiếu số trang in (chân trang OCR miss) — id vẫn truy pdf-page;
box-detection và mapping case vẫn là batch ④.


---

## Batch ④ (cùng ngày) — EXERCISE→SkillCase + gate tự động: **SCALE GATE ĐÃ XANH**

### Phát hiện chặn đường: text đã gom dòng cho **0%** biểu thức parse được

Đo trước khi viết luật: 803 bài tập Toán, regex `a/b ± c/d` khớp **0**. Không phải lỗi
OCR — sách in phân số **XẾP CHỒNG DỌC**, OCR trả token số rời (tử ở y, mẫu ở y+0,02,
cùng cột x). ⇒ mapping bài tập KHÔNG THỂ chạy trên text; phải dựng lại từ HÌNH HỌC.

### `rebuild_fractions.py` — dựng phân số tất định từ bbox

Luật: hai token SỐ cùng cột (|dx| ≤ 0,035) cách nhau ≤ 0,03 theo y ⇒ tử/mẫu; hai phân số
cùng hàng cách ≤ 0,22 với toán tử ở giữa ⇒ biểu thức. Ca ⇒ **đúng luật `fractionCase` của
kernel** (không viết luật song song). Mọi thứ khác ⇒ không dựng.

**Kết: 34 biểu thức**, mỗi cái mang `status: INFERRED` (dựng từ hình học ≠ nguyên văn).

### Hai FP thật bị bắt và vá (không tắt gate)

1. **Ghép hai bài cạnh nhau**: không siết khoảng cách thì `a)` và `b)` cùng hàng dính thành
   biểu thức ma («10/15 + 11/8»). Siết 0,22 ⇒ 53→38.
2. ⭐ **CHƯƠNG TRÌNH LỌC NHẬN DẠNG**: B53 «Khái niệm phân số» tr.50 sinh «2/3 − 3/5» —
   nhưng sách **chưa dạy phép trừ phân số** ở bài đó ⇒ gần chắc là gạch nối bị đọc thành
   phép tính. Thêm luật: không nhận phép cộng/trừ phân số TRƯỚC bài đầu tiên dạy nó
   (B60 lớp 4, đọc từ TOC thật) ⇒ loại 4 ca. Đây là chương trình lọc nhận dạng, không
   phải nhận dạng lọc chương trình.

### KIỂM CHÉO NGOẠI VI (bằng chứng mạnh nhất của batch)

B60 tr.74-76 = phần «cộng/trừ phân số **CÙNG** mẫu» → **8/8 dựng ra `denominator-equal`**;
tr.78+ = phần «**KHÁC** mẫu» → chuyển sang divisible/non-divisible. Luật hình học + luật
case của kernel, kiểm chéo với **cấu trúc bài học của sách** — khớp, không phải tự-nói-tự-nghe.

### `verify_corpus_gates.py` — SCALE GATE thành lệnh chạy được

11 check trên DỮ LIỆU THẬT (suite Dart giữ luật trên fixture vì corpus ở ngoài git):
G1 provenance (assertion đủ, RULE=EXPLICIT, truy được trang) · G2 chống rò xuyên-sách,
xuyên-lớp và trong TV5 · G3 mapping (INFERRED, khớp sự thật bài học, không mẫu 0, không
vượt phạm vi, không sinh phép tính chưa dạy) · G4 trung thực (unmapped giữ nguyên).
**🟢 11/11 XANH — Founder Delta §7/§13 scale gate ĐÃ MỞ.**

### Coverage nói thẳng

34 biểu thức = **17% bài tập trong chương phân số (197)**, **2% toàn bộ 1.706 bài tập** —
phần lớn bài tập là đọc/tìm/chọn/viết, không chứa biểu thức nào. Không đoán để nâng số.
Residual: bài tập dạng cột dọc/có hình, phép nhân-chia phân số, số thập phân — mở rộng
luật khi cần, mỗi lần kèm kiểm chéo bài học tương ứng.
