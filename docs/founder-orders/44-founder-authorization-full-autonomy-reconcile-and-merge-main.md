# FOUNDER AUTHORIZATION — FULL AUTONOMY TO RECONCILE AND MERGE MAIN

Founder cấp toàn quyền cho Claude hoàn tất việc dọn merge debt Round 4–7 và MERGE vào `main`.

Không cần quay lại xin Founder approval cho từng PR hoặc final `round7 → main` PR.

Mục tiêu:

RECONCILE → VERIFY → PUSH → MERGE MAIN → CLEAN UP → REPORT.

Đừng biến việc này thành thêm một research round hoặc một quy trình phê duyệt phức tạp.

## AUTHORITY

Claude được toàn quyền:

- audit dependency / ancestry / containment;
- rebase / merge / compose integration branches khi cần;
- resolve merge conflicts;
- sửa documentation inconsistency;
- canonicalize tài liệu theo rule Repository Source of Record;
- chạy tests / static checks / verification;
- commit;
- push;
- mở/cập nhật/đóng PR;
- merge PR;
- merge integration composition vào `main`;
- đóng các PR đã subsumed;
- cập nhật branch sau merge;
- dọn merge debt và bookkeeping.

Không cần Founder approval thêm cho các thao tác Git/repo nói trên.

## CURRENT MERGE MODEL

Không tiếp tục coi 20 PR là 20 đơn vị độc lập.

Containment audit hiện cho thấy:

- 15/20 PR đã nằm trong Round 7: #73 #79 #80–#88 #90–#93
- phần chưa được hấp thụ: #89 #94 #95 #96 #97
- #97 ⊂ #95

Vì vậy ưu tiên reconcile theo mô hình bốn đơn vị thực:

#94 → #95 (sau ancestry proof có thể close #97 as subsumed) → #96 → residual #89
→ compose/reconcile Round 7 → merge vào main.

Đây là working plan, không phải thứ tự mù.
Nếu repository truth cho thấy thứ tự khác an toàn hơn, Claude được tự điều chỉnh và thực hiện.

## IMPORTANT: DO NOT MERGE #79 ALONE JUST BECAUSE AN OLD PLAN SAID SO

Audit mới đã chứng minh #79 riêng lẻ không phải integration boundary tốt:

- nó chỉ giao tầng Round 4/5;
- để lại phần lớn stacked debt;
- một số report trên nó tham chiếu code chưa có trong chính #79.

Dùng current repository truth, không dùng doctrine đã hết hạn.

## MERGE SAFETY RULE

Mục tiêu là đưa repository về một `main` coherent.

Không được làm mất hoặc rewrite research truth.

Đặc biệt phải giữ nguyên semantics của:

DONE / PARTIAL / FAILED / FALSIFIED / BLOCKED / DEFERRED / NOT STARTED
HARDWARE UNVERIFIED / LICENSING-DISTRIBUTION BLOCKED

Không biến:

PARTIAL → DONE
UNVERIFIED → VERIFIED
research result → production result
technical validation → distribution right

chỉ vì code đã được merge.

## ROUND 5

Round 5 không có Founder acceptance chính thức.

Không retroactively ghi "Round 5 Founder Accepted" chỉ vì code của Round 5 cuối cùng được merge vào main.

Giữ historical truth: 8 PASS · 1 PARTIAL · 1 FAIL

và ghi merge hiện tại là integration/governance action, không phải retroactive research acceptance.

## GOLDEN CI LIMITATION

`timeline_history_test.dart` hiện có path:

markTestSkipped('fixture thật chưa sinh trên máy này')

Fixture thật bị gitignore/D4 nên CI không thể dùng nó.

Do đó: CI GREEN != GOLDEN CHAIN VERIFIED.

Không cần đưa SGK fixture vào Git để làm CI xanh.

Nhưng phải đảm bảo documentation/test reporting không tạo false-green claim.

Nếu fixture vắng mặt: Golden verification phải được mô tả rõ là SKIPPED / UNVERIFIED, không phải PASS.

Standing principle: ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION.

## D4 / RESTRICTED MATERIAL

Không commit:

- verbatim SGK pages;
- SGK crops;
- copyrighted/restricted corpus;
- D4 evidence body;
- large restricted derived corpus

chỉ để làm merge hoặc CI hoàn chỉnh.

Repo giữ canonical: reports; decisions; methodology; manifests; provenance; hashes khi phù hợp;
reproduction instructions; licensing classification.

Restricted evidence vẫn ở ngoài Git.

## REPOSITORY SOURCE OF RECORD

Tiếp tục hoàn thành governance task đang chạy:

REPOSITORY = CANONICAL SOURCE OF RECORD.
Desktop/ZIP/scratchpad = temporary review/evidence workspace only.

Task Orders, reports, Founder decisions, architecture proposals, research conclusions,
acceptance criteria và methodology phải được canonicalize vào repo.

Không cần giữ Desktop ZIP sau Founder review.

## TEST / VERIFY

Trước final merge vào main:

- verify ancestry/containment;
- verify no unintended deletion of research docs;
- run appropriate automated tests;
- run static/analyze checks phù hợp;
- identify skipped/unverifiable tests honestly;
- verify D4 material không bị staged/tracked;
- verify canonical docs cần thiết đã nằm trong repo;
- verify final diff/main composition coherent.

Không cần đạt một "perfect evidence state" giả tạo để merge.

Known limitations được phép tồn tại nếu được ghi đúng trạng thái.

## MAIN MERGE AUTHORIZED

Sau khi Claude đánh giá composition đủ an toàn: MERGE VÀO `main`.

Không dừng lại để hỏi Founder: "May I merge?" / "Should I proceed?" / "Approve final PR?"

Founder đã approve trong Task Order này.

Push `main`/merge PR theo workflow repo hiện tại.

## AFTER MERGE

1. Verify `main` HEAD.
2. Verify repo clean.
3. Verify relevant CI/result.
4. Close PRs đã demonstrably subsumed/merged.
5. Không xoá branch nếu việc giữ branch có giá trị provenance; không cần aggressive cleanup.
6. Update canonical merge/research documentation nếu cần.
7. Báo chính xác những test/evidence vẫn SKIPPED / UNVERIFIED / BLOCKED.

## NEXT BOTTLENECK

Sau khi merge debt được xử lý: Recognition + Role Disambiguation vẫn là bottleneck nghiên cứu tiếp theo.

Nhưng KHÔNG tự mở Round 8 trong task này.

Task này là: CANONICALIZE + RECONCILE + MERGE MAIN. Không phải một research round mới.

## FOUNDER GATES CÒN LẠI

Không có Founder gate cho Git merge trong task này.

Chỉ dừng nếu gặp hành động thực sự ngoài quyền repo như:

- chi tiền thật;
- secret/credential cần Founder nhập;
- legal/licensing approval;
- store-console/public distribution;
- destructive operation không thể phục hồi;
- thay đổi product direction lớn ngoài scope Round 4–7.

Nếu không thuộc các loại trên, Claude tự quyết và tiếp tục.

## STOP CONDITION

Chỉ STOP khi:

- canonical-record audit hoàn tất;
- governance docs canonical;
- merge debt Round 4–7 đã reconcile;
- appropriate PRs đã merge/close;
- final composition đã MERGE INTO MAIN;
- main đã verify;
- không có unintended D4 material trong Git;
- trạng thái research/evidence vẫn trung thực;
- repo state sạch hoặc mọi residual được giải thích.

Sau đó báo Founder ngắn gọn:

MERGED / MAIN HEAD / PRs CLOSED / REMAINING / TESTS / SKIPPED / UNVERIFIED /
CANONICAL RECORD STATUS / REMAINING REAL BLOCKERS / NEXT BOTTLENECK

Không xin thêm approval sau khi các điều kiện trên đã đạt.
