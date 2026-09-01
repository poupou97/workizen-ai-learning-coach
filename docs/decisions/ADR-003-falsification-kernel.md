# ADR-003 — Bốn lỗ hổng lộ ra khi cố ý phá kernel, và hai lỗ chưa vá

**Ngày:** 2026-09-01 · **Trạng thái:** ACCEPTED (L2, agent tự quyết)
**Bằng chứng:** `test/e2e/falsification_test.dart` · 9 test · 4 phép đột biến đều đỏ

---

## CURRENT

Kernel qua được 39 test và một thin slice end-to-end. Nhưng mọi test đang có đều hỏi
*"kiến trúc có làm được điều ta muốn không?"*. Chưa test nào hỏi *"kiến trúc có nói điều
KHÔNG ĐÚNG không?"*.

## EVIDENCE

Bốn test viết để **thất bại**. Cả bốn đều thất bại thật trên mã cũ — lỗ hổng có thật, đo
được, không phải suy đoán.

### F1 · mastery công bố vượt bằng chứng

Khái niệm ba ca, học sinh luyện kỹ hai ca, ca thứ ba **chưa hỏi lần nào**
⇒ `stateAt()` trả `mastered`.

Nguyên nhân: `derived` lấy `min` trên các ca **CÓ bằng chứng**. ADR-001 chọn `min` với lý
do *"`mean` giấu một ca hỏng sau một ca vững"* — nhưng `min` giấu trọn ca **chưa gặp**.
Tệ hơn: "đã phủ hết ca" và "còn ca chưa hỏi" cho **cùng** một kết luận, nên kết luận đó
không mang thông tin.

Với sản phẩm: Parent Coach nói *"con đã nắm vững quy đồng"* trong khi một phần ba khái
niệm chưa từng được hỏi.

### F2 · phương pháp sai VỀ TOÁN HỌC lọt qua bất biến P0

`fractionCase(5, 5)` → `denominator-divisible`, vì `5 % 5 == 0`.

Nên `3/5 + 1/5` bị xếp vào ca "chia hết" và Tutor nhận *"lấy mẫu số lớn hơn"* — cho một
bài **không có bước quy đồng nào**. Đây đúng ca PHASE 16 gọi tên: *pedagogically available
nhưng mathematically inapplicable*. Bất biến P0 nói phải chặn, mà nó lọt.

Sách xác nhận đây là ca riêng: cộng cùng mẫu số được dạy **trước** quy đồng.

### F3 · gợi ý của Tutor làm nhiễu chính bằng chứng

Test này **không biên dịch được** — và đó chính là phát hiện. `observe(bool)` không có
chỗ nào biểu diễn *"đúng, nhưng sau khi được cho xem lời giải"*.

Hệ quả là một **vòng lặp tự xác nhận**:

```
Tutor gợi ý → trẻ làm đúng → mastery tăng → engine kết luận đã vững
   → thôi gợi ý → trẻ sai → gợi ý lại → ...
```

Can thiệp của chính hệ thống trở thành bằng chứng ủng hộ hệ thống. Đây là lỗi **đo lường**,
không phải lỗi tham số — không tinh chỉnh `slip`/`guess` nào sửa được.

### F4 · lý do hiển thị cho phụ huynh chọn ca tuỳ tiện

`b.strong.first` = phần tử đầu theo **thứ tự chèn của Map**. Với hai ca thì không lộ; với
ba ca thì câu nói với phụ huynh đổi theo việc ai thêm ca nào trước. Đo được: cùng bằng
chứng, khác thứ tự chèn ⇒ khác câu nói.

## PROPOSED — đã áp

| Lỗ | Sửa |
|---|---|
| F1 | Thêm `MasteryState.coverageIncomplete`. `stateAt()` chỉ được nói `mastered` khi **mọi** ca đã biết đều có bằng chứng |
| F2 | `fractionCase` trả ca thứ ba `denominator-equal`. Chưa có method nào đăng ký cho ca này ⇒ TutorScope **fail closed** — đúng hành vi mong muốn |
| F3 | Thêm `SupportLevel {none, hint, workedStep, fullSolution}` + `observeWithSupport`. `fullSolution` ⇒ belief **không đổi**, không vào `evidenceCount`; `hint`/`workedStep` ⇒ chỉ cho số hạng `learn`, không cho công trả lời đúng. Đếm riêng `supportedCount` |
| F4 | `contrastCaseFor` — ưu tiên ca được dạy **gần nhất trước** ca đang vướng (theo `introducedGrade`); dự phòng xếp theo số bằng chứng rồi id. Tất định |

Đột biến kiểm chứng — cả bốn **đỏ**, cả bốn xác nhận đã áp vào tệp bằng grep (§4.5):

| Phép | Kết quả |
|---|---|
| gỡ chốt độ phủ trong `stateAt` | 🔴 |
| gỡ ca `denominator-equal` | 🔴 |
| cho `fullSolution` hành xử như tự làm | 🔴 |
| quay lại `b.strong.first` | 🔴 |

## CONSEQUENCE — hai lỗ CHƯA vá, ghi ra để không bị quên

### ⚠️ F5 · không có mô hình quên

`bktUpdate` chỉ tăng: `posterior + (1 - posterior) * learn`. Không tham số `forget`,
`observe` không nhận thời điểm. Một học sinh vững tháng 9 vẫn "vững" tháng 6 dù không
chạm lại lần nào. PHASE 16 gọi tên `forgetting`.

Chưa vá vì cần mô hình thời gian trong toàn chuỗi bằng chứng — không phải sửa một hàm.

### ⚠️ F6 · một bài tập chỉ quy được về MỘT khái niệm

`decide({required String conceptId, ...})` nhận **một** concept. Nhưng `3/4 + 2/5` cần
`quy-dong` **và** `cong-phan-so` **và** có thể `rut-gon`. Benchmark OSS đã ghi nhận đúng
điều này: EduStudio dùng `cpt_seq` — một bài tập ánh xạ **nhiều** concept (Q-matrix).

Khi trẻ sai, engine quy lỗi cho một khái niệm mà **không có cách nào biểu diễn** "sai,
nhưng chưa biết vì khái niệm nào trong ba". Quy lỗi sai địa chỉ tệ hơn không quy lỗi.

Chưa vá vì đổi chữ ký `decide` là đổi kiến trúc, cần một ADR riêng và bằng chứng corpus
về bài tập đa kỹ năng.

### Ghi chú về giá trị

Bốn lỗ trên **không** lộ ra qua thêm tính năng. Chúng chỉ lộ khi viết test cố ý phá. Ba
trong bốn liên quan trực tiếp tới việc **nói với phụ huynh điều không đúng về đứa trẻ** —
loại lỗi mà độ chính xác dự đoán cao không cứu được.
