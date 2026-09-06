# FOUNDER AUTONOMOUS RUN — HỌC CÙNG SAM
## ROOT CAUSE → FIX → TRUSTED SLICE

Founder sẽ offline. KÍCH HOẠT AUTONOMOUS EXECUTION NGAY.

Không chờ Founder giữa các bước kỹ thuật. Không dừng chỉ để báo cáo.
Repository là canonical source of record. Jira phải phản ánh execution truth.

Current baseline: main = 6fd728d · CI success · 0 PR open · WAL-213 DONE · E24 = WAL-211 ·
WAL-214/215 Ready · WAL-216/217 Ideas · WAL-218 Ready · trusted = 0 ·
eligible for teaching = 0 · toanExercises shipped = 0

WAL-213 đã tạo evidence rằng giả thuyết "recognition là bottleneck" có thể sai.
Không chạy WAL-214 theo thiết kế cũ một cách máy móc.

## MISSION

FIND ROOT CAUSE → FIX SMALLEST UPSTREAM CAUSE → PROVE IT →
ATTEMPT ONE NARROW TRUSTED LEARNING SLICE → nếu đủ evidence, nối nó gần nhất có thể tới learner.

Không hạ evidence bar để tạo PASS.
Nếu scope không đạt trust: SHRINK SCOPE, NOT THE BAR.

## PHASE A — BOUNDED ROOT-CAUSE AUDIT

Trên đúng 12 teaching-critical errors hiện có, truy nguyên từng case:
source → geometry → SDM block → recognition → repair → role → serving.

Classify root cause:
1. BLOCK BOUNDARY / SEGMENTATION
2. CHARACTER / DIGIT RECOGNITION
3. ROLE DISAMBIGUATION
4. COMPOSITION / GROUPING
5. PIPELINE ORDERING
6. UNKNOWN

Không suy luận root cause chỉ từ final output.

Xác minh độc lập các findings WAL-213:
- 13/17 recovery failures do token contamination / bad boundary;
- numerator/denominator split;
- recognizer đủ scale ở recoverable cases;
- recovered observation supersession contract hoạt động;
- block-level Δ0 là thật.

Dùng measurement thực tế. Không dựa vào comments/docs nếu code/data contradict.

## PHASE B — AUTO DECISION

Claude tự quyết sau audit.

IF segmentation/geometry dominant → reframe WAL-214 nếu cần → implement smallest SDM
segmentation/boundary fix.
IF recognition dominant → execute WAL-214.
IF role dominant → execute WAL-215.
IF pipeline ordering / answer-label timing là root cause đáng kể → nâng WAL-216 lên P0 và fix.
IF mixed → chọn smallest UPSTREAM intervention có khả năng loại nhiều teaching-critical errors nhất.

Không cần Founder approval cho lựa chọn engineering này.
Update Jira trước/sau execution để ticket phản ánh đúng truth.

## PHASE C — VERIFY THE FIX

Không chấp nhận: "tests green therefore solved".
Phải đo lại đúng population trước/sau.

Report ít nhất: teaching-critical errors BEFORE/AFTER · segmentation BEFORE/AFTER ·
recognition BEFORE/AFTER · role BEFORE/AFTER · unknown BEFORE/AFTER.

Không double-count một root cause qua nhiều category nếu causal chain đã xác định upstream cause.
Mutation/adversarial check nếu phù hợp.
Nếu fix không cải thiện: FALSIFY nó và move on. Không polish một hypothesis đã fail.

## PHASE D — WAL-215 / WAL-216

Sau upstream fix: re-evaluate WAL-215 và WAL-216. Chỉ chạy work còn có giá trị sau evidence mới.

Question-vs-non-question vẫn là P0 nếu còn giải thích teaching-critical errors.
Pipeline-ordering fix WAL-216 được ưu tiên nếu evidence cho thấy agreement chạy trước khi
answer identity được recover.

Không giữ ticket P0 chỉ vì Founder từng xếp P0 nếu premise của nó đã bị evidence mới falsify.

## PHASE E — WAL-218

Fix CI false-green. 9 tests không được âm thầm skip trong khi CI tạo impression rằng
Golden Chain đã VERIFIED.

KHÔNG commit SGK/D4 real fixture để làm CI xanh.

Thiết kế verification sao cho: fixture absent → explicit UNVERIFIED / SKIPPED semantics,
và CI/report không được biến nó thành verified PASS.

Nếu có thể tạo synthetic/corpus-free equivalent để pin invariant: làm.
Nhưng synthetic PASS != real Golden verification.

## PHASE F — NARROW TRUSTED SLICE

Đây là PRODUCT NORTH STAR của autonomous run.

Sau các fix cần thiết: tìm smallest real learning slice có khả năng đi end-to-end.

Ưu tiên: 1 grade × 1 subject × 1 lesson/content type × smallest useful learner experience.
Không cần breadth.

Mục tiêu: SOURCE → STRUCTURE → RECOGNITION → ROLE → VALIDATION → TRUST → LEARNER-SERVABLE ARTIFACT.

Nếu một lesson quá rộng: thu nhỏ content type.
Nếu một subject quá khó: chọn class có evidence tốt nhất.

Không cherry-pick bằng cách biết trước answer rồi điều chỉnh threshold.
Selection rule phải được ghi TRƯỚC final evaluation nếu việc lựa chọn có thể bias kết quả.

## RESEARCH STOP CONDITION

Nếu sau iteration này vẫn trusted = 0 hoặc eligible for teaching = 0 hoặc không tạo được
learner-servable trusted slice, THÌ STOP mở research direction mới.
Không Round 8 chỉ để tiếp tục nghiên cứu.

Thay vào đó tạo NARROW-SLICE-BLOCKER-REPORT với: smallest attempted slice · exact blocker ·
minimum missing capability · evidence · smallest next implementation required.

Sau đó chỉ được tiếp tục nếu work tiếp theo trực tiếp unblock slice đó.

## DEVICE

Không sử dụng Nokia nếu Founder đang dùng máy / không available. Không giả hardware PASS.
Nếu không có device: TECHNICALLY VALIDATED / HARDWARE UNVERIFIED.
Không để thiếu hardware chặn engineering/research có thể làm offline.

## D4 / LEGAL

SGK pages/crops: INTERNAL / RESEARCH ONLY. Không commit D4-restricted evidence vào Git.
Không thay đổi licensing/distribution status. Không public/distribute copyrighted SGK material.

## WAL-196 / FOUNDER DECISIONS

KHÔNG tự ratify D-135, D-136, D-137, D-138.
KHÔNG activate trust threshold. KHÔNG quyết licensing WAL-43.

Thay vào đó chuẩn bị FOUNDER-DECISION-PACK.md. Mỗi decision:
QUESTION · CURRENT EVIDENCE · OPTIONS · CLAUDE RECOMMENDATION · CONSEQUENCE IF DEFERRED.

Founder decision không được trở thành lý do để agent ngồi idle: chạy mọi work độc lập trước.

## AUTONOMY

FULL AUTONOMY cho: repository inspection · bounded research · implementation · refactor ·
tests · measurement · mutation tests · Jira updates · documentation · commit · push · PR ·
CI · merge main · close/reopen/reframe Jira issue theo evidence · tạo child issue nếu thật sự
cần · Confluence reconciliation · tiếp tục issue kế tiếp theo decision rules trên.

Có thể merge PR vào main khi CI green, evidence đủ, không vi phạm Founder gates,
status semantics truthful. Không giữ PR chờ Founder review chỉ vì ceremony.

## FOUNDER GATES — PHẢI DỪNG

legal/licensing · trust threshold activation · D-135…D-138 ratification ·
public/store distribution · money · secrets/credentials · destructive irreversible action ·
major product-direction decision không thể suy ra từ Founder decisions.

Không ping Founder cho housekeeping.

## SOURCE OF RECORD

Mọi Task Order, research result, audit, measurement methodology, architecture proposal,
decision request, final report phải canonicalize trong repo và commit.
Desktop/ZIP chỉ review copy, không phải archive.

## FINAL STATE WHEN FOUNDER RETURNS

Để lại một báo cáo duy nhất: AUTONOMOUS-RUN-RESULT.md

1. START STATE · 2. ROOT CAUSE OF 12 ERRORS · 3. WHAT WAS FIXED · 4. BEFORE → AFTER ·
5. WAL ISSUES COMPLETED / REFRAMED · 6. TRUSTED SLICE RESULT · 7. WHAT A CHILD CAN USE NOW ·
8. CI / DEVICE / D4 STATUS · 9. REMAINING TRUE BLOCKERS · 10. FOUNDER DECISIONS REQUIRED ·
11. NEXT SINGLE BEST ACTION

Nếu child-delivery vẫn = 0: nói thẳng = 0.
Không dùng số commit/test/issue để thay thế product outcome.

BẮT ĐẦU NGAY. Không chờ Founder sau Phase A.
