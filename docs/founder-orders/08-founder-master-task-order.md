# FOUNDER MASTER TASK ORDER
# HỌC CÙNG SAM
## NGHIÊN CỨU UX K–12 DỰA TRÊN TOÀN BỘ DỮ LIỆU SGK
## + PHẢN BIỆN 38 CONCEPT
## + TẬN DỤNG NĂNG LỰC WORKIZEN HUB
## + SHARED DEVICE / MULTI-PROFILE
## + MÔ HÌNH KIẾM TIỀN

TRẠNG THÁI:
XẾP HÀNG — TỰ ĐỘNG CHẠY SAU KHI OCR / INGESTION TOÀN BỘ CORPUS K–12 HOÀN TẤT.

MỨC ƯU TIÊN:
P0 — NGHIÊN CỨU SẢN PHẨM / UX / KIẾN TRÚC.

==================================================
0. MỤC TIÊU CỦA FOUNDER
==================================================

Học cùng SAM hiện đã có:

- corpus SGK K–12 đang OCR / ingestion;
- 38 concept AI-first trong repo;
- Curriculum Graph / Content Graph;
- Concept / SkillCase / Method;
- TutorScope;
- TeachingAct;
- LearningEvidence;
- Student Knowledge State;
- LearningSession;
- nghiên cứu chương trình AI chính thức;
- nhiều capability có sẵn từ Workizen AI Personal Hub;
- yêu cầu nhiều trẻ dùng chung một thiết bị;
- định hướng Student Free / Teacher Free / Parent Premium.

Founder KHÔNG muốn production UI được xây tiếp chủ yếu từ:

- trực giác;
- generic LMS;
- generic chatbot;
- hình concept đẹp;
- giả định về từng môn học;
- assumption rằng tất cả môn đều học giống Toán.

Pipeline đúng phải là:

TOÀN BỘ CORPUS SGK
    ↓
BẰNG CHỨNG CHƯƠNG TRÌNH
    ↓
ĐẶC THÙ TỪNG MÔN
    ↓
LOẠI HOẠT ĐỘNG HỌC
    ↓
PHƯƠNG PHÁP SƯ PHẠM
    ↓
INTERACTION SURFACE
    ↓
LUỒNG UX
    ↓
PHẢN BIỆN 38 CONCEPT
    ↓
KẾ HOẠCH PRODUCTION.

38 concept chỉ là:

DESIGN INTENT / UX REFERENCE.

KHÔNG phải production spec.

==================================================
1. ĐIỀU KIỆN KÍCH HOẠT TASK
==================================================

Nhận Task Order ngay bây giờ.

NHƯNG:

KHÔNG chạy phần audit chính cho tới khi OCR / ingestion
toàn bộ corpus hiện tại hoàn tất.

Tiếp tục ingestion đang chạy.

KHÔNG dừng ingestion giữa chừng chỉ để làm UX audit.

Task chỉ bắt đầu khi có checkpoint cuối gồm:

- số sách đã xử lý / tổng số sách;
- SUCCESS;
- PARTIAL;
- FAILED;
- coverage lớp 1–12;
- coverage theo môn;
- SourceDocument;
- Lesson;
- Section;
- ContentUnit;
- Exercise / Activity nếu có;
- semantic type distribution;
- SOURCE_EXPLICIT;
- SOURCE_DEMONSTRATED;
- INFERRED nếu có;
- lỗi OCR;
- lỗi layout;
- unknown;
- unmapped;
- structural coverage;
- semantic coverage;
- ingestion version / commit.

QUAN TRỌNG:

100% FILE ĐÃ XỬ LÝ
!=
100% KIẾN THỨC ĐÃ HIỂU.

Phải báo riêng:

STRUCTURAL COVERAGE

và:

SEMANTIC COVERAGE.

==================================================
2. KHÓA SNAPSHOT CORPUS
==================================================

Ngay khi ingestion hoàn tất:

khóa một snapshot để dùng cho toàn bộ nghiên cứu.

Ghi rõ:

- timestamp;
- ingestion commit/version;
- số sách;
- success;
- partial;
- failed;
- số lớp;
- số môn;
- ContentUnit;
- Exercise/Activity;
- semantic model version;
- knowledge model version nếu applicable.

5 báo cáo phải dùng chung snapshot này.

Không silent-update evidence giữa chừng.

==================================================
3. THỨ TỰ NGUỒN BẰNG CHỨNG
==================================================

Ưu tiên:

1. SGK thật đã ingest.
2. SourceDocument / Lesson / Section / ContentUnit.
3. Exercise / Activity.
4. Curriculum Graph.
5. Concept / SkillCase / Method.
6. nguồn chương trình chính thức.
7. chương trình AI chính thức.
8. ADR / architecture hiện tại.
9. 38 concept.
10. research hiện có.
11. external research nếu cần.

Mọi kết luận quan trọng phải gắn loại:

SOURCE_EVIDENCE
ARCHITECTURE_EVIDENCE
EXTERNAL_RESEARCH
INFERENCE
HYPOTHESIS
UNKNOWN.

Không biến inference thành sự thật chương trình.

==================================================
4. PHÂN TÍCH CORPUS TRƯỚC UX
==================================================

Không bắt đầu bằng việc nhìn 38 màn hình.

Trước tiên trả lời:

SGK K–12 thực sự yêu cầu học sinh làm những gì?

Tìm các pattern:

- đọc;
- viết;
- nghe;
- nói;
- quan sát;
- nhận biết;
- so sánh;
- phân loại;
- nối;
- sắp xếp;
- điền;
- tính toán;
- giải bài;
- giải thích;
- chứng minh;
- thực hành;
- thí nghiệm;
- đo;
- biểu đồ;
- bảng;
- bản đồ;
- phân tích nguồn;
- viết luận;
- thảo luận;
- trình bày;
- dự án;
- thiết kế;
- sáng tạo;
- biểu diễn;
- phản tư.

Không cố biến mọi hoạt động trong SGK thành app feature.

==================================================
5. PHÂN TÍCH THEO NHÓM LỚP
==================================================

Phân tích ít nhất:

Lớp 1–2
Lớp 3–5
Lớp 6–9
Lớp 10–12.

Với từng nhóm:

- mật độ chữ;
- độ dài instruction;
- phụ thuộc hình ảnh;
- nhu cầu đọc;
- nhu cầu viết;
- vai trò giọng nói;
- mức tự chủ;
- độ phức tạp bài tập;
- mức trừu tượng;
- dữ liệu/nguồn;
- loại assessment;
- mức khác nhau giữa các môn.

Từ đó mới đề xuất UX.

Không chỉ dựa trên generic age theory.

==================================================
6. PHÂN TÍCH THEO TỪNG MÔN
==================================================

Phân tích tất cả môn thực sự có trong corpus.

Ít nhất nếu dữ liệu có:

- Toán;
- Tiếng Việt;
- Ngữ văn;
- Ngoại ngữ;
- Tự nhiên và Xã hội;
- Khoa học;
- Khoa học tự nhiên;
- Vật lý;
- Hóa học;
- Sinh học;
- Lịch sử;
- Địa lý;
- GDCD / nội dung xã hội liên quan;
- Tin học;
- Công nghệ;
- Âm nhạc;
- Mỹ thuật;
- Hoạt động trải nghiệm;
- Giáo dục AI;
- môn khác nếu corpus có.

Không ép cấu trúc môn theo concept cũ.

Ví dụ:

KHTN 6–9 là integrated subject
thì UX phải phản ánh đúng context đó.

Với mỗi môn xác định:

- mục tiêu học;
- activity pattern;
- exercise pattern;
- response type;
- SkillCase;
- LearningEvidence;
- TeachingAct;
- surface phù hợp;
- khác biệt theo độ tuổi;
- concept hiện tại có phù hợp không;
- surface còn thiếu;
- Hub capability nào có thể reuse.

==================================================
7. PHẢN BIỆN TAXONOMY HOẠT ĐỘNG
==================================================

Kiểm tra taxonomy hiện tại:

A. Problem Solving
B. Scientific Investigation
C. Reading / Argument / Source Reasoning
D. Spatial / Data Reasoning
E. Language
F. Assessment
G. Creative / Performance.

Không assume đúng.

Nếu corpus cho thấy cần:

MERGE
SPLIT
RENAME
ADD
REMOVE

thì đề xuất.

==================================================
8. PHÂN TÍCH RESPONSE TYPE
==================================================

Kiểm tra candidate taxonomy:

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

Không force.

Tìm loại khác nếu corpus có.

Nguyên tắc:

SAME CONCEPT
!=
SAME SKILL
!=
SAME EVIDENCE.

Ví dụ:

nhận biết
giải thích
lựa chọn
áp dụng
viết
sửa
chuyển giao

có thể là SkillCase khác nhau.

==================================================
9. AUDIT LẠI 38 CONCEPT
==================================================

Sau corpus analysis mới re-audit 38 màn.

Mỗi màn phải có:

- mục đích hiện tại;
- learning job;
- bằng chứng corpus;
- phù hợp grade nào;
- phù hợp môn nào;
- phù hợp activity nào;
- dữ liệu cần;
- LearningEvidence impact;
- provenance;
- Hub reuse;
- rủi ro.

Decision:

KEEP
MODIFY
MERGE
SPLIT
REPLACE
DEFER.

Không giữ kết luận audit cũ nếu full corpus falsify.

==================================================
10. SCREEN != SURFACE != STATE
==================================================

Không assume 38 ảnh = 38 production route.

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

có thể chỉ là:

1 Learning Workspace
+
nhiều pedagogical state.

Mục tiêu:

- giữ continuity;
- ít chuyển màn;
- không mất learning context;
- giảm cognitive switching.

==================================================
11. KIẾN TRÚC INTERACTION CẦN PHẢN BIỆN
==================================================

Falsify:

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
TutorScope
    ↓
Surface Resolver
    ↓
Learning Surface
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

Candidate surface:

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

Minimize theo corpus.

==================================================
12. LUỒNG HỌC PHẢI ĐƯỢC SUY RA TỪ ACTIVITY
==================================================

Không mặc định:

Home → Subject → Chat.

Phản biện ít nhất các flow:

GIẢI BÀI
Home
→ bài học/bài tập
→ Workspace
→ tự làm
→ probe
→ hint nếu cần
→ tự làm lại
→ evidence
→ review.

ĐỌC HIỂU
Text
→ Reader
→ đọc/quan sát
→ câu hỏi
→ evidence/source
→ trả lời
→ feedback
→ reflection.

VIẾT / ESSAY
Đề bài
→ hiểu yêu cầu
→ brainstorm
→ outline
→ học sinh viết
→ SAM phản hồi
→ học sinh sửa
→ reflection.

KHOA HỌC
Hiện tượng/câu hỏi
→ quan sát
→ giả thuyết
→ thí nghiệm/model/data
→ phân tích
→ giải thích
→ kết luận.

LỊCH SỬ
Nguồn/sự kiện
→ context
→ quan sát
→ chronology
→ compare evidence
→ claim
→ explanation.

ĐỊA LÝ
Map/Data
→ locate
→ inspect
→ compare
→ spatial reasoning
→ conclusion.

SÁNG TẠO / BIỂU DIỄN
Prompt
→ create/perform
→ artifact/recording
→ feedback
→ reflection.

GIÁO DỤC AI
derive trực tiếp từ chương trình chính thức.

==================================================
13. TƯỜNG MINH NGUỒN VÀ PHƯƠNG PHÁP
==================================================

Invariant:

NO TEACHING WITHOUT PEDAGOGICAL PROVENANCE.

Mọi academic TeachingAct phải trả lời được:

- đang học kiến thức gì;
- thuộc lớp/môn/bài nào;
- tại sao SAM chọn hoạt động này;
- Method nào;
- nguồn nào;
- trang nào;
- SOURCE_EXPLICIT / SOURCE_DEMONSTRATED / SAM_INFERRED;
- tại sao TutorScope cho phép.

Nguồn phải visible từ đầu interaction.

Không đợi tới màn Source cuối cùng.

==================================================
14. UX THEO ĐỘ TUỔI
==================================================

Không tạo 12 app.

Mục tiêu:

ONE DESIGN SYSTEM
+
AGE-ADAPTIVE POLICY.

Phân tích:

Lớp 1–2
Lớp 3–5
Lớp 6–9
Lớp 10–12.

Khác nhau ở:

- typography;
- density;
- button size;
- mascot;
- voice;
- text;
- terminology;
- navigation;
- explanation depth;
- autonomy;
- parent involvement;
- animation;
- reward.

Không dùng XP/streak/ranking như proxy của mastery.

==================================================
15. SHARED DEVICE / MULTI-PROFILE
==================================================

Founder requirement:

một gia đình có thể chỉ có một điện thoại/tablet.

Model:

ONE DEVICE
    ↓
FAMILY
    ├── Parent
    ├── Learner A
    ├── Learner B
    └── Learner C.

Invariant:

DEVICE != LEARNER
ACCOUNT != LEARNER
PARENT != LEARNER.

Không bắt trẻ có email/account riêng.

Shared:

- app;
- curriculum;
- Knowledge Pack;
- Content Store.

Per learner:

- profile;
- grade;
- timetable;
- sessions;
- evidence;
- knowledge state;
- review schedule;
- recommendation.

Critical:

NO CROSS-LEARNER EVIDENCE CONTAMINATION.

Profile switch phải switch toàn bộ educational context.

Không sibling ranking.

Thay:

"So sánh nhanh"

bằng:

"Tình hình các con".

==================================================
16. TẬN DỤNG WORKIZEN AI PERSONAL HUB
==================================================

Audit repo Hub thực tế.

Không chỉ dùng list Founder đưa.

Kiểm tra ít nhất:

- OCR;
- Document Scanner;
- Camera;
- QR / Barcode;
- STT;
- TTS;
- Voice;
- Smart Canvas;
- AI Provider Router;
- Free AI Provider;
- BYOK;
- Ollama/local AI;
- Login;
- Register;
- Account;
- Backup;
- Restore;
- Storage;
- Sync;
- AI Usage;
- Quota;
- Library;
- Document Intelligence;
- PDF ingestion;
- Search;
- Mindmap;
- Presentation;
- Infographic;
- Summary;
- Document Q&A;
- Notifications;
- Settings;
- Localization;
- Analytics;
- Crash Reporting;
- Sharing;
- Export;
- Deep Link;
- Design System.

Phân loại:

REUSE AS-IS
REUSE + ADAPTER
EXTRACT SHARED
POC
REJECT.

==================================================
17. NGUYÊN TẮC REUSE HUB
==================================================

Không:

copy code Hub
→ rename
→ SAM.

Ưu tiên:

WORKIZEN SHARED CAPABILITY
    ↓
EDUCATION SAFETY ADAPTER
    ↓
HỌC CÙNG SAM.

Reuse hạ tầng tối đa.

Xây mới phần tạo nên “bộ não giáo dục”:

- Curriculum;
- Knowledge Graph;
- SkillCase;
- Method;
- TutorScope;
- TeachingAct;
- LearningEvidence;
- Student Knowledge State;
- Next Best Learning Action;
- Pedagogical Provenance.

==================================================
18. CHILD SAFETY
==================================================

Generic Hub capability không tự động phù hợp trẻ em.

Mỗi capability phải classify:

ALLOW
ADAPT
AGE-GATED
PARENT-GATED
SANITIZE
DISABLE
RESEARCH.

Audit đặc biệt:

- generic chat;
- external links;
- ads;
- analytics;
- provider data;
- imported documents;
- voice;
- export/share;
- cloud processing;
- notifications.

AI Router không có pedagogical authority.

OCR không được tự tạo LearningEvidence.

==================================================
19. LOCAL-FIRST
==================================================

Giữ định hướng:

SHARED LOCAL KNOWLEDGE
+
PER-LEARNER LOCAL STATE
+
OPTIONAL CLOUD INFERENCE / SYNC.

Không duplicate Knowledge Pack cho từng trẻ.

UX phải hoạt động hợp lý khi:

- offline;
- mạng yếu;
- máy Android cũ;
- một thiết bị dùng nhiều trẻ.

==================================================
20. TUTOR MODE != ASSESSMENT MODE
==================================================

Tutor/Practice:

SAM có thể:
- hỏi;
- probe;
- hint;
- scaffold;
- giải thích.

Assessment:

assistance phải restricted/disabled tùy policy.

Independent evidence phải được bảo toàn.

Không để hint trong assessment làm evidence giả.

==================================================
21. PROGRESS
==================================================

Không dùng:

XP
streak
leaderboard
top %
completion %

như Learning Truth.

Ưu tiên:

- estimated mastery;
- coverage;
- confidence;
- independent performance;
- assisted performance;
- self-correction;
- hint-depth reduction;
- retention;
- transfer;
- review due.

Unobserved != failed.
Unobserved != mastered.

==================================================
22. GIÁO DỤC AI
==================================================

Màn AI Learning phải derive từ chương trình AI chính thức.

Không biến thành generic course:

AI
→ ML
→ Deep Learning
→ Prompt Engineering.

Dùng official YCCĐ và 4 strand đã ingest.

==================================================
23. MÔ HÌNH KINH DOANH
==================================================

FOUNDER DIRECTION:

HỌC SINH
→ MIỄN PHÍ.

GIÁO VIÊN
→ MIỄN PHÍ.

PHỤ HUYNH
→ CÓ LỚP TRẢ PHÍ / PREMIUM.

Học sinh và giáo viên có thể sử dụng phiên bản có quảng cáo
nếu phù hợp về pháp lý, privacy, child safety và UX.

Đây là business hypothesis cần nghiên cứu và phản biện.

Không hard-code paywall trước khi audit.

==================================================
24. STUDENT FREE
==================================================

Founder muốn học sinh được tiếp cận SAM miễn phí.

Research phạm vi core free:

- Home;
- môn học;
- curriculum;
- basic Tutor;
- Camera Tutor;
- practice;
- review;
- quiz;
- Learning Map;
- basic voice;
- local Knowledge Pack;
- history;
- basic learning tools.

Không tạo tình trạng:

"Free"

nhưng thực tế không học được nếu không trả tiền.

Cloud AI có cost phải model riêng.

Nghiên cứu:

LOCAL
+
FREE PROVIDER
+
LOW-COST PROVIDER
+
FAIR USAGE
+
ADS
+
OPTIONAL PREMIUM CAPACITY.

==================================================
25. TEACHER FREE
==================================================

Teacher Mode là persona riêng.

FOUNDER DIRECTION:

GIÁO VIÊN ĐƯỢC DÙNG MIỄN PHÍ.

Nghiên cứu use case:

- tra chương trình;
- tra nguồn;
- soạn bài;
- tạo practice;
- tạo quiz;
- worksheet;
- giải thích nhiều cách;
- tài liệu;
- OCR/scan;
- Smart Canvas;
- presentation;
- mindmap;
- QR tài nguyên;
- AI curriculum support.

Không tự động biến SAM thành full LMS.

Teacher Free có thể là acquisition channel:

Teacher
→ Student
→ Parent.

Nhưng phải research/falsify.

==================================================
26. PARENT BASIC + PARENT PREMIUM
==================================================

Không khóa toàn bộ Parent Mode.

Một số tính năng phụ huynh phải basic/free:

- tạo learner;
- đổi profile;
- consent;
- privacy;
- delete/export data;
- account recovery;
- basic family settings;
- parental safety settings.

Premium candidate:

- Parent Daily Brief;
- Weekly Learning Insight;
- “Tối nay tôi nên giúp con điều gì?”;
- Parent Coach;
- giải thích điểm yếu SkillCase;
- independent vs assisted insight;
- kế hoạch ôn;
- xu hướng nhiều tuần;
- timetable-aware recommendation;
- assessment insight;
- multi-child advanced overview;
- proactive recommendation;
- automatic backup/sync;
- family multi-device convenience.

Premium phải bán:

INSIGHT
+
COACHING
+
CONVENIENCE.

Không bán surveillance.

==================================================
27. QUẢNG CÁO
==================================================

Founder cho phép Student Free và Teacher Free có quảng cáo.

NHƯNG:

quảng cáo trong Student Mode là:

CHILD SAFETY
+
PRIVACY
+
LEGAL
+
UX GATE.

Phải nghiên cứu:

- chính sách trẻ em;
- personalized vs non-personalized ads;
- consent;
- ad SDK collection;
- Google Play;
- Apple;
- quy định Việt Nam;
- age band;
- teacher context.

Baseline ưu tiên để nghiên cứu:

CONTEXTUAL / NON-PERSONALIZED ADS

thay vì:

BEHAVIORAL TARGETING TRẺ EM.

Không assume personalized ads được phép.

==================================================
28. KHÔNG CHÈN QUẢNG CÁO VÀO LEARNING LOOP
==================================================

Strong Founder hypothesis:

KHÔNG để quảng cáo cắt ngang việc học.

Ví dụ vùng không quảng cáo:

Camera
→ Confirm
→ Diagnostic
→ Attempt
→ Hint
→ Your Turn
→ Success.

Cũng ưu tiên NO-AD trong:

- Assessment;
- Essay;
- Voice interaction;
- Reading;
- Problem solving;
- Science investigation.

Không dùng:

“Xem quảng cáo để nhận hint”
“Xem quảng cáo để xem đáp án”
“Xem quảng cáo để SAM giải tiếp”
“Xem quảng cáo để giữ streak”.

Quảng cáo không được thao túng pedagogy.

==================================================
29. VỊ TRÍ QUẢNG CÁO CẦN NGHIÊN CỨU
==================================================

Có thể nghiên cứu:

- sau khi hoàn thành session;
- Home transition;
- Library browsing;
- Teacher utility areas;
- một số non-learning transition;
- sponsored educational resources nếu cực kỳ minh bạch.

Không assume chỗ nào cũng hợp lý.

Đo:

- interruption;
- trust;
- accidental click;
- age appropriateness;
- learning disruption;
- parent perception.

Invariant:

SPONSORED CONTENT
!=
CURRICULUM RECOMMENDATION.

SAM không được giả quảng cáo thành lời khuyên học tập.

==================================================
30. PARENT PREMIUM CÓ THỂ REMOVE ADS
==================================================

Research hypothesis:

Parent Premium
→ tất cả learner profile trong family được AD-FREE.

Candidate value proposition:

FREE STUDENT
+ FREE TEACHER
+ safe ads

vs

PARENT PREMIUM
→ Parent Coach
→ insight sâu
→ family convenience
→ cloud backup/sync
→ có thể AD-FREE toàn family.

Không chốt pricing trong task này.

==================================================
31. ĐƠN VỊ SUBSCRIPTION
==================================================

Nghiên cứu subscription theo:

FAMILY

thay vì mặc định:

PER CHILD.

Ví dụ:

Parent Premium
    ↓
Family
    ├── Bé A
    ├── Bé B
    └── Bé C.

Không ép mỗi trẻ mua một subscription
nếu chưa có evidence economics.

Free student profile vẫn phải hoạt động
khi Parent Premium hết hạn.

==================================================
32. AI COST / UNIT ECONOMICS
==================================================

Free Student + Free Teacher yêu cầu cost model thực tế.

Ước tính cost theo:

- learner/day;
- session;
- OCR;
- STT;
- TTS;
- cloud LLM;
- document processing;
- teacher generation.

So sánh:

ON-DEVICE
LOCAL
FREE PROVIDER
LOW-COST MODEL
BYOK
PREMIUM MODEL.

Tận dụng AI Usage / Provider Router của Hub.

Routing hypothesis:

LOCAL / DETERMINISTIC FIRST
    ↓
FREE / CHEAP WHEN SUFFICIENT
    ↓
CLOUD MODEL WHEN NEEDED.

Nhưng cost không được override:

TutorScope
Pedagogy
Provenance
Child Safety.

==================================================
33. MONETIZATION KHÔNG ĐƯỢC THAY ĐỔI LEARNING TRUTH
==================================================

Invariant:

PAYMENT STATUS
!=
LEARNING TRUTH.

Premium không được làm:

- mastery cao hơn;
- evidence khác;
- assessment dễ hơn;
- kết luận tốt hơn;
- curriculum khác giả tạo.

Student Knowledge State độc lập subscription.

AD VIEW
không bao giờ là LearningEvidence.

==================================================
34. BUSINESS FUNNEL CẦN NGHIÊN CỨU
==================================================

Candidate funnel:

TEACHER FREE
    ↓
STUDENT FREE
    ↓
SAM TẠO GIÁ TRỊ HỌC THẬT
    ↓
PARENT NHẬN BASIC INSIGHT
    ↓
PARENT PREMIUM
    ↓
PARENT COACH + ADVANCED INSIGHT + CONVENIENCE.

Hoặc:

STUDENT
→ PARENT.

Phải falsify.

Không cố tình làm Student Free tệ đi để ép Parent trả tiền.

==================================================
35. NGUYÊN TẮC KINH DOANH
==================================================

Không tối ưu:

MORE SCREEN TIME
→ MORE ADS
→ MORE REVENUE.

Đây là incentive xấu cho giáo dục.

Desired:

BETTER LEARNING
→ PARENT THẤY GIÁ TRỊ THẬT
→ PARENT TỰ NGUYỆN PREMIUM.

Không tối ưu:

- addiction;
- streak;
- ad impressions;
- unnecessary chat;
- time-in-app.

Ưu tiên:

- tiến bộ;
- độc lập;
- retention;
- transfer;
- useful parent guidance;
- trust.

==================================================
36. CÂU HỎI PHẢN BIỆN BẮT BUỘC
==================================================

Phản biện ít nhất:

F1. Có thực sự cần 38 production screens?
F2. Một Subject Home có đủ mọi môn?
F3. Chat đủ cho mọi môn?
F4. Mỗi môn cần UI riêng hoàn toàn?
F5. Grade = mastery?
F6. Timetable = exact lesson?
F7. Correct after hint = independent?
F8. Transcript = LearningEvidence?
F9. Quiz = Assessment?
F10. Curriculum Graph chứa UI?
F11. Một UI dùng lớp 1–12?
F12. XP/streak = progress?
F13. sibling ranking có ích?
F14. History = timeline?
F15. Geography = map?
F16. Physics/Chemistry = simulation?
F17. Essay tutor nên viết bài mẫu trước?
F18. AI Learning concept khớp official curriculum?
F19. Mọi Hub capability đều nên sang SAM?
F20. Canvas cần mọi môn?
F21. OCR = educational truth?
F22. LLM có pedagogical authority?
F23. Device = learner?
F24. Mỗi learner cần account?
F25. Mỗi learner cần Knowledge Pack riêng?
F26. Mỗi môn cần chatbot memory riêng?
F27. Citation chỉ cần cuối câu trả lời?
F28. 100% OCR = hiểu 100% curriculum?

BUSINESS:

F29. Student hoàn toàn free có bền vững?
F30. Teacher hoàn toàn free có hợp lý?
F31. Parent Mode toàn bộ nên paywall?
F32. Ads có đủ giúp funding Student Free?
F33. Personalized ads cho trẻ có được phép/phù hợp?
F34. Ads trong Tutor session có chấp nhận được?
F35. Rewarded ads đổi hint/answer có phù hợp giáo dục?
F36. Parent Premium nên remove ads toàn family?
F37. Có cần subscription per child?
F38. Teacher Free có tạo acquisition loop?
F39. Dashboard phụ huynh có đủ để bán?
F40. Parent Coach có phải giá trị paid mạnh hơn raw analytics?
F41. Free AI cloud có bền vững?
F42. Hub free provider giảm COGS thực tế bao nhiêu?

Không hard-code câu trả lời.
Dùng evidence.

==================================================
37. OUTPUT — CHỈ TẠO ĐÚNG 5 FILE
==================================================

Tất cả tại:

docs/design/

Không tạo thêm hàng loạt report nhỏ.

--------------------------------------------------
FILE 1
01-CURRICULUM-UX-EVIDENCE-REPORT.md
--------------------------------------------------

Nội dung:

- final corpus snapshot;
- structural coverage;
- semantic coverage;
- grade distribution;
- subject distribution;
- lessons;
- sections;
- ContentUnits;
- semantic types;
- activity;
- exercises;
- response patterns;
- OCR/layout gaps;
- unknown;
- cross-grade findings.

Trọng tâm:

SGK K–12 thực tế yêu cầu học sinh làm gì?

--------------------------------------------------
FILE 2
02-K12-SUBJECT-UX-FIT-REPORT.md
--------------------------------------------------

Mỗi môn:

- evidence;
- grade coverage;
- learning goal;
- activity;
- exercise;
- response;
- SkillCase;
- TeachingAct;
- LearningEvidence;
- interaction surface;
- age difference;
- concept fit;
- missing UX;
- Hub reuse;
- quảng cáo có phù hợp context đó không;
- unknown.

Có matrix:

GRADE BAND
× SUBJECT
× ACTIVITY
× RESPONSE
× SURFACE
× TEACHING ACT
× EVIDENCE
× AGE POLICY.

--------------------------------------------------
FILE 3
03-38-CONCEPT-SCREEN-REAUDIT.md
--------------------------------------------------

Đủ 38 màn.

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
Ad Eligibility
Risk.

Ad Eligibility:

NEVER
POSSIBLE_TRANSITION
PARENT_PREMIUM
RESEARCH.

Cuối file:

KEEP
MODIFY
MERGE
SPLIT
REPLACE
DEFER

và:

proposed production screen count
proposed surface count
screen→state changes
missing surface
unsupported concept.

--------------------------------------------------
FILE 4
04-PROPOSED-LEARNING-UX-AND-FLOWS.md
--------------------------------------------------

Đây là solution report.

Bao gồm:

- final IA;
- Learning Shell;
- Home;
- Subject;
- Surface Resolver;
- Age Policy;
- provenance;
- Camera;
- Voice;
- Tutor;
- Review;
- Quiz;
- Assessment;
- Parent;
- Shared Device;
- Multi-profile;
- Teacher;
- Library;
- Notifications;
- Settings;
- Hub reuse.

Bắt buộc vẽ flow:

Onboarding
Learner Setup
Shared Device
Home
Subject
Problem Solving
Camera Tutor
Reading
Writing
Essay
Science
History
Geography
Creative/Performance
AI Education
Quiz
Assessment
Review
Voice
Teacher
Parent
Multi-child.

Bổ sung business flow:

STUDENT FREE
TEACHER FREE
PARENT BASIC
PARENT PREMIUM
AD-SAFE TRANSITION
FAMILY SUBSCRIPTION
AD-FREE FAMILY.

Mỗi learning flow dùng:

ENTRY
→ CONTEXT
→ SURFACE
→ TEACHING ACT
→ LEARNER ACTION
→ EVIDENCE
→ NEXT ACTION.

--------------------------------------------------
FILE 5
05-FOUNDER-RECOMMENDATIONS-AND-CHALLENGES.md
--------------------------------------------------

Đây là report phản biện mạnh nhất.

Phải nói rõ:

A. Founder/GPT assumption nào đúng.

B. assumption nào sai.

C. assumption nào chưa đủ evidence.

D. 38 concept overfit chỗ nào.

E. corpus làm thay đổi sản phẩm ra sao.

F. môn nào cần specialized UX.

G. môn nào reuse surface.

H. màn nào nên merge.

I. màn nào replace.

J. surface nào thiếu.

K. grade band yếu nhất.

L. data gaps.

M. child safety risk.

N. Hub reuse recommendation.

O. shared-device implications.

P. local-first implications.

Q. business model recommendation.

R. Student Free scope.

S. Teacher Free scope.

T. Parent Basic scope.

U. Parent Premium value.

V. advertising recommendation.

W. ad-free family hypothesis.

X. subscription unit.

Y. AI COGS model.

Z. free-provider strategy.

AA. cái gì TUYỆT ĐỐI không nên monetization.

AB. experiment cần chạy.

AC. risk nếu implement 38 concept ngay.

AD. production priority.

AE. những thứ chưa nên build.

AF. recommended First Vertical Slice.

AG. Founder decision còn cần sau này.

==================================================
38. ĐÁNH GIÁ LẠI WAL-108 SAU 5 REPORT
==================================================

Không bắt đầu major production implementation WAL-108
trước khi 5 report xong.

Sau report:

đánh giá lại WAL-108:

KEEP
MODIFY
SPLIT
REORDER.

Nếu Toán 5 B6 vẫn là slice tốt nhất:
giữ và giải thích bằng evidence.

Nhưng phải có ít nhất 3 bounded architecture checks:

A. Toán — Problem Solving.
B. Tiếng Việt/Ngữ văn — Reading/Writing.
C. History / Geography / Science tùy evidence mạnh nhất.

Mục tiêu:

không để architecture overfit Toán.

==================================================
39. JIRA / CONFLUENCE / GIT
==================================================

Audit Jira trước.

Reuse / modify / merge.

Không tạo:

- ticket theo từng grade;
- ticket theo từng subject;
- ticket theo từng screen.

Reconcile ít nhất:

WAL-108
WAL-109
WAL-110
và các ticket UX/curriculum/business liên quan.

Chỉ tạo ticket mới khi:

- finding stable;
- có evidence;
- actionable;
- không duplicate.

Confluence:
Founder/product truth ổn định.

Git:
5 báo cáo là source technical/design truth.

==================================================
40. CÁCH CHẠY
==================================================

Task này đã được Founder duyệt trước.

Do đó:

1. Tiếp tục OCR / ingestion.
2. Khi ingestion hoàn tất, không hỏi Founder lại.
3. Verify final checkpoint.
4. Lock snapshot.
5. Tự động chạy toàn bộ task.
6. Tạo đúng 5 file.
7. Reconcile Jira.
8. Commit/push.
9. Báo Founder checkpoint.

KHÔNG tiếp tục major UI implementation sau report
trước Founder checkpoint.

==================================================
41. FORMAT CHECKPOINT CUỐI
==================================================

# CORPUS SNAPSHOT

# TOP 10 PHÁT HIỆN TỪ SGK

# PHÁT HIỆN THEO NHÓM LỚP

# PHÁT HIỆN THEO MÔN

# AUDIT 38 MÀN
KEEP
MODIFY
MERGE
SPLIT
REPLACE
DEFER

# THAY ĐỔI UX LỚN NHẤT

# INTERACTION SURFACE CUỐI CÙNG

# FLOW ĐỀ XUẤT

# AGE-ADAPTIVE UX

# HUB REUSE

# SHARED DEVICE / MULTI-PROFILE

# MÔ HÌNH KINH DOANH
Student Free
Teacher Free
Parent Basic
Parent Premium
Ads
Ad-free Family
Subscription Unit
AI Cost

# WAL-108
KEEP / MODIFY / SPLIT / REORDER

# TOP RISKS

# DATA GAPS

# JIRA CHANGES

# BLOCKERS

# FOUNDER DECISION CÒN CẦN

# NEXT

==================================================
42. NGUYÊN TẮC CUỐI
==================================================

Đừng hỏi:

"Làm sao implement 38 concept?"

Hãy trả lời:

"Với toàn bộ SGK K–12 thực tế,
học sinh Việt Nam ở từng lứa tuổi và từng môn
thực sự cần học như thế nào,
SAM nên hỗ trợ bằng interaction nào,
38 concept phải thay đổi ra sao,
những năng lực nào có thể reuse từ Workizen Hub,
và mô hình Student Free + Teacher Free + Parent Premium
có thể vận hành bền vững mà không làm hỏng trải nghiệm học
hoặc tạo incentive xấu cho trẻ hay không?"

Mục tiêu cuối cùng:

HỌC SINH ĐƯỢC HỌC TỐT
+
GIÁO VIÊN DỄ TIẾP CẬN
+
PHỤ HUYNH NHẬN ĐƯỢC GIÁ TRỊ THỰC
+
SAM CÓ MÔ HÌNH KINH DOANH BỀN VỮNG.

Không kiếm tiền bằng cách làm trẻ phụ thuộc SAM lâu hơn.

Giá trị thương mại phải đến từ:

SAM GIÚP TRẺ TIẾN BỘ
→ PHỤ HUYNH NHÌN THẤY GIÁ TRỊ
→ PHỤ HUYNH SẴN SÀNG TRẢ PHÍ.
