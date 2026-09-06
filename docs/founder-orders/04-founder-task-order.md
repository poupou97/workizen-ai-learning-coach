# FOUNDER TASK ORDER
## LEARNER-CONTEXTUAL UX / SUBJECT-SPECIFIC LEARNING ENVIRONMENTS
## BACKLOG AUDIT + RESEARCH + FALSIFICATION

Priority: Product/UX architecture research + backlog reconciliation
Mode: Autonomous
Founder approval required only under existing L1/irreversible gates.

============================================================
0. WHY THIS TASK EXISTS
============================================================

Founder has added a set of product requirements around:

1. Learner onboarding/profile.
2. Grade-aware personalized Home.
3. Parent + multiple learner profiles.
4. Timetable as learning context.
5. LearningSession / conversation organization.
6. Subject-specific learning contexts.
7. Different learning/assessment experiences:
   - problem solving
   - multiple choice
   - essay
   - oral
   - experiment
   - map
   - graph
   - source analysis
   - etc.
8. Specialized UI/UX for different subject families.
9. SAM remains one coherent tutor across these environments.
10. Research comparable educational products/LMS before locking architecture.

IMPORTANT:

These are Founder product hypotheses/directions, NOT permission to blindly
implement all of them.

First inspect repository truth, current Jira backlog, Confluence, ADRs,
wireframes, domain models and current UI implementation.

REUSE / MODIFY / MERGE existing work where possible.

DO NOT create duplicate Epics/issues.

Founder explicitly requests CRITIQUE/FALSIFICATION.

If any requirement below is pedagogically wrong, technically overbuilt,
inconsistent with existing architecture, harmful to UX, privacy-sensitive,
or premature for MVP:

SAY SO WITH EVIDENCE.

============================================================
1. LEARNER PROFILE — ONBOARDING
============================================================

Research/reconcile onboarding around a LEARNER PROFILE.

Candidate fields:

- preferred/display name
- birth year / age context
- current grade
- curriculum/program where necessary
- textbook/series only where pedagogically necessary
- optional interests/preferences where justified

IMPORTANT INVARIANT:

BIRTH YEAR != CURRENT GRADE.

Do NOT permanently infer grade from birth year.

Two learners of the same age may be in different grades.

Current grade must be independently confirmable/changeable.

Also:

CURRENT GRADE != MASTERY.

Example:

learner selects Grade 5

means:

CurriculumPosition = Grade 5

NOT:

Grade1..Grade4 = mastered.

Mastery requires LearningEvidence.

Audit existing domain model for whether these concepts are currently
incorrectly coupled.

============================================================
2. PARENT ACCOUNT != LEARNER
============================================================

Research/reconcile model:

Guardian / Parent
        |
        +-- Learner A
        |
        +-- Learner B
        |
        +-- Learner ...

Each learner should potentially have independent:

- birth/age context
- current grade
- curriculum context
- timetable
- subject context
- Student Knowledge State
- LearningEvidence
- LearningSessions
- recommendations
- review schedule

Switching learner must switch educational context.

Do NOT assume account == student.

At the same time, challenge whether full multi-child account support belongs
in MVP or whether the domain model should support it while UI ships later.

============================================================
3. CURRICULUM-AWARE HOME
============================================================

Founder does NOT want the same generic feature/tool grid for every child.

Research Home as:

LearnerProfile
    ↓
Curriculum Context
    ↓
Available Subjects
    ↓
Timetable Context
    ↓
Student Knowledge State
    ↓
Review Schedule
    ↓
Next Best Learning Actions
    ↓
HOME

Home should answer something closer to:

"What should I learn/do today?"

rather than:

"Which AI tool would you like to open?"

Candidate Home hierarchy:

A. TODAY
- subjects relevant today
- unfinished/recommended learning
- timetable-aware actions

B. COMING UP
- tomorrow's relevant subjects
- review due
- known assessments/homework if trustworthy data exists

C. MY SUBJECTS
- curriculum-relevant subject entry points

Do NOT lock this IA without UX falsification.

============================================================
4. TIMETABLE CONTEXT
============================================================

Founder approves adding TIMETABLE as learning context.

However:

SAM is NOT primarily a timetable-management application.

Timetable exists to improve learning recommendations.

Initial conceptual model may be as small as:

TimetableEntry
- learnerId
- weekday/date context
- period/order
- subjectId
- optional trusted metadata

Potential input methods:

- manual
- simple weekly timetable
- camera/import later
- school integration later

Research optional camera flow:

photo timetable
→ perception/OCR
→ learner/parent confirmation
→ canonical timetable

Apply existing perception safety principles where applicable.

CRITICAL:

TIMETABLE SUBJECT != EXACT LESSON.

If timetable says:

"Tuesday period 1 = Mathematics"

SAM MUST NOT silently infer:

"Teacher will teach Lesson 17"

unless there is trusted evidence.

Possible future trusted sources may include:

- teacher/school plan
- explicit learner/parent input
- confirmed homework
- class progress
- validated KHDH/school data

Prediction must be represented as prediction, not fact.

Timetable should be OPTIONAL during onboarding unless evidence strongly
supports making it mandatory.

Research whether asking for it during onboarding creates excessive friction.

============================================================
5. LEARNING SESSION / CONVERSATION MODEL
============================================================

Founder asks how every conversation/learning session should be stored and
presented.

Do NOT model learning history merely as chat transcripts.

Research/reconcile:

Learner
  ↓
LearningSession
  ↓
Interaction Events
  ↓
LearningEvidence
  ↓
Student Knowledge State

Candidate LearningSession metadata:

- sessionId
- learnerId
- subjectId
- grade/curriculum context
- startedAt / endedAt
- trigger
- learningGoal
- Concept/SkillCase references
- knowledgeModelVersion
- tutorPolicyVersion
- outcome summary

Potential triggers:

- MANUAL
- TIMETABLE_PREP
- CAMERA_HOMEWORK
- REVIEW_DUE
- SAM_RECOMMENDATION
- ASSESSMENT
- OTHER

Do not freeze enum names without domain audit.

============================================================
6. HISTORY MUST SUPPORT MULTIPLE VIEWS
============================================================

Founder wants learning history understandable:

BY DATE:
"What did my child/I learn today?"

BY SUBJECT:
"How am I progressing in Mathematics?"

BY KNOWLEDGE:
"What evidence exists for this Concept/SkillCase?"

Recommended conceptual hierarchy:

Learner
  |
  +-- Calendar/Day → LearningSessions
  |
  +-- Subject → LearningSessions
  |
  +-- Knowledge State → LearningEvidence across many sessions

IMPORTANT:

Store each session ONCE.

Do not duplicate records for day/subject views.

Date/subject/concept/skill associations should allow different projections.

Research UX for:

- Today/history
- Subject history
- Knowledge/progress history
- Parent summary

============================================================
7. TRANSCRIPT != LEARNING EVIDENCE
============================================================

Preserve/strengthen this separation:

Conversation Transcript
        ↓
Interaction Events
        ↓
Evidence qualification
        ↓
LearningEvidence
        ↓
Student Knowledge State

A correct answer after hints must NOT become equivalent to an independent
correct answer.

Example:

Attempt 1
incorrect
assistanceLevel = 0

Teaching intervention
SMALL_HINT

Attempt 2
correct
assistanceLevel = 1

Evidence meaning:

"Correct after one small hint"

NOT:

"Mastered."

Audit whether current WAL architecture actually preserves enough historical
intervention lineage to reconstruct this distinction.

Explicitly revisit previous open concern:

Does historical evidence preserve exact enough:

- TeachingAct
- assistance level
- tutor policy version
- intervention identity/hint identity where needed
- pre/post intervention attempt relation?

If not, report the architectural gap.

Do NOT claim this is solved merely because current tests are green.

============================================================
8. RETENTION / PRIVACY
============================================================

Research separate retention policies for:

A. raw camera/image
B. transcript
C. interaction events
D. LearningEvidence
E. derived Student Knowledge State

Candidate principle:

raw sensory data shortest retention
transcript potentially limited
LearningEvidence longer-lived
derived state replayable where feasible

ADR-006 local-first remains binding.

Child data should not automatically become cloud history.

Do NOT introduce cloud dependency merely to support history.

Identify legal/privacy questions separately from architecture assumptions.

============================================================
9. MAJOR UX DIRECTION:
SUBJECT-SPECIFIC LEARNING ENVIRONMENTS
============================================================

Founder rejects the simplistic model:

"one Chat screen + subject selector."

But Founder also does NOT want a completely independent app/UI architecture
for every school subject.

Research a middle architecture:

                 SAM LEARNING SHELL
                         |
                 Subject Context
                         |
                 Activity Context
                         |
                 Interaction Surface
                         |
                       SAM

SAM remains one coherent tutor/persona.

The environment changes according to the nature of the learning task.

============================================================
10. CLASSIFY BY LEARNING INTERACTION, NOT ONLY SUBJECT
============================================================

Research whether subject families can share reusable learning surfaces.

Initial hypothesis to challenge:

A. PROBLEM SOLVING
Potential subjects:
- Mathematics
- Physics
- quantitative Chemistry

Potential surfaces:
- Problem Workspace
- Step Workspace
- Formula
- Equation
- Graph
- Diagram
- Camera

B. SCIENTIFIC INVESTIGATION
Potential:
- Physics
- Chemistry
- Biology

Potential surfaces:
- observation
- hypothesis
- experiment/model
- table
- graph
- explanation
- conclusion

C. READING / ARGUMENT / SOURCE REASONING
Potential:
- Literature/Vietnamese
- History
- Civic education
- portions of Geography

Potential surfaces:
- Source Reader
- annotation
- evidence
- outline
- argument
- Essay Workspace

D. SPATIAL / DATA REASONING
Potential:
- Geography
- portions of History/Science

Potential surfaces:
- Map
- layers
- charts
- spatial selection
- compare regions
- explanation

E. LANGUAGE LEARNING
Potential:
- English/foreign languages

Potential surfaces:
- listening
- speaking
- pronunciation
- reading
- writing
- roleplay

F. ASSESSMENT
Cross-subject.

Potential formats:
- MCQ
- MULTI_SELECT
- SHORT_ANSWER
- ESSAY
- STEP_SOLUTION
- ORAL
- MIXED

These categories are hypotheses.

FALSIFY THEM.

Add/remove/merge categories if evidence suggests a better taxonomy.

============================================================
11. SUBJECT EXAMPLES TO RESEARCH
============================================================

At minimum research UX for:

MATHEMATICS
- problem representation
- scratch/work area
- step reasoning
- formulas
- graph
- camera
- progressive hints

PHYSICS
- formulas
- units
- vectors
- diagrams
- graphs
- circuit/light/mechanics representations
- problem solving
- experiment reasoning

CHEMISTRY
- chemical equations
- balancing
- periodic table
- structures where appropriate
- quantities/calculation
- observations
- experiments
- safety

HISTORY
- chronology/timeline
- primary/secondary sources where appropriate
- cause/effect
- comparison
- evidence-based argument
- essay

GEOGRAPHY
- map
- layers
- charts
- climate/population/data visualization
- spatial comparison
- evidence-based explanation

VIETNAMESE/LITERATURE
- reading
- comprehension
- annotation
- outline
- writing
- revision
- argument/evidence where applicable

Do not assume all grades require the same complexity.

============================================================
12. LEARNING MODE != EXAM MODE
============================================================

Research explicit separation between:

LEARN / PRACTICE / REVIEW

and:

ASSESS / EXAM.

During learning:

SAM may:
- ask diagnostic questions
- provide progressive hints
- ask learner to explain
- encourage verification
- step back
- provide feedback

During a real assessment/exam simulation:

SAM assistance may need to be disabled/restricted.

Example:

ExamSession
→ questions
→ learner responses
→ no tutoring during attempt
→ post-assessment analysis afterward

Do NOT contaminate independent assessment evidence with tutoring.

This must connect to existing assistance/evidence semantics.

============================================================
13. ESSAY UX
============================================================

Research Essay Workspace as a first-class learning surface.

Possible flow:

Prompt
→ understand prompt
→ brainstorm
→ outline
→ learner draft
→ evidence/source check
→ SAM critique
→ learner revision
→ final reflection

SAM should not default to writing the essay for the learner.

Research evidence that can be collected from the PROCESS, not merely final
text.

Especially investigate History / Geography / Vietnamese.

============================================================
14. SUBJECT CONTEXT
============================================================

Founder asks whether each subject can have different "context/conversation."

Answer this architecturally.

Candidate:

SAM
 + LearnerContext
 + CurriculumContext
 + SubjectContext
 + ActivityContext
 + TutorScope
 + Relevant Knowledge
 + Student Knowledge State

Examples:

MathContext:
- current curriculum position
- Concepts
- SkillCases
- Methods
- allowed methods
- problem state
- previous attempts

HistoryContext:
- topic
- chronology
- source evidence
- concepts
- argument state

GeographyContext:
- topic
- map/data context
- spatial evidence
- charts/data
- explanation state

Do NOT implement independent chatbot memory silos unless evidence supports it.

Determine:
- what context is session-local
- subject-longitudinal
- learner-global
- derived/retrievable
- disposable

============================================================
15. INTERACTION SURFACE ARCHITECTURE
============================================================

Research architecture similar to:

SAM Learning Shell
       |
       +-- Problem Workspace
       +-- Step Solver
       +-- Formula/Equation
       +-- Diagram
       +-- Graph
       +-- Timeline
       +-- Source Reader
       +-- Essay Workspace
       +-- Map
       +-- Table/Data
       +-- Quiz
       +-- Camera
       +-- Voice
       +-- SAM Conversation

Do NOT implement this list blindly.

The goal is a COMPOSABLE LEARNING SURFACE SYSTEM.

A subject/activity composes only the surfaces it needs.

Example hypothesis:

Math
= Problem + Step + Graph + Camera + SAM

Physics
= Problem + Formula + Diagram + Graph + SAM

Chemistry
= Equation + Table + Experiment + SAM

History
= Timeline + Source + Essay + SAM

Geography
= Map + Chart + Source + Essay + SAM

Vietnamese
= Reader + Essay + Voice + SAM

Falsify composition using actual curriculum examples.

============================================================
16. AGE-ADAPTIVE UX
============================================================

Research how the same learning surface changes by age/grade.

Dimensions:

- amount of text
- visual density
- SAM mascot prominence
- voice usage
- iconography
- navigation complexity
- terminology
- independence
- parent involvement
- writing/input expectations

Do NOT create 12 separate Design Systems.

Prefer:

ONE DESIGN SYSTEM
+
AGE/DEVELOPMENTAL PRESENTATION POLICIES.

Validate whether grade bands are more appropriate than exact grade-specific UI.

============================================================
17. CURRICULUM-DRIVEN UI — BUT DO NOT OVERFIT
============================================================

Investigate whether local Curriculum/Content knowledge can inform:

Subject
→ LearningObjective
→ Activity Type
→ appropriate Interaction Surface

But do NOT assume Curriculum Graph should contain presentation/UI decisions.

Challenge separation of concerns.

Potential better model:

Curriculum says WHAT is being learned.

Pedagogy/Activity model says HOW it should be learned.

UI Surface resolver says WHICH interaction surface renders that activity.

Research and decide.

Avoid polluting authoritative curriculum truth with product UI metadata.

============================================================
18. LOCAL-FIRST / PERFORMANCE
============================================================

ADR-006 remains binding.

Routine operations such as:

- learner selection
- subject list
- timetable
- today's Home
- learning history
- knowledge state lookup
- curriculum position

should preferably work from local structured data.

Do NOT introduce:

- always-on vector DB
- local large LLM
- continuous vision processing
- unnecessary embeddings

just to support these UX features.

Connect with WAL-83/WAL-84.

WAL-84 should eventually measure relevant mobile workloads including:

- DB open
- Home query
- subject query
- history query
- graph lookup
- FTS/BM25
- timetable recommendation query
- camera/OCR burst
- normal tutor interaction

Metrics should include where feasible:

- latency
- memory
- CPU
- battery
- thermal state
- jank/frame impact

Storage size != runtime compute cost.

============================================================
19. COMPETITOR / LMS RESEARCH
============================================================

Do a fresh evidence-based benchmark.

At minimum investigate:

- CK-12 / Flexi
- IXL
- ALEKS
- Khan Academy / Khanmigo
- Brilliant
- Labster

Also find strong current products specifically for:

- History learning
- Geography/map learning
- essay/writing learning
- Physics
- Chemistry
- assessment/exam practice
- K-12 parent learning insights

Do NOT copy visual designs.

Extract reusable interaction principles.

Questions:

1. How do they organize Grade → Subject → Skill/Lesson?
2. Is tutor embedded in activity or separate chat?
3. How do specialized subjects change UI?
4. How is adaptive recommendation presented?
5. How is progress/mastery represented?
6. How do they handle assessments?
7. How do they handle essays/open response?
8. How do they handle labs/maps/graphs?
9. How do they represent history/session?
10. What is weak or missing that SAM can improve?

============================================================
20. REQUIRED RESEARCH ARTIFACT:
INTERACTION SURFACE MATRIX
============================================================

Produce a matrix approximately:

Subject / Subject Family
×
Learning Goal
×
Activity Type
×
Assessment Type
×
Interaction Surface
×
TeachingAct
×
LearningEvidence
×
Age Band

Example:

Math
× fraction addition
× guided practice
× step solution
× Problem+Step Workspace
× DIAGNOSTIC_PROBE/SMALL_HINT/STEP_BACK
× independent/assisted attempts
× Grade 5

History
× causal reasoning
× source analysis
× essay
× Timeline+Source+Essay
× ASK_FOR_EVIDENCE/REFLECT
× argument/evidence/revision events
× Grade 9

Do not explode into every lesson.

Use representative curriculum cases.

============================================================
21. REQUIRED FALSIFICATION
============================================================

At minimum challenge:

F1
"Every subject needs its own UI."

Try to show reusable cross-subject surfaces.

F2
"One universal chat UI is enough."

Try representative Math/History/Geography/Chemistry cases.

F3
"Grade determines mastery."

Must fail.

F4
"Timetable tells us exact lesson."

Must fail unless additional evidence exists.

F5
"Every learning conversation should become mastery evidence."

Must fail.

F6
"Correct after hint == independent correctness."

Must fail.

F7
"Assessment and tutoring can share the same assistance policy."

Try to falsify.

F8
"Curriculum Graph should contain UI layout/surface decisions."

Challenge strongly.

F9
"One age presentation works equally well for Grade 1 and Grade 12."

Challenge.

F10
"Every subject needs persistent separate chatbot memory."

Challenge.

F11
"Parent account == learner."

Must fail.

F12
"All transcript data must be retained forever for personalization."

Challenge using privacy/utility trade-offs.

F13
"Adding timetable to onboarding always improves UX."

Test onboarding friction / skip flow.

F14
"Interactive/specialized UI necessarily requires heavy mobile AI compute."

Challenge architecturally.

============================================================
22. BACKLOG / JIRA AUDIT
============================================================

BEFORE creating tickets:

Search all existing WAL:

- onboarding
- learner profile
- parent
- multi-child
- Home
- timetable
- learning session
- conversation
- evidence
- mastery
- subject
- assessment
- exam
- essay
- graph
- camera
- age adaptive
- UI/UX
- wireframe
- Design System
- current First UI slice

Map findings:

EXISTING — KEEP
EXISTING — MODIFY
EXISTING — MERGE
MISSING — CREATE
RESEARCH LATER
REJECT

Avoid ticket explosion.

Prefer one coherent Epic/workstream with staged issues if no equivalent exists.

Do NOT create one ticket per subject or grade.

============================================================
23. PRIORITY / EXECUTION
============================================================

Do NOT automatically interrupt the current highest-value autonomous work.

Determine where these requirements affect work that is being designed NOW.

Especially:

- onboarding
- Home
- First UI slice
- LearningSession
- LearningEvidence
- Design System

If current wireframes would create architectural lock-in inconsistent with
these findings, intervene now.

Otherwise:

document + backlog + sequence later.

Research should inform implementation, not paralyze it.

============================================================
24. REQUIRED OUTPUT
============================================================

Checkpoint must include:

STATUS

BACKLOG AUDIT
- existing relevant tickets
- duplicates
- gaps
- proposed changes

FOUNDER REQUIREMENTS
- accepted as-is
- modified
- challenged/rejected

LEARNER PROFILE

PARENT / MULTI-CHILD

TIMETABLE

HOME / NEXT ACTION

LEARNING SESSION

CONVERSATION vs LEARNING EVIDENCE

SUBJECT CONTEXT

SUBJECT-FAMILY TAXONOMY

INTERACTION SURFACE MATRIX

ASSESSMENT / EXAM

ESSAY / OPEN RESPONSE

AGE-ADAPTIVE UX

COMPETITOR FINDINGS

ARCHITECTURE

LOCAL-FIRST / PERFORMANCE

PRIVACY / RETENTION

FALSIFIED
- F1...F14 with evidence

JIRA
- created/modified/merged
- no duplicate confirmation

ADR
- whether any new ADR is actually warranted
- do NOT create ADR merely because research exists

BLOCKERS

NEXT
- ranked autonomous queue

============================================================
25. DECISION STANDARD
============================================================

Do not optimize for agreeing with Founder.

Optimize for:

- learning effectiveness
- learner independence
- curriculum correctness
- evidence integrity
- age appropriateness
- usability
- privacy
- local-first feasibility
- maintainability
- mobile performance
- product differentiation

Founder explicitly authorizes:

"Ý tưởng của tôi có thể sai. Hãy phản biện bằng evidence."

If a simpler model survives falsification better, recommend it.

If current architecture is already sufficient, DO NOT redesign it merely
because this Task Order exists.

Continue autonomous execution after checkpoint under existing Founder gates.
