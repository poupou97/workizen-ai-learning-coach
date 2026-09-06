# FOUNDER ADDENDUM — ROUND 7
## PROFILE THEO TỪNG HỌC SINH + LỚP/MÔN/SÁCH + THỜI KHÓA BIỂU + HOME NHIỀU MÔN

Tôi vừa review Round 7 trên máy thật.

Ngoài việc sửa Home thành multi-subject Home + Smart Learning Cards,
cần audit và hoàn thiện một lớp nền quan trọng:

PROFILE
→ GRADE
→ SUBJECT / BOOK SET
→ TIMETABLE
→ LEARNING PROGRESS / STUDENT STATE
→ TODAY HOME / NEXT ACTION

Đây là P0 PRODUCT INTEGRITY + UX.

KHÔNG ĐƯỢC GIẢ ĐỊNH IMPLEMENTATION HIỆN TẠI ĐÃ ĐÚNG.
PHẢI AUDIT CODE + DATA + DEVICE BEHAVIOR TRƯỚC.

==================================================
1. AUDIT PROFILE ISOLATION
==================================================

Kiểm tra hiện tại hệ thống có thực sự phân biệt theo từng Learner Profile hay chưa.

Phải audit tối thiểu:

LearnerProfile
Grade
Subjects
Books
Timetable
LearningSession
Lesson history
Opened learning views
Student State
Validated Evidence
Progress
Next Action
Recent lessons
Home recommendations

Câu hỏi bắt buộc:

Nếu cùng một account/device có:

Na — Lớp 6
Minh — Lớp 5

thì:

Na có thấy đúng sách/môn Lớp 6 không?

Minh có thấy đúng sách/môn Lớp 5 không?

Progress Bài 17 của Na
có xuất hiện sang Minh không?

History có leak không?

Evidence có leak không?

Next Action có leak không?

Home Smart Cards có leak không?

Timetable có leak không?

Không chấp nhận isolation chỉ ở UI.

Phải trace persistence/storage/runtime.

==================================================
2. INVARIANT
==================================================

Giữ invariant:

DEVICE != USER
ACCOUNT != LEARNER

Learning state phải thuộc đúng:

LearnerProfileId

Không được chỉ dựa vào:

currentGrade
device
account
global singleton
hardcoded learner
hardcoded grade.

Tìm toàn bộ hardcoded:

Na
Lớp 6
grade 6
KHTN 6
Bài 17

và phân loại:

GOLDEN FIXTURE
UI DEMO
PRODUCTION PATH
BUG.

==================================================
3. PROFILE PHẢI SỞ HỮU LEARNING CONTEXT
==================================================

Thiết kế/kiểm chứng model theo hướng:

Account
 └── LearnerProfile
      ├── Grade
      ├── Curriculum / Book Set
      ├── Subjects
      ├── Timetable
      ├── Learning History
      ├── Student State
      ├── Evidence
      └── Recommendation Context

Không bắt buộc dùng đúng class hierarchy này.

Audit kiến trúc hiện tại trước.

Không tạo duplicate state model nếu đã có model phù hợp.

==================================================
4. PROFILE SWITCH TEST
==================================================

Tạo bounded test:

PROFILE A:
Na
Lớp 6

PROFILE B:
Minh
Lớp 5

Cho Na:

mở KHTN 6 Bài 17
mở Đọc
mở Trực quan

Sau đó switch Minh.

Expected:

Minh KHÔNG được thấy progress của Na.

Home của Minh phải dùng:

Grade 5
subjects/books Grade 5
Timetable của Minh
learning history của Minh.

Sau đó switch lại Na.

Na phải giữ đúng state cũ.

Test:

restart app
switch profile
restart app
switch lại.

Có automated regression test nếu architecture cho phép.

==================================================
5. TIMETABLE LÀ FIRST-CLASS PRODUCT FEATURE
==================================================

Round 7 hiện chưa thể hiện rõ concept Thời khóa biểu.

Khôi phục nó thành một phần của Learning Home.

Timetable không chỉ là màn hình trang trí.

Nó phải tham gia vào:

TODAY
Smart Learning Cards
Next Action candidate generation
Subject ordering
Learning context.

Ví dụ:

THỨ HAI

Toán
Tiếng Việt
KHTN
Tiếng Anh

Home hôm đó ưu tiên Smart Cards
của những môn này.

Nhưng:

TIMETABLE != PEDAGOGY.

Timetable chỉ là context/signal.

Không được biến:

"Có tiết Toán hôm nay"

thành:

"Con phải học bài X"
hoặc
"Con chưa hiểu bài X"

nếu Student State không chứng minh.

==================================================
6. TIMETABLE UX
==================================================

Research lại concept timetable đã có trong repo/docs/design history nếu tồn tại.

Không tự thiết kế mới trước khi audit concept cũ.

UX tối thiểu:

HÔM NAY
Thứ Hai · 4 môn

[Toán] [Tiếng Việt] [KHTN] [Tiếng Anh]

→ Xem thời khóa biểu

Full timetable có thể theo kiểu:

          T2   T3   T4   T5   T6
Tiết 1
Tiết 2
Tiết 3
Tiết 4
...

Có thể nghiên cứu UX mobile tốt hơn dạng bảng cổ điển.

Ưu tiên child-friendly.

==================================================
7. PROFILE CREATION → GRADE
==================================================

Khi tạo Learner Profile:

Tên
Lớp

Ví dụ:

Na
Lớp 6

Sau khi chọn Grade,
hệ thống phải resolve được:

AVAILABLE SUBJECTS
AVAILABLE TEXTBOOKS

từ corpus/catalog hiện có.

Không hardcode một danh sách giả
nếu catalog thật đã tồn tại.

==================================================
8. AUTO-GENERATE TIMETABLE
==================================================

Thêm capability:

"Tạo thời khóa biểu cho con"

Khi tạo profile,
cho phép:

[A] Tạo tự động
[B] Tự sắp xếp / chỉnh sau
[C] Bỏ qua

AUTO GENERATION phải dựa trên:

Grade
Subject catalog
Textbook catalog

nhưng KHÔNG random trực tiếp theo số file PDF/book.

Cần normalize:

BOOK
→ SUBJECT

Ví dụ một subject có thể có:

SGK
SBT
Tập 1
Tập 2
SGV

Không được biến chúng thành nhiều môn.

==================================================
9. RANDOM ≠ CHAOTIC
==================================================

Founder muốn có khả năng random timetable
theo các môn/sách có trong từng lớp.

Implement theo hướng:

CONSTRAINED RANDOM GENERATOR.

Input:

LearnerProfile.grade
availableSubjectsForGrade
daysPerWeek
slotsPerDay
optional subject frequency rules
randomSeed

Output:

Timetable.

Random phải reproducible bằng seed
để test được.

Ví dụ:

generateTimetable(
 grade: 6,
 seed: 12345
)

luôn tạo cùng một timetable.

==================================================
10. SUBJECT FREQUENCY
==================================================

Không tự tuyên bố đây là
"thời khóa biểu chuẩn Bộ GDĐT"
nếu chưa có nguồn/rule chính thức.

V1 có thể ghi rõ:

"Thời khóa biểu gợi ý"

Nếu chưa có curriculum frequency truth,
dùng bounded heuristic.

Ví dụ:

core/high-frequency subjects
có thể xuất hiện nhiều hơn,
nhưng phải document heuristic.

Research xem repo/corpus/metadata hiện tại
có dữ liệu curriculum frequency thật không.

Nếu có:
ưu tiên dữ liệu thật.

Nếu không:
giữ GENERATED / SUGGESTED.

==================================================
11. USER CAN EDIT
==================================================

Generated timetable không phải truth bất biến.

Cho phép:

đổi môn
đổi tiết
đổi ngày
regenerate
reset.

Edit thuộc LearnerProfile.

Không ảnh hưởng profile khác.

==================================================
12. HOME INTEGRATION
==================================================

Kết hợp với yêu cầu Multi-subject Home.

Home không chỉ lấy:

recent lesson.

Home candidate context phải có:

TODAY TIMETABLE
+
RECENT LEARNING
+
STUDENT STATE
+
AVAILABLE LESSONS.

Ví dụ:

HÔM NAY
Thứ Hai · 4 môn

[ KHTN 6 ]
Bài 17
Đang học
→ Học với SAM

[ Toán 6 ]
Hôm nay có Toán
→ Mở môn

[ Tiếng Việt 6 ]
Hôm nay có Tiếng Việt
→ Mở môn

horizontal Smart Cards.

==================================================
13. ONE NEXT ACTION
==================================================

Timetable có thể tạo nhiều candidate.

Nhưng SAM vẫn chỉ đưa:

ONE PRIMARY NEXT ACTION.

Ví dụ:

SAM GỢI Ý

Tiếp tục KHTN 6 · Bài 17
→ Học với SAM

Phải ghi được reason/source của recommendation.

Không fake personalization.

==================================================
14. NO FAKE PROGRESS
==================================================

Đặc biệt khi thêm Profile + Timetable:

TIMETABLE ENTRY != LEARNING SESSION

OPENED != UNDERSTOOD

VIEWED != MASTERED

TAP != COMPETENCE

PROFILE AGE/GRADE != KNOWLEDGE STATE

Generated timetable không tạo Evidence.

==================================================
15. DEVICE ACCEPTANCE TEST
==================================================

Trên máy thật tạo:

Na — Lớp 6
Minh — Lớp 5

Generate timetable riêng cho cả hai.

Expected:

Grade khác.
Subject/book set khác.
Timetable khác.
Home cards khác.
History khác.
Progress khác.
Next Action khác.

Cho Na học/mở một lesson.

Switch Minh.

Không được leak state.

Switch lại Na.

State phải còn.

Restart app.

Kiểm tra lại.

==================================================
16. DELIVERABLE
==================================================

Báo Founder:

A. PROFILE ISOLATION AUDIT
PASS / PARTIAL / FAIL

B. bảng ownership hiện tại:
Grade
Books
Subjects
Timetable
History
Progress
Student State
Evidence
Next Action

thuộc Account / Profile / Global ở đâu.

C. hardcoded learner/grade findings.

D. Timetable architecture hiện tại:
EXISTS / PARTIAL / MISSING.

E. concept timetable cũ tìm thấy trong repo.

F. Grade → Subject → Book resolution.

G. constrained random timetable POC.

H. Multi-profile device test.

I. Multi-subject Home + timetable integration.

J. BEFORE / AFTER screenshots.

K. Founder Acceptance Card.

==================================================
17. GOVERNANCE
==================================================

Autonomous reversible work allowed.

DO NOT:

lower trust thresholds
fake evidence
mass reprocess corpus
make licensing decisions
claim generated timetable is official curriculum
perform destructive migration
merge without Founder approval.

STOP:

READY FOR FOUNDER REVIEW.

DO NOT MERGE.