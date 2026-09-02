# So sánh scheduler: CURRENT vs FSRS-style vs Leitner (WAL-107)

**Trạng thái:** research-only (Founder §G). `review_schedule.dart` KHÔNG bị
sửa một dòng nào. Script: `tool/poc/scheduler_compare.py` (seed cố định).

## Kết quả (200 học sinh × 6 kỹ năng × 120 ngày mô phỏng)

| scheduler | reviews/skill | lapses (ôn TRỄ) | early (ôn SỚM) | retention@120 | #hằng số |
|---|---|---|---|---|---|
| CURRENT (7d ×2, trần 4 bước) | 7.4 | 7.45 | 0.00 | 0.181 | 4 |
| CURRENT-3d (CÙNG hình dạng, base 3d) | 11.2 | 5.29 | 0.42 | 0.590 | 4 |
| FSRS-style rút gọn | 29.5 | 25.48 | 0.33 | 0.668 | 5 |
| Leitner 1/3/7 | 21.4 | 0.00 | 3.47 | 0.955 | 1 |

## Đọc kết quả — ba điều, theo thứ tự chắc chắn giảm dần

1. **Đòn bẩy chính là THAM SỐ, không phải hình dạng.** Đổi đúng MỘT hằng số
   có tên (`baseInterval` 7d→3d, giữ nguyên SM-2-shape) đưa retention từ
   0.18 lên 0.59 và giảm lapses. Base 7d dài hơn độ bền ban đầu của kỹ năng
   MỚI (mô hình: 3-7 ngày) nên lần ôn đầu hầu như luôn trễ — và một lần trễ
   kéo vòng xoáy học-lại. Nếu có ngày muốn chỉnh lịch ôn, ứng viên số 1 là
   hằng số này — đúng khuôn ADR-004 (hằng số có tên, có lý do, thay được).
2. **FSRS-style KHÔNG tự thắng khi chưa hiệu chuẩn.** Bản rút gọn 5 tham số
   chưa khớp dữ liệu gọi ôn trễ liên tục (ước lượng S ≠ S thật). Đây chính
   là lý do Founder-đúng khi cấm auto-thay: FSRS chỉ có nghĩa khi fit trên
   trace THẬT — chưa có trace thật thì nó chỉ là 5 hằng số chưa ai bảo lãnh.
3. **Leitner rẻ-bảo-trì và chắc nhưng ĐẮT thời gian trẻ** (21 vs 7-11 lần
   ôn/kỹ năng) — «gọi ôn dày thì nhớ» không phải phát hiện, là chi phí.

## Giới hạn ghi thật

Ground truth là GIẢ ĐỊNH mô phỏng (quên mũ + spacing ×2.2 trần 60d, seed 42)
— mọi con số trên so sánh ĐƯỢC với nhau nhưng không phải đo lường trẻ thật.
Bước có nghĩa kế tiếp: chạy lại trên trace JSONL store thật (sau WAL-84 /
khi có dữ liệu WAL-49). KHÔNG đề xuất đổi tham số production từ mô phỏng này.
