# ROUND 7 · VÒNG 2 — SAM DẠY: PHẢN HỒI PHỤ THUỘC LỖI

**Golden Lesson:** KHTN 6 · Bài 17 «Tách chất khỏi hỗn hợp» (Founder order 49 — đã duyệt).
**Nền:** nhánh vòng 1 `round7/v1-home-workspace-visual` (PR #115, CHƯA merge) — không phải `main`.
**Máy thật:** Nokia 6.1 (`192.168.1.3:5555`), `ai.workizen.learningcoach`, `adb install -r`
(không gỡ cài lần nào — app data của Founder còn nguyên).

**Trạng thái:** READY FOR FOUNDER REVIEW. **DO NOT MERGE** (order 48 thu hồi quyền merge).

---

## 0 · YÊU CẦU QUYẾT ĐỊNH, TRẢ LỜI BẰNG MỘT BẢNG

> **Phản hồi phải phụ thuộc lỗi.** Không dùng mặc định «Chưa đúng — nhưng gần rồi» cho mọi
> đáp án sai. Gần đúng ⇒ nói vì sao gần. Sai bản chất ⇒ giải thích misconception tương ứng.
> Chưa đủ bằng chứng ⇒ không suy diễn trạng thái hiểu bài.

Câu 1 của Bài 17 — «Quá trình làm muối từ nước biển sử dụng phương pháp tách chất nào?» —
có **bốn** lựa chọn, nên phải có **bốn** phản hồi khác nhau. Đây là toàn văn SAM nói, cạnh
nhau, để Founder liếc một cái là thấy không hai cái nào giống nhau:

| Trẻ chọn | SAM nói (nguyên văn trên máy) | «Bài này dùng ở đâu» |
|---|---|---|
| **A · Lọc** | «Con chọn «Lọc». Sách viết — **Dùng để tách: tách chất rắn không tan ra khỏi chất lỏng.**» | → **«Lọc nước từ hỗn hợp nước lẫn đất»** (chạm là nhảy tới sơ đồ ấy) |
| **B · Cô cạn** | *(đáp án khoá)* «Khớp với điều sách viết: làm nước biển bay hơi để thu muối là phương pháp cô cạn…» + **«Con trả lời khớp ở lần thử thứ n, sau k gợi ý.»** | — |
| **C · Chiết** | «Con chọn «Chiết». Sách viết — **Dùng để tách: tách các chất lỏng không tan vào nhau ra khỏi nhau.**» | → **«Tách dầu ăn khỏi nước»** |
| **D · Lắng** | «Con chọn «Lắng». Sách viết — **Dùng để tách: tách các chất rắn lơ lửng nặng hơn ra khỏi các chất nhẹ hơn.**» | **«Bài này chưa có sơ đồ riêng cho cách «Lắng» — sách chỉ nhắc tên nó ở phần tóm tắt. SAM không dựng thêm sơ đồ.»** |

Mỗi dòng in đậm là **NGUYÊN VĂN SGK** — ô «Dùng để tách» của chính cách trẻ chọn, trong bảng
so sánh trang 63 mà pipeline đã trích. Không có LLM trong đường này; không có câu nào SAM tự
nghĩ ra. Cột phải cũng khác nhau, và khi bài **không có** gì để chỉ thì SAM **nói thẳng** thay
vì gợi bừa.

Khung máy thật: `05-wrong-loc.png` · `07-wrong-chiet.png` · `08-wrong-lang.png` (lượt 1) và
`20/22/23-AFTER-*.png` (lượt 2).

### Câu 3 (MCQ ghép hai cách) — cùng luật, dữ liệu khác

| Trẻ chọn | SAM nói |
|---|---|
| **A** «Hoà tan vào nước → lọc bỏ cát → cô cạn lấy muối» | *(đáp án khoá)* |
| **B** «Chiết bằng phễu chiết» | «Con chọn «Chiết». Sách viết — Dùng để tách: tách các chất lỏng không tan vào nhau…» → «Tách dầu ăn khỏi nước» |
| **C** «Để lắng rồi gạn lấy muối» | «Con chọn «Lắng». Sách viết — Dùng để tách: tách các chất rắn lơ lửng nặng hơn…» → «bài này chưa có sơ đồ riêng» |

### Câu 2 (trẻ tự viết) — nhánh «CHƯA ĐỦ BẰNG CHỨNG» là THẬT

Trẻ gõ một câu SAM không đối chiếu được với chữ nào trong bài (`10-free-text-insufficient.png`):

> **SAM chưa đủ căn cứ để nói gì về câu này của con.**
>
> `SAM CHỈ BIẾT CHỪNG NÀY` — SAM chỉ đối chiếu được CHỮ con viết với lời sách trong bài. Câu
> của con không có chữ nào SAM đối chiếu được, nên SAM **KHÔNG BIẾT** con đã hiểu hay chưa —
> và SAM không đoán.
>
> ↺ **Thử lại** — Con thử viết lại bằng vài chữ có trong bài, hoặc xin SAM một gợi ý nhé.

Đây không phải một câu an ủi khác: nó là **một nhánh riêng** (`DiagnosisKind.insufficient`),
và nó nói ĐÚNG GIỚI HẠN của máy (so chữ, không chấm ý) thay vì đoán trạng thái hiểu bài.

Có chữ đối chiếu được thì SAM kể ra **đúng những chữ ấy** và vẫn nói rõ «chữ trùng nhau chưa
nói con hiểu hay chưa hiểu — SAM so CHỮ, không chấm Ý».

---

## 1 · LỜI ẤY ĐẾN TỪ ĐÂU (và vì sao nó không thể bịa)

`lib/features/lesson_workspace/teaching/answer_diagnosis.dart` — **hàm thuần** trên
`SemanticData` + `AskStep`. Nó **dùng lại** phép so khớp nguyên từ và `explainForEntity` của
vòng 1 (`views/visual_explain.dart`), không viết bản thứ hai.

```
trẻ chọn «Lọc»
  → entityHits("Lọc", semantic)            so khớp NGUYÊN TỪ, hai chiều
  → explainForEntity(bảng so sánh, i)      ô «Dùng để tách» NGUYÊN VĂN + mentionsOf("Lọc")
  → AnswerDiagnosis(misconception, …)      headline nhắc lại lựa chọn của TRẺ
```

Bốn luật, giữ bằng test:

1. **Không sinh chữ nội dung.** Mọi câu về nội dung là nguyên văn `SemanticData`. Thứ tệp này
   thêm vào là *quan hệ máy đọc được*: tên nào trẻ chọn, sách viết gì về tên ấy, bài dùng nó
   ở đâu.
2. **Không lộ đáp án ở nhánh «sai bản chất».** Tên phương án đúng chỉ xuất hiện ở `scaffold`
   của kịch bản, khi hết thang gợi ý (`09-scaffold-then-q2.png`). Lộ ngay lần sai đầu thì
   «thử lại» vô nghĩa — có test quét chữ «cô cạn» trong cả ba phản hồi.
3. **Không có căn cứ ⇒ nói ít đi.** Lựa chọn không có trong bảng nào của bài ⇒ nhánh
   `insufficient`, không bịa một dòng sách cho nó.
4. **Không danh tính bài.** Test quét CẢ THƯ MỤC `teaching/` tìm `KHTN|Bài\s*\d+|lessonNo…`
   và cấm `import lesson_document` — cùng kỷ luật vòng 1 đã đặt cho `views/`.

---

## 2 · VÒNG LẶP, ĐÚNG THỨ TỰ ORDER 49 §2

Order 49: `GIẢI THÍCH NGẮN → HỎI → TRẺ TRẢ LỜI → SAM PHẢN HỒI THEO CÂU TRẢ LỜI →
GIẢI THÍCH KHÁC NẾU CẦN → THỬ LẠI`.

Trước vòng này, `TutorRunner.submit` khi không khớp chỉ **nhả một gợi ý viết sẵn** — cùng một
gợi ý dù trẻ chọn gì. Nay:

```
submit(answer)  không khớp
   ├─ lượt learner        «Lọc»
   ├─ lượt DIAGNOSE       ⭐ phản hồi theo LỖI CỦA CHÍNH TRẺ (mới)
   ├─ lượt hint           cách giải thích KHÁC (thang ≤2 bậc, như cũ)
   └─ KHÔNG advance       câu hỏi còn nguyên ⇒ THỬ LẠI
hết thang ⇒ scaffold (chỉ chỗ trong sách) + đi tiếp — không kẹt, không chê
```

- `TurnKind.diagnose` là loại lượt mới; `TutorRunner` nhận một **hàm** `diagnose` chứ không
  biết `SemanticData` (core không phụ thuộc feature). **Không truyền hàm ⇒ hành vi y như
  trước vòng 2** — có test.
- Dải pha đổi theo: `Giải thích › Hỏi › Con trả lời › Phản hồi › Giải thích khác › Thử lại`.
  Vòng 3 dựng dải này khi phản hồi đến SAU gợi ý; nay thứ tự thật đã đảo nên dải phải nói
  đúng cái app làm, nếu không nó tự mâu thuẫn ngay trên màn.
- **Băng «↺ Đến lượt con thử lại — chọn lại một đáp án»** trên hàng lựa chọn, và đáp án đã
  chọn mang dấu **«đã thử»** (vẫn bấm được — đánh dấu, không khoá) — `21-AFTER-retry-visible.png`.

---

## 3 · `CORRECT ANSWER != MASTERY`, thành một câu

Khớp mẫu KHÔNG được đọc thành «đã thạo». Ngay dưới lượt khớp, màn in **chuyện đã xảy ra**, đo
từ transcript — không có biến đếm nào khác:

> **Con trả lời khớp ở lần thử thứ 2, sau 1 gợi ý.** *(`12b`, `24-AFTER-…`)*

và khi trẻ đã mở cách học khác trong phiên: «… — trước đó con đã **mở** Trực quan.» (TRACE ≠
EVIDENCE: «mở», không bao giờ «hiểu»).

Thẻ kết thay lời chúc bằng **từng câu một** (`13-end-card-story.png`, `24-AFTER-…`):

```
Con đã đi qua 3/3 câu hỏi của sách cùng SAM.
· Câu 1/3: Con đã thử 3 lần; SAM chưa khớp được câu trả lời nào nên đã chỉ chỗ trong sách.
· Câu 2/3: Con đã thử 3 lần; SAM chưa khớp được câu trả lời nào nên đã chỉ chỗ trong sách.
· Câu 3/3: Con trả lời khớp ở lần thử thứ 2, sau 1 gợi ý.
Đây là kịch bản thử nghiệm — SAM ghi nhận con đã THAM GIA, chưa phải bằng chứng con đã hiểu.
```

Không sao, không phần trăm, không điểm — test quét cả màn cấm `%`, `⭐`, «đã thạo», «thành
thạo», «con hiểu rồi», «điểm».

---

## 4 · MÁY THẬT — HAI LƯỢT, BA LỖI TÌM ĐƯỢC VÀ SỬA

Founder yêu cầu đi **cả đáp án ĐÚNG lẫn đáp án SAI**, và **nhiều hơn một** phương án sai.
Lượt 1 đi ba phương án nhiễu của câu 1, một câu tự viết không đối chiếu được, và một đáp án
đúng sau hai lần thử.

| # | Lỗi thấy trên máy | Khung | Sửa |
|---|---|---|---|
| **D1** ⭐ | Sau một đáp án sai, runner thêm HAI lượt (phản hồi rồi gợi ý) nhưng **neo cuộn lấy lượt SAM CUỐI** ⇒ màn mở ra ở «Gợi ý 1/2», còn câu nói về **đáp án của chính trẻ** nằm khuất phía trên, phải cuộn ngược lên mới đọc được. Vòng lặp order 49 §2 **bị đảo ngay trên màn**. | `05-wrong-loc.png` (phải cuộn lên mới thấy: `06`) | Neo vào lượt **PHẢN HỒI** nếu có; không có thì giữ hành vi cũ. Ghép đôi: `BEFORE-AFTER-phan-hoi-len-dau.png` |
| **D2** | Thẻ kết nói «SAM chưa khớp được **câu nào**» — nhập nhằng: câu hỏi hay câu trả lời? | `13-end-card-story.png` | «… chưa khớp được **câu trả lời** nào» |
| **D3** | Lời mời thử lại trong thẻ dài **ba dòng**, **giống hệt nhau ở mọi đáp án sai**, và lặp gần hết với băng «Đến lượt con thử lại» ngay dưới nó ⇒ trên máy nó trông đúng như câu an ủi mặc định Founder đã bác. | `05`/`07`/`08` | Rút còn **một dòng** nói VIỆC CẦN SO («Con so dòng sách ở trên với câu hỏi — có khớp không?»); băng lo việc cần LÀM |

Lượt 2 xác nhận cả ba (`20`–`24-AFTER-*.png`): màn mở ra ở phản hồi, thứ tự đúng, một dòng
thử lại, thẻ kết nói rõ.

### Lỗi tìm được TRONG test trước khi lên máy

Đo widget ở khổ Nokia (360×640 dp) trước lượt 1:

| Đo | Trước | Sau |
|---|---|---|
| Chữ nói về MÁY ở đầu màn «Học với SAM» | **232 dp** (dòng runtime 136 + chú giải nhãn 96) | **51 dp** (một dòng + ⓘ) |
| Nội dung dạy đầu tiên | 402 dp = **63 %** màn | 221 dp = **35 %** |
| Nút «Tiếp ▸» | 1055 dp = 1,6 màn | 874 dp |

Sự thật không mất: sheet «Nguồn & độ tin» **đã có sẵn** dòng runtime đầy đủ, nay có cả chú
giải nhãn. Con số PEDAGOGY REALITY («Máy đã kiểm 7/17 bước…») vẫn ở đầu màn. Đây là đúng phép
vòng 1 đã dùng cho «Vì sao SAM chọn sơ đồ này».

### Cạm bẫy máy thật, ghi lại để lần sau không mất 20 phút

**`adb install -r` báo `Success` KHÔNG chứng minh mã mới đã lên máy.** Ở lượt 2, ba lần cài
liên tiếp vẫn để máy chạy **bản cũ** — `dumpsys` báo `lastUpdateTime` mới và `codePath` mới,
nhưng `pm path` sau đó trỏ về một thư mục khác. Cách kiểm duy nhất đáng tin:

```
adb exec-out cat /data/app/<codePath>/base.apk > /tmp/dev.apk
unzip -p /tmp/dev.apk assets/flutter_assets/kernel_blob.bin | grep -a -c "<một chuỗi MỚI>"
```

Và: bản **debug** (211 MB) bị OS giết giữa chừng trên Nokia 3 GB khi Play Store đang churn —
`flutter build apk --profile` (132 MB, AOT, không R8) chạy ổn định. `--release` **không dựng
được** trên máy này: R8 báo thiếu lớp ML Kit (chinese/devanagari/japanese/korean recognizer).
Đó là nợ cấu hình android/, không thuộc vòng này — **BLOCKED**, đã ghi ở §7.

---

## 5 · GUARDRAIL — không cái nào bị nới

| Bất biến | Ở đâu trong vòng này |
|---|---|
| `OPENED != UNDERSTOOD` | Câu «chuyện đã xảy ra» nói «con đã **mở** Trực quan», không bao giờ «đã hiểu». |
| `TAP != COMPETENCE` | Chọn đúng một ô ⇒ SAM nói mấy lần thử / mấy gợi ý, không phong trạng thái. Thẻ kết đếm THAM GIA. |
| **`CORRECT ANSWER != MASTERY`** | §3. Không sao, không %, không «đã thạo» — test quét cả màn. |
| `MOCK != EVIDENCE` | Không thêm đường ghi nào. `TutorView` vẫn không có `LearnerStore`, không có kiểu để phát `LearningEvent`. |
| `LLM OUTPUT != TRUTH` | `answer_diagnosis.dart` không gọi gì. Mọi câu về nội dung là nguyên văn `SemanticData`; phần SAM thêm là quan hệ máy đọc được, kiểm lại bằng mắt được. |
| `FIXTURE != TRUSTED CORPUS` | Chip «Bản thử nghiệm» + nhãn «SAM (kịch bản thử nghiệm)» không đổi. Lượt phản hồi mang nhãn **kịch bản** (không tự phong «runtime có kiểm») vì runtime không lập kế hoạch cho nó. |
| `trusted = 0`, `eligible for teaching = 0` | **Không đổi.** Vòng này không chạm pipeline, không chạm cổng TC, không chạm pack. Pack dựng lại từ `origin/main` (782757f4), `contentHash 846ccc69fa88…` **giống hệt** vòng 1, `pack_provenance verify` ⇒ **12/12 DEFAULT**. |
| D4 | Fixture thật + pack vẫn gitignore. Khung máy thật ra `~/Desktop/wal-evidence/round7-v2-device-2026-09-06/`, **không commit**. |

---

## 6 · TEST

`1206 xanh · 0 đỏ · 8 skip` (skip = bài thật lớp 5 chưa sinh trên máy này).

| Tệp | Giữ điều gì |
|---|---|
| `test/features/lesson_workspace/answer_diagnosis_test.dart` (18) | ⭐⭐ **ba/bốn phương án sai ⇒ ba/bốn lời khác nhau** (so `fullText`), mỗi lời mang đúng dòng sách của cách ĐÓ và **không mượn** dòng của cách khác · không lộ đáp án · «gần rồi» và mọi chữ chấm điểm bị cấm · nhánh `insufficient` nói «KHÔNG BIẾT» · hư từ không tính là «đối chiếu được» · tất định · so khớp nguyên từ hai chiều · **quét cả thư mục `teaching/`** · chạy trên **fixture THẬT** khi máy có |
| `test/features/lesson_workspace/tutor_teaching_loop_test.dart` (10) | ⭐⭐ hai đáp án sai ⇒ hai **màn** khác nhau (khổ Nokia 360×640) · thứ tự PHẢN HỒI → GIẢI THÍCH KHÁC · câu hỏi **không đóng** sau phản hồi (băng thử lại + dấu «đã thử») · **neo cuộn rơi vào lượt phản hồi** (lỗi D1) · không hook ⇒ hành vi cũ · `CORRECT ANSWER != MASTERY` trên màn · câu tự viết không đối chiếu được ⇒ «SAM CHỈ BIẾT CHỪNG NÀY» · liên hệ mở đúng sơ đồ |

Test đổi theo là **CHỦ Ý**, mỗi chỗ có chú thích: dải pha (order 49 §2), chú giải nhãn không
còn ở đầu màn «Học với SAM», thẻ kết dài thêm nên nút bước tiếp phải cuộn tới.

---

## 7 · PLANNED vs ACTUAL

| # | PLANNED | ACTUAL | Trạng thái |
|---|---|---|---|
| 1 | Phản hồi phụ thuộc lỗi — không một câu mặc định cho mọi đáp án sai | Bốn lựa chọn câu 1 ⇒ bốn lời khác nhau, mỗi lời là nguyên văn sách về đúng cách trẻ chọn (§0) | **DONE** |
| 2 | Nhánh «sai bản chất» = misconception tương ứng | Đối chiếu ô «Dùng để tách» của cách trẻ chọn + bài dùng nó ở đâu; không lộ đáp án | **DONE** |
| 3 | Nhánh «gần đúng» = nói vì sao gần | Có, và là nhánh chạy được: MCQ trùng một phần với đáp án ghép nhiều cách; câu tự viết có chữ đối chiếu được. **Bài 17 câu 1/3 không có phương án nào rơi vào nhánh này** — dữ liệu quyết định, không ép | **DONE** (không có bằng chứng máy thật cho nhánh này ở Bài 17) |
| 4 | Nhánh «chưa đủ bằng chứng» — không suy diễn | Nhánh riêng + câu «SAM KHÔNG BIẾT con đã hiểu hay chưa». Đi được trên máy (`10`) | **DONE** |
| 5 | Vòng lặp có THỬ LẠI, không thành màn quiz | Phản hồi trước, giải thích khác sau, câu hỏi không đóng; băng thử lại + dấu «đã thử»; dải pha nói đúng vòng lặp | **DONE** |
| 6 | `CORRECT ANSWER != MASTERY` | Câu «chuyện đã xảy ra» + thẻ kết từng câu; test quét cấm mastery/điểm | **DONE** |
| 7 | Máy thật: đi ĐÁP ÁN ĐÚNG và ĐÁP ÁN SAI, **nhiều hơn một** phương án sai | 2 lượt · 3 phương án nhiễu câu 1 + 2 phương án nhiễu câu 3 + 1 câu tự viết không căn cứ + 1 đáp án đúng sau 2 lần thử | **DONE** |
| 8 | Sửa feedback/pedagogy từ cái thấy trên máy | D1 (neo cuộn — lỗi thật, đảo vòng lặp) · D2 (chữ nhập nhằng) · D3 (lời thử lại lặp và giống nhau) | **DONE** |
| 9 | Dùng lại `visual_explain` thay vì viết lookup thứ hai | `answer_diagnosis.dart` gọi `explainForEntity` / `mentionsOf` / `containsWord` | **DONE** |
| 10 | Guardrail không nới | Bảng §5 | **DONE** |
| 11 | Bản release cho máy thật | `--release` **không dựng được**: R8 thiếu lớp ML Kit. Đi bằng `--profile`. Nợ cấu hình `android/`, không thuộc phạm vi vòng 2 | **BLOCKED** |
| 12 | Phần ghim 281 dp của workspace | Vòng 2 rút phần chữ về MÁY trong Tutor (232 → 51 dp) nhưng **không** đụng phần ghim của workspace — vẫn là câu hỏi Founder từ vòng 1 | **PARTIAL** |
| 13 | Vòng 3 — Golden Journey đầy đủ + Luyện tập | Ngoài phạm vi vòng 2 theo order 49 | **NOT STARTED** |

### Chưa xong, nói thẳng

- **Nhánh «gần đúng» chưa có bằng chứng máy thật.** Nó có test (dữ liệu có kiểu + câu tự
  viết), nhưng Bài 17 câu 1 không có phương án nhiễu nào chia sẻ một cách tách với đáp án
  khoá, nên trên máy nó không xuất hiện. Ép cho nó xuất hiện = bịa dữ liệu. **PARTIAL.**
- **Lượt phản hồi mang nhãn «kịch bản thử nghiệm» dù nội dung là nguyên văn sách**
  (`trustedStructuredLesson`). Đây là lựa chọn AN TOÀN có chủ ý: `RuntimePlan` không lập kế
  hoạch cho lượt này nên SAM không tự phong nhãn xanh. Nếu Founder muốn nhãn phản ánh nguồn
  dữ liệu chứ không phải nguồn kế hoạch, đó là một quyết định đáng đưa ra chứ không nên tự
  quyết.
- **Liên hệ «Bài này dùng ở đâu» trong lời phản hồi mở Trực quan và cuộn tới đúng thẻ**
  (`VisualView.scrollToSemanticId` mới) — có test widget, **chưa** chạm thử trên máy ở lượt 2.
- **`CORRECT ANSWER != MASTERY` chỉ nói được cái Tutor tự thấy** (mấy lần thử, mấy gợi ý) và
  cái `WorkspaceTrace` cho biết (đã MỞ view nào). Câu Founder nêu — «con đã làm đúng câu này
  **sau khi xem sơ đồ**» — cần trace của Luyện tập, thuộc **vòng 3**.

---

## 8 · CẦN FOUNDER QUYẾT

1. **Nhãn của lượt phản hồi**: giữ «kịch bản thử nghiệm» (an toàn, hiện tại) hay đổi sang một
   nhãn thứ ba nói «lời sách, SAM chỉ đối chiếu»?
2. **Bản dựng cho máy thật**: sửa R8 (thêm keep-rule ML Kit vào `android/app`) để có bản
   release, hay tiếp tục đi bằng `--profile` ở các vòng sau?
3. Ba câu vòng 1 còn treo (phần ghim 281 dp · màn «Vào bài học» · tiêu đề IN HOA) — vòng 2
   không đụng tới.
