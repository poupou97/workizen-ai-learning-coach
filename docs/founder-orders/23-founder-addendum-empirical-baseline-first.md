# FOUNDER ADDENDUM — EMPIRICAL BASELINE FIRST
## AS-IS → THEORY → TO-BE → PRODUCT EXPERIENCE

This is an ADDENDUM to the existing:

HỌC CÙNG SAM — Education Data Architecture,
Deep Research Method & UI/UX Connection

Master Task Order.

It does NOT replace the previous order.

The purpose of this addendum is to correct one important risk:

DO NOT DESIGN SAM'S EDUCATION DATA ARCHITECTURE
FROM AN IDEALIZED GRAPH / ONTOLOGY FIRST.

Học cùng SAM already contains substantial
empirically-proven learning architecture.

Research must start from that truth.

==================================================
1. USE THE LATEST REVIEW BUNDLE AS BASELINE
==================================================

Use the latest:

HOC-CUNG-SAM-K12-REVIEW

as the empirical baseline.

Cross-check against current repo/Jira/Confluence
because the bundle may already be behind current main.

Important existing evidence includes at least:

- WAL-190 Experiment
- Ngữ văn raw-OCR falsification
- WAL-192 Source-Grounded Assessment
- WAL-193 Product Experience defect
- SkillCase / Method
- Pedagogy Runtime / PlannedAct
- LearningEvidence
- EvidenceValidator
- Student/mastery state
- Bookshelf / Learning Map
- existing Learning Surfaces
- Breadth × Depth × UX Matrix
- current 38 AI-first concepts
- CONCEPT-TO-PRODUCTION-PLAN.

Do not assume these are perfect.

But do not ignore or replace them without evidence.

==================================================
2. FIRST OUTPUT: AS-IS EVIDENCE-BACKED ARCHITECTURE
==================================================

Before researching an ideal future architecture,
reverse-engineer:

AS-IS SAM LEARNING ARCHITECTURE.

This must describe what the current system
ACTUALLY proves today.

Not what docs say it intends to become.

Use:

CODE
TESTS
REAL CORPUS
GOLD SETS
DEVICE EVIDENCE
JIRA EVIDENCE
FALSIFIED EXPERIMENTS.

Build an evidence-backed model covering, where present:

SOURCE
↓
STRUCTURE
↓
KNOWLEDGE
↓
PEDAGOGY
↓
ACTIVITY / EXPERIENCE
↓
SAM / TOOL / SURFACE
↓
LEARNER ACTION
↓
CANDIDATE EVIDENCE
↓
EVIDENCE VALIDATION
↓
LEARNER STATE
↓
ADAPTATION / NEXT ACTION
↓
PRODUCT EXPERIENCE.

Do not force this exact decomposition
if current evidence contradicts it.

==================================================
3. RECONSTRUCT REAL PROVEN CHAINS
==================================================

Use real cases to reconstruct architecture.

--------------------------------
CASE A — WAL-190
--------------------------------

Show the complete Experiment chain.

Example shape:

SGK source
→ deterministic recognition
→ Experiment Activity
→ Experiment Surface
→ learner interaction
→ CandidateEvidence
→ EvidenceValidator
→ Learning State.

Identify:

PROVEN
PARTIAL
MISSING.

This should become a GOLD REFERENCE
for a connected learning capability.

--------------------------------
CASE B — NGỮ VĂN
--------------------------------

Represent the falsification explicitly.

Raw OCR text
-X→ Trusted Reading Passage.

Show discovered missing capability:

PDF Layout
→ Content Region
→ Main Passage / Sidebar / Footnote
→ trusted semantic extraction.

Do NOT revive phrase-blacklist/per-book heuristics.

--------------------------------
CASE C — WAL-192
--------------------------------

Represent:

SGK Question
+
Pedagogical Role
+
SGV Answer
→ Source-Grounded Assessment.

Important:

Represent separately:

TECHNICAL VALIDITY
TRUST
BREADTH / YIELD
UX MATURITY
PRODUCT PRIORITY.

WAL-192 demonstrates an important principle:

PROVEN
does NOT automatically mean
HIGH COVERAGE
or
BUILD NOW.

Architecture truth
!=
Capability maturity
!=
Product priority.

--------------------------------
CASE D — WAL-193
--------------------------------

Use WAL-193 as Product Experience evidence.

It demonstrates:

BACKEND PROVEN
+
UI EXISTS
!=
PRODUCT EXPERIENCE VALID.

Architecture review must therefore include
real UI/UX consumption,
not merely presence of a screen.

==================================================
4. DO NOT USE ONE STATUS FOR EVERYTHING
==================================================

Claude must evaluate at least three independent dimensions.

A. EPISTEMIC STATUS

Examples:

PROVEN
PARTIAL
HYPOTHESIS
FALSIFIED
MISSING.

B. CAPABILITY MATURITY

Examples:

DATA_ONLY
BACKEND_ONLY
SURFACE_EXISTS
CONNECTED
PRODUCT_VALIDATED.

C. DECISION / PRIORITY

Examples:

SCALE
IMPLEMENT
RESEARCH_MORE
DEFER
STOP.

Do not collapse these dimensions.

Example:

Source-Grounded Assessment may be:

epistemic:
PROVEN within bounded scope;

breadth:
LOW;

UX:
NOT BUILT;

decision:
DEFER.

This distinction must survive in the proposed model.

==================================================
5. NEGATIVE KNOWLEDGE IS FIRST-CLASS
==================================================

Preserve existing falsifications.

Examples:

Raw OCR
-X→ Trusted Ngữ văn Passage.

A/B/C/D shape
-X→ Automatically Gradable Question.

Browsable Lesson
-X→ Learnable Lesson.

Trace
-X→ LearningEvidence.

Activity Exists
-X→ Valid Evidence.

Do not delete negative knowledge
when architecture evolves.

Research that falsifies a relationship
is a cumulative architecture result.

==================================================
6. ONLY THEN STUDY THEORY / PRIOR ART
==================================================

After AS-IS reconstruction,
compare it against relevant education theory
and implementation references.

At minimum evaluate:

Knowledge Space Theory
Competence-Based KST
Knowledge Components
Evidence-Centered Design
Bayesian Knowledge Tracing
Curriculum / Competency Graphs
Educational Knowledge Graphs
1EdTech CASE / OpenCASE
Learning Commons Knowledge Graph
Vanderbilt Knowledge Spaces
pyBKT
prerequisite / learning progression research.

Do NOT ask:

"How can SAM implement KST?"

Ask:

"What problem in CURRENT SAM
does KST solve better?"

Likewise for every theory/repository.

==================================================
7. REQUIRED THEORY COMPARISON
==================================================

For each important external concept classify:

RETAIN
= current SAM already has a suitable equivalent.

FORMALIZE
= current SAM has the concept implicitly,
  but needs explicit semantics/contracts.

EXTEND
= current model is sound but incomplete.

REPLACE
= evidence shows current abstraction is wrong.

REJECT
= external pattern does not fit SAM.

HYPOTHESIS
= potentially useful but not yet proven.

Examples requiring explicit evaluation:

Concept
SkillCase
Method
Knowledge Component

and:

current mastery/BKT
vs
Knowledge Space / Knowledge Frontier.

Do not rename/restructure existing concepts
merely to align terminology with academic literature.

==================================================
8. SECOND OUTPUT: TO-BE CANDIDATE ARCHITECTURE
==================================================

Only after:

AS-IS
+
REAL EVIDENCE
+
THEORY COMPARISON

produce:

TO-BE CANDIDATE SAM EDUCATION DATA ARCHITECTURE.

Show explicitly:

AS-IS
        ↓
evidence / falsification
        ↓
theory / prior art
        ↓
architecture gap
        ↓
TO-BE proposal.

Every meaningful TO-BE change must answer:

WHAT PROBLEM DOES THIS SOLVE?

WHAT EVIDENCE JUSTIFIES IT?

WHAT DATA CHANGES?

WHAT QUERY/DECISION BECOMES POSSIBLE?

WHAT PRODUCT CAPABILITY USES IT?

WHAT UI/UX CONSUMES IT?

WHAT CHILD/PARENT VALUE RESULTS?

==================================================
9. GRAPH IS A HYPOTHESIS, NOT THE GOAL
==================================================

Evaluate whether the best architecture representation is:

one unified graph;

multiple linked graphs;

typed architecture registry;

relational model;

JSON/JSONL;

graph + registry;

or another hybrid.

A preferred hypothesis to challenge is:

MACHINE-READABLE TYPED REGISTRY
        ↓
generated Architecture Graph views
        ↓
linked Capability Matrix
        ↓
linked UI/UX Concept Matrix.

Do NOT assume this is correct.

Graph may be:

a conceptual model;

a generated visualization;

a query structure;

a runtime representation;

or unnecessary.

Do NOT introduce a graph database
unless runtime requirements justify it.

==================================================
10. KEEP THREE DIFFERENT QUESTIONS SEPARATE
==================================================

Do NOT replace the existing
Breadth × Depth × UX Matrix with a graph.

Maintain separate but linked views.

--------------------------------
A. ARCHITECTURE GRAPH / MODEL
--------------------------------

Answers:

HOW DOES THE LEARNING OS RELATE?

Example:

Curriculum
→ SkillCase
→ Pedagogy
→ Activity
→ Evidence
→ State.

--------------------------------
B. BREADTH × DEPTH × UX MATRIX
--------------------------------

Answers:

HOW MATURE IS EACH CAPABILITY?

Examples:

Experiment
Reading
Assessment
Camera
Parent
Next Action.

--------------------------------
C. CONCEPT ↔ DATA CAPABILITY MATRIX
--------------------------------

Answers:

WHERE DOES THE CHILD/PARENT
EXPERIENCE THIS CAPABILITY?

Examples:

Home
Bookshelf
Lesson
SAM Workspace
Why
Source
Review
Parent.

Do not collapse these into one unreadable artifact.

==================================================
11. DEEP RESEARCH OUTPUT CONTRACT
==================================================

For every future meaningful deep-research task,
evaluate the following chain:

QUESTION
↓
CURRENT SYSTEM / ARCHITECTURE GAP
↓
THEORY / PRIOR ART
↓
HYPOTHESIS
↓
WHAT WOULD FALSIFY IT
↓
CORPUS / SOURCE EVIDENCE
↓
GOLD SET / TEST
↓
RESULT
↓
CUMULATIVE LEARNING-SYSTEM DELTA
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

Do not require artificial graph changes.

Use the broader invariant:

NO DEEP RESEARCH WITHOUT
A CUMULATIVE LEARNING-SYSTEM DELTA.

A valid delta may be:

architecture relation added;

relationship proven;

relationship falsified;

confidence strengthened;

new trust boundary;

new reusable capability;

coverage changed;

missing capability discovered;

product connection established;

UI shell discovered;

architecture hypothesis rejected.

==================================================
12. DATA ARCHITECTURE MUST ANSWER REAL QUERIES
==================================================

Do not judge architecture by diagram elegance.

Test whether it can answer real SAM questions.

At minimum:

--------------------------------
QUERY 1
--------------------------------

"What is this child learning right now?"

Expected inputs may include:

Learner
Grade
Subject
Book
Lesson
Intent
Context.

--------------------------------
QUERY 2
--------------------------------

"What is this child allowed/expected
to learn here?"

Must involve curriculum/pedagogy truth.

--------------------------------
QUERY 3
--------------------------------

"What should SAM do now?"

Must not delegate pedagogical authority
to unrestricted LLM reasoning.

--------------------------------
QUERY 4
--------------------------------

"Why is the child wrong?"

Must trace:

LearnerAction
→ Evidence
→ SkillCase / misconception / prerequisite
→ allowed intervention.

--------------------------------
QUERY 5
--------------------------------

"What should the child learn next?"

Evaluate:

mastery/BKT
+
prerequisite relations
+
possibly Knowledge Space / Learning Frontier.

--------------------------------
QUERY 6
--------------------------------

"Why is SAM teaching this?"

Trace:

PlannedAct
→ pedagogy
→ source/provenance
→ SGK/SGV.

--------------------------------
QUERY 7
--------------------------------

"What should the parent know?"

Evidence
→ learner interpretation
→ ParentInsight

without sibling ranking/surveillance.

If the proposed architecture cannot answer
real learning/product questions,
challenge its usefulness.

==================================================
13. RETRIEVAL MUST CONNECT TO ARCHITECTURE
==================================================

Explicitly evaluate:

LearningContext
        ↓
Curriculum / Knowledge boundary
        ↓
Pedagogy permission
        ↓
Source search boundary
        ↓
BM25 / FTS / lexical retrieval
        ↓
exact SGK/SGV evidence
        ↓
provenance
        ↓
PlannedAct
        ↓
SAM realization.

Determine:

what Graph/relations decide;

what BM25 decides;

where semantic retrieval is useful;

where lexical retrieval is safer;

how page/region/source survives;

what happens when confidence is insufficient.

Remember:

RETRIEVED != PERMITTED.

==================================================
14. EVERY DATA CAPABILITY NEEDS A PRODUCT CONSUMER
==================================================

For every meaningful data capability identify:

DATA
↓
RUNTIME DECISION
↓
PRODUCT CAPABILITY
↓
UI/UX SURFACE
↓
USER VALUE.

Examples:

Prerequisite relation
+
Student State
↓
Learning Frontier
↓
Next Best Learning Action
↓
Home / Learning Map
↓
"Con nên học gì tiếp?"

--------------------------------

Source provenance
↓
trusted explanation
↓
Why / Source
↓
exact SGK/SGV context
↓
"Vì sao SAM dạy như vậy?"

--------------------------------

PedagogicalRole
↓
interaction semantics
↓
SAM Workspace / Assessment
↓
discussion is not graded as MCQ.

--------------------------------

LearningEvidence
↓
Student State
↓
Review / Learning Map / Parent
↓
progress reflects actual learner behavior.

==================================================
15. AUDIT THE 38 CONCEPTS AGAINST REAL DATA
==================================================

Use:

concept/concept-ai-first/

and:

CONCEPT-TO-PRODUCTION-PLAN.md.

For each relevant concept determine:

WHAT DATA DOES THIS EXPERIENCE REQUIRE?

DOES THAT DATA EXIST?

IS IT TRUSTWORTHY?

WHAT RUNTIME DECISION POWERS IT?

IS IT:

DATA_CONNECTED
PARTIAL
BACKEND_ONLY
SHELL_ONLY
MISSING
SUPERSEDED?

Identify both directions:

BACKEND CAPABILITY
with no visible learner experience;

and:

BEAUTIFUL CONCEPT/UI
with no trustworthy learning intelligence underneath.

WAL-193 should be used as evidence
that UI presence alone is insufficient.

==================================================
16. REQUIRED VISUAL OUTPUTS
==================================================

Founder must be able to review the result visually.

Produce small readable views.

At minimum:

A. AS-IS SAM LEARNING ARCHITECTURE

B. TO-BE CANDIDATE ARCHITECTURE

C. AS-IS → TO-BE DELTA

D. SOURCE / KNOWLEDGE / PEDAGOGY /
   EVIDENCE / ADAPTATION flow

E. UI/UX CONNECTION VIEW.

Prefer generated Mermaid/Graphviz
or another maintainable representation.

Do not produce one giant 500-node diagram.

Founder should understand the executive architecture
in under 5 minutes.

==================================================
17. JIRA — LOG THIS ADDENDUM
==================================================

Update the bounded Education Data Architecture
research workstream created/reused by the Master Task Order.

Do NOT create duplicate tickets.

Ensure Jira contains explicit TODO/evidence for:

[ARCH]
Reverse-engineer AS-IS evidence-backed
SAM Learning Architecture.

[ARCH]
Reconstruct WAL-190 / Ngữ văn /
WAL-192 / WAL-193 architecture cases.

[RESEARCH]
Compare AS-IS architecture against
KST / KC / CASE / ECD / BKT / Education KG.

[ARCH]
Classify external patterns:
RETAIN / FORMALIZE / EXTEND /
REPLACE / REJECT / HYPOTHESIS.

[ARCH]
Propose TO-BE candidate Education Data Architecture.

[ARCH]
Validate TO-BE architecture against real SAM queries.

[UX/ARCH]
Map Data Architecture to 38 AI-first concepts.

[PRODUCT/ARCH]
Update Breadth × Depth × UX Matrix
without replacing it with graph.

[ARCH]
Produce AS-IS / TO-BE / Delta visual review.

[ARCH]
Founder Review — Education Data Architecture Proposal.

Keep tickets medium-sized.

Use existing tickets if equivalent work exists.

==================================================
18. IMPORTANT JIRA STATUS RULE
==================================================

This architecture proposal is NOT considered DONE
when research/documents are finished.

Final review ticket must stop at:

READY FOR FOUNDER REVIEW.

Report:

AS-IS
THEORY COMPARISON
TO-BE
ARCHITECTURE DELTA
DATA MODEL
REAL QUERY VALIDATION
UI/UX IMPACT
BREADTH × DEPTH × UX IMPACT
RISKS
COUNTERARGUMENT
UNPROVEN HYPOTHESES
SMALLEST V1
JIRA TODO STATUS.

Then wait for:

FOUNDER + GPT REVIEW.

Do NOT adopt the new architecture before approval.

==================================================
19. EXISTING AUTONOMOUS WORK
==================================================

Do not unnecessarily stop already-authorized
reversible engineering work.

But do NOT allow other workstreams
to implicitly adopt this proposed architecture
before the review gate.

If WAL-192 has already reached its gate,
use its final evidence.

Do not reopen it merely to satisfy this task.

==================================================
20. FINAL FOUNDER PRINCIPLE
==================================================

Học cùng SAM must grow:

BROAD
+
DEEP
+
VISIBLE IN PRODUCT EXPERIENCE.

Founder does not want:

research
→ report
→ forgotten.

Nor:

graph
→ beautiful diagram
→ no runtime value.

Nor:

backend
→ proven
→ invisible to child.

Nor:

UI
→ beautiful
→ no learning truth.

The required cumulative chain is:

REAL EVIDENCE
        ↓
AS-IS ARCHITECTURE
        ↓
EDUCATION THEORY / PRIOR ART
        ↓
FALSIFICATION / VALIDATION
        ↓
TO-BE DATA ARCHITECTURE
        ↓
LEARNING INTELLIGENCE
        ↓
PRODUCT CAPABILITY
        ↓
UI/UX
        ↓
CHILD / PARENT VALUE.

The goal is NOT to make SAM look academically sophisticated.

The goal is to discover,
formalize,
and continuously improve
the architecture that actually makes:

HỌC CÙNG SAM
A BETTER LEARNING SYSTEM.

Research deeply.

But research methodically.

Start from what SAM has actually proven.

Challenge Founder + GPT assumptions.

Propose something better where evidence supports it.

Then stop at:

READY FOR FOUNDER REVIEW

and WAIT FOR FOUNDER + GPT REVIEW.
