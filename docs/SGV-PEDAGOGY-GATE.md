# SGV CÓ NUÔI ĐƯỢC SAM KHÔNG — cổng 11 · 12 · 13 · 14

2026-09-11. Hạt giống mẫu đóng băng: `20260911` (rút lần đầu) và `20260912`
(rút LẠI sau khi sửa luật, để không tự chấm bài mình).

---

## GATE 1 · SGK ↔ SGV — **PASS**

### Đơn vị và luật

| | đơn vị |
|---|---|
| SGK LESSON | một bản ghi `lessonReadings` của pack đang phục vụ |
| SGV LESSON SECTION | dải trang SGV từ tiêu đề bài tới tiêu đề bài kế tiếp |

Mỗi cấp đòi **dữ kiện nguồn ĐỘC LẬP cùng nói một điều** — không cấp nào được
quyết bằng một mình:

- **B1** SGV **tự khai** «SGK ‹môn› ‹lớp›» in trong thân sách (49/60 cuốn mẫu)
- **B2** tiêu đề bài SGV **trùng** tiêu đề bài SGK ở mức đo được (≥25% số mục)
- **L1** tiêu đề «Bài N» ở **đầu trang THÂN** — trang mục lục bị loại
- **L2** chữ cạnh tiêu đề **trùng** tiêu đề bài N của SGK (Jaccard ≥ 0,34)
- **L3** ngay sau tiêu đề có mục **MỞ THÂN BÀI** (MỤC TIÊU / YÊU CẦU CẦN ĐẠT /
  MỤC ĐÍCH), dò trên chữ **đã bỏ dấu** vì OCR rụng dấu («MỤC ĐICH»)

⛔ Riêng lẻ **KHÔNG** đủ: cùng số bài · tên gần giống · quy ước tên tệp · gần
nhau về vị trí.

### Census — mẫu số chính xác

| | CONFIDENT | AMBIGUOUS | UNKNOWN | mẫu số |
|---|---|---|---|---|
| cặp SÁCH | **78** | 46 | 96 | **220** |
| cặp BÀI | **589** | 151 | 155 | **895** |

Leaf record ở `poc-out/pedagogy/sgk-sgv-pairs.csv` — mỗi dòng mang cuốn SGV,
số trang, chữ tiêu đề, cuốn SGK, số bài, ba cờ L1/L2/L3 và độ trùng, đủ để
kiểm lại tại nguồn.

### L3 sinh ra từ một ca GHÉP SAI đo được

`09-sgv-toan-9` tr93 in «Bài 11. Tỉ số lượng giác của góc nhọn **4 tiết** ·
Bài 12… 3 tiết · Luyện tập chung 2 tiết» — một **bảng phân bổ tiết** trong
phần giới thiệu sách. Số bài ĐÚNG, tiêu đề TRÙNG KHÍT, và chỉ 3 lần «Bài N»
nên lọt dưới ngưỡng mục lục. Chốt L3 giết nó bằng cấu trúc nguồn: bảng phân
bổ không mở thân bài. Nay là `AMBIGUOUS`.

### Kiểm độc lập — không dùng lại tiêu đề

Dán nhãn bằng tiêu đề là **vòng tròn**: nó xác nhận lại đúng dữ kiện luật đã
dùng. Nên xếp hạng chữ trang SGV so với **mọi** bài của cuốn SGK:

| thứ hạng của bài được ghép | số | |
|---|---|---|
| hạng 1 | 409 | 67,7% |
| hạng 2–3 | 100 | 16,6% |
| hạng 4–5 | 28 | 4,6% |
| hạng > 5 | 67 | 11,1% |

⚠ Bản đầu dùng **một** bài mồi nhử «xa nhất theo số hiệu» — **lệch hệ thống**:
với bài số lớn, mồi luôn rơi vào Bài 1, mà Bài 1 của Tin học là bài mở đầu đầy
từ vựng chung. Hai ca «trượt» hoá ra ghép **ĐÚNG**. Xếp hạng toàn bộ thì không
còn chỗ cho một mồi may mắn.

Hạng > 5 **không phải** ghép sai: soi 12 ca thì 11 đúng — trang bài THỰC HÀNH
và trang nặng ngôn ngữ năng lực chung thì từ vựng không giống thân bài SGK.

### Tỉ lệ GHÉP SAI

| mẫu | n | TRUE | FALSE | tỉ lệ sai |
|---|---|---|---|---|
| đóng băng 20260911 (trước khi có L3) | 40 | 40 | 0 | 0% |
| dải nghi ngờ hạng > 5 | 12 | 11 | **1** | 8,3% |
| **đóng băng 20260912 — rút LẠI sau khi sửa luật** | **30** | **30** | **0** | **0%** |

Mẫu cuối phủ **11 lớp · 21 cuốn SGK**, và **chưa ca nào từng được soi**, nên
không nhiễm bởi lần sửa luật. Với n=30 chỉ kết luận được **«dưới ~10%»**,
không phải «bằng 0».

---

## GATE 2 · BẰNG CHỨNG SƯ PHẠM — **PARTIAL**

Chỉ đọc trong **dải trang của cặp CONFIDENT**. Ngoài dải ⇒ không lấy.

| loại | SOURCE_EXPLICIT | SOURCE_DEMONSTRATED | UNKNOWN | có ≥1 |
|---|---|---|---|---|
| OBJECTIVE | 589 | 0 | 0 | 100,0% ⚠ |
| ACTIVITY | 588 | 1 | 0 | 100,0% ⚠ |
| HINT | 586 | 0 | 3 | 99,5% ⚠ |
| ASSESSMENT | 445 | 10 | 134 | 77,2% |
| ANSWER | 237 | 98 | 254 | **56,9%** |
| MISCONCEPTION | 60 | 1 | 528 | **10,4%** |

⚠ **BA SỐ ĐẦU KHÔNG ĐƯỢC ĐỌC NHƯ THÀNH TÍCH.**
- `OBJECTIVE` 100% là **VÒNG TRÒN**: chốt L3 đã đòi có «MỤC TIÊU» mới công
  nhận ghép, nên mọi bài CONFIDENT tất yếu có mục tiêu. Đây là hệ quả của luật
  ghép, không phải một phép đo độc lập.
- `ACTIVITY` và `HINT` ~100% là **từ vựng chung** của mọi trang SGV («hoạt
  động», «lưu ý», «gợi ý»). Xuất hiện, không phải dùng được.

Hai loại thật sự phân biệt được là **ANSWER** và **MISCONCEPTION**.

### Sở hữu mức VIỆC — «đáp án thuộc bài» ≠ «đáp án thuộc việc trẻ đang làm»

Khớp **số** không dùng được: bài SGK đánh số «N.» ở **97,0%** nhưng dùng
«Câu N» chỉ **3,1%**, mà «N.» còn là số **MỤC** chứ không riêng câu hỏi. Phép
đo đầu của tôi khớp số và ra **1,7%** — **sai phía SGK**.

Luật đúng xét **CHỮ của chính câu hỏi**: SGV in nguyên văn câu hỏi (trong khối
«1. Câu hỏi»), và câu ấy phải trùng ≥50% từ với thân bài SGK.

> **ANSWER gắn được ĐÚNG VIỆC: 81/589 = 13,8%.**

Soi 8/8 ca tại nguồn: SGV in **nguyên văn** đúng câu hỏi của SGK
(«Chất nào sau đây được gọi là vôi sống?», «Quá trình thụ tinh diễn ra như thế
nào?»). Sở hữu thật, không phải trùng hợp.

---

## GATE 3 · TRỤC TIN CẬY — **đã phân xử, hai chiều**

`13.634/13.634 = SOURCE_EXPLICIT` của bản cũ **không phải** phân loại tin cậy —
đó là một khẳng định do chính bộ trích gán. Nay tách hai trục:

| trục | mức | nghĩa |
|---|---|---|
| **A · SỰ THẬT NGUỒN** | `SOURCE_EXPLICIT` | có nhãn mục in ra |
| | `SOURCE_DEMONSTRATED` | sách thể hiện mà không gắn nhãn |
| | `UNKNOWN` | không đủ căn cứ |
| **B · SỰ THẬT SỞ HỮU** | `LESSON_OWNED` | trong dải trang bài đã ghép CONFIDENT |
| | `TASK_LINKED` | còn dẫn được tới đúng câu hỏi SGK in ra |

`SOURCE_EXPLICIT` **không** tự động là `SAFE_FOR_TUTOR`.

---

## MA TRẬN QUYỀN CỦA SAM

| bằng chứng | mẫu số | SAM ĐƯỢC PHÉP | SAM **KHÔNG** được |
|---|---|---|---|
| OBJECTIVE (vòng tròn) | 589/589 | nói bài này nhắm tới gì, theo chữ sách | coi là đã đo độc lập |
| ACTIVITY `audience=TEACHER` | 588/589 | đi theo trình tự hoạt động của nguồn | đọc nguyên lời SGV cho trẻ — SGV viết cho người lớn đứng lớp |
| HINT `audience=TEACHER` | 586/589 | dựa vào để chọn bước kế tiếp | biến thành lời gợi ý nói với trẻ |
| ASSESSMENT | 455/589 | nói việc này ở mức Biết/Hiểu/Vận dụng | suy ra trẻ đã thành thạo |
| ANSWER + `TASK_LINKED` | **81/589** | đối chiếu câu trả lời của trẻ với đáp án sách, ĐÚNG việc ấy | dùng cho 508 bài còn lại |
| MISCONCEPTION | 61/589 | chẩn đoán đúng lỗi sách đã nêu tên | chẩn đoán ở 528 bài còn lại |

**SAM vẫn phải BỊA nếu làm:** diễn đạt gợi ý theo lời trẻ hiểu · dựng thang
scaffold cho một đứa trẻ cụ thể · chấm đúng/sai ở 508 bài không gắn được việc ·
gọi tên lỗi ở 528 bài không có nhầm-lẫn in ra · mọi câu phản hồi.

---

## GATE 14 · **CAN SGV SAFELY POWER SAM? → PARTIAL**

**CÓ THỂ mở rộng ngay — 79 bài** (`T1`): đáp án gắn **đúng việc** + hướng dẫn
hoạt động + hình **có danh tính** đã tới tay trẻ.

| | |
|---|---|
| lớp | 6 (9) · 7 (7) · 8 (5) · 9 (18) · 10 (6) · 11 (17) · 12 (17) |
| môn | KHTN 30 · Hoá 16 · Công nghệ 11 · Sinh 10 · Lịch sử 6 · Tin 3 · LS&ĐL 1 · Địa 1 · chuyên đề CN 1 |
| có thêm nhầm-lẫn in ra | 4 |

**CHƯA thể mở rộng:**
- **Lớp 1–5: 0 bài `T1`.** SGV tiểu học phần lớn trượt ngay cổng SÁCH (lớp 1:
  0/10 CONFIDENT; lớp 2: 1/10; lớp 5: 1/15) — nhiều cuốn không in «Bài N» làm
  tiêu đề. Không được nói SAM phủ K-12.
- **508/589 bài** có đáp án nhưng **không gắn được việc** ⇒ SAM không được chấm.
- **131 cuốn SGV** (46 AMBIGUOUS + 96 UNKNOWN sau khi trừ) chưa ghép được sách.

## Phân tầng năng lực theo bằng chứng

| tầng | số | |
|---|---|---|
| **T1** đáp án gắn đúng việc + hoạt động + hình có danh tính | **79** | 13,4% |
| T2 đáp án gắn đúng việc + hoạt động | 2 | 0,3% |
| T3 có đáp án nhưng chưa gắn được việc + hoạt động | 254 | 43,1% |
| T4 chỉ mục tiêu + hoạt động | 254 | 43,1% |

Đây là **hướng kiến trúc**, chưa thi công: bài ít bằng chứng thì SAM **giảm
năng lực**, không bịa bù.

---

## TODO 16 · SAM SCALE POC 1 → 10 — **PASS** (2026-09-11)

**10/10 bài** qua cùng một bộ dựng và cùng một runtime · **0 logic riêng từng bài**.

### Cổng máy thật — 2 máy · 3 nhóm môn

| máy | bài | môn | kết quả |
|---|---|---|---|
| Nokia 6.1 (cáp) | Hoá học 11 · Bài 13 | Hoá học | ĐẠT |
| S24 (WiFi) | Sinh học 11 · Bài 2 | Sinh học | ĐẠT |
| S24 (WiFi) | Lịch sử 10 · Bài 9 | Lịch sử | ĐẠT |

Mỗi bài: đúng hồ sơ/lớp · đúng sách/bài · **việc là chữ nguyên văn SGK** · thẻ
«SÁCH VIẾT» trích nguyên văn kèm xuất xứ («trang PDF 16 · chạm để tra cứu») ·
ba tab mở được · **không có bước hỏi** ⇒ không có chỗ phán đúng/sai · nút
«Tiếp ›».

APK **kéo từ cả hai máy về**: 10/10 bài đủ vòng dạy + cờ
`samReady=true · answerCheckReady=false · misconceptionReady=false`.
Không tin «install Success».

### BACK / RESUME — **PASS**

Lịch sử 10 Bài 9 → tab SAM → BACK → Thành tích → Giá sách → Trang chủ → mở
lại → tab SAM. Sau resume: **cùng sách · cùng bài · cùng việc · cùng nguồn ·
cùng cờ năng lực**. Không lệch danh tính, không leo thang năng lực. Thẻ ở màn
chính đổi đúng «CHƯA BẮT ĐẦU» → «TIẾP TỤC · Đã mở: Đọc · Học với SAM».

### Ghi nhận nợ CHỮ SẢN PHẨM — *chưa sửa*

| dòng chữ | phán định | căn cứ |
|---|---|---|
| «Máy chưa ràng buộc được bài này với sách» | **TRUTHFUL** | `lib/core/curriculum/` chỉ có **một** binding (`khtn6_bai17.dart`); không bài POC nào có `SemanticBinding`, nên runtime không chứng minh được `TutorScope` và từ chối nhãn `runtimeGuided`. Cảnh báo ĐÚNG, **phải giữ**. |
| «SAM đi theo kịch bản viết sẵn — chưa phải SAM thật» | **TRUTHFUL, thiếu chính xác** | Các bước **là** viết sẵn theo nghĩa không suy luận lúc chạy — nhưng chúng được **SUY TẤT ĐỊNH TỪ NGUỒN**, không phải người gõ tay. Chữ hiện tại không phân biệt hai điều đó. Sửa ở vòng sau, **không xoá cảnh báo để UI đẹp**. |

### Kết luận

`SAM_READY = 10/10` · `ANSWER_CHECK_READY = 0/10` · `MISCONCEPTION_READY = 0/10`.

**Đã chứng minh scale SAM_READY 1 → 10 bằng một runtime ăn bằng chứng dùng
chung.** KHÔNG phải «10 bài có full AI Tutor».
