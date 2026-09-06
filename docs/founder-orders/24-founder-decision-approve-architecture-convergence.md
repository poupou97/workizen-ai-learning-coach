# FOUNDER DECISION — APPROVE ARCHITECTURE CONVERGENCE
## Merge 2 Learning Paths + Full K–12 Corpus Audit

FOUNDER DECISION: APPROVED

Tôi đồng ý hướng:

MERGE / CONVERGE hai hệ thống hiện tại:

A. DEEP INTELLIGENCE PATH
Concept
→ SkillCase
→ CurriculumEdge
→ Pedagogy
→ Graph-guided Retrieval
→ PlannedAct

và:

B. SCALE / LEARNABLE PATH
Corpus
→ Activity Recognition
→ LearningActivity
→ Learning Surface
→ Evidence.

Mục tiêu cuối:

REAL LESSON
→ LearningActivity
→ Concept / SkillCase
→ Curriculum / Pedagogy Permission
→ Source Retrieval
→ PlannedAct / SAM
→ Learning Surface
→ LearnerAction
→ ValidatedEvidence
→ Student State
→ Next Action
→ UI/UX.

==================================================
1. IMPORTANT FOUNDER REQUIREMENT
==================================================

Không được thiết kế convergence chỉ dựa trên
Toán 5 Bài 6 hoặc vài lesson mẫu.

PHẢI RÀ SOÁT FULL CORPUS K–12:

LỚP 1 → 12

toàn bộ SGK/SGV hiện có trong corpus.

Mục tiêu không phải manual annotate mọi lesson.

Mục tiêu là hiểu:

- những cấu trúc nào lặp lại;
- những cấu trúc nào khác nhau theo môn/lớp;
- Concept/SkillCase mapping có scale được không;
- ActivityPattern nào scale được;
- prerequisite nào có evidence;
- PedagogicalRole nào nhận diện được;
- SGV cung cấp pedagogy/answer/objective gì;
- những môn nào cần architecture khác;
- những trường hợp nào không thể tự động hóa an toàn;
- những missing capability nào đang chặn convergence.

FULL CORPUS AUDIT
!=
FULL MANUAL ANNOTATION.

==================================================
2. FIRST — CENSUS THE ENTIRE CORPUS
==================================================

Rà toàn bộ corpus hiện có.

Tạo census theo:

Grade
Subject
Book
SGK / SGV
Chapter
Lesson
Activity
Activity Pattern
Objective if detectable
Concept candidate
SkillCase candidate
Pedagogical Role
Source provenance
Answer/evaluation availability
layout quality
retrieval readiness
Evidence capability.

Không được suy diễn dữ liệu không chắc chắn thành truth.

Classify confidence/trust.

==================================================
3. BUILD A K–12 COVERAGE MAP
==================================================

Founder cần nhìn được toàn cảnh 12 lớp.

Output tối thiểu:

GRADE × SUBJECT matrix.

Cho từng vùng:

SOURCE_AVAILABLE
STRUCTURED
LESSON_BROWSABLE
ACTIVITY_PRESENT
SEMANTIC_MAPPABLE
PEDAGOGY_MAPPABLE
EVIDENCE_CAPABLE
DEEP_INTELLIGENCE_READY
UX_CONNECTED.

Phải cho biết số lượng và tỷ lệ.

Không chỉ báo cáo aggregate toàn hệ thống.

==================================================
4. FIND REUSABLE PATTERNS
==================================================

Không làm architecture theo từng môn một cách máy móc.

Từ full corpus, tìm các pattern tái sử dụng.

Ví dụ cần kiểm chứng:

Problem Solving
Experiment
Reading
Writing
Source Reasoning
Quick Check
Assessment
Classification
Comparison
Process
Map / Spatial
Data / Chart
Listening
Speaking
Project / Group.

Đây chỉ là seed list.

Corpus quyết định taxonomy thực tế.

Measure:

pattern
→ bao nhiêu grade
→ bao nhiêu subject
→ bao nhiêu lesson
→ extraction confidence
→ pedagogy confidence
→ Evidence potential
→ existing Surface
→ missing Surface.

==================================================
5. FIND EXCEPTIONS, NOT ONLY HAPPY PATHS
==================================================

Full K–12 audit phải chủ động tìm các trường hợp
làm architecture hiện tại thất bại.

Đặc biệt:

Grade 1 / early literacy
Math
Science
Ngữ văn
Tiếng Việt
History
Geography
Tin học
English / foreign language
Arts
Music
PE
GDTC
physical/group/project activities.

Không được ép mọi môn vào cùng một interaction model.

Một Learning OS chung là mục tiêu.

Nhưng subject/activity-specific adapters
được phép nếu corpus chứng minh cần thiết.

==================================================
6. CONCEPT / SKILLCASE SCALE TEST
==================================================

Đây là câu hỏi P0:

Concept / SkillCase architecture hiện tại
có scale được từ 1 lesson lên K–12 không?

Dùng full corpus để tìm evidence.

Không cần tạo full semantic graph ngay.

Thay vào đó:

- detect candidates at scale;
- cluster recurring structures;
- sample representative gold sets;
- validate;
- falsify;
- estimate coverage.

Determine:

RETAIN
FORMALIZE
EXTEND
or
REPLACE

cho current Concept / SkillCase model.

Founder đã approve convergence,
KHÔNG approve blind mass-generation.

==================================================
7. PREREQUISITE AUDIT
==================================================

Không mass-infer prerequisite rồi coi là truth.

Rà corpus để tìm nguồn prerequisite đáng tin:

SGK sequence
SGV explicit prerequisite
review/reference statements
concept introduction/reuse
cross-grade dependency
teacher guidance.

Remember:

SOURCE ORDER != PREREQUISITE.

Output:

PROVEN prerequisite
PARTIAL
CANDIDATE/HYPOTHESIS
UNKNOWN.

Founder muốn biết:

Có đủ prerequisite evidence để sau này
test KST / Learning Frontier hay chưa?

==================================================
8. PEDAGOGY AUDIT
==================================================

Đặc biệt khai thác SGV.

Tìm:

learning objective
prerequisite
activity sequence
guiding question
expected learner response
misconception
support/scaffold
assessment
expected product
practice/application
pedagogical role.

Mục tiêu:

SOURCE
→ PEDAGOGY MODEL

không phải:

SOURCE
→ giant LLM prompt.

Measure mức độ scale theo Grade/Subject/Book.

==================================================
9. CONVERGENCE BRIDGE
==================================================

Sau full corpus audit,
thiết kế THIN CONVERGENCE BRIDGE.

Không rewrite cả hai hệ thống.

Bridge phải cho phép existing:

LearningActivity

liên kết dần với:

Concept
SkillCase
PedagogicalRole
Curriculum permissions
Source provenance
Evidence semantics.

Ví dụ conceptual only:

LearningActivity
   ↓
SemanticBinding
   ├→ Concept
   ├→ SkillCase
   ├→ PedagogicalRole
   ├→ Source
   └→ confidence / provenance.

Tên/model thực tế do Claude quyết định.

Không implement abstraction này
nếu evidence cho thấy model khác tốt hơn.

==================================================
10. FAIL CLOSED
==================================================

Không có semantic mapping đáng tin:

→ lesson vẫn có thể hoạt động ở capability level hiện tại
nếu an toàn.

Nhưng:

→ KHÔNG giả Concept;
→ KHÔNG giả SkillCase;
→ KHÔNG giả prerequisite;
→ KHÔNG tạo Evidence semantics sâu;
→ KHÔNG dùng graph permission giả.

Convergence phải incremental.

Không được biến 113 Learnable hiện tại
thành 0 chỉ vì chưa semantic-map hết.

==================================================
11. REPRESENTATIVE GOLD SET
==================================================

Sau khi FULL corpus census hoàn tất,
chọn representative gold set.

Không chọn ngẫu nhiên 3–5 bài cùng loại.

Gold set phải bao phủ:

early grade
middle grade
high school

và nhiều activity/subject family.

Bao gồm cả:

happy path
edge case
known falsification
layout-heavy case
open-response
gradable assessment
non-gradable activity.

Dùng gold set để validate architecture sâu.

FULL SCAN gives BREADTH.

GOLD SET gives DEPTH.

Cả hai đều bắt buộc.

==================================================
12. THEN BUILD CONVERGENCE VERTICAL SLICES
==================================================

Chỉ sau census + gold validation,
implement bounded representative slices.

Mỗi slice phải chạy:

REAL SOURCE
→ REAL LESSON
→ REAL ACTIVITY
→ semantic binding
→ pedagogy permission
→ graph-guided retrieval
→ SAM
→ learner action
→ Evidence
→ state
→ UI.

Ưu tiên reuse existing Surfaces.

Không mass-wire K–12 trước khi slices pass.

==================================================
13. UI/UX REQUIREMENT
==================================================

Mỗi capability sâu phải có visible consumer.

Founder muốn thấy intelligence trên:

Home
Learning Map
Lesson
SAM Workspace
Why
Source
Review
Next Action
Parent

khi phù hợp.

Không tạo screen chỉ để show graph.

Ví dụ:

prerequisite intelligence
→ "Con nên ôn phần này trước."

source provenance
→ "Theo sách" / Why / Source.

Evidence
→ real progress.

Student State
→ Review / Parent.

Next Action
→ Home / Learning Map.

==================================================
14. REQUIRED OUTPUT
==================================================

Tạo/update:

K12 FULL CORPUS COVERAGE MAP

K12 ACTIVITY PATTERN CENSUS

K12 SEMANTIC / PEDAGOGY READINESS MAP

K12 PREREQUISITE EVIDENCE MAP

AS-IS → CONVERGED ARCHITECTURE

THIN CONVERGENCE BRIDGE PROPOSAL

REPRESENTATIVE GOLD SET

CONVERGENCE VALIDATION REPORT

CONCEPT ↔ DATA ↔ UX MATRIX.

Machine-readable CSV/JSON where useful.

Founder report phải trả lời đơn giản:

1. Đã rà bao nhiêu / tổng bao nhiêu sách?
2. Đã rà đủ Grade 1–12 chưa?
3. Những pattern lớn nào phủ được bao nhiêu lesson?
4. Concept/SkillCase scale được không?
5. Pedagogy từ SGV scale được không?
6. Prerequisite evidence hiện đủ đến đâu?
7. Bao nhiêu lesson có khả năng nối Deep Intelligence?
8. Bao nhiêu chưa thể nối và vì sao?
9. Bridge architecture là gì?
10. UI/UX nào được hưởng lợi?
11. Rủi ro false-truth lớn nhất?
12. Bước scale tiếp theo là gì?

==================================================
15. JIRA
==================================================

Update WAL-195 / WAL-196 theo Founder decision:

FOUNDER APPROVED:
ARCHITECTURE CONVERGENCE DIRECTION.

Do NOT mark whole Epic Done.

Create/reuse bounded TODOs for:

P0 — Full K–12 Corpus Census

P0 — Grade × Subject Coverage Map

P0 — K–12 Activity Pattern Census

P0 — Concept/SkillCase Scale Audit

P0 — SGV Pedagogy Scale Audit

P0 — Prerequisite Evidence Audit

P0 — Thin Convergence Bridge

P0 — Representative Cross-K12 Gold Set

P0 — Convergence Vertical Slice

P0 — Deep Intelligence → UI/UX Validation

P1 — KST Readiness Re-evaluation
only after prerequisite evidence exists.

Avoid duplicate tickets.

==================================================
16. AUTONOMOUS AUTHORITY
==================================================

Founder authorizes autonomous execution for:

audit
scripts
corpus census
analysis
Jira/Confluence
tests
gold sets
bounded architecture implementation
representative vertical slices
UI integration
PR
CI
merge

within existing reversible governance.

Do not stop after each research finding.

Continue through the convergence validation.

Still stop for:

large destructive migration
commercial copyright/licensing decision
mass uncontrolled LLM generation
large manual annotation operation
new paid infrastructure
public/store release
fundamental product fork.

==================================================
17. SUCCESS CONDITION
==================================================

Success is NOT:

"We scanned all PDFs."

Success is NOT:

"We created a graph."

Success is NOT:

"We connected 113 lesson IDs."

Success means:

FULL K–12 CORPUS
has been systematically understood,

the reusable learning structures
and exceptions are measured,

and the two existing SAM systems
are converging through a validated architecture
that can scale incrementally across Grade 1–12.

Target:

BREADTH
+
DEEP INTELLIGENCE
+
EVIDENCE
+
VISIBLE PRODUCT EXPERIENCE.

Proceed autonomously.

Do not ask Founder to approve normal reversible steps.

Report at meaningful checkpoints with evidence.
