# FOUNDER TASK — JIRA RECONCILIATION + NEXT WORK SELECTION

Claude được toàn quyền tiếp tục Học cùng SAM.

Repository `main` hiện đã reconcile Round 4–7.
Không cần audit lại merge vừa hoàn tất.

## Mục tiêu

Trước khi mở Round 8 hoặc tạo thêm research work:

ĐỐI CHIẾU JIRA WAL VỚI REPOSITORY TRUTH.

Repo là canonical source of record.
Jira là execution/project tracking layer và phải phản ánh đúng trạng thái repo.

## P0 — AUDIT JIRA WAL

Đọc toàn bộ Jira project WAL và đối chiếu với:

- current `main`;
- canonical Task Orders;
- Founder Decisions;
- Round 4–7 reports;
- research conclusions;
- architecture/research proposals;
- merged PR history;
- current product/research blockers.

Phân loại các Jira issue:

1. DONE thực sự
2. DONE nhưng Jira chưa cập nhật
3. IN PROGRESS nhưng work thực tế đã hoàn tất
4. TODO / READY vẫn còn hợp lệ
5. SUPERSEDED bởi work/decision mới hơn
6. DUPLICATE
7. BLOCKED
8. Issue mô tả không còn đúng với architecture/research truth hiện tại
9. Work đã xuất hiện trong repo nhưng chưa có Jira issue phù hợp

Không được suy ra DONE chỉ từ title hoặc commit message.
Dùng repository evidence.

## P0 — RECONCILE

Claude được toàn quyền:

- update Jira status;
- sửa description/acceptance criteria;
- link evidence/PR/docs;
- close duplicate/superseded issue;
- tạo issue mới khi phát hiện work thật chưa được tracking;
- cập nhật Epic;
- sắp lại priority/backlog.

Không cần Founder approval cho Jira housekeeping.

KHÔNG tạo hàng loạt issue chỉ để làm board đẹp.

## P0 — NEXT BOTTLENECK

Research truth hiện tại:

CALIBRATION IS NOT THE BOTTLENECK.

Next bottleneck:

RECOGNITION + ROLE DISAMBIGUATION.

Hai failure mechanisms đã đo:

1. digit / character corruption;
2. non-question content being served as a question.

Dual-OCR exact agreement cũng không đủ làm trust signal.

Do đó:

- không mở thêm calibration work;
- không hạ trust threshold;
- không activate `trusted`;
- không dùng coverage increase làm mục tiêu thay cho correctness.

Kiểm tra Jira xem các vấn đề này đã được tracking chưa.

Nếu chưa: tạo Epic/workstream phù hợp.
Nếu đã có: reuse/update issue hiện tại, không duplicate.

## PRODUCT TRUTH PHẢI GIỮ

Hiện tại:

- trusted = 0
- eligible for teaching = 0
- R-1 = HARDWARE UNVERIFIED
- SGK crops = LICENSING-DISTRIBUTION BLOCKED / D4
- Round 5 = 8 PASS · 1 PARTIAL · 1 FAIL, không có Founder acceptance hồi tố
- merge Round 4–7 là governance/integration delivery, không phải product delivery
- CI GREEN != GOLDEN CHAIN VERIFIED khi real fixture vắng mặt

Không được Jira cleanup làm mất các trạng thái này.

## NEXT WORK SELECTION

Sau reconciliation:

Tự chọn 3–5 issue có giá trị cao nhất tiếp theo.

Ưu tiên theo thứ tự:

P0 — Recognition + Role Disambiguation
P0 — blocker trực tiếp ngăn trusted content tới learner
P1 — verification gap có nguy cơ false-green
P1 — product UX/device validation nếu nó unblock product truth
P2 — optimization/polish

Không tự động coi "Round 8" là mục tiêu.

Round chỉ là execution container.
Bottleneck/product outcome mới là mục tiêu.

Nếu backlog hiện tại đã có issue phù hợp: dùng issue đó.
Nếu cần tạo Epic mới: tạo Epic + child issues vừa đủ để chạy.

## REPOSITORY GOVERNANCE

Mọi Task Order, audit report, research report, Founder Decision, architecture proposal,
research proposal, acceptance criteria quan trọng phải canonicalize trong repo.

Desktop/export chỉ là Founder review copy và có thể bị xoá.

## AUTONOMY

Claude được toàn quyền:

Jira audit → Jira reconciliation → chọn next work → implement/research → test → commit → push → PR → merge main

Không cần Founder approval cho Git/Jira operations thông thường.

Chỉ dừng cho Founder nếu gặp:

- legal/licensing decision;
- real-money action;
- secret/credential;
- store/public distribution;
- destructive irreversible action;
- product-direction decision lớn chưa có Founder decision.

## BÁO CÁO ĐẦU TIÊN

TRƯỚC KHI bắt đầu work mới, báo ngắn:

JIRA BEFORE
JIRA RECONCILED
DONE / SUPERSEDED / REMAINING
TOP 5 NEXT ISSUES
ISSUE CLAUDE CHỌN CHẠY TIẾP
WHY

Sau đó không cần chờ Founder nếu không có Founder gate.

Tiếp tục chạy issue đã chọn.

Mọi báo cáo/kết luận cuối phải lưu trong repo.
