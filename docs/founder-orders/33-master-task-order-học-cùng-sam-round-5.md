MASTER TASK ORDER — HỌC CÙNG SAM — ROUND 5
DATA ACCURACY: REPAIR → VALIDATE → RESTORE

Founder ACCEPT Round 4.

Tiếp tục autonomous development với mô hình hiện tại:

A. PROVE
B. EXPERIENCE
C. DISCOVER
D. LEGACY REPROCESS

Nhưng PRIORITY #1 của Round 5 là:

TĂNG ĐỘ CHÍNH XÁC VÀ ĐỘ TIN CẬY CỦA DỮ LIỆU.

Không giải bài toán bằng cách chỉ WITHHOLD thêm.

==================================================
1. NORTH STAR ROUND 5
==================================================

Round 4 chứng minh:

OLD legacy false trust:
0.727

tc2-p2:
0.297

Teaching-critical:
0.722 → 0.176

Đây là tiến bộ lớn nhưng CHƯA ĐỦ TỐT để dạy trẻ.

Đồng thời coverage giảm:

0.683 → 0.551

Founder không chấp nhận chiến lược dài hạn:

SAI
→ WITHHOLD
→ DONE.

Target phải là:

SAI
→ DETECT
→ WITHHOLD
→ REPAIR
→ VALIDATE
→ RESTORE.

Mục tiêu:

WRONG SERVED ↓↓↓
CORRECT SERVED ↑
TRUST ↑
COVERAGE phục hồi ↑

Không đánh đổi accuracy để lấy coverage.
Không đánh đổi coverage vô hạn để lấy accuracy.

==================================================
2. BUILD DATA ACCURACY WORKSTREAM
==================================================

Tập trung nghiên cứu và triển khai bounded improvements cho:

1. OCR/text fidelity
2. Vietnamese diacritics
3. formula / number / unit fidelity
4. reading order
5. multi-column layout
6. role classification
7. lesson identity
8. lesson attachment
9. figure / caption relations
10. table structure
11. source attribution
12. provenance

Mỗi failure class phải có:

DETECT
→ REPAIR candidate
→ VALIDATE
→ RESTORE or WITHHOLD.

Không được repair rồi mặc định TRUSTED.

==================================================
3. THIRD-SIGNAL ARCHITECTURE
==================================================

Round 4 falsified:

OCR_A == OCR_B
therefore
TEXT == TRUE.

Hai OCR stack có thể cùng sai.

Xây/research Third Signal layer.

Ưu tiên theo thứ tự:

A. Vietnamese lexical / orthographic signal
B. source/layout/context constraints
C. deterministic number/unit/formula checks
D. cross-page / heading / TOC consistency
E. independent human review for high-risk/disagreement
F. third OCR/parser stack only where evidence shows benefit

Không thêm OCR engine chỉ vì “nhiều model hơn”.

Đo contribution của từng signal.

Ví dụ:

OCR A
+
OCR B
+
Vietnamese lexicon
+
layout/source context
→ candidate text
→ confidence/evidence
→ validate
→ trusted / repaired / withheld.

Mọi automatic repair phải lưu:

- original observations;
- repaired value;
- repair rule;
- supporting signals;
- provenance;
- confidence;
- validation result.

Không overwrite source observation.

==================================================
4. VIETNAMESE TEXT ACCURACY
==================================================

P0 research + POC:

tìm cách phát hiện/sửa các lỗi kiểu:

“Tiền hành”
vs
“Tiến hành”

và các lỗi dấu/nguyên âm mà hai OCR cùng mắc.

Nghiên cứu bounded:
- Vietnamese dictionary/lexicon;
- syllable validity;
- word frequency;
- contextual constraints;
- deterministic spelling candidates;
- language-model assistance ONLY as suggestion, never truth.

Nếu dùng LLM:
LLM output = RepairCandidate

KHÔNG:
LLM output = TrustedText.

Trusted repair phải được xác nhận bằng independent signal/source.

Đo:

precision of repair
recall
false correction rate.

False correction đặc biệt quan trọng.

==================================================
5. MATH / FORMULA / NUMBER ACCURACY
==================================================

Toán vẫn là high-risk.

Không reconstruct biểu thức từ OCR prose một cách suy đoán.

Research/POC riêng:

- formula region detection;
- image-region preservation;
- math OCR/parser candidates;
- digit/fraction/operator verification;
- unit consistency;
- bounding-box/source comparison.

Nếu chưa xác minh:
WITHHOLD formula region.

Nhưng tiếp tục nghiên cứu cách RESTORE nó an toàn.

Target:

formula withheld
→ specialized extraction
→ deterministic validation
→ restored structured formula.

Không:
formula withheld forever.

==================================================
6. LAYOUT / READING ORDER
==================================================

Round 4 đã cải thiện reading order mạnh.

Tiếp tục đặc biệt với:
- two-column;
- sidebar;
- activity box;
- caption;
- callout;
- page continuation;
- lesson starting mid-page;
- book-end/back-cover detection.

14 pipeline defects của Round 4 phải trở thành regression corpus.

Đặc biệt giữ test cho:
- “Giá:” không được kết thúc book;
- “Website:” không được làm mất phần còn lại;
- chapter labels không được hallucinate;
- year trong History title không được cắt;
- attachment phải reversible/recoverable.

==================================================
7. ROLE DEFINITION — P0
==================================================

Round 4 cho thấy role disagreement là vấn đề định nghĩa.

Viết:

ROLE DEFINITION SPEC v1

cho tối thiểu:

HEADING
BODY
QUESTION
OPTION
ANSWER
CAPTION
SIDEBAR
TABLE
FORMULA
FIGURE
FIGURE_TEXT
FOOTNOTE
ATTRIBUTION
OBJECTIVE
ACTIVITY
RULE
SPEECH_BUBBLE
RUNNING_HEAD
PAGENUM
UNKNOWN

Mỗi role phải có:

- semantic definition;
- inclusion criteria;
- exclusion criteria;
- positive examples;
- confusing counterexamples;
- relationship rules;
- teaching consequence;
- default trust consequence.

Sau đó:

re-annotate bounded disagreement sample.

Đo lại inter-annotator agreement.

Không train/tune role classifier trước khi taxonomy đủ rõ.

==================================================
8. TRUST GATE RESEARCH
==================================================

Chưa tự tạo production release threshold.

Nhưng Claude phải xây infrastructure để Founder có thể quyết định.

Tạo candidate:

THRESHOLDS.example.json

KHÔNG phải production THRESHOLDS.json.

Nó phải cho phép mô phỏng:

“Nếu threshold X thì:
- wrong served?
- correct served?
- coverage?
- teaching-critical?
- withheld?
- restored?”

Chạy sensitivity analysis.

Founder cần thấy trade-off curve,
không chỉ một con số.

Không tự chọn điểm trên curve làm production gate.

==================================================
9. LEGACY REPROCESS — BATCH 2+
==================================================

Tiếp tục cứu legacy data.

Không mass-run toàn corpus.

Chọn representative batches dựa trên failure classes:

- Math/high formula;
- two-column;
- Vietnamese text;
- Science;
- History/Geography.

Mỗi batch:

ORIGINAL
→ OLD
→ NEW
→ REPAIRED
→ INDEPENDENT AUDIT.

Báo:

OLD false trust
NEW false trust

OLD teaching-critical
NEW teaching-critical

OLD correct served
NEW correct served

OLD wrong served
NEW wrong served

WITHHELD
RESTORED
FALSELY WITHHELD.

Đặc biệt thêm metric:

RESTORE PRECISION

= số block restore đúng /
  tổng số block được restore.

Không được tăng coverage bằng restore thiếu precision.

==================================================
10. GOLDEN SLICE #1 — BÀI 17
==================================================

Giữ tc2-p1 hiện tại cho product prototype nếu cần,
với trust marking trung thực.

CHƯA adopt tc2-p2 nếu nó làm hỏng vertical slice.

Nhưng dùng tc2-p2 làm research baseline.

Mục tiêu Round 5:

tìm cách lấy những block đúng bị p2 withhold
→ repair/validate
→ restore

để cuối cùng tạo candidate tốt hơn cả p1 và p2:

tc2-p3 candidate.

Desired:

accuracy >= p2
coverage > p2

Không được đạt coverage bằng nới guard.

Tiếp tục nâng real Pedagogy Runtime khi có evidence thật.

Không fake validator.

==================================================
11. GOLDEN SLICE #2 — HISTORY
==================================================

Approve bounded continuation:

LS&ĐL 5 — Bài 8.

Approve research/bounded implementation của:

prose-dated-events-v1
story-attribution-v1

nhưng giữ trạng thái PROPOSED/bounded.

Không coi là universal K–12 rule.

History phải tiếp tục falsify:

- document model;
- TimelineSemantic;
- source attribution;
- lesson identity;
- deterministic validator;
- tutor abstraction.

Không copy Science-specific assumptions.

==================================================
12. UI/UX CONTINUES IN PARALLEL
==================================================

Không dừng Lane B để chờ data.

Current EF ~80–85%.

Tiếp tục:
- Home;
- Bookshelf;
- Chapter;
- Smart Book;
- Visual;
- SAM Tutor;
- Next Action;
- source/trust explanation.

Trực quan hiện vẫn chưa đạt concept board.

Cho phép tiếp tục cải thiện Visual Learning
bằng typed/source-grounded structures.

Không unconstrained LLM-generated visual truth.

Tiếp tục Nokia device loop.

Nếu integrated build khác byte ở app surface:
phải walk lại integrated build.

==================================================
13. REBUILD PACKS
==================================================

APPROVE rebuild packs vì provenance hiện tại đã stale.

Nhưng trước khi rebuild:

snapshot:
- old pack;
- manifest;
- hash;
- pipeline version;
- baseline metrics.

Sau rebuild:

OLD baseline vẫn phải reproducible.

Không overwrite historical baseline.

Verify phải PASS với provenance mới.

Nếu content delta lớn:
audit representative delta trước khi coi pack usable.

==================================================
14. DATA VERSIONING
==================================================

Mọi dữ liệu phải phân biệt rõ:

ORIGINAL OBSERVATION
REPAIRED CANDIDATE
VALIDATED REPAIR
TRUSTED
WITHHELD
LEGACY
SUPERSEDED.

Không overwrite truth history.

Mỗi repair cần trace được:

source
→ observation
→ failure
→ repair
→ validation
→ final disposition.

==================================================
15. ROUND 5 METRICS
==================================================

Giữ FIVE PRODUCT SCORES:

1 Experience Fidelity
2 Source Reality
3 Source Trust
4 Pedagogy Reality
5 Evidence Reality

Giữ LEGACY REPROCESS SCOREBOARD.

Thêm DATA ACCURACY SCOREBOARD:

- false trust;
- teaching-critical error;
- display fidelity error;
- reading-order error;
- role error;
- attachment error;
- formula/number/unit error;
- correct served;
- wrong served;
- withheld;
- false withheld;
- restored;
- restore precision;
- coverage.

Báo BEFORE → AFTER.

Không average thành một score.

==================================================
16. SUCCESS CRITERIA
==================================================

Round 5 thành công nếu chứng minh được:

1. ít nhất một major failure class được REPAIR,
   không chỉ WITHHOLD;

2. restored blocks có independent validation;

3. wrong served tiếp tục giảm;

4. correct served/coverage bắt đầu phục hồi;

5. role taxonomy rõ hơn và agreement tăng;

6. third signal chứng minh có hoặc không có giá trị bằng measurement;

7. Bài 17 vẫn usable và thật hơn;

8. History tiếp tục falsify architecture;

9. UI/UX tiếp tục tiến bộ trên máy thật;

10. không có trust claim nào được tạo chỉ để đẹp metric.

==================================================
17. GOVERNANCE
==================================================

Claude được autonomous trên:
- research;
- pipeline repair;
- bounded reprocess;
- tests;
- UI/UX;
- device validation;
- architecture research;
- PR creation;
- documentation.

Không direct main.
Không tự merge.

Không tự:
- đặt production trust threshold;
- mass reprocess toàn corpus;
- public SGK distribution;
- unrestricted LLM;
- major architecture fork;
- destructive migration.

Nếu một lane bị block:
tiếp tục lane khác.

Mọi PR cuối cùng:
READY FOR FOUNDER REVIEW.

==================================================
18. FOUNDER CHECKPOINT
==================================================

Round 5 report phải trả lời ngắn gọn:

1. DATA CHÍNH XÁC HƠN BAO NHIÊU?
2. LỖI NÀO ĐÃ ĐƯỢC SỬA THẬT,
   thay vì chỉ withhold?
3. BAO NHIÊU NỘI DUNG ĐÚNG ĐÃ ĐƯỢC RESTORE?
4. WRONG SERVED giảm bao nhiêu?
5. CORRECT SERVED tăng bao nhiêu?
6. THIRD SIGNAL nào thực sự có ích?
7. Legacy data có tiến gần teaching-ready không?
8. Bài 17 thật hơn ở đâu?
9. History đã phá/chứng minh gì?
10. Trẻ nhìn thấy sản phẩm tốt hơn ở đâu?

Kèm:
- Five Product Scores
- Data Accuracy Scoreboard
- Legacy Reprocess Scoreboard
- Golden #1 / #2 status
- Device evidence
- PR list
- Open P0
- next bottleneck.

Không merge.

START ROUND 5 AUTONOMOUSLY NOW.
