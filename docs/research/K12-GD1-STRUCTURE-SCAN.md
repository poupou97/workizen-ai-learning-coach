# WAL-73 — GĐ1: quét cấu trúc TOÀN BỘ corpus SGK lớp 1–12

**Ngày:** 2026-09-01 · **Chạy:** 61 phút · 0đ · 0 LLM (Apple Vision OCR + parse tất định)
**Mã:** `tool/extract/structure_scan.py` (+ `parse_structure.py` v3) · output
`poc-out/graph/structure-scan.json` (NGOÀI git — ADR-002, kể cả tên bài học là phái sinh SGK)

## Số ĐẾM được (không ước)

| | |
|---|---|
| Cuốn quét | **531** (12 lớp; lớp 10-12 ~80 cuốn/lớp vì chuyên đề + tổ hợp) |
| Tổng trang | **62.729** |
| Cuốn ra bài thật | **366 (69%)** — **7.199 bài học** có tên + trang in, 3.351 chương/chủ đề |
| 0-bài (TOC thấy, quy ước tên chưa phủ) | 125 — chủ yếu tiếng Trung (16), HĐTN (12), chuyên đề (11), Mĩ thuật THPT |
| NO_TOC | 40 — gần như toàn ngoại ngữ (Nhật/Pháp/Đức/Hàn: mục lục «Contents», bố cục khác) |

## Bài học tự-bác trong chính phiên (giữ làm chứng tích)

Bản v2 («Bài N» duy nhất) báo «463/531 OK» — nhưng đào sâu: chỉ **224 cuốn (42%)** thật sự
ra bài; 239 cuốn «OK» là GIẢ (TOC thấy, 0 bài — đúng loại lỗi «OCR coverage ≠ knowledge
coverage» Founder cảnh báo). v3 thêm Chuyên đề/Chủ đề/Tuần/Unit ⇒ 366 cuốn thật, 7.199 bài
(+56%), re-parse chỉ 9s nhờ OCR cache. **Luật rút ra: «status OK» phải định nghĩa bằng
SẢN LƯỢNG (≥1 bài), không bằng «tìm thấy trang mục lục».**

## Tầng structure trong Knowledge Pack — ĐO THẬT toàn corpus

7.199 bài + 531 book + FTS contentless: **899KB SQLite / 113KB gzip-JSON** (124 B/bài).

## Mật độ text (cho ngoại suy GĐ2) — đo trên 2.301 trang OCR thật

1.472 B text/trang · gzip ratio 0,33 ⇒ tầng text TOÀN corpus ≈ **92MB thô / 30MB gzip**
[NGOẠI SUY TỪ MẪU ĐO — caveat: mẫu là trang đầu/cuối sách, mật độ trang thân bài có thể khác;
GĐ2 mẫu sẽ đo lại]. Kể cả vậy: nằm êm trong ngân sách «app lớn chấp nhận được» của ADR-006.

## Residual (địa chỉ rõ)

165 cuốn chưa ra bài (125+40) — ngoại ngữ & định dạng đặc thù; ưu tiên thấp cho lõi SAM
(Toán/TV/KH đã phủ) nhưng ĐÃ ĐẾM, không giấu · «Nội dung bài» chưa trích (đó là GĐ2) ·
tên bài chưa hiệu đính chính tả OCR.
