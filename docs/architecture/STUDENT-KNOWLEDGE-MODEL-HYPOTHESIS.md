# Student Knowledge Model — giả thuyết

**Status:** HYPOTHESIS · chưa implement · bám bằng chứng đo được từ POC Toán 5 KNTT.

> Hai hệ **tách rời**: Textbook Knowledge Base (nội dung, có thể bị thay/xoá vì lý do
> pháp lý) và Student Knowledge Model (dữ liệu của trẻ, phải sống sót qua việc đó).
> Ranh giới này là `KnowledgeContentProvider` — xem `BASE-CLONE-PLAN.md` §15.

---

## ⭐ Ba phát hiện từ corpus làm đổi thiết kế

### ① Root gap có thể nằm NGOÀI lớp hiện tại

Đo trên 53 trang Toán 5 KNTT: `quy đồng` xuất hiện ở trang 12, 20, 21 — nhưng trang 12
là **bài luyện tập** (*"Quy đồng mẫu số các phân số."*), không phải trang dạy. Bài 3 tên
là *"**Ôn tập** phân số"*.

⇒ Toán 5 **ôn** quy đồng, **không dạy**. Nó được dạy ở **lớp 4**.

**Hệ quả:** thuật toán root-gap của §5 sẽ tìm ra một lỗ hổng mà corpus lớp 5 **không có
nội dung để vá**. Prerequisite graph **bắt buộc xuyên lớp**, hoặc Tutor sẽ chẩn đoán đúng
rồi bó tay. Đây là lý do kỹ thuật để mở rộng corpus — không phải "càng nhiều càng tốt".

### ② Từ vựng phải khớp SÁCH, không khớp toán học

`phân số bằng nhau` — **0 lần** trong 53 trang. Sách dùng `rút gọn` và `phân số tối giản`.
Một prerequisite do LLM đặt tên "phân số bằng nhau" là **thuật ngữ đứa trẻ chưa gặp**.

⇒ `Concept` phải mang **`textbook_term`** (từ sách) tách khỏi `canonical_name` (của ta).

### ③ Method gắn với LỚP, không gắn với khái niệm

Toán 5 KNTT dạy mẫu số chung = **tích hai mẫu số**; `BCNN` xuất hiện **0 lần**.
Cùng một concept "quy đồng", lớp khác sẽ dạy method khác.

⇒ `Method` là entity riêng, gắn `(concept, grade, book_series)` — không gắn concept suông.

---

## Mô hình đề xuất

```
Student ─┬─ ConceptState ── Concept        (khoá ngoài sang Curriculum Graph)
         └─ Evidence[]   ── Attempt/Hint/Error
```

`ConceptState` **không lưu nội dung SGK** — chỉ lưu `concept_id` + trạng thái học. Xoá
corpus thì graph này còn nguyên.

### Mastery state

`UNKNOWN · INTRODUCED · LEARNING · NEEDS_PRACTICE · MASTERED · REVIEW_DUE`

⚠️ Kèm **`confidence`** riêng. `MASTERED` với 1 bằng chứng khác hẳn `MASTERED` với 12 —
gộp hai thứ vào một nhãn là mất chính thông tin cần để quyết định ôn hay tiến.

⭐ §14 an toàn: state gắn vào **concept**, không gắn vào **đứa trẻ**. Không có trường nào
mô tả học sinh; chỉ có trường mô tả *quan hệ giữa học sinh và một khái niệm tại một thời
điểm*. Câu hệ thống được phép nói: *"khái niệm X cần luyện thêm"*. Không bao giờ:
*"con yếu Toán"*.

### Learning evidence

| Nhóm | Trường |
|---|---|
| Kết quả | `correct` · `error_type` · `misconception_id?` |
| Nỗ lực | `attempts` · `hint_count` · `hint_depth` · `self_corrected` |
| Thời gian | `response_ms` · `at` |
| Ngữ cảnh | `exercise_id` · `concept_ids` · `difficulty` · `source` (camera/quest/diagnostic) |

**Một câu đúng KHÔNG phải MASTERED.** Đúng sau 3 gợi ý sâu là bằng chứng *yếu*; đúng ở
một dạng bài **khác** (transfer) là bằng chứng *mạnh*. Trọng số phải phản ánh điều đó.

## Chưa quyết (research gap)

Hàm cập nhật mastery · ngưỡng chuyển state · mô hình quên · trọng số transfer ·
độ dài lịch sử cần giữ. Xem `ADAPTIVE-LEARNING-METHODS-RESEARCH.md`.
