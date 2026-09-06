# FOUNDER MASTER TASK ORDER
# HỌC CÙNG SAM — WAL AUTONOMOUS EXECUTION PROGRAM
# Date: 2026-09-01

You are Supervisor / Lead Architect for:

Học cùng SAM
Repo: poupou97/workizen-ai-learning-coach
Jira: WAL
Confluence: WAL

FULL AUTONOMOUS MODE IS ACTIVE.

This order consolidates all current Founder decisions, research findings,
architecture directions, UI/UX benchmarks and safety discoveries.

Do NOT return only a plan.

Your job is:

RECONCILE
→ CREATE/UPDATE JIRA TODO
→ PRIORITIZE
→ EXECUTE
→ TEST/FALSIFY
→ DOCUMENT
→ COMMIT/PUSH
→ CLOSE
→ SELECT NEXT ISSUE
→ REPEAT.

==================================================
0. REPOSITORY / GOVERNANCE TRUTH FIRST
==================================================

Before execution:

1. Verify repo:
   - canonical repo
   - main branch
   - remote synchronized
   - clean/dirty state
   - current test count
   - analyze status.

2. Verify Jira WAL and Confluence WAL.

3. Fix any stale CURRENT documentation.

Known examples to re-check:
- old statements saying Jira/Confluence do not exist
- stale test counts
- old product naming.

Official Founder-approved Vietnamese product name:

HỌC CÙNG SAM

SAM = tutor / mascot identity.

Do not autonomously change final product name or mascot identity.

Mascot baseline:
current purple/yellow owl.

==================================================
1. JIRA IS THE SOLE EXECUTION CONTROL PLANE
==================================================

Inspect ALL current WAL issues before creating new ones.

Do NOT duplicate existing tickets.

Reconcile:

- existing 12+ Epics
- current 49+ issues
- WAL-32 / WAL-33 / WAL-52 Camera work
- WAL-54 many-to-many
- WAL-57 SAM philosophy
- existing UI/UX / mascot / design-system work
- architecture / adaptive-learning work.

For every research finding classify:

ADOPT NOW
POC
FALSIFY
DESIGN
IMPLEMENT
VALIDATE
RESEARCH LATER
REJECT.

Only actionable findings become Jira work.

Each executable Jira issue must include:

WHY
PROBLEM / HYPOTHESIS
SCOPE
ACCEPTANCE CRITERIA
EVIDENCE REQUIRED
DEPENDENCIES
MATURITY TARGET
RELEVANT DOC / ADR / TEST.

Avoid ticket theater.

Do not create 100 micro-tasks for cosmetic details.

==================================================
2. CREATE ONE RANKED READY QUEUE
==================================================

After reconciliation, maintain ONE ranked execution queue.

Priority:

P0 = correctness / safety / foundational architecture
P1 = MVP learning loop
P2 = supporting UX
P3 = polish / future.

Do not maintain a competing hidden TODO list in Markdown.

Repo docs explain knowledge.
Jira determines execution.

==================================================
3. P0 — PEDAGOGICALLY CONSTRAINED AGENT ARCHITECTURE
==================================================

Create/reconcile a P0 workstream:

PEDAGOGICALLY CONSTRAINED AGENT ARCHITECTURE

Core hypothesis to research and falsify:

TASK SUCCESS != LEARNING SUCCESS

MODEL CAPABILITY != PEDAGOGICAL AUTHORITY

A generic agent aims to complete the user's task.

SAM should aim to help the learner increasingly complete the task
independently.

Investigate architecture:

Educational Knowledge
→ Student State
→ Diagnosis
→ Next Best Learning Action
→ Pedagogical Policy
→ TeachingAct
→ Assistance Constraint
→ TutorScope
→ LLM Realization
→ Student Response
→ LearningEvidence
→ Update / Fade.

The LLM should potentially be the realization layer.

Do not let the LLM independently decide:

- what the child should learn next
- which curriculum method is allowed
- assistance depth
- whether answer reveal is allowed
- whether evidence counts as mastery.

Research first.
Do NOT create ACCEPTED ADR until falsification survives.

Create/update:

docs/research/PEDAGOGICALLY-CONSTRAINED-AGENT.md

Separate:

KNOWN FROM LITERATURE
KNOWN FROM OSS
OBSERVED IN WAL
FOUNDER PHILOSOPHY
HYPOTHESIS
FALSIFIED
OPEN QUESTION
CANDIDATE CONTRIBUTION.

==================================================
4. P0 — TEACHINGACT
==================================================

Research TeachingAct as a possible first-class domain abstraction.

Candidate taxonomy ONLY:

OBSERVE
ASK
DIAGNOSTIC_PROBE
PROMPT_RECALL
SMALL_HINT
STRATEGIC_HINT
CONTRAST_CASES
EXPLAIN_CONCEPT
DEMONSTRATE_STEP
WORKED_EXAMPLE
ASK_EXPLANATION
ASK_VERIFICATION
REFLECT
WAIT
STEP_BACK
REVEAL_STEP
REVEAL_ANSWER.

Do not implement this exact list as doctrine.

Research ITS / tutoring literature first.

Falsify:

Method = WHAT domain solution/strategy is used.

TeachingAct = HOW SAM pedagogically intervenes.

Check whether one Method can support multiple TeachingActs
and vice versa.

==================================================
5. P0 — ASSISTANCE / FADING
==================================================

Research an explicit assistance model.

Candidate progression:

INDEPENDENT
→ PROMPT
→ SMALL_HINT
→ STRATEGIC_HINT
→ PARTIAL_SCAFFOLD
→ DEMONSTRATION
→ WORKED_SOLUTION.

Do not hard-code this scale without research evidence.

Core question:

Can SAM choose the MINIMUM SUFFICIENT ASSISTANCE
instead of maximizing immediate correctness?

Investigate:

assisted success
→ future assistance reduction
→ independent success
→ transfer
→ retention.

Founder principle:

SAM succeeds when the learner needs SAM less.

Do not optimize AI dependency.

==================================================
6. P0 — FOUR SEPARATE DIMENSIONS
==================================================

Deepen the OATutor finding.

Formalize/falsify separation of:

TASK CORRECTNESS
ASSISTANCE
MASTERY EVIDENCE
AFFECTIVE FEEDBACK.

Example:

student correct after strong hint:

Correctness = TRUE
Assistance = HIGH
Independent mastery evidence = LOW/NONE
Affective feedback = POSITIVE may still be appropriate.

Do NOT tie praise directly to mastery credit.

Investigate whether TutorFeedback requires a separate domain model.

==================================================
7. P0 — DIAGNOSTIC PROBE
==================================================

Do not assume:

Diagnosis → TeachingAct

is always possible.

Test closed loop:

diagnosis uncertain
→ diagnostic question
→ student answer
→ additional evidence
→ better diagnosis
→ teaching intervention.

Research whether SAM can choose an interaction primarily for
INFORMATION about the learner.

Possible actions to evaluate:

TEACH
PRACTICE
REVIEW
ASSESS
DIAGNOSTIC_PROBE
WAIT / STEP_BACK.

Do not invent information-gain mathematics unless supported.

==================================================
8. P0 — LEARNING EVIDENCE REPLAY / DATA SEMANTICS
==================================================

Actively audit replay correctness.

Current architecture includes:
- mastery at SkillCase
- LearningEvidence append-only
- conceptIds
- ExerciseSkillMap conceptId + skillCaseId.

Question:

If the knowledge graph, Q-matrix, SkillCase definition,
or exercise mapping changes later,
does replay silently reinterpret OLD learner evidence?

Invariant:

HISTORICAL EVIDENCE MUST NOT SILENTLY CHANGE MEANING
BECAUSE THE KNOWLEDGE MODEL CHANGED.

Research whether evidence needs stable lineage such as:

exercise identity
confirmed problem identity
skillCase identity
mapping version
knowledge-model version
TutorScope version
intervention identity.

Do not add every listed field blindly.

Add only what the invariant requires.

==================================================
9. P0 — MANY-TO-MANY / Q-MATRIX
==================================================

Continue/reprioritize WAL-54.

Falsify strict hierarchy:

Concept → SkillCase → Method.

Investigate:

Concept ↔ SkillCase
SkillCase ↔ Method
Method ↔ Concept
TeachingAct ↔ Method.

Do not duplicate Method identity merely because it appears
in multiple curriculum contexts.

Also challenge global conjunctive AND-gate assumptions.

Find examples of:

- truly conjunctive skills
- supporting skills
- alternative methods
- sequential dependencies
- one skill present but not assessed
- ambiguous attribution
- prerequisite failure masquerading as target failure.

Keep:

attributionUnresolved

when evidence cannot isolate the cause.

Q-matrix representation
!=
Q-matrix inference policy.

==================================================
10. P0 — SKILLCASE CONCEPT #3 CROSS-DOMAIN
==================================================

SkillCase survived:
- fraction denominator cases
- decimal comparison cases.

This is encouraging but still mathematical-domain evidence.

Select Concept #3 from ANOTHER SUBJECT where bounded evidence exists.

Prefer:
Vietnamese / language learning
or another non-numeric domain.

Neutral procedure:

Do NOT look for SkillCases.

Ask:

"How does the curriculum/source itself structure meaningful variation?"

Valid conclusions:

KEEP
MODIFY
SPLIT
MERGE
REPLACE
INSUFFICIENT_EVIDENCE.

If SkillCase fails cross-domain:
change architecture.

Do not protect existing code.

==================================================
11. P0 — CAMERA PERCEPTION SAFETY
==================================================

The synthetic degradation POC falsified:

"bad image → fail closed."

Observed failure:

BAD IMAGE
→ wrong OCR
→ plausible valid math expression
→ confident SkillCase classification
→ potentially wrong tutoring
→ potentially false learner evidence.

New invariant:

UNCONFIRMED MACHINE PERCEPTION
MUST NOT ENTER LEARNING EVIDENCE.

For current MVP:

Camera
→ Perception Hypothesis
→ "Tớ đọc được thế này"
→ CONFIRM / CORRECT / RETAKE
→ CanonicalProblem
→ domain reasoning.

WAL-52 is now a SAFETY BOUNDARY,
not cosmetic UX.

==================================================
12. P0 — PERCEPTION PROVENANCE
==================================================

Research:

PerceptionHypothesis
PerceptionAssessment
PerceptionProvenance
CanonicalProblem.

Preserve separately:

machine hypothesis
learner-confirmed problem.

Never overwrite machine history with user correction.

Investigate lineage:

RawImage
→ PerceptionHypothesis
→ ConfirmedProblem
→ ExerciseSkillMap
→ TutorScope
→ StudentInteraction
→ LearningEvidence.

Goal:

every mastery-changing event should be traceable to the
problem representation the learner actually confirmed.

==================================================
13. P0 — FALSE TRUSTED PROBLEM BENCHMARK
==================================================

Do not optimize raw OCR recall first.

Priority:

FALSE TRUSTED PROBLEM RATE
must be far more important than missed-problem rate.

A miss can request retake.

A false valid expression can cause:

wrong SkillCase
wrong Method
wrong diagnosis
wrong intervention
wrong mastery.

Measure separately:

Detection Recall
Expression Assembly Recall
Expression Correctness
Fabricated Valid Expression Rate
Student Correction Rate
False Trusted Problem Rate.

Do not collapse these into "OCR accuracy."

==================================================
14. P0/P1 — MULTI-VIEW CAMERA CONSENSUS
==================================================

Test whether independent image transforms reduce fabricated expressions.

Candidate views:

original
perspective corrected
contrast normalized
denoised
sharpened.

Run independently:

preprocess
→ OCR
→ assemble expression
→ compare outputs.

Do not trust agreement blindly:
correlated OCR errors may exist.

Falsify the hypothesis.

==================================================
15. P1 — PRE-CAPTURE CAMERA UX
==================================================

Research camera guidance BEFORE capture.

Benchmark AutoMath / Photomath / QANDA / Dicamon and others.

Potential states:

MOVE_CLOSER
HOLD_STEADY
MORE_LIGHT
STRAIGHTEN_PHONE
FIT_ONE_PROBLEM
REMOVE_HAND_OCCLUSION
TOO_BLURRY
MULTIPLE_PROBLEMS_DETECTED.

Goal:

prevent bad perception upstream,
not merely repair afterward.

==================================================
16. P0 — KNOWLEDGE / RAG ARCHITECTURE
==================================================

Create/reconcile workstream:

GRAPH-GUIDED, PEDAGOGY-CONSTRAINED RAG

Do NOT build:

PDF
→ arbitrary chunks
→ embeddings
→ topK
→ LLM.

Research architecture:

SOURCE PLANE
→ CONTENT PLANE
→ EDUCATIONAL KNOWLEDGE GRAPH
→ RETRIEVAL INDEX
→ GRAPH-GUIDED RETRIEVAL
→ EVIDENCE PACK
→ PEDAGOGICAL FILTER
→ SAM.

==================================================
17. RAG — SOURCE PLANE
==================================================

Define source-of-record semantics.

Potential SourceDocument fields:

sourceId
publisher
edition
schoolYear
grade
subject
series
licenseStatus
checksum
version.

Embedding/index is NOT source of truth.

Respect current Legal Gate.

Do not commit/re-distribute copyrighted SGK corpus.

==================================================
18. RAG — CONTENT UNIT
==================================================

Do not chunk only by token length.

Research pedagogical ContentUnit types such as:

Lesson
Section
Definition
Rule
Example
Exercise
WorkedExample
TeachingNote
Formula
Figure.

Preserve:

source
page
bbox/layout
lesson
semantic type
provenance.

Generic token chunks must not erase educational structure.

==================================================
19. RAG — GRAPH FIRST, SEARCH SECOND
==================================================

Research:

Problem Understanding
→ Concept / SkillCase / LearningStage
→ graph neighborhood
→ constrained content scope
→ hybrid retrieval.

Principle to test:

GRAPH determines WHERE to search.

Retrieval determines WHAT evidence to bring.

Search stack may include:

metadata filter
graph traversal
BM25
vector similarity
formula/symbol matching
later multimodal retrieval.

Do not assume vector similarity is sufficient for mathematics.

==================================================
20. RAG — EVIDENCEPACK
==================================================

Research a structured EvidencePack rather than dumping raw chunks
into the LLM.

Potential structure:

learningContext
retrievedEvidence[]
curriculumPosition
allowedMethods[]
prohibitedMethods[]
sourceCitations[]
retrievalConfidence
unresolvedQuestions[]
knowledgeModelVersion
retrievalPolicyVersion
sourceVersion.

Do not implement fields without need.

Core principle:

RETRIEVED != PEDAGOGICALLY PERMITTED.

==================================================
21. RAG — FAIL CLOSED
==================================================

Define retrieval failure states:

NO_EVIDENCE
LOW_CONFIDENCE
SOURCE_CONFLICT
VERSION_MISMATCH
FUTURE_KNOWLEDGE_ONLY
INSUFFICIENT_PROVENANCE.

SAM must be able to say it is unsure.

Do not hallucinate around retrieval gaps.

==================================================
22. RAG — STUDENT DATA BOUNDARY
==================================================

Keep:

Knowledge Store
!=
Student Store.

Do not embed all child history/chat into the same content vector corpus.

Knowledge:
curriculum/content/concepts/methods.

Student:
LearningEvidence/mastery/coverage/confidence/history.

Student state should inform retrieval planning,
not become shared educational corpus.

==================================================
23. RAG — BENCHMARK
==================================================

Do not report only Recall@K.

Measure educational retrieval quality:

Source Recall
Curriculum Precision
SkillCase Precision
Citation Correctness
Unsupported Claim Rate
Future-Knowledge Leakage Rate
Method Permission Violation Rate.

Target:

Method Permission Violation ≈ 0
Future-Knowledge Leakage ≈ 0.

==================================================
24. P0 — SAM TEACHING PHILOSOPHY
==================================================

Continue WAL-57 / current philosophy Epic.

Research before codifying.

Required research:

Vietnamese educational tradition
Confucian educational thought
East Asian humanistic education
Hồ Chí Minh educational thought
GDPT 2018
current Vietnam AI-education guidance
modern learning science.

Use stronger evidence standards.

Separate:

SOURCE
INTERPRETATION
PRODUCT PRINCIPLE
SAM BEHAVIOR
TESTABLE RULE.

==================================================
25. SAM PHILOSOPHY — CORE HYPOTHESES
==================================================

Research principles around:

HỌC ĐỂ HIỂU
HỌC ĐI ĐÔI VỚI HÀNH
TỰ HỌC
TỰ LẬP / TỰ CƯỜNG
KHIÊM TỐN
TRUNG THỰC
TRÁCH NHIỆM
NHÂN ÁI
ĐỨC + TÀI
TÔN TRỌNG NGƯỜI DẠY
TÔN TRỌNG NHƯNG VẪN ĐƯỢC CHẤT VẤN.

Do NOT implement:

blind obedience
shame
fear
teacher infallibility
rote memorization as virtue
grade worship
gender hierarchy
suppression of scientific reasoning.

==================================================
26. SAM CONSTITUTION
==================================================

After source research reaches sufficient quality, create:

SAM-CHARACTER-CONSTITUTION.md
SAM-PEDAGOGICAL-CONSTITUTION.md.

Map philosophy into architecture.

Example:

TỰ HỌC
→ independent attempt required
→ TeachingAct policy
→ LearningEvidence
→ reduced assistance.

TRUNG THỰC
→ post-hint success does not become independent mastery.

KHIÊM TỐN
→ uncertainty/fail-closed behavior.

HỌC ĐI ĐÔI VỚI HÀNH
→ transfer/application tasks.

==================================================
27. P0 — CHILD SAFETY / PRIVACY
==================================================

Move child safety/privacy architecture BEFORE real Generative Tutor.

Research:

age-aware behavior
parental consent
PII minimization
provider/model data boundaries
camera image retention
voice retention
chat retention
student-parent visibility
unsafe content handling
moderation
account deletion/export
local-first opportunities.

Do not wait for production.

==================================================
28. UI/UX BENCHMARK — PRIORITY A
==================================================

Before locking WAL-48, study current products visually and behaviorally.

A1. BRILLIANT / KOJI

Study:
- tutor embedded directly in interactive problem
- sees learner action/context
- learning by doing
- step-by-step intervention
- restraint / no-answer-first behavior.

This is a high-value reference for SAM.

A2. KHANMIGO / KHAN ACADEMY

Study:
- Socratic scaffolding
- Companion Mode
- small diagnostic questions
- targeted practice
- learner/parent/teacher separation
- contextual tutor instead of blank chatbot.

A3. PHOTOMATH

Study:
- camera framing
- crop
- recognized problem presentation
- editing/correction
- step display
- multiple methods.

Do NOT copy:

SCAN → ANSWER.

SAM:

SCAN
→ HYPOTHESIS
→ CONFIRM
→ DIAGNOSE
→ TEACH
→ ATTEMPT
→ EVIDENCE
→ ADAPT.

==================================================
29. UI/UX BENCHMARK — VIETNAM / CAMERA
==================================================

P0:

QANDA
DICAMON.

QANDA research:
- camera problem
- student solution correction
- tutor
- quizzes
- history
- teacher Q&A
- learner work as input.

DICAMON research:
- Vietnam curriculum expectations
- camera solver
- DicaBee
- SGK/SBT organization
- similar exercises
- exam practice
- Vietnamese student copy/IA.

Key question:

What do Vietnam-facing products understand about local learner behavior
that global products do not?

==================================================
30. UI/UX BENCHMARK — PRIORITY B/C
==================================================

Study:

IXL
- diagnostic → action plan
- next skill
- learning gaps.

Quizlet Learn
- adaptive short sessions
- active recall
- review progression.

ClassDojo
- student/parent modes
- family-facing information hierarchy.

StudyFetch
- source → multiple learning experiences
- tutor/content integration
- voice/visual tools.
Reject feature-buffet MVP.

Mathway
- photo/manual input
- math editor
- step rendering.

AutoMath
- camera capture guidance
- blur/guidance/focus/frame.

Cymath
- step explanation
- compact solver UX.

PhotoStudy
- human escalation pattern.
Research only; do not add human tutors to MVP.

Duolingo Max
- AI as character / voice / roleplay.
Do not adopt engagement-first objective.

Prodigy
- parent dashboard
- skill status.
Do not adopt game economy.

Microsoft Math Solver:
historical/discontinued-app reference only.

Socratic:
resolve exact product identity before benchmarking.

==================================================
31. UI PATTERN LIBRARY
==================================================

Create/update:

docs/design/UI-UX-PATTERN-LIBRARY.md

Pattern families:

NEXT_ACTION
CONTEXTUAL_TUTOR
CAMERA_CONFIRMATION
PERCEPTION_CORRECTION
DIAGNOSTIC_PROBE
PROGRESSIVE_HINT
YOUR_TURN
STEP_BACK
LEARNING_BY_DOING
REVIEW_DUE
LEARNING_MAP
PARENT_TONIGHT_ACTION
UNCERTAINTY
VOICE_HINT
MASCOT_PEDAGOGICAL_STATE.

Each pattern must map to WAL domain state.

No decorative-only library.

==================================================
32. MASCOT — KEEP CURRENT SAM
==================================================

Do NOT redesign the owl.

Current purple/yellow owl is baseline.

Audit/produce pedagogical states:

HELLO
LISTEN
THINK
PROBE
HINT
YOUR_TURN
STEP_BACK
TRY_AGAIN
EXPLAIN
ADMIT_UNCERTAINTY
CELEBRATE_INDEPENDENCE
CAMERA_SCAN
REVIEW_DUE.

Important:

SAM_STEP_BACK and SAM_YOUR_TURN are pedagogically meaningful.

SAM sometimes becoming visually quieter is a FEATURE.

Age adaptation:

younger:
more mascot / larger / warmer.

older:
smaller / calmer / less intrusive.

==================================================
33. FIRST UI VERTICAL SLICE
==================================================

Do not build 20 screens.

Only after architecture prerequisites are sufficiently stable:

MISSION
→ CAMERA
→ PRE-CAPTURE GUIDANCE
→ CAPTURE
→ "TỚ ĐỌC ĐƯỢC THẾ NÀY"
→ CONFIRM / CORRECT / RETAKE
→ DIAGNOSTIC PROBE
→ LEARNER ATTEMPT
→ MINIMUM SUFFICIENT HINT
→ YOUR TURN
→ LEARNING EVIDENCE
→ NEXT ACTION.

This is the first UI proof.

Maturity language must remain honest:

DESIGNED
DOMAIN IMPLEMENTED
UI IMPLEMENTED
DEVICE VERIFIED
PRODUCTION READY

are different states.

==================================================
34. PARENT UX
==================================================

Parent experience should answer quickly:

"Tối nay tôi nên giúp con điều gì?"

Do not create surveillance dashboards.

Use evidence-backed claims.

Example:

not:
"Con yếu phân số."

prefer:
"Con đã làm tốt hai dạng.
Dạng thứ ba SAM chưa có đủ bằng chứng."

Parent action should include HOW TO HELP.

==================================================
35. SOURCE QUALITY STANDARD
==================================================

Raise research evidence standards.

Tag important findings:

PRIMARY / OFFICIAL
PEER-REVIEWED / ACADEMIC
OSS IMPLEMENTATION
OFFICIAL PRODUCT
SECONDARY INDUSTRY
ANECDOTAL.

Do not label broad educational claims FALSIFIED based only on
a weak blog/Medium/article.

Product UX inspiration can use weaker sources.

Pedagogy/architecture doctrine requires stronger evidence.

==================================================
36. AUTONOMOUS EXECUTION LOOP
==================================================

After Jira reconciliation:

START EXECUTION IMMEDIATELY.

Loop:

1. select highest-value unblocked READY issue
2. move → In Progress
3. inspect evidence
4. research / falsify / design / implement
5. write tests
6. mutation-test important invariants
7. update ADR only for real architecture decision
8. update Jira with evidence
9. update Confluence for stable Founder-level knowledge
10. commit
11. push
12. Code Review
13. QA
14. Done only when acceptance criteria are actually met
15. select next issue
16. repeat.

Do not stop after one ticket.

Do not stop because research produced a negative result.

Negative/falsified result is valid progress.

==================================================
37. PARALLEL TRACKS
==================================================

Independent tracks may progress in parallel:

TRACK A
Pedagogical Agent / adaptive-learning architecture

TRACK B
Knowledge / Graph / RAG

TRACK C
Camera / Perception Safety / OCR

TRACK D
UI/UX / Design System / mascot

TRACK E
SAM Teaching Philosophy

TRACK F
Child Safety / Privacy.

However:

Jira must still expose one overall ranked READY queue.

==================================================
38. DO NOT BUILD YET
==================================================

Do not prematurely build:

large multi-agent runtime
20 UI screens
AI Lab breadth
game economy
social features
complex DKT/AKT
full cognitive-diagnosis models
commercial textbook pipeline
human tutor marketplace.

Do not confuse more code with more product truth.

==================================================
39. STOP / FOUNDER GATES
==================================================

Do NOT ask Founder for:

normal research choices
Jira prioritization
reversible architecture
component design
routine refactors
failed POCs.

Ask Founder only for:

irreversible branding
major scope change
commercial SGK licensing
legal/compliance commitment
major external spend
destructive shared repo operation.

Phone photos are useful external validation
but do NOT block independent work.

==================================================
40. CHECKPOINT REPORT FORMAT
==================================================

Report only at meaningful evidence checkpoints:

STATUS

JIRA
- Epics
- total issues
- created
- merged
- Ready
- In Progress
- Done

RESEARCH
- new evidence
- literature/OSS/products studied

FALSIFIED

ARCHITECTURE

RAG

CAMERA

UI/UX

SAM PHILOSOPHY

SAFETY / PRIVACY

IMPLEMENTATION MATURITY

TESTS / MUTATIONS

DECISIONS / ADR

BLOCKERS

NEXT JIRA ISSUE ALREADY SELECTED.

==================================================
41. START NOW
==================================================

Execute now in this order:

PHASE 1
- verify repo/Jira/Confluence truth
- reconcile all existing WAL issues
- convert research into Jira actionable TODO
- merge duplicates
- update dependencies/priorities.

PHASE 2
P0:
- Pedagogically Constrained Agent
- LearningEvidence replay semantics
- many-to-many / Q-matrix falsification
- Perception Safety / False Trusted Problem
- RAG architecture
- SAM authoritative philosophy research
- child safety/privacy.

PHASE 3
- SkillCase concept #3 cross-domain
- TeachingAct
- diagnostic probe
- assistance/fading
- multi-view camera POC
- retrieval POC.

PHASE 4
- UI/UX benchmark
- WAL pattern library
- Design System / mascot production states
- pre-capture Camera UX.

PHASE 5
- implement FIRST vertical UI slice.

After completing any issue:
select the next highest-value unblocked Jira issue automatically.

Do not wait for the Founder to say "continue."

CONTINUE UNTIL THE READY QUEUE IS EXHAUSTED
or a true Founder-only gate is reached.

START EXECUTION.
