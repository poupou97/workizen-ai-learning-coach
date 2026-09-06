# FOUNDER MASTER TASK ORDER
# HỌC CÙNG SAM
## POST-INGESTION K–12 CURRICULUM-GROUNDED UX / 38 CONCEPT / SUBJECT / HUB REUSE AUDIT

STATUS:
QUEUED — EXECUTE AUTOMATICALLY AFTER FULL K–12 INGESTION COMPLETES

PRIORITY:
P0 RESEARCH / PRODUCT / UX ARCHITECTURE GATE

==================================================
0. FOUNDER INTENT
==================================================

Founder đã có:

- corpus SGK K–12 đang OCR/ingestion;
- 38 AI-first concept screens của Học cùng SAM trong repo;
- Curriculum/Content/Student Knowledge architecture;
- TutorScope / Method / SkillCase / TeachingAct / LearningEvidence;
- AI Curriculum research;
- nhiều capability đã có từ Workizen AI Personal Hub;
- yêu cầu Shared Device / Multi-profile cho gia đình.

KHÔNG muốn production UI tiếp tục được thiết kế chủ yếu bằng:
- trực giác;
- generic EdTech patterns;
- ChatGPT-like UX;
- hình concept đẹp;
- assumption về cách từng môn được học.

Founder muốn:

    CORPUS SGK THẬT
        ↓
    K–12 LEARNING STRUCTURE
        ↓
    SUBJECT / ACTIVITY SEMANTICS
        ↓
    PEDAGOGICAL INTERACTION
        ↓
    UX SURFACES / FLOW
        ↓
    PRODUCTION UI.

Nhiệm vụ này phải dùng toàn bộ dữ liệu K–12 ingest được
để quay lại PHẢN BIỆN 38 concept screens.

38 concept screens là:

    DESIGN INTENT / VISUAL REFERENCE BASELINE

KHÔNG phải:

    PRODUCTION SPEC.

==================================================
1. EXECUTION GATE — KHÔNG CHẠY TRƯỚC KHI INGESTION XONG
==================================================

Task này được giao NGAY BÂY GIỜ nhưng chưa chạy phần audit chính.

Tiếp tục current K–12 OCR / ingestion cho đến khi hoàn thành
toàn bộ corpus hiện tại.

KHÔNG interrupt ingestion để chạy task này giữa chừng.

Chỉ bắt đầu audit khi đạt final ingestion checkpoint.

Final checkpoint phải có ít nhất:

- processed books / total books;
- SUCCESS;
- PARTIAL;
- FAILED;
- Grade 1–12 coverage;
- subject coverage;
- SourceDocument count;
- lesson count;
- section count;
- ContentUnit count;
- exercise/activity count nếu đã extract;
- semantic type distribution;
- explicit / demonstrated / inferred distribution nếu có;
- OCR failures;
- layout failures;
- unknown/unmapped;
- structural coverage;
- semantic coverage;
- ingestion version / commit / snapshot identifier.

CRITICAL:

    100% FILES PROCESSED
    !=
    100% CURRICULUM UNDERSTOOD.

Phải báo riêng:

STRUCTURAL COVERAGE

và:

SEMANTIC COVERAGE.

Nếu có failed/partial books:

KHÔNG được fake 100%.

Ghi rõ phần nào không đủ bằng chứng.

==================================================
2. LOCK CORPUS SNAPSHOT
==================================================

Ngay sau ingestion hoàn thành:

Lock một reproducible snapshot cho task này.

Ghi:

CORPUS SNAPSHOT
- timestamp;
- ingestion commit/version;
- total books;
- processed;
- success;
- partial;
- failed;
- ContentUnits;
- subjects;
- grades;
- semantic extraction version;
- knowledge model version nếu applicable.

Toàn bộ 5 report sau phải dựa trên snapshot này.

Nếu ingestion tiếp tục được sửa sau đó:
không silently thay đổi evidence của report.

==================================================
3. SOURCE OF TRUTH
==================================================

Thứ tự evidence:

1. Real ingested SGK corpus.
2. Extracted SourceDocument / Lesson / Section / ContentUnit.
3. Exercise / Activity data.
4. Curriculum Graph.
5. Concept / SkillCase / Method.
6. Official curriculum sources hiện có.
7. Official AI curriculum:
   QĐ2422/QĐ-BGDĐT
   CV5588/BGDĐT-GDPT.
8. Existing architecture/ADR.
9. 38 concept screens.
10. Existing research.
11. External research nếu thực sự cần.

Mọi kết luận quan trọng phải distinguish:

SOURCE_EVIDENCE
ARCHITECTURE_EVIDENCE
EXTERNAL_RESEARCH
INFERENCE
HYPOTHESIS
UNKNOWN.

Không biến inference thành curriculum truth.

Không đủ evidence:

    UNKNOWN / INSUFFICIENT DATA.

==================================================
4. CORPUS ANALYSIS — PHẢI LÀM TRƯỚC UX
==================================================

Không mở 38 concept rồi audit ngay.

Trước tiên hãy phân tích corpus.

Tìm actual patterns trong SGK:

- lesson structures;
- section structures;
- instruction patterns;
- examples;
- worked examples;
- exercises;
- questions;
- activities;
- projects;
- experiments;
- reading;
- writing;
- speaking;
- listening;
- observation;
- source analysis;
- map/data work;
- creative/performance;
- reflection;
- assessment.

Thống kê khi data cho phép.

Mục tiêu:

    SGK THỰC SỰ YÊU CẦU HỌC SINH LÀM GÌ?

không phải:

    APP HỌC ONLINE THƯỜNG CÓ GÌ?

==================================================
5. GRADE-BAND ANALYSIS
==================================================

Phân tích ít nhất:

GRADE 1–2
GRADE 3–5
GRADE 6–9
GRADE 10–12.

Với từng band, nghiên cứu từ SGK thật:

- text density;
- instruction length;
- image/illustration dependency;
- reading demand;
- writing demand;
- learner autonomy;
- oral activities;
- interaction complexity;
- exercise complexity;
- assessment patterns;
- abstract reasoning;
- source/data use;
- subject differentiation.

Sau đó derive UX implications.

Ví dụ:

Grade 1–2:
có thực sự cần:
- voice-heavy;
- larger controls;
- more mascot;
- lower text density;
- parent assistance?

Phải evidence-grounded.

Không chỉ dùng generic age assumptions.

==================================================
6. SUBJECT-BY-SUBJECT ANALYSIS
==================================================

Phân tích tất cả subject/content family thực sự có trong corpus.

Ít nhất nếu data support:

- Toán;
- Tiếng Việt;
- Ngữ văn;
- Ngoại ngữ;
- Tự nhiên & Xã hội;
- Khoa học;
- Khoa học tự nhiên;
- Vật lý;
- Hóa học;
- Sinh học;
- Lịch sử;
- Địa lý;
- GDCD / relevant social education;
- Tin học;
- Công nghệ;
- Âm nhạc;
- Mỹ thuật;
- Hoạt động trải nghiệm;
- AI Education;
- subject khác trong actual corpus.

Đặc biệt xử lý đúng curriculum reality:

Ví dụ:
KHTN 6–9 có thể là integrated subject.

Không ép concept Physics/Chemistry standalone
nếu curriculum context hiện tại không như vậy.

Với mỗi subject:

A. Learning goals.

B. Activity patterns.

C. Exercise patterns.

D. Response types.

E. Observable LearningEvidence.

F. Suitable TeachingActs.

G. Suitable interaction surfaces.

H. Age differences.

I. Existing concept fit.

J. Missing UX.

K. Subject adapter requirements.

L. Hub capability reuse opportunities.

==================================================
7. FALSIFY ACTIVITY FAMILY TAXONOMY
==================================================

Dùng corpus để kiểm tra taxonomy hiện tại:

A. Problem Solving

B. Scientific Investigation

C. Reading / Argument / Source Reasoning

D. Spatial / Data Reasoning

E. Language

F. Assessment

G. Creative / Performance.

Không assume taxonomy đúng.

Tìm actual activity patterns như:

- observe;
- identify;
- recall;
- classify;
- compare;
- match;
- order;
- fill;
- calculate;
- derive;
- prove;
- explain;
- discuss;
- debate;
- investigate;
- experiment;
- measure;
- graph;
- map;
- annotate;
- draw;
- design;
- create;
- write;
- revise;
- listen;
- speak;
- read aloud;
- roleplay;
- sing;
- perform;
- present;
- project;
- collaborate;
- reflect.

Minimize/modify taxonomy dựa trên data.

Không biến mọi classroom activity thành app feature.

Ví dụ:

group discussion

có thể được support,
nhưng không nhất thiết cần giả lập nhóm bằng AI.

==================================================
8. RESPONSE TYPE ANALYSIS
==================================================

Falsify/minimize candidate response taxonomy:

MCQ
MULTI_SELECT
MATCHING
ORDERING
FILL_BLANK
SHORT_TEXT
NUMERIC
STEP_SOLUTION
ESSAY
SOURCE_ANALYSIS
MAP_SPATIAL
GRAPH_DATA
EXPERIMENT_REASONING
DRAWING
DIAGRAM
ORAL
LISTENING_RESPONSE
PROJECT
PERFORMANCE
REFLECTION.

Không force taxonomy vào corpus.

Tìm thêm nếu cần.

Đặc biệt kiểm tra:

    SAME CONCEPT
    !=
    SAME EVIDENCE.

Ví dụ một Concept có thể có SkillCase:

recognize
explain
choose
apply
create
revise
transfer.

SAM phải phân biệt learner:

"nhận biết được"

với:

"tự áp dụng được".

==================================================
9. RE-AUDIT 38 AI-FIRST CONCEPT SCREENS
==================================================

Sau khi hoàn thành corpus/subject/activity analysis,
mới quay lại 38 concept screens.

Audit từng screen:

01 Onboarding Welcome
02 Learner Profile
03 Subject Setup
04 Timetable
05 Home
06 Subjects
07 Subject Home
08 Camera
09 Camera Confirm
10 Tutor Start
11 Diagnostic
12 Problem Workspace
13 Hint
14 Your Turn
15 Success
16 Why This Method
17 Source
18 Review
19 Learning Map
20 Quiz
21 Assessment
22 Result
23 Vietnamese
24 Essay
25 Physics
26 Chemistry
27 History
28 Geography
29 AI Learning
30 History Sessions
31 Progress
32 Parent Home
33 Parent Detail
34 Multi-child
35 SAM Voice
36 Library
37 Notifications
38 Settings.

Mỗi screen:

CURRENT INTENT
CORPUS EVIDENCE
LEARNING JOB
GRADE FIT
SUBJECT FIT
ACTIVITY FIT
ROLE
DATA REQUIRED
LEARNING EVIDENCE IMPACT
PROVENANCE REQUIREMENT
HUB REUSE
RISKS

Decision:

KEEP
MODIFY
MERGE
SPLIT
REPLACE
DEFER.

REMOVE chỉ khi có bằng chứng rõ.

Không giữ kết quả audit cũ nếu full corpus falsifies nó.

==================================================
10. SCREEN != SURFACE != STATE
==================================================

Đây là câu hỏi bắt buộc.

38 concept images không có nghĩa production cần 38 routes.

Phân biệt:

SCREEN
SURFACE
STATE
COMPONENT
OVERLAY
DRILL-DOWN.

Ví dụ:

Problem Workspace
Hint
Your Turn
Success

có thể là:

1 Workspace
+ multiple pedagogical states

thay vì 4 route độc lập.

Mục tiêu:

- continuity;
- ít navigation;
- giữ learning context;
- giảm cognitive switching.

Đề xuất final production screen/surface architecture
dựa trên evidence.

==================================================
11. PROPOSE LEARNING INTERACTION SYSTEM
==================================================

Falsify architecture:

SAM LEARNING SHELL
        ↓
LearnerContext
        ↓
CurriculumContext
        ↓
SubjectContext
        ↓
ActivityContext
        ↓
TutorScope
        ↓
Interaction Surface Resolver
        ↓
Learning Surface(s)
        ↓
TeachingAct
        ↓
Learner Response
        ↓
LearningEvidence
        ↓
Student Knowledge State
        ↓
Next Best Learning Action.

Candidate reusable surfaces:

- SAM Conversation;
- Camera;
- Reader;
- Problem Workspace;
- Step Workspace;
- Smart Canvas;
- Formula/Equation;
- Diagram;
- Graph;
- Table/Data;
- Timeline;
- Source Reader;
- Essay Workspace;
- Map;
- Quiz;
- Assessment;
- Voice;
- Experiment;
- Simulation;
- Creative Workspace;
- Reflection.

Minimize based on corpus.

Không tạo 18 surface chỉ vì concept đã liệt kê.

==================================================
12. DERIVE FLOWS FROM LEARNING ACTIVITY
==================================================

Đề xuất flow từ corpus.

Không mặc định:

Home → Subject → Chat.

Falsify ít nhất:

PROBLEM SOLVING

Home
→ Subject
→ Activity
→ Problem Workspace
→ Independent Attempt
→ Diagnostic
→ Hint if needed
→ Your Turn
→ Evidence
→ Review.

READING

Home
→ Text
→ Reader
→ Observe/Read
→ Question
→ Evidence/Source
→ Response
→ Feedback
→ Reflection.

WRITING / ESSAY

Prompt
→ Understand
→ Brainstorm
→ Outline
→ Learner Draft
→ Feedback
→ Learner Revision
→ Reflection.

SCIENCE

Question/Phenomenon
→ Observe
→ Hypothesis
→ Experiment/Model/Data
→ Analysis
→ Explanation
→ Conclusion.

HISTORY

Source/Event
→ Context
→ Observe Source
→ Chronology
→ Compare Evidence
→ Claim
→ Explanation.

GEOGRAPHY

Map/Data
→ Inspect
→ Locate
→ Compare
→ Spatial/Data Reasoning
→ Conclusion.

CREATIVE / PERFORMANCE

Prompt
→ Create/Perform
→ Artifact/Recording
→ Feedback
→ Reflection.

AI EDUCATION

derive directly from official YCCĐ and 4 strands.

Không biến thành generic AI course.

==================================================
13. PEDAGOGICAL PROVENANCE
==================================================

Mọi proposed academic UX phải tuân:

    NO TEACHING WITHOUT PEDAGOGICAL PROVENANCE.

UI phải có khả năng trả lời:

WHAT?
Đang học gì?

WHERE?
Ở đâu trong curriculum?

WHY?
Tại sao SAM chọn hoạt động này?

HOW?
Method nào?

SOURCE?
Nguồn nào/page nào?

AUTHORITY?
SOURCE_EXPLICIT
SOURCE_DEMONSTRATED
SAM_INFERRED?

PERMISSION?
Tại sao TutorScope cho phép?

Provenance phải available từ đầu interaction.

Không chỉ Screen 17.

16 Why This Method và 17 Source
là detailed drill-down.

==================================================
14. AGE-ADAPTIVE UX
==================================================

Không tạo 12 app.

Target:

ONE DESIGN SYSTEM
+
AGE-ADAPTIVE POLICY.

Falsify policies cho:

Grade 1–2
Grade 3–5
Grade 6–9
Grade 10–12.

Evaluate:

- typography;
- density;
- control size;
- navigation;
- mascot prominence;
- voice;
- reading;
- terminology;
- explanation depth;
- autonomy;
- parent involvement;
- animation;
- reward/gamification.

De-gamify nếu evidence không support learning value.

Không dùng XP/streak/leaderboard như proxy mastery.

==================================================
15. SHARED DEVICE / MULTI-PROFILE
==================================================

Founder requirement:

Học cùng SAM phải phục vụ gia đình chỉ có một thiết bị.

Model:

ONE DEVICE
    ↓
FAMILY
    ├── Parent
    ├── Learner A
    ├── Learner B
    └── Learner C.

Invariant:

DEVICE != USER
ACCOUNT != LEARNER
PARENT != LEARNER.

Một trẻ không bắt buộc có account/email riêng.

Shared:

- app;
- curriculum;
- Content Store;
- Knowledge Pack.

Per learner:

- LearnerProfile;
- grade;
- timetable;
- Student Knowledge State;
- LearningEvidence;
- sessions;
- review schedule;
- recommendations.

Critical:

NO CROSS-LEARNER EVIDENCE CONTAMINATION.

Đề xuất UX:

Minh Anh · Lớp 5 ▾
→ Đổi người học.

Parent Mode riêng.

Không sibling ranking.

"SO SÁNH NHANH"

nếu còn trong concept:

falsify/replace bằng:

"TÌNH HÌNH CÁC CON".

==================================================
16. HUB CAPABILITY REUSE — AUDIT AGAINST REAL CURRICULUM
==================================================

Dùng corpus mới để re-evaluate Hub reuse.

Audit actual Workizen AI Personal Hub capability,
không chỉ Founder list.

Ít nhất:

OCR
Document Scanner
Camera
QR/Barcode
STT
TTS
Voice
Smart Canvas
AI Provider Router
Free Providers
BYOK
Local AI/Ollama
Auth/Login/Register
Account
Backup/Restore
Storage
Sync
AI Usage/Quota
Library
Document Intelligence
PDF ingestion
Search
Mindmap
Presentation
Infographic
Summary
Document Q&A
Notifications
Settings
Localization
Analytics
Crash Reporting
Share/Export
Deep Links
Design System.

Map từng capability vào actual subject/activity.

Ví dụ:

OCR:
môn/activity nào thực sự dùng?

STT:
oral evidence nào?

TTS:
grade/activity nào?

Canvas:
Math?
Physics?
Chemistry?
Geography?
Essay planning?
Creative?

Document Reader:
Vietnamese?
History?
Science?

Mindmap:
có actual learning value ở đâu?

QR:
có real educational workflow hay chỉ vì Hub có?

Không reuse capability chỉ vì nó tồn tại.

==================================================
17. REUSE PRINCIPLE
==================================================

Target:

WORKIZEN SHARED CAPABILITIES
        ↓
EDUCATION SAFETY ADAPTER
        ↓
SAM EDUCATION DOMAIN.

Không copy source rồi rename.

Reuse infra tối đa.

Xây mới phần educational intelligence.

Shared candidates:

OCR
Scan
Camera
QR
STT/TTS
AI Router
Auth
Backup
Storage
Library infrastructure
Notifications
Canvas primitives
Document handling
Design tokens.

SAM-specific:

Curriculum
Content/Knowledge Graph
SkillCase
Method
TutorScope
TeachingAct
LearningEvidence
Student Knowledge State
Next Best Learning Action
Pedagogical Provenance
Learner/Parent policies.

==================================================
18. CHILD SAFETY / HUB ADAPTATION
==================================================

Generic Hub feature không tự động phù hợp child.

Mọi reuse phải classify:

ALLOW
ADAPT
AGE-GATED
PARENT-GATED
SANITIZE
DISABLE
RESEARCH.

Đặc biệt audit:

- generic chat;
- external web links;
- sharing;
- analytics;
- provider data;
- imported documents;
- voice;
- image generation;
- export;
- notifications;
- cloud processing.

Hub AI Router không có pedagogical authority.

Hub OCR không tạo LearningEvidence trực tiếp.

==================================================
19. LOCAL-FIRST
==================================================

Giữ ADR-006.

Target:

SHARED LOCAL K–12 KNOWLEDGE
+
PER-LEARNER LOCAL STATE
+
OPTIONAL CLOUD INFERENCE/SYNC.

Không duplicate Knowledge Pack cho từng child.

Phân tích UX implications:

- offline;
- storage;
- download/update;
- shared family device;
- old Android;
- low-resource device.

Không để UX giả định luôn online.

==================================================
20. TUTOR MODE != ASSESSMENT MODE
==================================================

Falsify current screens 20/21/22.

Tutor/Practice:

SAM có thể:
probe
hint
scaffold
explain.

Assessment:

assistance restricted/disabled according to policy.

Independent evidence phải được bảo toàn.

Sau assessment:
analysis/remediation mới diễn ra.

Nếu Screen 21 thực chất là Result:
SPLIT/REPLACE accordingly.

==================================================
21. STUDENT PROGRESS
==================================================

Audit Progress/Parent screens.

Không dùng:

completion %
XP
streak
rank
radar chart

như Learning Truth nếu data không support.

Ưu tiên:

estimated mastery
coverage
confidence
independent performance
assisted performance
self-correction
hint-depth reduction
retention
transfer
review due.

Unobserved != failed.
Unobserved != mastered.

==================================================
22. AI EDUCATION
==================================================

Screen 29 phải audit trực tiếp với official AI curriculum.

Không dùng generic ladder:

AI
→ ML
→ Deep Learning
→ Prompt Engineering

nếu không khớp chương trình.

Use actual:

267 YCCĐ / official data currently available

và 4 strands:

A Human-centered thinking
B AI ethics
C AI techniques/applications
D AI system design.

Grade progression phải derive từ curriculum.

==================================================
23. CRITICAL FALSIFICATION QUESTIONS
==================================================

Bắt buộc phản biện:

F1
Có thực sự cần 38 production screens?

F2
Một Subject Home đủ mọi môn?

F3
Một Chat UI đủ mọi môn?

F4
Mỗi môn cần UI hoàn toàn riêng?

F5
Grade = mastery?

F6
Timetable = exact lesson?

F7
Correct-after-hint = independent?

F8
Transcript = LearningEvidence?

F9
Quiz = Assessment?

F10
Curriculum Graph nên chứa UI?

F11
Một age UI dùng Grade1–12?

F12
XP/streak = learning progress?

F13
Sibling comparison có educational value?

F14
History = timeline?

F15
Geography = map?

F16
Physics/Chemistry = simulation?

F17
Essay tutor nên viết bài trước?

F18
AI Learning concept khớp official curriculum?

F19
Mọi Hub capability nên sang SAM?

F20
Canvas cần cho mọi subject?

F21
OCR result = educational truth?

F22
LLM/provider có pedagogical authority?

F23
Device = learner?

F24
Mỗi learner cần account?

F25
Mỗi learner cần Knowledge Pack riêng?

F26
Mỗi subject cần separate chatbot memory?

F27
Source citation chỉ cần hiện cuối answer?

F28
100% OCR = 100% curriculum understood?

Expected answer không được hard-code.

Falsify bằng evidence.

==================================================
24. OUTPUT — TẠO ĐÚNG 5 REPORT FILE
==================================================

Tất cả đặt tại:

docs/design/

Không tạo thêm hàng loạt report nhỏ.

==================================================
FILE 1
01-CURRICULUM-UX-EVIDENCE-REPORT.md
==================================================

Đây là EVIDENCE REPORT.

Bao gồm:

- final corpus snapshot;
- success/partial/failed;
- structural coverage;
- semantic coverage;
- Grade1–12 distribution;
- subject distribution;
- lesson/section/ContentUnit;
- semantic types;
- explicit/demonstrated/inferred;
- exercise/activity statistics;
- response patterns;
- activity taxonomy findings;
- OCR/layout issues;
- unknown/unmapped;
- source quality;
- important cross-grade patterns.

Đặc biệt trả lời:

"SGK K–12 thực sự yêu cầu học sinh làm những loại hoạt động nào?"

==================================================
FILE 2
02-K12-SUBJECT-UX-FIT-REPORT.md
==================================================

Đây là K–12 × SUBJECT REPORT.

Với mỗi subject:

- corpus evidence;
- grade availability;
- learning goals;
- activity patterns;
- exercise patterns;
- response types;
- SkillCase implications;
- TeachingAct implications;
- LearningEvidence;
- interaction surfaces;
- age differences;
- current concept fit;
- missing UX;
- Hub reuse;
- unknowns.

Có summary matrix:

GRADE BAND
× SUBJECT
× ACTIVITY
× RESPONSE
× SURFACE
× TEACHING ACT
× EVIDENCE
× AGE POLICY.

==================================================
FILE 3
03-38-CONCEPT-SCREEN-REAUDIT.md
==================================================

Re-audit đủ 38 concept.

Table:

ID
Screen
Current Intent
Corpus Evidence
Learning Job
Grade Fit
Subject Fit
Activity Fit
Decision
Reason
Recommended Change
Entry
Exit
Hub Reuse
Risk.

Cuối file:

- KEEP count;
- MODIFY;
- MERGE;
- SPLIT;
- REPLACE;
- DEFER;
- proposed production screen count;
- proposed surface count;
- screen vs state changes;
- unsupported concepts;
- missing concepts.

==================================================
FILE 4
04-PROPOSED-LEARNING-UX-AND-FLOWS.md
==================================================

Đây là SOLUTION REPORT.

Đề xuất final:

- app IA;
- Learning Shell;
- Home;
- Subject navigation;
- Next Best Learning Action;
- age policy;
- SubjectContext;
- ActivityContext;
- Surface Resolver;
- surface catalogue;
- provenance UX;
- Camera Tutor;
- Voice;
- Review;
- Quiz;
- Assessment;
- Library;
- Parent;
- Multi-profile;
- shared device;
- Notifications;
- Settings;
- Hub reuse.

Vẽ flow cụ thể cho:

Onboarding
Learner Setup
Shared Device
Home
Subject
Problem Solving
Camera Tutor
Reading
Writing/Essay
Science
History
Geography
Creative/Performance
AI Education
Quiz
Assessment
Review
Voice
Parent
Multi-child.

Format mỗi flow:

ENTRY
→ CONTEXT
→ SURFACE
→ TEACHING ACT
→ LEARNER ACTION
→ EVIDENCE
→ NEXT ACTION.

==================================================
FILE 5
05-FOUNDER-RECOMMENDATIONS-AND-CHALLENGES.md
==================================================

Đây là CRITICAL REVIEW.

Không summarize đơn thuần.

Phải nói thẳng:

A. Founder/GPT assumptions nào được corpus xác nhận.

B. Assumptions nào bị falsify.

C. Assumptions nào chưa đủ evidence.

D. 38 concept overfit ở đâu.

E. UX nào không phù hợp K–12.

F. Grade band nào yếu nhất.

G. Subject nào cần specialized surface.

H. Subject nào reuse được surface.

I. Screens nên merge.

J. Screens nên replace.

K. Screens/surfaces còn thiếu.

L. Hub capability nào nên reuse.

M. Hub capability nào không nên reuse.

N. Child-safety gaps.

O. Multi-profile/shared-device implications.

P. Local-first implications.

Q. Risks nếu implement concept ngay.

R. Recommended product architecture.

S. Recommended production sequence.

T. What NOT to build yet.

U. Decisions Founder cần đưa ra sau này.

V. Recommended First Vertical Slice.

==================================================
25. ĐÁNH GIÁ LẠI WAL-108 SAU 5 REPORT
==================================================

KHÔNG chạy production implementation lớn của WAL-108
trước khi 5 report hoàn thành.

Sau reports:

re-evaluate WAL-108.

Decision:

KEEP
MODIFY
SPLIT
REORDER.

Nếu:

Toán 5 Bài 6

vẫn là best first vertical slice:
giữ.

Nhưng phải giải thích bằng evidence.

Nếu corpus cho thấy cần thêm một cross-subject falsification slice:
đề xuất.

First slice cuối cùng phải chứng minh ít nhất:

Curriculum
→ Activity
→ Surface
→ TutorScope
→ Method
→ TeachingAct
→ Learner Action
→ LearningEvidence
→ Knowledge State
→ Next Action.

==================================================
26. CROSS-SUBJECT ARCHITECTURE CHECK
==================================================

Trước production lock-in,
dùng ít nhất 3 bounded examples:

A. Toán — Problem Solving.

B. Tiếng Việt/Ngữ văn — Reading/Writing.

C. Một môn khác có interaction khác rõ rệt,
ưu tiên History / Geography / Science
dựa trên corpus evidence.

Không cần build full UI.

Mục tiêu:

falsify Math overfitting.

==================================================
27. JIRA / CONFLUENCE / GIT
==================================================

Task này chủ yếu là research/design audit.

Jira:

Search existing WAL trước.

Reuse / modify / merge.

Không:
- one ticket per subject;
- one ticket per grade;
- one ticket per screen.

Reconcile đặc biệt:

WAL-108
WAL-109
WAL-110
và existing UX/curriculum tickets.

Chỉ tạo ticket mới nếu:
- finding stable;
- có evidence;
- có action;
- không duplicate.

Confluence:
stable Founder/Product truth.

Git:
5 reports + technical/design evidence.

==================================================
28. EXECUTION BEHAVIOR
==================================================

Task đã được Founder phê duyệt trước.

Do đó:

1. Tiếp tục current OCR/ingestion.
2. Không dừng hỏi Founder khi ingestion hoàn thành.
3. Verify final ingestion checkpoint.
4. Lock corpus snapshot.
5. Tự động bắt đầu task này.
6. Tạo đủ 5 reports.
7. Reconcile Jira.
8. Commit/push.
9. Sau đó báo Founder checkpoint.

Không cần hỏi:

"Corpus xong rồi, có tiếp tục không?"

Câu trả lời đã là:

YES.

Nhưng:

KHÔNG tự bắt đầu major production UI implementation
sau report trước Founder checkpoint.

==================================================
29. FINAL FOUNDER CHECKPOINT
==================================================

Sau khi hoàn thành, báo:

# CORPUS SNAPSHOT

processed/total
success
partial
failed
grades
subjects
ContentUnits
activities/exercises
structural coverage
semantic coverage.

# TOP 10 SGK-DERIVED FINDINGS

Chỉ findings có evidence mạnh.

# GRADE BAND FINDINGS

1–2
3–5
6–9
10–12.

# SUBJECT FINDINGS

Điểm quan trọng theo từng subject family.

# 38 SCREEN REAUDIT

KEEP
MODIFY
MERGE
SPLIT
REPLACE
DEFER.

# BIGGEST UX CHANGES

Concept hiện tại thay đổi gì sau full corpus.

# FINAL SURFACE SYSTEM

Bao nhiêu surface,
surface nào shared,
surface nào specialized.

# FINAL FLOW RECOMMENDATION

Các learning flow chính.

# AGE-ADAPTIVE UX

Các khác biệt chính.

# HUB REUSE

REUSE AS-IS
REUSE + ADAPTER
EXTRACT SHARED
POC
REJECT.

# SHARED DEVICE / MULTI-PROFILE

Final recommendation.

# FIRST SLICE

KEEP/MODIFY WAL-108 và lý do.

# TOP RISKS

# DATA GAPS

# JIRA CHANGES

# BLOCKERS

# FOUNDER DECISIONS REQUIRED

# NEXT RECOMMENDED EXECUTION

==================================================
30. FINAL PRINCIPLE
==================================================

Đừng hỏi:

    "Làm sao biến 38 ảnh concept thành app?"

Hãy dùng toàn bộ corpus K–12 để trả lời:

    "Trẻ em Việt Nam từ lớp 1 đến lớp 12
    thực sự phải học và thực hiện những loại hoạt động nào,
    từng môn khác nhau ra sao,
    SAM nên hỗ trợ những hoạt động đó bằng interaction nào,
    và 38 concept hiện tại phải thay đổi thế nào để phục vụ việc học đó?"

Pipeline quyết định phải là:

FULL K–12 CORPUS
        ↓
CURRICULUM EVIDENCE
        ↓
SUBJECT + ACTIVITY SEMANTICS
        ↓
PEDAGOGICAL MODEL
        ↓
INTERACTION SURFACES
        ↓
UX FLOWS
        ↓
38-CONCEPT RECONCILIATION
        ↓
PRODUCTION PLAN.

Không đảo ngược pipeline này.
