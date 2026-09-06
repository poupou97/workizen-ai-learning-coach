# Track B · Round 5 — Lesson Workspace: bản đồ trùng lặp + ba phương án trợ giúp

**Ngày:** 2026-09-06 · **Nhánh:** `lane-b/round5-experience` → base `integration/round5-2026-09-06`
· **Trạng thái:** READY FOR FOUNDER REVIEW — chưa merge gì.

Founder cầm máy và nói đúng chỗ: workspace **lặp lại, tốn chiều dọc**, có **quá nhiều hiện
diện của cùng ba Learning View**, **thẻ đề xuất chiếm chỗ thường trực**, và **CTA lặp lại
điều hướng đã thấy**. Tài liệu này: (1) đo hiện trạng, (2) bản đồ trùng lặp, (3) ba phương
án khác nhau về bản chất, (4) số đo trên máy thật, (5) đề nghị.

---

## 1. ĐO TRƯỚC KHI SỬA

Hai phép đo độc lập, cả hai đều lặp lại được:

**(a) Cây widget** — `test/features/lesson_workspace/workspace_density_test.dart`, đúng khung
nhìn Nokia 6.1 (1080×1920 @2.75 ⇒ **392.7×698.2 dp**), fixture MẪU (chạy được ở CI):

| | chrome GHIM · Đọc | Trực quan | **Học với SAM** | nhãn View nhìn thấy |
|---|---|---|---|---|
| bản hiện tại | 225.0 dp | 225.0 dp | **411.0 dp = 58.9 % khung nhìn** | 7 · 7 · 6 |

Y của **nội dung bài đầu tiên** ở Trực quan (đã tính cả thẻ nằm trong vùng cuộn): **384.0 dp**.

**(b) Máy thật** — Nokia 6.1, fixture THẬT (KHTN 6 Bài 17), phiên mới, cùng chuỗi chạm, đo
bằng khớp mẫu ảnh trên dòng tiêu đề nội dung «SAM (kịch bản thử nghiệm)» (sai số khớp `0.0`):

> **820 px / 1920 = 42.7 % màn hình bị tiêu trước khi nội dung bài bắt đầu.**

## 2. BẢN ĐỒ TRÙNG LẶP

Phân loại: **NAV** điều hướng · **NỘI DUNG** · **ĐỀ XUẤT** · **GIẢI THÍCH** · **TRẠNG THÁI**
· **TIẾN TRÌNH** · **⛔ TRÙNG**.

| # | Chỗ xuất hiện | Màn | Loại | Nó nói thêm điều gì KHÔNG chỗ nào khác nói | Bỏ được không |
|---|---|---|---|---|---|
| 1 | ← + «Giá sách › KHTN 6 › Chương IV» | luôn | NAV | con đang ở đâu | không |
| 2 | «Bài 17 · Tách chất khỏi hỗn hợp» | luôn | NỘI DUNG | bài nào | không |
| 3 | «SGK KHTN 6 · trang 60–63» | luôn | TRẠNG THÁI | nguồn + trang | không |
| 4 | chip «Bản thử nghiệm…» | luôn | TRẠNG THÁI | mức tin cậy (bắt buộc theo doctrine) | không |
| 5 | tab `[Đọc][Trực quan][Học với SAM]` | luôn | NAV | đổi View trong **1 chạm** | không |
| 6 | bong bóng SAM «Con muốn học bài này theo cách nào?» | màn chọn | GIẢI THÍCH | **không gì** — ba tab ngay trên đã nói đúng điều đó | **⛔ TRÙNG** |
| 7 | ba thẻ «Đọc như sách / Trực quan hoá / Học cùng SAM» | màn chọn | NỘI DUNG + NAV | **các con số đếm được** («16 đoạn · 8 hình · 11 câu hỏi · 4 chỗ SAM để trống») | giữ — nhưng tên phải trùng tên tab |
| 8 | «🦉 SAM đề xuất cách này — vì sao?» lồng trong thẻ 1 | màn chọn | ĐỀ XUẤT + GIẢI THÍCH | lý do | giữ |
| 9 | thẻ «SAM đề xuất» (chân dung + lý do + CTA) | trong View | ĐỀ XUẤT | lý do | **thay bằng lớp hé dần** |
| 10 | nút CTA `[✨ Trực quan]` trên thẻ ấy | trong View | NAV | **không gì** — tab cùng tên nằm ngay phía trên | **⛔ TRÙNG** |
| 11 | «Đã mở: ● Đọc ○ Trực quan ○ Học với SAM» | trong View | TIẾN TRÌNH | dấu vết phiên | gộp được vào lớp trợ giúp |
| 12 | chân dung SAM trên thẻ đề xuất | trong View | TRẠNG THÁI | **không gì** — SAM không nói ở đây | **⛔ TRÙNG (kỷ luật linh vật)** |
| 13 | «Về mục lục» trên thẻ kết của Tutor | tutor | NAV | **không gì** — nút ← đã có | ⛔ TRÙNG (ngoài phạm vi vòng này) |

**Phát hiện phụ, đo được:** bộ đếm nhãn chỉ bắt 5 lần trên màn chọn chứ không phải 6, vì
ba View được gọi bằng **hai bộ chữ khác nhau** — tab «Học với SAM» nhưng thẻ «Học cùng SAM».
Trẻ đọc **sáu nhãn cho ba thứ**, hai trong số đó còn khác chữ. Đó là một phần của cảm giác
«lặp mà vẫn rối».

## 3. NGUYÊN LÝ TƯƠNG TÁC ĐÃ MƯỢN (nguyên lý, không sao chép hình)

Nhìn ra ngoài ứng dụng giáo dục:

- **Hé dần (progressive disclosure)** — thông tin CHÍNH luôn thấy, lý do mở theo yêu cầu.
  Không phải «ẩn hết rồi hiện khi bấm».
- **Chip/hàng có thể bung** (inline expandable) — trạng thái trung gian PEEK nói **đích đến**
  chứ không chỉ nói «có gợi ý».
- **Gợi ý gắn với đích** (contextual inline suggestion) — dấu hiệu nằm ngay trên thứ người
  dùng sẽ chạm, thay vì ở một thẻ riêng.
- **Bottom sheet cho lời giải thích** — lời dài không nên chiếm chỗ thường trực.
- **Kỷ luật nhân vật**: linh vật xuất hiện khi nhân vật **thực sự nói**; một gợi ý dùng biểu
  tượng (💡), không dùng chân dung.

## 4. BA PHƯƠNG ÁN — khác nhau về bản chất, không phải ba biến thể của cùng một thẻ

Cả ba nhận **cùng một `NextAction`** (`Student State + Learning Context + Pedagogy Runtime →
Next Action`). Không có động cơ đề xuất thứ hai: `assist_layer.dart` **không được** nhập
`LessonDocument`, `WorkspaceTrace`, `nextActionFor` — có test soi mã.

Chọn lúc build: `--dart-define=WAL_ASSIST=icon|peek|inlineTab`, mặc định `card` = bản hiện
tại, để so A/B trên cùng một máy. **Sản phẩm không có nút đổi.**

| | A · ICON | B · PEEK CHIP | C · INLINE TAB |
|---|---|---|---|
| dấu hiệu mặc định | 💡 + chấm báo, trong hàng tiêu đề | một dòng «💡 SAM gợi ý: Xem Đọc ⌄» | 💡 **trong nhãn tab** đích: «📖 Đọc 💡» |
| mở «vì sao» | bottom sheet | bung **tại chỗ** | **không có tại chỗ** — phải sang View đó |
| thu gọn | luôn là 💡 | «Để sau» ⇒ 💡 về hàng tiêu đề | không có trạng thái mở |
| chi phí dòng | 0 | 1 dòng (48 dp) | 0 |
| điểm mạnh | gọn, lời dài có chỗ thở | **nói ĐÍCH ĐẾN với 0 chạm** | gọn nhất, gợi ý dính đúng chỗ sẽ chạm |
| điểm yếu | 💡 xa cụm tab; **làm tiêu đề bài xuống 2 dòng** | tốn 1 dòng khi đang hé | **không giải thích được «vì sao» tại chỗ** |

## 5. SỐ ĐO TRÊN MÁY THẬT (Nokia 6.1, Bài 17, cùng trạng thái, cùng chuỗi chạm)

Y của nội dung bài đầu tiên ở **Học với SAM** — màn Founder thấy tốn nhất:

| bản | y (px) | % màn hình | tiết kiệm so với hiện tại | khung ảnh |
|---|---|---|---|---|
| **HIỆN TẠI (card)** | 820 | 42.7 % | — | `round5-4-card-tutor.png` |
| **A icon** | 634 | 33.0 % | −186 px (−22.7 %) | `round5-4-icon-tutor.png` |
| **B peek** (đang hé) | 712 | 37.1 % | −108 px (−13.2 %) | `round5-4-peek-tutor.png` |
| **B peek** (đã «Để sau») | 634 | 33.0 % | −186 px (−22.7 %) | `round5-5-peek-collapsed-fixed.png` |
| **C inlineTab** | **565** | **29.4 %** | **−255 px (−31.1 %)** | `round5-5-inline-tutor-fixed.png` |

Cây widget (fixture mẫu, CI): chrome ghim ở Học với SAM **411 dp → 225 dp** (A và C) hoặc
**281 dp** (B); nhãn View nhìn thấy **7 → 3** (A, C) hoặc **4** (B).

**Chạm để đổi View:** 1 ở cả bốn (tab). **Chạm để hiểu «vì sao»:** hiện tại 0 · A 1 · B 1 ·
C — không có tại chỗ.

## 6. HAI LỖI MÁY THẬT TÌM RA (đã sửa, đã đi lại)

- **D4 · C**: huy hiệu 💡 là một `InkWell` ~21 dp **lơ lửng** ở góc ô tab — dưới ngưỡng chạm
  48 dp và đọc như không thuộc tab nào. Sửa: huy hiệu **nằm trong nhãn tab**, vùng chạm là
  cả tab, nhãn trợ năng của tab mang luôn câu «Gợi ý của SAM: …».
- **D5 · B**: sau «Để sau», gợi ý **biến mất hoàn toàn** — vi phạm «hé dần, không phải giấu
  đi». Sửa: trạng thái thu gọn của B mượn đúng dấu hiệu của A (💡 ở hàng tiêu đề).

## 7. MÀN CHỌN VÀ TAB CÓ THỪA NHAU KHÔNG?

**Không hoàn toàn — nhưng bong bóng và cách đặt tên thì thừa.** Ba thẻ mang thứ tab không
mang: **các con số đếm từ chính bài** («16 đoạn · 8 hình · 11 câu hỏi trong sách · 4 chỗ SAM
để trống»). Bỏ màn chọn là mất câu trả lời cho «bài này học được bằng những cách nào, và mỗi
cách có gì» — câu số 3 trong sáu câu Founder muốn thấy ngay.

Điều **thừa thật** trên màn chọn: (a) bong bóng «Con muốn học bài này theo cách nào?» khi ba
tab cùng nghĩa đã nằm ngay trên; (b) **hai bộ chữ cho cùng ba View**.

**Đề nghị (chưa làm, chờ Founder):** giữ màn chọn, bỏ bong bóng, và **thống nhất một bộ tên**
(«Đọc · Trực quan · Học với SAM») ở mọi chỗ; các con số chuyển thành dòng phụ của thẻ.

## 8. GIỚI HẠN ĐÃ TÔN TRỌNG

- **Không giấu hết**: mọi phương án đều có dấu hiệu đề xuất **nhìn thấy được** ở cả ba View —
  có test đi qua cả bốn phương án và bắt buộc điều đó.
- **AI-first không biến mất**: B nói **đích đến** với 0 chạm; A và C có chấm báo / huy hiệu.
- **Không có động cơ thứ hai**: test soi mã cấm `assist_layer` chạm vào bài hay trace.
- **Không cá nhân hoá giả**: chữ lý do vẫn là `next.reason` do runtime sinh; không thêm câu
  nào ngụ ý «con đã hiểu». MỞ ≠ HIỂU, CHẠM ≠ HỌC ĐƯỢC, ĐỌC ≠ THÀNH THẠO.
- **Trợ năng**: nhãn + gợi ý cho trình đọc màn hình ở mọi dấu hiệu, vùng chạm ≥ 48 dp.
- **Kỷ luật linh vật**: 💡 cho gợi ý; 🦉 và chân dung SAM chỉ còn ở chỗ SAM thực sự nói.
