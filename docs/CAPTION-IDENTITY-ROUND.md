# DANH TÍNH CHÚ THÍCH — bằng chứng thay cho proxy (2026-09-10)

Phạm vi Founder chốt: chỉ hai họ hỏng **#1 nguồn có mà không giao** và
**#3 giao rồi mà mất danh tính**, khi nguyên nhân thật là danh tính chú thích.
Không đụng #2 (bảng vỡ), #4 (neo vị trí), #5 (phụ thuộc dây chuyền).

Mục tiêu **không phải** «lấy được nhiều chú thích hơn», mà là:

    VẬT THỂ NGUỒN  ↔  CHÚ THÍCH IN  ↔  HÌNH TỚI TAY TRẺ

đủ bằng chứng để nói ba thứ ấy là **cùng một vật**.

---

## 1 · CĂN NGUYÊN

Lịch sử 5 Bài 4 tr.24 — dòng chú thích **sạch và đứng đầu dòng**:

    x=0,327  y=0,907  «Hình 2. Bản đồ phân bố dân cư Việt Nam năm 2024»

Bị loại vì `blocks()` gom nó với **hai nhãn toạ độ bản đồ** («100», «108°»)
thành khối **3 dòng**, mà luật nhận chú thích **một cấp** chỉ áp dụng khi khối
**≤ 2 dòng**.

⇒ tấm bản đồ **67,4% trang** không tới tay trẻ ⇒ bài tập in *«Dựa vào bản đồ
phân bố dân cư Việt Nam năm 2024, hãy kể tên 3 tỉnh…»* **không làm được**.

**Kích thước khối là thứ `blocks()` tình cờ dựng ra, không phải thứ sách in.**

## 2 · QUY MÔ

**14.768** chú thích đánh số in trên toàn corpus:

| | n | |
|---|---|---|
| nhận qua mẫu hai cấp «Hình 14.2» | 10.059 | 68,1% |
| nhận qua mẫu một cấp, khối ngắn | 2.809 | 19,0% |
| **bị loại CHỈ vì khối > 2 dòng** | **1.900** | **12,9%** |

Lệch rất mạnh theo môn — cổng đang canh theo môn dùng đánh số hai cấp:

| Khoa học 4/5 | GDTC | Lịch sử | Tin học · Địa lí | KHTN · Toán · Hoá |
|---|---|---|---|---|
| **42,6%** | **33,8%** | **31,1%** | ~10% | **~1%** |

## 3 · ĐO TRƯỚC KHI RA LUẬT

Mẫu **đóng băng 80 ca**, seed `20260911`, 3/4 lấy từ nhóm đang bị loại. **Dán
nhãn tay từng ca, chỉ nhìn chữ và ngữ cảnh chữ** — không nhìn bố cục, để khỏi
đo lại chính thứ đã dùng để dán nhãn. Nhãn: **66 thật · 14 không phải**.

Bốn họ dương tính giả tìm được:

* **CÂU** — «Hình 1 gắn liền với hoạt động của…», «Hình 8 và cho biết bạn An…»
* **DANH SÁCH** — «Hình 4: Sơ đồ…; Hình 5: Sơ đồ…; Hình 6: Sơ đồ…»
* **CÂU DẪN CHIẾU** — «Hình 9a.1 và Hình 9a.2 còn cung cấp cho HS…»
* **PHÉP NHÂN** — «bảng 10 x 10, cột 10 x 1 và các khối lập phương đơn vị»

## 4 · LUẬT

Nhận **bất kể khối dài bao nhiêu** khi đủ ba điều kiện của **chính dòng ấy**:

| | điều kiện | chặn cái gì |
|---|---|---|
| ① | **dấu ngăn** `.` hoặc `:` ngay sau số hiệu | CÂU (không có dấu ngăn) |
| ② | **có tên** sau dấu ngăn | «Hình 9a.9.» kết một câu |
| ③ | **đúng một danh tính** trong dòng | DANH SÁCH · CÂU DẪN CHIẾU |

Điều kiện ③ áp cho **cả nhánh hai cấp**: một dòng mang hai danh tính thì
**không gán an toàn cho MỘT hình được** — loại là fail-closed đúng. Sửa một họ
dương tính giả **đã có sẵn** (57/10.059 = 0,57%).

**Đánh số TRƠ** («Hình 11») giữ nguyên luật khối ≤2 — không có tên thì không
có bằng chứng, **không nới**.

### Chấm trên mẫu đóng băng

| | precision | recall |
|---|---|---|
| luật cũ | 95,0% | 28,8% |
| **luật này** | **100,0%** | **93,9%** |

Cả hai đều tăng. 4 ca còn bỏ sót đều là đánh số trơ trong khối 3–4 dòng — cố ý.

**Không nhạy với ngưỡng độ dài tên** (1→8 ký tự cho cùng kết quả): nó không
phải một núm vặn.

### Kiểm-đột-biến

| đột biến | |
|---|---|
| bỏ ① dấu ngăn | ⛔ đỏ |
| bỏ ② có tên | ⛔ đỏ |
| bỏ ③ một danh tính | ⛔ đỏ |
| **nới thẳng ngưỡng ≤2 → ≤8** (cách làm SAI) | ⛔ đỏ |
| khôi phục | ✅ xanh |

## 5 · TÁC ĐỘNG

**+1.455** mốc chú thích: GDTC +623 · Lịch sử +449 · Tin học +214 · Địa lí +45
· Khoa học +35 · **KHTN +8**.

Cổng tin cậy chạy lại trên 16.800 trang:

| | trước | sau |
|---|---|---|
| `REGION_TRUSTED` | 8.537 | **9.018** |
| `IDENTITY_RESOLVED` / vào dòng đọc | 7.733 | **8.189** |
| `TABLE_TRUSTED` | 654 | **699** |

Theo môn: Lịch sử **+172 (+32,6%)** · Tin học +140 · GDTC +108 · **KHTN +0** ·
Công nghệ **−1** (do điều kiện ③, đúng ý đồ).

## 6 · CA BẮT BUỘC — Lịch sử 5 Bài 4

| chặng | trước | sau |
|---|---|---|
| `SOURCE_PRESENT` | ✅ `picture` 67,4% trang | ✅ |
| vùng đáng tin ở bài 4 | **0** | **1** (tr.24) |
| danh tính | — | **«Hình 2. Bản đồ phân bố dân cư Việt Nam năm 2024»** |
| ảnh trong pack | 1 | **2** |
| ảnh có chú thích (cả lớp 5) | 314 | **360** |

Tác dụng phụ đúng hướng: một bảng ở Bài 22 nay đáng tin nên hiện bằng **ảnh**
thay vì các ô chữ vỡ («Bắc Băng Dương», «Thái Bình Dương 165,3»). Đó là bài
DUY NHẤT trong lớp 5 mất khối chữ, và mất đúng thứ đáng mất.

## 7 · CÒN LẠI, KHÔNG GIẤU

* **~45 khối chữ rác của nhãn bản đồ vẫn còn** trong dòng đọc — trẻ nay thấy
  **cả bản đồ lẫn rác**. Vẫn tốt hơn trước, nhưng cần một luật **chặn chữ do
  vùng hình sở hữu** (giống `owned_by_table` đã có). **Ngoài phạm vi vòng này.**
* **Phễu dò mực của đường D vẫn không dựng được bản đồ** — tài liệu của chính
  nó ghi họ bản đồ có 26% «không thấy». Tấm bản đồ tới được là nhờ **đường
  Docling**, không phải đường D.
* 4 ca chú thích **đánh số trơ** trong khối 3–4 dòng vẫn bỏ sót.
* Họ hỏng **#2 · #4 · #5** còn nguyên, đúng như phạm vi đã chốt.
