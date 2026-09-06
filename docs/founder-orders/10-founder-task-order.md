# FOUNDER TASK ORDER
# SAM MULTI-AGENT LEARNING + ACADEMIC PERSPECTIVE GRAPH
# PRIORITY: P2 / LOW / RESEARCH LATER
# PURPOSE: CAPTURE THE IDEA → RESEARCH → CHALLENGE → SMALL POC LATER

## 1. FOUNDER IDEA

Log một research direction mới cho Học cùng SAM:

SAM Multi-Agent Learning
+
SAM Academic Knowledge & Perspective Graph

Đây KHÔNG phải ưu tiên hiện tại.

Không làm gián đoạn:
- UI/UX production;
- first vertical slice;
- subject-specific learning surfaces;
- current P0/P1 work.

Mục tiêu hiện tại:
1. hiểu đúng ý tưởng Founder;
2. lưu vào Jira để không mất;
3. nghiên cứu khi đến lượt;
4. không over-engineer architecture bây giờ.


## 2. CORE THESIS

Multi-agent trong SAM không chủ yếu nhằm:

“cho nhiều AI cùng suy nghĩ để tạo câu trả lời tốt hơn.”

Founder muốn nghiên cứu:

“Dùng nhiều agent/perspective đại diện cho các tầng kiến thức,
phương pháp, nhân vật học thuật, quan điểm và cách tư duy
để học sinh phải nhớ lại, so sánh, phản biện, giải thích và kiểm chứng.”

Student cognitive work > AI conversation.


## 3. MULTI-LEVEL KNOWLEDGE AGENTS

Ví dụ cùng một bài Vật lý:

- học sinh giỏi lớp 7;
- học sinh giỏi lớp 8;
- học sinh giỏi lớp 9.

Mỗi agent bị giới hạn bởi:

Curriculum Knowledge Boundary của cấp/lớp đó.

Ví dụ:

Problem
  ↓
Applicable Methods
  ├─ Grade 7 Method
  ├─ Grade 8 Method
  └─ Grade 9 Method

SAM có thể dùng chúng để hỏi:

- Con còn nhớ cách lớp trước không?
- Hai cách này khác nhau thế nào?
- Cách nào đơn giản hơn?
- Cách nào con đã được học?
- Kiến thức lớp 9 xây trên kiến thức lớp 7/8 nào?

Mục tiêu:

current problem
→ opportunistic recall of previous knowledge
→ retention evidence
→ deeper understanding.


## 4. ACADEMIC PERSPECTIVE AGENTS

Một dạng agent khác đại diện cho:

- scientist;
- mathematician;
- author;
- historical figure;
- school of thought;
- documented academic perspective.

Ví dụ:

Physics:
Galileo → Newton → Einstein

Chemistry:
Dalton → Thomson → Rutherford → Bohr → modern model

Mathematics:
Euclid → Descartes → alternative mathematical representations

History:
documented perspectives of historical actors

Literature:
author/context/textual evidence/critical interpretations.

Không xây “celebrity chatbot”.

Person phải xuất hiện vì concept thực sự liên quan đến họ.


## 5. IMPORTANT DISTINCTION

Tách:

A. SOLUTION PERSPECTIVE

Một vấn đề có thể giải bằng:
- knowledge level khác nhau;
- method khác nhau;
- representation khác nhau.

B. ACADEMIC PERSPECTIVE

Một concept/theory có thể được nhìn qua:
- người phát triển;
- người phản biện;
- mô hình trước;
- mô hình sau;
- evidence/experiment;
- historical context.

Hai chiều có thể giao nhau trong cùng một bài học.


## 6. EXAMPLE — VELOCITY / MOTION

Không hardcode:

velocity → Newton → Einstein.

Resolver phải bắt đầu từ concept.

Question/Problem
  ↓
Concept Recognition
  ↓
Curriculum Context
  ↓
Student State
  ↓
Relevant Methods
  ↓
Academic History / Perspectives
  ↓
Pedagogical Value
  ↓
SAM decides whether perspective is useful.

Einstein không được xuất hiện chỉ vì nổi tiếng.

Nếu Newtonian perspective đủ cho bài:
không cần Einstein.

Nếu mục tiêu là mở rộng:
có thể cho thấy giới hạn của classical model và góc nhìn relativity.


## 7. HISTORY EXAMPLE

Có thể nghiên cứu:

SAM Historical Council.

Ví dụ một sự kiện có:

Historical Perspective A
Historical Perspective B
Primary Source
Source Critic
Chronology
SAM
Student.

Student có thể đóng vai Judge:

- ai có evidence tốt hơn?
- nguồn nào hỗ trợ claim?
- đâu là fact?
- đâu là interpretation?
- đâu là inference?

Historical person agent phải grounded bằng documented evidence.

Không tự bịa:
- lời nói;
- suy nghĩ riêng;
- cảm xúc;
- động cơ;
- quan điểm chưa có nguồn.


## 8. ACADEMIC GRAPH IDEA

Nghiên cứu một graph có khả năng nối:

Curriculum
Grade
Subject
Lesson
LearningObjective

Concept
SkillCase
Method
Formula
Theorem
Theory
Model

Person
Discovery
Experiment
Evidence
Claim
Source

LearnerState
Misconception
LearningEvidence

Activity.

Không cần implement toàn bộ schema ngay.


## 9. IMPORTANT RELATIONSHIPS TO RESEARCH

Candidate relationships:

introducedAt
buildsOn
requires
applicableTo
alternativeTo
generalizes
specialCaseOf

formulatedBy
proposedBy
discoveredBy
refinedBy
challengedBy
supersededBy

supportedBy
contradictedBy
limitedBy

agreesWith
conflictsWith

illustrates
canBeSolvedBy.

Đây chỉ là candidate ontology.
Research phải được phép thay đổi.


## 10. GRAPH PATTERN THESIS

Founder đặc biệt muốn nghiên cứu:

Graph có thể tự bộc lộ những pattern học tập
mà chúng ta chưa hardcode trước hay không?

Ví dụ:

Grade7 Concept
→ buildsOn
→ Grade8 Concept
→ buildsOn
→ Grade9 Concept

Pattern:
CROSS-GRADE RECALL / SPIRAL KNOWLEDGE.


Theory A
→ contradictedBy Experiment
→ refinedBy Theory B

Pattern:
SCIENTIFIC MODEL EVOLUTION.


Method A
→ alternativeTo Method B
→ same problem

Pattern:
MULTIPLE SOLUTION METHODS.


Claim A
→ conflictsWith Claim B
→ both supported by different sources

Pattern:
ACADEMIC DEBATE.


CurrentProblem
→ requires Concept X
+
Learner weak on Concept X

Pattern:
OPPORTUNISTIC MICRO-REVIEW.


Concept
→ Diagram
→ Formula
→ Experiment

Pattern:
MULTIPLE REPRESENTATIONS.


## 11. GRAPH PATTERN RESOLVER

Research future architecture:

Academic Graph
+
Curriculum Graph
+
Learner Graph
        ↓
Graph Pattern Resolver
        ↓
Learning Opportunity
        ↓
Perspective / Agent Selection
        ↓
Learning Activity
        ↓
Student Response
        ↓
Learning Evidence.

Candidate formula:

Learning Opportunity
=
Graph Pattern
× Learner State
× Curriculum Permission
× Pedagogical Policy.


## 12. POSSIBLE LEARNING PATTERNS

Do not lock these as final.

Research candidates:

CROSS_GRADE_RECALL
MULTIPLE_METHODS
ACADEMIC_DEBATE
SCIENTIFIC_MODEL_EVOLUTION
THEORY_VS_EVIDENCE
CLAIM_VS_SOURCE
COUNTEREXAMPLE
MULTIPLE_REPRESENTATIONS
HISTORICAL_PERSPECTIVES
TEACH_BACK
SPOT_THE_ERROR
TRANSFER
MICRO_REVIEW.


## 13. MULTI-AGENT IS NOT THE UI

Do not expose technical agents like:

Agent 1
Agent 2
Agent 3.

Possible product representations:

“Học cùng nhóm”
“Các bạn giải thế nào?”
“Con còn nhớ cách cũ không?”
“Góc nhìn học thuật”
“Bàn tròn lịch sử”
“Các nhà khoa học đã nghĩ thế nào?”
“Có cách giải khác không?”
“Bắt lỗi lập luận”
“Xem bằng chứng”.

SAM remains the primary product identity.


## 14. IMPLEMENTATION DOES NOT REQUIRE MANY LLM CALLS

Important research question:

Product multi-agent
!=
many autonomous LLM calls.

Possible implementation:

deterministic graph
→ perspective planner
→ one LLM generates constrained perspectives
→ verifier
→ SAM.

Only use real independent agents when evidence shows value.

Evaluate:
- latency;
- cost;
- consistency;
- pedagogical benefit.


## 15. PERSON FOLLOWS CONCEPT

Important hypothesis:

PERSON FOLLOWS CONCEPT.

Not:

CONCEPT FOLLOWS PERSON.

Do not find places to insert Newton/Einstein/etc.

Instead:

Lesson
→ Concept/Theory/Method
→ Academic History
→ Relevant Person
→ Evidence
→ Perspective.

If no meaningful relationship:
do not introduce a person.


## 16. SOURCE / TRUTH BOUNDARY

Historical/scientific/literary personas must not become
unrestricted impersonation engines.

Separate:

SOURCE FACT
DOCUMENTED POSITION
ACADEMIC/HISTORICAL RECONSTRUCTION
SAM EXPLANATION
STUDENT INTERPRETATION.

Do not present reconstructed speech as authentic quotation.


## 17. FUTURE RESEARCH / REPO STUDY

When this P2 workstream reaches execution:

search internet/GitHub/academic references for:

- multi-agent education;
- teachable agents;
- simulated learners;
- pedagogical agents;
- Socratic agents;
- debate agents;
- historical simulation;
- virtual scientist;
- learning companions;
- knowledge graph education;
- epistemic knowledge graphs;
- graph-based tutoring;
- misconception agents;
- multi-perspective learning.

Clone relevant OSS repos where useful.

Study code, architecture and research.

Do not just summarize README.

Challenge the Founder hypothesis.


## 18. FIRST POC — LATER

Do NOT build now.

When priority reaches this workstream,
prefer only 3 bounded experiments:

POC A — Physics / Math
Same problem
→ different grade knowledge boundaries
→ different solution methods
→ recall previous knowledge.

POC B — Science
Theory/model evolution
→ scientist/evidence perspectives
→ learner explains why model changed.

POC C — History
2 documented historical perspectives
+ Source Critic
→ learner evaluates evidence and gives conclusion.

Use real curriculum/source data.


## 19. SUCCESS QUESTION

The POC is NOT successful because:

“the agents produced interesting conversations.”

It succeeds only if evidence suggests the student does more:

RECALL
COMPARE
QUESTION
VERIFY
EXPLAIN
ARGUE
CORRECT
TRANSFER.

If AI talks more but student thinks less:
FAIL.


## 20. JIRA

Audit existing Jira first.

If no suitable workstream exists,
create one umbrella:

SAM — Multi-Agent Learning & Academic Perspective Graph

Priority:
P2 / LOW / RESEARCH LATER.

Candidate medium tickets:

1. Multi-Agent Learning Research
2. Academic Perspective Graph Research
3. Graph Pattern Discovery Research
4. Cross-Grade Knowledge Agent POC
5. Scientific Perspective POC
6. Historical Council POC
7. Cost/Latency/Pedagogical Evaluation

Do not create micro-ticket spam.

Link/depend on current curriculum graph,
Knowledge Stories,
Adaptive Learning Activities
and Student State work where appropriate.


## 21. WHAT TO DO NOW

NOW:

- understand the thesis;
- audit Jira;
- log the research direction;
- link dependencies;
- preserve examples;
- mark P2 / LOW;
- return to current higher-priority work.

DO NOT NOW:

- redesign current architecture around this;
- create dozens of persona agents;
- implement Newton/Einstein chatbots;
- change production UI;
- delay UI/UX work;
- reprocess the full corpus;
- build a generic multi-agent framework.


## FOUNDER THESIS

MULTI-AGENT IN SAM IS NOT ABOUT
MAKING AI TALK TO AI.

IT IS ABOUT MAKING DIFFERENT STRUCTURES OF KNOWLEDGE,
METHODS, EVIDENCE AND PERSPECTIVES VISIBLE TO THE LEARNER.

ACADEMIC GRAPH SHOULD NOT ONLY ANSWER:

“WHAT IS CONNECTED?”

IT SHOULD EVENTUALLY HELP SAM DISCOVER:

“WHAT LEARNING OPPORTUNITY IS HIDDEN
IN THESE CONNECTIONS?”

FOR NOW:
CAPTURE → RESEARCH LATER → CHALLENGE → POC → PROVE.
