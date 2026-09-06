FOUNDER DECISION — CONSENSUS ACCEPTED, PREPARE EXECUTION PLAN ONLY

Tôi đã review `SAM-PRODUCT-CONSENSUS-REPO-REVIEW.md`.

Consensus hiện tại được chấp nhận làm baseline cho vòng tiếp theo.

Đặc biệt chấp nhận ba correction:

1. Assessment không bị giới hạn là end-of-Review.
   Existing context-dependent claim behavior là hướng đúng.
   Assessment introduction theo claim vẫn UNPROVEN — chưa làm.

2. Home đã có recommendation thật.
   Vấn đề chính là context/intent bị đứt SAU recommendation:
   `resolveAgenda → Home → Start → generic Bookshelf`.

3. Core có nhiều primitive đúng riêng lẻ,
   nhưng CHƯA chứng minh chúng hội tụ thành một complete Learning Experience.

Không cần thêm vòng tranh luận product model lúc này.

NHƯNG CHƯA CODE.

==================================================
1. RECONCILE EXECUTION PLAN WITH CURRENT JIRA
==================================================

Đọc toàn bộ WAL liên quan tới journey này.

Đối chiếu với consensus vừa được chấp nhận.

Đặc biệt kiểm tra:

- WAL-138
- WAL-143
- WAL-166
- WAL-167
- WAL-168
- WAL-170
- WAL-172
- WAL-173
- WAL-175

và các ticket liên quan:

Home
Agenda
Bookshelf
Book
Lesson
Activity
Intent
Experience
SAM
Evidence
Review
Assessment
Camera
Next Best Action.

CHƯA sửa Jira.

Chỉ đề xuất:

KEEP
RE-SCOPE
SUPERSEDED
DONE-BUT-PRODUCT-REVIEW
DEFER.

==================================================
2. FIND THE SHORTEST PATH TO A COMPLETE LOOP
==================================================

Không hỏi:

“Ticket Ready tiếp theo là gì?”

Hỏi:

“Khoảng cách ngắn nhất từ CURRENT APP
đến một COMPLETE LEARNING LOOP là gì?”

Target capability:

REAL CHILD SITUATION
→ CONTEXT
→ SAM RECOMMENDATION + REASON
→ START
→ CONTEXT SURVIVES NAVIGATION
→ LESSON/ACTIVITY
→ LEARNING INTENT
→ APPROPRIATE EXPERIENCE
→ SAM INTERACTION
→ CHILD ACTION
→ TRACE / EVIDENCE
→ SUMMARY
→ CONTINUITY / NEXT ACTION.

Không mặc định phải implement toàn bộ chain trong một ticket.

Hãy xác định những đoạn:

ALREADY WORKING

DISCONNECTED

MISSING.

==================================================
3. WAL-175
==================================================

WAL-175 đã code trước consensus nhưng chưa PR/merge/device verify.

Đừng tự động bỏ hoặc tiếp tục chỉ vì đã làm.

Audit nó với consensus mới:

- phần nào đúng;
- phần nào ad hoc;
- phần nào reusable;
- có tạo assumption sai không;
- có nên KEEP / MODIFY / SPLIT / ABANDON.

Đặc biệt:
`activitiesForIntent` hiện chưa được coi là
Experience Pattern architecture.

Đừng biến implementation đầu tiên thành abstraction
chỉ vì nó đã tồn tại.

==================================================
4. EXPERIENCE — DO NOT PREMATURELY BUILD AN ENGINE
==================================================

Repo hiện chưa có Experience Pattern thực sự.

Không mặc định solution tiếp theo là:

“build ExperiencePattern engine”.

Trước tiên xác định bằng golden learning experience thật:

WHAT varies by Intent?

WHAT varies by Activity?

WHAT varies by Subject?

WHAT is shared?

WHAT does SAM actually do?

Sau đó mới biết abstraction nào đáng tồn tại.

==================================================
5. SAM
==================================================

SAM presence hiện chưa có model/code chủ đích.

Đừng bắt đầu bằng `SamPresenceEngine`.

Đề xuất trước PRODUCT BEHAVIOR trong một real journey:

- SAM xuất hiện lúc nào;
- nói gì;
- dựa vào evidence/context nào;
- khi nào im lặng;
- khi nào hint;
- khi nào step back;
- khi nào summarize;
- cái gì được nhớ cho lần sau.

Sau khi có behavior thật mới quyết định code shape.

==================================================
6. GOLDEN JOURNEY
==================================================

Đề xuất ONE golden journey lớp 5 tốt nhất để falsify hệ thống.

Không cần cover toàn app.

Journey phải đủ để chứng minh:

CONTEXT
→ INTENT
→ EXPERIENCE
→ SAM
→ CHILD ACTION
→ EVIDENCE/TRACE
→ CONTINUITY.

Ưu tiên dữ liệu SGK thật.

Cho biết:

- chọn book nào;
- lesson/activity nào;
- intent nào;
- vì sao case này tốt;
- concepts nào trong 38 được reuse;
- existing core nào được dùng;
- missing pieces nào phải nối.

Sau đó đề xuất SECOND PROBE rất nhỏ
để chứng minh journey đầu không phải hardcode.

Có thể khác:
subject,
intent,
activity type,
hoặc entry path.

Không implement.

==================================================
7. BOOK vs CAMERA
==================================================

Không cần giải quyết Book-first vs Camera-first.

Giữ đây là TESTABLE HYPOTHESIS.

Golden journey có thể chọn một entry để kiểm chứng,
nhưng không được biến lựa chọn đó thành canonical IA.

==================================================
8. OUTPUT
==================================================

Viết một execution proposal ngắn ra Desktop:

`SAM-NEXT-EXECUTION-PROPOSAL.md`

Nội dung:

# Current Loop Reality

# Jira Reconciliation Proposal

# WAL-175 Decision

# Golden Journey Proposal

# Second Reuse Probe

# Existing Core To Reuse

# Missing Connections

# SAM Behavior In This Journey

# 38 Concepts Reused

# What NOT To Build Yet

# Proposed Jira Delta

# Recommended Execution Order

# Founder Decisions Needed

Không sửa Jira.
Không code.
Không merge WAL-175.
Không mở rộng architecture.

Xong file thì STOP.

Founder sẽ review proposal trước khi cấp quyền execution.
