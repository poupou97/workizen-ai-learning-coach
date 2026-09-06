# FOUNDER TASK ORDER
## ROUND 7 CLOSEOUT + REPOSITORY SOURCE-OF-RECORD + MERGE-DEBT RECONCILIATION

### FOUNDER VERDICT

Round 7 được ACCEPTED.

Kết luận nghiên cứu chính được chấp nhận:

CALIBRATION IS FINISHED.
THE NEXT BOTTLENECK IS RECOGNITION + ROLE DISAMBIGUATION.

Không mở thêm Round 8 calibration.
Không activate trusted threshold.
Không hạ evidence bar để lấy coverage.

Round 7 đã chứng minh đủ rằng threshold/calibration hiện không thể giải quyết teaching-critical error vì các failure mechanism chính không quan sát được bằng các signal hiện có.

Giữ nguyên:
- trusted = 0
- eligible for teaching = 0
- Golden SGK crops = INTERNAL / RESEARCH ONLY theo D4
- hardware = UNVERIFIED cho đến khi có device walk thật
- TECHNICALLY VALIDATED != HARDWARE VERIFIED != DISTRIBUTION RIGHT

==================================================
P0 — NEW STANDING GOVERNANCE RULE
REPOSITORY IS THE SOURCE OF RECORD
==================================================

Từ task này trở đi, áp dụng thành standing rule cho project.

## 1. Canonical source of record

Repository phù hợp là SOURCE OF RECORD lâu dài.

Mọi artefact có giá trị quyết định, kiến trúc, nghiên cứu hoặc cần truy vết phải được lưu trong repo và commit.

Bao gồm tối thiểu:

- Task Order / Master Task Order
- Research plan
- Research report
- Audit report
- Round report / consolidated report
- Founder Decision / Decision Record
- ADR
- RFC
- Architecture proposal
- Architecture assessment
- Technical proposal
- Product proposal ảnh hưởng implementation
- UX proposal ảnh hưởng implementation
- Acceptance criteria
- Measurement methodology
- Gate definition
- Threshold definition
- Evaluation methodology
- Important experiment result
- Final recommendation / verdict
- Manifest / provenance / reproduction instruction cần để hiểu hoặc tái tạo kết quả

Nếu một quyết định có khả năng ảnh hưởng implementation tương lai, nó không được chỉ tồn tại trong chat hoặc Desktop.

Nó phải có canonical document trong repo.

## 2. Desktop / external copies are REVIEW COPIES ONLY

Mọi file được export ra:

- ~/Desktop
- ZIP
- temporary folder
- scratchpad
- hoặc bất kỳ vị trí ngoài repo nào

chỉ được coi là:

TEMPORARY FOUNDER REVIEW COPY.

Không phải canonical archive.
Không phải source of record.
Không được là nơi duy nhất giữ một quyết định/tài liệu quan trọng.

Founder có thể xoá các bản này ngay sau khi review.

Do đó:

REPO = CANONICAL RECORD
DESKTOP / ZIP = REVIEW SNAPSHOT ONLY

Không xây quy trình phụ thuộc vào việc Desktop ZIP tồn tại lâu dài.

## 3. Correct previous archive semantics

Audit các tài liệu Round 4–7 đang gọi Desktop ZIP/per-round ZIP là:

- archive of record
- source of record
- canonical archive
- hoặc wording tương đương.

Sửa semantics thành:

Repository = canonical source of record.
ZIP/Desktop export = review snapshot / review copy.

Không rewrite lịch sử.
Không xoá hash cũ.
Không giả vờ archive loss chưa từng xảy ra.

Nếu cần, thêm governance clarification giải thích:

"Previous Desktop ZIPs were review snapshots. Repository documentation is the canonical project record under the Founder governance clarified on 2026-09-06."

## 4. Evidence exception — DO NOT blindly put everything into Git

Rule SOURCE OF RECORD không có nghĩa phải nhét mọi binary/evidence vào Git.

Không commit chỉ để thỏa rule:

- verbatim SGK pages
- SGK crops bị D4 hạn chế
- copyrighted/restricted material
- large datasets
- large generated binaries
- sensitive/private device evidence
- artefact không phù hợp với Git

Đối với evidence body không được/không nên lưu trong repo:

Repo phải giữ đủ metadata để hiểu evidence:

- manifest
- provenance
- SHA/hash nếu phù hợp
- source/status
- generation/reproduction instructions
- licensing/distribution classification
- relation tới report/decision
- lý do evidence body không nằm trong Git

Không biến restricted evidence thành public/distributable chỉ vì cần archive.

D4 vẫn có hiệu lực.

## 5. Round/task close rule

Từ nay không được tuyên bố một Round/Task CLOSED chỉ vì ZIP đã được build.

Close sequence chuẩn:

WORK COMPLETE
→ CANONICAL DOCS WRITTEN
→ DECISIONS RECORDED
→ ARCHITECTURE/RESEARCH CONCLUSIONS RECORDED
→ METHODOLOGY/GATES RECORDED
→ COMMIT TO REPO
→ VERIFY TRACEABILITY
→ OPTIONAL REVIEW ZIP
→ FOUNDER REVIEW
→ REVIEW COPY MAY BE DELETED

Review ZIP phải được tạo SAU canonicalization, không phải ngược lại.

Không được có:

Desktop ZIP → only source of truth.

==================================================
P0 — ROUND 4–7 CANONICAL RECORD AUDIT
==================================================

Audit Round 4, 5, 6, 7.

Mục tiêu không phải rebuild thêm ZIP.

Mục tiêu là chứng minh canonical knowledge cần giữ đã nằm trong repository.

Lập matrix:

ROUND
DOCUMENT / DECISION
CANONICAL REPO PATH
COMMIT
STATUS
REPRODUCIBLE?
EXTERNAL-EVIDENCE DEPENDENCY?
GAP?

Kiểm tra tối thiểu:

- consolidated reports
- research plans
- Task Orders nếu còn giá trị
- Founder decisions
- acceptance criteria
- methodology
- gates
- architecture conclusions
- measured results
- provenance
- reproduction instructions
- licensing classifications
- known limitations
- Round verdicts

Nếu Desktop copy biến mất nhưng canonical record vẫn đủ trong repo:

Không coi đó là project-record loss.

Nếu phát hiện thông tin quan trọng CHỈ tồn tại trong ZIP/Desktop/scratchpad:

Đó mới là GAP thật.

Canonicalize phần được phép canonicalize vào repo.

Restricted evidence không được copy vào Git; chỉ canonicalize metadata/provenance theo rule trên.

==================================================
P0 — MERGE-DEBT RECONCILIATION
==================================================

Hiện tại có khoảng:

- 20 open PR
- 4 stacked research rounds
- ~259 commits ahead of main

Không mở research round mới trên stack này.

Audit toàn bộ dependency/subsumption của Round 4–7.

Ưu tiên kiểm tra plan hiện tại:

merge #79
→ close #73 IF demonstrably subsumed
→ reconcile remaining PRs

Nhưng đây KHÔNG phải lệnh merge mù.

Claude phải xác minh:

- dependency
- superseded work
- duplicate work
- conflicting conclusions
- ordering requirements
- tests
- documentation dependencies
- research truth preservation

Không bulk merge chỉ để giảm PR count.

Không được làm mất:

- measured evidence
- negative findings
- FALSIFIED results
- PARTIAL results
- historical decisions
- provenance
- Round 4–7 conclusions

Đặc biệt:

NEVER TURN PARTIAL INTO DONE.

Allowed status semantics tiếp tục là:

DONE
PARTIAL
FAILED
FALSIFIED
BLOCKED
DEFERRED
NOT STARTED

==================================================
NEXT RESEARCH DIRECTION
==================================================

Sau khi baseline/merge debt được reconcile, bottleneck tiếp theo là:

RECOGNITION + ROLE DISAMBIGUATION

Không phải calibration.

Chuẩn bị research direction cho:

1. Digit recognition / digit corruption
2. OCR character corruption
3. Question vs non-question semantic-role classification
4. Structural/semantic role recognition
5. Failure cases mà dual-OCR character-exact agreement vẫn cùng sai
6. Signal mới có khả năng phát hiện lỗi mà threshold hiện tại không thấy
7. Population-real evaluation
8. Cross-engine disagreement / uncertainty nếu thực sự cung cấp signal mới
9. Evidence để phân biệt recognition failure với reasoning failure

Test design phải bao gồm population thật.

Không được chỉ test synthetic fixture có đúng premise của rule.

Standing principle:

ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION.

Ví dụ:

0/0 present

không được tự động PASS nếu expected population đáng lẽ > 0.

Gate phải kiểm cả expected population/existence obligation khi semantics yêu cầu.

==================================================
TITLE FIDELITY — FOUNDER DECISION
==================================================

108 multi-word ALL-CAPS titles:

PRESERVE SOURCE VERBATIM.

Không sentence-case nếu transformation có thể làm sai/mất proper noun.

Đây là fidelity fail-safe, không nhất thiết là UX cuối cùng.

Có thể nghiên cứu normalization sau, nhưng chỉ activate nếu chứng minh được proper-noun preservation trên population thật.

Correctness > typography cleanliness.

==================================================
DEVICE + LICENSING
==================================================

Nokia/device:

Không suy diễn hardware PASS từ composition/emulator/static evidence.

Nếu chưa có real-device walk:

HARDWARE UNVERIFIED.

Không can thiệp thiết bị khi đang được Founder sử dụng cá nhân.

SGK:

Page/crop SGK nguyên văn:

INTERNAL / RESEARCH ONLY
LICENSING-DISTRIBUTION BLOCKED

TECHNICALLY POSSIBLE != DISTRIBUTION RIGHT.

Không để technical PASS làm mất licensing classification.

==================================================
DELIVERABLES CỦA TASK NÀY
==================================================

Tất cả deliverables dưới đây PHẢI nằm trong repository và được commit:

1. Governance update:
   REPOSITORY-SOURCE-OF-RECORD.md
   hoặc tích hợp vào governance document canonical hiện có.

2. ROUND4-7-CANONICAL-RECORD-AUDIT.md

3. MERGE-DEBT-RECONCILIATION-PLAN.md

4. Nếu cần:
   update ARCHIVE-REGISTRY.md để phản ánh đúng semantics:
   registry = provenance/identity registry,
   không phải Desktop archive policy.

5. Update các docs đang gọi Desktop ZIP là archive/source of record.

6. NEXT-RESEARCH-DIRECTION.md
   chỉ ở mức research direction cho
   Recognition + Role Disambiguation.

Không triển khai Round 8.

Không activate threshold.

Không bắt đầu POC mới chỉ để giữ agent bận.

==================================================
AUTONOMY
==================================================

Claude có toàn quyền:

- audit repo
- sửa documentation
- tạo/cập nhật governance docs
- chạy tests/checks
- phân tích PR dependency
- đề xuất merge order
- canonicalize permitted documentation
- commit/push documentation và non-destructive governance work

Không cần Founder approval cho housekeeping/research documentation không thay đổi product behavior.

Founder gate chỉ khi thực sự cần cho:

- product decision mới
- legal/licensing decision
- distribution decision
- destructive operation
- secret/credential
- real-money action
- merge có conflict về product/research truth không thể tự giải quyết

==================================================
STOP CONDITION
==================================================

Task này kết thúc khi:

- repository-source-of-record rule đã canonical trong repo;
- Round 4–7 canonical record audit hoàn tất;
- archive wording đã được sửa;
- merge-debt reconciliation plan có evidence;
- next bottleneck được ghi là Recognition + Role Disambiguation;
- tất cả tài liệu trên đã commit/push;
- repo/worktree state được báo chính xác.

Sau đó STOP.

KHÔNG tự mở Round 8.
KHÔNG tiếp tục calibration.
KHÔNG tạo workstream mới chỉ vì còn thời gian.

Báo Founder:

DONE
GAPS
MERGE PLAN
CANONICAL RECORD STATUS
NEXT BOTTLENECK
FOUNDER GATES (nếu thực sự còn)
