# AUTONOMOUS EXECUTION QUEUE

Lệnh 60 — chế độ giám sát tự chủ. Jira WAL là hàng đợi việc; hàng đợi này là
thứ tự tôi tự chọn sau khi đọc 68 issue đang mở, và tôi chạy nó **không chờ
Founder duyệt**, trừ Founder Gate.

**Founder Gate (không tự làm):** merge vào `main` · phát hành · quyết định
bản quyền/pháp lý · hạ ngưỡng tin cậy · migration phá huỷ.

Chốt ngày **2026-09-07**. Ảnh chụp backlog: 68 mở — 26 In Progress · 34 Ideas ·
7 Ready · 1 QA. Theo loại: 24 Epic · 38 Task · 3 Story · 3 Bug.

---

## Nguyên tắc xếp thứ tự

Không xếp theo nhãn ưu tiên của Jira — 54/68 issue đều là `Medium`, nên nhãn
ấy không phân biệt được gì. Xếp theo bốn câu hỏi:

1. **Việc này có tự chạy được không**, hay cần Founder / cần corpus không nằm
   trong repo / cần quyết định pháp lý?
2. **Sai thì trẻ chịu hậu quả gì?** Nội dung sai > không có nội dung.
3. **Nó có làm cho các việc sau đo được không?** Sửa hạ tầng đo lường trước.
4. **Đã có bằng chứng nó đang hỏng chưa**, hay mới chỉ là nghi ngờ?

---

## HÀNG ĐỢI

### 1. WAL-223 — FALSE GREEN: vắng mặt đang được đọc là thành công ✅ XONG (Code Review)

Mười chỗ, bốn chỗ sống trên CI, mỗi chỗ đã đọc tận nguồn chứ không suy từ tên.
Luật: **ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION.**

Đứng đầu hàng vì **hôm nay tôi vấp đúng lớp lỗi này hai lần**:

* `showLearningImage` nhận `bleedScale` rồi không truyền xuống — test xanh vì
  test dựng thẳng widget, đi vòng qua đúng chỗ hỏng.
* Chân dung đã xác minh không hiện ở đâu cả — `forPerson()` trả non-null cho 0
  chuyện, mà không test nào đỏ.

Cả hai đều là **một khẳng định dương được thoả mãn bằng sự vắng mặt**. Khi hạ
tầng đo lường còn đọc «không có» thành «đạt», mọi con số ở các mục dưới đều
không đáng tin. Nên mục này đi trước — nó quyết định các mục sau có đo được
hay không.

Đã có mẫu sẵn trong repo: `tool/ci/golden_chain_verdict.py` (WAL-218) với
denominator floor · ledger · claim gate · đối chiếu ledger↔filesystem.

Chạy được ngay: chỉ đụng ngữ nghĩa báo cáo, **không** cần corpus, **không**
đụng D4/WAL-43.

### 2. WAL-193 — «Bạn có biết?» hiện title vô nghĩa khi thiếu năm sinh–mất ✅ VỐN ĐÃ XONG

`Bug`. Trẻ đọc thấy chuỗi rác trên Home. Nhỏ, chạy được ngay, cùng vùng mã tôi
vừa làm (Discovery/stories) nên ngữ cảnh còn nóng. Nội dung sai tệ hơn không
có nội dung.

### 3. WAL-194 — thân chuyện mất ký tự đầu («ương pháp» thay vì «Phương pháp») ✅ XONG (Code Review)

`Bug`, cùng vùng. Đây là lỗi DỮ LIỆU lộ ra ở UI, nên phải truy về chỗ cắt chuỗi
chứ không vá ở lớp hiển thị. Cần đo trên kho thật trước khi sửa.

### 4. WAL-226 — độ phủ chân dung: 1/21 → thêm 2–3 người

Cấu trúc vừa được thông (mục này trước đây bế tắc mà không ai biết). Mỗi người
là **một hồ sơ pháp lý riêng** — không suy từ Thạch Lam. Dừng lại và báo cáo
nếu quyền không rõ; `UNKNOWN_RIGHTS` là kết quả hợp lệ, không phải thất bại.

### 5. WAL-216 — chữ cái phương án «A.»–«D.» được phục hồi SAU khi `agreement()` chạy

Nhãn P0. Một điểm mù cấu trúc trong đo lường OCR: chuỗi bị sửa sau khi đã chấm
điểm đồng thuận ⇒ điểm đồng thuận không nói về thứ được ship. Cùng họ với
WAL-223 (số liệu nói về một vật khác với vật thật).

### 6. WAL-214 — DIGIT LOSS và SEGMENTATION là HAI lỗi, không phải một

`Ready`, nhãn P0. Gộp hai chế độ hỏng vào một con số thì không sửa được cái
nào. Cần benchmark đóng băng — kiểm xem có nằm trong repo không trước khi hứa.

### 7. WAL-215 — question vs non-question, phần dư sau Phase B

`Ready`. Nối tiếp WAL-214, cùng bộ đo.

### 8. WAL-225 — nguồn TYPOGRAPHY / FONT FAMILY vẫn UNRESOLVED

Đứng cuối **có chủ ý**. Lệnh 57 §8.4 cấm suy font từ hình chữ, và tôi không có
tệp nguồn của concept. Không có bằng chứng mới thì mục này **không đổi trạng
thái được** — đẩy lên trước chỉ tạo ra phỏng đoán. Cần Founder cung cấp tệp
thiết kế gốc.

---

## KHÔNG ĐƯA VÀO HÀNG ĐỢI (và vì sao)

| Issue | Lý do |
|---|---|
| WAL-171 (High) | Cần SGV + corpus không nằm trong repo. Nhãn High nhưng không tự chạy được ở đây. |
| WAL-43 · WAL-165 | Quyết định pháp lý / phân loại công khai — **Founder Gate**. |
| WAL-121…124, WAL-155…162 | Founder đã đánh dấu P2 · DEFERRED. Tôn trọng nhãn ấy. |
| WAL-13 | Thay đổi cấu trúc repo (submodule) — đụng nhiều repo, cần Founder. |
| WAL-192 | Đang chờ Founder gate decision, ghi rõ trong ticket. |
| WAL-49 | Cần học sinh/phụ huynh thật — không phải việc của tôi. |

---

## Nhật ký

| Ngày | Mục | Kết quả |
|---|---|---|
| 2026-09-07 | WAL-226 (lát cắt) | 1/21 chân dung đã xác minh; **lộ lỗi cấu trúc**: tài sản đúng + cổng đúng vẫn = 0 vì không đường nào dẫn tới. Đã sửa, đã kiểm trên Nokia. |
| 2026-09-07 | (ngoài hàng đợi) | `showLearningImage` nuốt `bleedScale` — bản vá hôm trước im lặng vô hiệu. Sửa + test đi đúng đường sản phẩm + kiểm-đột-biến. |
| 2026-09-07 | **1 · WAL-223** | **10/10 xong** → Code Review. 4 cổng CI + 6 cổng chạy tay. Đo được: 5/12 pack rỗng từng được chứng nhận «bản mặc định»; 11/12 lần «đạt» của guard không kiểm mục nào; xoá một giá trị đã ghi từng làm cổng metric xanh. ⚠ Bản sửa đầu của tôi là một **false RED** (thiếu 3/6 họ hoạt động) — bắt được vì đi đo pack thật trước khi tin con số. |
| 2026-09-07 | **2 · WAL-193** | **Đã xong từ trước** (commit `2bf7058`), ticket chỉ bị bỏ quên ở `Ideas` → Done. Suýt làm lại từ đầu; đối chiếu dữ liệu + git trước khi gõ dòng mã nào. |
| 2026-09-07 | **3 · WAL-194** | Xong → Code Review. Ticket ước lượng «1 story · THẤP»; đo thật **8/38 cụt đầu + 15/38 cụt đuôi**, và nhãn «TRÍCH NGUYÊN VĂN» đang hứa nhiều hơn nội dung. Kèm lỗi thứ hai: pack chép **đúng một lần** nên bản vá không bao giờ tới được máy đã cài. |
