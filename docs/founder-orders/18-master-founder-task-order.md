# MASTER FOUNDER TASK ORDER
## HỌC CÙNG SAM — AUTONOMOUS P0 → P1 EXECUTION

MODE:
FULL AUTONOMOUS EXECUTION

ROLE:
Claude = Supervisor / Technical Product Executor của workstream Học cùng SAM.

Không cần Founder duyệt từng ticket, từng PR hoặc từng quyết định kỹ thuật thông thường.

Tự động chạy:

AUDIT
→ CHALLENGE
→ JIRA
→ DEPENDENCY
→ IMPLEMENT
→ TEST
→ EVIDENCE
→ REAL DEVICE khi cần
→ PR
→ CI
→ MERGE
→ NEXT READY TASK

Không dừng sau mỗi bước để báo cáo.

Chỉ báo Founder khi:
- hoàn thành milestone có ý nghĩa;
- architecture hypothesis bị falsify;
- có Product fork mà evidence không phân xử được;
- legal/licensing/commercial blocker;
- significant spending;
- destructive/shared-data operation;
- public release/store submission;
- hoặc cần Founder UX test thực tế.

==================================================
0. PRODUCT TRUTH — KHÔNG ĐƯỢC LÀM LỆCH
==================================================

Học cùng SAM không phải chatbot giải bài.

Mental model:

Learner Profile / Grade
→ Bookshelf
→ Book
→ Chapter
→ Lesson
→ Learning State
→ Learning Intent
→ Learning Experience with SAM
→ Learning Tool
→ LearnerAction
→ CandidateEvidence
→ Evidence Validator
→ Student State
→ Learning Map / Parent / Home / Review
→ Next Best Learning Action.

Core principles:

SGK = LEARNING MAP.

SAM = LEARNING COMPANION.

PEDAGOGY decides what should happen.

PlannedAct expresses the permitted pedagogical action.

SAM realizes that action naturally.

LEARNING TOOLS are where the child does the work.

EVIDENCE decides what the product may claim.

GAMIFICATION presents real progress.

COVERAGE != MASTERY.

TRACE != EVIDENCE.

ASSISTED != INDEPENDENT.

UNKNOWN STAYS UNKNOWN.

CONTEXT != PROMPT.

ONE EVIDENCE TRUTH
→ MULTIPLE AUTHORIZED PROJECTIONS:
Child / Parent / Home / Review / Learning Map.

Không:
- generic chatbot;
- God Agent;
- per-lesson Dart;
- per-screen/per-subject prompt builder;
- fake mastery %;
- fake stars;
- XP/streak/leaderboard;
- sibling ranking;
- parallel Parent scoring system;
- invented curriculum truth.

==================================================
1. ACCEPT CURRENT AUDIT RESULT
==================================================

Founder ACCEPT kết luận:

B — PARTIALLY SUPPORTED / DISCONNECTED

Canonical LearningContext hiện CHƯA tồn tại.

Repo hiện có các primitive riêng:

- LearnerProfile
- LessonKey / curriculumForLesson
- LearningIntent / proposeIntent
- TeachingProvenance / explainTeaching
- AssistancePolicy
- TutorScope
- TeachingAct / PlannedAct
- realization_contract.dart
- LearningAgenda
- WAL-179 lineage work

nhưng chưa có runtime abstraction compose chúng thành một
canonical LearningContext.

Hiện navigation chủ yếu truyền context thủ công qua constructors.

PlannedAct/Pedagogy/resolveSurface chưa được nối vào feature runtime.

SAM copy hiện chủ yếu hardcoded trong widget.

Camera hiện không có Subject/Lesson/Intent context inheritance.

Không tranh luận lại audit này trừ khi code mới đã thay đổi evidence.

==================================================
2. P0-A — CANONICAL HIERARCHICAL LEARNING CONTEXT
==================================================

Audit Jira trước.

Nếu đã có ticket đúng capability:
→ re-scope/reuse.

Nếu chưa có:
→ tạo một WAL capability ticket phù hợp.

Không duplicate.

Tên candidate:

Hierarchical Learning Context & Context Slicing

nhưng được quyền dùng tên khác nếu phù hợp architecture repo hơn.

--------------------------------------------------
GOAL
--------------------------------------------------

ONE SAM.
ONE CANONICAL LEARNING CONTEXT.

SAM phải biết mình đang đứng ở đâu trong learning journey.

Context enrich theo:

GLOBAL
Learner
Grade
Age/Presentation Policy
high-level state

        ↓

SUBJECT
+ Subject

        ↓

BOOK
+ sourceDocumentId
+ Book/version/provenance

        ↓

LESSON
+ Chapter/ContentNode
+ Lesson
+ LearningIntent
+ relevant curriculum/pedagogical context

        ↓

ACTIVITY
+ Activity / Problem

        ↓

TURN
+ PlannedAct
+ Assistance
+ recent LearnerAction
+ relevant Evidence.

Không phải mọi field đều required.

Unknown context phải giữ UNKNOWN/null.

Không suy đoán chỉ để fill object.

--------------------------------------------------
ENTRY POINT BEHAVIOR
--------------------------------------------------

SAM FROM HOME:

biết:
Learner + Grade + high-level state.

Không tự invent Subject/Book/Lesson.

SAM FROM SUBJECT:

inherit Global
+ Subject.

SAM FROM BOOK:

inherit
+ Book/sourceDocumentId.

SAM FROM LESSON:

inherit
+ Chapter/Lesson
+ Intent
+ relevant knowledge/provenance.

SAM FROM ACTIVITY:

inherit
+ Activity/Problem
+ PlannedAct/assistance khi có.

--------------------------------------------------
CAMERA
--------------------------------------------------

Camera từ Home:

Learner + Grade
Subject = unknown
Lesson = unknown

→ perception/classification
→ learner confirmation
→ mới bind thêm context.

Camera từ:

Toán 5
→ Book
→ Bài 6
→ Homework
→ Camera

phải có khả năng inherit known:

Learner
Subject
Book
Lesson
Intent.

UNCONFIRMED MACHINE PERCEPTION
MUST NOT ENTER LEARNING EVIDENCE.

Context inheritance không được biến thành inference authority.

--------------------------------------------------
IMPLEMENTATION CONSTRAINT
--------------------------------------------------

Ưu tiên:

small
immutable
composable
testable

LearningContext.

Không tạo giant Context Engine.

Không dùng ambient global mutable context nếu có thể tránh.

Không tạo:

HomePromptBuilder
MathPromptBuilder
SciencePromptBuilder
LessonPromptBuilder
CameraPromptBuilder.

==================================================
3. P0-B — CONTEXT AVAILABLE != CONTEXT INJECTED
==================================================

Đây là invariant.

LearningContext là runtime truth.

Nó KHÔNG phải toàn bộ LLM prompt.

Model:

Full LearningContext
        ↓
Context Builder
        ↓
Pedagogy / Current Purpose
        ↓
PlannedAct
        ↓
Context Slicing
        ↓
Relevant Context Slice
        ↓
Realization
        ↓
LLM only if useful.

Ví dụ:

“Con thử làm trước nhé.”

có thể deterministic/template/TTS.

Không cần LLM.

Nếu giải thích concept:

inject only:
- grade;
- lesson;
- relevant source evidence;
- permitted method;
- assistance ceiling;
- required recent context.

Nếu trẻ hỏi:

“Tại sao cách này khác hôm qua?”

mới retrieve relevant historical evidence/session.

Không serialize:
- full Student State;
- full book;
- full SGK;
- full history;
- unrelated evidence

vào mọi call.

Nếu hiện tại chưa có LLM runtime:
đừng build một LLM stack chỉ để chứng minh Context Slicing.

Hãy chứng minh contract bằng deterministic realization/test trước.

==================================================
4. P0-C — WAL-179 CANONICAL LINEAGE
==================================================

Giữ separation:

LearningContext
= READ/RUNTIME PATH
“SAM biết gì ngay bây giờ?”

WAL-179
= IDENTITY/WRITE PATH
“Event/Evidence này thuộc learning context nào?”

Không gộp responsibility.

Nhưng hai abstraction phải tương thích.

Tìm minimum stable lineage dùng chung cho:

- Learning Context;
- Learning Event;
- Evidence;
- Session Replay;
- Learning Map;
- Parent View;
- Citation;
- Next Action;
- future Class Materials.

Candidate:

learnerId
subjectId
sourceDocumentId?
contentNodeId / lesson identity?
activityId?
skillCaseId?
conceptId?
sessionId
intent
plannedAct / assistance
learnerAction
evidence.

Đây là hypothesis, không bắt buộc schema literal này.

Không thêm arbitrary `lessonId` chỉ để làm stars.

==================================================
5. P0-D — WAL-178 TOOL CONTRACT + EVIDENCE VALIDATOR
==================================================

Tiếp tục WAL-178.

Target architecture:

LearningContext
+ Curriculum/State/Intent/Safety
        ↓
Pedagogy Policy
        ↓
PlannedAct
{
 TeachingAct
 AssistanceCeiling
 Provenance
 Intent
 Why
}
        ↓
Realization Policy
        ↓
silence / template / text / TTS / guarded LLM
        ↓
Learning Tool
        ↓
LearnerAction
+ Trace
+ CandidateEvidence
+ Completion
        ↓
Evidence Validator
        ↓
ValidatedLearningEvidence
        ↓
Student State.

TeachingAct là VALUE.

Không biến TeachingAct thành autonomous agent.

Learning Tool không được tự quyết pedagogy.

Tool không được mint authoritative LearningEvent/Evidence trực tiếp.

Tool trả về learner action/candidate evidence.

Evidence Validator là gate duy nhất quyết định cái gì được coi là
validated learning evidence.

--------------------------------------------------
POC
--------------------------------------------------

Dùng Khoa học 5 Bài 1 nếu vẫn là falsification probe tốt nhất.

Không force `duDoan` vì source thực tế không có.

SOURCE TRUTH > DESIRED UX.

Thà SAM im còn hơn bịa pedagogy/content.

Mục tiêu không phải polish Bài 1.

Mục tiêu là chứng minh reusable contract.

==================================================
6. P0-E — SAM REALIZATION
==================================================

SAM không phải generic chatbot.

SAM không quyết định:
- curriculum;
- method;
- target;
- assistance ceiling;
- evidence;
- mastery.

Pedagogy Runtime quyết định.

SAM realization có thể:
- silence;
- deterministic text;
- mascot reaction;
- TTS;
- question;
- hint;
- guarded LLM realization;
- open/return Learning Tool.

8/15 TeachingActs hiện có thể deterministic/template:
reuse evidence này.

Không bắt buộc LLM.

Không chuyển hardcoded Vietnamese prose từ Widget sang một giant map
rồi tuyên bố architecture solved.

Nếu tạo act catalogue:
phải subject/lesson-agnostic ở mức hợp lý và gắn với TeachingAct.

==================================================
7. P0 ACCEPTANCE / FALSIFICATION
==================================================

P0 không PASS chỉ vì:

- có class LearningContext;
- tests xanh;
- có JSON;
- có interface.

Phải chứng minh vertical runtime path thật:

Home
→ Subject/Book
→ Lesson
→ Activity
→ LearningContext enrich/preserve
→ Intent
→ Pedagogy
→ PlannedAct
→ Learning Tool
→ LearnerAction
→ CandidateEvidence
→ Evidence Validator
→ canonical lineage
→ persisted state/event.

Phải chứng minh:

1. learner identity không mất;
2. known context được inherit;
3. unknown không bị invent;
4. screen không tự build pedagogy prompt;
5. context survives navigation;
6. PlannedAct consume đúng context;
7. Tool không tự mint evidence truth;
8. Validator quyết định evidence;
9. same lineage có thể đọc lại;
10. architecture không lesson-specific.

Nokia real-device verify nếu runtime/UI path liên quan.

Nếu P0 fail:
→ không che failure;
→ Jira;
→ fix hypothesis/architecture;
→ retest.

==================================================
8. P1-A — WAL-181 LEARNING MAP
==================================================

Chỉ chạy khi P0 đủ evidence.

Bookshelf/Book/Chapter/Lesson phải trở thành Learning Map,
không chỉ content browser.

Nhưng:

COVERAGE != MASTERY.

Không fake %.

Không force stars từ dữ liệu không đủ.

Truth layer candidate:

UNSEEN
ENGAGED
INDEPENDENT_EVIDENCE
REVIEW_DUE
INSUFFICIENT_EVIDENCE

Đây là hypothesis; challenge bằng existing model.

Child-facing projection có thể:
- light-up;
- subtle badge;
- star;
- SAM reaction;
- gentle completion.

Visual projection != semantic truth.

Nếu stars gây hiểu nhầm:
được quyền đổi representation.

Unlearned lesson:
KHÔNG LOCK.

Learning Map phải degrade gracefully cho lessons chưa có SkillCase model.

==================================================
9. P1-B — WAL-180 PARENT SESSION SUMMARY
==================================================

Parent không cần:

“Con hiểu 82%.”

Parent cần narrative grounded in same evidence:

- con học gì;
- tự làm được gì;
- cần SAM giúp ở đâu;
- hỗ trợ có giảm không;
- phần nào cần ôn;
- phần nào chưa đủ evidence.

Ví dụ:

“Tuần này con học thêm 3 bài.
Bài 2 con tự hoàn thành.
Bài 3 cần SAM gợi ý một lần.
Bài 1 đang đến lúc nên ôn lại.”

Parent View phải đọc CÙNG event/evidence truth với Child Learning Map.

Không tạo parallel Parent scoring system.

Falsification #2:

ONE EVIDENCE TRUTH
→ CHILD PROJECTION
→ PARENT PROJECTION.

Nếu cần hai hệ tính truth khác nhau:
architecture hypothesis FAIL.

==================================================
10. LESSON LEARNING WORKSPACE
==================================================

Giữ Product Direction:

Lesson không nên là static lesson screen chứa nhiều paragraph/question
hardcode.

Lesson là Learning Workspace / Learning Experience with SAM.

Natural actions có thể gồm:

- Học trước
- Làm bài tập
- Ôn lại
- Tra cứu
- Tóm tắt
- Kiểm tra nhanh

Không assume cả 6 là LearningIntent.

Current likely separation:

LearningIntent:
- prepare
- homework/practice
- review
- lookup

Summary:
utility/representation.

Quick Check:
assessment/action/policy.

Challenge bằng code trước khi mở rộng enum.

Không tạo fake choice.

Same Lesson + Different Intent
→ may produce Different Learning Experience.

==================================================
11. LEARNING TOOL UX
==================================================

Không lock Tool presentation quá sớm.

Evaluate as needed:

A. Inline in conversation
B. Full-screen
C. Hybrid

Current Founder hypothesis:
HYBRID có khả năng tốt:

SAM/lesson workspace
→ tool preview/action
→ full-screen specialized Tool khi cần
→ return result/context to SAM.

Nhưng không refactor toàn bộ UI chỉ để chứng minh hypothesis.

Specialized tools vẫn first-class:

Math Workspace
Experiment
Essay
Timeline
Map
Graph
Diagram
Quiz
Camera
Simulation
Reader.

Conversation không được biến tất cả thành text chat.

==================================================
12. TEXTBOOK CITATION / SOURCE VIEW
==================================================

Preserve direction:

📖 Theo sách
≠
✨ SAM giải thích.

SAM/source output phải có provenance.

Citation có thể sau này mở:

source chip
→ exact page/context bottom sheet
→ optional full-page textbook/source viewer.

Current SourceAsset bbox/crop có thể chưa đủ.

Research PageAsset/SourcePage/DocumentPage abstraction nếu cần.

Không build full viewer trong P0/P1 trừ khi dependency thật sự bắt buộc.

WAL-171 hiện DEFER nếu vẫn đúng.

Copyright/commercial distribution vẫn là separate gate.

==================================================
13. PERSONAL CLASS CONTEXT — PRESERVE FOR FUTURE
==================================================

Không cần kéo P2 vào P0.

Nhưng P0 architecture KHÔNG được khóa đường cho capability này.

Future per Learner + Subject:

📘 Official Books
🗺 Learning Map
📂 Tài liệu lớp của con
   📝 Tests
   📄 Worksheets
   👩‍🏫 Teacher materials
   📷 Notebook/class scans
   Assignment/revision materials.

Potential pipeline:

Capture/Import
→ OCR/Document Understanding
→ Classification
→ Learner/Parent Confirmation
→ Subject/Book/Lesson mapping
→ Personal Class Library/Class Context.

Keep three truths separate:

OFFICIAL CURRICULUM
= SGK/SGV/program truth.

TEACHER/CLASS CONTEXT
= what this particular class is doing.

LEARNER WORK
= what the child actually attempted/performed.

Do not collapse them.

Uploaded document != Evidence.

Scanned test != Evidence.

Only learner performance through validation may become Learning Evidence.

WAL-146 remains DEFER unless dependency analysis proves otherwise.

==================================================
14. CAMERA FUTURE COMPATIBILITY
==================================================

Camera is a capability, not isolated feature.

Eventually:

Camera(Home)
→ minimal context.

Camera(Lesson)
→ inherited lesson context.

Camera(Homework)
→ inherited intent/context.

Camera imported test/worksheet
→ class-document context.

Do not implement every entry point now.

But canonical context contract must not prevent them.

==================================================
15. HUB REUSE
==================================================

When relevant, audit Workizen AI Personal Hub reuse:

- Camera/Scan
- OCR
- Document Intelligence
- Library
- local storage
- sync
- QR
- device discovery
- TTS/STT
- notifications
- provider abstraction
- document viewer.

Classify only when needed:

REUSE AS-IS
REUSE WITH ADAPTATION
EXTRACT SHARED
NOT SUITABLE.

Do not duplicate infrastructure unnecessarily.

==================================================
16. JIRA OPERATING RULES
==================================================

Jira = control plane.

Before creating:
→ search existing WAL tickets.

Prefer:
REUSE
→ RE-SCOPE
→ COMMENT/DEPENDENCY
before NEW.

Tickets capability-oriented.

Không tạo hàng loạt ticket theo:
Bài 1
Bài 2
Bài 3
...

Gold lesson/probe ticket chỉ khi dùng để falsify architecture.

Keep tickets medium-sized.

Mỗi ticket phải có:
- goal;
- architecture claim;
- dependencies;
- acceptance criteria;
- evidence required;
- explicit non-goals.

Nếu research đã falsify hypothesis:
không giữ ticket như implementation backlog chỉ vì nó từng được tạo.

==================================================
17. AUTONOMOUS PRIORITY
==================================================

Current expected order:

P0:
A. Hierarchical Learning Context / Context Builder
B. WAL-179 Canonical Lineage
C. WAL-178 Tool Contract + Evidence Validator

Claude được quyền reorder A/B/C nếu dependency evidence cho thấy thứ tự khác tốt hơn.

Có thể làm chung bounded branch/slice nếu coupling cao,
nhưng Jira responsibility vẫn phải rõ.

Sau P0:

P1:
D. WAL-181 Learning Map projection
E. WAL-180 Parent Session Summary.

Falsification:

#1
Runtime truth:
Context → Act → Tool → Evidence → Lineage.

#2
Projection truth:
Same Evidence → Child + Parent.

P2 giữ deferred:
- Personal Class Library
- Scan/OCR Class Context
- Full-page Textbook Viewer
- broader content expansion/research.

==================================================
18. CONTENT SCALING RULE
==================================================

Không giải quyết scale bằng per-lesson code.

Target:

8,000+ lessons
!=
8,000 Dart flows
!=
8,000 prompts.

Runtime code phải scale theo:

Context
Pedagogy
TeachingAct
Learning Tool
Evidence Contract
Experience Pattern/Blueprint where proven.

Lesson-specific truth thuộc:
data/content/provenance/config,
không phải handwritten product architecture.

Không build giant Content-Pedagogy Compiler chỉ vì vision.

Compiler chỉ được nâng priority khi runtime evidence chứng minh đó là
bottleneck tiếp theo.

==================================================
19. REAL DEVICE / EVIDENCE
==================================================

Không tin DONE chỉ từ report.

Evidence hierarchy:

CODE
→ TEST
→ RUNTIME
→ REAL DEVICE
→ REPLAY/STATE
→ USER-VISIBLE BEHAVIOR.

Dùng Nokia khi cần chứng minh:
- navigation;
- context preservation;
- child UX;
- TTS;
- interaction flow;
- state refresh.

Không bắt device test cho pure data utility nếu unit/integration evidence đủ.

Founder Acceptance Card cho milestone quan trọng:

Ticket(s)
Goal
Claims proven
Evidence
Runtime/device path
Falsified assumptions
Unproven items
PASS / PARTIAL / FAIL.

==================================================
20. AUTONOMOUS LOOP
==================================================

Sau mỗi ticket/slice:

IF PASS:
→ merge
→ Jira evidence
→ select highest-value dependency-ready task
→ continue automatically.

IF PARTIAL:
→ identify missing evidence
→ fix/re-scope
→ retest
→ continue.

IF FAIL:
→ record falsification
→ challenge architecture
→ update Jira
→ choose smallest corrective experiment
→ continue.

Không dừng vì:
- cần chọn class name;
- cần chọn internal abstraction;
- cần re-scope ticket;
- cần fix bug;
- cần thêm test;
- cần đổi dependency;
- hypothesis Founder bị code evidence bác.

Claude có quyền tự quyết các việc trên.

==================================================
21. GIT / CI
==================================================

Tuân thủ repo governance hiện tại.

Không direct-push main nếu branch protection yêu cầu PR.

Normal loop:

branch
→ implement
→ analyze/test
→ evidence
→ PR
→ CI
→ merge
→ clean state
→ next.

Không force-push/delete shared history.

Không dùng local build artifact để che missing tracked asset/dependency.

==================================================
22. STOP CONDITIONS
==================================================

Chỉ STOP và hỏi Founder khi:

1. branding/product positioning irreversible;
2. commercial copyright/licensing commitment;
3. significant spend;
4. destructive shared/prod/data operation;
5. public release/store submission;
6. irreversible migration/data compatibility risk;
7. two legitimate product directions remain and evidence cannot decide;
8. cần Founder đánh giá subjective UX trên máy thật.

Technical choices bình thường:
TỰ QUYẾT.

Nếu blocker có workaround reversible:
dùng workaround và tiếp tục.

==================================================
23. REPORTING
==================================================

Không gửi Founder report sau từng ticket.

Chỉ gửi milestone report ngắn:

DONE
- ...

EVIDENCE
- ...

FALSIFIED
- ...

PRODUCT VISIBLE NOW
- ...

NEXT
- ...

BLOCKED
- only if real stop condition.

Technical details đầy đủ để trong:
Git / Jira / evidence artifacts.

==================================================
24. START NOW
==================================================

Bắt đầu thực thi ngay.

First action:

1. Audit Jira cho Hierarchical Learning Context.
2. Create/re-scope ticket nếu cần.
3. Re-evaluate dependency WAL-178/WAL-179.
4. Chọn smallest P0 vertical falsification.
5. Implement.
6. Test.
7. Evidence.
8. Nokia verify nếu cần.
9. PR/CI/merge.
10. Continue autonomously.

Không quay lại Founder để xin duyệt thứ tự kỹ thuật.

Target milestone đầu tiên:

PROVE:

Home/Book/Lesson/Activity context
→ canonical LearningContext
→ PlannedAct
→ existing Learning Tool
→ LearnerAction
→ CandidateEvidence
→ Evidence Validator
→ canonical lineage

mà không:
- invent unknown context;
- per-screen prompt;
- per-lesson hardcode;
- fake evidence.

Sau khi PASS:
tự chuyển sang Learning Map + Parent Summary.

EXECUTE NOW.
