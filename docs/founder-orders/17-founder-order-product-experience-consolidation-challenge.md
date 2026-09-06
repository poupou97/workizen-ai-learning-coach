FOUNDER ORDER — PRODUCT EXPERIENCE CONSOLIDATION & CHALLENGE

Mục tiêu:
Tôi muốn anh phản biện một lần cuối các Product Intent mới được làm rõ cho Học cùng SAM.

Đây KHÔNG phải lệnh implement ngay.
Không được đồng ý theo Founder chỉ để chiều ý.

Hãy đối chiếu với:
- repo hiện tại;
- 38 concept;
- Evidence Model;
- Pedagogy Runtime / PlannedAct;
- LearningIntent;
- LearningEvent / LearningSession;
- Bookshelf / Book / Chapter / Lesson;
- Surface / Learning Tool;
- SourceAsset / provenance;
- Parent / Learner architecture;
- kết quả Golden Journey;
- Conversation Spine / Agent-First research vừa hoàn thành.

Với từng hypothesis bên dưới:
ACCEPT / ACCEPT WITH CHANGES / REJECT / DEFER
+ evidence từ code/runtime/research
+ contradiction nếu có.

Nếu đồng thuận sau challenge:
→ cập nhật Product/Architecture truth phù hợp
→ tạo/re-scope Jira Epic/Story/Task cần thiết
→ tránh duplicate ticket hiện có
→ chưa tự động implement broad scope.

==================================================
A. CORE PRODUCT MENTAL MODEL
==================================================

Mental model Founder muốn:

Learner Profile / Grade
→ Giá sách của con
→ Book
→ Chapter
→ Lesson
→ Learning State
→ Learning Intent
→ Learning Experience with SAM
→ Learning Tool
→ Evidence
→ cập nhật Learning Map
→ Next Best Learning Action.

SGK không chỉ là content browser.

BOOK / CHAPTER / LESSON phải trở thành LEARNING MAP của trẻ cho cả năm học.

Trẻ nhìn vào phải hiểu nhẹ nhàng:

- mình đã đi tới đâu;
- phần nào đã tiếp xúc;
- phần nào tự làm được;
- phần nào cần SAM hỗ trợ;
- phần nào nên ôn lại;
- phía trước còn gì.

Bài/chương chưa học KHÔNG bị lock.
Trẻ luôn có thể mở và học trước.

Challenge:
1. Mental model này có phù hợp architecture hiện tại?
2. Current implementation đang lệch ở đâu?
3. 38 concept nào thực sự thuộc journey này?
4. Có đang biến Bookshelf thành content browser thay vì Learning Map không?

==================================================
B. GENTLE GAMIFICATION — EVIDENCE IS TRUTH
==================================================

Founder muốn Học cùng SAM có cảm giác như một game học tập RẤT NHẸ.

Không phải:
- XP;
- leaderboard;
- sibling ranking;
- streak pressure;
- countdown;
- fake mastery %;
- addictive mechanics.

Tôi muốn trẻ có cảm giác:

“Cuốn sách của mình đang dần được hoàn thiện.”

Có thể dùng:
- chapter/book gradually light up;
- badge;
- star/visual completion;
- SAM reaction;
- subtle celebration;
- visual progress.

Nhưng invariant:

GAMIFICATION PRESENTS PROGRESS.
EVIDENCE ESTABLISHES TRUTH.
COVERAGE ≠ MASTERY.

Không được suy:
1 event = ★
hay
★★ = hiểu 66%.

Challenge mô hình semantic state bên dưới, ví dụ:

UNSEEN
ENGAGED
INDEPENDENT_EVIDENCE
REVIEW_DUE
INSUFFICIENT_EVIDENCE

Đây chỉ là hypothesis, không bắt buộc đúng enum này.

Visual star/badge/color chỉ là projection lên Child UX.

Nếu dữ liệu không đủ:
→ fail closed
→ “chưa đủ bằng chứng”
→ không ép ra mastery.

Parent cũng không được nhận một hệ scoring khác.

Một Evidence truth → nhiều projection:
- Child gentle progress;
- Parent narrative;
- Home recommendation;
- Review;
- Learning Map.

Challenge:
1. Có nên giữ stars hay dùng visual khác?
2. Nếu giữ stars, semantics nào không gây hiểu nhầm mastery?
3. Chapter state aggregate lesson thế nào?
4. Coverage và mastery tách ra sao?
5. Recency / review-due tác động thế nào?
6. Assisted vs independent tác động thế nào?
7. Có thể “degrade gracefully” cho 842/843 lesson chưa có skill model không?

==================================================
C. LESSON = LEARNING WORKSPACE WITH SAM
==================================================

Khi trẻ mở một Lesson, Founder không muốn một LessonScreen tĩnh với hàng loạt paragraph/question hardcode.

Hypothesis:

Lesson trở thành một LEARNING WORKSPACE / LEARNING CONVERSATION WITH SAM.

Natural actions có thể gồm:

- Học trước
- Làm bài tập
- Ôn lại
- Tra cứu / Xem sách
- Tóm tắt
- Kiểm tra nhanh

KHÔNG giả định cả 6 đều là LearningIntent.

Hãy giữ separation of concerns.

Ví dụ cần challenge:

LearningIntent:
- prepare
- homework/practice
- review
- lookup

Summary:
có thể là utility/action.

Quick Check:
có thể thuộc Assessment / Assistance Policy thay vì LearningIntent.

Không tạo fake choice:
nếu các lựa chọn dẫn đến cùng Learning Experience thì không cần hỏi trẻ.

==================================================
D. SAM CONVERSATION ≠ GENERIC CHATBOT
==================================================

Founder muốn trẻ có cảm giác:

“Mình đang học bài này cùng SAM.”

SAM có thể:
- hỏi;
- giải thích;
- TTS;
- nhận text/voice;
- đưa hint;
- yêu cầu giải thích;
- mở Learning Tool;
- im khi trẻ cần tự làm;
- quay lại sau Tool;
- phản hồi dựa trên evidence.

Nhưng:

SAM KHÔNG tự quyết pedagogy.
LLM KHÔNG tự quyết curriculum/method/assistance/evidence.

Architecture hypothesis vẫn là:

LearningContext
→ Pedagogy Runtime
→ PlannedAct
→ SAM realization
→ Learning Tool
→ LearnerAction
→ CandidateEvidence
→ Evidence Validator
→ Student State.

TeachingAct là VALUE emitted by pedagogy, không phải autonomous agent.

Không tạo God Agent / generic chatbot.

Challenge:
Conversation nên là:
A. primary container,
B. optional realization,
C. hybrid with Surface,
hay model khác?

==================================================
E. LEARNING TOOL PRESENTATION
==================================================

Không assume Tool bắt buộc inline trong chat.

Hãy challenge 3 mô hình:

1. Inline Tool inside conversation
2. Full-screen Tool → return to conversation
3. Hybrid:
   conversation preview/action
   → full-screen Tool khi cần
   → return result/context to SAM

Đánh giá ít nhất:
- mobile UX;
- Math;
- Science Experiment;
- Essay;
- Map/Timeline;
- Quiz;
- Camera;
- scale K–12;
- Tool Contract;
- current Navigator implementation.

Founder hiện nghiêng về HYBRID nhưng chưa lock.

==================================================
F. TEXTBOOK CITATION & FULL SOURCE VIEW
==================================================

Founder muốn SGK luôn cách trẻ khoảng một cú chạm.

Khi SAM dùng source:

📖 Theo sách
SGK Khoa học 5 · Bài X · Trang Y

Bấm citation:
→ bottom sheet mở đúng source/page/context.

Có thể kéo/mở:
→ full textbook/source viewer.

Có thể:
- xem nguyên trang;
- hình minh họa;
- bảng/sơ đồ;
- zoom;
- trang trước/sau;
- quay lại đúng learning context.

Invariant:

📖 THEO SÁCH = source thật.
✨ SAM GIẢI THÍCH = SAM realization.

Không masquerade SAM inference thành SGK truth.

Claude đã chỉ ra SourceAsset hiện thiên về crop/bbox.
Hãy challenge data model cần thêm gì:
- PageAsset?
- SourcePage?
- DocumentPage?
- page image registry?
- hay reuse primitive hiện có?

Không implement viewer trong vòng này.

==================================================
G. PERSONAL CLASS CONTEXT — SCAN MATERIALS
==================================================

Bổ sung Product Intent mới.

Trong từng Subject, trẻ/phụ huynh có thể scan/import tài liệu thực tế của lớp:

- đề kiểm tra;
- phiếu bài tập;
- bài cô giao;
- giáo án/tài liệu giáo viên nếu gia đình có;
- kế hoạch tuần;
- notebook/vở ghi;
- ảnh bảng;
- worksheet;
- tài liệu ôn tập.

Ví dụ:

TOÁN 5
├── 📘 SGK / Official Curriculum
├── 🗺 Learning Map
└── 📂 Tài liệu lớp của con
     ├── 📝 Đề kiểm tra
     ├── 📄 Phiếu bài tập
     ├── 👩‍🏫 Tài liệu cô giáo
     └── 📷 Vở / bài trên lớp

Input có thể:
Camera / Scan / Import document.

Pipeline hypothesis:

Capture/Import
→ OCR / Document Understanding
→ Classification
→ Learner Confirmation
→ Subject / Book / Chapter / Lesson mapping
→ Personal Class Library / Class Context.

Không cho machine perception chưa confirm đi thẳng vào Learning Evidence.

==================================================
H. THREE DIFFERENT TRUTHS — DO NOT COLLAPSE
==================================================

Đây là hypothesis quan trọng cần challenge:

1. SGK / SGV / official curriculum
   → cho SAM biết chương trình chính thức nói gì.

2. Teacher / class materials
   → cho SAM biết lớp của đứa trẻ đang thực tế học/làm gì.

3. Tests / learner work / interaction
   → cho SAM evidence về chính đứa trẻ.

DO NOT COLLAPSE THESE THREE TRUTHS.

Có thể diễn đạt:

“SGK tells SAM what the curriculum is.
Teacher materials tell SAM what this class is doing.
Learner work tells SAM what this child can actually do.”

Teacher material KHÔNG tự động trở thành official curriculum truth.

Uploaded test KHÔNG tự động trở thành evidence.

Notebook scan KHÔNG tự động chứng minh mastery.

==================================================
I. SCANNED TEST → LEARNING EXPERIENCE
==================================================

Ví dụ Parent scan:

“Đề kiểm tra giữa kỳ — Toán 5”

SAM có thể:
- OCR;
- tách question;
- map chapter/lesson/skill nếu đủ confidence;
- hỏi confirm nếu uncertain;
- lưu vào Class Library.

Nhưng chỉ khi trẻ thực sự làm:

Scanned Test
→ Questions
→ Curriculum/Skill Mapping
→ Learner Attempt
→ CandidateEvidence
→ Evidence Validator
→ Validated Evidence.

SAM có thể sau đó nói trung thực:

- con tự làm được dạng nào;
- dạng nào cần hint;
- câu nào chưa đủ evidence;
- câu nào thuộc phần chưa học;
- phần nào nên ôn.

Challenge đặc biệt:
- assessment integrity;
- answer leakage;
- teacher answer key;
- OCR uncertainty;
- duplicate questions;
- test vs homework semantics;
- Tutor Mode ≠ Exam Mode.

==================================================
J. PERSONAL CLASS LIBRARY
==================================================

Challenge model:

Learner
└── Grade
    └── Subject
        ├── Official Books
        ├── Teacher/Class Materials
        ├── Tests
        ├── Worksheets
        ├── Notebook Scans
        ├── Learning Sessions
        └── Validated Evidence

Không nhất thiết UI phải hiện hierarchy này.
Đây là domain hypothesis.

Đánh giá:
- cái nào Knowledge Store;
- cái nào learner-private;
- cái nào class context;
- cái nào evidence;
- cái nào trace;
- retention/privacy;
- offline/local-first;
- shared device.

==================================================
K. EVENT / IDENTITY LINEAGE
==================================================

Claude đã phát hiện event hiện chưa có identity đủ tốt để hỏi:

“Session này thuộc chính xác Book/Lesson nào?”

Nếu đồng thuận cần mở rộng event model, đừng thêm một lessonId rời chỉ phục vụ stars.

Challenge một canonical lineage dùng chung cho:

Learning Map
Parent View
Session Replay
Citation
Evidence
Class Materials
Next Action.

Ví dụ hypothesis:

learnerId
→ subjectId
→ sourceDocumentId
→ contentNodeId / lessonId
→ activityId
→ skillCaseId? / conceptId?
→ sessionId
→ plannedAct / assistance
→ learnerAction
→ evidence.

Không bắt buộc schema này.
Hãy tìm minimum stable identity chain.

==================================================
L. PARENT VIEW / FAMILY LEARNING LINK
==================================================

Parent không cần “AI chấm con 82%”.

Parent cần hiểu nhẹ nhàng:

- con đang học đến đâu;
- tuần này học thêm gì;
- tự làm được gì;
- SAM đã giúp ở đâu;
- chỗ nào nên ôn;
- mức hỗ trợ có giảm theo thời gian không;
- lớp đang học gì nếu có Class Context.

Ví dụ narrative:

“Tuần này con học thêm 3 bài Khoa học.
Con tự hoàn thành hoạt động Bài 2.
Bài 3 cần SAM gợi ý một lần.
Bài 1 đang đến lúc nên ôn lại.”

Parent View phải projection từ CÙNG Event/Evidence model.

Không xây parallel scoring/tracking system.

Giữ:

TRACE ≠ EVIDENCE.

Live View / P2P vẫn research-only.
Session Summary có thể là MVP tốt hơn Live surveillance.

==================================================
M. HUB REUSE
==================================================

Đối chiếu khả năng reuse từ Workizen AI Personal Hub:

- Camera/Scan;
- OCR;
- Document Intelligence;
- Library;
- local storage;
- QR pairing;
- device discovery;
- sync;
- TTS/STT;
- notifications;
- AI Router/provider abstraction;
- privacy/storage;
- document viewer.

Không copy blindly.

Classify:
REUSE AS-IS
REUSE WITH ADAPTATION
EXTRACT SHARED
NOT SUITABLE.

==================================================
N. REQUIRED CHALLENGE OUTPUT
==================================================

Không viết báo cáo dài vì mục đích báo cáo.

Trả Founder trước bằng một bảng quyết định ngắn:

Hypothesis | Verdict | Evidence | Change needed

Sau đó trả lời:

1. Product model tổng thể có coherent không?
2. Chỗ nào Founder đang trộn:
   navigation / intent / assessment / pedagogy / presentation?
3. Chỗ nào Evidence Model hiện chưa support?
4. Chỗ nào data hiện chưa support?
5. Chỗ nào architecture hiện đã có nhưng disconnected?
6. Chỗ nào cần schema change?
7. Chỗ nào chỉ cần UI projection?
8. Chỗ nào không nên build?
9. Có contradiction nào với 38 concepts hoặc doctrine hiện tại?
10. Nếu build đúng, model này có scale K–12 mà không per-lesson Dart không?

==================================================
O. JIRA RULE — ONLY AFTER CHALLENGE
==================================================

Sau khi challenge:

ACCEPT
hoặc
ACCEPT WITH CHANGES

→ được phép log/re-scope vào Jira.

REJECT
→ ghi lý do, KHÔNG tạo implementation ticket.

DEFER
→ chỉ log research/backlog nếu thực sự cần.

Trước khi tạo ticket:
- audit Jira WAL hiện tại;
- reuse/re-scope ticket có sẵn;
- tránh duplicate;
- giữ ticket medium-sized;
- dependency rõ;
- evidence/acceptance criteria rõ.

Tôi muốn tổ chức Jira theo capability, KHÔNG theo từng màn hình/bài học.

Candidate workstreams để anh challenge, KHÔNG mặc định phải tạo tất cả:

1. Learning Map / Evidence-backed Progress Projection
2. Lesson Learning Workspace / SAM Experience
3. PlannedAct → Learning Tool Contract
4. CandidateEvidence → Evidence Validator
5. Canonical Learning Context / Event Lineage
6. Source Citation → Page/Textbook Viewer
7. Personal Class Library
8. Scan/OCR → Class Context Pipeline
9. Scanned Assessment / Test Ingestion
10. Parent Learning Summary / Evidence Projection
11. Hub Capability Reuse
12. Learning Experience Factory / Content-Pedagogy Compiler

Không tạo ticket kiểu:
“Implement Bài 1”
“Implement Bài 2”
“Implement Chương 3”
trừ gold probe/evidence fixture có lý do rõ ràng.

==================================================
P. EXECUTION AFTER JIRA
==================================================

Sau khi Jira được cập nhật:

KHÔNG chạy toàn bộ backlog ngay.

Chỉ đề xuất cho Founder:

P0 — architecture/data prerequisite
P1 — product-visible slice
P2 — expansion/research

Và chọn MỘT bounded next slice có khả năng falsify architecture mạnh nhất.

Tôi nghi candidate tốt là:

Book/Lesson
→ contextual Learning Intent
→ PlannedAct
→ one existing Learning Tool
→ LearnerAction
→ CandidateEvidence
→ Evidence Validator
→ Learning Event with canonical lesson lineage
→ Learning Map projection
→ Parent-readable session summary.

Nhưng đây chỉ là Founder hypothesis.

Hãy challenge và đề xuất slice tốt hơn nếu evidence cho thấy cần.

==================================================
FINAL PRINCIPLES
==================================================

SGK IS THE LEARNING MAP.

SAM IS THE LEARNING COMPANION.

LEARNING TOOLS ARE WHERE THE CHILD DOES THE WORK.

PEDAGOGY DECIDES WHAT SHOULD HAPPEN.

EVIDENCE DECIDES WHAT WE MAY CLAIM.

GAMIFICATION PRESENTS REAL PROGRESS.

COVERAGE IS NOT MASTERY.

TEACHER MATERIALS DESCRIBE CLASS CONTEXT,
NOT OFFICIAL CURRICULUM TRUTH.

UPLOADED WORK IS NOT LEARNING EVIDENCE
UNTIL THE CHILD ACTUALLY PRODUCES VALIDATABLE PERFORMANCE.

ONE EVIDENCE TRUTH,
MULTIPLE AUTHORIZED PROJECTIONS:
CHILD / PARENT / HOME / REVIEW / LEARNING MAP.

NO PER-LESSON HARDCODED PRODUCT ARCHITECTURE.

Nếu các nguyên tắc trên xung đột với code/runtime/evidence thực tế:
hãy challenge Founder.
Không được sửa bằng cách giả dữ liệu cho khớp vision.
