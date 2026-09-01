# WAL-63 — False Trusted Problem benchmark: 6 chỉ số, cấm gộp thành "OCR accuracy"

**Ngày:** 2026-09-01 · **Nguyên tắc:** một MISS chỉ tốn một lần chụp lại; một biểu-thức-bịa-được-TIN
kéo sai cả chuỗi (ca → method → chẩn đoán → can thiệp → mastery). Tối ưu FTP trước, recall sau.

## Định nghĩa 6 chỉ số (TÁCH BIỆT — không có "OCR accuracy" tổng)

| # | Chỉ số | Định nghĩa | Đo được hôm nay? |
|---|---|---|---|
| 1 | **Detection Recall** | tỷ lệ TRANG chứa bài toán được phát hiện có ≥1 phân số/biểu thức ứng viên | ✅ pipeline hiện có |
| 2 | **Expression Assembly Recall** | tỷ lệ biểu thức thật được GHÉP TRỌN | ✅ (5-expr ground truth; trần op-token) |
| 3 | **Expression Correctness** | trong các biểu thức ghép được: đúng từng chữ số so với trang | ✅ đối chiếu tay/nhãn |
| 4 | **Fabricated Valid Expression Rate** | biểu thức KHÔNG có trên trang nhưng hợp lệ cú pháp, trên tổng biểu thức phát ra | ✅ — chỉ số HẠNG NHẤT cho mọi thay đổi pipeline |
| 5 | **Student Correction Rate** | tỷ lệ lần trẻ SỬA ở màn xác nhận | ⛔ cần màn WAL-52 chạy thật |
| 6 | **False Trusted Problem Rate** | tỷ lệ bài SAI nhưng lọt qua CẢ xác nhận (trẻ bấm nhầm "đúng rồi") | ⛔ cần sản phẩm + người thật; đây là chỉ số an toàn CUỐI |

## Số đo hiện hành (baseline, tất định — tái lập bằng tool/poc/*)

| Input | #2 Assembly Recall | #4 Fabricated (1-view) | #4 sau consensus ≥3/6 |
|---|---|---|---|
| Scan sạch | 5/5 | 0/5 (0%) | — |
| L1 | 2/5 | 3/5 phát ra (60%) | 2/4 (50%) |
| L2 | 1/5 | 1/2 (50%) | 0/1 (0%) |
| L3 | 0/5 | 5/5 (100%) | 2/2 (100%) |

## Luật sử dụng
1. Mọi PR đổi pipeline perception PHẢI báo đủ #1–#4 per-level; #4 không được tăng.
2. #5/#6 kích hoạt khi slice camera chạy; #6 ≈ 0 là điều kiện để perception được cấp quyền
   ghi LearningEvidence **sau xác nhận** — không bao giờ trước.
3. Ground truth mở rộng dần (hiện 5 biểu thức/3 trang — đủ cho hướng, chưa đủ cho kết luận
   tinh; thêm trang có nhãn tay là việc rẻ, làm khi chạm ngưỡng quyết định).
