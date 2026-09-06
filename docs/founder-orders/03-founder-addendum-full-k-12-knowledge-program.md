FOUNDER ADDENDUM — FULL K-12 KNOWLEDGE PROGRAM

WAL-73 and WAL-74 are approved.

However, they are NOT yet sufficient to represent the Founder goal:

"Transform the available Grade 1–12 textbook corpus into
Học cùng SAM's Educational Knowledge."

Create/reconcile a formal Jira Epic:

K-12 CURRICULUM KNOWLEDGE INGESTION

Do not create hundreds of per-book tickets yet.

WAL-73 and WAL-74 should become the first stages of this program.

==================================================
END STATE
==================================================

The end state is NOT:

"all PDFs OCR'ed."

It is:

Grade 1–12 educational content is represented as structured,
versioned, provenance-aware knowledge that SAM can reason over.

Target knowledge layers:

SourceDocument
→ Grade / Subject / Book
→ Chapter / Lesson / Section
→ Atomic ContentUnit
→ LearningObjective
→ Concept
→ SkillCase
→ Method
→ Prerequisite / CurriculumEdge
→ ExerciseSkillMap / Q-matrix
→ Examples / Exercises / Teaching Notes
→ Retrieval Index / EvidencePack.

==================================================
STAGE 1 — CORPUS INVENTORY + STRUCTURE
==================================================

Existing:
WAL-73

All Grade 1–12 books:

- inventory
- subject
- grade
- series
- volume
- edition/year where observable
- table of contents
- lesson/section hierarchy
- printed page mapping
- glossary/index where present
- parse failures.

No silent parse failure.

Output:
K-12 corpus coverage matrix.

==================================================
STAGE 2 — ATOMIC PEDAGOGICAL CONTENT
==================================================

Existing:
WAL-74

Convert structural sections into atomic pedagogical units such as:

RULE
DEFINITION
EXAMPLE
EXERCISE
WORKED_EXAMPLE
TEACHING_NOTE
FORMULA
FIGURE
READING
ACTIVITY
QUESTION
SUMMARY

when supported by the subject/source.

Do not assume Mathematics roles apply unchanged to every subject.

Preserve:

sourceId
page
bbox/layout
lesson/section
role
provenance
version.

==================================================
STAGE 3 — SEMANTIC KNOWLEDGE EXTRACTION
==================================================

Create a Jira task/workstream for:

ContentUnit
→ LearningObjective
→ Concept
→ SkillCase where justified
→ Method where justified.

Important:

Do NOT force SkillCase onto every subject.

SkillCase remains a hypothesis that must survive cross-domain evidence.

Deterministic/source-explicit extraction first.

LLM inference must be marked separately.

SOURCE FACT
!=
LLM INFERENCE.

==================================================
STAGE 4 — CROSS-GRADE CURRICULUM GRAPH
==================================================

Create task for building:

Concept progression across Grade 1–12.

Relations may include:

INTRODUCES
REINFORCES
APPLIES
REVIEWS
REQUIRES
BUILDS_ON

but relation vocabulary must be evidence-backed.

Especially distinguish:

source sequence
from
inferred prerequisite.

Do not convert book order automatically into prerequisite truth.

==================================================
STAGE 5 — METHODS / CASES / PEDAGOGICAL BOUNDARIES
==================================================

Create task to discover:

- different taught methods
- method applicability
- case transitions
- curriculum exposure boundaries
- methods not yet introduced.

This is what eventually powers TutorScope.

Do not let generic mathematical knowledge override
the method actually introduced at the learner's stage.

==================================================
STAGE 6 — EXERCISE / Q-MATRIX KNOWLEDGE
==================================================

Create task for mapping exercises to:

Concept(s)
SkillCase(s)
LearningObjective(s)
required/supporting skills.

Preserve:

attribution uncertainty
provenance
mapping version.

Do not force fully known mappings.

==================================================
STAGE 7 — KNOWLEDGE QA / FALSIFICATION
==================================================

Create a dedicated validation task.

For each subject/grade sample, test:

- wrong lesson mapping
- future-knowledge leakage
- wrong Concept mapping
- wrong SkillCase mapping
- false prerequisite
- missing provenance
- conflicting sources
- OCR-induced fabricated knowledge
- unsupported LLM inference.

Knowledge ingestion must fail visibly.

==================================================
STAGE 8 — RETRIEVAL BUILD
==================================================

After structured knowledge exists:

build Graph-guided RAG artifacts.

Graph determines WHERE.
Retrieval determines WHAT.

Generate/index:

ContentUnits
metadata
lexical index
formula/symbol index where relevant
optional embeddings only when measured benefit exists.

Do not use embedding generation as a substitute for semantic modeling.

==================================================
STAGE 9 — COVERAGE DASHBOARD
==================================================

Create a machine-readable K-12 Knowledge Coverage Report.

Track at minimum:

Grade coverage
Subject coverage
Books inventoried
Lessons parsed
Atomic units extracted
Concepts mapped
LearningObjectives mapped
SkillCases validated
Methods mapped
Exercises mapped
Prerequisites verified
Units with uncertain inference
Parse failures
Legal status.

Founder must be able to answer:

"What percentage of the curriculum does SAM actually understand?"

without confusing OCR coverage with knowledge coverage.

==================================================
STAGE 10 — INCREMENTAL EXECUTION
==================================================

Do NOT process all Grade 1–12 semantically in one giant batch.

Execution should be incremental.

Current preferred progression:

1. existing Math 4–5 validated slice
2. cross-domain Concept #3
3. MVP grade/subject scope
4. neighboring prerequisite grades
5. expand subject by subject
6. eventually full Grade 1–12 corpus.

Use findings from earlier batches to improve pipeline
before scaling them across hundreds of books.

==================================================
IMPORTANT — DO NOT CREATE TICKET EXPLOSION
==================================================

Do NOT create:

444 book tickets
or
12 × every subject tickets

today.

Create the PROGRAM + stage-level executable tasks.

When a stage becomes operational,
generate bounded batch tickets dynamically.

Example:

"K-12 Batch — Grade 5 Mathematics"
rather than one ticket per PDF.

==================================================
LEGAL BOUNDARY
==================================================

Current corpus remains:

LOCAL RESEARCH ONLY / LEGAL REVIEW PENDING

Do not:

push extracted textbook content to Git
publish corpus
expose textbook API
commercialize derived copyrighted content
train public/shared models on the corpus.

Knowledge architecture must allow future replacement with
licensed/official/open/teacher-created sources.

==================================================
AUTONOMOUS QUEUE RULE
==================================================

This program belongs in Jira NOW,
but it does not automatically override current higher-value P0 work.

WAL-73 may remain Ideas/P1 unless its low-cost structural scan
is useful to an active research dependency.

Semantic full-corpus stages remain gated until the architecture
survives bounded slices.

When each dependency becomes satisfied:

automatically move the next K-12 ingestion stage
Ideas → Analysis → Ready

and execute it in normal WAL autonomous order.

Do not require Founder to remember to say "continue."

==================================================
DEFINITION OF DONE — LONG TERM
==================================================

Do not declare:

"SAM knows Grade 1–12"

because PDFs were indexed.

That claim requires evidence that the corpus has been transformed into:

structured
pedagogically meaningful
versioned
source-traceable
retrievable
validated

Educational Knowledge.

Create/update Jira now.
Continue current autonomous execution afterward.
