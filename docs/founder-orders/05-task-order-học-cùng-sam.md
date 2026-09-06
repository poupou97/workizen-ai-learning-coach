# TASK ORDER — HỌC CÙNG SAM

## P0 Research — Learning Science, Pedagogy Engine, Student Model & Parent Coach

### MISSION

Nghiên cứu và phản biện độc lập để thiết kế nền tảng sư phạm cho **Học cùng SAM**.

Mục tiêu không phải xây thêm chatbot học tập.

Mục tiêu là trả lời:

1. SAM phải biết **học sinh đang hiểu gì / chưa hiểu gì** như thế nào?
2. SAM phải chọn **phương pháp dạy nào** cho từng tình huống?
3. SAM làm sao giúp học sinh **tự suy nghĩ**, thay vì giải bài hộ?
4. SAM làm sao biết một học sinh đã **thực sự mastery**?
5. SAM phải ôn tập như thế nào để kiến thức được giữ lâu?
6. SAM phải giải thích rõ:

   * đang dạy môn gì;
   * kiến thức nào;
   * dùng phương pháp nào;
   * vì sao dùng phương pháp đó;
   * nguồn kiến thức nào;
   * bằng chứng nào cho thấy học sinh đã hiểu.
7. Cha mẹ nên tham gia ở mức nào để hỗ trợ mà không trở thành “giáo viên thứ hai”?
8. Parent Mode phải tạo ra hành động hữu ích gì?

Research first.

NO production implementation.

NO accepted ADR.

NO merge main.

Founder review required.

---

# 1. CURRENT-TRUTH AUDIT FIRST

Trước khi research bên ngoài, đọc toàn bộ truth hiện tại của Học cùng SAM:

* START-HERE
* CURRENT-STATUS
* Product Vision
* architecture docs
* curriculum/content pipeline
* ContentUnit model
* source/provenance model
* OCR pipeline
* SkillCase
* teaching-method docs
* current student-progress model
* current parent/family concept nếu có
* current tests
* Jira
* Confluence

Tạo:

`docs/research/SAM-LEARNING-CURRENT-TRUTH.md`

Phân loại capability:

`BUILT`
`PARTIAL`
`RESEARCHED`
`PLANNED`
`MISSING`
`CONFLICTING`
`REJECTED`

Đặc biệt audit xem SAM hiện có thật sự:

* student mastery model?
* misconception model?
* learning history?
* spaced review?
* retrieval practice?
* adaptive difficulty?
* teaching strategy selector?
* Socratic tutoring?
* worked-example logic?
* parent insight?
* source-level provenance?
* tutoring evaluation?

Không suy đoán từ tên class/file.

Phải đọc code/data model thật.

---

# 2. RESEARCH QUESTIONS

Nghiên cứu theo 6 workstream.

## WS-A — STUDENT MODEL / KNOWLEDGE TRACING

Tìm cách biểu diễn trạng thái học của từng trẻ.

Research:

* Bayesian Knowledge Tracing
* Deep Knowledge Tracing
* Item Response Theory
* mastery learning
* misconception tracking
* skill/knowledge-component graph
* confidence/uncertainty
* forgetting
* transfer
* learning velocity
* prerequisite relationships

Phải trả lời:

> Có nên lưu “điểm môn Toán” hay phải lưu mastery ở mức knowledge component?

Ví dụ:

`Toán`
→ `Phân số`
→ `Quy đồng`
→ `Cộng khác mẫu`
→ `Bài toán lời văn`

Mỗi node có:

* mastery
* confidence
* evidence
* attempts
* common mistakes
* last practiced
* forgetting risk
* source/curriculum reference

---

# 3. WS-B — REASONING / PROBLEM-SOLVING DIAGNOSIS

Không chỉ xem đáp án đúng/sai.

Research cách phân tích:

* từng bước giải
* scratch work
* verbal reasoning
* hint usage
* hesitation
* misconception
* skipped steps
* arithmetic error
* conceptual error
* strategy error

Question:

> Hai học sinh cùng sai một đáp án nhưng sai vì nguyên nhân khác nhau thì SAM phải dạy khác nhau thế nào?

Thiết kế conceptual pipeline:

`Problem`
→ `Student attempt`
→ `Reasoning evidence`
→ `Error classification`
→ `Misconception hypothesis`
→ `Teaching response`
→ `Retry`
→ `Verification`

---

# 4. WS-C — TEACHING STRATEGY ENGINE

Research evidence-backed methods:

* Socratic questioning
* guided discovery
* worked examples
* fading
* scaffolding
* retrieval practice
* spaced practice
* interleaving
* elaboration
* self-explanation
* mastery learning
* deliberate practice
* formative assessment
* metacognition
* confidence calibration
* error-based learning

Phải tránh biến tất cả thành một prompt lớn.

Propose:

`TeachingStrategy`

as explicit structured concept.

Potential example:

* `SOCRATIC_GUIDANCE`
* `MINIMAL_HINT`
* `WORKED_EXAMPLE`
* `STEP_BY_STEP_SCAFFOLD`
* `RETRIEVAL_QUIZ`
* `SPACED_REVIEW`
* `ERROR_CORRECTION`
* `SELF_EXPLANATION`
* `TRANSFER_PROBLEM`

Mỗi strategy cần:

* when to use
* when NOT to use
* target age
* target subject
* cognitive load
* prerequisite
* expected student action
* success criteria
* evidence/source

---

# 5. WS-D — MEMORY / RETENTION ENGINE

Research:

* forgetting curve
* spaced repetition
* FSRS
* retrieval practice
* review scheduling
* mastery decay
* confidence decay
* interleaving

Không biến SAM thành flashcard app.

Research cách kết hợp:

`Curriculum mastery`
+
`student weakness`
+
`forgetting risk`
+
`review schedule`

để SAM tự quyết định:

> Hôm nay nên học bài mới hay ôn lại?

Propose:

`Learning Agenda Engine`

Input:

* curriculum position
* mastery
* prerequisite
* recent mistakes
* review due
* available study time
* child fatigue/cognitive load

Output:

* learn
* practice
* review
* retrieve
* explain
* stop/rest

---

# 6. WS-E — TUTOR EVALUATION

Research cách đo một AI tutor tốt.

Không chấp nhận:

“LLM trả lời hợp lý.”

Xây conceptual:

# SAM Tutor Eval Suite

Evaluate:

* có đưa đáp án quá sớm không?
* có hỏi đúng câu hỏi không?
* có hiểu lỗi của học sinh không?
* có dùng đúng trình độ?
* có hint quá mạnh không?
* có khiến học sinh tự làm không?
* có kiểm tra lại understanding không?
* có chuyển sang bài transfer không?
* có giữ đúng nguồn/curriculum không?
* có hallucinate kiến thức không?
* có giữ consistency giữa nhiều lượt không?

Tạo candidate benchmark scenarios:

* học sinh lớp 2
* lớp 4
* lớp 6
* lớp 9
* lớp 12
* Math
* Vietnamese
* Science
* writing
* student asks for final answer
* student gives random answer
* student repeatedly fails
* student is overconfident
* student understands concept but calculates wrong

---

# 7. WS-F — PARENT COACH

Research parental-engagement evidence.

Question:

> Cha mẹ nên biết và làm gì?

Do NOT design Parent Mode as surveillance dashboard.

Reject:

* quá nhiều điểm số
* leaderboard
* micromanagement
* raw chat transcript dump
* “con học 42 phút hôm nay” without context

Research Parent Coach model:

`What child is learning`
+
`What child understands`
+
`What child struggles with`
+
`Whether it is normal`
+
`What parent should do`
+
`What parent should NOT do`

Example:

> Con đang nắm tốt phép nhân phân số nhưng còn yếu quy đồng.
> Tối nay không cần giảng bài cho con.
> Chỉ cần hỏi con giải thích bằng lời vì sao 1/2 = 2/4.

Explore:

* weekly parent brief
* concern escalation
* study habit recommendations
* motivation
* sleep/study balance
* parent questions to ask
* teacher escalation boundary
* age-appropriate autonomy
* privacy boundaries

---

# 8. MANDATORY REPO CLONE & CODE STUDY

Create isolated research directory.

Example:

`research/oss/learning-science/`

Do NOT add cloned repos into product dependency graph.

Do NOT vendor them into production.

Clone only shortlist below after verifying canonical repo URL and license.

---

## P0 REPO 1 — OATutor

Goal:

Study intelligent tutoring + mastery tracking.

Audit:

* knowledge-component representation
* Bayesian Knowledge Tracing
* exercise selection
* student state update
* content model
* feedback
* evaluation
* UI interaction

Question:

> Which parts are actual reusable architecture vs tightly coupled to OATutor?

Output:

`docs/research/oss/OATUTOR-AUDIT.md`

---

## P0 REPO 2 — KT-PSP-25 / StatusKT

Verify canonical repository first.

Goal:

Study knowledge tracing from problem-solving process.

Audit:

* input representation
* reasoning process representation
* labels
* model architecture
* training data
* evaluation metrics
* assumptions
* subject limitation
* inference cost
* practical applicability to K-12 mobile tutor

Question:

> Can SAM infer conceptual weakness from steps/reasoning without needing a heavy research model?

Output:

`docs/research/oss/KT-PSP-AUDIT.md`

---

## P0 REPO 3 — SocraticBench

Goal:

Study systematic evaluation of Socratic tutoring.

Audit:

* benchmark structure
* simulated student
* tutor evaluator
* scoring
* test cases
* LLM-as-judge risks
* reproducibility

Question:

> What should SAM copy as an evaluation methodology, not as product code?

Output:

`docs/research/oss/SOCRATICBENCH-AUDIT.md`

---

## P0/P1 REPO 4 — Socratic Tutor / ai-tutoring

Verify canonical repo.

Goal:

Study anti-answer / guidance-first tutoring interaction.

Audit:

* prompt/system policy
* subject logic
* state handling
* hint strategy
* student control
* privacy/local model support

Question:

> Is this real pedagogy architecture or mainly prompt engineering?

Output:

`docs/research/oss/SOCRATIC-TUTOR-AUDIT.md`

---

## P1 REPO 5 — OpenTutor

Goal:

Study adaptive learning + spaced repetition + memory.

Audit:

* FSRS/spaced repetition
* knowledge graph
* adaptive learning
* material ingestion
* notes/flashcards/quizzes
* student state
* cognitive-load handling

Question:

> Which learning-loop concepts make sense for SAM without turning SAM into Anki?

Output:

`docs/research/oss/OPENTUTOR-AUDIT.md`

---

## P1 REPO 6 — Tuteur IA

Goal:

Study multi-child + parent + persistent learning state.

Audit:

* parent account
* child profile
* grade/subject
* mastery display
* session memory
* family data model

Question:

> What is a useful Parent View vs a surveillance dashboard?

Output:

`docs/research/oss/TUTEUR-IA-AUDIT.md`

---

## P1 REPO 7 — Open Alpha

Goal:

Study parent coach + K-12 adaptive tutoring.

Audit:

* student tutor architecture
* parent AI coach
* progress model
* personalization
* account/family model

Question:

> Is Parent Coach actually useful or mainly marketing?

Output:

`docs/research/oss/OPEN-ALPHA-AUDIT.md`

---

## P1 REPO 8 — OpenLesson / “Tutor That Listens to You Think”

Verify canonical repository.

Goal:

Study verbal reasoning capture.

Audit:

* STT pipeline
* reasoning segmentation
* hesitation/error detection
* tutor response
* latency
* privacy
* mobile feasibility

Question:

> Can voice reasoning become a meaningful SAM learning interaction?

Output:

`docs/research/oss/VERBAL-REASONING-TUTOR-AUDIT.md`

---

# 9. CLONE RULES

For every repo:

Before clone:

* verify canonical GitHub repo
* record commit SHA
* record stars only as weak signal
* record latest meaningful commit
* record release history
* record license
* commercial implications
* dependency health
* issues
* test coverage
* abandoned/deprecated warning

After clone:

Must inspect at least:

* README
* LICENSE
* architecture/docs
* package manifests
* core domain code
* tests
* data model
* prompts if any
* evaluation scripts
* datasets
* sample flows

If runnable locally without risky setup:

Run:

* existing tests
* sample/demo
* minimal experiment

Record exact command and result.

Do NOT spend excessive time fixing a broken repo.

Classify:

`RUNS`
`PARTIAL`
`BROKEN`
`DOCS ONLY`
`NOT WORTH RUNNING`

---

# 10. README CLAIM VS CODE REALITY

For each repo create:

| Claimed capability | Evidence in code | Evidence in tests | Actually works? | SAM relevance |
| ------------------ | ---------------- | ----------------- | --------------- | ------------- |

This is mandatory.

If README says:

“adaptive learning”

Claude must identify exactly:

* where adaptation is implemented
* what state drives it
* whether it is deterministic or LLM prompt
* whether it is tested

Do NOT repeat marketing claims.

---

# 11. RESEARCH LEARNING SCIENCE SOURCES

Do not rely only on GitHub.

Research authoritative work from sources such as:

* Education Endowment Foundation
* learning-science reviews
* cognitive psychology
* educational psychology
* mastery learning literature
* retrieval practice
* spacing
* interleaving
* worked examples
* metacognition
* formative assessment
* tutoring research

Prioritize:

* systematic reviews
* meta-analyses
* peer-reviewed work
* established educational guidance

For each major method record:

| Method | Evidence strength | Age/subject | Good for | Risks | SAM usage |
| ------ | ----------------- | ----------- | -------- | ----- | --------- |

Do not state “research proves” without source.

---

# 12. VIETNAM K-12 REALITY

Everything must be checked against Vietnamese phổ thông context.

Research:

* curriculum structure
* grade levels
* subject boundaries
* textbook/source provenance
* school assessment
* common teaching patterns
* parent involvement
* device reality
* Vietnamese language
* Math notation
* primary-school reading level

Question:

> Does an imported Western tutoring method need adaptation for Vietnamese students?

Do not assume direct portability.

---

# 13. PEDAGOGY POLICY / LEARNING CONSTITUTION

Propose a candidate:

# SAM Learning Constitution

Not implementation.

Possible principles to evaluate:

1. Do not give final answer before reasonable student effort.
2. Diagnose before teaching.
3. Use the smallest useful hint.
4. Prefer student explanation over passive reading.
5. Distinguish conceptual vs procedural vs careless errors.
6. Practice retrieval, not just rereading.
7. Schedule review based on forgetting/mastery.
8. Adapt difficulty.
9. Verify transfer, not only same-question success.
10. Preserve source provenance.
11. Explain teaching strategy when appropriate.
12. Parent should coach, not solve.
13. Student autonomy increases with age.
14. Safety and emotional tone appropriate for children.

Each principle must include evidence or clear rationale.

---

# 14. PROPOSE STUDENT MODEL

Produce conceptual schema.

Example only:

`StudentProfile`

* grade
* curriculum
* preferences

`KnowledgeState`

* conceptId
* mastery
* confidence
* evidenceCount
* lastObserved
* forgettingRisk

`Misconception`

* concept
* pattern
* evidence
* confidence

`LearningEvent`

* problem
* attempt
* hint
* result
* reasoning
* strategy

`ReviewItem`

* concept
* dueAt
* reason

Do NOT implement.

Critique whether this becomes too complex.

---

# 15. TEACHING DECISION ENGINE

Propose explicit decision flow:

`What concept?`
→ `What prerequisite?`
→ `What does student already know?`
→ `What went wrong?`
→ `What cognitive load?`
→ `Which teaching strategy?`
→ `What student action?`
→ `How verify?`
→ `Update mastery`

Illustrate with at least:

* primary-school Math
* secondary Math
* Vietnamese reading/writing

---

# 16. EXAMPLE END-TO-END FLOWS

Produce at least 10 realistic tutoring scenarios.

Example:

### Scenario — lớp 5 phân số

Student:

> “Con không biết cộng 2/3 + 1/4.”

SAM must show:

1. identify concept
2. check prerequisite
3. diagnose
4. select teaching strategy
5. Socratic question
6. hint
7. child response
8. retry
9. transfer question
10. mastery update
11. review scheduling
12. parent insight

Do NOT just write chat dialogue.

Expose internal pedagogical state at product-spec level.

---

# 17. PARENT COACH FLOWS

Provide at least:

* daily brief
* weekly brief
* child repeatedly stuck
* child losing motivation
* child rushing/careless errors
* child doing well
* exam preparation
* parent asks “có cần học thêm không?”
* parent asks “tại sao con sai bài này?”
* parent tries to force too much study

For each:

`Evidence`
→ `Interpretation`
→ `Parent action`
→ `Do not do`
→ `Escalate?`

---

# 18. CRITICAL REVIEW — TRY TO KILL THE IDEA

Mandatory.

Write:

`docs/research/SAM-PEDAGOGY-CRITICAL-REVIEW.md`

At least 12 failure modes.

Include:

* false mastery inference
* LLM misdiagnosis
* over-scaffolding
* child gaming the tutor
* dependency on AI
* parent surveillance
* curriculum mismatch
* wrong age adaptation
* prompt-based “pedagogy theater”
* excessive complexity
* learning analytics without evidence
* cognitive overload
* privacy
* bias
* reward/gamification distortion
* hallucinated explanations

For each:

`Risk`
→ `Why`
→ `Detection`
→ `Mitigation`
→ `Kill condition`

---

# 19. COMPARE 3 ARCHITECTURE LEVELS

Compare:

## OPTION A — SIMPLE

`Curriculum + RAG + Tutor Prompt`

## OPTION B — STRUCTURED TUTOR

`Curriculum + Student Model + Teaching Strategies + Eval`

## OPTION C — FULL ADAPTIVE LEARNING ENGINE

`Knowledge Graph + Knowledge Tracing + Misconception Model + Spacing + Tutor Eval + Parent Coach`

Score:

* educational value
* complexity
* data requirements
* observability
* explainability
* implementation effort
* child safety
* maintainability
* product differentiation

Recommend smallest architecture that creates real learning value.

---

# 20. REPO RECOMMENDATION

Final classification for every cloned repo:

`ADOPT PATTERN`
`POC`
`REFERENCE`
`REJECT`

For anything marked ADOPT PATTERN:

Specify exact pattern.

Example:

Bad:

> “Use OATutor.”

Good:

> “Study its BKT mastery-update pattern, but do not adopt its whole content/domain model.”

---

# 21. REQUIRED DELIVERABLES

Create:

`docs/research/SAM-LEARNING-CURRENT-TRUTH.md`

`docs/research/SAM-LEARNING-SCIENCE-EVIDENCE-MAP.md`

`docs/research/SAM-STUDENT-MODEL-RESEARCH.md`

`docs/research/SAM-TEACHING-STRATEGY-ENGINE.md`

`docs/research/SAM-MEMORY-RETENTION-ENGINE.md`

`docs/research/SAM-TUTOR-EVALUATION-FRAMEWORK.md`

`docs/research/SAM-PARENT-COACH-RESEARCH.md`

`docs/research/SAM-LEARNING-CONSTITUTION.md`

`docs/research/SAM-PEDAGOGY-CRITICAL-REVIEW.md`

`docs/research/SAM-PEDAGOGY-ARCHITECTURE-RECOMMENDATION.md`

plus OSS audit files listed above.

If existing docs already cover a topic:

UPDATE canonical doc.

Do not create duplicate truth.

---

# 22. FINAL RECOMMENDATION

Return:

## TOP 5 findings

## TOP 5 pedagogical patterns worth adopting

## TOP 3 repo patterns worth POC

## TOP 5 things SAM must NOT do

## Parent Coach recommendation

## Student Model recommendation

## Tutor Eval recommendation

## Smallest viable Learning Engine

## Biggest technical risk

## Biggest educational risk

## What should NOT be built yet

## Founder decisions required

---

# 23. JIRA / CONFLUENCE

Create/find the correct Jira issue according to existing project conventions.

Do not invent project key.

Start comment:

* scope
* repo shortlist
* research questions
* no implementation gate

Log actual work.

Completion comment:

* cloned repos + SHA
* tests/demo status
* top patterns
* critical findings
* licensing concerns
* recommended architecture level
* Founder decisions

Confluence:

Update/create the appropriate Learning Science / Pedagogy research page.

Link:

`Jira ↔ Confluence ↔ repo docs`

Final Jira status:

`In Review`

NOT Done.

---

# 24. STOP GATE

DO NOT:

* change production tutoring behavior
* change prompts
* implement Student Model
* add BKT
* implement Parent Coach
* add new DB schema
* add dependencies
* copy OSS code into production
* accept ADR
* merge main

After completion:

# STOP

Report:

**SAM Learning Science & Pedagogy research complete. Repos cloned and audited against code reality. Research only. Ready for Founder and independent critique.**

Wait for approval.
