FOUNDER DECISION — OPEN POINTS / NEXT EXECUTION

Cảm ơn đã expose rõ các quyết định tự chủ.

Founder quyết định:

1. WAL-183 CROSS-SUBJECT FALSIFICATION

ACCEPT quyết định bỏ test chéo môn ở tầng challengeSignalFor.

Nếu challengeSignalFor thực sự subject/skill-agnostic,
không cần tạo một test Science/Tiếng Việt chỉ để satisfy checklist.

Nhưng ghi rõ phạm vi claim:

PROVEN:
Adaptive Challenge POLICY có thể subject-agnostic.

NOT YET PROVEN:
challenge CONTENT / activity difficulty semantics
có thể scale generic cross-subject.

Không reopen WAL-183 chỉ vì việc này.

Cross-subject falsification sẽ xảy ra khi chúng ta có
real challenge content/activity generation/selection.

--------------------------------------------------

2. EXERCISE DIFFICULTY CONTENT

Founder xác nhận đây là REAL PRODUCT GAP,
nhưng KHÔNG yêu cầu implement hàng loạt ngay.

🌱 Củng cố
🎯 Vừa sức
🚀 Thử thách

chỉ thật sự có ý nghĩa khi activity/content có thể thay đổi
theo challenge recommendation.

Tuy nhiên:

DO NOT hand-author
Easy/Normal/Hard exercises per lesson.

DO NOT create three exercise banks/screens per lesson.

Keep this as a capability/research backlog item.

Future direction to challenge:

Curriculum / SkillCase
        ↓
Allowed Knowledge + TutorScope
        ↓
Activity / Item Model
        ↓
Challenge Dimensions
        ↓
Bounded Item Selection / Variant
        ↓
Learning Tool
        ↓
Evidence.

Challenge dimensions may include:

- prerequisite demand;
- reasoning depth;
- number of steps;
- novelty;
- representation;
- transfer;
- scaffold;
- assistance.

HARDER != FUTURE CURRICULUM.

Do not start implementation until current Product Experience
and real subject journeys create enough evidence.

If Jira has no representation of this gap,
create/re-scope ONE research/capability ticket only.
No implementation Epic yet.

--------------------------------------------------

3. WAL-176 GOLDEN JOURNEY

CONTINUE.

Founder agrees WAL-176 is an ongoing Product Discovery / Walking Epic
and does not need an artificial Done condition yet.

Next priority:

TIẾNG VIỆT
→ LỊCH SỬ
→ TIẾNG ANH.

Walk as REAL learner on Nokia.

Do not merely check whether screens open.

For each subject ask:

A. Can the learner understand where they are?
   Bookshelf → Book → Chapter/Lesson → activity.

B. Does the experience feel appropriate to THIS subject,
   rather than a generic lesson/dashboard/chat?

C. Is LearningIntent meaningful?
   Do not show fake choices.

D. Does SAM have the correct LearningContext?

E. Does SAM help at the correct moments?

F. Are source/provenance claims truthful?

G. Does interaction produce TRACE or real EVIDENCE correctly?

H. Does resulting Evidence affect Learning Map / Parent / Next Action coherently?

I. Are there contradictions across screens?

J. What happens with insufficient structured corpus?

K. Does existing UI/UX cover the need,
   or is a genuinely new Learning Surface required?

Do not create new UI simply because a subject feels different.

First attempt:

existing Surface
→ existing component extension
→ composition of existing components
→ only then new Surface if evidence requires it.

--------------------------------------------------

4. IMPORTANT — USE THESE JOURNEYS AS FALSIFICATION

Tiếng Việt, Lịch sử và Tiếng Anh are not just QA coverage.

Use them to challenge current architecture.

Especially look for whether they falsify assumptions around:

- Lesson Workspace;
- LearningIntent;
- Hierarchical LearningContext;
- PlannedAct;
- Evidence model;
- Learning Visual representations;
- Adaptive Challenge;
- source/provenance;
- activity taxonomy;
- Book → Lesson hierarchy;
- Parent projection.

Examples:

Lịch sử may expose:
OCR text exists but structured event/date semantics do not.

Tiếng Việt may expose:
writing/reading cannot be modeled like correct/incorrect Math evidence.

Tiếng Anh may expose:
voice/listening/pronunciation and repeated practice require
different interaction/evidence semantics.

Do not force these subjects into existing abstractions
just to make the journey PASS.

A useful FAIL/PARTIAL with evidence is more valuable.

--------------------------------------------------

5. GOLDEN JOURNEY OUTPUT

For each walked subject:

PASS / PARTIAL / FAIL

with only:

- journey walked;
- real content used;
- what worked;
- what was falsified;
- product gap;
- architecture gap if any;
- evidence;
- smallest proposed action.

If gap is local/reversible:
→ Jira
→ fix
→ test
→ Nokia
→ PR/CI/merge
→ continue.

If genuine Product fork:
→ stop that branch and ask Founder.

Do not stop the whole autonomous backlog.

--------------------------------------------------

6. WAL-176 CLOSURE

Do NOT close WAL-176 yet.

After Tiếng Việt + Lịch sử + Tiếng Anh are walked,
reassess whether Golden Journey has enough representative coverage.

At that point propose one of:

A. CLOSE — representative subject families sufficiently proven.

B. KEEP AS PERIODIC REGRESSION JOURNEY.

C. SPLIT remaining discovery into narrower capability tickets
   and close WAL-176.

Founder does not need to define this before the evidence exists.

--------------------------------------------------

NEXT

Continue autonomous execution now:

Tiếng Việt
→ Lịch sử
→ Tiếng Anh

using real device + real corpus wherever available.

Fix bounded evidence-backed gaps automatically.

Do not expand UI unnecessarily.

Do not hand-author subject content just to make a journey pass.

DO NOT OPTIMIZE FOR GREEN STATUS.
OPTIMIZE FOR FINDING WHERE THE PRODUCT MODEL BREAKS.
