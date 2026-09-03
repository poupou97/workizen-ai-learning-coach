# SAM — Product Experience Review

Vòng nghiên cứu sản phẩm, **không triển khai**. Viết cho Founder + GPT cùng phản biện trước
khi có lệnh code tiếp.

Bằng chứng dùng trong báo cáo: **38 ảnh concept** ở `concept/concept-ai-first/` (xem trực
tiếp từng ảnh, không đọc tên file), **corpus thật** (`poc-out/`), **app đang chạy trên Nokia
6.1**, và các bất biến đang được test giữ trong `lib/` + `test/`.

Tôi không đồng ý với phần lớn mô hình sản phẩm trong 38 concept. Lý do ở dưới.

---

## A. 38 CONCEPT ĐANG CỐ DỰNG SẢN PHẨM GÌ

Đọc theo hành trình chứ không theo số thứ tự, 38 concept mô tả **một EdTech companion app
đầy đủ** với năm khối:

1. **Thiết lập** (01–04): chọn vai (học sinh / phụ huynh) → hồ sơ → chọn môn → thời khoá biểu
   → mục tiêu. Một wizard 5 bước.
2. **Trung tâm điều khiển** (05–07, 19, 30–31): Home, Subjects, Subject Home, Learning Map,
   History, Progress — tất cả đều là **bảng điều khiển số liệu**.
3. **Đường dạy** (08–18, 20–22): Camera → Confirm → Tutor Start → Diagnostic → Workspace →
   Hint → Your Turn → Success → Why This Method → Source → Review → Quiz → Assessment →
   Result.
4. **Môn học** (23–29): Tiếng Việt, Essay, Physics, Chemistry, History, Geography, AI Learning.
5. **Người lớn & hệ thống** (32–38): Parent Home, Parent Detail, Multi-child, SAM Voice,
   Library, Notifications, Settings.

**Mô hình sản phẩm ẩn phía sau** — đọc từ chính các màn, không từ lời mô tả:

> SAM là một **khoá học số có đo lường**. Trẻ tiến theo một **lộ trình có khoá**, mỗi bước
> sinh ra **điểm và phần trăm**, tiến độ được **quy đổi thành XP / cấp / chuỗi ngày / huy
> hiệu**, và người lớn xem **bảng số liệu** để biết con đang ở đâu so với mục tiêu và so với
> các bạn.

Ba bằng chứng cho thấy đó đúng là mô hình, không phải trang trí:

- **Số liệu là nội dung chính**, không phải phụ chú. Subject Home (07) mở đầu bằng «Mức hiểu
  72% · Độ chính xác 78% · Thời gian trung bình 9 phút». Learning Map (19) đặt «42% hoàn
  thành · Cấp độ 4 · 2.450/4.000 XP · chuỗi 7 ngày» **trên cùng**, trước cả nội dung.
- **Động lực được thiết kế bằng phần thưởng ngoại sinh**: XP, cấp, huy hiệu, «Đỉnh tri thức»,
  quà, «+50 XP», trò chơi «Đấu trường SAM», **bảng xếp hạng tuần** giữa các học sinh (29).
- **Tiến trình bị khoá**: các nút trong Learning Map và danh sách bài tập (12) có ổ khoá 🔒,
  mở dần theo hoàn thành.

Đây là một sản phẩm **hoàn toàn hợp lý** và rất phổ biến. Nhưng nó **không phải** sản phẩm mà
Founder đã và đang xây. Xem mục C.

---

## B. 38 CONCEPT LÀM ĐÚNG ĐIỀU GÌ

Có bốn ý tưởng tôi cho là **đúng và nên giữ**, và chúng là phần giá trị nhất của bộ concept.

### B1. Camera Confirm (09) — ranh giới xác nhận

Màn này đúng gần như hoàn hảo: ảnh gốc, **chữ SAM đọc được** (sửa được), rồi **SAM xác định**
môn / lớp / chủ đề / kỹ năng, và chỉ sau khi trẻ bấm «Xác nhận và tiếp tục» thì mới đi tiếp.
Nó đặt **con người ở giữa** giữa nhận dạng và giảng dạy. Đây là bước duy nhất trong 38 concept
xử lý đúng chuyện «AI có thể đọc sai».

### B2. Why This Method (16) — giải thích bản chất

«Ý tưởng chính → Giải thích chi tiết → **Tại sao cách này đúng** (hình bánh chia 20 phần) →
Ghi nhớ nhanh». Đây là màn duy nhất dạy **vì sao**, bằng **biểu diễn trực quan** thay vì công
thức. Nó cũng là màn duy nhất tôn trọng trí tò mò của trẻ thay vì tối ưu tốc độ ra đáp án.

### B3. Physics (25) — mô phỏng là một *surface*, không phải một *screen*

«Mô phỏng trực quan» với hai thanh trượt (v, t) và đồ thị s–t cập nhật trực tiếp là bằng chứng
mạnh nhất trong cả bộ concept cho luận điểm: **môn khác nhau cần bề mặt tương tác khác nhau**,
chứ không phải màn hình khác nhau. Trẻ *kéo* để hiểu quan hệ, không đọc để nhớ quan hệ.

### B4. Tiếng Việt (23) — công cụ theo *hoạt động*

Dải «Công cụ luyện tập»: Chính tả (nghe–viết) · Từ vựng (thẻ ghi nhớ) · Đặt câu · Đọc hiểu ·
Viết đoạn. Đây là lần duy nhất bộ concept thừa nhận **một môn gồm nhiều loại hoạt động khác
nhau về bản chất** — và nó trùng khớp với bằng chứng corpus: mục lục Tiếng Việt tự liệt kê
*Đọc / Nói và nghe / Viết* bên trong **cùng một bài**.

Ngoài ra: hình minh hoạ và giọng văn với trẻ (bong bóng thoại của SAM) nhất quán và dễ thương;
Camera → Confirm → Tutor là một dây chuyền hợp lý.

---

## C. 38 CONCEPT LÀM SAI ĐIỀU GÌ

### C1. ⚠️ Sai lớn nhất: đo lường được đưa thẳng vào mặt đứa trẻ

Đếm trên chính các ảnh: **phần trăm hiểu bài** (07, 23, 25, 31), **điểm số /100** (11, 21),
**XP và cấp** (19, 29, 31), **chuỗi ngày 🔥** (11, 19, 23, 31, 32), **sao ★★★** (12, 19, 23),
**huy hiệu** (21, 31, 32), **xếp hạng «Top 15%», «Top 18%»** (21, 29, 32), **bảng xếp hạng
giữa học sinh** (29).

Ba vấn đề, theo thứ tự nghiêm trọng:

1. **Con số là bịa.** «Mức hiểu 72%» không phải đại lượng đo được. Muốn nói một đứa trẻ hiểu
   72% một khái niệm thì phải có mô hình đo và khoảng tin cậy. Sản phẩm đang xây chọn đúng
   con đường ngược lại: `ConceptSummary` phát biểu theo **ba trục** (*đã kiểm gì · chưa kiểm
   gì · tự làm hay có hỗ trợ*) và **từ chối** quy về một con số. Một con số **giấu mất** thứ
   quan trọng nhất: *cái gì chưa được kiểm*.
2. **Điểm và chuỗi ngày đổi động cơ học.** Trẻ chuyển từ «mình hiểu chưa» sang «mình được
   mấy điểm, mình có giữ được chuỗi không». Chuỗi ngày đặc biệt độc với trẻ tiểu học: nó biến
   một ngày ốm thành một mất mát, và tạo áp lực học **để giữ số**.
3. **Xếp hạng giữa trẻ em là ranh giới tôi sẽ không bước qua.** Concept 29 in tên và XP của
   các học sinh khác cạnh nhau và xếp trẻ ở hạng 18. Concept 21 gắn nhãn «Top 15%». Trong một
   sản phẩm học tập cho trẻ em Việt Nam — nơi áp lực so sánh vốn đã nặng — đây là tính năng
   gây hại, không phải tính năng tạo động lực.

App hiện tại **đã có test chặn** chuyện này (không %/điểm/XP/chuỗi trong UI của trẻ). Nghĩa
là 38 concept và sản phẩm đang xây **mâu thuẫn ở tầng luật**, không phải ở tầng thẩm mỹ.

### C2. ⚠️ Parent: so sánh anh chị em được in thành một khối UI

Concept 32 đặt ba đứa con cạnh nhau kèm 86% / 75% / 68% ngay ở thanh chuyển con. Concept 34
có hẳn khối tiêu đề **«So sánh nhanh»** với ba đường trên một biểu đồ, cộng huy hiệu «Nhà vô
địch».

Đây là **phản-mẫu**, không phải thiếu sót. Nó biến sản phẩm đồng hành thành công cụ so bì
trong chính gia đình. App hiện tại nói ngược lại ngay trên màn: *«Mỗi con một nhịp học riêng —
SAM kể chuyện từng bạn, không so sánh ai với ai»* — và có test giữ.

### C3. ⚠️ Sư phạm sai trong màn Hint (13)

Concept 13 dạy trẻ tìm **BCNN** để quy đồng `3/4 + 2/5`. Trong chương trình Toán 5 (Kết nối
tri thức), **BCNN chưa được dạy ở Bài 6** — cách sách dùng là «lấy tích hai mẫu». Sản phẩm
đang xây có bất biến và test riêng để **cấm** BCNN xuất hiện ở bài này.

Điều đáng chú ý: chính concept 16 lại viết «Mẹo của SAM: không nhất thiết phải quy đồng về
BCNN» — tức là **hai concept mâu thuẫn nhau** về phương pháp. Đây là dấu hiệu bộ concept được
thiết kế **từ hình dung về môn Toán**, không phải từ sách giáo khoa thật.

### C4. Thang hỗ trợ bị phá theo hai cách

- Concept 12 hiển thị **cả 4 bước lời giải** («SAM gợi ý: Bước 1…Bước 4») ngay dưới vùng làm
  bài, trước khi trẻ thử. Không còn khoảng lặng để trẻ tự nghĩ.
- Concept 13 cho trẻ **tự chọn độ chi tiết gợi ý** (Nhẹ / Vừa / Chi tiết). Mức hỗ trợ trở
  thành *tuỳ chọn giao diện* thay vì *hệ quả của việc trẻ đã thử*.

Cả hai đều xoá mất thứ có giá trị nhất trong dạy học: **productive struggle**. Sản phẩm đang
xây làm ngược: lời giải trọn vẹn chỉ mở sau ≥1 lần tự thử, và mức hỗ trợ đi vào bằng chứng
(«đúng sau gợi ý nhỏ» khác «đúng sau khi xem lời giải»).

### C5. «Source» (17) không phải provenance — nó là bãi link

Concept 17 tên là «Nguồn tham khảo» nhưng nội dung là **liên kết bên thứ ba**: VnDoc,
Loigiaihay.com, Toploigiai.vn, video YouTube, sách tham khảo thương mại. Hai trong số đó là
**trang tra lời giải** — đúng thứ mà cổng REVEAL sinh ra để ngăn. Đưa trẻ tới đó ngay trong
lúc học là tự phá cơ chế của chính mình.

«Nguồn» đúng nghĩa phải là: **câu này SAM lấy từ đâu trong sách của con** — trang in, dòng
chữ in, và phân biệt rõ *lời sách* với *lời SAM*. App hiện tại làm đúng điều đó
(«SAM làm theo ví dụ trong SGK Toán 5, trang 21»), concept thì không có khái niệm này.

### C6. «AI Learning» (29) là một sản phẩm khác lẫn vào

Một môn không có trong chương trình phổ thông, dạy ChatGPT/LLM/Prompt Engineering, kèm **bảng
xếp hạng học sinh** và **link thẳng tới ChatGPT, Gemini, Claude, Copilot cho trẻ**. Ba vấn đề:
lệch định vị sản phẩm (SAM là bạn học **theo SGK**), rủi ro an toàn (trẻ vào chatbot đa dụng
không kiểm soát), và nó chiếm chỗ của chính vấn đề khó chưa giải xong (dạy được 7.626 bài
trong SGK).

### C7. Kiến trúc thông tin không nhất quán

Bốn thanh điều hướng khác nhau xuất hiện trong cùng bộ concept:

| Concept | Bottom nav |
|---|---|
| 05 Home, 07 Subject Home | Hôm nay · Môn học · **SAM** · Tiến bộ · Thêm |
| 23 Tiếng Việt | Trang chủ · Học tập · Thành tích · Cài đặt |
| 29, 31 | Home · Library · Progress · Quiz · Profile |
| 32, 34 | Parent Home · Multi-child · Reports · Messages · Settings |

Không thể nói đây là «một sản phẩm» cho tới khi chọn một IA.

### C8. Bố cục máy tính bảng/desktop cho một sản phẩm điện thoại

Concept 12 (Problem Workspace) là ba cột: danh sách 10 bài bên trái, canvas viết tay ở giữa,
công cụ + ghi chú bên phải. Trên điện thoại 393dp — máy thật đang chạy — bố cục này không tồn
tại. Nhiều concept khác cũng rộng hơn khung điện thoại.

### C9. Ba thứ **thiếu hẳn**, và đều quan trọng

1. **Không có giá sách / không có cuốn SGK nào.** Trong 38 concept, trẻ đi vào bài qua *môn*
   và *lộ trình*, chưa bao giờ qua **cuốn sách đang nằm trên bàn**. Với học sinh Việt Nam,
   sách giấy là trung tâm của việc học ở lớp — đây là lỗ hổng lớn nhất của bộ concept.
2. **Không có ý định học (learning intent).** Mọi nút đều là «Tiếp tục học» — tiếp tục *lộ
   trình*. Không có chỗ nào hỏi trẻ *hôm nay con cần gì*: chuẩn bị cho bài ngày mai, hay ôn
   lại bài vừa học trên lớp. Đây chính là chỗ giả thuyết mới của Founder đánh trúng.
3. **Không có trạng thái «SAM chưa biết».** Mọi màn đều có số, có tiến độ, có gợi ý. Không màn
   nào xử lý *thiếu dữ liệu* — trong khi ở corpus thật, đa số bài **chưa có nội dung dạy**.
   Một sản phẩm chỉ đẹp khi đủ dữ liệu là một sản phẩm chưa thiết kế xong.

---

## D. GIẢ THUYẾT 4-MODE CỦA FOUNDER — ĐÚNG Ở ĐÂU

**Đúng ở tầng nền, và đây là bước tiến thật so với 38 concept.**

1. **Ý định phải đến trước nội dung.** Câu «Hôm nay con muốn làm gì với cuốn sách này?» giả
   định trẻ mở app **vì một tình huống**, không phải để tiếp tục một thanh tiến độ. Điều này
   đúng với đời thật: trẻ mở sách vì *mai có tiết*, vì *cô giao bài*, vì *không hiểu chỗ nào
   đó*. 38 concept không có khái niệm này.
2. **Cùng một bài, ý định khác nhau ⇒ trải nghiệm khác nhau.** Đây là luận điểm mạnh nhất
   trong đề xuất của Founder, và tôi tin nó đúng. Khoa học 5 Bài 1 khi *học trước* phải là
   quan sát → dự đoán → điều cần chú ý trên lớp; khi *ôn lại* phải là nhớ lại → giải thích →
   bắt lỗi hiểu sai. Cùng nội dung nguồn, khác hoạt động, khác bằng chứng sinh ra.
3. **«Học trước» được định nghĩa đúng.** Mục tiêu ghi rõ: *giúp con dễ hiểu bài khi giáo viên
   dạy* — **không thay giáo viên**. Đây là định vị đúng cho một sản phẩm học tại nhà ở Việt
   Nam, và nó tránh được cái bẫy lớn nhất của gia sư AI: cạnh tranh với trường học.
4. **Camera không mặc định là «chụp → đáp án».** Founder viết rõ chuỗi phải là capture →
   understand → confirm → guide → attempt → verify → evidence. Đúng.
5. **Tách nội dung nguồn khỏi lời SAM.** «SOURCE CONTENT và SAM EXPLANATION phải được hiểu là
   hai thứ khác nhau» — đây chính là thứ concept 17 làm hỏng.

---

## E. GIẢ THUYẾT 4-MODE — SAI Ở ĐÂU

Tôi phản biện bốn điểm.

### E1. «Xem sách» không phải một chế độ học

Ba mode kia là **ý định học** (ôn / chuẩn bị / nhờ giúp). «Xem sách» là **truy cập tài liệu**
— nó nên có mặt **ở mọi nơi**, mọi lúc, như một lớp phủ, chứ không phải một nhánh ngang hàng.
Đặt nó thành mode thứ 3 gây hai hại: (a) làm menu dài thêm mà không thêm ý định; (b) mời trẻ
chọn con đường **không sinh bằng chứng gì** — và với trẻ, đó luôn là lựa chọn dễ nhất.

**Đề xuất**: «Xem trong sách» là **nút phụ luôn hiện** trong mọi hoạt động, không phải mode.

### E2. Camera không thuộc phạm vi cuốn sách

Founder tự đặt câu hỏi này và câu trả lời là: **global**. Trẻ chụp *phiếu bài tập*, *vở*, *đề
cô phát* — phần lớn **không thuộc cuốn nào trên giá**. Bắt trẻ chọn sách trước rồi mới chụp là
thêm một bước sai. Hơn nữa app hiện tại đã đi đúng: camera là hành động ở Home.

**Đề xuất**: Camera là **lối vào toàn cục**, và *kết quả* của nó mới được neo về bài/sách nếu
nhận ra được. Trong sách vẫn có thể có nút «chụp bài trang này», nhưng đó là lối tắt, không
phải nơi ở của tính năng.

### E3. Bốn nhãn này quá trừu tượng với trẻ tiểu học

«Ôn bài» và «Học trước» là **từ vựng của người lớn về việc học**. Một đứa lớp 2 không phân
biệt được «ôn» với «học». Kể cả lớp 5 cũng thường không biết mình đang *ôn* hay đang *học lại
vì chưa hiểu*.

Chia theo lứa:

| Lứa | Hiểu mô hình 4 mode? | Nhận xét |
|---|---|---|
| Lớp 1–3 | **Không** | Cần **một** việc được đề nghị sẵn. Chọn nhiều là gánh nặng. |
| Lớp 4–6 | **Một phần** | Phân biệt được «mai có tiết» vs «cô giao bài». «Ôn» vs «học trước» thì mơ hồ. |
| THCS | **Có** | Bắt đầu tự điều phối việc học. |
| THPT | **Có, và muốn nhiều quyền hơn** | Muốn nhảy thẳng tới bài/dạng cụ thể. |

**Đề xuất**: dùng **ngôn ngữ tình huống** thay vì ngôn ngữ sư phạm —
«**Mai có tiết này**» (chuẩn bị) · «**Cô vừa dạy rồi**» (ôn) · «**Con có bài tập**» (camera).
Trẻ nhận ra *tình huống của mình*; nó không cần biết tên gọi sư phạm.

### E4. Ý định gắn vào **BÀI**, không phải vào **CUỐN SÁCH**

Đây là phản biện kỹ thuật-sản phẩm quan trọng nhất của tôi.

Một cuốn sách có 30 bài ở **các trạng thái khác nhau**: bài 1–12 đã học trên lớp, bài 13 đang
học, bài 14 mai mới học. Hỏi «hôm nay con muốn làm gì **với cuốn sách này**» là hỏi sai đơn
vị — câu trả lời phụ thuộc vào **bài nào**, không phải cuốn nào.

Tệ hơn: nếu chọn mode ở mức sách, ta buộc phải lọc danh sách bài theo mode («đây là các bài
ôn được»), và điều đó **giả vờ biết** bài nào trẻ đã học trên lớp — thứ SAM **không** biết trừ
khi có thời khoá biểu chính xác.

**Đề xuất**: chọn **bài** trước, rồi ý định xuất hiện **tại bài** — nơi SAM biết đủ để **gợi ý
sẵn** một ý định (dựa trên thời khoá biểu + bằng chứng) thay vì bắt trẻ chọn trong hư không.

### E5. Điểm còn thiếu: Assessment và «Hỏi SAM» chưa có chỗ

Founder hỏi và tôi trả lời:
- **Assessment không phải mode thứ 5.** Nó là **cách kết thúc** của ý định «ôn»: khi bằng
  chứng đã đủ, SAM đề nghị «thử tự làm không cần gợi ý». Biến nó thành mode riêng là mời trẻ
  đi làm bài kiểm tra tự nguyện — điều gần như không xảy ra.
- **«Hỏi SAM» là lớp phủ toàn cục**, không phải mode, không phải tab. Nó phải mang theo **ngữ
  cảnh đang mở** (bài nào, bước nào), nếu không nó thoái hoá thành một chatbot chung chung.

---

## F. SAM PRODUCT EXPERIENCE MODEL vNEXT — ĐỀ XUẤT CỦA TÔI

### F0. Một câu định vị

> SAM là **bạn học đi cùng cuốn sách và thời khoá biểu của con**, giúp con **hiểu bài trước và
> sau giờ lên lớp**, và **chỉ nói những điều nó có bằng chứng**.

Ba mệnh đề đó quyết định mọi thứ còn lại: neo vào **sách + lịch** (không phải lộ trình riêng),
phục vụ **quanh giờ học ở trường** (không thay trường), và **trung thực** (không điểm ảo).

### F1. Ai mở SAM, và vì sao

| Người | Vì sao mở | Tần suất thật |
|---|---|---|
| Trẻ tiểu học (lớp 1–5) | bố mẹ bảo ngồi vào bàn; có bài tập; mai có tiết | gần như hằng ngày, buổi tối |
| Trẻ THCS/THPT | mắc một bài cụ thể; ôn trước kiểm tra | theo đợt, không đều |
| Phụ huynh | «tối nay học gì với con», «con có ổn không» | 1–2 lần/tuần, ngắn |

Thiết kế phải tối ưu cho **cột giữa** — *lý do thật*, không phải cho hành vi lý tưởng.

### F2. Home = **một việc**, không phải bảng điều khiển

Home trả lời đúng một câu: **«Bây giờ làm gì?»**

- Một thẻ đề nghị **duy nhất**, có lý do nhìn thấy được («Mai có tiết Khoa học» / «Hôm qua con
  cần 2 lần gợi ý ở phần này»).
- Ba lối vào cố định bên dưới: **Chụp bài tập** · **Sách của con** · **Bố mẹ**.
- Khi không có gì đáng làm: **nói thẳng là không có** (app hiện tại đã làm đúng — «Hôm nay
  nghỉ ngơi nhé»). Một sản phẩm dám nói «hôm nay không cần học thêm» là sản phẩm đáng tin.

*Bỏ khỏi Home*: xu/điểm, % môn, chuỗi ngày, danh sách «tiếp tục học» nhiều thẻ, gợi ý dài.

### F3. Giá sách = **nhận ra sách**, không phải chế độ học

Giữ như hiện tại (bìa thật, lưới, theo lớp). Vai trò duy nhất: *nhận ra cuốn sách trên bàn*.
Bấm vào **không mở PDF**.

### F4. Book Home = **mục lục có trạng thái**

Danh sách bài theo đúng thứ tự sách. Mỗi bài nói **một** điều: có việc gì làm được, hoặc chưa
có. Không phần trăm, không khoá, không sao.

### F5. ⭐ Ý định xuất hiện **tại bài**, và SAM **đề nghị trước**

Đây là điểm khác biệt cốt lõi giữa đề xuất của tôi và giả thuyết của Founder.

Khi trẻ mở một bài, SAM **không hỏi một menu rỗng**. Nó nói một câu, kèm lối rẽ:

```
Bài 1 · Thành phần và vai trò của đất

   «Mai lớp con có tiết này.»            → [ Cùng xem trước ]     (đề nghị chính)

   Hoặc:  · Cô dạy rồi, con ôn lại
          · Con có bài tập cần giúp
          · Xem trong sách
```

- **Đề nghị chính** suy từ dữ liệu có thật: thời khoá biểu (mai có tiết) → *chuẩn bị*; có bằng
  chứng gần đây / đến hạn ôn → *ôn*; không có gì → *xem trước*, mức nhẹ nhất.
- Ba lối còn lại **luôn hiện**, không ẩn — trẻ vẫn toàn quyền.
- «Xem trong sách» đặt cuối và **không** ngang hàng về thị giác: nó là tra cứu, không phải học.

Nếu không có thời khoá biểu, SAM **không đoán**: câu mở đầu thành «Con muốn bắt đầu thế nào?»
với ba lối như nhau. **Không bịa lý do.**

### F6. Bốn ý định, đặt tên theo tình huống của trẻ

| Ý định | Câu trẻ đọc | Hình dạng hoạt động | Bằng chứng sinh ra |
|---|---|---|---|
| **Chuẩn bị** | «Mai có tiết này» | quan sát → **dự đoán** → điều cần chú ý trên lớp | dự đoán (chưa chấm đúng/sai) |
| **Ôn lại** | «Cô dạy rồi» | nhớ lại → giải thích → làm thử → bắt lỗi hiểu sai | attempt có/không hỗ trợ |
| **Bài tập** | «Con có bài tập» | chụp → xác nhận → chẩn đoán → gợi ý bậc thang → tự làm | attempt + mức hỗ trợ |
| *(phủ)* **Xem trong sách** | «Xem lại chỗ này» | trang / hình / tư liệu gốc + gloss của SAM có nhãn riêng | không sinh bằng chứng |

**Chỉ ba ý định đầu là chế độ học.** Cái thứ tư là lớp phủ.

### F7. Khi nào SAM im lặng

Đây là phần thiết kế mà 38 concept không có, và tôi cho là **đặc điểm nhận dạng** của sản phẩm:

- Chưa có bằng chứng ⇒ **không kết luận** («chưa kiểm» ≠ «chưa biết»).
- Chưa có lời dạy có nguồn cho phương pháp ⇒ **không nói gì**, không rơi về câu chung chung.
- Trẻ chưa tự thử ⇒ **không mở lời giải**.
- Không có gì đáng ôn hôm nay ⇒ **nói là không có**.
- Câu hỏi mở không có đáp án in trong sách ⇒ **không chấm đúng/sai**.

---

## G. CÁC HÀNH TRÌNH LÕI

**1. Vòng ngày của trẻ** — mở → *một* đề nghị → làm 5–10 phút → SAM nói đã ghi nhận được gì →
đóng. *Thứ kéo trẻ quay lại*: **không phải chuỗi ngày**, mà là (a) tối nay có bài tập thật,
(b) mai có tiết, (c) SAM nhớ chỗ con vướng và hẹn gặp lại đúng chỗ đó.

**2. Vòng theo sách** — giá sách → cuốn → bài → ý định → hoạt động → bằng chứng.

**3. Vòng chuẩn bị** — (từ thời khoá biểu) → bài của tiết mai → quan sát/dự đoán → *«mai lên
lớp con để ý chỗ này»* → kết thúc. **Không** kiểm tra, **không** chấm.

**4. Vòng ôn** — SAM nêu chỗ có bằng chứng yếu → nhớ lại → làm thử 1–2 bài → nếu tự làm được
thì SAM nói rõ mức chắc chắn; nếu chưa thì hẹn lại.

**5. Vòng bài tập (camera)** — chụp → SAM đọc → **trẻ xác nhận** → nhận diện bài/dạng → nếu
ngoài phạm vi: **nói thẳng là chưa dạy được** → nếu trong phạm vi: chẩn đoán → gợi ý bậc thang
→ trẻ tự làm → xác nhận → bằng chứng.

**6. Vòng xem sách** — mở đúng trang/hình/tư liệu; lời sách và lời SAM **tách bạch**; muốn hỏi
thêm thì «Hỏi SAM» mang theo ngữ cảnh.

**7. Vòng kiểm tra hiểu bài** — **chỉ mở khi bằng chứng đủ**; không hỗ trợ trong lúc làm; kết
quả trả về **theo từng ý**, không phải điểm tổng.

**8. Vòng phụ huynh** — mở → **một** câu về từng con → *một* việc làm cùng con tối nay (~10
phút) → quyền dữ liệu. **Không bảng số, không so sánh.**

**9. Vòng nhiều con / máy dùng chung** — đổi người học trong 2 chạm; dữ liệu **cách ly**; hồ
sơ mới không đụng hồ sơ cũ. *(Đã kiểm trên máy thật hôm nay.)*

---

## H. IA / ĐIỀU HƯỚNG ĐỀ XUẤT

**Một** thanh dưới, **ba** mục (không phải bốn hay năm):

```
[ Hôm nay ]      [ Sách của con ]      [ Bố mẹ ]
```

- **Hôm nay** — một việc + ba lối vào (chụp / sách / hỏi SAM).
- **Sách của con** — giá sách → cuốn → bài → ý định → hoạt động.
- **Bố mẹ** — sau PIN.

Bỏ khỏi thanh dưới: «Tiến bộ» (không phải nơi trẻ nên ở hằng ngày; đưa vào phần Bố mẹ và vào
cuối mỗi phiên), «Thư viện», «Quiz», «Thành tích», «Messages».

**Nút SAM nổi ở giữa** (concept 05): bỏ. Nó gợi ý «chat với AI» là hoạt động chính — sai định
vị. «Hỏi SAM» nên là **lớp phủ theo ngữ cảnh**, gọi từ trong bài.

---

## I. MÔ HÌNH SÁCH → Ý ĐỊNH HỌC

```
Sách (nhận ra)
  └─ Bài (đơn vị của sách, KHÔNG phải đơn vị trải nghiệm)
       └─ Ý ĐỊNH  ← SAM đề nghị, trẻ đổi được
            └─ Hoạt động  ← nơi CHỌN Experience Pattern
                 └─ Surface(s)
                      └─ Bằng chứng
```

**«Bài» không phải trải nghiệm nguyên tử** — corpus đã chứng minh: mục lục Tiếng Việt tự liệt
kê *Đọc / Nói và nghe / Viết* trong cùng một bài. Vậy chọn pattern phải xảy ra ở **hoạt động**.

Nhưng — và đây là chỗ tôi tự phản biện — **UX không nên bắt trẻ chọn hoạt động**. Trẻ chọn
**ý định**; hệ thống dịch (ý định × hoạt động có thật trong bài) ra **một chuỗi**. Nếu bài có
ba hoạt động, ý định «ôn» có thể chạy cả ba nối tiếp; ý định «chuẩn bị» có thể chỉ chạy phần
quan sát. **Kiến trúc chọn ở mức hoạt động; giao diện hỏi ở mức ý định.**

---

## J. TRẢI NGHIỆM THEO MÔN

Môn khác nhau **không cần màn hình riêng**, nhưng **cần bề mặt tương tác riêng**. Đây là bảng
tôi rút ra từ concept + corpus:

| Môn | Hoạt động thật trong sách | Surface cần có | Đã có? |
|---|---|---|---|
| Toán | bài tập có đáp số | ô nhập + thang gợi ý + provenance | ✅ |
| Tiếng Việt | đọc hiểu · nói và nghe · viết | đoạn văn verbatim + câu hỏi mở + ô viết; **ghi âm** cho nói–nghe | một phần (thiếu nói–nghe) |
| Khoa học | thí nghiệm (chuẩn bị/tiến hành/dự đoán) | **cổng dự đoán** + ô quan sát | ✅ |
| Vật lí | thí nghiệm + quan hệ đại lượng | như Khoa học + **mô phỏng có tham số** (concept 25) | thiếu mô phỏng |
| Hoá học | thí nghiệm + phương trình | như trên + **trình bày phương trình** | thiếu |
| Sinh học | quan sát cấu trúc | hình có nhãn / phóng to | thiếu |
| Lịch sử | tư liệu gốc | trích verbatim + attribution + gloss **có nhãn riêng** | ✅ |
| Địa lí | bản đồ, biểu đồ | **bản đồ đọc được** (phóng, chỉ điểm) | một phần |
| Tiếng Anh | nghe · nói · từ vựng | **audio** + ghi âm + thẻ từ | ❌ thiếu hẳn |
| Công nghệ / Tin học | quy trình, thao tác | danh sách bước có tick | một phần |
| Âm nhạc / Mĩ thuật / GDTC | biểu diễn, tạo tác | **nộp ảnh/âm thanh**, không chấm đúng/sai | ❌ |

**Hai lỗ hổng lớn nhất**: **âm thanh** (Tiếng Anh và Tiếng Việt nói–nghe — chiếm phần lớn thời
lượng học ngôn ngữ) và **mô phỏng tham số** (Vật lí/Hoá). Không surface nào trong hai nhóm này
tồn tại trong sản phẩm hiện tại.

---

## K. VAI TRÒ CỦA SAM TRONG TỪNG HÀNH TRÌNH

| Hành trình | SAM là | SAM **không** được là |
|---|---|---|
| Home | người đề nghị *một* việc, có lý do | bảng thành tích |
| Chuẩn bị | người đặt câu hỏi để trẻ để ý trên lớp | người dạy trước bài của cô |
| Ôn | người chỉ ra *chỗ chưa chắc*, có dẫn chứng | người chấm điểm |
| Bài tập | người bắc thang, giữ cổng lời giải | máy giải bài |
| Xem sách | người chú thích **có nhãn riêng** | người viết lại lời sách |
| Kiểm tra | người im lặng | người gợi ý |
| Phụ huynh | người kể *một* điều có bằng chứng | người xếp hạng các con |

---

## L. TRẺ vs PHỤ HUYNH

Hai sản phẩm khác nhau dùng chung một kho bằng chứng:

- **Trẻ**: ngôn ngữ tình huống, một việc, không số, không so sánh, kết thúc bằng «SAM ghi nhận
  được gì».
- **Phụ huynh**: ngôn ngữ *hành động cùng con*, một việc tối nay ~10 phút, **luôn kèm mức chắc
  chắn** («7 lần tự làm — chưa đủ để kết luận»), và **quyền dữ liệu** (lấy ra / xoá).

App hiện tại đã đúng hướng này và **tốt hơn hẳn concept 32/33/34**.

---

## M. GIỮ / SỬA / GỘP / BỎ / THÊM

| Concept | Quyết định | Lý do |
|---|---|---|
| 01 Onboarding | **Sửa** | Bỏ wizard 5 bước; hỏi 2 câu (tên, lớp) rồi vào học. Môn/TKB/mục tiêu hỏi sau, khi cần. |
| 02 Learner Profile | **Gộp** vào onboarding | |
| 03 Subject Setup | **Bỏ** ở onboarding | Lớp đã suy ra được bộ môn; hỏi lại là thừa. |
| 04 Timetable | **Giữ, hạ ưu tiên** | Rất giá trị (sinh ra ý định «mai có tiết») nhưng **tuỳ chọn**, nhập sau. |
| 05 Home | **Làm lại** | Từ dashboard → **một việc + ba lối vào**. |
| 06 Subjects | **Bỏ** | Bị giá sách thay thế. Trẻ nhận ra *sách*, không nhận ra *môn trừu tượng*. |
| 07 Subject Home | **Làm lại thành Book Home** | Bỏ 6 tab và mọi %; còn mục lục có trạng thái. |
| 08–09 Camera + Confirm | **Giữ** | Concept 09 là màn tốt nhất bộ. |
| 10 Tutor Start | **Gộp** vào Confirm | Một bước xác nhận là đủ. |
| 11 Diagnostic | **Làm lại** | Bỏ điểm/100 và chuỗi ngày. Chẩn đoán phải là *câu nói về chỗ vướng*, không phải bảng điểm. |
| 12 Problem Workspace | **Làm lại cho điện thoại** | Bỏ 3 cột; bỏ hiển thị 4 bước trước khi trẻ thử. Giữ **canvas viết tay** như một ý tưởng đáng làm. |
| 13 Hint | **Sửa (gấp)** | Bỏ BCNN khỏi Toán 5 B6; bỏ chọn độ chi tiết; thang hỗ trợ do **hành vi** quyết định. |
| 14 Your Turn | **Giữ** | Đúng tinh thần. |
| 15 Success | **Sửa** | Bỏ điểm/sao; nói *đã ghi nhận được gì*. |
| 16 Why This Method | **Giữ, nâng lên** | Nên là **đích đến**, không phải màn phụ. |
| 17 Source | **Làm lại hoàn toàn** | Từ bãi link bên thứ ba → **provenance trong SGK của con**. Bỏ link trang tra lời giải. |
| 18 Review | **Giữ** | Hợp với mô hình ôn theo bằng chứng. |
| 19 Learning Map | **Làm lại** | Bỏ XP/cấp/chuỗi/khoá/sao/radar. Giữ ý «bản đồ»: **bài nào có bằng chứng, bài nào chưa kiểm**. |
| 20 Quiz / 21 Assessment / 22 Result | **Gộp thành một**, đặt sau ôn | Bỏ điểm/100, «Top 15%», «Chia sẻ kết quả», «Đấu trường». Trả kết quả **theo từng ý**. |
| 23 Tiếng Việt | **Giữ phần công cụ**, bỏ phần số | «Công cụ luyện tập» chính là hoạt động — giữ. |
| 24 Essay | **Giữ** | Cần cho ý định viết. |
| 25 Physics | **Giữ mô phỏng** | Surface đáng giá nhất chưa được xây. |
| 26–28 Chemistry/History/Geography | **Giữ ý**, bỏ vỏ dashboard | Cần surface riêng (phương trình, tư liệu, bản đồ). |
| 29 AI Learning | **BỎ** | Ngoài chương trình; có xếp hạng trẻ em; đẩy trẻ tới chatbot đa dụng. |
| 30 History Sessions | **Gộp** vào phần Bố mẹ | Trẻ không cần nhật ký phiên học. |
| 31 Progress | **Làm lại + chuyển sang Bố mẹ** | Bỏ %/XP/streak/radar. |
| 32 Parent Home | **Làm lại** | Bỏ điểm TB, chuỗi, huy hiệu, «Top 18%». |
| 33 Parent Detail | **Giữ hướng hiện tại của app** | App thật đang tốt hơn concept. |
| 34 Multi-child | **Bỏ khối «So sánh nhanh»** | Vi phạm nguyên tắc không so sánh. |
| 35 SAM Voice | **Giữ, nhưng ưu tiên thấp** | Có giá trị thật cho lớp 1–3 (chưa đọc trôi). |
| 36 Library | **Bỏ / hoãn** | Trùng với giá sách; chưa có nội dung để chứa. |
| 37 Notifications | **Giữ tối thiểu** | Chỉ nhắc *việc có thật*; không nhắc giữ chuỗi. |
| 38 Settings | **Giữ** | Thêm: quyền dữ liệu, PIN, đổi người học. |
| **THÊM** | **Giá sách** | Không có trong 38 concept. Là neo mạnh nhất với học sinh VN. |
| **THÊM** | **Chọn ý định tại bài** | Không có trong 38 concept. |
| **THÊM** | **Trạng thái «SAM chưa biết»** | Bắt buộc, vì đa số bài chưa có nội dung dạy. |
| **THÊM** | **Surface âm thanh** | Tiếng Anh + Tiếng Việt nói–nghe. Lỗ hổng lớn nhất theo môn. |

---

## N. APP HIỆN TẠI ĐANG SAI GÌ

Đi qua app trên Nokia hôm nay, với tư cách học sinh rồi phụ huynh:

1. **⭐ Ý định bị rơi ngay ở cửa.** Home có đúng các động từ cần thiết («Học trước», «Ôn
   luyện», «Làm bài tập»…). Nhưng bấm **«Học trước»** thì mở ra **giá sách** — mà giá sách
   không phải một ý định. Từ đó trở đi, ý định **biến mất**: chọn sách → chọn bài → sheet
   «Bài này có mấy việc» hỏi *hoạt động*, không hỏi *ý định*. Kết quả: trẻ vào bằng «học
   trước» nhưng nhận được **cùng một trải nghiệm** như mọi lối khác. Đây đúng là chỗ giả
   thuyết của Founder cần đánh vào — và là **khoảng cách lớn nhất** giữa app và mô hình vNext.
2. **Home vẫn còn là danh sách nút.** Năm chip ngang hàng + thẻ đề xuất + «Bạn có biết» + «Ôn
   lại» + «Thử dạng mới». Đúng hướng hơn concept, nhưng vẫn bắt trẻ **chọn**, trong khi thứ
   trẻ cần là **một việc**.
3. **«Bài này có mấy việc — con chọn nhé» là ngôn ngữ kiến trúc rò ra UX.** Trẻ không nghĩ
   theo «việc»; đó là từ của `LessonActivity`. Nên là: *«Con muốn bắt đầu thế nào?»*.
4. **Nhiều bài chỉ nói «SAM đang học bài này — con chụp bài tập để học cùng nhé».** Trung
   thực, nhưng lặp lại hàng chục lần liên tiếp thì thành **một cuốn sách toàn cửa khoá**. Cần
   nói khác đi: cho phép «xem trong sách» ngay cả khi chưa dạy được.
5. **Chưa có gì cho lớp 10.** Trẻ lớp 10 duyệt được 41 cuốn, mở được 5 thí nghiệm, nhưng
   **không được dạy** dòng nào. Home nói thật («SAM chưa có nội dung lớp 10») — đúng, nhưng
   sản phẩm chưa dùng được cho lứa đó.
6. **Kết thúc phiên còn mỏng.** Sau thí nghiệm chỉ có «Về danh sách bài». Thiếu câu «SAM ghi
   nhận được gì» — chính là thứ tạo lý do quay lại.
7. **Không có đường vào «xem trong sách»** ở nơi trẻ cần nó nhất (đang học mà quên).
8. Nhỏ hơn: thao tác đầu tiên sau khi mở app hay bị nuốt; vài bài hiện «Bài 1» trần; hai cuốn
   «Công nghệ 10» trùng tên.

**Điều app đang làm ĐÚNG mà concept làm sai** (không được đánh mất khi làm lại UX): không
điểm/%, không XP/chuỗi, không so sánh anh chị em, fail-closed khi thiếu bằng chứng, provenance
trỏ về SGK thật, phân biệt lời sách với lời SAM, quyền dữ liệu của phụ huynh.

---

## O. KHOẢNG CÁCH: APP HIỆN TẠI vs MÔ HÌNH ĐỀ XUẤT

| Thành phần vNext | Hiện trạng | Khoảng cách |
|---|---|---|
| Home = một việc | thẻ đề xuất + 5 chip | **vừa** — bớt đi, không thêm |
| Giá sách | ✅ có, chạy máy thật | không |
| Book Home = mục lục có trạng thái | ✅ gần đúng | nhỏ |
| **Ý định tại bài** | ❌ **không có** | **lớn — ưu tiên 1** |
| SAM đề nghị ý định theo TKB | ❌ TKB có, chưa dùng để suy ý định | **lớn** |
| Chuẩn bị (quan sát → dự đoán) | một phần (thí nghiệm có dự đoán) | vừa |
| Ôn theo bằng chứng | ✅ có resolver + màn ôn | nhỏ |
| Camera → confirm → thang gợi ý | ✅ đủ | nhỏ |
| «Xem trong sách» ở mọi nơi | ❌ chỉ ở vài chỗ | vừa |
| Kết thúc phiên «ghi nhận được gì» | một phần | vừa |
| Surface âm thanh | ❌ không có | **lớn** |
| Mô phỏng tham số (Lí/Hoá) | ❌ không có | lớn (nhưng sau) |
| Phụ huynh: một việc + quyền dữ liệu | ✅ tốt hơn concept | không |
| Nhiều con / máy chung | ✅ đã kiểm máy thật | không |

---

## P. GIẢ ĐỊNH CHƯA ĐƯỢC CHỨNG MINH

Liệt kê thẳng, vì báo cáo này sẽ bị phản biện:

1. **Trẻ sẽ chọn ý định.** Chưa có bằng chứng người dùng. Có thể trẻ luôn bấm cái đầu tiên.
2. **«Chuẩn bị» có giá trị thật.** Giả thuyết sư phạm hợp lý (advance organizer), nhưng chưa
   đo trên trẻ Việt Nam.
3. **Thời khoá biểu đủ chính xác để suy ý định.** Phụ thuộc phụ huynh nhập và giữ đúng. Nếu
   sai, SAM đề nghị sai — **tệ hơn không đề nghị**.
4. **Bỏ gamification không làm giảm quay lại.** Đây là đặt cược lớn nhất và **ngược với phần
   lớn ngành**. Tôi tin nó đúng về đạo đức; tôi **không** có dữ liệu giữ chân.
5. **Một việc mỗi ngày là đủ.** Có thể quá ít với phụ huynh đang trả tiền cho «học thêm».
6. **Trẻ phân biệt được lời sách và lời SAM** khi có nhãn. Cần kiểm với trẻ thật.
7. **Bìa sách đủ để nhận ra cuốn.** Đã chạy tốt trên máy, chưa kiểm với trẻ.
8. Sau khi sửa nạp dữ liệu, **97 cuốn vẫn giữ mục lục cũ** — chưa biết bao nhiêu bài trong đó
   dùng được thật.

---

## Q. CÂU HỎI SẢN PHẨM CÒN MỞ

1. Khi thời khoá biểu **trống**, SAM lấy gì làm mỏ neo? (Tôi đề xuất: không đoán, hỏi thẳng.)
2. Trẻ lớp 1–3 **chưa đọc trôi** — bao nhiêu phần trải nghiệm cần **giọng nói**? Nếu nhiều thì
   SAM Voice không phải ưu tiên thấp mà là **điều kiện cần** cho lứa đó.
3. Sản phẩm phục vụ **một lứa hay cả K–12**? Trải nghiệm lớp 2 và lớp 11 gần như không thể
   chung một Home. Tôi nghiêng về **chọn một lứa để đúng trước** (lớp 4–6).
4. Khi SAM **chưa dạy được** một bài (đa số), trải nghiệm tối thiểu tử tế là gì? Hiện là một
   câu xin lỗi lặp lại.
5. Bài tập trẻ chụp mà **không thuộc SGK** (phiếu, đề cô ra) — có phải phần lớn ca dùng thật
   không? Nếu đúng thì **camera**, không phải giá sách, mới là trục chính.
6. Phụ huynh có thật sự làm «việc tối nay ~10 phút» không? Nếu không, phần phụ huynh nên là
   **báo cáo tuần** chứ không phải lời mời hằng ngày.
7. «Kiểm tra hiểu bài» do **trẻ** mở hay do **SAM** mở khi đủ bằng chứng?

---

## R. BẤT ĐỒNG MẠNH NHẤT VỚI FOUNDER

**R1. «Xem sách» không nên là mode.** Nó là lớp phủ. Đặt ngang hàng sẽ tạo một lối thoát
không sinh bằng chứng, và trẻ sẽ chọn nó.

**R2. Ý định phải gắn vào BÀI, không vào CUỐN SÁCH.** Hỏi ở mức sách là hỏi sai đơn vị: các
bài trong một cuốn ở trạng thái khác nhau. Đây là bất đồng kỹ thuật-sản phẩm quan trọng nhất
của tôi với đề xuất hiện tại.

**R3. Camera là toàn cục, không thuộc sách.** Phần lớn thứ trẻ chụp không nằm trong SGK.

**R4. Đừng hỏi trẻ chọn mode — hãy ĐỀ NGHỊ, rồi cho đổi.** «Hôm nay con muốn làm gì?» đẩy gánh
nặng siêu nhận thức sang đứa trẻ, đúng lúc nó ít có khả năng nhất. SAM có thời khoá biểu và
bằng chứng — **nó nên đoán trước, và chịu trách nhiệm về phỏng đoán đó**.

**R5. 38 concept không phải nền tảng để xây tiếp.** Chúng là một sản phẩm **khác** — hay, đẹp,
nhưng vận hành trên mô hình đo lường + phần thưởng mà Founder đã bác bỏ trong chính doctrine
của mình. Dùng chúng làm spec sẽ kéo sản phẩm ngược lại. Nên đối xử với chúng như **thư viện ý
tưởng** (giữ 09, 16, 23-công-cụ, 25-mô-phỏng) chứ không phải bản thiết kế.

**R6. «AI Learning» nên bỏ hẳn.** Ngoài chương trình, có xếp hạng trẻ em, đẩy trẻ tới chatbot
đa dụng. Nếu muốn dạy AI cho trẻ, đó là **sản phẩm khác**.

**R7. Lớp 10 hiện là lời hứa suông.** Duyệt được 41 cuốn nhưng không được dạy gì. Hoặc đầu tư
nội dung cho một lứa THPT, hoặc **nói rõ SAM là sản phẩm tiểu học** — trạng thái nửa vời hiện
nay là tệ nhất cho niềm tin.

---

## S. KHUYẾN NGHỊ CUỐI

**1. Chốt mô hình trước, đừng chốt màn hình.** Câu cần chốt: *SAM đề nghị một việc dựa trên
sách + lịch + bằng chứng, và im lặng khi không có căn cứ.* Mọi màn suy ra từ đó.

**2. Việc đáng làm nhất kế tiếp là NỐI Ý ĐỊNH XUYÊN SUỐT**, không phải thêm màn. Cụ thể: ý
định chọn ở **bài**, SAM **đề nghị trước**, và ý định **định hình** hoạt động + bằng chứng.
Đây là thay đổi đắt nhất về giá trị và rẻ nhất về mã — kiến trúc đã sẵn sàng (`LessonActivity`,
`classifyCase`, `MethodHints`, evidence kernel).

**3. Chọn một lứa để đúng trước.** Tôi đề xuất **lớp 4–6**: đọc trôi, tự dùng máy được, có bài
tập về nhà thật, và corpus lớp 5 đang mạnh nhất.

**4. Giữ nguyên các bất biến trung thực.** Không điểm, không %, không XP/chuỗi, không so sánh
anh chị em. Đây là **khác biệt cạnh tranh**, không phải hạn chế — và nó là lý do duy nhất một
phụ huynh nên tin cái app này hơn một app luyện đề.

**5. Ba lỗ hổng phải thừa nhận công khai**: âm thanh (ngoại ngữ + nói–nghe), mô phỏng (Lí/Hoá),
và **đa số bài chưa dạy được**. Không lỗ nào giải được bằng UI.

**6. Đừng implement báo cáo này nguyên khối.** Thứ đáng làm đầu tiên là **một lát cắt dọc**:
một bài, một ý định được đề nghị, một hoạt động, một bằng chứng, đo trên máy thật với một đứa
trẻ thật. Nếu trẻ không dùng ý định, phần còn lại của mô hình sai.

---

*Bằng chứng thiết bị của vòng này: `~/Desktop/wal-evidence/REVIEW-*`, `GATE2-*`, `MAIN-*`.
Không có thay đổi mã sản phẩm nào trong vòng này.*
