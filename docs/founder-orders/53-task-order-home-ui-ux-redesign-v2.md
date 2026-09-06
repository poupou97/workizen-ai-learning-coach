# TASK ORDER — HOME UI/UX REDESIGN V2
Priority: P0
Mode: REDESIGN ALLOWED
Goal: nâng Home từ functional lên product-quality.

Founder chưa duyệt UI/UX hiện tại.

Hai vấn đề đã xác nhận:
1. Bìa SGK đang hiển thị dạng vuông → sai hình thái vật thể.
2. Card bài học/gợi ý chưa tận dụng hình ảnh thật trong bài → thiếu nhận diện thị giác.

====================================
1. SÁCH / CÁC MÔN CỦA CON
====================================

Redesign card môn học theo hình thái "quyển sách".

- Bìa phải DỌC, không square.
- Ưu tiên aspect ratio khoảng 2:3 hoặc 3:4.
- Dùng bìa thật từ assets/pack/covers/.
- Không crop thành hình vuông.
- Giữ được nhận diện bìa và chữ nếu có thể.
- Border radius nhẹ.
- Shadow/elevation rất tiết chế.
- Layout nên tạo cảm giác "kệ sách".

Mỗi môn:
[cover dọc]
Tên môn
Lớp

Không cần nhồi nhiều metadata lên bìa.

Fallback:
- chỉ khi thật sự không có cover;
- dùng typography/initial;
- không thay bằng ảnh môn khác.

====================================
2. BÀI HỌC / TIẾP TỤC HỌC
====================================

Redesign lesson card thành image-first card.

Nguồn ảnh:
- ưu tiên ảnh/hình thật đã extract từ chính bài học;
- KHÔNG tạo ảnh giả;
- KHÔNG lấy ảnh từ bài khác.

Card nên:
- ngang;
- ảnh làm full-bleed background hoặc hero image;
- có gradient/scrim để text luôn đọc được;
- text đặt ở vùng không che focal content nếu có thể.

Ví dụ:

[ảnh thật bài học]

Khoa học 6
Bài 17 · Tách chất
Tiếp tục học →

Nếu bài có nhiều ảnh:
- chọn ảnh đại diện tốt nhất bằng deterministic heuristic;
- ưu tiên ảnh lớn, rõ, mang nghĩa nội dung;
- tránh icon, logo, bảng nhỏ, ảnh quá hẹp.

Nếu không có ảnh phù hợp:
- fallback clean card;
- không bịa illustration.

====================================
3. BA DẢI PHẢI KHÁC HÌNH THÁI
====================================

Không dùng một card pattern cho cả 3 section.

A. SẮP TỚI
→ compact schedule cards
→ thiên về thời gian / môn / tiết

B. CÁC MÔN CỦA CON
→ book-cover cards
→ vertical visual object

C. TIẾP TỤC HỌC
→ image-first lesson cards
→ horizontal, lớn hơn, giàu hình ảnh

Visual hierarchy phải giúp trẻ nhìn thoáng qua đã phân biệt được ba loại nội dung.

====================================
4. HOME COMPOSITION
====================================

Giữ semantic order đã chốt:

SẮP TỚI
→ CÁC MÔN CỦA CON
→ TIẾP TỤC HỌC

Nhưng được phép redesign mạnh:
- spacing
- card dimensions
- typography
- corner radius
- section headers
- scroll behavior
- density
- image treatment
- hierarchy

Không bị ràng buộc bởi layout hiện tại.

====================================
5. TRUTHFULNESS — KHÔNG ĐƯỢC PHÁ
====================================

Giữ nguyên:
- không bịa tên bài từ môn;
- không bịa giờ từ tiết;
- không bịa mastery;
- không bịa phần trăm hiểu bài;
- không dùng ảnh từ nội dung khác;
- learner context phải đúng profile active.

====================================
6. DEVICE-FIRST
====================================

Thiết kế trên màn hình thật, không chỉ dựa screenshot/widget test.

Yêu cầu kiểm:
- Nokia hiện tại;
- text dài;
- cover dọc không bị méo;
- ảnh lesson không crop mất nội dung chính;
- gradient đủ contrast;
- scroll Home không quá nặng.

====================================
7. DELIVERABLE
====================================

Trước khi merge:
- ảnh Home full screen;
- close-up "Các môn của con";
- close-up "Tiếp tục học";
- ví dụ lesson có ảnh;
- ví dụ lesson không có ảnh;
- ví dụ subject có cover;
- ví dụ fallback không cover.

Báo ngắn:
1. layout trước;
2. layout sau;
3. asset selection rule;
4. fallback rule;
5. test/analyze;
6. device evidence;
7. commit/PR.

Không merge nếu chỉ thay màu/bo góc.
Mục tiêu là thay đổi rõ ràng về visual hierarchy và object semantics.
