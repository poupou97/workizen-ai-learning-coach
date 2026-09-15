# LỆNH MỞ ĐẦU — dán cho Claude trên máy Windows

> Sao chép nguyên khối dưới đây làm tin nhắn ĐẦU TIÊN gửi Claude ở máy mới.

---

```
# FOUNDER — TIẾP QUẢN DỰ ÁN «HỌC CÙNG SAM» TRÊN MÁY MỚI

Đây là máy Windows mới. Dự án vừa di trú từ macOS. Bạn KHÔNG bắt đầu từ số
không — có một Claude đã làm dự án này nhiều tháng và để lại bàn giao đầy đủ.

==================================================
0. ĐỌC TRƯỚC — CHƯA LÀM GÌ CẢ
==================================================

Đọc theo đúng thứ tự này, hết rồi mới gõ dòng mã đầu tiên:

1. docs/HANDOFF-TO-NEXT-CLAUDE.md   ← đọc KỸ, đây là định hướng
2. docs/MASTER-TODO.md              ← trạng thái cấp Founder
3. docs/MACHINE-MIGRATION.md        ← máy, dữ liệu, bootstrap
4. CLAUDE.md ở gốc workspace

Không tóm tắt lại cho tôi. Đọc để LÀM ĐÚNG.

==================================================
1. KHÔI PHỤC DỮ LIỆU NẶNG
==================================================

Dữ liệu nặng KHÔNG nằm trong Git. `git clone` chỉ cho bạn mã.

Tải từ OneDrive: Documents / Workizen Learning / zips

Giải nén theo thứ tự T1 → T3 → T3b → T2a → T2b.

TRƯỚC KHI GIẢI NÉN: đối chiếu băm

    Get-FileHash <tệp>.zip -Algorithm SHA256

so với SHA256SUMS.txt. Khác một ký tự ⇒ tải lại, KHÔNG giải nén.

Bên trong zip mọi đường bắt đầu bằng `repo-heavy/`. Sau khi giải, chuyển
`nguon-chi-thuc`, `poc-out`, `assets` lên thẳng gốc repo (bỏ tầng
`repo-heavy`).

Bật long paths trước khi giải nén — đường dài nhất 169 ký tự, cộng
thư mục gốc là vượt 260.

==================================================
2. CỔNG BẮT BUỘC — VERIFY
==================================================

    python tool\ops\migration_manifest.py --base . --verify MIGRATION-MANIFEST.json

Phải in «ĐẠT». Chưa ĐẠT thì CHƯA ĐƯỢC coi là khôi phục xong và KHÔNG được
làm gì tiếp. Báo tôi con số sai lệch.

==================================================
3. KHÔI PHỤC BỘ NHỚ LÀM VIỆC
==================================================

Trong T1-critical.zip có thư mục `claude-memory/` — 38 tệp: 37 bài học đã trả giá
thật. Nó KHÔNG thuộc repo.

Chép cả 38 tệp vào thư mục memory của bạn trên máy này — trên Windows là

    %USERPROFILE%\.claude\projects\<slug-của-repo>\memory\

rồi ĐỌC MEMORY.md và đọc hết. Trong đó có những cái bẫy đã tốn nhiều giờ để
phát hiện. Không đọc thì bạn sẽ dẫm lại từng cái.

==================================================
4. TUYỆT ĐỐI KHÔNG LÀM
==================================================

KHÔNG chạy lại OCR trên Windows.

Kho canonical dựng bằng docling + ocrmac (Apple Vision, chỉ macOS). Mọi con
số của dự án hiệu chỉnh trên đầu ra ấy. Engine khác = MỘT KHO KHÁC, không
phải một bản sao. Kho có sẵn adapter RapidOCR/PaddleOCR — đó là ứng viên của
một vòng bakeoff cũ, KHÔNG phải bản thay thế.

KHÔNG dựng lại pack/fixture để «cho chắc». Chúng đã có trong bản khôi phục.

KHÔNG tự mở workstream nào trong danh sách ĐÓNG BĂNG ở
docs/HANDOFF-TO-NEXT-CLAUDE.md §8.

KHÔNG hồi sinh ba giả thuyết đã bị bác bỏ.

==================================================
5. NGHIỆM THU MÔI TRƯỜNG
==================================================

    flutter analyze                                   → sạch
    flutter test                                      → 1.495 đạt, 11 bỏ qua
    cd tool && python -m unittest discover -s tests    → 1.516 test, 23 bỏ qua
    flutter build apk --profile

Số test khác con số trên ⇒ báo tôi, đừng tự sửa test cho khớp.

==================================================
6. BÁO CÁO RỒI DỪNG
==================================================

Báo đúng mẫu ở cuối docs/MASTER-TODO.md, gồm:

- verify manifest: ĐẠT / sai lệch bao nhiêu
- bộ nhớ đã khôi phục: bao nhiêu tệp
- flutter analyze / flutter test / python test: số thật
- build APK: được / không
- thiết bị: có adb thấy máy không

Rồi DỪNG. Không tự chạy việc tiếp theo.

Việc tiếp theo tôi sẽ chọn giữa hai hướng đã nêu ở
docs/HANDOFF-TO-NEXT-CLAUDE.md §9:

  B — tìm quy tắc trong SGV cho 15/33 bài chưa ràng buộc được
  C — ghép SGK↔SGV cho lớp 1–5 (hiện đóng góp 0 bài)

==================================================
7. CÁCH TÔI LÀM VIỆC
==================================================

Tôi ra lệnh dài, đánh số mục — đọc hết rồi mới làm.

Sau khi tôi duyệt một vòng, bạn chạy tự chủ: đo/dựng → test → PR → CI xanh →
merge main → bằng chứng máy thật → sửa tiếp. Không hỏi tôi từng PR.

Kiểm-đột-biến là BẮT BUỘC: sửa xong thì cố ý làm hỏng từng chốt, test phải
ĐỎ. Đột biến sống sót nghĩa là bất biến chưa được chứng minh.

Không báo phần trăm nếu không có mẫu số tái hiện được.

Tôi quý việc bạn tự bác bỏ mình hơn là một con số đẹp. Tìm ra lỗi của chính
mình thì báo thẳng — đó là bằng chứng tốt, không phải thất bại.

Viết tiếng Việt.

BẮT ĐẦU TỪ MỤC 0.
```
