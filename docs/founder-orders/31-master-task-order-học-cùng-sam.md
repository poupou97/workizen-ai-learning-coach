MASTER TASK ORDER — HỌC CÙNG SAM
AUTONOMOUS PARALLEL DEVELOPMENT
PROVE + EXPERIENCE + DISCOVER

Founder đã review toàn bộ:
- PRE-AUTONOMY CHECKPOINT
- DUAL-TRACK CHECKPOINT
- Track A / B-lane
- Track B Lesson Workspace vertical slice
- Trusted Corpus / TC-v2
- Learning Views research

Founder ACCEPT hướng hiện tại.

============================================================
0. FOUNDER INTENT
============================================================

Không phát triển theo kiểu:

CORE XONG → SAU ĐÓ MỚI LÀM UI

và cũng không:

UI ĐẸP → SAU ĐÓ MỚI LO CORE.

Học cùng SAM phải phát triển SONG SONG.

Operating model từ bây giờ:

PROVE + EXPERIENCE + DISCOVER

LANE A — PROVE
Làm cho dữ liệu, evidence, pedagogy và runtime đúng.

LANE B — EXPERIENCE
Làm cho Founder/trẻ có thể nhìn, chạm, học thử và đánh giá sản phẩm.

LANE C — DISCOVER
Tiếp tục nghiên cứu K–12 để biết kiến trúc hiện tại generalize được tới đâu.

Ba lane chạy song song khi file/worktree/dependency cho phép.

Không để một lane vô lý block hai lane còn lại.

============================================================
1. GOLDEN VERTICAL SLICE
============================================================

Giữ:

KHTN 6
Bài 17 — “Tách chất khỏi hỗn hợp”

làm GOLDEN END-TO-END VERTICAL SLICE hiện tại.

Đây KHÔNG phải lesson duy nhất được nghiên cứu.

Nó là integration target để chứng minh toàn chain:

Original Source
→ Structured Document Model
→ Block Trust
→ Trusted Structured Lesson
→ LessonDocument
→ LearningActivity
→ SemanticBinding
→ Concept / SkillCase / Method khi applicable
→ Lesson Workspace
   ├── Đọc / Smart Book
   ├── Trực quan / Visual Learning
   └── Học với SAM
→ LearnerAction
→ EvidenceValidator
→ LearningEvidence
→ Student Knowledge State
→ Next Best Learning Action

Không tăng +N lessons chỉ để báo coverage.

============================================================
2. LANE A — PROVE / TRUTH
============================================================

Tiếp tục các P0/P1 core đã xác định.

Ưu tiên:

A1. TRUSTED SOURCE → PRODUCT

Xây bridge thật:

TrustedLearningSource
→ Trusted Structured Lesson
→ LessonDocument

LessonDocument của Track B là candidate CONSUMER CONTRACT.

Không tạo thêm một Corpus Model thứ ba nếu không có bằng chứng cần thiết.

Preserve:
- block id
- source document
- page
- bbox
- role
- relations
- lesson identity
- provenance
- trust status
- withholding reasons

WITHHELD phải tiếp tục fail-closed.

WITHHELD != TRUSTED.
WITHHELD content không được lén trở thành SAM-readable text.

------------------------------------------------------------

A2. FALSE-TRUST AUDIT — P0

Tiếp tục 484-row shipped-content false-trust audit.

Thực hiện annotation / measurement theo protocol hiện có.

Báo riêng:
- text fidelity
- reading order
- role fidelity
- lesson attachment
- false trust
- teaching-critical false trust
- display-only false trust
- layout family / subject nếu đủ sample

Không tự hạ threshold để PASS.

Không biến measurement target thành release policy.

Founder sẽ chốt release threshold sau khi có số đo.

Không tăng production coverage trước G1/G2/G3.

------------------------------------------------------------

A3. EVIDENCE CONTRACT

Founder invariant:

SELF REPORT != COMPETENCE.

Các hành động kiểu:

“Con đã làm xong”
“Con đã đọc”
“Con đã trả lời”

nếu chưa có validator:

→ ParticipationEvidence

KHÔNG được tạo:
- independent success
- competence
- mastery
- “Tự làm được”

Parent UI không được suy competence từ participation.

Research/formalize candidate:

ValidatedEvidence

Target model:

LearnerAction
→ EvidenceValidator
→ ValidatedEvidence
→ Student Knowledge State

Chỉ deterministic/approved validator mới được tạo evidence đủ mạnh
để thay đổi competence/mastery.

------------------------------------------------------------

A4. EVIDENCE INTEGRITY

Giữ/finalize:
- globally/appropriately unique event IDs
- idempotent append
- retry/re-open không double-count mastery
- backward-compatible legacy read

Research bounded:
- append-on-disk durability
- integrity/tamper strategy

Không thay storage architecture lớn nếu chưa cần Founder decision.

------------------------------------------------------------

A5. LINEAGE

Scale surfaces phải có lineage đầy đủ.

Camera-originated Tutor:

DEFAULT:
sourceDocumentId = null
lessonNo = null

Chỉ stamp lesson khi camera được gọi từ một explicit,
resolved LearningContext đủ tin cậy.

Không:
camera image → AI guess lesson → lineage truth.

------------------------------------------------------------

A6. DEEP ↔ SCALE CONVERGENCE

Không chọn Deep HOẶC Scale.

Chúng bổ sung nhau.

Target candidate:

Trusted Structured Lesson
→ LearningActivity
→ SemanticBinding
→ Concept / SkillCase
→ Method
→ Pedagogy Runtime

Scale/Activity = breadth / what learner does.

Concept/SkillCase/Method = pedagogical depth /
what is being learned and how SAM may teach it.

Implement only bounded contracts needed to prove convergence.

Không mass-convert K–12.

Không tạo runtime thứ ba.

Các claim “Founder-approved convergence” không có evidence:
→ TBD / PROPOSED.

------------------------------------------------------------

A7. PEDAGOGY RUNTIME

Bài 17 hiện có prototype scripted tutor.

Progressively investigate/replace safe portions with REAL bounded
Pedagogy Runtime.

Target:

Trusted Source
+
LearningContext
+
Student State
+
Allowed Methods
+
LearningActivity / PlannedAct
→ Pedagogy Runtime
→ permitted tutor behavior

SAM TUTOR != CHAT.

LLM không quyết định pedagogy.

RETRIEVED != PERMITTED.

Không unrestricted LLM wiring.

Không bypass guard/runtime.

Nếu capability thật chưa có:
giữ prototype rõ ràng thay vì giả capability production.

------------------------------------------------------------

A8. NEXT ACTION

Progressively replace prototype Next Action with:

Student Knowledge State
+
Learning Context
+
pedagogical rules
→ Next Best Learning Action

Không invent thời gian/phần trăm/mastery.

============================================================
3. LANE B — EXPERIENCE / UIUX
============================================================

Không chờ Lane A hoàn tất.

Tiếp tục làm sản phẩm NHÌN THẤY ĐƯỢC.

Golden Slice hiện khoảng 55–65% Experience Fidelity.

Direction:
đưa nó dần tới khoảng 75–85%.

Đây là directional target, KHÔNG phải vanity KPI.

------------------------------------------------------------

B1. JOURNEY

Tiếp tục hoàn thiện:

Bookshelf
→ Book
→ Chapter
→ Lesson
→ Lesson Workspace

Lesson Workspace:

[📖 Đọc]
[✨ Trực quan]
[🦉 Học với SAM]

+
SAM đề xuất
+
Next Action

Founder cầm máy phải hiểu ngay:

1. Con đang ở đâu?
2. Đang học bài gì?
3. Có những cách học nào?
4. SAM đang làm gì?
5. Tại sao SAM đề xuất việc đó?
6. Tiếp theo con nên làm gì?

------------------------------------------------------------

B2. SMART BOOK

Tiếp tục Hybrid Smart Book.

Trusted blocks:
→ native rendering.

Unsupported/untrusted:
→ withheld / safe fallback.

Không biến unknown thành textbook truth.

Improve:
- typography
- hierarchy
- image/caption relation
- reading order
- source reference
- navigation
- source anchor
- withheld state
- font controls
- child readability

Page/image crop vẫn INTERNAL/RESEARCH ONLY
cho tới khi licensing được quyết định.

------------------------------------------------------------

B3. VISUAL LEARNING

Tiếp tục typed/source-grounded Visual Learning.

Ví dụ:

ProcessStep[] → Process
HistoricalEvent[] → Timeline
ConceptRelation[] → Concept Map
Comparison[] → Comparison
GeoEntity[] → Map

Không:

lesson text
→ unconstrained LLM
→ mindmap/visual
→ child.

Nếu semantic structure chưa đủ trust:
fail closed / prototype-marked.

Visual Learning là renderer family,
không phải một nút “Mindmap”.

------------------------------------------------------------

B4. HỌC VỚI SAM

Tiếp tục làm visible tutor experience:

explain
→ ask
→ learner response
→ hint/scaffold
→ check
→ feedback
→ next

Không shame child.

Không fake grading.

Prototype SAM phải machine-marked.

Prototype behavior không được tạo LearningEvidence.

Khi real Pedagogy Runtime có capability tương ứng:
thay từng phần prototype bằng real capability.

------------------------------------------------------------

B5. GENERAL UI DEFECTS

Tiếp tục sửa các lỗi đã audit thấy, ưu tiên những lỗi gây hiểu sai:

- raw source/document ids lộ ra UI
- cross-grade source asset
- android app label “learning_coach”
- hard-coded grade “5”
- cold-start blank nếu xác định được nguyên nhân bounded
- TOC/title presentation
- figure/caption mismatch
- misleading empty states
- source/trust states

Không làm cosmetic cleanup vô tận nếu không ảnh hưởng journey.

============================================================
4. LANE C — DISCOVER / K–12 RESEARCH
============================================================

Lane C chạy song song.

Mục tiêu KHÔNG phải tăng production coverage.

Mục tiêu:
tìm xem architecture/capability nào sẽ unlock K–12 tiếp theo.

Allowed:

- corpus census
- modality taxonomy
- 27 Activity Pattern registry research
- source-layout research
- SGV pairing research
- role-layer research
- candidate renderer research
- candidate Learning Surface research
- architecture falsification
- candidate lesson selection

Không mass implement 27 patterns.

Không claim “learnable/trusted” chỉ từ detection.

BROWSABLE != LEARNABLE.
ACTIVITY_PRESENT != EVIDENCE_CAPABLE.
TRACE != EVIDENCE.

------------------------------------------------------------

SECOND GOLDEN LESSON STRATEGY

Không cần đợi Bài 17 hoàn hảo 100%.

Khi một abstraction của Bài 17 đã đủ evidence,
đề xuất lesson #2.

Lesson #2 phải cố tình KHÁC modality/domain
để falsify architecture.

Ví dụ candidates:

- History → timeline / source reasoning
- Math → problem solving / method gating
- Language → reading/writing

Không chọn một Science lesson gần giống chỉ để dễ PASS.

Founder review trước khi biến candidate thành next production slice.

============================================================
5. REAL DEVICE — MANDATORY LOOP
============================================================

UI work không DONE chỉ vì widget test xanh.

Mỗi milestone visible:

BUILD
→ INSTALL
→ WALK
→ SCREENSHOT
→ OBSERVE
→ DEFECT
→ ITERATE
→ REGRESSION TEST

Nokia hiện tại là real-device validation target.

Không bypass lock/device security.

Nếu device unavailable:
tiếp tục code/test/emulator và queue device checklist.
Không ngồi chờ.

============================================================
6. EVIDENCE RETENTION
============================================================

Device-verified claim phải truy lại được evidence.

Không dựa duy nhất vào Desktop screenshots.

Thiết kế bounded evidence retention:

- manifest
- timestamps
- commit/build id
- device/build metadata
- evidence file hashes
- stable bundle/artifact location
- checklist/result

Không commit raw copyrighted PDFs.

Không lưu private lock-screen/personal notification frames.

Nếu evidence bị mất:
claim DEVICE VERIFIED phải bị downgrade
nếu không còn nguồn độc lập để chứng minh.

============================================================
7. REPORTING — FIVE SEPARATE SCORES
============================================================

Từ vòng này KHÔNG dùng một “Real Capability Ratio” chung.

Mỗi checkpoint báo riêng:

1. EXPERIENCE FIDELITY
   UI/UX gần Founder concept bao nhiêu?

2. SOURCE REALITY
   Bao nhiêu visible content đến từ source thật?

3. SOURCE TRUST
   Bao nhiêu content đi qua production-trusted path?

4. PEDAGOGY REALITY
   Bao nhiêu tutor behavior do real Pedagogy Runtime điều khiển?

5. EVIDENCE REALITY
   Bao nhiêu interaction tạo evidence hợp lệ,
   được validator/evidence contract cho phép?

Không average năm số này thành một score.

Ngoài ra báo:

- device verified?
- fixture/prototype dependency?
- open P0?
- regressions?
- next falsifier?

============================================================
8. CURRENT FOUNDER GATES
============================================================

KHÔNG tự động:

- production coverage expansion
- trust threshold changes
- Short-Answer Surface
- unrestricted LLM wiring
- full-corpus reprocess
- mass Learning Views
- 27-pattern implementation
- public SGK text/image distribution
- destructive data migration
- major architecture fork

False-trust annotation = P0.

Licensing:
verbatim SGK text/page/image remains
INTERNAL / RESEARCH ONLY
until explicit decision.

============================================================
9. PR / GOVERNANCE
============================================================

Autonomous work is allowed for reversible,
bounded, test-backed work across all three lanes.

Use isolated worktrees/branches where useful.

CI must pass.

No direct main.

Every PR stops at:

READY FOR FOUNDER REVIEW

unless the CURRENT task explicitly authorizes that specific merge.

A previous merge authorization is NOT standing merge authority.

Do not merge merely because CI is green.

============================================================
10. CURRENT OPEN PR INTEGRATION
============================================================

Review dependencies before integrating Track B.

Do not blindly merge #66 ahead of required Track-A contracts.

Prefer dependency-aware integration.

Before Track B integration:

- rebase/update against accepted Track-A contracts as required
- rerun full CI
- rebuild
- install
- rerun Golden Slice on Nokia
- confirm fixture/prototype boundaries remain intact
- confirm Sessions/Evidence behavior remains correct

Report any semantic conflict instead of silently resolving
a Founder-level architecture decision.

============================================================
11. AUTONOMOUS EXECUTION RULE
============================================================

Do not stop after every small task to ask Founder.

Continue with the next independent reversible task.

Stop only when:

A. a Founder gate is reached;
B. irreversible/destructive action is required;
C. licensing/public release decision is required;
D. major architecture fork requires Founder decision;
E. evidence contradicts a core assumption and continuing would
   manufacture progress;
F. no safe independent work remains.

If one lane is blocked:
continue safe work in the other lanes.

Evidence > plan.
Measured reality > Jira status.
Human-visible product > invisible progress claims.
Trust > coverage.

============================================================
12. NEXT CHECKPOINT
============================================================

Return ONE consolidated Founder report.

Show:

LANE A — PROVE
- trusted pipeline delta
- false-trust status
- evidence integrity
- lineage
- pedagogy runtime delta
- Student State / Next Action delta

LANE B — EXPERIENCE
- latest Nokia journey
- Experience Fidelity
- major UX changes
- defects found on device
- defects fixed/open

LANE C — DISCOVER
- what was learned about K–12 generalization
- which assumptions were proven/falsified
- candidate second lesson and WHY it is a strong falsifier
  if evidence is sufficient

FIVE SCORES:
- Experience Fidelity
- Source Reality
- Source Trust
- Pedagogy Reality
- Evidence Reality

Then give autonomy status PER SCOPE:

- Core engineering
- UI/UX
- Architecture research
- Trusted-content expansion
- Pedagogy automation
- LLM Tutor
- Public content distribution

Use:
A READY
B READY WITH GUARDRAILS
C NOT READY
D REBASE

Do not collapse these into one global grade.

============================================================
13. CORE PRODUCT PRINCIPLE
============================================================

HỌC CÙNG SAM must not become:

a beautiful UI on unreliable knowledge,

or:

a perfect invisible architecture nobody can use.

BUILD THE TRUTH
+
BUILD THE EXPERIENCE
+
CONTINUOUSLY DISCOVER HOW TO SCALE IT.

Each must challenge and falsify the others.

Continue autonomously now.
