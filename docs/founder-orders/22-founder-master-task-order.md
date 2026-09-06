# FOUNDER MASTER TASK ORDER
## HỌC CÙNG SAM — Education Data Architecture, Deep Research Method & UI/UX Connection

MODE:
RESEARCH + ARCHITECTURE REVIEW + JIRA PLANNING

STATUS:
PROPOSAL — NOT YET AN ARCHITECTURE DECISION

REVIEW GATE:
FOUNDER + GPT APPROVAL REQUIRED BEFORE ARCHITECTURE ADOPTION

==================================================
0. FOUNDER INTENT
==================================================

Học cùng SAM phải phát triển đồng thời:

1. BREADTH
   - nhiều lớp;
   - nhiều môn;
   - nhiều lesson;
   - nhiều Learning Activity Pattern;
   - nhiều learning capability.

2. DEPTH
   - hiểu curriculum;
   - hiểu knowledge/prerequisite;
   - hiểu pedagogy;
   - source-grounded;
   - Evidence đáng tin;
   - hiểu learner state;
   - adaptive;
   - biết nên học gì tiếp theo.

3. PRODUCT EXPERIENCE
   - toàn bộ intelligence bên dưới phải tạo ra
     hành vi và trải nghiệm hữu ích trên UI/UX.

Founder cho phép và khuyến khích deep research.

Nhưng:

DEEP RESEARCH KHÔNG ĐƯỢC KẾT THÚC
CHỈ BẰNG REPORT/FINDINGS.

Founder muốn mỗi vòng nghiên cứu sâu tích lũy thành:

RESEARCH
→ EDUCATION THEORY / PRIOR ART
→ DATA ARCHITECTURE
→ LEARNING INTELLIGENCE
→ PRODUCT CAPABILITY
→ UI/UX
→ CHILD / PARENT VALUE.

==================================================
1. FIRST — AUDIT CURRENT TRUTH
==================================================

Trước khi đề xuất kiến trúc mới:

Audit repo + Jira + Confluence + existing research.

Tìm và đối chiếu ít nhất:

- current Curriculum/Knowledge model;
- Concept;
- SkillCase;
- Method;
- prerequisite relations;
- LearningActivity;
- PedagogicalRole;
- TeachingAct;
- PlannedAct;
- AssistancePolicy;
- LearningContext;
- LearningIntent;
- Source/Provenance;
- SGK/SGV model;
- BM25/FTS/retrieval;
- LearningEvidence;
- EvidenceValidator;
- Student Knowledge State;
- mastery/BKT;
- ReviewDue;
- Adaptive Challenge;
- Next Action;
- Bookshelf/Learning Map;
- Parent;
- existing Learning Surfaces;
- existing architecture docs/ADR;
- readiness matrices;
- existing Knowledge Graph work if any.

Also audit:

concept/concept-ai-first/

38 concepts

and:

docs/design/CONCEPT-TO-PRODUCTION-PLAN.md

Do not reinvent things already implemented.

==================================================
2. CORE RESEARCH QUESTION
==================================================

Determine:

WHAT SHOULD THE EDUCATION DATA ARCHITECTURE
OF HỌC CÙNG SAM ACTUALLY BE?

Do not assume the answer is one giant Knowledge Graph.

Founder + GPT currently hypothesize a hybrid may be appropriate:

Curriculum / Knowledge Graph
+
Pedagogy Model
+
Source Index / BM25
+
Evidence Ledger
+
Student Knowledge State
+
Experience / Session Context
+
Product Experience consumers.

But this is only a hypothesis.

Claude MUST challenge it.

==================================================
3. RESEARCH EDUCATION THEORY / PRIOR ART
==================================================

Research and compare relevant foundations.

At minimum evaluate:

- Knowledge Space Theory (KST);
- Competence-Based Knowledge Space Theory;
- Knowledge Components;
- prerequisite / learning progression models;
- Evidence-Centered Design;
- Bayesian Knowledge Tracing;
- Educational Knowledge Graphs;
- Curriculum / Competency Graphs;
- 1EdTech CASE;
- Learning Commons Knowledge Graph;
- Vanderbilt Knowledge Spaces;
- pyBKT;
- educational prerequisite discovery research.

For each:

WHAT PROBLEM DOES IT SOLVE?

WHAT DATA MODEL DOES IT USE?

WHAT DOES SAM ALREADY HAVE?

WHAT SHOULD SAM ADOPT?

WHAT SHOULD SAM ADAPT?

WHAT SHOULD SAM REJECT?

WHAT PRODUCT EXPERIENCE COULD IT ENABLE?

Do not summarize papers/repos merely for documentation.

==================================================
4. RESEARCH REAL REPOSITORIES
==================================================

Inspect implementation, not README only.

Priority references include:

Vanderbilt Knowledge Spaces

Learning Commons Knowledge Graph

1EdTech CASE / OpenCASE

pyBKT

and other high-quality OSS discovered during research.

Inspect where useful:

schemas
data structures
relationships
algorithms
student-state model
prerequisite representation
retrieval
storage
APIs
tests
licensing
maintenance state.

Do not integrate any repo yet.

==================================================
5. DETERMINE THE CORRECT DATA PLANES
==================================================

Evaluate whether SAM should explicitly separate:

--------------------------------------------------
A. CURRICULUM / KNOWLEDGE
--------------------------------------------------

Examples:

Curriculum
Grade
Subject
Book
Chapter
Lesson
LearningObjective
Concept
KnowledgeComponent / SkillCase
Method
Prerequisite.

Relatively stable educational truth.

--------------------------------------------------
B. PEDAGOGY
--------------------------------------------------

Examples:

PedagogicalRole
ActivityPattern
TeachingAct
AssistancePolicy
TutorScope
AllowedMethod
LearningExperienceBlueprint if justified.

Answers:

HOW should this be learned/taught?

--------------------------------------------------
C. SOURCE / RETRIEVAL
--------------------------------------------------

Examples:

SGK
SGV
SourceDocument
Page
ContentRegion
Passage
Keyword
BM25 / FTS index
provenance.

Answers:

WHERE is the supporting source?

--------------------------------------------------
D. LEARNER / EVIDENCE
--------------------------------------------------

Examples:

LearnerAction
Attempt
Assistance
CandidateEvidence
LearningEvidence
EvidenceValidator
mastery
ReviewDue.

Answers:

WHAT has this learner actually demonstrated?

--------------------------------------------------
E. EXPERIENCE / SESSION
--------------------------------------------------

Examples:

LearningIntent
LearningContext
PlannedAct
SAMRealization
LearningTool
LearningSurface
Session.

Answers:

WHAT is happening now?

--------------------------------------------------
F. ADAPTATION
--------------------------------------------------

Examples:

Knowledge State
Knowledge Frontier / Outer Fringe
Adaptive Challenge
Review policy
NextBestLearningAction.

Answers:

WHAT SHOULD THIS LEARNER DO NEXT?

--------------------------------------------------
G. PRODUCT / FAMILY
--------------------------------------------------

Examples:

LearnerProfile
ActiveLearner
Bookshelf
LearningMap
ParentInsight
ClassContext.

Do not force these planes if evidence suggests
a better decomposition.

==================================================
6. GRAPH HYPOTHESIS
==================================================

Evaluate whether graph semantics are appropriate for relations such as:

CONTAINS
TEACHES
REQUIRES
INTRODUCES
REVIEWS
USES_METHOD
HAS_OBJECTIVE
HAS_ACTIVITY
HAS_PEDAGOGICAL_ROLE
SUPPORTED_BY_SOURCE
PROVENANCE_FROM
ANSWERED_BY
REALIZED_BY
GUIDED_BY
PRODUCES
VALIDATED_BY
UPDATES
RECOMMENDS
ADAPTS_TO.

Potential example:

Grade
→ Subject
→ Book
→ Lesson
→ Objective
→ Concept
→ SkillCase
→ Method.

But DO NOT adopt this ontology automatically.

Determine actual node/edge model from evidence.

==================================================
7. GRAPH ≠ GRAPH DATABASE
==================================================

Explicitly evaluate:

Graph as conceptual model?

Graph as machine-readable registry?

Graph as generated visualization?

Graph as runtime data structure?

Graph database?

Do NOT introduce:

Neo4j
or equivalent infrastructure

unless real requirements justify it.

A valid conclusion may be:

typed JSON/relational source of truth
→ generated graph views.

==================================================
8. SOURCE RETRIEVAL / BM25
==================================================

Evaluate architecture such as:

LearningContext
      ↓
Curriculum/Knowledge relations
      ↓
search boundary
      ↓
BM25 / FTS
      ↓
exact SGK/SGV passage
      ↓
provenance
      ↓
Pedagogy Runtime
      ↓
SAM.

Determine:

What should graph/filter decide?

What should BM25 decide?

Where semantic retrieval is actually necessary?

Where exact lexical retrieval is preferable?

How should source/page/region provenance survive retrieval?

What happens when confidence is insufficient?

Remember:

RETRIEVED != PERMITTED.

==================================================
9. KNOWLEDGE SPACE / NEXT BEST LEARNING
==================================================

Specifically investigate whether KST / Knowledge Space concepts
can strengthen:

Student Knowledge State
+
prerequisite graph
+
Next Best Learning Action.

Evaluate concepts such as:

knowledge state
surmise relation
learning space
outer fringe / learning frontier.

Determine whether SAM could reliably support:

"What should this child learn next?"

without allowing an LLM to invent the learning path.

Compare against current simplified BKT/mastery architecture.

Do NOT replace current model without evidence.

==================================================
10. EVIDENCE STATUS / EPISTEMIC MODEL
==================================================

Evaluate how architecture relationships should represent truth.

Possible statuses:

PROVEN
PARTIAL
HYPOTHESIS
FALSIFIED
MISSING.

But challenge these statuses.

Determine whether important relations also need:

scope
confidence
source
evidence strength
version
provenance
limitations.

Examples from existing evidence:

SGK experiment marker
→ Experiment Activity
PROVEN / WAL-190.

Raw OCR
-X→ trustworthy Ngữ văn passage
FALSIFIED.

Layout-aware extraction
→ trustworthy passage
HYPOTHESIS.

A/B/C/D shape
-X→ automatically gradable question
FALSIFIED.

SGK pedagogical role + SGV answer
→ source-grounded assessment
PARTIAL / WAL-192.

Browsable
-X→ Learnable equivalence.

Trace
-X→ Evidence equivalence.

Preserve negative knowledge.

==================================================
11. REQUIRED DEEP RESEARCH METHOD
==================================================

Evaluate and improve this proposed method:

QUESTION
↓
CURRENT ARCHITECTURE GAP
↓
THEORY / PRIOR ART
↓
HYPOTHESIS
↓
EXPECTED ARCHITECTURE DELTA
↓
WHAT WOULD FALSIFY IT
↓
SOURCE / CORPUS EVIDENCE
↓
REPRESENTATIVE GOLD SET
↓
TEST / FALSIFY
↓
RESULT
↓
DATA ARCHITECTURE DELTA
↓
PRODUCT CAPABILITY DELTA
↓
UI/UX CONNECTION
↓
BREADTH / DEPTH IMPACT
↓
DECISION.

Decision:

SCALE
IMPLEMENT BOUNDED
RESEARCH MORE
DEFER
STOP.

Challenge this process if it is too heavy.

==================================================
12. PROPOSED RESEARCH INVARIANT
==================================================

Evaluate this Founder rule:

NO DEEP RESEARCH WITHOUT
A CUMULATIVE LEARNING-SYSTEM DELTA.

A valid delta may be:

- architecture relation added;
- relation proven;
- relation falsified;
- confidence strengthened;
- architecture hypothesis rejected;
- reusable capability discovered;
- trust boundary discovered;
- coverage changed;
- product connection established;
- missing capability discovered.

This intentionally replaces the narrower:

"NO RESEARCH WITHOUT GRAPH DELTA."

Claude should propose a better invariant if necessary.

==================================================
13. ARCHITECTURE → PRODUCT CAPABILITY
==================================================

Every architecture recommendation must identify:

DATA
↓
QUERY / DECISION
↓
RUNTIME CONSUMER
↓
PRODUCT CAPABILITY.

Example:

SkillCase
REQUIRES
SkillCase
+
Student State
↓
Learning Frontier
↓
NextBestLearningAction
↓
"What should I learn next?"

Another:

SGK Question
+
PedagogicalRole
+
SGV TrustedAnswer
↓
deterministic validation
↓
Source-Grounded Assessment.

Do not accept architecture that has no meaningful consumer.

==================================================
14. PRODUCT CAPABILITY → UI/UX
==================================================

Every capability must identify the existing/proposed UI consumer.

Audit at least:

Onboarding
Home
Bookshelf
Book
Chapter/Lesson
Learning Map
Learning Intent
SAM Workspace
Camera
Confirm
Problem Solving
Experiment
Reading
Writing
Assessment
Hint
Your Turn
Why
Source
Review
Result
Next Action
Parent
Voice
Library.

Examples:

--------------------------------------------------
PREREQUISITE / KNOWLEDGE FRONTIER
--------------------------------------------------

Data:
SkillCase prerequisite + learner mastery.

Product:
Next Best Learning Action.

UI:
Home / Learning Map / SAM.

Child sees:
"Con nên ôn phần này trước."

--------------------------------------------------
SOURCE PROVENANCE
--------------------------------------------------

Data:
Activity → SourceRegion → SGK/SGV.

Product:
explainable teaching.

UI:
Why / Source Viewer.

Child sees:
"Theo sách" + exact source.

--------------------------------------------------
PEDAGOGICAL ROLE
--------------------------------------------------

Data:
Activity → DISCUSSION / SELF_CHECK / APPLICATION.

Product:
correct interaction semantics.

UI:
SAM Workspace / Assessment.

SAM does not mark an opinion/discussion prompt wrong.

--------------------------------------------------
LEARNING EVIDENCE
--------------------------------------------------

Data:
LearnerAction → ValidatedEvidence → SkillCase.

Product:
real progress.

UI:
Review / Learning Map / Parent.

--------------------------------------------------
KST / LEARNING FRONTIER
--------------------------------------------------

If validated:

Data:
Knowledge State + prerequisite relations.

Product:
ready-to-learn recommendation.

UI:
Home → Next Action.

==================================================
15. AUDIT THE 38 CONCEPTS AGAINST DATA ARCHITECTURE
==================================================

Build:

CONCEPT ↔ DATA ARCHITECTURE MATRIX.

For each relevant concept determine:

What data does this screen require?

Does that data currently exist?

Is it trustworthy?

What runtime decision powers it?

Is the screen:

DATA_CONNECTED
PARTIAL
BACKEND_ONLY
SHELL_ONLY
MISSING
SUPERSEDED?

Identify:

UI concept waiting for missing architecture;

proven backend capability invisible in UI;

concept whose assumptions conflict with newer architecture;

existing component that should be reused.

Do NOT implement 38 screens.

==================================================
16. REQUIRED REAL QUERY WALKTHROUGHS
==================================================

Use current SAM evidence to model at least these:

CASE A — OPEN REAL LESSON

Child:
opens real Grade/Subject/Book/Lesson.

Show:

UI
→ LearningContext
→ Curriculum/Knowledge query
→ allowed pedagogy
→ source retrieval
→ Learning Experience
→ SAM.

--------------------------------------------------
CASE B — CHILD ANSWERS INCORRECTLY
--------------------------------------------------

Show:

LearnerAction
→ CandidateEvidence
→ EvidenceValidator
→ SkillCase
→ mastery/state
→ prerequisite analysis
→ Next Action
→ UI change.

--------------------------------------------------
CASE C — CHILD ASKS "TẠI SAO?"
--------------------------------------------------

Show:

current context
→ pedagogy decision
→ graph/source boundary
→ BM25 retrieval
→ SGK/SGV provenance
→ explanation
→ Why / Source UI.

--------------------------------------------------
CASE D — PARENT OPENS PROGRESS
--------------------------------------------------

Show:

Evidence
→ learner state
→ learning interpretation
→ ParentInsight
→ Parent UI.

Ensure:

coverage != mastery.

==================================================
17. BREADTH × DEPTH × UX MODEL
==================================================

Propose a lightweight capability matrix:

CAPABILITY
| BREADTH
| DEPTH
| DATA
| UX
| EVIDENCE
| BOTTLENECK
| STATUS.

Seed from current evidence:

Experiment
Reading
Source-Grounded Assessment
Problem Solving
Camera
Learning Map
Next Action
Parent
etc.

This should expose:

broad but shallow;

deep but narrow;

backend-only;

UI shell;

fully connected capability.

==================================================
18. REQUIRED ARCHITECTURE OUTPUTS
==================================================

Create proposal-review artifacts.

At minimum:

docs/research/
SAM-EDUCATION-DATA-ARCHITECTURE-REVIEW.md

docs/architecture/
SAM-EDUCATION-DATA-ARCHITECTURE-PROPOSAL.md

docs/design/
SAM-CONCEPT-DATA-CAPABILITY-MATRIX.md

The architecture proposal must include:

1. Executive architecture diagram.
2. Data planes.
3. Candidate entities/nodes.
4. Candidate relationships/edges.
5. Source-of-truth ownership.
6. Provenance/trust model.
7. Retrieval architecture.
8. Student-state architecture.
9. Adaptation / Next Action architecture.
10. UI/UX consumers.
11. Real query walkthroughs.
12. Existing architecture retained.
13. Proposed changes.
14. Rejected alternatives.
15. Open hypotheses.
16. Falsified assumptions.
17. Risks.
18. Smallest V1.

Also create machine-readable/visual prototype
ONLY if useful for evaluating the proposal.

Do not create production graph infrastructure.

==================================================
19. CLAUDE MUST COUNTERARGUE
==================================================

Explicitly challenge:

- Is Graph actually useful?
- Is this architecture theater?
- Should graph be generated view rather than source of truth?
- Are Concept/SkillCase/Method the right abstractions?
- Should Knowledge Component be introduced?
- Does KST fit Vietnam K–12?
- Does KST conflict with current BKT/mastery?
- Does CASE add useful semantics or unnecessary complexity?
- Should Pedagogy be a graph?
- What belongs in graph vs relational/JSON/BM25?
- How do we prevent stale data?
- How does curriculum versioning work?
- Can inferred prerequisites become dangerous?
- Can this scale without creating 50k+ meaningless nodes?
- Does the architecture actually improve learner experience?

Include:

COUNTERARGUMENT TO CLAUDE'S OWN RECOMMENDATION

and:

WHAT WOULD FALSIFY CLAUDE'S RECOMMENDATION.

==================================================
20. JIRA — CREATE A BOUNDED RESEARCH WORKSTREAM
==================================================

Audit existing WAL issues first.

Reuse/update existing issues where scope already exists.

Do NOT create duplicates.

If no suitable existing Epic exists,
create ONE bounded Epic:

[ARCH] Education Data Architecture & Learning Graph Research

Suggested purpose:

Define and validate how curriculum, knowledge,
pedagogy, source retrieval, learner evidence,
student state and product experience should connect
for Học cùng SAM.

==================================================
21. JIRA TODO BACKLOG
==================================================

Create/reuse bounded Jira issues approximately as follows.

Do NOT blindly create these if equivalent tickets already exist.

--------------------------------
P0 — CURRENT TRUTH
--------------------------------

[ARCH] Audit current SAM learning/data architecture

Output:
current-state architecture map
+
duplication/gaps.

--------------------------------
P0 — THEORY / PRIOR ART
--------------------------------

[RESEARCH] Evaluate Education Graph / KST / KC / CASE / BKT models

Include:

Vanderbilt Knowledge Spaces
Learning Commons KG
1EdTech CASE/OpenCASE
pyBKT
Evidence-Centered Design
prerequisite research.

Output:
adopt/adapt/reject matrix.

--------------------------------
P0 — DATA MODEL
--------------------------------

[ARCH] Propose SAM Education Data Planes

Curriculum
Knowledge
Pedagogy
Source/Retrieval
Evidence
Student State
Experience
Adaptation
Product.

Output:
candidate architecture.

--------------------------------
P0 — GRAPH MODEL
--------------------------------

[ARCH] Evaluate Curriculum / Knowledge / Pedagogy Graph

Output:

candidate nodes
candidate edges
trust/status
scope
versioning
provenance

AND recommendation:

graph / typed registry / relational / hybrid.

--------------------------------
P0 — RETRIEVAL
--------------------------------

[ARCH] Define Graph-Guided Source Retrieval + BM25

Output:

LearningContext
→ search boundary
→ BM25
→ provenance
→ pedagogy
→ SAM.

Compare lexical/semantic/hybrid retrieval.

--------------------------------
P0 — STUDENT MODEL
--------------------------------

[RESEARCH] Evaluate KST Learning Frontier vs current BKT/mastery

Output:

whether/how:

prerequisite graph
+
Student State
→ Next Best Learning Action.

No replacement implementation yet.

--------------------------------
P0 — UI/UX CONNECTION
--------------------------------

[UX/ARCH] Map Education Data Architecture to 38 Concepts

Output:

Concept ↔ Data Capability Matrix

and classifications:

DATA_CONNECTED
PARTIAL
BACKEND_ONLY
SHELL_ONLY
MISSING
SUPERSEDED.

--------------------------------
P0 — REAL QUERY VALIDATION
--------------------------------

[ARCH] Validate architecture with real SAM learner journeys

Required:

Open Lesson
Wrong Answer
Why?
Parent Progress.

Output:

end-to-end data/query/UI traces.

--------------------------------
P1 — NEGATIVE KNOWLEDGE
--------------------------------

[ARCH] Define Architecture Evidence / Falsification Registry

Evaluate representation for:

PROVEN
PARTIAL
HYPOTHESIS
FALSIFIED
MISSING

plus provenance/scope/version/confidence.

--------------------------------
P1 — BREADTH × DEPTH × UX
--------------------------------

[PRODUCT/ARCH] Build capability maturity matrix

Output:

Breadth
Depth
Data
UX
Evidence
Bottleneck.

--------------------------------
P1 — RESEARCH METHOD
--------------------------------

[RESEARCH] Define Deep Research Output Contract

Output:

repeatable:

Research
→ Architecture
→ Capability
→ UI/UX
→ Value

method.

--------------------------------
FINAL REVIEW GATE
--------------------------------

[ARCH] Founder Review — SAM Education Data Architecture Proposal

This ticket is NOT implementation.

Attach/link all outputs.

Summarize:

RECOMMENDED ARCHITECTURE
WHY
WHAT WE KEEP
WHAT CHANGES
WHAT WE REJECT
UI/UX VALUE
RISKS
COST
SMALLEST V1
OPEN DECISIONS.

Status must stop at:

READY FOR FOUNDER REVIEW.

==================================================
22. JIRA ISSUE QUALITY
==================================================

Keep tickets MEDIUM and evidence-oriented.

Each ticket should contain:

QUESTION / GOAL

WHY IT MATTERS

CURRENT EVIDENCE

OUTPUT REQUIRED

ACCEPTANCE EVIDENCE

DEPENDENCIES

DECISION ENABLED.

Avoid giant prompt-like Jira descriptions.

Avoid creating dozens of subtasks.

==================================================
23. TODO EXECUTION ORDER
==================================================

Recommended dependency order:

CURRENT TRUTH
      ↓
THEORY / PRIOR ART
      ↓
DATA PLANES
      ↓
┌─────────────┬──────────────┐
↓             ↓              ↓
GRAPH      RETRIEVAL     STUDENT MODEL
↓             ↓              ↓
└─────────────┴──────┬───────┘
                     ↓
            REAL QUERY VALIDATION
                     ↓
           UI/UX CONCEPT MAPPING
                     ↓
          BREADTH × DEPTH × UX
                     ↓
          RESEARCH METHOD REVIEW
                     ↓
           ARCHITECTURE PROPOSAL
                     ↓
             FOUNDER REVIEW.

Parallelize independent research where useful.

Do not create artificial sequential blockers.

==================================================
24. WAL-192 / CURRENT CONTENT WORK
==================================================

Do not abandon already-authorized bounded work.

WAL-192 should reach its clear gate decision
according to the current Founder instruction.

Its evidence should become one real case
for this architecture review.

Do not let this new research proposal reopen
unbounded content exploration.

==================================================
25. HARD IMPLEMENTATION GATE
==================================================

This Master Task Order authorizes:

research;
repo audit;
theory/repo review;
architecture analysis;
small throwaway models;
documentation;
Jira/Confluence planning;
architecture diagrams;
query walkthroughs;
concept/data mapping;
counterarguments.

It DOES NOT yet authorize:

production architecture rewrite;
graph database introduction;
mass curriculum graph generation;
SkillCase replacement;
Evidence semantic migration;
new mastery model;
KST production adoption;
CASE production adoption;
mass UI implementation based on this architecture;
large migration/refactor.

When proposal reaches sufficient evidence:

STOP THIS ARCHITECTURE PROPOSAL WORKSTREAM.

Set final Jira review issue:

READY FOR FOUNDER REVIEW.

Then report:

==================================================
FOUNDER ACCEPTANCE CARD
==================================================

1. RECOMMENDED ARCHITECTURE

2. WHY

3. DATA ARCHITECTURE DIAGRAM

4. EDUCATION THEORY SUPPORTING IT

5. REPOS / PRIOR ART

6. WHAT CURRENT SAM ALREADY HAS

7. WHAT SHOULD CHANGE

8. WHAT SHOULD NOT CHANGE

9. GRAPH:
   yes/no/hybrid and why

10. BM25 / RETRIEVAL ROLE

11. STUDENT STATE / KST / BKT RELATIONSHIP

12. UI/UX CAPABILITIES ENABLED

13. 38-CONCEPT IMPACT

14. REAL QUERY WALKTHROUGHS

15. BREADTH IMPACT

16. DEPTH IMPACT

17. RISKS

18. COUNTERARGUMENT

19. WHAT REMAINS UNPROVEN

20. SMALLEST V1

21. JIRA TODO STATUS

22. DECISIONS REQUIRED FROM FOUNDER.

Then:

WAIT FOR FOUNDER + GPT REVIEW.

==================================================
26. FINAL FOUNDER PRINCIPLE
==================================================

Founder does NOT want:

research
→ report
→ forgotten.

Founder wants:

research
→ cumulative learning-system knowledge
→ data architecture
→ runtime intelligence
→ product capability
→ UI/UX behavior
→ child/parent value.

Likewise:

DATA ARCHITECTURE IS NOT SUCCESS
IF NO REAL PRODUCT BEHAVIOR CAN CONSUME IT.

And:

UI IS NOT SUCCESS
IF IT HAS NO TRUSTWORTHY LEARNING DATA UNDERNEATH.

The target architecture must connect:

CURRICULUM
→ KNOWLEDGE
→ PEDAGOGY
→ SOURCE
→ EXPERIENCE
→ LEARNER ACTION
→ EVIDENCE
→ STUDENT STATE
→ ADAPTATION
→ NEXT ACTION
→ PRODUCT EXPERIENCE.

Claude must determine whether this exact model is correct.

DO NOT simply agree with Founder + GPT.

Research it.
Challenge it.
Falsify weak assumptions.
Propose something better if warranted.

Then stop at the review gate.

FOUNDER + GPT WILL REVIEW BEFORE ADOPTION.
