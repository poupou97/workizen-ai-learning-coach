# MASTER FOUNDER TASK ORDER
# HỌC CÙNG SAM — K–12 CONTENT → LEARNING EXPERIENCE READINESS
# GRADES 1–12
#
# THIS ORDER SUPERSEDES:
# 1. Founder Review — WAL-176 / Next Content→Experience Bottleneck Audit
# 2. Founder Scope Expansion — K–12 Full-Scope Assessment
#
# Treat them as ONE workstream, NOT two parallel initiatives.

MODE:
FULL AUTONOMOUS EXECUTION

AUDIT
→ K–12 SWEEP
→ READINESS MATRIX
→ FALSIFICATION
→ REPRESENTATIVE GOLDEN JOURNEYS
→ ROOT-CAUSE ANALYSIS
→ RECOMMENDATION
→ JIRA REBASELINE
→ BOUNDED P0 IMPLEMENTATION
→ VERIFY
→ REPEAT

Do not wait for Founder between normal reversible technical decisions.

==================================================
0. FOUNDER DECISION / WHY THIS EXISTS
==================================================

Golden Journey has now proven substantial parts of the Product Shell:

- Bookshelf;
- Book/Lesson navigation;
- LearningIntent;
- activities;
- Evidence;
- Learning Map;
- Parent Summary;
- Adaptive Challenge policy;
- real-device execution.

Recent walks also exposed:

Tiếng Việt:
PARTIAL, runtime works, one real UI regression fixed.

Lịch sử:
PARTIAL, architecture works where curated structured content exists,
but corpus semantics are thin.

Tiếng Anh:
FAIL honestly because no learning activities are available.

Therefore the next major question is no longer primarily:

“Does the app flow work?”

It is:

“Can real K–12 curriculum content become a truthful,
pedagogically useful SAM Learning Experience at scale?”

Founder now expands this assessment to:

ALL GRADES 1 → 12.

==================================================
1. PRIMARY PRODUCT QUESTION
==================================================

Answer:

“Nếu hôm nay một học sinh bất kỳ từ lớp 1 tới lớp 12
mở Học cùng SAM với đúng SGK của mình,
SAM thực sự giúp em đó HỌC được tới mức nào?”

Evaluate the complete chain:

SOURCE
→ STRUCTURE
→ SEMANTICS
→ PEDAGOGY
→ LEARNING CONTEXT
→ EXPERIENCE
→ LEARNER ACTION
→ EVIDENCE
→ ADAPTATION
→ PARENT / NEXT ACTION.

Find exactly where this chain works.

Find exactly where it breaks.

Find why.

Then recommend the highest-leverage path to make it scale.

==================================================
2. IMPORTANT — THIS IS NOT MASS IMPLEMENTATION
==================================================

FULL K–12 SCOPE
does NOT mean:

implement every K–12 lesson.

Do NOT:

- hand-code thousands of lessons;
- create one ticket per lesson;
- create one Epic per subject;
- manually QA every lesson;
- generate thousands of lessons with uncontrolled LLM;
- build new UI just because content is missing;
- create fake content to make coverage green.

Instead:

100% STRUCTURAL / MACHINE-ASSESSABLE SWEEP

+

STRATIFIED REPRESENTATIVE DEEP VALIDATION.

==================================================
3. WAL-176 ROLE
==================================================

KEEP WAL-176 OPEN.

Clarify its role as:

PERIODIC GOLDEN JOURNEY / PRODUCT REGRESSION PROBE.

Do not turn WAL-176 into the K–12 assessment checklist.

Create/reuse the appropriate Jira capability/workstream
for this Master Order.

WAL-176 should be rerun when meaningful content/runtime capability changes.

Examples:

- English pipeline becomes available;
- History structured semantics land;
- new Learning Surface ships;
- content compiler changes;
- Evidence semantics change;
- Learning Visualizer gains a representation;
- major Lesson Workspace change.

==================================================
4. TODO 1 — INVENTORY ALL K–12
==================================================

FIRST:

Build/reuse an automated inventory of the actual corpus/runtime.

Cover:

Grade 1
Grade 2
Grade 3
Grade 4
Grade 5
Grade 6
Grade 7
Grade 8
Grade 9
Grade 10
Grade 11
Grade 12.

For each actual Grade × Subject combination determine:

- books;
- SGK / SGV where applicable;
- chapters/content hierarchy;
- lessons;
- activities;
- structured semantics;
- pedagogical information;
- provenance;
- runtime mapping;
- available Learning Surface;
- Evidence capability;
- Adaptive capability.

Do not infer from filenames alone.

Use actual corpus/runtime truth.

==================================================
5. TODO 2 — GENERATE K–12 READINESS MATRIX
==================================================

Create a reproducible matrix.

Suggested dimensions:

Grade
Subject
Books
Lessons
Structural
Semantic
Pedagogy
Activity
Surface
Evidence
Adaptive
Device Proven
Readiness
Main Blocker.

Generate it from data/scripts where possible.

Do not maintain hundreds of rows manually.

This artifact should be reproducible after corpus changes.

==================================================
6. READINESS LEVELS
==================================================

Classify meaningful Grade × Subject combinations.

Suggested:

L0 — SOURCE ONLY

Book/source exists but no usable learning experience.

L1 — BROWSABLE

Book/lesson can be navigated/read.

L2 — STRUCTURED

Meaningful structured content/activity data exists.

L3 — LEARNABLE

Real SAM Learning Experience exists.

L4 — EVIDENCE-CAPABLE

LearnerAction can produce truthful validated learning evidence.

L5 — ADAPTIVE

Evidence/state influences review/challenge/next learning action.

Exact enum names may change.

But preserve the distinction.

CRITICAL:

BOOK EXISTS
!=
LESSON EXISTS
!=
STRUCTURED CONTENT
!=
LEARNING EXPERIENCE
!=
LEARNING EVIDENCE
!=
ADAPTIVE LEARNING.

==================================================
7. TODO 3 — EXECUTIVE K–12 HEATMAP
==================================================

Derive an executive heatmap from the detailed matrix.

Rows/columns should allow Founder to understand:

Grades 1–12
×
subject or subject-family readiness.

Use truthful categories such as:

READY
PARTIAL
BLOCKED
NOT ASSESSED

or better evidence-backed equivalents.

Founder should understand the current K–12 state in <5 minutes.

Do NOT produce:

“K–12 = 63% complete.”

==================================================
8. TODO 4 — REAL COVERAGE METRICS
==================================================

Calculate separate truthful metrics where data permits:

- books structurally indexed;
- lessons structurally identified;
- lessons with meaningful semantics;
- lessons with pedagogy;
- lessons with runtime activities;
- lessons with suitable Learning Surface;
- lessons capable of validated Evidence;
- lessons/adaptive contexts actually adaptive;
- representative real-device journeys verified.

Do not collapse dimensions into one fake completion number.

==================================================
9. TODO 5 — CLUSTER SUBJECT FAMILIES
==================================================

Do not treat every subject as a separate application.

Analyze reusable Learning Interaction families.

Candidate families:

A. MATHEMATICAL / PROBLEM SOLVING

B. LANGUAGE / LITERACY

C. FOREIGN LANGUAGE / COMMUNICATION

D. SCIENTIFIC INVESTIGATION

E. HISTORY / SOURCE REASONING

F. GEOGRAPHY / SPATIAL + DATA

G. COMPUTING / AI / TECHNOLOGY

H. SOCIAL / CIVIC

I. other families actually justified by corpus.

These names are hypotheses.

Use evidence to merge/change them.

Goal:

find reusable experience patterns and shared bottlenecks.

==================================================
10. TODO 6 — AGE-BAND FALSIFICATION
==================================================

Assess at minimum:

Grade 1–2
Grade 3–5
Grade 6–9
Grade 10–12.

Challenge whether one Learning OS truly works across all.

Evaluate:

- information density;
- reading demand;
- SAM language;
- independence;
- navigation;
- visual support;
- voice importance;
- scaffold;
- Parent role;
- complexity of Learning Tools.

Do NOT automatically create different apps or different navigation.

Try:

same Product Shell
+
AgePolicy
+
appropriate projection/surface.

But falsify this if evidence says it fails.

==================================================
11. TODO 7 — TRACE CONTENT → EXPERIENCE
==================================================

For representative lessons trace exact lineage:

SourceDocument
→ BookManifest
→ ContentNode / hierarchy
→ Lesson
→ semantic structure
→ pedagogical information / blueprint
→ Activity
→ LearningIntent
→ Hierarchical LearningContext
→ Pedagogy
→ PlannedAct
→ Learning Surface / Tool
→ LearnerAction
→ CandidateEvidence
→ EvidenceValidator
→ Learning State
→ Learning Map
→ Parent Summary
→ Review / Next Action / Adaptive Challenge.

Mark the exact break point.

Do not say merely:

“English unsupported.”

Say for example:

Source ✓
Structure ✓
Semantics ✗
Pedagogy ✗
Activity ✗
Surface ?
Evidence ?
Adaptive ?

with code/data evidence.

==================================================
12. TODO 8 — WORKING VS FAILING COMPARISON
==================================================

Use contrasts.

Current known examples include:

WORKING / STRONGER:
- Toán 5;
- Khoa học 5;
- Geography Map where real structured source asset exists.

PARTIAL:
- Tiếng Việt;
- History curated source reasoning.

FAIL / EMPTY:
- current English representative lessons.

Extend comparison across:

lower primary;
upper primary;
lower secondary;
upper secondary.

Ask:

WHY does one real lesson become learnable
while another real lesson stops?

==================================================
13. TODO 9 — STRATIFIED SAMPLING
==================================================

Do NOT manually walk all lessons.

Choose samples based on matrix/outliers.

Must include representative cases from:

Grade 1–2
Grade 3–5
Grade 6–9
Grade 10–12.

Include different subject families.

Also deliberately sample:

- youngest grade;
- oldest grade;
- sparse book;
- dense book;
- unusual hierarchy;
- volume split;
- multiple activities;
- no activities;
- source-heavy lesson;
- exercise-heavy lesson;
- strong semantics;
- OCR-only content.

Goal:

BREAK THE MODEL.

Not prove happy-path coverage.

==================================================
14. TODO 10 — GOLDEN JOURNEYS ON REAL DEVICE
==================================================

Walk selected high-information journeys on Nokia where feasible.

Do not merely verify:

“screen opens.”

Evaluate:

- can learner understand where they are?
- is LearningIntent meaningful?
- does experience fit the subject?
- is SAM context correct?
- does SAM appear at useful moments?
- is provenance truthful?
- is Trace/Evidence distinction correct?
- does Evidence affect downstream state correctly?
- are Parent/Learning Map/Home coherent?
- are there contradictions across screens?
- does insufficient content fail honestly?

Local UI/runtime bugs:

→ Jira
→ fix
→ test
→ Nokia
→ PR/CI
→ merge

without waiting for Founder.

==================================================
15. TODO 11 — ANALYZE THE REAL BOTTLENECK
==================================================

Classify each failure primarily as:

A. SOURCE

B. STRUCTURAL EXTRACTION

C. SEMANTIC EXTRACTION

D. PEDAGOGY

E. ACTIVITY MODEL

F. LEARNING SURFACE

G. SAM REALIZATION

H. EVIDENCE SEMANTICS

I. ADAPTATION

J. RUNTIME WIRING

K. AGE PROJECTION

or combination.

Then aggregate.

Founder wants to know:

WHAT SHARED BOTTLENECK BLOCKS THE MOST K–12 LEARNING COVERAGE?

==================================================
16. TODO 12 — RE-EVALUATE LEARNING EXPERIENCE FACTORY
==================================================

Use K–12 evidence to revisit:

SGK / SGV
→ Structural Extraction
→ Semantic Structure
→ Pedagogy
→ Experience Pattern
→ Learning Surface
→ SAM
→ Evidence.

Do NOT build this because the diagram looks elegant.

Audit which arrows exist.

For missing transformations determine whether they should be:

- deterministic;
- rule-based;
- extracted from SGV;
- compiled;
- LLM-assisted + validated;
- human gold-reviewed;
- subject-family adapted.

==================================================
17. BLUEPRINT COMPILER QUESTION
==================================================

Explicitly revisit the old Blueprint Compiler hypothesis.

Answer:

What can genuinely be compiled?

What cannot?

Does current evidence justify reviving it?

Does it need a narrower responsibility?

Would subject-family adapters be more truthful?

Is pedagogy extractable from SGV sufficiently?

Where is human/gold review required?

Possible verdicts include:

ACCEPT
ACCEPT WITH CHANGES
DEFER
REJECT.

Do not protect the old decision.

==================================================
18. CORE SCALE TARGET
==================================================

Target is NOT:

8,000 handwritten learning experiences.

Target is also NOT:

8,000 AI-generated hallucinated learning experiences.

Target:

SOURCE-GROUNDED
+
PEDAGOGICALLY VALIDATED
+
REUSABLE
+
COMPOSABLE
LEARNING EXPERIENCES.

Key question:

How much can be shared?

How much must vary by subject family?

How much must vary by lesson?

==================================================
19. TODO 13 — EVIDENCE MODEL FALSIFICATION
==================================================

Challenge current Evidence architecture across K–12.

Math:
- correctness;
- method;
- independence.

Vietnamese:
- reading;
- draft;
- revision;
- assistance;
- explanation.

English:
- comprehension;
- listening;
- speaking;
- pronunciation;
- writing;
- repeated practice.

Science:
- observation;
- prediction where permitted;
- explanation;
- reasoning.

History:
- source reasoning;
- causal reasoning;
- evidence-backed conclusion.

Geography:
- map/data interpretation.

Determine whether:

LearnerAction
→ CandidateEvidence
→ EvidenceValidator

is generic enough.

Do not force all subjects into correct:true/false.

If extension is required:
find the smallest shared extension.

==================================================
20. TODO 14 — LEARNING VISUALIZER EVIDENCE
==================================================

Use K–12 assessment to gather evidence for the open
SAM Learning Visualizer hypothesis.

Do NOT build visual templates merely for audit.

Record natural representation needs:

Timeline
Process
Map
Concept Map
Comparison
Cause/Effect
Formula
Graph
Hierarchy
Review Sheet
etc.

Current doctrine remains:

NO STRUCTURED FACT
→ NO AUTHORITATIVE STRUCTURED VISUAL FACT.

History Timeline remains blocked until source semantics justify it.

Also look for the stronger hypothesis:

SAME CONTENT
+
DIFFERENT LEARNING INTENT
→
DIFFERENT USEFUL REPRESENTATION.

Do not force implementation until real evidence exists.

==================================================
21. TODO 15 — ADAPTIVE CHALLENGE K–12
==================================================

Keep current policy separation:

Learner Capability
!=
Challenge
!=
User Preference.

Audit what challenge means across subject families.

🌱 Củng cố
🎯 Vừa sức
🚀 Thử thách

must eventually correspond to real activity differences.

But DO NOT hand-author three exercise banks.

Investigate reusable Challenge Dimensions:

- prerequisite demand;
- reasoning depth;
- steps;
- novelty;
- transfer;
- representation;
- scaffold;
- assistance.

HARDER != FUTURE CURRICULUM.

Current policy can remain proven while challenge-content generation/selection
remains an open capability.

==================================================
22. TODO 16 — PARENT EXPERIENCE ACROSS K–12
==================================================

Evaluate current Parent Summary across age bands.

Parent of Grade 1
may need different explanation density from
Parent of Grade 12.

But preserve:

ONE EVIDENCE TRUTH
→ MULTIPLE PROJECTIONS.

No:
- separate parent scoring DB;
- fake precision;
- sibling ranking.

Reuse existing Parent UX.

Do not create a new analytics subsystem.

==================================================
23. TODO 17 — SHARED DEVICE / LEARNER ISOLATION
==================================================

Preserve:

DEVICE != USER
ACCOUNT != LEARNER
PARENT != LEARNER.

Use automated invariants where possible.

Representative tests must confirm:

Learner A
→ Grade/context/evidence A

switch

Learner B
→ Grade/context/evidence B

switch back

Learner A state unchanged.

No cross-learner evidence contamination.

Do not manually repeat for all 12 grades if architecture-level tests prove it.

==================================================
24. TODO 18 — SOURCE / PROVENANCE SCALE
==================================================

At K–12 scale preserve:

OCR CONFIDENCE
!=
SOURCE TRUTH CONFIDENCE.

SOURCE_EXPLICIT
!=
SOURCE_DEMONSTRATED
!=
SAM_INFERRED.

No provenance
→ no curriculum-truth claim.

No structured source
→ no authoritative structured claim.

Do not relax these rules merely to increase readiness metrics.

==================================================
25. TODO 19 — IDENTIFY WHAT NOT TO BUILD
==================================================

K–12 audit must explicitly identify waste.

Examples could include:

- unnecessary new UI;
- duplicate Learning Surfaces;
- generic chatbot fallback;
- per-subject app architecture;
- per-lesson Dart;
- premature visualization framework;
- premature multi-agent system;
- mass LLM extraction;
- fake mastery dashboards;
- duplicate evidence models.

Evidence must determine actual list.

==================================================
26. TODO 20 — PRIORITIZE THE GAPS
==================================================

Rank candidate work using:

UNLOCKED K–12 LEARNING COVERAGE
×
PEDAGOGICAL VALUE
×
REUSE ACROSS GRADES/SUBJECTS
×
EVIDENCE QUALITY
÷
IMPLEMENTATION COST / RISK.

Do not prioritize because something is visually impressive.

==================================================
27. TODO 21 — RECOMMEND P0 / P1 / DEFER
==================================================

After assessment produce:

P0
= smallest shared capabilities unlocking the most real learning.

P1
= valuable capabilities after P0.

DEFER
= useful but not current bottleneck.

DO NOT BUILD
= hypotheses falsified or low leverage.

For each P0 recommendation state:

- blocker solved;
- Grade × Subject coverage unlocked;
- architecture affected;
- estimated implementation shape;
- validation method;
- dependency;
- risk.

==================================================
28. TODO 22 — JIRA REBASELINE
==================================================

Audit Jira before creating tickets.

Reuse/re-scope existing tickets first.

Do NOT create:

one ticket per lesson;
one ticket per book;
one Epic per subject;
hundreds of K–12 tickets.

Prefer capability-oriented tickets.

Examples only if evidence supports:

- Semantic Content Extraction;
- Pedagogy/Blueprint Pipeline;
- Language Activity Model;
- Subject-family Adapter;
- Evidence Extension;
- Age Projection.

Do not pre-create these merely because they are listed here.

==================================================
29. AUTOMATIC FIX POLICY
==================================================

Claude has authority to automatically fix:

- local bugs;
- broken navigation;
- untappable controls;
- missing wiring to already-existing data;
- incorrect mappings;
- projection/copy contradictions;
- small reusable adapters;
- bounded technical gaps clearly supported by evidence.

Process:

Jira
→ branch
→ implementation
→ tests
→ Nokia if user-visible
→ PR
→ CI
→ merge
→ close
→ continue.

==================================================
30. LARGE GAP POLICY
==================================================

Do NOT automatically launch broad implementation for:

- thousands of missing lessons;
- large LLM content generation;
- major new architecture;
- new app per age/subject;
- major copyright/commercial operation;
- large manual content operation.

For these:

bounded POC
→ evidence
→ recommendation.

If still a genuine major Product/Architecture fork:
Founder decision.

==================================================
31. IMPLEMENT AFTER ASSESSMENT — DO NOT JUST REPORT
==================================================

This Master Order is not research-only.

After the K–12 assessment:

if P0 contains small/medium shared capabilities
with strong evidence and no Founder-level fork:

START THEM AUTOMATICALLY.

Do not stop at:

“Here are my recommendations.”

Instead:

Assessment
→ Jira Rebaseline
→ highest-leverage P0
→ bounded implementation
→ test
→ evidence
→ real device where relevant
→ PR/CI/merge
→ update readiness matrix
→ rerun affected Golden Journey
→ next P0.

==================================================
32. P0 STOP CONDITION
==================================================

Continue automatically until:

- current P0 recommendation set is implemented/proven;
- OR dependency blocks execution;
- OR hypothesis is falsified;
- OR Founder-level decision is required.

Do not continue into massive content generation without validated pipeline evidence.

==================================================
33. FOUNDER REPORT
==================================================

Give Founder ONE concise report:

# HỌC CÙNG SAM — K–12 READINESS & RECOMMENDATION

A. EXECUTIVE VERDICT

How ready is SAM for real K–12 learning?

B. HEATMAP

Grades 1–12 × Subject Families.

C. REAL COVERAGE

Separate metrics:
Structure
Semantics
Pedagogy
Experience
Evidence
Adaptive.

D. WHAT WORKS

Stop rebuilding these.

E. WHAT ONLY LOOKS SUPPORTED

Books/content present but not truly learnable.

F. TOP BOTTLENECKS

Ranked by K–12 impact.

G. AGE FINDINGS

1–2
3–5
6–9
10–12.

H. SUBJECT-FAMILY FINDINGS

What can share architecture,
what genuinely differs.

I. EVIDENCE FINDINGS

Whether current model survives K–12.

J. CONTENT→EXPERIENCE FINDINGS

Exact broken transformations.

K. TOP 5 ACTIONS

Ranked.

L. JIRA REBASELINE

What was reused/re-scoped/created.

M. WHAT NOT TO BUILD

Evidence-backed.

N. FOUNDER DECISIONS

ONLY genuine product/architecture/legal/cost forks.

Keep detailed data/evidence in repo/Jira.

Do not dump hundreds of rows into Founder report.

==================================================
34. TODO LIST — EXECUTION CHECKLIST
==================================================

Use this as the operational Todo hierarchy.

[ ] T01 Audit existing Jira/research/code before creating work
[ ] T02 Inventory Grade 1–12 corpus/runtime
[ ] T03 Generate Grade × Subject readiness matrix
[ ] T04 Generate executive heatmap
[ ] T05 Calculate multi-dimensional coverage metrics
[ ] T06 Cluster actual subject families
[ ] T07 Assess Age Bands 1–2 / 3–5 / 6–9 / 10–12
[ ] T08 Trace representative Content→Experience pipelines
[ ] T09 Compare working/partial/failing lessons
[ ] T10 Select stratified/outlier samples
[ ] T11 Walk high-information Golden Journeys on Nokia
[ ] T12 Fix bounded runtime/UI bugs discovered
[ ] T13 Classify exact pipeline breakpoints
[ ] T14 Identify shared K–12 bottlenecks
[ ] T15 Re-evaluate Learning Experience Factory
[ ] T16 Re-evaluate Blueprint Compiler
[ ] T17 Falsify Evidence model across subject families
[ ] T18 Collect Learning Visualizer evidence
[ ] T19 Assess Adaptive Challenge semantics across families
[ ] T20 Assess Parent projection across age bands
[ ] T21 Verify learner/shared-device isolation
[ ] T22 Audit provenance/source-truth scaling
[ ] T23 Identify unnecessary architecture/UI/content work
[ ] T24 Rank gaps by leverage/cost/risk
[ ] T25 Produce P0 / P1 / DEFER / DO-NOT-BUILD recommendation
[ ] T26 Rebaseline Jira around capabilities
[ ] T27 Automatically start highest-leverage bounded P0
[ ] T28 Test + evidence + Nokia + PR/CI/merge
[ ] T29 Regenerate readiness matrix after P0
[ ] T30 Re-run affected WAL-176 Golden Journey
[ ] T31 Continue next P0 if dependency-ready
[ ] T32 Deliver concise Founder K–12 decision report

==================================================
35. SUCCESS CRITERIA
==================================================

This work is NOT successful because:

- 12 grades appear in UI;
- all books appear;
- tests are green;
- Jira tickets are closed;
- PDFs were indexed.

It succeeds if we can truthfully answer:

For every major K–12 region:

WHAT CAN THE CHILD ACTUALLY LEARN?

WHY CAN SAM TEACH IT?

WHAT SOURCE SUPPORTS IT?

WHAT DOES THE CHILD DO?

WHAT EVIDENCE CAN WE CLAIM?

HOW DOES SAM ADAPT AFTERWARD?

And where this is not possible:

WHAT EXACT CAPABILITY IS MISSING?

==================================================
FINAL DOCTRINE
==================================================

FULL K–12 SCOPE.
NOT FULL K–12 HAND-CODING.

ONE MASTER WORKSTREAM.
NOT TWO DUPLICATE AUDITS.

100% STRUCTURAL ASSESSMENT.
REPRESENTATIVE DEEP FALSIFICATION.

BOOK EXISTS != LEARNABLE.

CONTENT EXISTS != PEDAGOGY.

TRACE != EVIDENCE.

COVERAGE != MASTERY.

REVIEW_DUE != CURRENTLY_STRUGGLING.

NO STRUCTURED FACT
→ NO AUTHORITATIVE STRUCTURED CLAIM.

NO PER-LESSON PRODUCT CODE.

NO MASS LLM GENERATION BEFORE VALIDATED PIPELINE.

REUSE PRODUCT UX.

REUSE LEARNING SURFACES.

ONE EVIDENCE TRUTH.

FIX THE SHARED PIPELINE,
NOT 8,000 LESSONS ONE BY ONE.

AFTER FINDING THE BOTTLENECK:
DO NOT JUST REPORT IT.
FIX THE HIGHEST-LEVERAGE BOUNDED P0
AND MEASURE HOW MUCH K–12 COVERAGE IT UNLOCKS.
