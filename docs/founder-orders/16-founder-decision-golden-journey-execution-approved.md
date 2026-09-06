FOUNDER DECISION — GOLDEN JOURNEY EXECUTION APPROVED

Tôi đã review `SAM-NEXT-EXECUTION-PROPOSAL.md`.

Proposal được chấp nhận với các quyết định sau.

==================================================
1. FOUNDER DECISIONS
==================================================

Q1 — Nối Home → Navigation:
APPROVED.

Đây là khoảng hở hẹp và có evidence rõ nhất.

Nhưng mục tiêu KHÔNG phải chỉ truyền thêm
`agenda.kind` / `conceptId`.

Mục tiêu product là:

SAM RECOMMENDATION
→ START
→ CONTEXT SURVIVES
→ RIGHT LEARNING EXPERIENCE.

Q2 — Golden Journey:
APPROVED.

Dùng:

KHOA HỌC 5
→ BÀI 1
→ CHUẨN BỊ
→ EXPERIMENT / PREDICTION.

Không đổi sang Camera-first ở vòng này.

Camera vẫn là first-class entry,
nhưng không cần nhồi vào Golden Journey #1.

Q3 — tín hiệu “tiết đã học xong”:
RECORD AS OPEN RESEARCH/BACKLOG QUESTION ONLY.

Không implement signal mới.

Q4 — Assessment:
KEEP UNPROVEN.

Không sửa Assessment trong vòng này.

==================================================
2. EXECUTION TARGET
==================================================

Bây giờ được phép CODE + TEST + UPDATE JIRA
trong phạm vi Golden Journey.

Không chạy backlog theo thứ tự Ready.

Target:

REAL CONTEXT
→ SAM RECOMMENDATION + REASON
→ START
→ CONTEXT SURVIVES NAVIGATION
→ BOOK / LESSON / ACTIVITY
→ PREPARE INTENT
→ EXPERIENCE
→ SAM INTERACTION
→ CHILD ACTION
→ TRACE / EVIDENCE
→ SUMMARY
→ CONTINUITY
→ HOME / NEXT ACTION.

Founder cần trải nghiệm được LOOP này trên Nokia.

==================================================
3. IMPORTANT — MISSING #1 IS NOT THE FINISH LINE
==================================================

Nối:

Home → Navigation

là việc đầu tiên.

Nhưng không được gọi Golden Journey DONE
chỉ vì context đã truyền xuyên navigation.

Trong journey Khoa học 5 Bài 1,
Founder phải thực sự nhìn thấy:

SAM biết vì sao đề xuất bài này
→ trẻ bấm Bắt đầu
→ app vào đúng context
→ intent Chuẩn bị được giữ
→ trẻ được hỏi dự đoán trước
→ SAM không lộ kết quả
→ trẻ quan sát / ghi
→ SAM phản hồi dựa trên interaction thật
→ session kết thúc
→ state/evidence/trace được ghi đúng
→ quay Home
→ recommendation/continuity phản ánh trạng thái mới hợp lý.

Không cần architecture mới để đạt điều đó.

==================================================
4. SAM — IMPLEMENT BEHAVIOR, NOT ENGINE
==================================================

Được phép implement SAM behavior cần thiết
cho Golden Journey.

KHÔNG xây `SamPresenceEngine`.

Trong case này:

HOME
SAM nói một câu có reason thật.

BEFORE EXPERIMENT
SAM hỏi dự đoán dựa trên `duDoan`.

CHILD THINKING / OBSERVING
SAM lùi lại / không chèn lời vô ích.

AFTER CHILD ACTION
SAM phản hồi cụ thể dựa trên interaction/evidence thật.

END
SAM tổng kết cái vừa quan sát được,
không praise chung chung.

RETURN
continuity phải dựa trên state thật.

Nếu behavior cần một implementation nhỏ:
làm.

Không tổng quát hóa trước khi có thêm case.

==================================================
5. WAL-175
==================================================

Trước tiên xác nhận WAL-175 trên Nokia.

Nếu cần USB thì chờ/cắm USB theo môi trường hiện có.

Audit result đã được chấp nhận:

- core LearningIntent: KEEP;
- fake-choice avoidance: KEEP;
- `activitiesForIntent`: AD HOC HYPOTHESIS;
- KHÔNG gọi nó Experience Pattern;
- KHÔNG dùng các nhánh chưa có corpus thật
  làm evidence cho architecture.

Nếu Nokia làm lộ lỗi:
fix.

Sau verify:
PR/CI/merge theo workflow bình thường.

==================================================
6. JIRA
==================================================

Được phép reconcile Jira theo proposal đã review.

- WAL-102 KEEP.
- WAL-104 KEEP; không trùng LearningIntent.
- WAL-138 RE-SCOPE:
  vấn đề là context bị đứt SAU recommendation,
  không phải thiếu recommendation.
- WAL-143 DONE-BUT-PRODUCT-REVIEW;
  Assessment framing vẫn UNPROVEN.
- WAL-166/167/168/170/172/173 KEEP.
- WAL-175 theo audit ở trên.

Tạo tối thiểu ticket cần thiết cho Golden Journey.

Không tạo 30–50 tickets.

Ghi câu hỏi:

“Làm sao biết tiết/bài đã thực sự được học trên lớp?”

vào research/backlog phù hợp.

KHÔNG implement.

==================================================
7. GOLDEN JOURNEY #1
==================================================

Primary case:

Khoa học 5
Bài 1 — Thành phần và vai trò của đất
Intent: CHUẨN BỊ.

Dùng dữ liệu SGK thật hiện có.

Không hardcode teaching prose nếu source/core
đã cung cấp được.

Không hardcode navigation theo tên môn/bài.

Không viết riêng một Khoa học 5 engine.

==================================================
8. SECOND REUSE PROBE
==================================================

Sau khi Golden Journey #1 chạy hoàn chỉnh trên Nokia:

chạy probe nhỏ:

TOÁN 5
→ ÔN LẠI
→ entry từ evidence/review state
→ exercise thật.

Mục tiêu:

FALSIFY HARDCODING.

Đổi:

subject
+ intent
+ entry path.

Nếu phải thêm branch kiểu:

if Khoa học...
if Toán...
if prepare...
if review...

hãy coi đó là evidence abstraction hiện tại chưa đúng.

Fix ở mức nhỏ nhất hợp lý.

==================================================
9. DO NOT OVERGENERALIZE AFTER PROBE #2
==================================================

Probe #2 PASS không đồng nghĩa:

“bây giờ đủ evidence xây ExperiencePattern engine”.

Sau #2 chỉ đánh giá:

- behavior nào lặp lại;
- behavior nào khác theo Intent;
- behavior nào khác theo Activity;
- behavior nào khác theo Subject;
- abstraction hiện tại có gây friction không.

Nếu chưa cần engine:
KHÔNG xây.

==================================================
10. 38 CONCEPTS
==================================================

Trong khi implement,
quay lại 38 concepts để lấy interaction/visual ideas.

Không chỉ reuse architecture idea.

Founder muốn NHÌN THẤY product lineage từ concepts.

Đặc biệt xem lại các concept liên quan:

Home / Next Action
Tutor Start
Diagnostic
Problem Workspace
Hint
Your Turn
Success
Why This Method
Source
Review

và subject-specific concepts nếu phù hợp.

Không copy pixel-perfect.

Không mang lại:
XP,
streak,
ranking,
fake score,
answer-first,
wrong provenance.

==================================================
11. REAL DEVICE LOOP
==================================================

Implementation loop:

CODE
→ TEST / ANALYZE
→ NOKIA
→ USE AS GRADE-5 CHILD
→ OBSERVE
→ FIX
→ NOKIA AGAIN.

Unit tests không thay thế product verification.

==================================================
12. AUTONOMY
==================================================

Claude có full autonomy với reversible implementation
trong phạm vi Golden Journey:

- navigation;
- state passing;
- components;
- data binding;
- small refactors;
- Jira reconciliation;
- SAM behavior;
- reuse/removal của code ad hoc nếu cần.

Không hỏi Founder từng quyết định nhỏ.

STOP và hỏi Founder chỉ khi gặp:

- product-direction conflict thật sự;
- irreversible legal/commercial decision;
- destructive/shared-data action;
- major scope expansion;
- major cost.

==================================================
13. STOP CONDITION
==================================================

STOP khi:

Golden Journey #1 chạy end-to-end trên Nokia

VÀ

Probe #2 đã được thử đủ để biết
journey #1 có hardcode hay không.

Không tự mở rộng K-12 sau đó.

Không tự xây ExperiencePattern engine.

Không tự bắt đầu Camera Golden Journey.

==================================================
14. REPORT
==================================================

Khi STOP condition đạt:

viết ra Desktop:

`SAM-GOLDEN-JOURNEY-EXECUTION-REPORT.md`

Báo cáo ngắn:

WHAT FOUNDER CAN USE NOW

GOLDEN JOURNEY #1

NOKIA EVIDENCE

SAM BEHAVIOR ACTUALLY EXPERIENCED

CONTEXT / INTENT / EXPERIENCE FLOW

TRACE / EVIDENCE / CONTINUITY RESULT

SECOND PROBE RESULT

WHAT WAS REUSED

WHAT HAD TO CHANGE

38 CONCEPTS VISIBLY REUSED

WHAT WAS FALSIFIED

WHAT STILL FEELS WRONG

JIRA CHANGES

NEXT RECOMMENDATION

FOUNDER DECISIONS NEEDED.

Sau đó STOP.

Không tự bắt đầu phase tiếp theo.

==================================================

Mục tiêu vòng này không phải:

“đóng WAL”.

Mục tiêu là lần đầu tiên chứng minh:

HỌC CÙNG SAM
CÓ MỘT VÒNG HỌC HOÀN CHỈNH
TRÊN THIẾT BỊ THẬT.

ARCHITECTURE SERVES THE EXPERIENCE.
JIRA SERVES THE PRODUCT.
EVIDENCE SERVES THE TRUTH.
