# SAM — Product Experience Convergence

Claude × GPT × Founder. Mục tiêu: **một mô hình sản phẩm và một ngôn ngữ chung** trước khi
viết thêm code. Không code trong vòng này.

Tài liệu này thay thế mục F–I của `SAM-PRODUCT-EXPERIENCE-REVIEW.md` (phần đề xuất). Các mục
chẩn đoán A–E, M, N của báo cáo cũ **vẫn giữ nguyên hiệu lực** — không bên nào phản đối chúng.

**Tôi đổi ý ở 5/10 tranh luận.** Chỗ nào GPT đúng tôi nói đúng; chỗ nào tôi vẫn giữ, tôi nói
rõ lý do và điều kiện có thể bác bỏ tôi.

---

## 1. NGÔN NGỮ CHUNG

Ngắn, đủ dùng, và **bỏ bớt một từ**.

| Từ | Định nghĩa chốt | Tầng |
|---|---|---|
| **BOOK** | Một cuốn sách in có thật, có định danh nguồn (`sourceDocumentId`) và bìa thật. Đơn vị **nhận ra** của trẻ. | Content |
| **SUBJECT** | Môn học. **Chiều ngữ cảnh + liên tục học tập**, không phải màn duyệt của trẻ. Một môn có thể có nhiều book. | Domain |
| **LESSON** | Một mục có định danh trong một book (`LessonKey` = sách + số + trang in). Đơn vị **của sách**, không phải đơn vị trải nghiệm. | Content |
| **ACTIVITY** | Một việc học có thật trong bài (đọc / viết / thí nghiệm / bài tập / tư liệu). **Đơn vị trải nghiệm nhỏ nhất.** | Content |
| **LEARNING INTENT** | Điều **người học muốn đạt được lúc này**: chuẩn bị · ôn · nhờ giúp bài tập · tra cứu. Thuộc về **người**, không thuộc về nội dung. | User intent |
| ~~LEARNING MODE~~ | **BỎ.** Trùng với INTENT và là nguyên nhân chính của tranh luận #1. Không dùng lại từ này. | — |
| **CAPABILITY** | Năng lực kỹ thuật gọi được từ nhiều nơi: camera, giọng nói, hỏi SAM, xem sách. **Không phải** ý định, **không phải** màn. | Capability |
| **EXPERIENCE PATTERN** | Hình dạng sư phạm của một hoạt động (EP-001…EP-006). Chọn ở mức **ACTIVITY × INTENT**. | Pedagogy |
| **SURFACE** | Primitive tương tác (ô nhập, thang gợi ý, cổng dự đoán, trình đọc tư liệu, mô phỏng, ghi âm). **Không mang sư phạm.** | UI |
| **NEXT BEST ACTION** | Đề xuất **suy ra** từ tín hiệu có thật (đã có trong mã: `LearningAgenda`, signals→resolve, `rest` là output hạng nhất). | State |
| **SAM** | Nhân vật + hành vi: đề nghị, hỏi, im lặng, nhận sai, quay lại chỗ vướng. **Không phải** một tab. | Relationship |
| **EVIDENCE** | `LearningEvent` từ hành vi thật (tự làm / xin gợi ý / được gợi ý / tự sửa / chốt). | State |
| **STUDENT STATE** | Suy từ evidence: đã kiểm gì · chưa kiểm gì · tự làm hay có hỗ trợ. **Không phải một con số.** | State |
| **TRACE** *(thêm mới)* | Dấu vết sử dụng **không phải bằng chứng học**: đã mở bài, đã xem trang. Dùng để SAM nhớ ngữ cảnh, **cấm** dùng để kết luận trẻ biết gì. | State |

**Ba bất đẳng thức phải nhớ:**
`INTENT ≠ CAPABILITY ≠ SURFACE` · `LESSON ≠ ACTIVITY` · `TRACE ≠ EVIDENCE`

---

## 2. NGUYÊN TẮC SẢN PHẨM ĐÃ HỘI TỤ

Chỉ liệt kê thứ **cả ba** đã đồng ý.

1. 38 concept là **thư viện nghiên cứu**, không phải đặc tả.
2. **Không**: điểm số, phần trăm hiểu bài bịa, XP, cấp, chuỗi ngày, xếp hạng, so sánh anh chị
   em, lộ trình khoá cứng.
3. SAM **chỉ nói điều có bằng chứng**; thiếu bằng chứng thì nói là chưa kiểm.
4. Sách in thật (bìa, trang, tên bài) là **mỏ neo nội dung**.
5. Cùng nội dung + khác ý định ⇒ khác trải nghiệm.
6. Camera **không bao giờ** là «chụp → đáp án»; luôn có bước **trẻ xác nhận**.
7. **Lời sách** và **lời SAM** phải tách bạch ở mọi nơi.
8. Trải nghiệm theo môn là cần thiết; **màn hình riêng theo môn thì không**.
9. Kiến trúc K–12 giữ nguyên; **UX được phép validate theo một cohort trước**.
10. Trẻ **phải giữ quyền tự quyết**: AI đề nghị, không áp đặt.

---

## 3. BẢNG GIẢI QUYẾT TRANH LUẬN

| # | Chủ đề | Kết luận | Tầng của bất đồng |
|---|---|---|---|
| 1 | Read / Explore | **AGREE WITH MODIFICATION** (GPT đúng) | tôi lẫn *user intent* với *pedagogical layer* |
| 2 | Lesson ↔ Intent | **REJECT đề xuất cũ của tôi** (GPT đúng) | tôi lẫn *domain model* với *navigation* |
| 3 | Camera | **AGREE** + một điều kiện an toàn | capability |
| 4 | Home | **AGREE WITH MODIFICATION** (GPT đúng về chữ, tôi đúng về ý) | navigation |
| 5 | Subject | **AGREE WITH MODIFICATION** (GPT đúng ở domain, tôi đúng ở UI trẻ) | domain vs navigation |
| 6 | Gamification | **AGREE WITH MODIFICATION** + hai phép thử quyết định được | motivation |
| 7 | SAM persona | **AGREE — GPT bắt đúng lỗi lớn của tôi** | relationship |
| 8 | Giá trị 38 concept | **AGREE** — tôi đã đánh giá thấp | research |
| 9 | Cohort | **AGREE WITH MODIFICATION** — thu hẹp còn **lớp 4–5** | validation |
| 10 | Anchor | **AGREE + formalize** + luật ưu tiên khi xung đột | product |

---

### Tranh luận #1 — READ / EXPLORE

**Tôi nói:** không phải mode, chỉ là lớp phủ.
**GPT nói:** là *user intent* hợp lệ, nhưng không phải *learning mode*; xuất hiện cả ở Book
Home lẫn overlay trong phiên học.
**Ý Founder phía dưới cả hai:** trẻ có quyền chỉ mở sách ra xem, và SAM không nên ép mọi lần
mở app thành một buổi học.

**Ai đúng ở đâu.** GPT đúng. Tôi đã **trộn hai câu hỏi khác tầng**: «đây có phải việc thật của
người dùng không» (có — hiển nhiên) và «nó có phải một chế độ sư phạm không» (không). Vì trộn,
tôi kết luận sai rằng nó không được là lối vào hạng nhất.

Điều tôi **vẫn giữ**: trong một bộ chọn, «xem sách» đặt **ngang hàng thị giác** với «học» sẽ
lệch hành vi — nó là lựa chọn rẻ nhất về nỗ lực. Đây là khẳng định về **trọng số UI**, không
phải về tính chính đáng, và nó **kiểm được**.

**Chốt.**
- Read là **LEARNING INTENT hạng nhất** ✅
- Read **không** là Experience Pattern, **không** có assistance policy, **không** sinh EVIDENCE ✅
- Read sinh **TRACE** (đã mở bài 3, đã xem trang 14) — để SAM nhớ ngữ cảnh, **cấm** suy ra
  hiểu biết. *(Đây là phần cả tôi lẫn GPT đều chưa nói: nếu không có TRACE, SAM sẽ quên; nếu
  TRACE bị tính là EVIDENCE, SAM sẽ nói dối.)*
- Read có mặt: ở **Book Home** (hành động), và **luôn có** trong mọi phiên học («Xem chỗ này
  trong sách») ✅
- Trong bộ chọn tại bài: Read đứng **cuối và nhẹ hơn** về thị giác. Nếu đo được trẻ vẫn học
  bình thường khi Read ngang hàng, tôi rút điều kiện này.

---

### Tranh luận #2 — LESSON ↔ INTENT *(quan trọng nhất)*

**Tôi nói:** Book → Lesson → Intent, vì mỗi bài một trạng thái.
**GPT nói:** Lesson và Intent là **hai chiều**, không phải cha–con; có hai lối vào; Next Best
Action có thể đã giải cả hai.
**Ý Founder:** đừng để implementation hiểu theo ba cách.

**Tôi sai, và sai ở chỗ nào.** Lý lẽ của tôi («trạng thái khác nhau theo bài») là lý lẽ về
**cách giải ý định**, không phải về **thứ tự điều hướng**. Tôi đã biến một sự thật dữ liệu
thành một ràng buộc UI. Trẻ nghĩ «con muốn ôn Toán» trước khi biết «Bài 6» — bắt nó chọn bài
trước là bắt nó trả lời câu khó hơn trước.

**Nhưng «hai chiều» một mình thì chưa đủ để implementation khỏi lệch.** Thiếu thứ neither of us
nói ra: **hợp đồng ràng buộc**.

**Chốt — LEARNING CONTEXT là mô hình chuẩn, không phải một thứ tự.**

```
LearningContext = { learner, subject, book, lesson|activity, intent, state, timetable, evidence }
```

**Luật ràng buộc (đây là thứ chốt để ba bên không hiểu khác nhau):**

1. Trải nghiệm **chỉ bắt đầu khi context đã ràng buộc đủ**: tối thiểu `activity` + `intent`.
2. Chiều nào **đã biết** thì giữ; chiều nào **thiếu** thì UI giải.
3. Chiều thiếu do **SAM đề nghị**, kèm **lý do nhìn thấy được**; trẻ **đổi được mọi chiều đã
   ràng buộc**.
4. ⭐ **Fail closed**: nếu SAM không có căn cứ thật (không evidence, không timetable), nó
   **không được đoán** chiều đó — phải hỏi. Cụ thể: intent-first mà không có căn cứ ⇒ hiện
   danh sách bài của cuốn để trẻ chọn, **không** tự chọn hộ một bài.
5. **Không** có thứ tự chuẩn. Có **ba lối vào hợp lệ ngang nhau**:

| Lối | Trẻ biết trước | SAM giải | Ví dụ |
|---|---|---|---|
| A · biết bài | book + lesson | intent | mở Khoa học 5 → Bài 1 → «Mai có tiết này» |
| B · biết mục tiêu | intent (± subject) | lesson | «Con muốn ôn Toán» → SAM chọn theo bằng chứng |
| C · Next Best Action | *(không gì)* | cả hai | Home: «Mai có Khoa học. Xem trước Bài 3 · ~7 phút» |

**Bằng chứng đã có trong mã:** `lib/core/agenda/learning_agenda.dart` đã làm đúng lối C —
signals → resolve, `rest` là output hạng nhất, thời khoá biểu **chỉ phá hoà** chứ không thắng
tín hiệu mạnh hơn, và mọi action truy được về tín hiệu sinh ra nó. Nghĩa là **lối C không phải
tính năng mới** — nó đã có và đúng doctrine, chỉ chưa được nối vào luồng của trẻ.

---

### Tranh luận #3 — CAMERA

**Đồng ý với GPT:** Camera là **CAPABILITY**, có **lối vào toàn cục** *và* **lối tắt trong
bài**.

**Một điều kiện tôi thêm — và nó quan trọng:** ngữ cảnh gắn sẵn ở lối tắt là **giả thuyết,
không phải sự thật**. Trẻ bấm «chụp bài này» từ Bài 6 vẫn có thể chụp nhầm trang khác, hoặc
chụp phiếu bài tập. Vậy:

- Bước xác nhận (concept 09) **luôn chạy**, kể cả khi context đã gắn sẵn.
- Nếu nhận diện **mâu thuẫn** với context gắn sẵn ⇒ **ưu tiên thứ nhận diện được**, và **nói
  ra** («Cái này trông không giống Bài 6 — con muốn tiếp tục ở đâu?»).
- **Cấm** dùng context gắn sẵn để *ép* phân loại bài chụp — đó chính là đường ngắn nhất tới
  provenance sai (đúng họ lỗi WAL-170 đã sửa ở tầng dữ liệu).

Kết quả camera vào hệ thống qua **giải ngữ cảnh**: nhận diện → xác nhận → thử ràng buộc
`lesson`/`activity`; không ràng buộc được thì **nói thẳng là chưa dạy được bài này**, không
mượn chương trình của bài khác.

---

### Tranh luận #4 — HOME

**GPT đúng về chữ, tôi đúng về ý.** «One task» của tôi dễ bị đọc thành «AI quyết định thay
trẻ». Cụm **recommendation-first** chính xác hơn.

**Chốt — Home có bốn thành phần cố định, không hơn:**

1. **Một đề xuất chính**, kèm **lý do nhìn thấy được** («Mai có Khoa học», «Hôm qua con cần 2
   lần gợi ý ở phần này»). Đúng **một**, không phải danh sách xếp hạng.
2. **Ba lối thoát ổn định**: 📷 Chụp bài · 📚 Sách của con · 💬 Hỏi SAM.
3. **Không** bề mặt số liệu nào.
4. Không có căn cứ ⇒ **nói là không có** («Hôm nay không có gì gấp»), rồi để ba lối thoát làm
   việc của chúng. `rest` đã là output hạng nhất trong `LearningAgenda` — giữ.

**Hai luật giữ cho nó không trượt về dashboard:**
- ⭐ **Lối thoát BẤT BIẾN**: luôn cùng vị trí, cùng thứ tự, mọi ngày. Chỉ *đề xuất* đổi. Trẻ
  xây được trí nhớ cơ bắp; agency là thứ **luôn ở đó**, không phải thứ phải đi tìm.
- ⭐ **Một đề xuất một lý do**: đề xuất nào không nêu được lý do truy về tín hiệu thì **không
  được hiện**.

---

### Tranh luận #5 — SUBJECT vs BOOKSHELF

**GPT đúng ở tầng domain. Tôi đúng ở tầng UI của trẻ.** Hai điều này không mâu thuẫn — tôi đã
phát biểu quá rộng («bỏ Subjects») khi ý tôi hẹp hơn («trẻ không duyệt theo môn trừu tượng»).

**Chốt:**

| Câu hỏi | Trả lời |
|---|---|
| Có màn **Subjects** cho trẻ duyệt không? | **Không.** Giá sách đã giải quyết việc nhận ra. Thêm một tầng trừu tượng là thêm một bước không giúp gì. |
| Có **SUBJECT CONTEXT** trong domain model không? | **Có, hạng nhất.** Liên tục học tập là **theo môn**, không theo cuốn: Toán 5 tập 1 → tập 2 không được làm đứt mạch bằng chứng. |
| Book Home và Subject Home có trùng? | **Có** — nên chỉ giữ **Book Home**. |
| Nhiều sách cùng môn thì trẻ đi đâu? | Giá sách xếp **các tập cạnh nhau theo thứ tự tập** (đã làm ở WAL-167). |
| Lịch sử / tiến trình / bằng chứng theo môn nằm ở đâu? | **Phần Bố mẹ** và **luồng ôn** («con đang vướng ở Toán»), không phải màn duyệt của trẻ. |

Subject là **chiều ngữ cảnh**, không phải **thực thể điều hướng**.

---

### Tranh luận #6 — GAMIFICATION

**GPT đúng rằng «no gamification» là doctrine quá thô.** Ăn mừng đúng chỗ là sư phạm tốt, và
SAM là một tài sản đang bị bỏ phí. Nhưng «tránh gây nghiện» không **quyết định được** — cần
phép thử.

**Chốt — nguyên tắc: ăn mừng HÀNH VI tạo ra việc học, không bao giờ ăn mừng CON SỐ.**

Hai phép thử, áp cho mọi ý tưởng tạo động lực:

> **Phép thử 1 — KHEN CÓ THỂ SAI KHÔNG?**
> Câu khen phải gắn với **một sự kiện có thật trong evidence log**, tới mức nếu nó sai thì trẻ
> nhận ra ngay. «Lần đầu con tự làm dạng này mà không cần gợi ý» — kiểm được. «Con giỏi lắm!»
> — không kiểm được, là tiếng ồn. Khen bịa là nói dối.

> **Phép thử 2 — NGHỈ BA NGÀY CÓ MẤT GÌ KHÔNG?**
> Nếu tính năng tạo ra **mất mát vì vắng mặt** (chuỗi ngày, cây héo, điểm rơi hạng), nó tối ưu
> engagement chứ không tối ưu học. Loại.

| Được | Không được |
|---|---|
| SAM vui khi trẻ **tự sửa** | chuỗi ngày, nhắc «giữ phong độ» |
| «Lần này con cần **ít gợi ý hơn** lần trước» | %, điểm, XP, cấp |
| Cột mốc cá nhân: **lần đầu tự làm được** một dạng | huy hiệu theo số lượng, xếp hạng |
| Khoảnh khắc kết thúc rõ ràng («xong rồi») | vật phẩm sưu tầm mở khoá nội dung |
| SAM đổi biểu cảm theo tình huống thật | ăn mừng mọi thao tác |

Ranh giới một câu: **phần thưởng phải là chính năng lực vừa đạt được**, không phải một thứ dán
lên trên nó.

---

### Tranh luận #7 — SAM PERSONA

**GPT bắt đúng, và đây là lỗi lớn nhất trong báo cáo trước của tôi.** Mô hình tôi viết đúng về
IA nhưng biến SAM thành *dịch vụ gợi ý + bộ chấp hành sư phạm*. Sản phẩm tên là **Học cùng
SAM**; nếu SAM chỉ là giọng nói của engine thì cái tên là sai.

**Nguyên tắc tôi đề xuất:**

> ⭐ **Sự hiện diện của SAM tỉ lệ NGHỊCH với năng lực của trẻ ngay lúc đó.**
> Có mặt lúc bắt đầu, lúc bí, lúc kết thúc. **Biến mất** trong lúc trẻ đang nghĩ.

| SAM **có mặt** | SAM **biến mất** |
|---|---|
| chào có ngữ cảnh («hôm qua con vướng chỗ này») | trong lúc trẻ đọc đoạn văn nguồn |
| đề nghị một việc + nói lý do | trong lúc trẻ đang thử làm |
| hỏi **dự đoán** trước khi lộ kết quả | trong bài kiểm tra hiểu bài |
| đưa gợi ý **theo bậc** khi trẻ đã thử | trong lúc trẻ xem sách |
| nhận ra trẻ **tự sửa** | sau khi trẻ đã làm đúng — lùi lại |
| kết phiên: **SAM ghi nhận được gì** | |
| nói **«SAM chưa chắc»** / **«SAM chưa dạy được bài này»** | |

**Ba thứ dễ nhầm — phân biệt để implementation không trượt:**

- **Bạn học (đúng)**: nhớ **một điều cụ thể** và quay lại đúng chỗ đó; đổi hành vi theo việc
  trẻ vừa làm; **tự rút lui** khi không cần.
- **Chatbot (sai)**: chờ trẻ gõ; trả lời mọi thứ; không nhớ bài nào đang mở.
- **Mascot dán lên phần mềm (sai)**: xuất hiện ở mọi màn, nói câu động viên chung chung, không
  đổi gì theo hành vi.

**Phép thử một câu:** *Nếu bỏ SAM khỏi màn này mà không mất thông tin nào, thì SAM ở đó chỉ là
hình dán.*

Ghi chú: cả «Hỏi SAM» phải **mang theo ngữ cảnh đang mở**. Một ô chat không biết trẻ đang ở
bài nào chính là định nghĩa của chatbot.

---

### Tranh luận #8 — 38 CONCEPT DÙNG THẾ NÀO

**GPT đúng, tôi đã đánh giá thấp.** Tôi nêu 4, danh sách đúng dài hơn.

**Ba tầng tách bạch — một concept có thể trượt tầng này và đạt tầng kia:**

| Tầng | Nghĩa | Lấy từ 38 concept? |
|---|---|---|
| **PRODUCT MODEL** | sản phẩm này *là gì*, đo cái gì, thưởng cái gì | ❌ **không lấy gì** — đây là chỗ 38 concept sai hệ thống |
| **INTERACTION IDEA** | một tương tác cụ thể giải một việc học cụ thể | ✅ **nguồn giá trị chính** |
| **VISUAL LANGUAGE** | màu, chữ, nhân vật, giọng văn | ✅ lấy có chọn lọc (nhân vật + giọng nói với trẻ rất tốt) |

| Concept | Ý tương tác giữ lại |
|---|---|
| 09 Camera Confirm | ảnh → chữ đọc được (sửa được) → **SAM xác định** → trẻ xác nhận |
| 14 Your Turn | trả lượt cho trẻ sau khi bắc thang |
| 16 Why This Method | «vì sao cách này đúng» bằng **biểu diễn trực quan** (hình chia phần) |
| 18 Review | ôn quay lại **đúng chỗ vướng** |
| 23 Tiếng Việt | **công cụ theo hoạt động** (chính tả / đặt câu / đọc hiểu / viết đoạn) |
| 24 Essay | viết có dàn ý + checklist, **không có bài mẫu** |
| 25 Physics | **mô phỏng có tham số** + đồ thị đồng bộ |
| 27 History | đọc **tư liệu gốc** rồi lập luận trên nó |
| 28 Geography | **bản đồ/dữ liệu tương tác** (phóng, chỉ điểm, đọc số liệu) |
| 35 SAM Voice | giọng nói — **điều kiện cần** cho lứa chưa đọc trôi |

**Luật dùng về sau:** khi mở một concept để lấy ý, **bắt buộc** ghi lại nó trượt tầng PRODUCT
MODEL ở đâu (ví dụ: «25 Physics — giữ mô phỏng, bỏ 72% và điểm 86/100»), để ý tưởng không kéo
theo mô hình sai.

---

### Tranh luận #9 — K–12 vs COHORT

**Đồng ý với khung của GPT**, thu hẹp cohort.

```
TẦM NHÌN SẢN PHẨM      = K–12
KIẾN TRÚC / TRI THỨC   = K–12   (giữ nguyên, không đụng)
ĐƯỜNG ỐNG NỘI DUNG     = K–12
COHORT KIỂM CHỨNG UX   = LỚP 4–5 trước
```

**Vì sao 4–5 chứ không 4–6** (sửa đề xuất cũ của tôi): lớp 6 là **chuyển cấp** — đổi trường,
đổi cách tổ chức môn, đổi mức tự chủ. Gộp 4–6 là trộn hai bài toán UX vào một lần kiểm chứng.
Lớp 4–5 là **một cấp, một kiểu thời khoá biểu, một kiểu bài tập về nhà**, trẻ **đọc trôi** (khác
lớp 1–3), và corpus lớp 5 đang mạnh nhất. Sau khi 4–5 đúng, **lớp 6 là phép thử mở rộng đầu
tiên** vì nó bẻ gãy đúng các giả định của tiểu học.

| Được phép tổng quát hoá | Bắt buộc thích ứng theo tuổi |
|---|---|
| mô hình bằng chứng, provenance | **lượng chữ** trên màn |
| mô hình ý định + ràng buộc ngữ cảnh | **giọng nói** (bắt buộc ở lớp 1–3) |
| luồng camera + xác nhận | **độ dài phiên** |
| khung IA (3 mục) | **mức nổi của nhân vật SAM** |
| luật im lặng của SAM | vai trò phụ huynh (đậm ở lớp nhỏ) |

**Tránh làm UI quá trẻ con:** nhân vật SAM phải là **cường độ điều chỉnh được**, không phải
thứ để gỡ bỏ — cùng một hệ thống, lớp nhỏ SAM nói nhiều và to hơn, lớp lớn SAM lùi về gần như
chỉ còn giọng văn. Nếu phải **thiết kế lại** cho THPT thì mô hình sai; nếu chỉ phải **chỉnh
tham số** thì đúng.

---

### Tranh luận #10 — ANCHOR

**Bốn mỏ neo của GPT đúng.** Tôi formalize thêm phần thiếu: **luật ưu tiên khi chúng xung
đột** — không có luật này thì implementation lại lệch.

| Mỏ neo | Trả lời câu hỏi | Hiện ra ở đâu |
|---|---|---|
| **BOOK** | «kiến thức này ở đâu ra» | giá sách, provenance, «xem trong sách» |
| **CAMERA** | «việc thật trước mặt con là gì» | lối vào toàn cục + lối tắt trong bài |
| **NEXT BEST ACTION** | «hôm nay làm gì» | Home |
| **SAM** | «con học **cùng ai**» | hành vi xuyên suốt, không phải một tab |

**Luật ưu tiên khi chọn đề xuất — theo thứ tự, dừng ở cái đầu tiên có căn cứ thật:**

```
1. Bằng chứng      (có chỗ vướng / đến hạn ôn)      → ôn
2. Thời khoá biểu  (mai có tiết này)                → chuẩn bị
3. Trạng thái sách (đang dở giữa chừng)             → tiếp tục
4. KHÔNG CÓ GÌ     → nói là không có; không bịa đề xuất
```

Đây đúng là thứ tự `LearningAgenda` đang làm (thời khoá biểu chỉ phá hoà, `rest` hạng nhất) —
tức là **luật này đã được kiểm chứng trong mã**, không phải ý tưởng mới.

**Câu hỏi «book-first hay camera-first» thì tôi không trả lời được bằng suy luận** — xem mục
24. Nhưng cấu trúc trên **không cần** câu trả lời đó để triển khai: cả hai đều là lối thoát ổn
định trên Home, và dữ liệu dùng thật sẽ nói cái nào nặng hơn.

---

## 4. MÔ HÌNH TRẢI NGHIỆM CHỐT

```
                          SAM HOME
                    (Next Best Action + 3 lối thoát ổn định)
                              │
        ┌─────────────────────┼─────────────────────┐
     📷 Camera            📚 Giá sách            💬 Hỏi SAM
        │                     │                     │
        │                   Book                    │
        │                     │                     │
        │              Lesson / Activity            │
        │                     │                     │
        └────────────► LEARNING CONTEXT ◄───────────┘
             { learner · subject · book · activity ·
               INTENT · state · timetable · evidence }
                              │
                 ràng buộc đủ? → thiếu thì SAM giải, có lý do
                              │
                    ACTIVITY × INTENT
                              │
                     EXPERIENCE PATTERN
                              │
                          SURFACE(s)
                              │
                    SAM (có mặt / im lặng)
                              │
                  EVIDENCE  ·hoặc·  TRACE
                              │
                       STUDENT STATE
                              │
                     NEXT BEST ACTION → Home
```

**Điểm khác cốt lõi so với cả hai bản trước:** không có mũi tên cố định từ Lesson sang Intent.
Cả hai là **chiều của Learning Context**, và **luật ràng buộc** ở tranh luận #2 là thứ chốt.

---

## 5. IA CHỐT

Một thanh dưới, **ba** mục:

```
[ Hôm nay ]        [ Sách của con ]        [ Bố mẹ ]
```

- **Hôm nay** — một đề xuất + ba lối thoát cố định (📷 · 📚 · 💬).
- **Sách của con** — giá sách → book → mục lục bài → *(ý định)* → hoạt động.
- **Bố mẹ** — sau PIN: một điều về mỗi con, một việc tối nay, tiến trình theo môn, quyền dữ liệu.

**Bỏ khỏi thanh dưới:** Tiến bộ (chuyển sang Bố mẹ + cuối phiên), Thư viện, Quiz, Thành tích,
Messages, và **nút SAM nổi ở giữa** (nó quảng cáo «chat với AI» là hoạt động chính — sai định
vị; SAM sống trong luồng, không trong tab).

---

## 6. HOME

Xem tranh luận #4. Bốn thành phần, hai luật (lối thoát bất biến · một đề xuất một lý do).

---

## 7. BOOK / SUBJECT

Xem tranh luận #5. **Book** = nhận ra + provenance. **Subject** = ngữ cảnh + liên tục, không
phải màn duyệt. **Book Home** = mục lục có trạng thái, không %, không khoá, không sao.

---

## 8. GIẢI RÀNG BUỘC BÀI + Ý ĐỊNH

Bốn ý định, đặt tên theo **tình huống của trẻ**, không theo từ vựng sư phạm:

| Ý định | Trẻ đọc thấy | Hình dạng | Sinh ra |
|---|---|---|---|
| **Chuẩn bị** | «Mai có tiết này» | quan sát → **dự đoán** → điều cần chú ý trên lớp | evidence (dự đoán, **không chấm đúng/sai**) |
| **Ôn lại** | «Cô dạy rồi» | nhớ lại → giải thích → làm thử → bắt lỗi hiểu sai | evidence |
| **Bài tập** | «Con có bài tập» | chụp → xác nhận → chẩn đoán → thang gợi ý → tự làm | evidence |
| **Tra cứu** | «Xem trong sách» | trang · hình · tư liệu gốc + gloss **có nhãn riêng** | **TRACE** (không phải evidence) |

Ba lối vào A/B/C ở tranh luận #2. Luật fail-closed: **không có căn cứ thì hỏi, không đoán.**

---

## 9. CAMERA

CAPABILITY. Toàn cục + lối tắt trong bài. Xác nhận **luôn chạy**. Context gắn sẵn là **giả
thuyết**; nhận diện mâu thuẫn thì **nói ra**. Không ràng buộc được bài ⇒ **nói thẳng chưa dạy
được**, không mượn chương trình bài khác.

---

## 10. ĐỌC / TRA CỨU

LEARNING INTENT hạng nhất · **không** phải Experience Pattern · sinh **TRACE** không sinh
EVIDENCE · có ở Book Home **và** trong mọi phiên học · trong bộ chọn thì đứng cuối, nhẹ hơn về
thị giác (điều kiện có thể bị bác bỏ bằng đo đạc).

---

## 11. MÔ HÌNH TƯƠNG TÁC CỦA SAM

Xem tranh luận #7. Nguyên tắc: **hiện diện tỉ lệ nghịch với năng lực lúc đó**. Phép thử: *bỏ
SAM khỏi màn này mà không mất thông tin ⇒ SAM ở đó là hình dán.* «Hỏi SAM» **luôn mang ngữ
cảnh đang mở**.

---

## 12. TRẢI NGHIỆM THEO MÔN

Không màn riêng theo môn. **Surface** riêng theo họ hoạt động:

| Họ hoạt động | Surface | Trạng thái |
|---|---|---|
| Giải bài có đáp số (Toán, Lí, Hoá) | ô nhập + thang gợi ý + provenance | ✅ có |
| Đọc hiểu (TV, Văn, Sử) | đoạn verbatim + câu hỏi mở + `correct: null` | ✅ có |
| Viết (TV, Văn, Anh) | đề + checklist, **không bài mẫu** | ✅ có |
| Thí nghiệm (Khoa, Lí, Hoá, Sinh) | chuẩn bị · **cổng dự đoán** · ô quan sát | ✅ có |
| Tư liệu gốc (Sử, GDCD) | trích + attribution + gloss **nhãn riêng** | ✅ có |
| Hình/bản đồ/dữ liệu (Địa, Sinh, Toán) | ảnh nguồn có provenance; **bản đồ tương tác** | một phần |
| **Nghe – nói (Anh, TV)** | **audio + ghi âm** | ❌ **thiếu hẳn** |
| **Quan hệ đại lượng (Lí, Hoá)** | **mô phỏng có tham số** (concept 25) | ❌ thiếu |
| Biểu diễn / tạo tác (Nhạc, Mĩ thuật, GDTC) | nộp ảnh/âm thanh, **không chấm đúng/sai** | ❌ thiếu |

**Hai lỗ hổng lớn nhất vẫn là: âm thanh và mô phỏng.** Không giải được bằng IA hay UX — cần
surface mới.

---

## 13. K–12 / TUỔI

Xem tranh luận #9. Kiến trúc K–12; kiểm chứng UX **lớp 4–5** trước; lớp 6 là phép thử mở rộng;
SAM là **cường độ điều chỉnh được**, không phải thứ để gỡ.

---

## 14. ĐỘNG LỰC / ĂN MỪNG

Xem tranh luận #6. **Ăn mừng hành vi, không ăn mừng con số.** Hai phép thử: *khen có thể sai
không* · *nghỉ ba ngày có mất gì không*.

---

## 15. 38 CONCEPT DÙNG VỀ SAU

Thư viện nghiên cứu, tách ba tầng (product model ❌ / interaction idea ✅ / visual language ✅
có chọn lọc). Mười concept đáng khai thác ở tranh luận #8. Mỗi lần lấy ý **phải ghi kèm** nó
trượt product model ở đâu.

---

## 16–22. CÁC VÒNG

**16 · Vòng ngày** — mở → **một** đề xuất có lý do → 5–10 phút → «SAM ghi nhận được gì» →
đóng. *Thứ kéo trẻ lại*: bài tập thật tối nay · tiết mai · **SAM nhớ chỗ vướng và hẹn đúng chỗ
đó**. Không phải chuỗi ngày.

**17 · Vòng sách** — giá sách → book → mục lục → *(ý định)* → hoạt động → evidence.

**18 · Vòng chuẩn bị** — bài của tiết mai → quan sát → **dự đoán** → «mai lên lớp con để ý chỗ
này». **Không kiểm tra, không chấm.** Dự đoán vào evidence với `correct: null`.

**19 · Vòng ôn** — SAM nêu chỗ bằng chứng yếu (có dẫn chứng) → nhớ lại → làm thử 1–2 bài → nói
rõ mức chắc chắn, hoặc hẹn lại. Kiểm tra hiểu bài **chỉ mở khi bằng chứng đủ**, không hỗ trợ
trong lúc làm, **trả kết quả theo từng ý** — không điểm tổng.

**20 · Vòng bài tập** — chụp → SAM đọc → **trẻ xác nhận** → giải ngữ cảnh → ngoài phạm vi thì
**nói thẳng** → trong phạm vi: chẩn đoán → thang gợi ý → **trẻ tự làm** → xác nhận → evidence.

**21 · Vòng tra cứu** — mở đúng trang/hình/tư liệu; **lời sách ≠ lời SAM**; «Hỏi SAM» mang ngữ
cảnh; sinh **TRACE**, không sinh evidence.

**22 · Vòng phụ huynh** — **một** điều về mỗi con (có mức chắc chắn) → **một** việc tối nay
~10 phút → tiến trình theo môn → quyền dữ liệu (lấy ra / xoá). **Không bảng số, không so sánh
anh chị em.** *(App hiện tại đã đúng hướng và tốt hơn concept 32/33/34.)*

---

## 23. NHỮNG THỨ SẼ KHÔNG BAO GIỜ XÂY

1. Phần trăm hiểu bài / điểm số / XP / cấp độ hiển thị cho trẻ.
2. Chuỗi ngày học và mọi cơ chế phạt vì vắng mặt.
3. Xếp hạng giữa trẻ em; «Top X%»; bảng xếp hạng.
4. So sánh anh chị em ở bất kỳ đâu trong phần phụ huynh.
5. Lời giải hiện ra **trước** khi trẻ thử.
6. Trẻ tự chọn độ chi tiết gợi ý (mức hỗ trợ là **hệ quả của hành vi**).
7. Liên kết tới trang tra lời giải, hoặc bất cứ gì gọi là «nguồn» mà không phải sách của trẻ.
8. Chatbot đa dụng thay cho luồng học; đưa trẻ tới chatbot bên thứ ba.
9. Dạy phương pháp **ngoài chương trình** của bài đó (ví dụ BCNN ở Toán 5 Bài 6).
10. Khen bịa, hoặc kết luận về hiểu biết khi chỉ có TRACE.
11. Vật phẩm sưu tầm / mở khoá nội dung bằng phần thưởng.
12. Đề xuất không nêu được lý do truy về tín hiệu.

---

## 24. CHƯA GIẢI ĐƯỢC — CẦN BẰNG CHỨNG NGƯỜI DÙNG THẬT

Chỉ liệt kê thứ **thật sự** cần trẻ/phụ huynh, không dùng để né quyết định.

| # | Câu hỏi | Cách giải quyết |
|---|---|---|
| U1 | **Trẻ có dùng ý định không**, hay luôn bấm cái đầu tiên? | Đo tỉ lệ chọn 4 ý định trong 2 tuần; nếu >85% dồn vào đề xuất mặc định thì bộ chọn là thừa — **cắt xuống còn đề xuất + «đổi việc khác»**. |
| U2 | **Camera hay giá sách nặng hơn?** (tranh luận #10) | Đo số lần dùng ba lối thoát ở tuần đầu. Quyết định thứ tự/độ nổi, **không** đổi kiến trúc. |
| U3 | Bỏ gamification có làm giảm quay lại không? | So sánh tần suất quay lại với chính nó theo thời gian; **không** thêm chuỗi ngày để «thử». |
| U4 | «Chuẩn bị» có giúp trẻ hiểu bài trên lớp hơn không? | Cần hỏi trẻ/giáo viên sau tiết. Đây là **giả thuyết sư phạm chưa kiểm**. |
| U5 | Thời khoá biểu có được nhập và giữ đúng không? | Nếu tỉ lệ nhập thấp thì mỏ neo «mai có tiết» sụp, và Home phải dựa hoàn toàn vào evidence. |
| U6 | Lớp 1–3 cần giọng nói tới mức nào? | Quyết định SAM Voice là ưu tiên thấp hay **điều kiện cần**. |
| U7 | Trẻ có phân biệt được lời sách với lời SAM khi có nhãn? | Hỏi trực tiếp trẻ sau khi dùng màn tư liệu. |
| U8 | Phụ huynh có làm «việc tối nay ~10 phút» không? | Nếu không → phần phụ huynh nên là **báo cáo tuần**, không phải lời mời hằng ngày. |

**Không** nằm trong danh sách này (đã đủ căn cứ để chốt, không chờ người dùng): mô hình Learning
Context, luật ràng buộc, camera toàn cục, bỏ màn Subjects, TRACE ≠ EVIDENCE, luật ưu tiên đề
xuất, danh sách mục 23.

---

## 25. KHUYẾN NGHỊ CUỐI

**1. Thứ đã hội tụ đủ để chốt hôm nay:** ngôn ngữ chung (mục 1), 10 nguyên tắc (mục 2), mô
hình Learning Context + luật ràng buộc (mục 4), IA ba mục (mục 5), mục 23 (không xây).

**2. Thay đổi lớn nhất so với báo cáo trước của tôi:** bỏ thứ tự chuẩn Book→Lesson→Intent. Ý
định và bài là **hai chiều**; thứ chốt là **luật ràng buộc + fail-closed**, không phải một cây
điều hướng.

**3. Thứ tôi nhận là mình sai:** Read là intent hạng nhất (tôi lẫn tầng) · Home nên là
recommendation-first (chữ của GPT đúng hơn) · Subject phải giữ trong domain (tôi phát biểu quá
rộng) · «no gamification» là doctrine quá thô · **và lỗi nặng nhất: tôi thiết kế mất SAM** —
biến sản phẩm thành engine gợi ý có mascot.

**4. Thứ tôi vẫn giữ dù bị phản đối:** Read phải nhẹ hơn về thị giác trong bộ chọn (kiểm được
bằng U1) · camera pre-bound chỉ là giả thuyết · lối thoát trên Home phải bất biến vị trí · và
**mục 23 là ranh giới cứng**, không phải sở thích.

**5. Việc đáng làm đầu tiên khi có lệnh code** — không phải thêm màn, mà **nối ý định xuyên
suốt**: `LearningAgenda` đã giải được Next Best Action đúng doctrine nhưng **luồng của trẻ đang
vứt nó đi** ở cửa giá sách. Đó là khoảng cách lớn nhất giữa mã hiện có và mô hình này, và nó
gần như hoàn toàn là **việc nối dây**, không phải việc xây mới.

**6. Cách kiểm chứng:** một lát cắt dọc — **một bài, một ý định được đề nghị, một hoạt động,
một bằng chứng** — đo trên máy thật với một đứa trẻ thật. U1 và U2 trả lời được ngay từ lát
cắt đó. Nếu trẻ không dùng ý định, phần lớn mô hình này sai và phải sửa trước khi mở rộng.

---

*Không có thay đổi mã sản phẩm trong vòng này. Tài liệu này dùng cùng `SAM-PRODUCT-EXPERIENCE-REVIEW.md`
(mục A–E, M, N vẫn hiệu lực) và `SAM-LEARNING-EXPERIENCE-FACTORY.md` (bằng chứng corpus).*
