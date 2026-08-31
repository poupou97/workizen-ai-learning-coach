# Phương pháp adaptive learning — so sánh và khuyến nghị V1

**Status:** RESEARCH · chưa implement gì.
**Kết luận trước:** V1 dùng **Mastery Learning + BKT rút gọn + Rule Engine**. Không DKT.

---

## So sánh

| | Mục đích | Dữ liệu cần | Giải thích được | Cold start | Cập nhật online | Hợp trẻ em | Hợp Curriculum Graph |
|---|---|---|---|---|---|---|---|
| **Mastery Learning** | học chắc rồi mới tiến | rất ít | ⭐⭐⭐ | ⭐⭐⭐ | ✅ | ⭐⭐⭐ | ⭐⭐⭐ |
| **BKT** | xác suất đã nắm 1 kỹ năng | ít | ⭐⭐⭐ | ⭐⭐ | ✅ | ⭐⭐⭐ | ⭐⭐⭐ |
| **IRT** | năng lực ↔ độ khó câu hỏi | **nhiều** (cần hiệu chuẩn item) | ⭐⭐ | ⛔ tệ | ~ | ⭐⭐ | ⭐ |
| **CAT** | chẩn đoán ít câu, nhiều thông tin | cần IRT trước | ⭐⭐ | ⛔ | ✅ | ⭐⭐ | ⭐ |
| **Knowledge Space Theory** | trạng thái tri thức khả dĩ | trung bình | ⭐⭐⭐ | ⭐⭐ | ✅ | ⭐⭐ | ⭐⭐⭐ |
| **DKT (deep)** | dự đoán từ chuỗi | **rất nhiều** | ⛔ hộp đen | ⛔ | ✅ | ⛔ | ⭐ |
| **Spaced repetition** | chống quên | ít | ⭐⭐⭐ | ⭐⭐⭐ | ✅ | ⭐⭐⭐ | ⭐⭐ |

## Vì sao KHÔNG chọn DKT cho V1

1. **Không có dữ liệu.** DKT cần hàng trăm nghìn lượt tương tác. Workizen có **0**.
2. **Không giải thích được.** §13 đòi Parent Coach nói *vì sao*. Một LSTM không nói được
   "vì 4/6 lỗi gần đây ở bước quy đồng" — mà đó chính là sản phẩm.
3. **Không audit được.** App cho trẻ em; §14 đòi mastery phải giải thích và phục hồi được.
4. Cold start tệ nhất trong bảng — đúng lúc ta cần nhất.

⇒ Không phải "deep learning kém", mà **sai công cụ cho giai đoạn này**. Xem lại khi có
telemetry thật, và chỉ khi rule engine chứng minh là không đủ.

## Vì sao IRT/CAT chưa dùng được — dù §10 muốn

§10 muốn *"5–10 câu thông minh hơn 50 câu đại trà"*. Đó chính là CAT. Nhưng CAT cần **IRT
đã hiệu chuẩn**, tức mỗi câu hỏi phải có tham số độ khó/phân biệt ước lượng từ **nhiều
học sinh thật**. Ta chưa có câu hỏi, chưa có học sinh.

⭐ **Đường đi được ngay:** chẩn đoán theo **prerequisite graph** thay vì theo IRT. Hỏi ở
nút *phía trên* trong chuỗi — sai thì lùi, đúng thì tiến. Tìm nhị phân trên đồ thị. Cần
`log₂(độ sâu chuỗi)` câu, không cần hiệu chuẩn gì. Với chuỗi phân số sâu ~4, tức **2–3
câu**. Đạt mục tiêu §10 mà không cần IRT.

## Khuyến nghị V1

```
Concept Graph (từ SGK, có provenance)
        +
BKT rút gọn cho mỗi (student, concept):  P(đã nắm)
   4 tham số: P(init) P(learn) P(slip) P(guess) — đặt theo tiên nghiệm, không học
        +
Rule/Policy Engine → Next Best Learning Action
        +
Spaced repetition cho REVIEW_DUE
```

Vì sao BKT rút gọn: cho ra **xác suất** (đáp ứng `confidence-aware` của §14), cập nhật
online sau từng lượt, giải thích được ("đúng 3 lần liên tiếp không gợi ý ⇒ P tăng"), và
chạy được với **một** học sinh. Tham số đặt tay trước, hiệu chuẩn sau khi có dữ liệu.

⚠️ `P(slip)` và `P(guess)` phải đặt riêng theo dạng bài: trắc nghiệm 4 lựa chọn có
`P(guess) ≈ 0.25` **theo cấu trúc**, bài tự luận thì gần 0. Dùng chung một hằng số là
đọc sai bằng chứng một cách hệ thống.

## Khoảng trống nghiên cứu

- Ngưỡng P để chuyển `LEARNING → MASTERED`
- Mô hình quên: hàm mũ theo thời gian hay theo số lần gặp lại
- Trọng số bằng chứng **transfer** (đúng ở dạng bài khác) — nghi là mạnh nhất, chưa có số
- Chuỗi tiên quyết **xuyên lớp** khi corpus lớp dưới chưa có
- Phân biệt `slip` (biết nhưng sai) với `misconception` (hiểu sai có hệ thống) từ lỗi thật
