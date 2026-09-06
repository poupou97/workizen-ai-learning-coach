TASK ORDER — HỌC CÙNG SAM
LEARNING VIEWS CONCEPT & REFERENCE RESEARCH

PRIORITY
P0 Research / Product Concept

STATUS
RESEARCH + ARCHITECTURE HYPOTHESIS ONLY.
DO NOT IMPLEMENT YET.

==================================================
1. FOUNDER PRODUCT IDEA
==================================================

Founder muốn nghiên cứu một mô hình mới cho Lesson Workspace của
“Học cùng SAM”.

Một bài học không nên bị đồng nhất với một màn PDF hoặc một màn chat.

Thay vào đó:

ONE TRUSTED LESSON
→ MULTIPLE LEARNING VIEWS

Cùng một bài học có thể được trình bày theo nhiều cách khác nhau,
tùy mục tiêu học tập, loại kiến thức và trạng thái của học sinh.

Concept ban đầu:

Giá sách
→ Chọn sách
→ Chọn chương
→ Chọn bài
→ Lesson Workspace
   ├── Mode 1: Smart Book / Đọc như sách
   ├── Mode 2: Visual Learning / Trực quan hóa
   └── Mode 3: SAM Tutor / Học cùng SAM


IMPORTANT:

Đây KHÔNG phải ba bản sao nội dung khác nhau.

Mục tiêu kiến trúc cần nghiên cứu là:

                  TRUSTED LESSON
                        │
             ┌──────────┼──────────┐
             ↓          ↓          ↓
         MODE 1      MODE 2      MODE 3
        Smart Book   Visual      SAM Tutor

Một nguồn nội dung đáng tin cậy
→ nhiều cách trải nghiệm học tập.


==================================================
2. PRODUCT PRINCIPLE
==================================================

Learning View != Learning Source.

Learning View chỉ là cách trình bày / tương tác với cùng một
Trusted Learning Source.

Không được để:

Mode 1 có một truth
Mode 2 có một truth khác
Mode 3 lại để LLM tự tạo một truth khác.

Cả ba phải truy nguyên được về cùng nguồn:

SGK / SGV
→ Trusted Structured Content
→ Learning Model / Pedagogy
→ Learning Views

Preserve provenance:

Book
→ Chapter
→ Lesson
→ Source Page
→ Source Block / BBox
→ Structured Content
→ Learning View


==================================================
3. MODE 1 — SMART BOOK / “ĐỌC NHƯ SÁCH”
==================================================

Founder intent:

Mode 1 giữ trải nghiệm gần với SGK gốc nhất,
nhưng KHÔNG nhất thiết render nguyên PDF.

Có thể reconstruct bài học thành native UI từ structured content.

Ví dụ:

Lesson
├── Heading
├── Paragraph
├── Image
├── Caption
├── Paragraph
├── Table
├── Formula
├── Question
├── Activity
└── Source Reference

UI nên giữ:

- thứ tự nội dung;
- ảnh minh họa;
- caption;
- bảng;
- công thức;
- câu hỏi;
- activity;
- cấu trúc section;
- quan hệ nội dung quan trọng.

Nhưng được phép cải thiện:

- responsive layout;
- font size;
- accessibility;
- zoom image;
- responsive table;
- highlight;
- bookmark;
- annotation;
- Ask SAM about this;
- source reference.

Không yêu cầu pixel-perfect SGK.

Mục tiêu:

“Gần sách đủ để học sinh nhận ra bài mình đang học,
nhưng native, responsive và AI-ready.”


RESEARCH QUESTION:

Có nên sử dụng:

PDF → Structured Document → Native Smart Book

thay cho:

PDF → PDF Viewer

hoặc:

PDF → Markdown → generic renderer?


==================================================
4. MODE 2 — VISUAL LEARNING
==================================================

Mode 2 KHÔNG được định nghĩa là chỉ “Mindmap”.

Tên concept:

VISUAL LEARNING VIEW

Hệ thống lựa chọn representation phù hợp với cấu trúc kiến thức.

Ví dụ:

Lịch sử
→ Timeline
→ Cause / Effect
→ Person / Event relationship

Địa lý
→ Map / Spatial View
→ Region comparison

Khoa học
→ Process Diagram
→ System Diagram
→ Cause / Effect
→ Observation sequence

Sinh học
→ System Map
→ Process
→ Classification

Concept-heavy lesson
→ Mindmap / Concept Map

Comparison-heavy lesson
→ Comparison View

Sequence-heavy lesson
→ Flow / Process View


Candidate renderers:

- Mindmap
- Concept Map
- Timeline
- Process / Flow
- Cause–Effect Map
- Comparison
- Classification Tree
- Map / Spatial
- System Diagram
- Data / Chart
- Flashcard-like visual summary


IMPORTANT ARCHITECTURE HYPOTHESIS:

Mode 2 không nên để LLM tự “sáng tác một mindmap”
mỗi lần học sinh mở bài.

Nghiên cứu mô hình:

Trusted Semantic Content
        ↓
Typed relationships
        ↓
Visual Renderer

Ví dụ:

HistoricalEvent[]
→ Timeline Renderer

ConceptRelation[]
→ Concept Map

ProcessStep[]
→ Process Diagram

ComparisonDimension[]
→ Comparison View

GeoEntity[]
→ Map

Như vậy Visual Learning có thể:

- deterministic hơn;
- source-grounded;
- cache được;
- kiểm tra được;
- rẻ hơn;
- tránh hallucination.


==================================================
5. MODE 3 — SAM TUTOR / INTERACTIVE LEARNING
==================================================

Không định nghĩa Mode 3 đơn giản là “Chat”.

Chat chỉ là một interaction mechanism.

Concept chính:

SAM TUTOR VIEW
hoặc
HỌC CÙNG SAM.

SAM chủ động tổ chức learning session dựa trên:

- lesson;
- curriculum;
- allowed pedagogy;
- Student Knowledge State;
- previous evidence;
- misconception;
- mastery;
- learning objective.

Ví dụ:

SAM:
“Trước khi bắt đầu, con còn nhớ tại sao...?”

Student answers.

System:

Student Action
→ Evidence
→ Pedagogy Runtime
→ Student State
→ Next Teaching Action

SAM có thể:

- explain;
- ask;
- hint;
- scaffold;
- demonstrate;
- ask student to observe;
- ask student to compare;
- ask student to classify;
- ask student to calculate;
- ask student to write;
- diagnose misconception;
- practice;
- review;
- check understanding.

Chat có thể xuất hiện,
nhưng không phải toàn bộ Mode 3.


IMPORTANT:

LLM DOES NOT DECIDE PEDAGOGY.

Pedagogy Runtime determines:

WHAT SAM MAY TEACH
WHAT SAM MAY ASK
WHAT METHOD IS ALLOWED
WHAT EVIDENCE IS VALID

LLM/SAM realizes the permitted teaching action.


==================================================
6. RELATIONSHIP WITH EXISTING ACTIVITY PATTERNS
==================================================

Do NOT create 27 buttons or 27 Learning Modes.

Existing K–12 Activity Patterns should be considered
underlying capabilities / Learning Surfaces.

Example:

                SAM TUTOR
                    │
          ┌─────────┼─────────┐
          ↓         ↓         ↓
       Observe   Compare   Calculate
       Reading   Writing   Experiment
       Question  Classify  ShortAnswer
          ...

Activity Pattern != top-level Mode.

Learning View = product-level experience.

Activity Pattern / Surface = capability used inside a View.


==================================================
7. MODE SELECTION / NEXT ACTION
==================================================

Research whether students should always manually choose a mode.

Founder hypothesis:

The three modes are visible and selectable:

[ Đọc ] [ Trực quan ] [ Học với SAM ]

BUT SAM may recommend the best next view.

Example:

“SAM đề xuất:
Xem Dòng thời gian trước — khoảng 5 phút.”

or:

“SAM đề xuất:
Học cùng SAM — khoảng 12 phút.
Lần trước con còn nhầm phần này.”

Therefore investigate:

Learning View Selection
as part of
NEXT BEST LEARNING ACTION.

Do not assume recommendation logic yet.

Research it.


==================================================
8. REFERENCE REPOSITORIES / PRODUCTS
==================================================

Research these as references.

DO NOT clone blindly.
DO NOT adopt architecture because a repo looks impressive.

For every reference extract:

- reusable product principle;
- content model;
- lesson model;
- renderer model;
- interaction model;
- tutor model;
- assessment/evidence model;
- strengths;
- weaknesses;
- license;
- maturity;
- applicability to SAM;
- what NOT to copy.


--------------------------------------------------
A. DEEPTUTOR
--------------------------------------------------

Repository:
https://github.com/HKUDS/DeepTutor

Priority:
P0 Research

Study especially:

- Book Engine / Living Books;
- document → interactive learning content;
- chapter/page organization;
- content blocks;
- figures;
- quizzes;
- flashcards;
- timeline;
- concept graph;
- interactive learning components;
- contextual tutor interaction.

Question:

Can its “Living Book” ideas inform:

Trusted Structured Lesson
→ multiple SAM Learning Views?


--------------------------------------------------
B. MATHIGON TEXTBOOKS
--------------------------------------------------

Repository:
https://github.com/mathigon/textbooks

Priority:
P0 Research

Study:

- interactive textbook architecture;
- structured course content;
- custom Markdown/content representation;
- interactive components;
- media/assets;
- hints;
- virtual tutor concepts;
- textbook + interaction coexistence.

Especially relevant to:

MODE 1 — Smart Book
+
MODE 3 — Tutor.


--------------------------------------------------
C. OPPIA
--------------------------------------------------

Repository:
https://github.com/oppia/oppia

Priority:
P0 Research

Study:

- interactive explorations;
- learner response → feedback → next state;
- skill;
- misconception;
- question;
- hints;
- branching;
- targeted feedback;
- learner state;
- tutoring interaction state machine.

Compare against SAM:

Concept
SkillCase
Evidence
Student Knowledge State
Pedagogy Runtime
PlannedAct
Next Action.

Do not force SAM into Oppia's model.

Use it as prior art.


--------------------------------------------------
D. H5P
--------------------------------------------------

Reference:
https://github.com/h5p

Priority:
P1 Research

Study:

- reusable interactive content types;
- Interactive Book;
- Timeline;
- Quiz;
- interactive video;
- presentation;
- reusable learning components.

Primary question:

What can SAM learn from the idea:

Lesson
→ composition of reusable Learning Surfaces?


--------------------------------------------------
E. SCAFFOLD
--------------------------------------------------

Repository:
https://github.com/brainjamworks/scaffold

Priority:
P1 Research / Experimental

Study:

- portable document/content model;
- structured learning content;
- separation of authoring/content/runtime;
- media;
- assessment;
- rendering;
- deterministic logic outside UI where applicable.

Question:

Can a similar separation help SAM create:

Trusted Structured Lesson
→ multiple renderers?


--------------------------------------------------
F. OPENMAIC
--------------------------------------------------

Repository:
https://github.com/THU-MAIC/OpenMAIC

Priority:
P1 Research

Study selectively:

- document/topic → learning experience;
- slides;
- quiz;
- simulation;
- mindmap;
- interactive classroom;
- AI teacher interaction.

Focus mainly on ideas relevant to:

MODE 2 — Visual Learning
and
MODE 3 — Interactive Learning.

Do not assume its architecture fits SAM.


==================================================
9. RESEARCH ADDITIONAL PRIOR ART
==================================================

Do not limit research to the repositories above.

Search for additional high-quality current references for:

- interactive textbooks;
- living books;
- adaptive textbooks;
- structured educational documents;
- multimodal learning content;
- knowledge visualization;
- concept maps;
- timeline learning;
- adaptive tutoring;
- intelligent tutoring systems;
- learning object models;
- reusable educational components;
- source-grounded educational AI.

Prefer:

- active OSS;
- research-backed systems;
- production systems with public architecture;
- standards;
- established learning science.

Avoid collecting dozens of shallow links.

Only add references that change a SAM decision.


==================================================
10. ARCHITECTURE QUESTION TO ANSWER
==================================================

Investigate whether SAM should converge toward:

                  ORIGINAL SGK / SGV
                         │
                         ↓
               Trusted Corpus Pipeline
                         │
                         ↓
              TRUSTED STRUCTURED LESSON
                         │
          ┌──────────────┼───────────────┐
          ↓              ↓               ↓
      SMART BOOK     VISUAL LEARN     SAM TUTOR
          │              │               │
     text/image       timeline        pedagogy
     table            mindmap         interaction
     formula          process         evidence
     question         map             adaptation
          │              │               │
          └──────────────┼───────────────┘
                         ↓
                  Student Evidence
                         ↓
                Student Knowledge State
                         ↓
                    NEXT ACTION


Challenge this architecture.

Do not prove it.

Try to falsify it.


==================================================
11. STRUCTURED LESSON CONTRACT
==================================================

Research what minimum canonical data model would allow
ONE lesson to power all three Learning Views.

Candidate concepts ONLY:

Book
Chapter
Lesson

ContentBlock
- Heading
- Paragraph
- Image
- Caption
- Table
- Formula
- Quote
- Question
- Activity
- Figure

SemanticBinding

Concept
SkillCase
Method
LearningObjective

HistoricalEvent
ProcessStep
ComparisonDimension
GeoEntity
ConceptRelation

SourceRef
Page
BBox
Provenance
Confidence

DO NOT implement this schema.

Determine:

RETAIN
FORMALIZE
EXTEND
REJECT
HYPOTHESIS

based on current SAM evidence and external prior art.


==================================================
12. IMPORTANT TRUST RULE
==================================================

Do not let prettier Learning Views weaken source trust.

MODE 2 and MODE 3 must not transform uncertain extraction
into authoritative teaching material.

Remember:

TRACE != EVIDENCE
RETRIEVED != PERMITTED
BROWSABLE != LEARNABLE
OCR TEXT != TRUSTED SOURCE

If structured source is uncertain:

FAIL CLOSED
or
show appropriate uncertainty/source fallback.

Trust > visual richness.


==================================================
13. UX CONCEPT
==================================================

Research a simple Lesson Workspace.

Possible conceptual UI:

Bài 6 — [Lesson title]

[ 📖 Đọc ] [ ✨ Trực quan ] [ 🦉 Học với SAM ]

SAM recommendation:

“Con nên xem sơ đồ trước.
Sau đó SAM sẽ cùng con luyện phần khó.”

MODE 1:
native textbook-like content.

MODE 2:
appropriate visual representation.

MODE 3:
interactive tutoring session.

Do NOT produce a huge redesign.

Use existing approved Học cùng SAM design language,
mascot and existing surfaces wherever possible.


==================================================
14. RESEARCH QUESTIONS
==================================================

Final report must explicitly answer:

1. Are three top-level Learning Views the right abstraction?

2. Should Mode 3 be Chat or SAM Tutor?

3. Should Mode 2 be one renderer or a family of renderers?

4. Can all three Views consume one canonical Trusted Lesson?

5. What data is common across all three?

6. What data is View-specific?

7. Can Mode 1 replace PDF Viewer in the primary learning journey?

8. When should original PDF remain accessible?

9. How should provenance survive transformation?

10. How should Visual Learning remain source-grounded?

11. Which visualization types are genuinely useful by subject?

12. Which should be deterministic vs AI-generated?

13. How should Activity Patterns relate to Learning Views?

14. How should Student Evidence move between Views?

15. Can learning started in Mode 1 continue naturally in Mode 3?

16. Can SAM recommend a Learning View as Next Action?

17. How should offline/download/cache work?

18. Could structured content materially reduce app/download size?

19. What architecture patterns should we learn from DeepTutor?

20. What should we learn from Mathigon?

21. What should we learn from Oppia?

22. What should we learn from H5P?

23. What useful ideas exist in Scaffold/OpenMAIC?

24. What should explicitly NOT be copied?

25. Does this concept strengthen or complicate the current
    Learning OS architecture?


==================================================
15. DELIVERABLES
==================================================

Produce a bounded Founder Review package containing:

00-START-HERE.md

01-LEARNING-VIEWS-FOUNDER-SUMMARY.md

02-CURRENT-LESSON-EXPERIENCE-AS-IS.md

03-THREE-LEARNING-VIEWS-CONCEPT.md

04-SMART-BOOK-RESEARCH.md

05-VISUAL-LEARNING-RESEARCH.md

06-SAM-TUTOR-RESEARCH.md

07-REFERENCE-REPOSITORY-COMPARISON.md

08-DEEPTUTOR-FINDINGS.md

09-MATHIGON-FINDINGS.md

10-OPPIA-FINDINGS.md

11-H5P-AND-OTHER-PRIOR-ART.md

12-STRUCTURED-LESSON-HYPOTHESIS.md

13-LEARNING-VIEW-DATA-FLOW.md

14-ACTIVITY-PATTERN-INTEGRATION.md

15-SOURCE-TRUST-AND-PROVENANCE.md

16-UX-CONCEPT.md

17-OPEN-QUESTIONS-AND-RISKS.md

18-RECOMMENDATION.md

19-JIRA-CONFLUENCE-STATUS.md

MANIFEST.md


==================================================
16. FINAL RECOMMENDATION FORMAT
==================================================

Do not end with vague prose.

Give explicit recommendation:

A. ADOPT CONCEPT
B. ADOPT WITH CHANGES
C. KEEP AS RESEARCH HYPOTHESIS
D. REJECT

Then classify each Mode independently:

MODE 1 — Smart Book
MODE 2 — Visual Learning
MODE 3 — SAM Tutor

And classify architecture ideas:

Trusted Structured Lesson
Multi-View Renderer
Visual Renderer Family
SAM Tutor Runtime
View Recommendation / Next Action
PDF-as-Reference
Structured Content Delivery


==================================================
17. TIMING / CURRENT WORK
==================================================

IMPORTANT:

Do NOT interrupt or expand the currently running
Trusted Corpus Feasibility work.

This task may be:

- recorded in Jira;
- prepared as a bounded follow-up research task;
- started after the current Trusted Corpus Founder report
  unless it can run independently without disturbing that work.

Trusted Corpus evidence takes precedence.

The current study may materially change assumptions about:

- text extraction;
- reading order;
- images;
- tables;
- formulas;
- lesson boundaries;
- structured content;
- provenance.

Therefore final Learning Views architecture must consume
the Trusted Corpus findings rather than assume them.


==================================================
18. CORE FOUNDER INTENT
==================================================

Do not design “three screens.”

Research a Learning Content Architecture where:

ONE LESSON
→ MANY WAYS TO UNDERSTAND IT.

Mode 1 preserves the familiarity and source fidelity of the book.

Mode 2 helps the child SEE the knowledge.

Mode 3 lets the child LEARN WITH SAM.

The differentiation of Học cùng SAM should not be:

“PDF reader + chatbot.”

It should move toward:

TRUSTED CURRICULUM
+ MULTIPLE LEARNING REPRESENTATIONS
+ PEDAGOGICAL TUTOR
+ STUDENT EVIDENCE
+ NEXT BEST LEARNING ACTION.

Evidence > aesthetics.
Pedagogy > chat.
Trust > coverage.
One source of truth > duplicated generated content.
