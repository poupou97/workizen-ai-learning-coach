# WAL-239 — CĂN NGUYÊN hư hại mã nguồn (2026-09-10)

Lệnh Founder: *«Find the FIRST stage where real code lines disappear while
line-number content survives.»*

Câu trả lời: **chúng không biến mất khỏi sản phẩm. Chúng biến mất khỏi PHÉP ĐO.**

---

## A · «HỌ B» KHÔNG PHẢI MẤT NỘI DUNG

Bản audit 2026-09-09 xếp 8/16 ca là «mất gần hết — chỉ còn số dòng»:

    BFS_Traversal (5 dòng) → «1 2 3 4 5»
    countNum (6 dòng)      → «3 4 2 6 1 5»
    Hanoi (7 dòng)         → «3 4 5 6 7 1 2»

Truy bốn ca xuyên suốt **bản in → Docling → dòng OCR → `blocks()` →
`page_paragraphs` → gắn bài → pack**, đối chiếu với `assets/pack` thật:

| ca | dòng mã in | tới pack | nằm ở |
|---|---|---|---|
| `BFS_Traversal` | 5 | **5/5** | 2 khối, **HEADER XẾP SAU THÂN** (39 so với 38) |
| `countNum` | 6 | **6/6** | 2 khối, thứ tự giữ |
| `Hanoi` | 5 | **5/5** | 2 khối, thứ tự giữ |
| `reverseorder` | 5 | **5/5** | 1 khối chính |

**21/21 dòng mã đều tới tay trẻ.** Không dòng nào mất.

### Vì sao phép đo báo là mất

`stem_exposure` đếm đoạn văn phủ **≥60% DIỆN TÍCH CỦA CHÍNH ĐOẠN** vào vùng mã.

| thứ nằm trong vùng | phủ | phép đo |
|---|---|---|
| khối CỘT SỐ DÒNG (hẹp, cao) | **100%** | ĐẾM |
| khối chứa dòng mã thật (đã hàn vào văn xuôi rộng cả trang) | **0,9%–39,7%** | BỎ SÓT |

Cột số dòng sống sót **trong phép đo**, không phải trong sản phẩm. Đây là lần
thứ tư trong hai ngày một kết luận sinh ra từ mẫu số/cửa sổ đo, không từ dữ liệu.

---

## B · CHẶNG PHÁ HUỶ ĐẦU TIÊN LÀ `blocks()`

`tool/corpus/lesson_reading.py::blocks` gom dòng theo **cột**: dòng mới phải
chồng x với GIAO của mọi dòng đã có trong khối. Với mã nguồn, **thụt lề tạo ra
bước nhảy x**, nên khối bị cắt ngay tại chỗ thụt vào — rồi mỗi mảnh hút lấy
văn xuôi nào tình cờ chồng x với nó.

Census toàn corpus, 334 vùng `code` **có dấu vết chương trình in**:

| | n | |
|---|---|---|
| bị xé thành nhiều khối | 201 | **60,2%** |
| hàn với chữ NGOÀI vùng | 294 | **88,0%** |
| tới **14 khối** cho một chương trình | 1 | |

Nhân chứng `BFS_Traversal` (Tin học 12 chuyên đề, tr.80): dòng
`def BFS_Traversal (V,Adj) :` bắt đầu ở x=0,1694, lọt vào dải x của **cột STT
của một bảng ở nửa trên trang** (0,1429–0,1755) nên bị hút vào khối ấy — và
khối ấy xếp **sau** khối chứa thân hàm.

Rồi `page_paragraphs` nối các dòng trong khối bằng **một dấu cách**
(`' '.join`) — đó là họ A, và nó chỉ là chặng thứ hai.

⇒ **HỌ A VÀ HỌ B CÙNG MỘT CĂN NGUYÊN.** Vùng mã chưa bao giờ được coi là MỘT
đơn vị; nó bị băm bởi luật gom cột dành cho văn xuôi rồi mới bị làm phẳng.

---

## C · BẢN VÁ — SỞ HỮU THEO DÒNG

`tool/corpus/code_source.py`. Lọc theo ĐOẠN không cứu được (đoạn nào cũng chỉ
phủ vài phần trăm), nên đơn vị là **DÒNG OCR**: dòng có tâm nằm trong vùng thì
thuộc vùng ấy, được bóc ra trước khi `blocks()` chạy, và dựng lại bằng đúng ba
thứ đo được từ trang in — `y` → ranh giới & thứ tự dòng · `x` → bậc thụt lề ·
chuỗi ký tự → nội dung giữ nguyên.

**Phạm vi hẹp có chủ ý:** chỉ **334/875** vùng nhãn `code` có dấu vết chương
trình in. 541 vùng còn lại phần lớn là lời giải Toán — giữ nguyên đường cũ.

### Hai lỗi do CHÍNH bản vá sinh ra, đã chặn

1. **TRANG HAI CỘT.** Docling khoanh khung `code` trải hết bề ngang trang
   (x 0,145–0,897 ở Tin học 12 tr.36), nên gom theo y hàn cột chú giải vào
   giữa câu lệnh: «`if k >= len (T):` Bước 2. Thực hiện thao tác». Với Python
   đó là **chương trình khác**. Nhận bằng **sự lặp lại** của khe dọc chứ không
   bằng một con số bề rộng; nhận ra thì KHÔNG dựng. → 7,8%.
   *Bản đầu của chốt này bắt nhầm **50,9%** vì chính cột số dòng cũng để lại
   khe lặp ở cùng một chỗ.*
2. **KHỐI MÃ BỊ VÙNG BẢNG NUỐT.** Trước kia dòng mã nằm lẫn trong đoạn văn
   rộng nên không luật sở hữu nào với tới; khớp gọn vào vùng rồi thì một vùng
   bảng chồng lên là nuốt trọn. Khối mã được miễn hai luật sở hữu ấy.

### Và một lỗi của POC hôm qua

`code_poc.reconstruct` bóc cột số dòng để đo thụt lề rồi **không trả lại** —
trái với chính chú thích của nó («vẫn giữ nguyên trong nội dung, không xoá chữ
của sách»). Đo được: **32 trang hụt đúng các chữ số ấy**. Nay số dòng in được
in lại, canh phải theo số rộng nhất, đúng như sách canh cột.

---

## D · CHẤT LƯỢNG

### Trước → sau, trên chính mẫu đóng băng n=16 của bản audit

| | TRƯỚC | SAU |
|---|---|---|
| có ranh giới dòng | **0/16** | **14/14** |
| nội dung verbatim đủ | — | **14/14** |
| chương trình bị xé nhiều khối | 11/16 | **0** |
| thụt lề đo được | — | 12/14 |
| thụt lề có bậc thật | — | 8/14 |
| chặn vì HAI CỘT (fail closed) | — | 2/16 |

### Census toàn corpus — 334 vùng

| | n | |
|---|---|---|
| dựng được khối mã | **286** | **85,6%** |
| chặn · hai cột | 26 | 7,8% |
| chặn · quá ít dòng | 16 | 4,8% |
| vùng rỗng | 6 | 1,8% |

Trong 286 khối dựng được:

| | n | |
|---|---|---|
| thụt lề **ĐO ĐƯỢC** | 227 | **79,4%** |
| thụt lề **KHÔNG đo được** (fail closed, không đoán) | 59 | 20,6% |
| có bậc thụt lề thật | 170 | 59,4% |

### Đối chứng âm — điều Founder đòi hỏi nhất

*«fixing code MUST NOT globally preserve arbitrary OCR newlines in normal
prose and damage Read UX.»*

| | |
|---|---|
| trang CÓ vùng mã | 181 |
| xuống dòng lọt vào VĂN XUÔI | **0** |
| lệch ký tự chữ (mất chữ của sách) | **0** |
| sai thứ tự đọc | **0** |
| trang KHÔNG có vùng mã (đối chứng) | 1.500 |
| khác đường cũ | **0** |

`WAL_CODE_OFF=1` đưa lượt dựng về đúng đường cũ mà không phải revert mã.

---

## E · CÒN NỢ

* **Trình bày**: khối mã ra `t:"text"`, client dựng bằng phông chữ thường nên
  bậc thụt lề canh không thẳng hàng. Ngữ nghĩa (dòng · nội dung · bậc) thì
  đúng và **sao chép được**. Muốn phông đều thì phải có khối kiểu riêng —
  Founder chưa cho phép, nên KHÔNG làm.
* **20,6%** khối không dựng được thụt lề, **7,8%** vùng bị chặn vì hai cột.
  Ảnh vùng nguồn vẫn là dự phòng ỨNG CỬ cho hai phần này, chưa thi công.
* **541** vùng nhãn `code` không có dấu vết chương trình in — chưa phân loại,
  giữ nguyên đường cũ. `UNKNOWN` là trạng thái hợp lệ.
