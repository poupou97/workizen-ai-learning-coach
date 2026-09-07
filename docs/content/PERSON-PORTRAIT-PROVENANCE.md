# LAI LỊCH CHÂN DUNG NHÂN VẬT

Lệnh 59 §P2. Mỗi bức chân dung ship trong sản phẩm phải có một mục ở đây.
Không có mục ⇒ không có dòng trong `PersonPortraits.verified` ⇒ thẻ trích dẫn
chạy nhánh KHÔNG ẢNH.

Ba bất biến Founder đặt ra, và mỗi cái bị kiểm bằng một mắt xích riêng:

| Bất biến | Mắt xích kiểm | Hỏng thì sao |
|---|---|---|
| `FOUND ON INTERNET != FREE TO SHIP` | Giấy phép truy được về bản gốc | `usage != approvedForProduct` |
| `SEARCH RESULT != ORIGINAL SOURCE` | `sourcePageUrl` trỏ về nơi số hoá bản gốc, không phải trang tổng hợp | không ship |
| `SEARCH RESULT != VERIFIED IDENTITY` | `identityCheckedAgainst` ghi bằng chứng CỤ THỂ | `eligibleForDisplay == false` |

---

## Thạch Lam — `p:thạch-lam`

| Trường | Giá trị |
|---|---|
| personId | `p:thạch-lam` |
| personName | Thạch Lam (Nguyễn Tường Vinh, sau đổi Nguyễn Tường Lân), 1910–1942 |
| assetPath | `assets/people/thach-lam.png` (288×352, thang xám) |
| portraitType | `historicalPhoto` → nhãn trẻ đọc: «Ảnh tư liệu» |
| usageStatus | `approvedForProduct` |
| sourcePageUrl | https://gallica.bnf.fr/ark:/12148/bpt6k42462606/f145 |
| sourceName | Nhà Văn Hiện Đại, Quyển ba — Vũ Ngọc Phan · Gallica/BnF |
| imageUrl | https://upload.wikimedia.org/wikipedia/commons/e/e0/Portrait_of_writer_Th%E1%BA%A1ch_Lam.jpg |
| author | Không rõ người chụp · sách của Vũ Ngọc Phan |
| licence | Phạm vi công cộng — PD-Vietnam (+ PD-1996 cho Hoa Kỳ) |
| licenceUrl | https://commons.wikimedia.org/wiki/Template:PD-Vietnam |
| retrievedAt | 2026-09-07 |

### Nguồn gốc — đi tiếp một bước nữa

Ứng viên tìm thấy trên Wikimedia Commons. **Commons chưa phải nguồn gốc.**
Trang tệp Commons tự khai tệp đến từ Gallica, mã `bpt6k42462606/f145` — bản số
hoá sách «Nhà Văn Hiện Đại» của Vũ Ngọc Phan. Đã tải trang ấy trực tiếp từ
Gallica và đối chiếu với tệp Commons: cùng một trang sách.

Một chi tiết đáng ghi: tệp Commons **không phải ảnh chân dung đã cắt** như tên
gọi gợi ý — nó là ảnh chụp NGUYÊN TRANG sách. Phần cắt là do repo này làm.

### Danh tính — bằng chứng là bản in, không phải siêu dữ liệu

`globalusage` của tệp trên Commons = **0**. Không wiki nào dùng nó, nên không
có đối chiếu chéo liên wiki. Bài Wikipedia tiếng Việt về Thạch Lam dùng một tệp
KHÁC (`Nhà_văn_Thạch_Lam.jpeg`, tải tại chỗ, không có trên Commons) — nên nó
cũng không xác nhận được tệp này.

Bằng chứng danh tính thật sự nằm trong chính bản in: dưới bản khắc, nhà xuất
bản in dòng chữ **«Thạch-Lam»**. Đó là chú thích của người xuất bản năm 1942,
không phải nhãn do người tải ảnh lên đặt năm 2020. Đã đọc trực tiếp trên ảnh
Gallica f145; f146 (mặt sau) cho thấy vệt in ngược của cùng bản khắc và cùng
dòng chữ, xác nhận đây là một trang in thật chứ không phải ảnh ghép.

### Giấy phép

PD-Vietnam: *tác phẩm nhiếp ảnh công bố lần đầu quá 75 năm*. Công bố 1942–1945
⇒ 81 năm tính đến 2026, vượt ngưỡng. Kèm PD-1996 cho Hoa Kỳ (công bố lần đầu
ngoài Hoa Kỳ). Phạm vi công cộng ⇒ **được phát hành**, nên tệp này commit được
và ship được — khác hẳn crop SGK vốn dừng ở `internalResearchOnly` (D4).

### Ảnh ship KHÔNG phải pixel gốc

Đường xử lý, ghi ra để tái lập được:

1. Cắt vùng bản khắc khỏi ảnh nguyên trang (dò biên bằng ngưỡng độ sáng, không
   ước lượng bằng mắt): hộp `(360, 619, 1222, 1993)` trên ảnh 1792×2904.
2. Cắt lần hai lấy đầu-và-vai theo tỉ lệ 0.818 để khớp khung 72×88 của thẻ —
   nếu để nguyên tỉ lệ 0.627, `BoxFit.cover` sẽ **cắt mất đỉnh đầu**.
3. Lọc median bán kính 5 để phá lưới tram của bản in ty-pô, rồi thu về 288×352.
4. Giãn tương phản, cắt 1% hai đuôi biểu đồ.

**KHÔNG** dựng lại khuôn mặt, **KHÔNG** upscale bằng mô hình sinh ảnh. Cả hai
đều sẽ bịa ra chi tiết mà bản in 1942 không hề mang, và một khuôn mặt bịa thì
tệ hơn hẳn không có ảnh.

---

## Han Cri-xti-an An-đéc-xen — `p:han-cri-xti-an-an-đéc-xen`

Ngữ văn 6, «Cô bé bán diêm» — trẻ Lớp 6 đang đọc.

| Trường | Giá trị |
|---|---|
| assetPath | `assets/people/han-cri-xti-an-an-dec-xen.png` (288×352) |
| sourcePageUrl | https://commons.wikimedia.org/wiki/File:HCA_by_Thora_Hallager_1869_crop.jpg |
| sourceName | Thora Hallager, 1869 · Bảo tàng Odense |
| author | Thora Hallager (1821–1884) |
| licence | Phạm vi công cộng — **PD-old-100-expired** (tác giả mất 1884) + công bố trước 1931 (Hoa Kỳ) |
| retrievedAt | 2026-09-07 |

**Danh tính** — khác hẳn ca Thạch Lam: đây là **ảnh chính** của bài Andersen trên Wikipedia và **20 wiki** dùng. Nguồn ghi Bảo tàng Odense, tức bảo tàng quê hương ông. Đối chiếu chéo thật, không phải một dòng siêu dữ liệu đơn độc.

---

## Ra-bin-đo-ra-nát Ta-go — `p:ra-bin-đo-ra-nát-ta-go`

Ngữ văn 6, «Mây và sóng».

| Trường | Giá trị |
|---|---|
| assetPath | `assets/people/ra-bin-do-ra-nat-ta-go.png` (288×352) |
| sourcePageUrl | https://commons.wikimedia.org/wiki/File:Rabindranath_Tagore_in_1909.jpg |
| sourceName | Les Prix Nobel 1913 (xuất bản 1914) |
| author | Generalstabens litografiska anstalt, 1909 |
| licence | Phạm vi công cộng — **PD-old-100-expired** |
| retrievedAt | 2026-09-07 |

**Danh tính** — công bố 1914 trong **«Les Prix Nobel 1913» tr.60**, niên giám của chính Quỹ Nobel cho người đoạt giải Văn chương 1913. **500 wiki** dùng. Đây là chuỗi mạnh nhất trong ba ảnh.

### ⚠ Hai ứng viên bị LOẠI — và vì sao

1. **Autochrome 1926 của Georges Chevalier** (bộ sưu tập Albert-Kahn) — đẹp nhất, nhưng **CC BY 4.0**, KHÔNG phải phạm vi công cộng. Dùng được nhưng kèm **nghĩa vụ ghi công tác giả**. Chọn bản PD để không mang nghĩa vụ ấy vào sản phẩm cho trẻ.
2. **`Rabindranath Tagore (cropped).jpg`** — PD, nhưng **tác giả không rõ**, nguồn ghi là một blog, ngày chỉ là «trước khi ông mất», và **0 wiki** dùng. PD nhưng lai lịch quá mỏng.

Đây chính là lý do luật «mỗi ảnh một hồ sơ» tồn tại: ba ảnh trong kho PD vì **ba lý do khác nhau** (PD-Vietnam 75 năm · tác giả mất >100 năm · công bố trước 1931).

---

## Chưa có chân dung (18/21 người trong `sam-stories.db`)

Không có dòng nào trong `verified` ⇒ màn chuyện của họ chạy nhánh KHÔNG ẢNH.
Đó là hành vi ĐÚNG, không phải lỗi cần vá vội. Theo dõi ở **WAL-226**.

Cạm bẫy cần tránh khi mở rộng: 18 người còn lại **không** cùng một hồ sơ pháp
lý. Nhân vật mất sau 1955 vẫn còn trong thời hạn bảo hộ; nhân vật nước ngoài
theo luật nước khác; ảnh do nhà nước chụp lại có quy tắc riêng. Không được suy
«Thạch Lam PD ⇒ nhà văn cùng thời cũng PD».
