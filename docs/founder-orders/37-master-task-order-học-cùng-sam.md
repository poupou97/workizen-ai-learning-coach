# MASTER TASK ORDER — HỌC CÙNG SAM
## GENERALIZED SEMANTIC GRAPH → VISUAL GRAMMAR
### “Không thiết kế 3.679 visualization — thiết kế một ngôn ngữ để 3.679 bài có thể được compile thành visualization”

PRIORITY: P0 RESEARCH + BOUNDED POC
MODE: AUTONOMOUS / REVERSIBLE
MERGE: NO
FINAL STATE: READY FOR FOUNDER REVIEW

==================================================
0. FOUNDER INTENT
==================================================

Founder muốn xây phần:

✨ TRỰC QUAN / VISUAL LEARNING

theo kiến trúc có khả năng tổng quát hóa toàn K–12.

KHÔNG muốn:

3,679 lessons
→ 3,679 visualization được thiết kế/edit riêng.

KHÔNG muốn:

Lesson text
→ LLM
→ generate arbitrary mindmap mỗi lần user mở bài.

KHÔNG muốn:

mỗi môn có một pipeline hoàn toàn riêng.

Founder hypothesis:

Trusted Structured Learning Content
→ Semantic Structure
→ Visual Grammar
→ deterministic / controlled Renderer
→ Visual Learning Surface.

AI có thể hỗ trợ semantic understanding/generation,
nhưng AI output không tự động trở thành source truth.

==================================================
1. NORTH STAR
==================================================

Nghiên cứu và chứng minh liệu có thể xây:

ONE GENERAL SEMANTIC LANGUAGE
+
SMALL SET OF VISUAL GRAMMARS
+
BOUNDED DOMAIN EXTENSIONS

để biểu diễn phần lớn kiến thức K–12.

Target architecture hypothesis:

Trusted Structured Lesson
        ↓
Semantic Extraction
        ↓
SemanticGraphCandidate
        ↓
Grounding + Validation
        ↓
Validated Semantic Graph
        ↓
Visual Pattern Selector
        ↓
Visual Spec
        ↓
Controlled Renderer
        ↓
✨ Visual Learning

Đây là HYPOTHESIS.

Không được coi là architecture approved
trước khi census + POC có evidence.

==================================================
2. AUDIT FIRST
==================================================

Trước khi thiết kế mới, audit toàn repo.

Tìm tất cả implementation/research hiện có liên quan:

- SemanticData
- SemanticBinding
- Concept
- SkillCase
- Method
- CurriculumEdge
- Knowledge Graph
- LearningActivity
- Activity Pattern
- Process
- Timeline
- Comparison
- ConceptMap
- visualization
- mindmap
- renderer
- visual learning
- Learning Views
- LessonDocument
- Trusted Structured Lesson
- sourceRef/provenance.

Phân loại:

EXISTS AND USED
EXISTS BUT NOT WIRED
PARTIAL
RESEARCH ONLY
MISSING.

Đặc biệt audit implementation hiện tại của:

Bài 17 KHTN6
→ Process
→ Comparison
→ ConceptMap
→ Timeline

để xác định:

- phần nào generic;
- phần nào hardcoded;
- phần nào fixture-specific;
- phần nào lesson-specific;
- phần nào có thể tái sử dụng.

REUSE BEFORE ADDING.

Không xây Semantic Graph thứ hai nếu model hiện tại
đã có representation tương đương.

==================================================
3. IMPORTANT ARCHITECTURAL BOUNDARY
==================================================

Phải giữ rõ:

SOURCE TRUTH
!=
SEMANTIC INTERPRETATION
!=
VISUAL REPRESENTATION.

Ví dụ:

Trusted Source:
“...”

Semantic interpretation:
CAUSE(A,B)

Visual representation:
arrow A → B.

Visual arrow KHÔNG phải source truth.

Một node/edge do AI suy ra phải có provenance
và semantic validation tương ứng.

Required conceptual chain:

SourceBlock(s)
→ SemanticClaim
→ Validation
→ SemanticNode/Edge
→ VisualElement.

Không tạo:

LLM says relationship
→ graph truth.

==================================================
4. RESEARCH A GENERAL SEMANTIC ONTOLOGY
==================================================

Không thiết kế ontology theo từng lesson.

Research một minimal cross-subject semantic vocabulary.

Candidate primitives để kiểm chứng:

CONCEPT
DEFINITION
PERSON
PLACE
EVENT
DATE
FACT
RULE
PRINCIPLE
CAUSE
EFFECT
PROCESS
PROCESS_STEP
CATEGORY
EXAMPLE
PROPERTY
OBJECT
SYSTEM
COMPONENT
FORMULA
QUANTITY
OBSERVATION
EVIDENCE
QUESTION
...

Candidate relationships:

IS_A
PART_OF
HAS_PROPERTY
DEFINED_AS
EXAMPLE_OF
CAUSES
LEADS_TO
BEFORE
AFTER
DEPENDS_ON
LOCATED_AT
ASSOCIATED_WITH
COMPARES_WITH
CONTRASTS_WITH
CONSISTS_OF
INPUT_TO
OUTPUT_OF
...

ĐÂY CHỈ LÀ CANDIDATE LIST.

Không copy nguyên list thành schema production.

Hãy dùng corpus thực để:

DISCOVER
→ CLUSTER
→ MINIMIZE
→ VALIDATE.

Ưu tiên ontology nhỏ nhưng composable.

==================================================
5. DOMAIN EXTENSIONS
==================================================

Kiểm tra hypothesis:

CORE SEMANTIC GRAPH
        +
DOMAIN EXTENSIONS.

Ví dụ:

Math
→ MathExpression / Math AST

Physics
→ Quantity / Unit / Symbol

Chemistry
→ ChemicalFormula / ChemicalReaction

History
→ Event / Person / Date / CauseEffect

Geography
→ Spatial / Place / Region

Science
→ Process / Observation / Experiment

Literature
→ Character / Event / Theme / Attribution

Không mặc định tất cả các extension trên đều cần.

Census phải chứng minh.

Mục tiêu:

domain-specific semantics cắm vào một core model chung,

KHÔNG:

ToánGraph
HistoryGraph
ScienceGraph
VietnameseGraph
...

thành các kiến trúc độc lập.

==================================================
6. VISUAL GRAMMAR RESEARCH
==================================================

Tách:

ACTIVITY PATTERN
khỏi
KNOWLEDGE VISUALIZATION PATTERN.

Không suy luận rằng 27 Activity Patterns
=> cần 27 renderer.

Research minimal visual families.

Candidate hypotheses:

HIERARCHY
→ Mindmap / Concept Tree

CHRONOLOGY
→ Timeline

SEQUENCE / PROCEDURE
→ Process Flow

CAUSE_EFFECT
→ Causal Diagram

COMPARISON
→ Comparison Matrix / Split View

CLASSIFICATION
→ Classification Tree

SYSTEM
→ System Diagram

SPATIAL
→ Map / Spatial View

QUANTITATIVE
→ Chart

RELATIONSHIP NETWORK
→ Concept Graph

FORMULA_RELATIONSHIP
→ Formula / Quantity Diagram

Đây là candidate set.

Census phải trả lời:

thực tế cần bao nhiêu visual families?

==================================================
7. COMPOSITION IS IMPORTANT
==================================================

Không giả định:

ONE LESSON = ONE VISUAL.

Một lesson có thể có:

Timeline
+
Cause/Effect
+
Concept hierarchy.

Research compositional VisualSpec.

Ví dụ conceptual:

VisualLesson
├── primaryView
├── secondaryViews[]
└── sections[].

Hoặc representation tương đương.

Không over-engineer schema trước POC.

==================================================
8. FULL K–12 CENSUS
==================================================

Dùng canonical denominator:

3,679 lessons.

Nhưng phải tôn trọng trạng thái dữ liệu hiện tại.

Không được gọi semantic extraction từ untrusted OCR
rồi báo đó là validated knowledge.

Census có thể dùng các tier:

A. source/semantic evidence đủ mạnh
B. candidate/hypothesis
C. insufficient source
D. modality/domain extension required
E. exception/unknown.

Mỗi metric phải ghi rõ denominator.

Census cần trả lời tối thiểu:

1. Bao nhiêu lesson map được vào semantic primitives chung?
2. Bao nhiêu lesson cần domain extension?
3. Bao nhiêu lesson chứa nhiều visual pattern?
4. Bao nhiêu lesson không map được?
5. Visual family frequency?
6. Semantic primitive frequency?
7. Relationship frequency?
8. Subject × visual family?
9. Grade × visual family?
10. Exception clusters là gì?

Không dùng LLM classification một lần rồi coi là ground truth.

Nếu dùng LLM cho census:
- record model/prompt/version;
- deterministic schema;
- confidence;
- source evidence;
- bounded independent review.

==================================================
9. GENERALIZATION TEST
==================================================

Đây là phần P0.

Không đánh giá bằng:

“demo nhìn đẹp”.

Đánh giá bằng:

GENERALIZATION.

Chọn representative lessons từ nhiều domain.

Tối thiểu research/POC nên có:

- KHTN
- Lịch sử
- Địa lý
- Toán
- Tiếng Việt / Ngữ văn
- Tin học
- English nếu source đủ.

Không cần tất cả trở thành production UI.

Mục tiêu là kiểm tra:

một semantic/visual grammar có reuse được
cross-subject hay không.

==================================================
10. BOUNDED POC — DO NOT BUILD EVERYTHING
==================================================

Sau census, chọn khoảng 4–6 visual families
có coverage/value cao nhất.

Không implement 8–12 renderer ngay.

POC ưu tiên những family đã có evidence tốt.

Ví dụ nếu census xác nhận:

Process
Timeline
Hierarchy
Comparison
CauseEffect

có coverage cao,

thì implement/reuse bounded renderers cho chúng.

Mỗi renderer phải nhận VisualSpec,
không nhận lesson ID.

BAD:

if lesson == "KHTN6_BAI17":
   draw_process(...)

GOOD:

ProcessVisualSpec
→ ProcessRenderer.

Không hardcode subject-specific screen.

==================================================
11. VISUAL SPEC
==================================================

Research một intermediate VisualSpec.

Ví dụ conceptual only:

VisualSpec
- type
- title
- nodes
- edges
- groups
- ordering
- emphasis
- sourceRefs
- confidence/trust
- accessibility metadata.

Renderer chỉ được render VisualSpec.

Renderer không tự suy luận kiến thức.

Semantic layer quyết định meaning.

Visual layer quyết định representation.

==================================================
12. AI ROLE
==================================================

AI/LLM được phép:

- propose semantic nodes;
- propose relationships;
- classify semantic patterns;
- propose visual family;
- propose VisualSpec;
- explain ambiguity.

Nhưng:

LLM OUTPUT != VALIDATED KNOWLEDGE.

LLM không được:

- invent facts;
- invent dates;
- invent causal relationships;
- silently add missing concepts;
- transform uncertain OCR into trusted graph;
- produce arbitrary learner-facing mindmap as truth.

Desired flow:

Trusted Content
→ LLM SemanticCandidate
→ source grounding
→ schema validation
→ deterministic/domain validation where possible
→ validated/proposed graph.

Nếu relationship chỉ là inference:

phải giữ trạng thái/provenance tương ứng.

==================================================
13. RUNTIME COST / OFFLINE-FIRST
==================================================

Research hypothesis:

semantic extraction có thể chủ yếu PRECOMPUTE.

Expected target:

PREPROCESS

Trusted Lesson
→ semantic graph
→ VisualSpec candidates
→ validation
→ versioned artefact.

RUNTIME

VisualSpec
→ renderer.

Không gọi Claude/Gemini mỗi lần learner mở mindmap
nếu visual đã có thể precompute.

Đo:

- runtime LLM calls;
- latency;
- artefact size;
- rendering performance;
- cacheability;
- deterministic replay.

==================================================
14. EDITABILITY / HUMAN CORRECTION
==================================================

Founder không muốn edit pixel từng lesson.

Nếu human correction cần thiết,
ưu tiên edit:

SEMANTIC GRAPH
hoặc
VISUAL SPEC

thay vì edit Flutter screen.

Ví dụ:

wrong relation
→ sửa edge.

wrong visual family
→ đổi VisualSpec.type.

missing event
→ add validated semantic node/sourceRef.

Sau correction:

renderer tự regenerate.

Research bounded editor/data workflow,
chưa cần build full CMS.

==================================================
15. LEARNING FROM EXCEPTIONS
==================================================

Exception không được giải quyết ngay bằng lesson-specific code.

Khi một lesson không represent được:

record:

UnsupportedSemanticPattern
hoặc
UnsupportedVisualPattern.

Cluster exceptions.

Nếu cùng pattern xuất hiện nhiều lần:

extend grammar ONCE
→ many lessons benefit.

Founder principle:

FIX THE LANGUAGE,
NOT 100 INDIVIDUAL LESSONS.

==================================================
16. RELATIONSHIP WITH THREE LEARNING VIEWS
==================================================

Phải chứng minh architecture hỗ trợ:

📖 ĐỌC
→ Trusted Structured Learning Content

✨ TRỰC QUAN
→ Validated Semantic Graph
→ VisualSpec
→ Renderer

🦉 HỌC VỚI SAM
→ Trusted Source
+ Semantic Graph
+ Pedagogy Runtime
+ Student State.

Semantic Graph có thể là shared semantic substrate.

Nhưng:

không tự động biến graph thành Pedagogy Truth.

Pedagogy Runtime vẫn quyết định:
- được dạy gì;
- method nào được phép;
- hỏi gì;
- evidence nào hợp lệ.

==================================================
17. RELATIONSHIP WITH STRUCTURED LEARNING CONTENT
==================================================

Tích hợp nghiên cứu này với finding mới của Round 5:

structure preservation là cross-domain P0.

Math:
fraction/exponent geometry

Poetry:
line/stanza structure

Dialogue:
speaker + utterance

Procedure:
label + steps

Question:
stem + options

Figure:
figure + caption

Table:
rows/columns

Không tạo semantic graph từ flat text
nếu source structure cần thiết đã bị mất.

Required principle:

SOURCE STRUCTURE
→ SEMANTIC STRUCTURE
→ VISUAL STRUCTURE.

==================================================
18. PROVENANCE
==================================================

Mỗi learner-visible semantic assertion phải trace được.

Desired conceptual lineage:

VisualElement
→ VisualSpec element
→ SemanticNode / SemanticEdge
→ SemanticClaim
→ SourceBlock(s)
→ TrustedLearningSource
→ page/bbox/provenance.

Nếu semantic relation không directly stated:

record inference status.

TRACE != EVIDENCE.

Do not fake provenance.

==================================================
19. METRICS
==================================================

Create a GENERALIZATION SCOREBOARD.

At minimum:

CANONICAL LESSONS
SEMANTICALLY CLASSIFIABLE
COMMON-CORE COVERAGE
DOMAIN-EXTENSION REQUIRED
UNSUPPORTED/UNKNOWN

VISUAL-FAMILY COVERAGE
MULTI-VISUAL LESSON RATE
EXCEPTION RATE

AUTO-GENERATED
HUMAN-ASSISTED
MANUAL-EXCEPTION

SOURCE-GROUNDED NODE PRECISION
SOURCE-GROUNDED EDGE PRECISION

VISUAL PATTERN ACCURACY
VISUAL SPEC VALIDITY

HUMAN CORRECTION RATE

RUNTIME LLM CALLS
PRECOMPUTED RATE.

Do not create one combined vanity score.

==================================================
20. IMPORTANT — DO NOT FAKE COVERAGE
==================================================

Do not claim:

“80% of K–12 supported”

because an LLM managed to output JSON for 80%.

SUPPORTED means the architecture can:

source
→ represent
→ validate
→ render

without inventing teaching truth.

Separate:

REPRESENTABLE
SEMANTICALLY EXTRACTABLE
VALIDATABLE
VISUALIZABLE
LEARNER-READY.

==================================================
21. EXPECTED ROUND OUTPUT
==================================================

Deliver:

A. CURRENT ARCHITECTURE AUDIT

B. SEMANTIC ONTOLOGY CANDIDATE
with evidence from real corpus.

C. VISUAL GRAMMAR CANDIDATE
with frequency/coverage evidence.

D. 3,679-LESSON CENSUS
with honest denominators.

E. EXCEPTION TAXONOMY

F. DOMAIN EXTENSION ANALYSIS

G. GENERALIZATION POC
on representative cross-subject lessons.

H. VISUALSPEC POC

I. 4–6 bounded reusable renderers
ONLY if census supports them.

J. GENERALIZATION SCOREBOARD

K. DEVICE EVIDENCE
for learner-visible POC if safe/available.

L. RECOMMENDATION:

GO
GO WITH ARCHITECTURE CHANGE
MORE EVIDENCE
NO-GO

for generalized Visual Learning.

==================================================
22. FOUNDER QUESTIONS
==================================================

Final report must answer directly:

1. Có thể tổng quát hóa Visual Learning cho K–12 không?

2. Bao nhiêu semantic primitives thực sự cần?

3. Bao nhiêu visual families thực sự cần?

4. Bao nhiêu % lesson có thể dùng common grammar?

5. Bao nhiêu % cần domain extension?

6. Bao nhiêu % thực sự cần manual exception?

7. Những môn nào generalize tốt nhất/kém nhất?

8. Một renderer có reuse cross-subject thật không?

9. LLM cần ở preprocess, runtime, hay cả hai?

10. Có cần edit từng lesson không?

11. Khi phải human edit, edit Semantic Graph/VisualSpec có đủ không?

12. Những source-structure gaps nào đang chặn visualization?

13. Architecture này có reuse được cho SAM Tutor không?

14. Chi phí để scale từ POC → 3,679 lessons là gì?

15. Bottleneck tiếp theo là:
    source accuracy,
    semantic extraction,
    validation,
    visual grammar,
    renderer,
    hay human review?

==================================================
23. GOVERNANCE
==================================================

Claude được autonomous cho:

- audit;
- research;
- census;
- scripts/tooling;
- tests;
- schemas/prototypes;
- bounded renderer POC;
- docs;
- screenshots/device evidence khi protocol cho phép;
- Jira/Confluence updates;
- branch + PR.

Founder gate:

- major irreversible architecture replacement;
- production trust thresholds;
- mass uncontrolled LLM generation;
- mass corpus rewrite;
- licensing/public textbook content;
- destructive migration;
- paid external infrastructure;
- public release.

Do NOT merge.

Stop at:

READY FOR FOUNDER REVIEW.

==================================================
24. FOUNDER PRINCIPLE
==================================================

Không xây:

3,679 lessons
→ 3,679 custom visualizations.

Hãy kiểm chứng khả năng xây:

TRUSTED STRUCTURED CONTENT
        ↓
GENERAL SEMANTIC LANGUAGE
        ↓
SMALL VISUAL GRAMMAR
        ↓
REUSABLE RENDERERS
        ↓
THOUSANDS OF LESSONS.

Nếu 100 lessons cùng fail vì một pattern:

không sửa 100 lessons.

Hãy hỏi:

“Ngôn ngữ của SAM đang thiếu primitive,
relationship hay visual grammar nào?”

Fix the abstraction when evidence supports it.

Accuracy and pedagogical truth remain above coverage.

Continue autonomously.
READY FOR FOUNDER REVIEW.
