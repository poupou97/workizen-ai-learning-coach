# TASK ORDER — HỌC CÙNG SAM
## P0 — Thiết lập Bottom Navigation 5 tab + IA cấp 1
Priority: HIGHEST / DO NOW
Mode: IMPLEMENTATION FIRST — KHÔNG NGHIÊN CỨU DÀI
Product: Học cùng SAM
Goal: tạo navigation cấp 1 rõ ràng, ổn định và dùng được ngay.

==================================================
1. MỤC TIÊU
==================================================

Hiện app chưa có bottom navigation đủ rõ.

Founder chốt IA cấp 1 gồm 5 tab:

1. Trang chủ
2. Giá sách
3. SAM
4. Thành tích
5. Thêm

Thứ tự bắt buộc:

Trang chủ | Giá sách | SAM | Thành tích | Thêm

SAM nằm chính giữa và là AI Tutor entry point chính.

Yêu cầu:
- Audit navigation hiện tại thật nhanh.
- Tận dụng structure/component hiện có nếu phù hợp.
- Sau audit triển khai ngay.
- Không dành nhiều thời gian viết proposal/research.
- Không redesign toàn bộ app trong task này.
- Ưu tiên có functional shell chạy được trên máy thật/emulator trước.

==================================================
2. BOTTOM NAVIGATION
==================================================

Thiết lập persistent bottom navigation:

[Home] [Bookshelf] [SAM] [Achievements] [More]

Label tiếng Việt:

🏠 Trang chủ
📚 Giá sách
🦉 SAM
🏆 Thành tích
☰ Thêm

SAM phải được tạo visual hierarchy nhẹ:
- nằm chính giữa;
- icon SAM/owl/mascot nếu asset phù hợp đã tồn tại;
- có thể lớn hơn các icon khác một chút;
- selected state rõ ràng;
- KHÔNG biến thành floating button quá lớn;
- KHÔNG phá Material/iOS navigation convention.

Bottom navigation phải:
- giữ nguyên khi chuyển giữa 5 tab;
- giữ state của từng tab nếu kiến trúc hiện tại cho phép;
- không reload màn hình vô lý khi đổi tab;
- support Android/iOS safe area;
- không đè lên Android system navigation;
- kiểm tra đặc biệt thiết bị có 3-button navigation.

==================================================
3. TAB 1 — TRANG CHỦ
==================================================

Không redesign Home sâu trong task này.

Chỉ đảm bảo Home trở thành root screen của tab Trang chủ.

Nếu Home hiện tại đã tồn tại:
- reuse;
- chỉnh navigation wiring;
- không rewrite.

Home về dài hạn sẽ trả lời:
"Hôm nay con nên học gì?"

Nhưng task này chỉ cần:
- render ổn;
- selected nav đúng;
- các CTA hiện tại không bị vỡ.

==================================================
4. TAB 2 — GIÁ SÁCH
==================================================

Tạo root tab "Giá sách".

Concept:

Giá sách = nội dung học theo profile hiện tại của học sinh.

Context ưu tiên:

Student
→ Grade/Class
→ Subject
→ Chapter
→ Lesson

Ví dụ header:

Nguyễn Minh Anh
Lớp 5 ▾

Sau đó:

Toán
Tiếng Việt
Khoa học
Lịch sử & Địa lý
Tiếng Anh
...

Không bắt user chọn lại "Lớp 5" mỗi lần vào Giá sách nếu student profile đã có.

Nếu app chưa đủ data:
- tạo UI shell sử dụng data/mock hiện có;
- không invent backend phức tạp;
- đánh dấu integration point rõ ràng.

Learning Views KHÔNG tạo tab bottom riêng.

Learning Views phải thuộc lesson/LearningContext bên dưới Giá sách.

==================================================
5. TAB 3 — SAM
==================================================

SAM là tab trung tâm.

Đây KHÔNG chỉ là "Chat".

Concept:

SAM = AI Tutor interaction hub.

Các interaction có thể gồm:

- Free conversation
- Nhập câu hỏi
- Chụp bài
- Voice hỏi SAM

Màn root có thể tối giản:

SAM
"Con muốn hỏi gì hôm nay?"

[📷 Chụp bài]
[⌨️ Nhập câu hỏi]
[🎤 Hỏi bằng giọng nói]

+ conversation UI hiện có nếu đã tồn tại.

QUAN TRỌNG:
- reuse chat/conversation stack hiện tại;
- không xây chat engine mới;
- không rewrite Camera Tutor;
- chỉ tạo đúng entry point/navigation.

Nếu hiện có nhiều điểm vào chat/SAM:
hãy gom navigation sao cho tab SAM trở thành canonical root.

==================================================
6. TAB 4 — THÀNH TÍCH
==================================================

Tạo root tab "Thành tích".

Task này chưa cần xây analytics engine mới.

Ưu tiên reuse dữ liệu hiện có:
- lesson progress;
- learning history;
- mastery;
- exercise results;
- streak nếu đã có.

Nếu data chưa đủ:
tạo shell có state hợp lý.

Khung mong muốn:

Thành tích

Tuần này
- số buổi học
- thời gian học
- số bài tập
- kiến thức mới

SAM nhận thấy
- phần đã vững
- phần cần luyện thêm

Bản đồ kiến thức / mastery
nếu component/data hiện tại đã hỗ trợ.

KHÔNG gamification quá mức.
Không cần leaderboard.
Không cần XP economy trong task này.

==================================================
7. TAB 5 — THÊM
==================================================

Tạo root tab "Thêm".

Đưa các chức năng secondary vào đây nếu chúng đang rải rác:

- Hồ sơ học sinh
- Chuyển/thêm học sinh
- Hồ sơ phụ huynh
- Lớp/chương trình học
- Nhật ký học tập
- Nội dung tải xuống
- Thông báo
- Quyền riêng tư
- AI & dữ liệu
- Trợ giúp
- Cài đặt

Không cần implement feature chưa tồn tại.

Chỉ:
- reuse screen hiện có;
- gom navigation hợp lý;
- placeholder có kiểm soát nếu thật sự cần.

==================================================
8. PERSISTENCE RULE
==================================================

Bottom navigation mặc định phải luôn tồn tại.

Chỉ hide trong các immersive/focus flow như:

- Camera capture full screen
- Quiz/test full screen
- Full-screen Learning View
- Video lesson full screen
- Flow đặc biệt cần tập trung hoàn toàn

Khi back:
bottom navigation phải trở lại bình thường.

==================================================
9. ROUTING / ARCHITECTURE
==================================================

Trước khi code:

Audit nhanh:
- router/navigation package đang dùng;
- shell/root scaffold hiện tại;
- screen ownership;
- deep links;
- tab state;
- Back button behavior.

Sau đó chọn giải pháp ít phá nhất.

Không:
- thay navigation framework nếu không cần;
- rewrite architecture;
- tạo duplicate screens;
- copy-paste business logic;
- phá deep link hiện có.

Ưu tiên:
existing architecture
→ minimal delta
→ production-safe.

==================================================
10. UX DETAILS
==================================================

Bottom navigation cần:

- selected/unselected state rõ;
- touch target đủ lớn;
- label không bị cắt;
- hỗ trợ Vietnamese text;
- dark/light theme nếu app đang support;
- responsive trên máy nhỏ;
- Android gesture navigation;
- Android 3-button navigation;
- iPhone safe-area/home indicator.

SAM center icon có thể nổi bật nhẹ nhưng phải cùng design language.

Không tự ý redesign Design System.

==================================================
11. TEST
==================================================

Minimum acceptance:

A. App launch → Trang chủ selected.

B. Tap lần lượt:
Trang chủ
→ Giá sách
→ SAM
→ Thành tích
→ Thêm

Không crash.

C. Back behavior hợp lý.

D. Chuyển tab không tạo duplicate route stack bất thường.

E. Mở một flow full-screen → bottom nav hide.

F. Back → bottom nav trở lại.

G. Không overlap Android system navigation.

H. Không regression flow:
- Camera Tutor
- SAM/chat
- lesson
- student/profile
nếu các flow này đang tồn tại.

Chạy:
- existing unit/widget tests;
- targeted navigation tests;
- flutter analyze;
- smoke test.

Nếu repo có device test procedure thì thực hiện theo procedure hiện tại.

==================================================
12. PHẠM VI KHÔNG LÀM
==================================================

Task này KHÔNG nhằm:

- redesign toàn bộ Home;
- hoàn thiện toàn bộ Bookshelf;
- build knowledge graph mới;
- build analytics engine;
- build achievement/game economy;
- build AI backend mới;
- refactor toàn app;
- nghiên cứu competitor;
- tạo ADR dài.

Mục tiêu là:

"Đưa IA 5 tab vào app thật nhanh, đúng kiến trúc và chạy ổn."

==================================================
13. FOUNDER DECISION — ĐÃ CHỐT
==================================================

Không cần hỏi lại Founder về cấu trúc tab.

Canonical IA:

Trang chủ
Giá sách
SAM
Thành tích
Thêm

SAM = tab chính giữa.

Learning Views = bên trong LearningContext/lesson,
KHÔNG phải bottom tab.

Grade/Class = context của student profile,
KHÔNG bắt chọn lại mỗi lần vào Giá sách.

==================================================
14. EXECUTION ORDER
==================================================

Làm theo thứ tự:

P0.1 Audit navigation hiện tại — thật nhanh
P0.2 Implement root navigation shell
P0.3 Wire 5 tabs
P0.4 Reuse existing screens
P0.5 Implement SAM center hierarchy
P0.6 Fix safe area/system nav
P0.7 Smoke test
P0.8 Add focused tests
P0.9 Screenshot 5 tab states
P0.10 Report + commit/PR

Nếu phát hiện vấn đề nhỏ có thể tự xử lý:
→ xử lý luôn.

Chỉ dừng hỏi Founder nếu có blocker kiến trúc nghiêm trọng hoặc phải phá một quyết định sản phẩm đã chốt.

==================================================
15. DELIVERABLE
==================================================

Khi xong báo ngắn:

1. Navigation cũ là gì.
2. Đã thay đổi file/component nào.
3. 5 tab đã hoạt động chưa.
4. Screen nào reuse.
5. Screen nào hiện chỉ là shell.
6. Bottom nav hide ở flow nào.
7. Test/analyze result.
8. Screenshot:
   - Trang chủ
   - Giá sách
   - SAM
   - Thành tích
   - Thêm
9. Commit hash.
10. PR nếu workflow repo yêu cầu.

Không gửi report nghiên cứu dài.

Ưu tiên SHIPPING.
