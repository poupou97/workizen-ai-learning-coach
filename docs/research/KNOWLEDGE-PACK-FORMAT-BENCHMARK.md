# WAL-83 — SAM Knowledge Pack: benchmark định dạng + A/B FULL vs MODULAR (vòng 1)

**Ngày:** 2026-09-01 · **Maturity:** POC MEASURED (liệu thật, scale nhỏ) ·
Mã: `tool/pack/compile_pack.py` · số liệu: `poc-out/pack/report.json` (ngoài git)

## Liệu đầu vào (THẬT, không bịa)

267 AI outcome (QĐ 2422) · 12 ContentUnit tay-biên Toán 4-5 (WAL-41) · 18 bài Toán 5 ·
bảng book GĐ1 (đang chạy — vòng này mới có mẫu lớp 5, ghi thật).

## Số đo chốt định dạng (ĐO, không ước)

| Biến thể (267 outcome, trang 512B) | Bytes | Ghi chú |
|---|---|---|
| SQLite bảng thô, không index tìm kiếm | 135.680 | nền |
| + FTS5 **contentless, detail=none** | **157.184** | **+21,5KB — match đa-từ chạy; mất phrase-query/highlight-nội-bộ (đọc text từ bảng nền thì vẫn highlight được)** |
| + FTS5 detail=none (có content) | 277.504 | +142KB |
| + FTS5 mặc định | 328.704 | +193KB — index đắt hơn cả dữ liệu |
| JSON + gzip -9 (đối chứng) | 27.599 | 12× nhỏ hơn SQLite full-FTS |

**Trang 4KB mặc định phí 8× cho pack nhỏ**: mỗi module SQLite gánh ~90KB overhead cố định
→ 512B đưa module lớp về ~35-40KB.

## A/B FULL vs MODULAR — kết quả vòng 1 (KHÔNG mặc định modular thắng — và đúng là nó THUA)

| | FULL (1 tệp) | MODULAR (core + 12 lớp) |
|---|---|---|
| Tổng bytes (512B page) | ~349KB | 462KB (**+32% overhead nhân bản schema/FTS ×13 tệp**) |
| HS lớp 5 cần tải | 349KB | 54KB (core 13KB + g05 41KB) |
| Độ phức tạp update | 1 tệp, 1 version | 13 tệp, ma trận version |
| Latency truy vấn | 0,05ms / FTS 0,04ms | tương đương |

**Kết luận vòng 1:** ở scale hiện tại **FULL thắng mọi mặt trừ bytes-tải-lần-đầu**.
Latency vô nghĩa ở scale này (<0,1ms cả hai).

## Quyết định định dạng (chốt sớm đúng AC) + ngưỡng lật

1. **Tầng content lớn** (GĐ2+: ContentUnit full-text): SQLite + **FTS5 contentless
   detail=none**, trang 512B–1KB — index rẻ 9×, đọc partial không cần nạp cả pack vào RAM.
2. **Tầng graph/curriculum nhỏ** (outcome, edges, mã): **gzip JSON nạp thẳng vào RAM**
   — 27,6KB cho cả khung AI 12 lớp; SQLite không mua được gì ở tầng này.
3. **FULL vs MODULAR: GIỮ FULL** cho tới khi một module lớp vượt **~10MB** nội dung thật
   (ngưỡng đề xuất từ chi phí tải/two-tier update; là GIẢ THUYẾT V1 — đo lại bằng GĐ2).
   Modular chỉ trả giá xứng khi content ≫ overhead — hiện overhead ≫ content.
4. Embeddings: **vẫn KHÔNG** (chưa có phép đo retrieval fail nào — luật ADR-006 giữ).

## NGOẠI SUY 1–12 — ĐÃ ĐIỀN từ số GĐ1 (đo, không ước từ PDF)

| Tầng | Số đo | Ghi chú |
|---|---|---|
| Curriculum (AI 2422) | 27,6KB gzip | ĐO — cả khung 267 outcome |
| Structure (7.199 bài, 531 cuốn, FTS) | **899KB SQLite / 113KB gzip** | **ĐO THẬT toàn corpus GĐ1** — 124 B/bài |
| Text/ContentUnit toàn K-12 | ≈ **92MB thô / 30MB gzip** | NGOẠI SUY từ 2.301 trang OCR đo (1.472 B/trang × 62.729 trang × gzip 0,33); GĐ2 mẫu đo lại |
| Text MỘT lớp | ≈ 7,7MB thô | dưới ngưỡng lật modular 10MB ⇒ **FULL vẫn đứng** (kể cả SGV; SGK thuần còn nhỏ hơn) |

Kết cho ADR-006: FULL pack toàn K-12 (curriculum + structure + text nén) ≈ **30–35MB**
— dư sức local-first, trong ngân sách «app lớn chấp nhận được» của Founder (100MB–2GB+).

## Residual

GĐ2 mẫu nhỏ → đo mật độ ContentUnit/trang thật rồi điền ngoại suy + kiểm ngưỡng 10MB ·
tầng formula-index chưa đo (chưa có corpus công thức trích) · ký/delta update = WAL-85.
