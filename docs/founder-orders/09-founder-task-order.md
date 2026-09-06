# FOUNDER TASK ORDER
# SAM ADAPTIVE LEARNING ACTIVITIES — OSS RESEARCH & REPO STUDY
# PRIORITY: P2 / LAST IN CURRENT ROADMAP
# MODE: DISCOVER → CLONE → STUDY → COMPARE → CHALLENGE → PROPOSE
# JIRA = EXECUTION MEMORY

==================================================
1. FOUNDER DIRECTION
==================================================

Tạo một workstream nghiên cứu riêng cho:

SAM Adaptive Learning Activities

Workstream này XẾP SAU CÙNG trong roadmap hiện tại.

Không được chen lên trước:
- UI/UX core;
- First Real Learning Experience;
- 38 concept → production backlog;
- vertical slice;
- subject-specific surfaces;
- shared learner/profile correctness;
- provenance;
- các blocker P0 khác.

Chỉ chạy khi các workstream ưu tiên cao hơn đã đủ ổn
hoặc khi Founder chủ động yêu cầu.

==================================================
2. MỤC TIÊU
==================================================

Founder muốn nghiên cứu:

- educational games;
- AI learning games;
- adaptive learning;
- quiz/activity engines;
- academy/course systems;
- gamified learning;
- learning-by-teaching;
- error detection games;
- simulations;
- interactive learning;
- camera/voice learning;
- curriculum-driven activities.

Mục tiêu KHÔNG phải:

“tìm nhiều game để nhét vào app.”

Mục tiêu là trả lời:

1. Activity/game nào thực sự tăng giá trị học tập?
2. Pattern nào có thể reuse cho SAM?
3. Pattern nào chỉ tăng engagement nhưng không tăng learning?
4. Cái gì Học cùng SAM có thể làm khác biệt hơn?
5. Có nên xây Activity Engine chung thay vì nhiều game riêng?
6. Workizen Personal Hub Game AI + Academy có thể reuse đến mức nào?

==================================================
3. JIRA
==================================================

Audit Jira trước.

Nếu chưa có representation phù hợp,
tạo workstream/epic:

SAM — Adaptive Learning Activities Research

Priority:

P2
hoặc
LAST / DEFERRED READY

theo convention Jira hiện tại.

Không đưa ticket vào active sprint/P0 queue.

Candidate work items:

ALA-01 OSS Discovery & Repo Shortlist
ALA-02 Workizen Hub Game AI Audit
ALA-03 Workizen Hub Academy Audit
ALA-04 Educational Activity Taxonomy
ALA-05 Repo Architecture Comparison
ALA-06 Pedagogy vs Gamification Review
ALA-07 Adaptive Activity Engine Proposal
ALA-08 Signature SAM Activity Concepts
ALA-09 Bounded POC Recommendation

Reuse WAL tickets hiện có nếu phù hợp.
Không duplicate.

==================================================
4. RESEARCH TRƯỚC, CODE SAU
==================================================

Không implement game mới trong phase đầu.

Phase đầu chỉ:

SEARCH
→ SHORTLIST
→ CLONE
→ RUN nếu hợp lý
→ READ CODE
→ STUDY ARCHITECTURE
→ STUDY UX
→ STUDY DATA MODEL
→ STUDY LICENSE
→ COMPARE
→ CHALLENGE.

Chỉ POC khi research cho thấy pattern có giá trị rõ.

==================================================
5. CLONE REPO
==================================================

Claude được phép tìm và clone các public OSS repo
có liên quan để nghiên cứu.

Không giới hạn vào repo đã biết.

Có thể nghiên cứu các nhóm:

A. EDUCATIONAL GAME ENGINES
B. QUIZ / PRACTICE SYSTEMS
C. ADAPTIVE LEARNING
D. FLASHCARD / SPACED REPETITION
E. LANGUAGE LEARNING
F. INTERACTIVE STEM
G. SIMULATION
H. AI TUTOR / AI EDUCATION
I. GAMIFICATION
J. COURSE / ACADEMY / LMS
K. CHILD-FRIENDLY LEARNING UX
L. VOICE / CAMERA LEARNING
M. LEARNING ANALYTICS
N. SKILL / MASTERY MODELING.

==================================================
6. REPO SELECTION CRITERIA
==================================================

Không clone hàng trăm repo vô ích.

Shortlist theo tiêu chí:

- source code thực;
- architecture đáng học;
- UX/activity pattern rõ;
- recent enough hoặc concept vẫn giá trị;
- license rõ;
- có khả năng chạy/audit;
- có relevance với SAM;
- không chỉ demo toy.

Mỗi repo ghi:

Repo
Purpose
License
Stack
Why Relevant
What To Study
What NOT To Copy
Status.

==================================================
7. PHẢI PHẢN BIỆN REPO
==================================================

Không viết report kiểu:

“repo này hay, có thể học hỏi.”

Với mỗi repo phải trả lời:

WHAT IT DOES WELL

WHAT IT OPTIMIZES FOR

WHAT PEDAGOGICAL ASSUMPTION IT MAKES

WHAT ENGAGEMENT MECHANICS IT USES

WHAT LEARNING EVIDENCE IT ACTUALLY CAPTURES

WHAT IT DOES POORLY

WHAT WOULD BE DANGEROUS TO COPY

WHAT FITS SAM

WHAT DOES NOT FIT SAM.

==================================================
8. PHÂN BIỆT GAME VÀ LEARNING ACTIVITY
==================================================

Bắt buộc phân loại:

ENTERTAINMENT GAME

GAMIFIED PRACTICE

LEARNING ACTIVITY

ASSESSMENT ACTIVITY

EXPLORATION

CREATIVE ACTIVITY

SIMULATION

REFLECTION

REAL-WORLD ACTIVITY.

Không gọi mọi interaction là “game”.

==================================================
9. NGUYÊN TẮC ĐÁNH GIÁ
==================================================

Một activity không được đánh giá tốt
chỉ vì:

- đẹp;
- nhiều animation;
- có XP;
- streak;
- badges;
- leaderboard;
- time spent;
- retention cao.

Đánh giá theo:

- learner thinking;
- independent attempt;
- retrieval practice;
- explanation;
- self-correction;
- transfer;
- evidence quality;
- hint dependency;
- difficulty adaptation;
- feedback quality;
- subject appropriateness.

==================================================
10. WORKIZEN PERSONAL HUB AUDIT
==================================================

Audit code thực của Workizen AI Personal Hub:

Game AI
Academy
Quiz
Canvas
Camera
OCR
Voice/STT/TTS
AI Router
Library
Progress
Notifications
related components.

Phân loại:

REUSE AS-IS
REUSE WITH ADAPTATION
EXTRACT SHARED
RESEARCH ONLY
NOT SUITABLE.

Không rebuild capability đã có nếu có thể reuse.

Nhưng generic Hub feature
không tự động phù hợp với child education.

==================================================
11. GAME AI AUDIT
==================================================

Đặc biệt trả lời:

Game AI hiện tại là:

- fixed games?
- generated game?
- prompt-driven?
- template-driven?
- data-driven?
- reusable renderer?
- adaptive?
- có learning evidence không?

Có thể biến thành:

Activity Renderer

thay vì Game Center hay không?

==================================================
12. ACADEMY AUDIT
==================================================

Đánh giá Academy hiện tại:

course
module
lesson
progress
quiz
content
navigation
storage
analytics.

Hỏi:

Có thể reuse thành:

SAM Learning Path
SAM Mission
Knowledge Adventure
Skill Journey

hay không?

Không mặc định bê nguyên LMS/course UX sang SAM.

==================================================
13. ACTIVITY PRIMITIVES
==================================================

Research xem có thể xây một tập nhỏ
reusable primitives thay vì hàng chục game riêng.

Candidate:

SELECT
MATCH
SORT
ORDER
GROUP
LABEL
CONNECT
FILL
BUILD
DRAW
EXPLAIN
SPEAK
LISTEN
COMPARE
SPOT_ERROR
PREDICT
OBSERVE
CLASSIFY
TIMELINE
MAP
SIMULATE
CREATE
REFLECT.

Không khóa taxonomy trước khi audit repo.

==================================================
14. CROSS-SUBJECT TEST
==================================================

Một primitive tốt phải thử được trên nhiều môn.

Ví dụ SORT:

Toán
→ phân loại phân số.

Tiếng Việt
→ từ loại.

Lịch sử
→ sắp xếp sự kiện.

Sinh học
→ phân loại sinh vật.

English
→ sentence ordering.

Nếu primitive chỉ phù hợp một domain,
ghi rõ subject-specific.

==================================================
15. ADAPTIVE ACTIVITY ENGINE
==================================================

Research architecture kiểu:

Learning Goal
+
Curriculum Context
+
Student State
+
Recent Evidence
+
Tutor Mode
+
Subject
+
Age
        ↓
Activity Selector
        ↓
Activity Template
        ↓
Content Binding
        ↓
Learner Interaction
        ↓
Evidence
        ↓
Next Action.

Đánh giá xem có hợp với SAM không.

Không quyết định architecture chỉ từ một repo.

==================================================
16. SIGNATURE SAM ACTIVITIES
==================================================

Bắt buộc nghiên cứu và phản biện ít nhất:

1. SPOT SAM'S MISTAKE
   “Bắt lỗi SAM”

2. TEACH SAM
   “Dạy lại SAM”

3. CHALLENGE ME
   Adaptive challenge.

4. KNOWLEDGE MISSION
   Curriculum + discovery mission.

5. CAMERA QUEST
   Learn from real world.

6. MYSTERY / DETECTIVE
   Evidence-based discovery.

7. WHAT IF?
   Counterfactual reasoning.

8. SCIENTIST MODE
   Predict → Observe → Evidence → Explain.

9. BUILD / CREATE
   Produce artifact.

10. FAMILY LEARNING CHALLENGE
    research only.

Không mặc định implement tất cả.

==================================================
17. “BẮT LỖI SAM”
==================================================

Research kỹ concept này.

Mục tiêu:

AI không luôn đóng vai người biết tất cả.

SAM cố tình đưa:

- lời giải sai;
- reasoning sai;
- nguồn không đủ;
- claim thiếu evidence;
- grammar error;
- timeline error;
- scientific misconception.

Learner phải:

detect
→ explain
→ correct
→ verify.

Phải đảm bảo intentional error
không bị ghi thành knowledge truth.

==================================================
18. “DẠY LẠI SAM”
==================================================

Research learning-by-teaching.

Learner giải thích lại concept cho SAM.

Đánh giá:

- spoken explanation;
- written explanation;
- key concept coverage;
- misconception detection;
- independent explanation;
- hint contamination.

Không đánh giá chỉ bằng keyword matching.

==================================================
19. CAMERA QUEST
==================================================

Research những pattern:

real-world scavenger hunt
object recognition learning
visual classification
measurement
environment observation
document/label reading.

Nhưng:

machine perception uncertain
không được tự biến thành LearningEvidence.

Giữ confirmation boundary.

==================================================
20. GAMIFICATION
==================================================

Research nhưng phản biện mạnh:

XP
streak
badges
levels
leaderboard
daily rewards
loot/progression.

Đánh giá:

cái nào hỗ trợ habit;
cái nào tạo addiction;
cái nào làm trẻ tối ưu điểm thay vì học.

Không recommend leaderboard/sibling competition
mặc định.

==================================================
21. DIFFERENTIATION
==================================================

Cuối research phải trả lời:

SAM khác các app có game ở đâu?

Không được trả lời:

“AI powered”
hoặc
“nhiều game”.

Đề xuất differentiation dựa trên combination:

Curriculum
+
Student State
+
Pedagogy
+
Adaptive Activity
+
Evidence
+
Camera/Voice
+
Vietnamese Knowledge
+
SAM personality.

==================================================
22. LICENSE
==================================================

Với mỗi repo:

license
commercial use
modification
distribution
copyleft implications
asset/data license.

AGPL/GPL/data-restricted repo:

research reference
không tự động copy code.

Nếu license unclear:
RESEARCH ONLY.

==================================================
23. SECURITY / CHILD SAFETY
==================================================

Repo bên ngoài có thể có:

analytics
ads
external tracking
accounts
chat
public content
UGC
third-party APIs.

Không reuse blindly.

Đánh giá:

child privacy
telemetry
account model
content safety
network dependency.

==================================================
24. DO NOT COPY UX BLINDLY
==================================================

Không clone aesthetic.

Không biến SAM thành:

Duolingo clone
Khan clone
Quizlet clone
game arcade clone.

Extract:

interaction pattern
state machine
feedback loop
data model
activity renderer
adaptive logic
learning evidence pattern.

==================================================
25. REQUIRED OUTPUT
==================================================

Tạo một report duy nhất:

docs/research/
SAM-ADAPTIVE-LEARNING-ACTIVITIES-OSS-REVIEW.md

Không tạo 10 report rời rạc.

Report gồm:

1. Executive verdict
2. Repo shortlist
3. Comparison matrix
4. Workizen Hub reuse
5. Activity taxonomy
6. Pedagogy vs gamification findings
7. Architecture patterns
8. Signature SAM activities
9. What to reject
10. Recommended POC
11. Jira recommendations.

==================================================
26. COMPARISON MATRIX
==================================================

Bắt buộc có bảng:

Repo
Category
Core Pattern
Adaptive?
Pedagogy
Evidence
Game Mechanic
Cross-subject
Offline
Reusable
License
SAM Fit
Main Risk.

==================================================
27. REPO CLONE EVIDENCE
==================================================

Không chỉ đọc README.

Với top repo phải có evidence:

- cloned;
- important directories inspected;
- key classes/modules identified;
- architecture path;
- activity data model;
- state/progress model;
- content model;
- screenshots/runtime nếu có thể chạy;
- findings linked to exact source files.

==================================================
28. RESEARCH SIZE
==================================================

Target:

broad discovery:
20–40 candidates.

serious shortlist:
8–15 repos.

deep study:
5–8 repos.

Không ép đủ số nếu quality thấp.

==================================================
29. CHALLENGE FOUNDER
==================================================

Founder đang giả định:

“Game/Academy có thể tạo khác biệt.”

Claude phải cố gắng FALSIFY giả định này.

Ví dụ có thể kết luận:

- game không phải moat;
- Academy không phù hợp;
- camera/voice + adaptive mission mạnh hơn;
- creative artifact mạnh hơn quiz;
- game chỉ nên là một surface.

Được phép kết luận như vậy.

==================================================
30. RECOMMENDATION FORMAT
==================================================

Kết luận từng hướng:

ADOPT
ADAPT
POC
RESEARCH LATER
REJECT.

Mỗi recommendation phải có:

Evidence
Reason
SAM Fit
Risk
Implementation Cost
Expected Learning Value.

==================================================
31. BOUNDED POC
==================================================

Nếu research đủ mạnh,
đề xuất tối đa 3 POC.

Ưu tiên candidate:

Spot SAM's Mistake
Teach SAM
Adaptive Mission / Challenge.

Không implement trước khi
roadmap priority cho phép.

Nếu đã tới lượt P2 này
và không có Founder Gate,
Claude có thể làm bounded POC.

==================================================
32. POC ACCEPTANCE
==================================================

POC phải dùng:

real curriculum content
+
real learner state/evidence model nếu có.

Không dùng random trivia demo.

Founder phải nhìn thấy:

same content
+
different learner state
→ different activity/difficulty/help.

==================================================
33. KHÔNG LÀM
==================================================

Không:

- clone hàng trăm repo;
- copy code license-risk;
- build Game Center ngay;
- tạo 50 mini game;
- thêm XP/streak trước learning model;
- tạo full LMS;
- tạo social leaderboard;
- dùng engagement như learning proof;
- dừng ở README summary.

==================================================
34. JIRA EXECUTION
==================================================

Log toàn bộ workstream vào Jira ngay bây giờ.

Nhưng set:

P2 / LAST PRIORITY / DEFERRED READY.

Giữ dependencies với P0/P1 hiện tại.

Không bắt đầu implementation
cho tới khi các higher-priority dependencies hoàn tất.

Research discovery nhẹ có thể chuẩn bị trước
nếu không làm gián đoạn P0.

==================================================
35. FINAL CHECKPOINT
==================================================

Khi workstream tới lượt chạy, báo Founder:

- repos đã nghiên cứu;
- repo đáng học nhất;
- repo bị loại;
- Hub Game AI reuse verdict;
- Hub Academy reuse verdict;
- proposed activity primitives;
- signature SAM features;
- adaptive engine verdict;
- gamification verdict;
- child-safety/license risks;
- max 3 POC recommendation;
- Jira next actions.

==================================================
36. NORTH STAR
==================================================

MỤC TIÊU KHÔNG PHẢI:

“TRẺ CHƠI GAME NHIỀU HƠN.”

MỤC TIÊU LÀ:

“TRẺ SUY NGHĨ NHIỀU HƠN,
TỰ LÀM NHIỀU HƠN,
GIẢI THÍCH TỐT HƠN,
VÀ DẦN CẦN SAM ÍT HƠN.”

GAME LÀ MỘT LEARNING SURFACE.

KHÔNG PHẢI SẢN PHẨM.

RESEARCH → CHALLENGE → PROVE → THEN BUILD.
