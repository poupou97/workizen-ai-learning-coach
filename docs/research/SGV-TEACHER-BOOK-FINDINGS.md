# SGV (sách giáo viên) — điều tra chứng cứ

**Nguồn:** `04-sgv-toan-4.pdf` (290 trang) · **mẫu OCR: 35 trang**, rải khắp sách để
tránh thiên lệch về chương phân số. LLM calls: 0.

---

## ⭐ KẾT QUẢ 1 — SkillCase được SÁCH GIÁO VIÊN xác nhận, `SOURCE_STATED`

SGV Bài 57, nguyên văn:

> *"Yêu cầu chủ yếu của tiết học: … HS hiểu được và biết cách quy đồng mẫu số hai phân số
> **(trường hợp có một mẫu số chia hết cho mẫu số còn lại)**"*
>
> *"Bài 1: Củng cố cách quy đồng mẫu số của hai phân số theo mẫu **(có một mẫu số chia
> hết cho mẫu số còn lại)**."*
>
> *"…dạng bài tập 3 (quy đồng mẫu số của nhiều phân số **trường hợp có một mẫu số chia
> hết cho các mẫu số còn lại**, ở bài này là ba phân số)"*

Tác giả chương trình dùng đúng chữ **"trường hợp"** để **giới hạn phạm vi bài học**.
`SkillCase` không phải abstraction tôi nghĩ ra — tôi tìm lại một cấu trúc họ đang dùng.

### Phép thử bác bỏ: "trường hợp" có phổ biến không, hay chỉ riêng quy đồng?

| | |
|---|---|
| trang SGV đã OCR | 35 |
| số lần cụm *"trường hợp"* | **13** |
| số chủ đề khác nhau | **≥5** — tr.75 · 105 · 190 · 216 · 217/218 · 225 |

⇒ Phổ biến khắp sách, **không** riêng phân số. Bằng chứng ủng hộ SkillCase là **cấu trúc
sư phạm tái diễn**. ✅ **KEEP.**

## ⭐ KẾT QUẢ 2 — mô hình của tôi quá THÔ, thiếu hai tầng

**① `Tiết` nằm dưới `Lesson`.** Bài 57 gồm *Tiết 1* (dạy ca chia hết) và *Tiết 2* (luyện
tập + mở rộng lên **ba phân số**). Mỗi tiết có mục tiêu riêng, ghi thẳng trong SGV. Mô
hình hiện tại chỉ có Lesson ⇒ mất mức chi tiết mà chính sách dùng để tổ chức dạy.

**② Ca có "kích thước", không chỉ có "điều kiện".** Cùng điều kiện *chia hết*, SGV tách:
2 phân số → 3 phân số → *"tuỳ điều kiện của lớp, GV có thể cho HS quy đồng mẫu số của
**bốn** phân số"*. Đó là **cùng ca, độ khó tăng dần**, không phải ca mới.

**③ `rút gọn rồi quy đồng` là HỢP THÀNH phương pháp**, không phải ca mới:
*"Bài 2: Bổ sung dạng bài rút gọn rồi quy đồng mẫu số"*. Mô hình cần biểu diễn được
"phương pháp A rồi phương pháp B".

## ⭐ KẾT QUẢ 3 — mục tiêu học tập là `SOURCE_STATED`, lấy được rẻ

Mỗi tiết mở đầu bằng *"Yêu cầu chủ yếu của tiết học: …"* — trích dẫn nguyên văn được,
có trang. Đây là `learning_objective` chất lượng cao mà **SGK không có**.

---

## ❌ KẾT QUẢ ÂM TÍNH — SGV **KHÔNG** ghi lỗi sai thường gặp của học sinh

Giả thuyết của tôi hôm qua: *"SGV là nguồn tốt nhất cho `common_mistakes` và
misconception"*. **Sai.**

Quét 52 đoạn `Lưu ý` / `HS có thể…` trong 35 trang (gồm trọn vùng chương phân số
tr.210–226). Kết quả: gần như toàn bộ là **chỉ dẫn tổ chức lớp**, không phải lỗi học sinh:

> *"Lưu ý: Nếu có điều kiện, GV nên sử dụng các hiệu ứng trình chiếu…"*
> *"Lưu ý: Đây là bài tập nâng cao nên tuỳ trình độ HS mà GV có thể không yêu cầu…"*
> *"Lưu ý: Tuỳ tình hình của lớp, GV có thể gợi ý như trên hoặc để HS tự làm"*

Gần nhất với chỉ dẫn về lỗi là hai câu về **cách trình bày**, không phải về hiểu sai:
> *"Khi thực hiện rút gọn phân số, HS có thể tách ra các bước để làm"*
> *"Khi rút gọn phân số phải đưa về phân số tối giản, có thể qua một số bước trung gian"*

**Không tìm thấy** câu nào dạng *"HS thường nhầm X với Y"*.

### Hệ quả kiến trúc — thay đổi kế hoạch

`caseTransitionGap` **không có nguồn văn bản** để nuôi. Misconception **không phải bài
toán trích xuất corpus** — nó là bài toán **học từ dữ liệu học sinh thật lúc chạy**.

⇒ `Misconception` nên là **evidence tích luỹ**, không phải entity trích sẵn từ sách.
Và ngày đầu ra mắt ta sẽ **không có** misconception nào — thiết kế phải chạy được với
tập rỗng đó, thay vì giả định có sẵn thư viện lỗi.

*(Giới hạn: 35/290 trang. Vắng mặt trong mẫu không chứng minh vắng mặt trong toàn sách.
Nhưng mẫu đã phủ trọn vùng bài 56–59 là nơi khả năng cao nhất.)*
