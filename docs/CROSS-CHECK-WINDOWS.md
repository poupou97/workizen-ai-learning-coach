# VÒNG ĐỐI CHIẾU — máy Windows báo số, máy Mac chấm

Founder đã tải 5 gói zip vào gốc repo trên máy mới. Vòng này **chỉ để đo và
đối chiếu**, chưa làm tính năng.

> **Đáp án không nằm trong tài liệu này.** Bản đối chiếu do phía Mac giữ.
> Vì vậy lệnh dưới đòi **đầu ra nguyên văn của lệnh**, không nhận số chép
> lại từ tài liệu. Chép số từ `docs/` là làm hỏng chính phép đo.

Sao chép nguyên khối dưới đây gửi Claude ở máy mới.

---

```
# FOUNDER — VÒNG ĐỐI CHIẾU SAU DI TRÚ

Tôi đã tải 5 gói zip vào gốc repo. Việc của bạn vòng này là KIỂM và BÁO SỐ
để tôi đối chiếu với máy cũ. CHƯA làm tính năng, CHƯA sửa gì.

Tôi có sẵn bảng đáp án ở máy cũ. Số bạn báo phải là số ĐO ĐƯỢC, dán nguyên
văn đầu ra terminal. Chép số từ trong docs/ ra là làm hỏng phép đo — lệch là
tôi thấy ngay.

==================================================
A. TRƯỚC KHI CHẠM VÀO ZIP
==================================================

    git pull
    git log --oneline -1
    git status --short

`git pull` là bắt buộc — tôi vừa thêm `*.zip` vào .gitignore. Không có nó thì
`git status` ngập 25 GB và một `git add -A` là hỏng repo.

Nếu `git status` vẫn liệt kê tệp .zip ⇒ DỪNG, báo tôi.

==================================================
B. KIỂM KÊ ZIP — chưa giải nén
==================================================

Báo cho mỗi tệp trong 5 tệp: TÊN · SỐ BYTE · SHA-256 đầy đủ

    Get-ChildItem *.zip | Select-Object Name, Length
    Get-FileHash *.zip -Algorithm SHA256 | Format-List

Đối chiếu với SHA256SUMS.txt đi kèm. Lệch một ký tự ⇒ tải lại tệp đó, KHÔNG
giải nén, báo tôi.

Rồi đếm số mục bên trong mỗi tệp mà chưa cần bung:

    tar -tf T1-critical.zip | Measure-Object -Line

Làm cho cả 5. Báo 5 con số.

==================================================
C. GIẢI NÉN
==================================================

Thứ tự: T1 → T3 → T3b → T2a → T2b.

Bật long paths trước cho chắc. ĐO ĐƯỢC trên 93.179 đường (kể cả biến thể
NFD): dài nhất **169 ký tự**. Cộng gốc kiểu `C:\Projects\...` (~48) là 217 —
vẫn dưới 260, nên long paths là bảo hiểm chứ không phải chốt chặn. Chỉ vượt
260 nếu thư mục gốc từ 91 ký tự trở lên.

    HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled = 1

Mọi đường bên trong zip bắt đầu bằng `repo-heavy/`. Sau khi bung phải BỎ tầng
đó — `nguon-chi-thuc`, `poc-out`, `assets` nằm thẳng ở gốc repo. Sai tầng thì
cổng verify ở mục D sẽ báo thiếu toàn bộ.

BA ĐIỀU KHÔNG LÀM:

1. `nguon-chi-thuc/` sau khi bung sẽ chứa 12 tệp .zip NỮA — đó là bản tải gốc
   từ Google Drive, giữ nguyên làm bản lưu. KHÔNG bung chúng. Kho đã dựng từ
   `poc-out/`, không phải từ đây.
2. KHÔNG xoá 5 gói zip cho tới khi mục D in «ĐẠT».
3. Tên tệp tiếng Việt có dấu tổ hợp kiểu macOS. Nếu thấy tên trông hỏng,
   BÁO — đừng tự đổi tên. Cổng verify đã biết xử lý hai dạng NFC/NFD, mắt
   người không phải trọng tài ở đây.

==================================================
D. CỔNG VERIFY — dán nguyên văn
==================================================

    python tool\ops\migration_manifest.py --base . --verify MIGRATION-MANIFEST.json

Dán TOÀN BỘ đầu ra, gồm cả bốn dòng đếm (thiếu · lệch kích thước · sai băm ·
thừa), không chỉ dòng kết luận.

Chưa in «ĐẠT» thì CHƯA khôi phục xong. Đừng sửa bản kê cho khớp cây tệp —
bản kê là chuẩn, cây tệp là cái đang bị nghi.

==================================================
E. BỘ NHỚ LÀM VIỆC
==================================================

`claude-memory/` nằm trong T1, KHÔNG thuộc repo. Chép vào thư mục memory của
bạn trên máy này rồi đọc hết.

Báo: đếm được bao nhiêu tệp `.md`, và MEMORY.md liệt kê bao nhiêu dòng.

Hai số này lệch nhau ĐÚNG 1 là bình thường — mục lục không tự kể tên nó.
Lệch khác 1 nghĩa là có bài học nằm ngoài mục lục — báo tôi tên tệp lệch.

==================================================
F. NGHIỆM THU MÔI TRƯỜNG — dán nguyên văn dòng tổng kết
==================================================

    flutter --version
    flutter analyze
    flutter test
    cd tool ; python -m unittest discover -s tests

Dán dòng tổng kết THẬT của mỗi lệnh (kiểu «All tests passed» kèm số, «Ran N
tests»). Đừng viết lại thành «đạt».

Số test lệch so với bảng của tôi ⇒ BÁO, tuyệt đối đừng sửa test cho khớp.
Test lệch sau di trú thường là dữ liệu thiếu, không phải test sai.

Báo cả SỐ TEST BỎ QUA. Bỏ qua nhiều hơn bình thường nghĩa là có dữ liệu chưa
khôi phục — và nó KHÔNG làm test đỏ. Đây đúng là chỗ CI xanh mà dữ liệu thiếu.

==================================================
G. ĐỌC DỰ ÁN
==================================================

Giờ mới đọc, theo thứ tự:

1. docs/HANDOFF-TO-NEXT-CLAUDE.md
2. docs/MASTER-TODO.md
3. docs/MACHINE-MIGRATION.md
4. CLAUDE.md gốc workspace

Đọc xong trả lời bốn câu bằng lời của bạn — tôi dùng để kiểm bạn có thật sự
nắm hay chỉ lướt:

1. Vì sao máy Windows này KHÔNG được chạy lại OCR? Nói rõ hệ quả kỹ thuật,
   đừng chỉ nói «vì không tương thích».
2. SAM_READY và ANSWER_CHECK_READY khác nhau ở chỗ nào, và vì sao
   ANSWER_CHECK_READY đang là 0?
3. Kể một giả thuyết đã bị BÁC BỎ trong dự án, và vì sao nó phải được giữ lại
   trong tài liệu thay vì xoá đi.
4. Trần 33 bài hiện nay bị chặn bởi cái gì?

==================================================
H. KHÔNG LÀM
==================================================

KHÔNG chạy OCR, KHÔNG đổi OCR engine, KHÔNG cài ocrmac.
KHÔNG dựng lại pack/fixture — đã có trong bản khôi phục.
KHÔNG mở workstream đang đóng băng (docs/HANDOFF-TO-NEXT-CLAUDE.md §8).
KHÔNG commit, KHÔNG mở PR trong vòng này.

==================================================
I. BÁO CÁO RỒI DỪNG
==================================================

Một bản báo cáo, đủ A–G, số thật, đầu ra nguyên văn. Chỗ nào không chạy được
thì ghi KHÔNG CHẠY ĐƯỢC kèm thông báo lỗi — đừng bỏ trống, đừng đoán.

Rồi DỪNG. Tôi đối chiếu với máy cũ xong mới giao việc tiếp.

Viết tiếng Việt.
```
