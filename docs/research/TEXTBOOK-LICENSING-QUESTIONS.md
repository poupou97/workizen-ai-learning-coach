# Bản quyền SGK — BLOCKER, không phải câu hỏi mở

**Ngày:** 2026-08-31 · cập nhật sau QĐ Founder

## Trạng thái

| | |
|---|---|
| R&D / POC kỹ thuật | ✅ **TECHNICAL_POC_ALLOWED_BY_FOUNDER** (31/08) |
| Thương mại hoá | 🔴 **COMMERCIAL_USE_LEGAL_REVIEW_PENDING** |

Founder đã đọc điều khoản dưới đây và quyết định **tiếp tục POC kỹ thuật local/private**.
Đây **không** phải tuyên bố corpus đã được cleared. Agent **không được** tự nâng lên
`LEGAL_APPROVED`, và **không được** dùng chính điều khoản này để dừng POC lần nữa — trừ
khi phát hiện rủi ro MỚI nghiêm trọng hơn.

Ranh giới đang áp dụng: xem §7 bên dưới.
**Bằng chứng:** đọc trực tiếp trang bản quyền trong chính tệp PDF của Founder

---

## 1. Điều tìm được — nguyên văn, không diễn giải

`05-sgk-toan-5-tap-mot.pdf`, trang PDF 141 (trang bản quyền):

> **Bản quyền © (2024) thuộc Nhà xuất bản Giáo dục Việt Nam.**
>
> *"Xuất bản phẩm đã đăng kí quyền tác giả. Tất cả các phần của nội dung cuốn sách
> này đều **không được sao chép, lưu trữ, chuyển thể dưới bất kì hình thức nào** khi
> chưa có sự cho phép bằng văn bản của Nhà xuất bản Giáo dục Việt Nam."*

Siêu dữ liệu xuất bản trên cùng trang:

| | |
|---|---|
| Bộ sách | **Kết nối tri thức với cuộc sống** |
| NXB | Nhà xuất bản Giáo dục Việt Nam (nxbgd.vn) |
| ISBN | tập một `978-604-0-39223-7` · tập hai `978-604-0-39224-4` |
| Mã số | `G1HH5T003h26` · Số ĐKXB `7-2026/CXBIPH/43-09/GD` |
| Giá bìa | 18.000 đ (bìa sau) |

---

## 2. Vì sao đây là blocker chứ không phải rủi ro cần theo dõi

Work order §W dặn: *"Không tự đưa legal conclusion nếu chưa có evidence."*
Tôi **không** suy luận từ sự im lặng. Ở đây có **văn bản cấm tường minh**, và ba
động từ nó cấm trùng khớp từng cái một với ba bước của pipeline đã thiết kế:

| Điều khoản cấm | Bước tương ứng trong POC |
|---|---|
| **sao chép** | trích text/OCR từng trang |
| **lưu trữ** | dựng chunk store, index, embedding |
| **chuyển thể dưới bất kì hình thức nào** | biến thành Curriculum Graph, concept, câu hỏi luyện tập |

Giả định *"có PDF ⇒ được xây trên đó"* bị chính tài liệu nguồn bác bỏ.

⚠️ Đây **không** phải kết luận pháp lý. Tôi không phải luật sư và không nói điều gì là
hợp pháp hay bất hợp pháp. Tôi báo cáo: **nguồn mang một điều khoản hạn chế bằng văn
bản, và điều khoản đó gọi tên đúng các thao tác chúng ta định làm.** Ai đủ thẩm quyền
đọc và quyết định là việc của Founder.

## 3. Điều này KHÔNG chặn

- Sản phẩm AI Learning Coach nói chung.
- Camera Tutor: học sinh chụp **bài trong sách của chính mình**, xử lý **trên máy**,
  không lưu trữ tập trung — hình thái pháp lý khác hẳn việc ingest cả bộ sách.
- Dạy theo **chương trình GDPT 2018** (Bộ GD&ĐT ban hành) — *chương trình* và *sách*
  là hai thứ khác nhau. Chương trình là văn bản nhà nước.
- Nội dung tự soạn bám chuẩn chương trình.

## 4. Bốn đường đi, cần Founder chọn

| | Đường | Ghi chú |
|---|---|---|
| **A** | Xin phép bằng văn bản NXBGDVN | Đúng thứ điều khoản đòi. Chậm, nhưng là đường sạch duy nhất để dùng chính SGK |
| **B** | Bám **Chương trình GDPT 2018** thay vì SGK | Chương trình là văn bản của Bộ, khác hẳn về bản quyền. Graph dựng từ *yêu cầu cần đạt*, không từ trang sách |
| **C** | Tự soạn nội dung theo chuẩn chương trình | Đắt về nội dung, sạch về pháp lý, và là tài sản của Workizen |
| **D** | Camera-only, on-device, không corpus | Học sinh mang sách của mình tới; app không lưu trữ SGK. Đúng doctrine Local First |

⭐ **B + D** có thể là tổ hợp mạnh nhất: graph từ chương trình nhà nước, nội dung tự
soạn, và Camera Tutor xử lý ngay trên máy — không repo nào chứa SGK.

## 5. Đã làm ngay để giảm rủi ro kỹ thuật

`.gitignore` chặn `nguon-chi-thuc/`, `*.pdf`, `poc-out/`. Trước đó thư mục 9,8GB này
nằm **untracked bên trong repo cha** `~/projects` (remote GitHub `workforceos-project`)
và `.gitignore` của repo cha không có dòng nào chặn — một lệnh `git add -A` là đủ để
**đăng tải lại** toàn bộ SGK lên GitHub công khai. Đã kiểm: git nay thấy **0** đường
dẫn SGK.

## 6. Câu hỏi còn để mở (không tự trả lời)

1. NXBGDVN có chương trình cấp phép cho nền tảng giáo dục số không?
2. "Trích dẫn hợp lý" theo Luật SHTT Việt Nam phủ tới đâu cho mục đích dạy học?
3. Xử lý **trên thiết bị của người dùng**, không lưu trữ tập trung — khác biệt pháp lý ra sao?
4. Học sinh chụp trang sách **mình đã mua** thì khác gì với việc nhà cung cấp ingest sẵn?
5. Ba bộ sách được phê duyệt (Kết nối tri thức · Chân trời sáng tạo · Cánh Diều) có
   điều khoản khác nhau không? *(Kho hiện tại chỉ có MỘT bộ — xem §7 inventory.)*


---

## 7. Ranh giới R&D đang áp dụng (QĐ Founder 31/08)

**Được:** OCR local · trích text local · chunking · embedding local · vector index local ·
metadata · mapping chương trình · trích concept · giả thuyết prerequisite · thí nghiệm
retrieval · thí nghiệm Camera Tutor.

**Chưa được:** commit SGK vào git · push lên GitHub · corpus công khai · phát tán lại PDF ·
cho người dùng tải trang sách · API SGK công khai · fine-tune model dùng chung từ corpus ·
thương mại hoá dựa trên corpus trước Legal Gate.

⭐ **Cách ly kiến trúc (§15):** mọi truy cập nội dung đi qua `KnowledgeContentProvider`.
Mục tiêu là **xoá hoặc thay corpus SGK mà không phá** Student Knowledge Graph, Tutor
Engine, Parent Coach, Curriculum model. Nếu Legal Gate ra kết quả xấu, ta thay
`LocalResearchTextbookProvider` bằng nguồn khác — không viết lại sản phẩm.
