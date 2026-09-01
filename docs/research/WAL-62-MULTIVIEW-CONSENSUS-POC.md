# WAL-62 — Multi-view consensus POC: verdict **PARTIALLY FALSIFIED**

**Ngày:** 2026-09-01 · **Công cụ:** `tool/poc/multiview_consensus_poc.py` (tất định) · dữ liệu L1-L3 của PHONE-SIM
**Giả thuyết:** đồng thuận đa biến thể tiền xử lý giảm Fabricated-Valid-Expression mà không giết recall.

## Thiết kế
6 view độc lập / trang: orig · autocontrast · denoise+sharpen · binarize (quang học) + scale×0.6 · scale×1.5
(hình học). Mỗi view: OCR → ghép biểu thức. Đồng thuận = biểu thức xuất hiện ở ≥k view.

## Kết quả

| Mức | 1-view (orig) | Đồng thuận ≥2/6 | Đồng thuận ≥3/6 |
|---|---|---|---|
| L1 | recall 2/5 · bịa 3 | 2/5 · **bịa 5** ⚠️ | 2/5 · bịa 2 |
| L2 | 1/5 · bịa 1 | 1/5 · **bịa 0** ✅ | 1/5 · bịa 0 ✅ |
| L3 | 0/5 · bịa 5 | 0/5 · bịa 5 | 0/5 · **bịa 2** |

## Bốn kết luận

1. **PARTIALLY FALSIFIED**: đồng thuận ngưỡng chặt giảm bịa ~50% (3/1/5 → 2/0/2) nhưng KHÔNG đạt
   FTP≈0 — lỗi tương quan sâu sống sót (`1/7 + 43/60` đạt ≥3/6 phiếu ở L3; `18/72 − 5/15` ở L1).
   Đúng rủi ro "đồng thuận giả" Founder cảnh báo: view quang học chia sẻ CÙNG hình học ⇒ lỗi
   GHÉP-THEO-TRỤC-Y tương quan; view đổi scale khử được một phần, không hết.
2. **Ngưỡng quan trọng hơn số view**: thêm view ở ngưỡng lỏng (≥2/6) làm bịa TĂNG ở L1 (3→5) —
   mỗi view mới góp thêm ứng viên rác đủ tìm bạn trùng.
3. **Đồng thuận không bao giờ cứu recall** (không thêm được cái không view nào thấy) — recall là
   bài của rectification/pre-capture, không phải của consensus.
4. **Hệ quả kiến trúc giữ nguyên bất biến §11**: consensus (+plausibility) chỉ là TIỀN-LỌC để giảm
   gánh xác nhận; **màn "tớ đọc được thế này" (WAL-52) vẫn là ranh giới an toàn duy nhất đáng
   tin** — UNCONFIRMED PERCEPTION không vào LearningEvidence.

## Việc mở ra (không tự làm ngay)
View sửa-phối-cảnh thật (corner detection) — ứng viên khử tương quan mạnh nhất, đo ở vòng sau;
kết hợp plausibility filter theo khối lớp (WAL-63 harness đã đo được Fabricated Rate làm chuẩn).
