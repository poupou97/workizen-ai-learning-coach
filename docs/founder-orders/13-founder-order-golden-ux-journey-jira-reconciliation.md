FOUNDER ORDER — GOLDEN UX JOURNEY + JIRA RECONCILIATION

Báo cáo convergence `SAM-PRODUCT-EXPERIENCE-CONVERGENCE.md`
được chấp nhận làm định hướng sản phẩm hiện tại.

Bây giờ chuyển từ PRODUCT CONVERGENCE sang PRODUCT UX EXECUTION.

Mục tiêu vòng này:

BIẾN PRODUCT MODEL + 38 CONCEPT
THÀNH MỘT TRẢI NGHIỆM MOBILE THẬT
MÀ FOUNDER CÓ THỂ CẦM NOKIA VÀ ĐÁNH GIÁ.

Nhưng TRƯỚC KHI CODE:

==================================================
1. RECONCILE JIRA VỚI PRODUCT DIRECTION MỚI
==================================================

Audit toàn bộ Jira WAL hiện tại có liên quan tới:

- Home
- Subjects
- Bookshelf
- Book Home
- Lesson
- Activity
- Tutor
- Camera
- Diagnostic
- Hint
- Review
- Assessment
- Progress
- Parent
- SAM
- Voice
- Library
- Experience Pattern
- Learning Surface
- LearningAgenda / Next Best Action
- curriculum/content presentation
- 38 concepts
- UI/UX.

Mục tiêu:

TRÁNH IMPLEMENT TICKET ĐƯỢC VIẾT
THEO CÁCH HIỂU SẢN PHẨM CŨ.

So sánh từng ticket với:

1. `SAM-PRODUCT-EXPERIENCE-REVIEW.md`
2. `SAM-PRODUCT-EXPERIENCE-CONVERGENCE.md`
3. 38 concept images gốc
4. implementation hiện tại.

Phân loại ticket:

KEEP
= vẫn đúng intent hiện tại.

RE-SCOPE
= mục tiêu đúng nhưng acceptance criteria / UX / architecture assumption đã cũ.

SUPERSEDED
= direction mới đã thay thế cách hiểu cũ.

DUPLICATE
= cùng capability/journey đã có ticket khác tốt hơn.

DONE-BUT-REVIEW
= technically Done nhưng UX/product behavior cần kiểm lại theo convergence.

DEFER
= đúng nhưng không cần cho golden journey hiện tại.

Không xoá Jira history.

Không reopen hàng loạt một cách máy móc.

Nếu ticket cũ sai:
giữ history và ghi rõ nó bị supersede/re-scope bởi product direction nào.

Đặc biệt tìm các ticket vẫn giả định:

- 38 concepts = 38 screens/spec;
- Subject Home là navigation bắt buộc;
- Book → Lesson → Intent là thứ tự cố định;
- Camera thuộc Book;
- Read/Explore không phải user intent;
- Home là dashboard;
- Home là one-task-only;
- SAM là floating chatbot/tab;
- Learning Mode là concept riêng với Intent;
- lesson = atomic experience;
- progress = % / score / XP / streak;
- book/lesson rendering = learning experience;
- architecture completion = product completion.

Những assumption này phải được đánh dấu rõ nếu còn tồn tại.

==================================================
2. DO NOT LET OLD JIRA DRIVE THE PRODUCT
==================================================

Từ vòng này:

Jira phục vụ Product Direction.

Product Direction KHÔNG được suy ngược
từ backlog cũ.

Nếu Jira và convergence mâu thuẫn:

CONVERGENCE + FOUNDER INTENT thắng.

Nhưng không được âm thầm thay ticket.

Update description/comment/acceptance criteria
để history cho thấy:

OLD ASSUMPTION
→ NEW UNDERSTANDING
→ WHY CHANGED.

==================================================
3. CREATE ONE EXECUTION EPIC / PARENT WORKSTREAM
==================================================

Sau audit, gom execution hiện tại dưới một mục tiêu rõ:

SAM GOLDEN STUDENT JOURNEY — GRADE 5

Không biến nó thành 30–50 ticket nhỏ ngay.

Chỉ tạo/re-scope số ticket vừa đủ để deliver journey.

Target journey:

HÔM NAY
→ SÁCH CỦA CON
→ GIÁ SÁCH VỚI BÌA SGK THẬT
→ CHỌN BOOK
→ BOOK HOME
→ CHƯƠNG / BÀI
→ LEARNING INTENT
→ ACTIVITY
→ EXPERIENCE
→ SAM GUIDANCE
→ XEM LẠI SGK KHI CẦN
→ TRẺ TỰ LÀM
→ HOÀN THÀNH
→ TỔNG KẾT
→ STUDENT STATE / NEXT BEST ACTION
→ HOME.

Camera là một entry khác:

CHỤP BÀI
→ NHẬN DIỆN
→ TRẺ XÁC NHẬN
→ RESOLVE CONTEXT
→ SAM GUIDANCE / HINT
→ TRẺ TỰ LÀM
→ EVIDENCE
→ TỔNG KẾT.

==================================================
4. PRODUCT BASELINE
==================================================

Founder đã xem lại toàn bộ 38 concepts.

Founder đánh giá chúng thể hiện khoảng:

70–80% PRODUCT / UI / UX INTENT

mà Founder muốn.

Do đó:

KHÔNG coi 38 concepts là final specification.

NHƯNG cũng KHÔNG coi chúng chỉ là một bộ ảnh tham khảo yếu.

Hãy dùng chúng làm:

UX / INTERACTION / VISUAL BASELINE.

Giữ và phát triển những ý tốt.

Sửa:
- pedagogy sai;
- fake metrics;
- leaderboard;
- sibling comparison;
- XP/streak;
- wrong provenance;
- answer-first behavior.

Bổ sung những phần concepts chưa giải đủ:

- Giá sách;
- Book Home;
- cách trình bày Chương / Bài / Activity;
- Learning Intents;
- cùng bài nhưng experience khác theo intent;
- tổng kết bài / môn;
- continuity;
- Next Best Action;
- SAM interaction xuyên journey.

Không tự thiết kế lại toàn bộ visual language
nếu concept hiện tại đã giải được vấn đề.

==================================================
5. GOLDEN JOURNEY FIRST
==================================================

Ưu tiên một golden journey lớp 5.

Không mở rộng tất cả K–12 trước khi journey này tốt.

Chọn một book/bài thật phù hợp từ corpus hiện có.

Journey phải chạy bằng DATA THẬT của SGK,
không phải demo text giả.

Founder cần nhìn thấy:

BOOK
→ CHAPTER / LESSON
→ ACTIVITY
→ EXPERIENCE.

Đây là phần đặc biệt quan trọng.

Không được biến nó thành:

BOOK
→ LESSON
→ dump text/cards
→ Next.

Hãy tự giải quyết cách một chương/bài SGK
trở thành một learning experience mobile.

==================================================
6. LEARNING INTENT
==================================================

Sử dụng vocabulary đã convergence.

Không dùng lại `LEARNING MODE`.

Current intents:

CHUẨN BỊ
“Mai có tiết này”

ÔN LẠI
“Cô dạy rồi”

BÀI TẬP
“Con có bài tập”

TRA CỨU
“Xem trong sách”.

Intent và Lesson/Activity
KHÔNG có parent-child order cố định.

LearningContext resolve dimensions còn thiếu.

Next Best Action có thể resolve cả:

lesson/activity + intent.

==================================================
7. SAM MUST BE VISIBLE AS A PRODUCT
==================================================

Không biến SAM thành:

- chatbot;
- floating button;
- mascot decoration;
- text generator phía cuối pipeline.

Trẻ phải cảm thấy:

“HỌC CÙNG SAM”.

SAM:

- đề nghị có lý do;
- nhớ context;
- hỏi;
- quan sát attempt;
- giúp khi cần;
- giảm hỗ trợ;
- im lặng khi trẻ đang nghĩ;
- nhận ra self-correction;
- nói chưa chắc khi chưa chắc;
- tổng kết;
- quay lại đúng chỗ cần thiết lần sau.

Dùng visual/interaction language từ concepts
nếu phù hợp.

==================================================
8. CORE MUST SERVE THIS EXPERIENCE
==================================================

Founder không cần thêm một vòng
“architecture proof” độc lập.

Hãy dùng golden journey để test core hiện tại.

Nếu core hiện tại support tốt:
REUSE.

Nếu thiếu:
FIX / EXTEND.

Nếu architecture abstraction đang làm UX khó hơn:
SIMPLIFY.

Nếu code hiện tại technically Done
nhưng không tạo được journey:
nó chưa Done ở product level.

Không hardcode từng lesson chỉ để demo.

Nhưng cũng không xây abstraction mới
nếu chưa có nhu cầu từ journey thật.

==================================================
9. USE EXISTING WORK
==================================================

Đặc biệt kiểm tra và reuse:

`LearningAgenda`

và Next Best Action logic hiện có.

Convergence đã phát hiện core này có thể đang đúng
nhưng UX hiện tại làm mất intent ở cửa Giá sách.

Ưu tiên:

CONNECT EXISTING CAPABILITIES

trước:

BUILD NEW ENGINE.

==================================================
10. REAL DEVICE LOOP
==================================================

Implement
→ tests/analyze
→ chạy Nokia
→ dùng như học sinh lớp 5
→ quan sát flow
→ sửa
→ chạy lại.

Đừng nghiệm thu journey bằng unit test בלבד.

Founder sẽ nghiệm thu PRODUCT trên máy thật.

==================================================
11. AUTONOMY
==================================================

Anh có toàn quyền với quyết định reversible:

- screen flow;
- navigation;
- component;
- state;
- data binding;
- Jira re-scope;
- implementation;
- refactor cần thiết;
- reuse/removal của code cũ.

Không hỏi Founder từng quyết định nhỏ.

Nếu implementation làm lộ ra assumption convergence sai:
được quyền sửa proposal.

Nhưng ghi lại ngắn:
ASSUMPTION → EVIDENCE → CHANGE.

==================================================
12. WHAT NOT TO DO
==================================================

Không:

- tiếp tục research architecture vô hạn;
- tạo thêm doctrine/rules không cần thiết;
- tạo 50 Jira tickets trước khi có UX;
- implement từng lesson thủ công;
- copy pixel-perfect 38 concepts;
- bỏ 38 concepts và tự thiết kế lại từ đầu;
- gọi parser/compiler thành product success;
- gọi test xanh thành UX success;
- tiếp tục ticket cũ chỉ vì nó đang ở Ready.

==================================================
13. REPORT BACK
==================================================

Khi golden journey đã đủ để Founder cầm Nokia review:

STOP.

Báo cáo ngắn:

STATUS

JIRA RECONCILIATION
- KEEP
- RE-SCOPE
- SUPERSEDED
- DONE-BUT-REVIEW
- DEFER
(chỉ các ticket quan trọng)

GOLDEN JOURNEY IMPLEMENTED

WHAT FOUNDER CAN USE NOW

REAL DEVICE EVIDENCE

WHAT WAS REUSED FROM CORE

WHAT CORE HAD TO CHANGE

WHAT CHANGED FROM 38 CONCEPTS AND WHY

WHAT OLD JIRA ASSUMPTIONS WERE REMOVED

WHAT STILL FEELS WRONG

WHAT NEEDS FOUNDER REVIEW.

Không cần report kiến trúc dài.

Mục tiêu vòng này là:

38 CONCEPTS
+
CONVERGENCE
+
CURRENT CORE
+
CURRENT JIRA

→ ONE COHERENT PRODUCT EXPERIENCE.

JIRA MUST NOT PRESERVE AN OLD PRODUCT
BY ACCIDENT.

ARCHITECTURE SERVES THE EXPERIENCE.

FOUNDER REVIEWS THE PRODUCT,
NOT THE ABSTRACTIONS.
