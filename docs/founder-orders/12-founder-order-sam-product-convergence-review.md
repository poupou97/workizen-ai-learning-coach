FOUNDER ORDER — SAM PRODUCT CONVERGENCE REVIEW
CLAUDE × GPT × FOUNDER
CHALLENGE → RECONCILE → CONVERGE → REPORT → STOP

Không code.

Vòng trước anh đã hoàn thành:
SAM-PRODUCT-EXPERIENCE-REVIEW.md

Founder và GPT đã review toàn bộ báo cáo.

Founder đánh giá vòng phản biện vừa rồi có giá trị.
GPT cũng đồng ý với phần lớn diagnosis của anh.

Nhưng GPT KHÔNG đồng ý hoàn toàn với Product Experience Model vNext
mà anh đề xuất.

Founder không muốn:

Claude nói một model,
GPT nói model khác,
Founder có hypothesis thứ ba,
rồi cuối cùng implementation chọn ngẫu nhiên một hướng.

Vòng này có đúng một mục tiêu:

CONVERGENCE.

Founder + GPT + Claude phải đi đến
MỘT PRODUCT EXPERIENCE MODEL đủ rõ để implementation sau này
không còn hiểu theo ba cách khác nhau.

Không bảo vệ proposal cũ chỉ vì anh viết nó.
Không mặc định GPT đúng.
Không mặc định Founder đúng.

Hãy phản biện từng điểm dưới đây bằng:
product reasoning + UX reasoning + pedagogy + evidence hiện có.

==================================================
CONTEXT — NHỮNG ĐIỂM ĐÃ GẦN NHƯ THỐNG NHẤT
==================================================

Founder + GPT đồng ý mạnh với các kết luận sau của anh:

1. 38 concepts KHÔNG phải final product specification.

Chúng chứa nhiều assumption của một EdTech/course product:
- fake mastery %
- score /100
- XP
- streak
- rank
- leaderboard
- locked progression
- sibling comparison.

Những thứ đó mâu thuẫn với hướng evidence-based hiện tại của SAM.

Do đó:

38 CONCEPTS
=
DESIGN / INTERACTION / PRODUCT RESEARCH LIBRARY

không phải:

38 SCREENS TO IMPLEMENT.

2. Các concept tốt phải được khai thác lại.

Đặc biệt:

09 Camera Confirm
14 Your Turn
16 Why This Method
18 Review
23 Vietnamese activity tools
24 Essay
25 Physics simulation
27 History/source reasoning
28 Geography/map-data interaction
35 SAM Voice

Không nhất thiết giữ UI nguyên bản.
Giữ design/interaction insight.

3. Các pattern sau phải loại bỏ hoặc sửa mạnh:

- fabricated mastery percentage;
- leaderboard trẻ em;
- sibling ranking;
- Top X%;
- pedagogically invalid method;
- source = answer-site links;
- answer shown before learner attempts;
- generic chatbot replacing learning flow.

4. Bookshelf + real textbook identity là product anchor quan trọng.

5. Same learning content + different learning intent
có thể tạo ra different learning experience.

6. Camera Confirm / human confirmation là pattern đúng.

7. SAM không được mặc định:
camera → answer.

8. Source content và SAM explanation phải phân biệt.

9. Subject-specific experience là cần thiết,
nhưng không nhất thiết subject-specific screen.

10. Architecture K–12 vẫn có thể giữ,
nhưng UX không cần giả vờ rằng Grade 2 và Grade 11
đã được giải quyết giống nhau.

Một khả năng:

ARCHITECTURE = K–12
UX VALIDATION = một cohort trước, ví dụ Grade 4–6.

Đây chưa phải quyết định cuối.
Anh được quyền phản biện.

==================================================
DISPUTE #1
READ / EXPLORE BOOK:
MODE, INTENT, ACTION HAY OVERLAY?
==================================================

Anh đề xuất:

“Xem sách không phải mode.
Nó là lớp phủ luôn có.”

GPT chỉ đồng ý một phần.

GPT lập luận:

Một học sinh hoàn toàn có user job:

“Con chỉ muốn mở SGK Khoa học 5 xem Bài 3.”

Đó là một intent hợp lệ.

Không phải mọi lần mở SAM đều phải:
- dạy;
- assess;
- sinh LearningEvidence.

SAM có thể phục vụ cả:

LEARNING

và

REFERENCE / EXPLORATION.

Do đó GPT đề xuất distinction:

READ / EXPLORE BOOK
=
legitimate USER INTENT / ACTION

nhưng

NOT necessarily a PEDAGOGICAL LEARNING MODE.

Đồng thời Read/Explore vẫn có thể xuất hiện như contextual overlay
trong Prepare / Review / Homework.

Ví dụ:

Book Home
→ Xem sách

và khi đang Review:
→ Xem chỗ này trong SGK.

Hãy phản biện.

Cần chốt rõ:

- Read có phải first-class user intent không?
- Có phải learning mode không?
- Có xuất hiện ở Book Home không?
- Có luôn accessible trong learning session không?
- Có sinh LearningEvidence không?
- Nếu không sinh evidence thì có vấn đề gì không?

Đừng tranh luận bằng từ “mode”.
Hãy chốt USER JOB + UX BEHAVIOR.

==================================================
DISPUTE #2
BOOK → LESSON → INTENT
HAY
BOOK → INTENT → LESSON?
==================================================

Đây là disagreement quan trọng nhất.

Anh đề xuất:

Book
→ Lesson
→ Intent
→ Activity
→ Pattern.

Lý do:
mỗi lesson trong một book có learning state khác nhau.

GPT đồng ý về data reasoning,
nhưng không đồng ý biến nó thành UX hierarchy bắt buộc.

Ví dụ trẻ có thể nghĩ:

“Con muốn ôn Toán.”

nhưng KHÔNG biết:
“Con cần ôn Bài 6.”

Hoặc:

“Mai có Khoa học.”

SAM có timetable/context
và có thể suggest lesson.

Hoặc:

“Con muốn học trước Tiếng Anh.”

Trong các trường hợp đó:

Intent
→ suggested lesson

có vẻ tự nhiên hơn:

Lesson
→ Intent.

GPT đề xuất:

LESSON
và
LEARNING INTENT

là TWO DIMENSIONS,
không phải quan hệ parent-child cố định.

Hai entry paths có thể cùng tồn tại:

A. Learner knows lesson:

Book
→ Lesson
→ Intent
→ Experience.

B. Learner knows goal:

Home / Book
→ Intent
→ SAM suggests Lesson
→ Experience.

Ngoài ra:

Next Best Action
có thể đã resolve cả Lesson + Intent,
nên learner không cần chọn cái nào.

Hãy phản biện mạnh điểm này.

Founder muốn một quyết định rõ:

Có thực sự cần một canonical order không?

Hay canonical model phải là:

Learning Context =
Learner
+ Book
+ Lesson/Activity
+ Intent
+ State
+ Timetable
+ Evidence

và UI chỉ resolve các dimensions còn thiếu?

Nếu đúng, hãy nói rõ.

Nếu sai, bảo vệ Book→Lesson→Intent.

==================================================
DISPUTE #3
CAMERA GLOBAL vs BOOK/LESSON CAMERA
==================================================

Ở đây GPT gần như đồng ý với anh:

CAMERA = GLOBAL CAPABILITY.

Vì trẻ có thể chụp:
- SGK;
- workbook;
- vở;
- worksheet;
- đề giáo viên;
- bảng;
- tài liệu ngoài SGK.

Không nên bắt trẻ chọn book trước camera.

Nhưng GPT đề xuất cả hai entry:

GLOBAL CAMERA
→ perception
→ confirmation
→ context resolution.

và:

LESSON CAMERA
→ camera với Book/Lesson context pre-bound.

Ví dụ trong Bài 6:

“Chụp bài của bài này.”

Hãy xác nhận/challenge.

Cần chốt:

Camera là:
- mode?
- capability?
- global entry?
- contextual shortcut?

Và camera result được attach vào learning context thế nào?

==================================================
DISPUTE #4
HOME = ONE TASK
HAY
RECOMMENDATION-FIRST HOME?
==================================================

Anh đề xuất:

Home trả lời đúng một câu:

“Bây giờ làm gì?”

Một primary recommendation.

GPT đồng ý direction nhưng phản đối interpretation quá literal.

GPT lo rằng Home có thể trở thành:

“AI quyết định trẻ phải làm gì.”

Một learner có thể mở app vì:
- mắc bài tập;
- muốn xem sách;
- muốn ôn kiểm tra;
- mai có tiết;
- muốn tiếp tục hôm qua.

GPT đề xuất:

RECOMMENDATION-FIRST HOME

không phải:

ONE-TASK-ONLY HOME.

Ví dụ:

PRIMARY:

“Mai có Khoa học.
Xem trước Bài 3 · khoảng 7 phút.”

[Bắt đầu]

Stable escape routes:

📷 Chụp bài
📚 Sách của con
💬 Hỏi SAM

Có thể thêm route khác nếu evidence chứng minh cần.

Founder thích hướng:

AI-FIRST
nhưng
USER STILL HAS AGENCY.

Hãy phản biện.

Chốt Home phải tối ưu cho:

NEXT BEST ACTION

nhưng không biến thành:

NEXT ONLY ACTION.

==================================================
DISPUTE #5
SUBJECTS vs BOOKSHELF
==================================================

Anh đề xuất bỏ Subjects screen
và để Bookshelf thay thế.

GPT cho rằng quyết định này có thể quá sớm.

BOOK != SUBJECT.

Một subject có thể có:

- SGK tập 1;
- SGK tập 2;
- workbook;
- chuyên đề;
- imported materials;
- student notes;
- assessments;
- learning history;
- mastery/evidence;
- subject-specific activities.

Trẻ cũng có thể nghĩ:

“Toán của con”

chứ không nhất thiết:

“Toán 5 Tập 1.”

GPT KHÔNG nhất thiết yêu cầu giữ concept 06 Subjects screen.

Nhưng GPT đề xuất giữ:

SUBJECT CONTEXT

trong Product IA/domain model.

Bookshelf giải quyết:

CONTENT RECOGNITION.

Subject Context giải quyết:

LEARNING DOMAIN CONTINUITY.

Hãy phản biện:

- Có cần Subject screen không?
- Có cần Subject Context không?
- Book Home và Subject Home có trùng nhau không?
- Subject nên là navigation entity hay chỉ context?
- Với nhiều sách cùng môn, user đi đâu?
- Progress/history/activity theo môn nằm ở đâu?

Đừng quyết định dựa trên việc screen hiện tại đã tồn tại hay chưa.

==================================================
DISPUTE #6
GAMIFICATION
==================================================

GPT đồng ý bỏ:

- leaderboard;
- sibling comparison;
- Top X%;
- fake mastery percentage;
- fabricated scores;
- engagement pressure.

Nhưng GPT chưa muốn biến:

“NO GAMIFICATION”

thành doctrine.

SAM vẫn có thể có:

- celebration;
- mascot reaction;
- personal milestones;
- discovery;
- completion moments;
- visual journey;
- “lần đầu con tự làm được”;
- “lần này con cần ít gợi ý hơn”;
- collectibles hoặc progress metaphor nếu không gây nghiện.

Distinction GPT đề xuất:

BAD:
competitive / fabricated / addictive / engagement-maximizing gamification.

POTENTIALLY GOOD:
learning-centered celebration
+ competence feedback
+ personal growth
+ playful interaction.

SAM mascot có thể là một lợi thế lớn ở đây.

Hãy phản biện.

Founder muốn tránh hai cực:

Duolingo hóa SAM

và

biến SAM thành phần mềm giáo dục khô khan.

Chốt nguyên tắc product-level,
không cần tạo thêm một rừng rules.

==================================================
DISPUTE #7
SAM PERSONA / PRESENCE
==================================================

GPT cho rằng report của anh rất mạnh về:

Book
Intent
Evidence
IA
Patterns

nhưng SAM đang có nguy cơ trở thành:

recommendation service
+
pedagogy actuator.

Trong khi tên sản phẩm là:

HỌC CÙNG SAM.

SAM phải tạo cảm giác:

“Con đang học cùng SAM.”

Không phải:

“Con đang sử dụng curriculum engine có mascot.”

Hãy đánh giá lại role của SAM xuyên suốt product.

Ví dụ SAM có thể:

- chào đúng context;
- nhớ chỗ hôm qua con vướng;
- đề nghị một việc;
- hỏi trẻ dự đoán;
- im lặng để trẻ thử;
- xuất hiện khi trẻ cần;
- lùi lại sau success;
- vui khi trẻ tự sửa;
- nói “SAM chưa chắc”;
- nói “con thử trước nhé”;
- giải thích tại sao chọn phương pháp;
- quay lại đúng chỗ cần ôn;
- celebrate independence.

SAM presence không có nghĩa:
chat bubble everywhere.

Câu hỏi:

WHERE SHOULD SAM BE PRESENT?

WHERE SHOULD SAM DISAPPEAR?

WHAT MAKES SAM FEEL LIKE A COMPANION?

WHAT WOULD MAKE SAM FEEL LIKE A CHATBOT?

WHAT WOULD MAKE SAM FEEL LIKE A MASCOT STUCK ON TOP OF SOFTWARE?

Đề xuất SAM Interaction Model.

==================================================
DISPUTE #8
38 CONCEPTS — GIỮ BAO NHIÊU GIÁ TRỊ?
==================================================

Report của anh nhấn mạnh bốn concept tốt nhất.

GPT nghĩ bộ 38 có nhiều reusable interaction ideas hơn:

09 Camera Confirm
14 Your Turn
16 Why This Method
18 Review
23 Vietnamese tools
24 Essay
25 Physics simulation
27 History/source reasoning
28 Geography/map/data
35 SAM Voice

Có thể còn thêm sau review.

Không giữ pixel.
Không giữ fake metrics.
Không giữ wrong pedagogy.

Nhưng đừng vì product model ẩn của 38 concept sai
mà vứt interaction insight tốt.

Hãy tạo distinction:

PRODUCT MODEL
vs
INTERACTION IDEA
vs
VISUAL LANGUAGE.

Một concept có thể:

FAIL product model

nhưng

PASS interaction idea.

Chốt cách 38 concepts sẽ được sử dụng về sau.

==================================================
DISPUTE #9
K–12 vs FIRST UX COHORT
==================================================

Anh đề xuất có thể chọn Grade 4–6 để đúng trước.

GPT đồng ý với ý tưởng validation cohort,
nhưng không muốn nó vô tình biến thành:

SAM = Grade 4–6 product.

Một possible model:

PRODUCT VISION = K–12

KNOWLEDGE / ARCHITECTURE = K–12

CONTENT PIPELINE = K–12

UX VALIDATION COHORT = Grade 4–6 FIRST

sau đó:

younger cohort adaptation
older cohort adaptation.

Hãy phản biện:

- Có nên chọn 4–6?
- Hay 3–5?
- Hay cohort khác?
- Những gì được phép generalize?
- Những gì bắt buộc age-adaptive?
- Làm sao tránh build UI quá trẻ con khiến THPT không dùng được?

Founder muốn K–12 vision vẫn còn.

==================================================
DISPUTE #10
BOOK-FIRST vs CAMERA-FIRST vs AI-FIRST
==================================================

Report của anh đặt Bookshelf rất cao.

Nhưng chính câu hỏi mở của anh nói:

Nếu phần lớn use case thật là
“con có bài tập cần giúp”

thì Camera có thể quan trọng hơn Bookshelf.

Founder muốn tránh việc vô tình biến SAM thành:

DIGITAL TEXTBOOK APP.

Nhưng cũng không muốn:

CAMERA HOMEWORK SOLVER.

Và càng không muốn:

GENERIC AI CHATBOT.

Hãy phản biện ba possible anchors:

BOOK-FIRST
CAMERA-FIRST
AI/NEXT-ACTION-FIRST.

Có thể câu trả lời không phải chọn một.

Ví dụ:

BOOK = curriculum/content anchor.

CAMERA = real-world input anchor.

NEXT BEST ACTION = daily UX anchor.

SAM = relationship/interaction anchor.

Nếu đây là synthesis đúng,
hãy formalize nó.

==================================================
PROPOSED SYNTHESIS FROM GPT
— CHALLENGE THIS
==================================================

GPT hiện hình dung:

                    SAM HOME
                       │
              NEXT BEST ACTION
                       │
          ┌────────────┼────────────┐
          │            │            │
       Camera       Bookshelf     Ask SAM
          │            │
          │           Book
          │            │
          │       Lesson / Explore
          │            │
          └──────► Learning Context
                       │
                 Learning Intent
                       │
               Activity / Pattern
                       │
             Interaction Surface(s)
                       │
                      SAM
                       │
               Learning Evidence
                       │
                 Student State
                       │
               Next Best Action
                       │
                      Home

Nhưng GPT bổ sung:

Intent và Lesson không có canonical parent-child relationship.

Có thể:

Book → Lesson → Intent

hoặc:

Intent → suggested Lesson

hoặc:

Next Best Action
đã resolve cả hai.

GPT cũng đề xuất bốn product anchors:

BOOK
= curriculum/content anchor.

CAMERA
= real-world input anchor.

NEXT BEST ACTION
= daily experience anchor.

SAM
= relationship/interaction anchor.

Đây KHÔNG phải quyết định Founder.

Đây là proposal để anh phá nếu sai.

==================================================
WHAT I WANT FROM CLAUDE
==================================================

Không viết một Product Model thứ ba rồi bỏ hai model còn lại.

Hãy làm:

CLAUDE MODEL
vs
GPT REVIEW
vs
FOUNDER INTENT

và RECONCILE từng disagreement.

Với mỗi dispute:

1. Claude original position.
2. GPT position.
3. Founder intent underlying both.
4. Evidence supporting each.
5. What each position gets right.
6. What each gets wrong.
7. Final synthesis.
8. Decision proposed.

Sử dụng một trong:

AGREE
AGREE WITH MODIFICATION
REJECT
UNRESOLVED — NEED USER EVIDENCE.

Không dùng:
“cả hai đều đúng”
rồi không chốt gì.

Nếu hai ý đúng ở hai layer khác nhau,
hãy nói chính xác layer:

USER INTENT
NAVIGATION
DOMAIN MODEL
PEDAGOGICAL MODE
CAPABILITY
SURFACE
STATE
CONTENT MODEL.

==================================================
CREATE A SHARED VOCABULARY
==================================================

Một nguyên nhân khiến chúng ta dễ “ông nói gà bà nói vịt”
là cùng một từ đang được dùng ở nhiều layer.

Hãy định nghĩa ngắn và chốt vocabulary:

BOOK
SUBJECT
LESSON
ACTIVITY
LEARNING INTENT
LEARNING MODE
CAPABILITY
EXPERIENCE PATTERN
SURFACE
NEXT BEST ACTION
SAM
EVIDENCE
STUDENT STATE.

Đặc biệt:

INTENT != MODE != CAPABILITY != SURFACE.

Nếu từ nào không cần,
hãy bỏ.

Không tạo ontology khổng lồ.

Chỉ đủ để Founder + GPT + Claude
nói cùng một ngôn ngữ.

==================================================
FINAL CONVERGENCE ARTIFACT
==================================================

Update/create:

SAM-PRODUCT-EXPERIENCE-CONVERGENCE.md

Tài liệu phải có:

1. SHARED VOCABULARY

2. AGREED PRODUCT PRINCIPLES
   Chỉ những gì thực sự đã hội tụ.

3. DISPUTE RESOLUTION TABLE

4. FINAL PRODUCT EXPERIENCE MODEL

5. FINAL IA

6. HOME MODEL

7. BOOK / SUBJECT MODEL

8. LESSON + INTENT RESOLUTION MODEL

9. CAMERA MODEL

10. READ / EXPLORE MODEL

11. SAM INTERACTION MODEL

12. SUBJECT-SPECIFIC EXPERIENCE MODEL

13. AGE / K–12 MODEL

14. MOTIVATION / CELEBRATION MODEL

15. ROLE OF THE 38 CONCEPTS GOING FORWARD

16. STUDENT DAILY LOOP

17. BOOK LOOP

18. PREPARE LOOP

19. REVIEW LOOP

20. CAMERA HOMEWORK LOOP

21. READ / EXPLORE LOOP

22. PARENT LOOP

23. WHAT WE EXPLICITLY WILL NOT BUILD

24. UNRESOLVED QUESTIONS THAT REQUIRE REAL USER EVIDENCE

25. FINAL CLAUDE RECOMMENDATION.

==================================================
IMPORTANT — CONVERGENCE, NOT CONSENSUS THEATER
==================================================

Founder muốn THỐNG NHẤT,
không muốn consensus giả.

Nếu evidence chưa đủ:

UNRESOLVED — NEED USER EVIDENCE.

Đừng invent answer.

Nhưng chỉ dùng trạng thái này cho thứ thực sự cần trẻ/phụ huynh thật.

Không dùng nó để né quyết định architecture/product logic
mà chúng ta đã đủ evidence để chốt.

Nếu GPT sai:
nói GPT sai.

Nếu Founder sai:
nói Founder sai.

Nếu proposal cũ của Claude sai:
tự sửa.

Founder không quan tâm ai thắng tranh luận.

Founder muốn:

ONE COHERENT PRODUCT.

==================================================
NO CODE
==================================================

Vòng này vẫn:

NO PRODUCT IMPLEMENTATION.

Không tự tạo execution backlog rồi chạy.

Không sửa UI theo kết luận.

Không refactor runtime theo model mới.

Có thể inspect repo/device/evidence nếu cần.

Sau khi hoàn thành convergence report:

STOP.

Gửi Founder:

- report;
- bảng những điểm đã hội tụ;
- những điểm thực sự unresolved;
- recommendation cuối.

Founder sẽ đưa report lại cho GPT.

Founder + GPT sẽ review.

Nếu còn disagreement:
chúng ta giải quyết disagreement cụ thể.

Nếu đã hội tụ:
Founder mới phát implementation order.

Mục tiêu không phải tạo thêm một tài liệu đẹp.

Mục tiêu là:

FOUNDER
+
GPT
+
CLAUDE

DÙNG CÙNG MỘT PRODUCT MODEL
VÀ CÙNG MỘT NGÔN NGỮ

TRƯỚC KHI VIẾT THÊM CODE.

Không code.
Converge.
Report.
STOP.
