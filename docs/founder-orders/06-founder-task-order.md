# FOUNDER TASK ORDER
## HỌC CÙNG SAM — AUDIT 38 AI-FIRST CONCEPT SCREENS
## UX ARCHITECTURE × LEARNING FLOW × K–12 CURRICULUM FIT × SUBJECT-SPECIFIC UX

### 0. QUYỀN THỰC THI

Bạn được toàn quyền chủ động thực hiện research / audit / architecture / UX design /
documentation / Jira / Confluence / ADR / prototype có thể đảo ngược.

KHÔNG dừng lại chỉ để hỏi Founder các quyết định nhỏ có thể tự nghiên cứu hoặc falsify.

Chỉ dừng khi gặp:
- quyết định thương hiệu không thể đảo ngược;
- licensing / bản quyền SGK;
- chi phí lớn;
- legal/compliance commitment;
- destructive operation trên shared repo;
- thay đổi scope sản phẩm lớn.

Sau khi hoàn thành audit:
- cập nhật Jira hiện có;
- merge/modify ticket nếu đã có;
- KHÔNG tạo ticket trùng;
- tự xếp Ready theo dependency/value;
- tiếp tục highest-value unblocked task nếu không có blocker.

==================================================
1. BỐI CẢNH
==================================================

Founder đã tạo và đưa vào repo bộ:

    concept-ai-first/

gồm 38 concept screens của Học cùng SAM.

Đây là:

    DESIGN INTENT / UX REFERENCE BASELINE

KHÔNG phải:
- pixel-perfect specification;
- final information architecture;
- final curriculum model;
- final interaction model;
- yêu cầu implement y nguyên ảnh.

Nhiệm vụ của bạn là nghiên cứu bộ concept này cùng toàn bộ Product Truth hiện có,
sau đó thiết kế lại UX architecture và learning flow hợp lý trước khi production implementation.

PHẢI đọc trước:
- 38 concept images;
- Product / Architecture docs;
- ADR hiện tại;
- Curriculum Graph / Content Graph;
- Student Knowledge State;
- LearningEvidence;
- TeachingAct;
- TutorScope;
- Method / SkillCase;
- Camera Perception;
- LearningSession;
- ADR-006 Local-first Knowledge Pack;
- AI Curriculum research;
- Jira hiện tại;
- Confluence hiện tại.

Không đánh giá 38 ảnh chỉ bằng thẩm mỹ.

==================================================
2. NORTH STAR
==================================================

Học cùng SAM không phải:

    "38 màn hình đẹp của một app học online"

Mà phải trở thành:

    AI Learning Coach hiểu:
    - học sinh là ai;
    - đang học lớp nào;
    - chương trình nào;
    - môn nào;
    - kiến thức nào;
    - chưa hiểu gì;
    - nên học gì tiếp;
    - nên hỗ trợ bao nhiêu;
    - dùng phương pháp nào;
    - dựa trên nguồn nào.

North Star:

    AI hiểu con đang học gì,
    chưa hiểu gì,
    và nên học gì tiếp theo.

Product principle:

    AI that teaches, not AI that cheats.

Anti-goal:

    SAM must not maximize learner dependence on AI.

Success:

    learner gradually needs less help from SAM.

==================================================
3. NGUYÊN TẮC AUDIT BẮT BUỘC
==================================================

Không được giả định Founder/GPT concept đúng.

Với mỗi màn hình phải phân loại:

    KEEP
    MODIFY
    MERGE
    SPLIT
    REPLACE
    REMOVE
    DEFER

Và trả lời:

1. Màn hình giải quyết learning job nào?
2. Ai dùng?
3. Grade band nào?
4. Subject nào?
5. Activity type nào?
6. Input context từ đâu?
7. Output đi đâu?
8. Có tạo LearningEvidence không?
9. Có TeachingAct không?
10. Assistance level nào được phép?
11. TutorScope ảnh hưởng thế nào?
12. Curriculum grounding nằm đâu?
13. Provenance/source hiển thị thế nào?
14. Có phù hợp Grade 1–12 không?
15. Có phù hợp mọi môn không?
16. Nếu không thì subject-specific variant là gì?
17. Có thể local-first không?
18. Có nguy cơ biến thành generic LMS / ChatGPT wrapper không?

==================================================
4. AUDIT FLOW TOÀN BỘ 38 SCREENS
==================================================

Hãy kiểm tra và đề xuất flow chính thức.

--------------------------------------------------
FLOW A — FIRST RUN / LEARNER CONTEXT
--------------------------------------------------

01 Onboarding Welcome
    ↓
02 Learner Profile
    ↓
03 Subject Setup
    ↓
04 Timetable
    ↓
05 Home

01 — ONBOARDING WELCOME

Mục tiêu:
- giải thích SAM là AI Learning Coach;
- không quảng cáo như generic AI chatbot;
- giải thích ngắn gọn SAM sẽ:
  hiểu chương trình → hiểu tiến độ → hướng dẫn → giúp tự làm.

Phải kiểm tra:
- Student vs Parent entry.
- Có cần role selection không?
- Privacy/parent consent theo độ tuổi.
- Không overload onboarding.

02 — LEARNER PROFILE

Tối thiểu:
- tên/nickname;
- birth year;
- current grade;
- curriculum context;
- learner profile.

Invariant:

    Birth year != current grade
    Current grade != mastery

Parent Account != Learner.

Một Parent có thể có nhiều LearnerProfile.

Không được suy luận:
"đang lớp 5 → đã biết toàn bộ lớp 1–4".

03 — SUBJECT SETUP

Không hard-code generic subject grid nếu Curriculum Knowledge đã biết môn học của grade.

Phải nghiên cứu:
- môn bắt buộc;
- môn lựa chọn;
- grade-dependent subjects;
- curriculum-specific subject naming.

Cho phép learner:
- ưu tiên môn;
- yêu thích;
- môn cần cải thiện.

Nhưng preference != curriculum truth.

04 — TIMETABLE

Timetable là CONTEXT INPUT.

Không phải core product.

Invariant:

    timetable subject != exact lesson

Ví dụ:

    Thứ Hai tiết 1 = Toán

KHÔNG được suy ra:

    ngày mai học Bài 17

trừ khi có:
- teacher/class progress;
- assignment;
- KHDH;
- learner/parent input;
- confirmed prediction.

Onboarding timetable phải optional/skippable.

Nghiên cứu:
- manual input;
- photo timetable → OCR → learner confirmation;
- local storage.

05 — HOME

Đây phải là:

    Learning Mission Center

không phải static app launcher.

Đề xuất IA:

    HÔM NAY
    SẮP TỚI
    NÊN HỌC TIẾP
    CÁC MÔN CỦA CON

Home phải derive từ:

LearnerProfile
+ Timetable
+ Curriculum Context
+ Student Knowledge State
+ Review Schedule
+ LearningSession history
→ Next Best Learning Action.

--------------------------------------------------
FLOW B — SUBJECT DISCOVERY
--------------------------------------------------

05 Home
   ↓
06 Subjects
   ↓
07 Subject Home

06 — SUBJECTS

Danh sách môn phải curriculum-aware và grade-aware.

Không biến thành "feature catalog".

Hiển thị:
- current curriculum position;
- progress;
- weak/review-due indicators;
- next recommended action.

07 — SUBJECT HOME

Không dùng một template y hệt cho tất cả môn.

Subject Home phải resolve theo:

    SubjectContext
    + ActivityContext
    + LearnerContext
    + Student State

Audit subject-specific variants.

==================================================
5. CORE TUTOR FLOW
==================================================

FLOW:

05/07
 ↓
08 Camera
 ↓
09 Camera Confirm
 ↓
10 Tutor Start
 ↓
11 Diagnostic
 ↓
12 Problem Workspace
 ↓
13 Hint
 ↓
14 Your Turn
 ↓
15 Success
 ↓
18 Review / 19 Learning Map / Next Action

08 — CAMERA

Camera là acquisition surface.

Phải hỗ trợ pre-capture guidance:
- move closer;
- hold steady;
- more light;
- straighten phone;
- fit one problem;
- remove occlusion;
- too blurry;
- multiple problems detected.

Không chạy continuous heavy CV nếu không cần.

09 — CAMERA CONFIRM

Đây là safety boundary, không phải cosmetic screen.

Invariant:

    UNCONFIRMED MACHINE PERCEPTION
    MUST NOT ENTER LEARNING EVIDENCE.

Flow:

Image
→ PerceptionHypothesis
→ "Tớ đọc được thế này"
→ Confirm / Correct / Retake
→ ConfirmedProblem.

Machine OCR confidence != source truth confidence.

10 — TUTOR START

Trước khi SAM bắt đầu dạy, learner phải hiểu:

- đang học môn gì;
- lớp nào;
- bài/chủ đề nào;
- SAM nghĩ đây là kỹ năng gì;
- phương pháp nào sẽ được dùng;
- dựa vào nguồn nào.

Đây là nơi bắt đầu "Pedagogical Provenance".

11 — DIAGNOSTIC

Không giải ngay.

SAM phải có khả năng:
- hỏi learner thử trước;
- diagnostic probe;
- recall prior knowledge;
- detect likely gap.

Diagnostic interaction có thể tạo LearningEvidence nếu đủ điều kiện.

12 — PROBLEM WORKSPACE

Đây phải là primary workspace cho problem-solving subjects.

Không biến thành Chat UI.

Có thể compose:
- problem statement;
- working area;
- formula;
- diagram;
- graph;
- steps;
- answer input;
- SAM intervention.

13 — HINT

Implement Assistance Ladder:

independent
→ prompt
→ small hint
→ strategic hint
→ partial scaffold
→ demonstration
→ worked solution.

Hint phải có identity/version và assistance level.

Correct-after-hint != independent correct.

14 — YOUR TURN

SAM phải step back.

Mục tiêu:
learner thực hiện lại / tiếp tục / transfer.

Đây là màn hình cực quan trọng cho product thesis:

    SAM succeeds when learner needs SAM less.

15 — SUCCESS

Không chỉ:
"Giỏi quá! + XP".

Phải thể hiện:
- learner tự làm được gì;
- cần bao nhiêu hỗ trợ;
- self-correction;
- mastery evidence;
- next action.

Praise:
- effort;
- strategy;
- correction;
- independence.

Không praise "thiên tài" liên tục.

==================================================
6. TRANSPARENCY / PEDAGOGICAL PROVENANCE
==================================================

16 Why This Method
17 Source

Hai screen này không được coi là phụ.

Chúng thể hiện product invariant:

    NO TEACHING WITHOUT PEDAGOGICAL PROVENANCE.

Mỗi academic TeachingAct phải có khả năng trả lời:

WHAT
    đang dạy kiến thức/kỹ năng nào?

WHERE
    nằm ở đâu trong curriculum?

WHY
    tại sao SAM chọn nó?

HOW
    đang dùng Method nào?

SOURCE
    nguồn nào/page nào?

AUTHORITY
    nguồn nói trực tiếp,
    nguồn minh họa,
    hay SAM suy luận?

PERMISSION
    tại sao Method này được phép ở learner context hiện tại?

16 — WHY THIS METHOD

Ví dụ:

Toán · Lớp 5
Bài 6 · Phân số

Cách đang học:
Đưa về cùng mẫu rồi cộng tử.

Vì sao?
✓ phù hợp bài hiện tại
✓ áp dụng được với bài toán này
✓ nằm trong TutorScope của học sinh

Nguồn:
SGK Toán 5...
Trang ...

17 — SOURCE

Phải phân biệt rõ:

SOURCE_EXPLICIT
SOURCE_DEMONSTRATED
SAM_INFERRED

Không được biến cả ba thành:

    "Theo SGK..."

Age-adaptive UI:

Grade nhỏ:
    📖 Theo sách
    🧭 Cách mình đang học
    ✨ SAM đang giải thích thêm

Parent/older student/teacher:
    source → page → ContentUnit
    → Method → SkillCase → TutorScope
    → version.

==================================================
7. REVIEW / KNOWLEDGE STATE
==================================================

18 Review
19 Learning Map
20 Quiz
21 Assessment
22 Result

18 — REVIEW

Review phải dựa trên:
- Review Schedule;
- mastery uncertainty;
- evidence recency;
- weak SkillCase;
- transfer need.

Không chỉ "làm lại câu sai".

19 — LEARNING MAP

Phải phản ánh Curriculum Graph + Student Knowledge State.

Phân biệt:
- curriculum coverage;
- estimated mastery;
- evidence coverage;
- confidence.

Unobserved != failed.
Unobserved != mastered.

20 — QUIZ

Practice/Quiz mode.

SAM có thể:
- probe;
- hint;
- explain;
- retry.

Nhưng evidence phải ghi assistance.

21 — ASSESSMENT

Invariant:

    TUTOR MODE != ASSESSMENT MODE.

Trong assessment:
- hạn chế/disable hint;
- không giải thay;
- không reveal answer giữa bài nếu policy cấm;
- preserve independent evidence.

Sau assessment mới:
- diagnosis;
- explanation;
- remediation/review.

22 — RESULT

Không chỉ show score.

Phải show:
- independent performance;
- assisted performance;
- evidence confidence;
- strengths;
- weak SkillCases;
- misconceptions nếu đủ evidence;
- next learning action.

==================================================
8. SUBJECT-SPECIFIC ENVIRONMENTS
==================================================

Audit kỹ screens:

23 Vietnamese
24 Essay
25 Physics
26 Chemistry
27 History
28 Geography
29 AI Learning

Không được kết luận chỉ bằng các concept hiện tại.

Research chương trình Grade 1–12 và đề xuất interaction model phù hợp.

--------------------------------------------------
23 — VIETNAMESE
--------------------------------------------------

Không chỉ vocabulary cards.

Audit các activity family:
- đọc;
- đọc hiểu;
- từ/câu;
- chính tả;
- nói/nghe;
- viết;
- ngữ pháp;
- cảm thụ;
- trình bày;
- revision.

Phải kiểm tra SkillCase khác nhau:

recognize
vs
explain
vs
choose
vs
apply
vs
independent writing
vs
revise.

Không collapse thành một mastery score duy nhất.

--------------------------------------------------
24 — ESSAY
--------------------------------------------------

Concept hiện tại phải được audit mạnh.

Essay flow ưu tiên:

Prompt
→ Understand
→ Brainstorm
→ Outline
→ Learner Draft
→ Evidence/Source Check
→ SAM Critique
→ Learner Revision
→ Reflection.

SAM KHÔNG default viết bài hộ.

LearningEvidence phải phân biệt:
- outline with assistance;
- independent draft;
- revision after feedback;
- final independent capability.

--------------------------------------------------
25 — PHYSICS
--------------------------------------------------

Không chỉ theory + quiz.

Interaction surfaces có thể cần:
- diagram;
- formula;
- graph;
- vector;
- circuit;
- optics;
- data table;
- simulation;
- problem workspace.

Audit Grade 1–12 applicability.

--------------------------------------------------
26 — CHEMISTRY
--------------------------------------------------

Nghiên cứu:
- equations;
- balancing;
- periodic table;
- reaction model;
- observation;
- calculation;
- experiment reasoning;
- safety;
- lab/simulation later.

Không biến simulation thành decorative animation.

--------------------------------------------------
27 — HISTORY
--------------------------------------------------

Concept timeline là hypothesis, không phải final answer.

Nghiên cứu:
- chronology;
- event;
- causality;
- source reading;
- evidence;
- compare interpretations;
- argument;
- map;
- essay;
- historical reasoning.

SAM phải phân biệt:

SOURCE CLAIM
vs
SAM INTERPRETATION
vs
LEARNER CONCLUSION.

Không trình bày interpretation như single authoritative truth nếu source không hỗ trợ.

--------------------------------------------------
28 — GEOGRAPHY
--------------------------------------------------

Map phải được xem như first-class interaction surface.

Nghiên cứu:
- map;
- layer;
- location;
- spatial relation;
- chart;
- demographic/economic data;
- climate;
- physical geography;
- comparison;
- source interpretation.

Không chỉ "map + flashcard".

--------------------------------------------------
29 — AI LEARNING
--------------------------------------------------

PHẢI đối chiếu trực tiếp với:

QĐ2422/QĐ-BGDĐT
CV5588/BGDĐT-GDPT

và AI Curriculum Graph hiện tại.

Không được thiết kế AI Learning như generic:

ChatGPT
→ Machine Learning
→ Deep Learning
→ Prompt Engineering

nếu không khớp official curriculum.

Đối chiếu 4 strand:

A — Human-centered thinking
B — AI ethics
C — AI techniques/applications
D — AI system design

theo Grade 1–12.

Official YCCĐ / code phải first-class.

Không có curriculum edge:
    không tự claim integration.

==================================================
9. LEARNING HISTORY / PROGRESS
==================================================

30 History Sessions
31 Progress

30 — HISTORY SESSIONS

Đề xuất model:

Learner
→ Day
→ Subject
→ LearningSession.

Nhưng session chỉ lưu MỘT LẦN.

Date view và Subject view chỉ là projection.

Không tạo separate memory silo per subject.

Session cần trace được:

- learner;
- subject;
- curriculum;
- activity;
- TeachingAct;
- assistance;
- method;
- source;
- evidence;
- outcome;
- versions.

Transcript != LearningEvidence.

31 — PROGRESS

Không chỉ completion % / XP / streak.

Audit để ưu tiên educational metrics:

- independent attempts;
- assisted attempts;
- hint-depth reduction;
- self-correction;
- retention;
- transfer;
- coverage;
- mastery estimate;
- evidence confidence;
- review due.

Gamification không được lấn át learning truth.

==================================================
10. PARENT EXPERIENCE
==================================================

32 Parent Home
33 Parent Detail
34 Multi-child

32 — PARENT HOME

Parent Home phải trả lời câu hỏi:

    "Tối nay tôi nên giúp con điều gì?"

không phải:
    "Tôi có thể giám sát con bao nhiêu?"

Ưu tiên:
- tonight action;
- important progress;
- weak/review-due area;
- upcoming known work;
- SAM recommendation.

33 — PARENT DETAIL

Không show false precision.

Phải phân biệt:
- mastery estimate;
- coverage;
- confidence;
- observed/unobserved;
- independent/assisted.

Không claim:
"Con yếu X"
nếu evidence chưa đủ.

34 — MULTI-CHILD

Model:

Parent/Guardian
    → Learner A
    → Learner B
    → Learner C

Mỗi learner có độc lập:
- grade;
- curriculum;
- timetable;
- Knowledge State;
- evidence;
- recommendation;
- session history.

KHÔNG khuyến khích comparison/ranking giữa anh chị em.

Audit concept hiện tại:
nếu "So sánh nhanh" giữa các con tạo competitive comparison không phù hợp,
hãy MODIFY/REMOVE.

==================================================
11. SAM VOICE
==================================================

35 SAM Voice

Voice không phải một generic assistant đứng ngoài learning architecture.

Voice phải sử dụng cùng:

LearnerContext
+ CurriculumContext
+ SubjectContext
+ ActivityContext
+ TutorScope
+ Student State
+ EvidencePack.

Nghiên cứu age-adaptive voice:

Primary:
    voice-heavy / short / friendly.

Secondary:
    more concise / controllable / less mascot-heavy.

Voice TeachingAct vẫn phải chịu:
- TutorScope;
- Method permission;
- provenance;
- assistance policy.

Không để voice bypass pedagogical constraints.

==================================================
12. LIBRARY
==================================================

36 Library

Audit cực kỹ.

Không được mặc định Library = Google Drive của học sinh.

Phân biệt:

A. SAM Curriculum Knowledge
B. Licensed/OER/teacher-created educational content
C. Learner imported documents
D. Saved learning artifacts
E. Offline Knowledge Pack.

Đừng expose raw internal Knowledge Pack như user documents nếu không có UX reason.

Local-first architecture ADR-006 phải được giữ.

==================================================
13. NOTIFICATIONS
==================================================

37 Notifications

Notifications phải phục vụ learning.

Ưu tiên:
- review due;
- upcoming timetable;
- unfinished learning session;
- parent-important insight;
- assessment;
- confirmed assignment.

Không tối ưu engagement/addiction.

Avoid:
- meaningless streak pressure;
- excessive XP;
- spam;
- guilt/shame notifications.

Age + parent policy aware.

==================================================
14. SETTINGS
==================================================

38 Settings

Audit theo role.

Student settings != Parent settings.

Nghiên cứu:
- learner profile;
- parent/guardian;
- privacy;
- retention;
- voice;
- accessibility;
- age-adaptive UI;
- offline content;
- Knowledge Pack;
- notifications;
- timetable;
- data export/delete;
- AI provider/cloud inference disclosure nếu applicable.

Child safety/privacy phải first-class.

==================================================
15. KHÔNG THIẾT KẾ THEO 12 APP RIÊNG
==================================================

Không tạo UI riêng hoàn toàn cho từng lớp.

Đề xuất:

    ONE DESIGN SYSTEM
    + AGE-ADAPTIVE POLICY
    + SUBJECT-AWARE INTERACTION SURFACES.

Audit ít nhất các band:

Grade 1–2
Grade 3–5
Grade 6–9
Grade 10–12.

Các biến có thể thay đổi:
- lượng chữ;
- kích thước control;
- mascot prominence;
- illustration;
- voice;
- terminology;
- navigation complexity;
- autonomy;
- parent involvement;
- explanation depth.

==================================================
16. INTERACTION SURFACE ARCHITECTURE
==================================================

Research/falsify architecture:

SAM Learning Shell
    ↓
LearnerContext
    ↓
CurriculumContext
    ↓
SubjectContext
    ↓
ActivityContext
    ↓
Interaction Surface Resolver
    ↓
one or more Learning Surfaces
    ↓
SAM TeachingAct
    ↓
LearningEvidence.

Candidate reusable surfaces:

- SAM Conversation
- Camera
- Problem Workspace
- Step Workspace
- Formula / Equation
- Diagram
- Graph
- Table / Data
- Timeline
- Source Reader
- Essay Workspace
- Map
- Quiz
- Assessment
- Voice
- Simulation
- Experiment
- Reflection.

Không đưa UI component vào authoritative Curriculum Graph.

Rule:

    Curriculum = WHAT
    Pedagogy/Activity = HOW
    Surface Resolver = WHICH INTERACTION
    UI = RENDERING.

==================================================
17. PHÂN LOẠI ACTIVITY — KHÔNG CHỈ THEO MÔN
==================================================

Falsify taxonomy sau:

A. Problem Solving
   Math / Physics / quantitative Chemistry

B. Scientific Investigation
   Physics / Chemistry / Biology / Science

C. Reading / Argument / Source Reasoning
   Vietnamese / Literature / History / Civics

D. Spatial / Data Reasoning
   Geography / Science / History

E. Language
   listening / speaking / reading / writing

F. Assessment
   MCQ / multi-select / short answer /
   essay / step solution / oral / mixed.

Nếu taxonomy sai hoặc thiếu:
MODIFY.

Không giữ chỉ vì Founder/GPT đề xuất.

==================================================
18. K–12 CURRICULUM FIT AUDIT
==================================================

Đây là deliverable bắt buộc.

Audit Grade 1–12 dựa trên corpus và official curriculum sources hiện có.

Không cần tạo 12 × N màn hình.

Tạo matrix:

GRADE BAND
× SUBJECT
× LEARNING GOAL
× ACTIVITY TYPE
× ASSESSMENT TYPE
× INTERACTION SURFACE
× TEACHING ACT
× LEARNING EVIDENCE
× AGE POLICY.

Ít nhất audit:

- Toán
- Tiếng Việt / Ngữ văn
- Ngoại ngữ nếu corpus/support đủ
- Tự nhiên & Xã hội
- Khoa học
- Vật lý
- Hóa học
- Sinh học
- Lịch sử
- Địa lý
- GDCD / relevant social education
- Tin học
- Công nghệ
- AI Education
- các môn khác có trong actual K–12 corpus.

Không suy đoán môn nếu corpus/current official sources không hỗ trợ.
Đánh dấu UNKNOWN / NEED SOURCE.

==================================================
19. CÁC FALSIFICATION BẮT BUỘC
==================================================

F1
38 concept screens có thực sự cần 38 production screens?

F2
Một Subject Home template có đủ cho mọi môn?

F3
Một Chat UI có đủ cho mọi learning activity?

F4
Mỗi subject cần một UI hoàn toàn riêng?

F5
Grade = mastery?

F6
Timetable = exact lesson?

F7
Correct after hint = independent success?

F8
Transcript = LearningEvidence?

F9
Quiz = Assessment?

F10
Curriculum Graph nên chứa UI component?

F11
Một age UI dùng được Grade1–12?

F12
Parent dashboard càng nhiều số càng tốt?

F13
Sibling comparison có giúp học tập?

F14
History chỉ cần timeline?

F15
Geography chỉ cần map?

F16
Physics/Chemistry simulation luôn có learning value?

F17
Essay AI nên viết mẫu trước cho học sinh?

F18
AI Learning hiện tại có đúng QĐ2422 Grade1–12 không?

F19
Library có cần expose toàn bộ local Knowledge Pack?

F20
XP/streak/completion có đại diện mastery?

F21
SAM Voice có được bypass TutorScope?

F22
Source citation chỉ cần show ở cuối câu trả lời?

Expected:
    NO.

Provenance phải available từ khi bắt đầu TeachingAct.

==================================================
20. CRITICAL DATA/RUNTIME AUDIT
==================================================

Trước khi chốt UI, kiểm tra data model có support end-to-end:

Source
→ ContentUnit
→ Concept
→ SkillCase
→ Method
→ Curriculum Position
→ TutorScope
→ TeachingAct
→ Assistance Level
→ Learner Response
→ LearningEvidence
→ Student Knowledge State
→ Next Best Learning Action.

Đặc biệt audit historical lineage:

Mỗi evidence/session có reconstruct được:

- TeachingAct nào?
- Method nào?
- assistance level?
- hint nào?
- policy version?
- knowledgeModelVersion?
- source/content version?
- learner response?
- independent hay assisted?

Nếu không:
tạo/revise ticket.

==================================================
21. DELIVERABLES BẮT BUỘC
==================================================

Tạo các artifact sau.

A. 38-SCREEN-AUDIT.md

Table:

Screen
Current Intent
Learning Job
Target Role
Grade Band
Subject Applicability
KEEP/MODIFY/MERGE/SPLIT/REMOVE/DEFER
Reason
Dependencies
Risks.

B. PROPOSED-APP-FLOW.md

Vẽ full navigation/learning flow.

Tối thiểu:

Onboarding
→ Learner
→ Subject
→ Timetable
→ Home

Home
→ Subject
→ Activity

Home/Subject
→ Camera
→ Confirm
→ Tutor
→ Diagnostic
→ Workspace
→ Hint
→ Your Turn
→ Evidence
→ Success
→ Review/Next Action.

Parent flow riêng.

C. K12-UX-CURRICULUM-FIT.md

Audit Grade1–12 × subjects.

D. INTERACTION-SURFACE-MATRIX.md

Subject/Family
× Goal
× Activity
× Assessment
× Surface
× TeachingAct
× Evidence
× Age Band.

E. SCREEN-FLOW-MATRIX.md

Mỗi screen:
entry conditions
→ context required
→ actions
→ exit states
→ next screens.

F. SUBJECT-UX-ARCHITECTURE.md

Math
Vietnamese/Literature
Physics
Chemistry
Biology/Science
History
Geography
Language
AI
etc.

G. AGE-ADAPTIVE-UX.md

Grade1–2
Grade3–5
Grade6–9
Grade10–12.

H. PARENT-UX-AUDIT.md

Parent Home
Parent Detail
Multi-child
Notifications
Privacy.

I. PEDAGOGICAL-PROVENANCE-UX.md

Define end-to-end:
Source → Method → TutorScope → TeachingAct → UI.

J. CONCEPT-TO-PRODUCTION-PLAN.md

Phân loại:

P0 FIRST VERTICAL SLICE
P1 CORE LEARNING
P2 SUBJECT SPECIALIZATION
P3 PARENT
P4 ADVANCED/OPTIONAL.

==================================================
22. ĐỀ XUẤT FIRST PRODUCTION VERTICAL SLICE
==================================================

Falsify nhưng ưu tiên kiểm tra flow:

05 Home
→ 07 Subject Home
→ 08 Camera
→ 09 Camera Confirm
→ 10 Tutor Start
→ 11 Diagnostic
→ 12 Problem Workspace
→ 13 Hint
→ 14 Your Turn
→ 15 Success
→ 16 Why This Method
→ 17 Source
→ 18 Review.

Đây phải chứng minh end-to-end:

curriculum grounded
+ camera safe
+ pedagogically constrained
+ provenance visible
+ assistance tracked
+ evidence generated
+ next action derived.

Không implement 38 screens cùng lúc.

==================================================
23. JIRA / CONFLUENCE
==================================================

Sau audit:

1. Search toàn bộ Jira WAL trước.
2. Map findings → existing issues.
3. MODIFY/MERGE ticket trước khi tạo mới.
4. Không tạo 1 ticket / screen.
5. Không tạo 1 ticket / subject.
6. Group theo architecture/workstream.

Candidate workstreams:

- Learner Context & Onboarding
- Learning Mission Home
- Learning Session
- Tutor Interaction System
- Interaction Surface System
- Subject Adapters
- Pedagogical Provenance
- Assessment
- Parent Experience
- Age Adaptive UX
- Local-first Library
- Notifications & Settings.

Confluence:
chỉ đưa stable product/UX truth.

Git:
technical/design source truth.

Jira:
execution control plane.

==================================================
24. CHECKPOINT FOUNDER
==================================================

Sau vòng audit đầu tiên, báo Founder ngắn gọn:

STATUS
- số concept KEEP
- MODIFY
- MERGE
- REMOVE
- DEFER

TOP 10 FINDINGS

K–12 FIT
- phù hợp tốt ở đâu
- concept nào đang overfit Grade4/5
- concept nào không phù hợp Grade1–2
- concept nào không đủ cho Grade10–12
- subject gaps

ARCHITECTURE
- interaction surfaces cuối cùng
- subject adapters
- age bands
- session/history model
- provenance model

FIRST SLICE
- screens được chọn
- lý do
- dependency
- acceptance criteria

JIRA
- ticket reused
- modified
- merged
- newly created

BLOCKERS
- chỉ blockers thực sự.

NEXT
- highest-value unblocked task.

==================================================
25. NGUYÊN TẮC CUỐI
==================================================

Đừng hỏi:

    "Làm thế nào để implement 38 màn hình?"

Hãy trả lời:

    "Học cùng SAM cần những learning environments nào
    để một học sinh từ lớp 1 đến lớp 12
    có thể học đúng chương trình,
    bằng interaction phù hợp với từng môn,
    được SAM hỗ trợ đúng mức,
    có nguồn và phương pháp minh bạch,
    và ngày càng tự học tốt hơn?"

38 concept screens là nguyên liệu để tìm câu trả lời đó.

Không phải câu trả lời cuối cùng.
