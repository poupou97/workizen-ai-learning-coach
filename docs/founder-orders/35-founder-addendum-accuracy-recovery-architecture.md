FOUNDER ADDENDUM — ACCURACY RECOVERY ARCHITECTURE

Founder bổ sung định hướng cho Round 5.

Không đặt mục tiêu tìm một OCR engine “hoàn hảo”.

Khi OCR/parser không đủ chắc chắn, Học cùng SAM cần có nhiều
con đường độc lập để DETECT → VERIFY → REPAIR → RESTORE.

==================================================
1. ACCURACY RECOVERY PIPELINE
==================================================

Thiết kế/audit theo mô hình:

SOURCE
→ OCR / Parser observations
→ deterministic validation
→ specialized domain validation
→ cross-corpus consistency
→ LLM semantic review
→ external authoritative verification when appropriate
→ human/user correction when necessary
→ validated correction
→ versioned Trusted Corpus.

Không phải mọi block đều phải chạy qua mọi tầng.

Router phải chọn verification path theo:
- content type;
- risk;
- disagreement;
- confidence;
- teaching consequence.

==================================================
2. LLM / CLAUDE AS VERIFIER
==================================================

Cho phép nghiên cứu LLM như một SECONDARY VERIFICATION SIGNAL.

Ví dụ:
OCR:
`c = 3×10° m/s`

Context:
Vật lý · vận tốc ánh sáng.

LLM có thể phát hiện:
expression có khả năng sai và đề xuất `3×10⁸ m/s`.

NHƯNG:

LLM OUTPUT != TRUTH.

LLM chỉ được tạo:
CorrectionCandidate
hoặc
AnomalySignal.

Mỗi candidate phải lưu:
- original observation;
- proposed correction;
- reason;
- context supplied;
- model/version;
- confidence nếu có;
- supporting/contradicting evidence.

Không cho Claude/LLM âm thầm rewrite Trusted Corpus.

==================================================
3. CROSS-CORPUS VERIFICATION
==================================================

Đây là ưu tiên cao trước Internet search.

Tận dụng chính corpus SGK/SGV.

Ví dụ nếu:

`Lý Thái Tổ`

xuất hiện đúng nhiều lần nhưng một occurrence thành:

`Lý Thái Tô`

thì tạo strong anomaly/correction evidence.

Research:

same-book consistency
same-lesson consistency
SGK ↔ SGV consistency
cross-grade terminology
repeated names
repeated definitions
repeated constants
repeated formulas.

Nhưng frequency != truth.

Nó là verification signal.

==================================================
4. EXTERNAL AUTHORITATIVE VERIFICATION
==================================================

Research bounded external verification.

Khi nội dung phù hợp, có thể dùng context để đối chiếu:
- official/reference sources;
- dictionaries;
- standardized scientific constants;
- authoritative terminology;
- other trusted public sources.

Ví dụ:
`Lý Thái Tô`
`3×10° m/s`
`bán sắc dân tộc`

có thể được đưa thành verification queries.

QUAN TRỌNG:

SEARCH RESULT != SOURCE TRUTH.

Internet evidence phải có:
- URL/source identity;
- retrieval timestamp;
- extracted claim;
- authority classification;
- relation to candidate correction.

Không lấy random search result để sửa SGK.

External verification trước mắt = RESEARCH/POC.
Không production auto-rewrite.

==================================================
5. USER / HUMAN CORRECTION
==================================================

Thiết kế correction workflow:

Learner / Parent / Teacher / Internal Reviewer
→ Report/Suggest Correction
→ ProposedCorrection
→ validation
→ Accepted / Rejected
→ new corpus version.

Không cho user trực tiếp overwrite canonical truth.

Correction record tối thiểu:

- sourceBlockId;
- original value;
- proposed value;
- reason;
- reporter type;
- source evidence;
- timestamp;
- validation result;
- reviewer/evidence;
- corpus version.

Research UX cho phép người dùng:

“Báo nội dung sai”

hoặc bounded:
“Đề xuất sửa”.

Nhưng chưa cần ship production UI nếu workflow/trust model chưa rõ.

==================================================
6. SPECIALIZED VERIFICATION
==================================================

Không bắt general OCR/LLM giải mọi domain.

Router theo content type:

TEXT
→ Vietnamese lexical/context validation

MATH
→ Math recognition
→ LaTeX/Math AST
→ structural validation

PHYSICS
→ Math AST
→ Symbol/Quantity/Unit/Constant validation

CHEMISTRY
→ Chemical Formula/Reaction structure

TABLE
→ table structure validator

HISTORY
→ names/dates/attribution consistency

VERSE
→ line/stanza structure.

==================================================
7. TRUST MUST BE EVIDENCE-BASED
==================================================

Không chỉ:

trusted = true.

Hướng tới:

TrustDecision
├── observations
├── validation signals
├── correction candidates
├── supporting evidence
├── contradictory evidence
├── provenance
└── disposition.

Possible disposition:

RAW
SUSPECT
WITHHELD
CORRECTION_PROPOSED
VALIDATED_REPAIR
TRUSTED
HUMAN_VERIFIED
CONFLICT.

Không bắt buộc implement toàn bộ enum/model nếu architecture hiện tại
đã có representation tương đương.

AUDIT FIRST.
REUSE BEFORE ADDING.

==================================================
8. IMPORTANT — DIFFERENT EVIDENCE STRENGTHS
==================================================

Không tạo trust ladder ngây thơ kiểu:

LLM < Internet < Human

và mặc định tầng cao hơn luôn đúng.

Ví dụ human cũng có thể sửa sai.

Trust phải phụ thuộc:
- evidence quality;
- independence;
- domain;
- source authority;
- reproducibility;
- teaching risk.

Human correction vẫn cần provenance.

==================================================
9. ROUND 5 POC
==================================================

Không mass implement.

Chọn một bounded Accuracy Recovery POC bằng chính các lỗi audit thật:

A. `3×10⁸ m/s → 3×10° m/s`
B. `Lý Thái Tổ → Lý Thái Tô`
C. `bản sắc → bán sắc`
D. `Cộng hoà → Cộng hoa`
E. `cây ổi → cây ỗi`

Với từng case, thử các signal:

- deterministic;
- specialized parser;
- Vietnamese lexical;
- cross-corpus;
- LLM semantic;
- external authoritative source.

Đo xem signal nào:

DETECT được lỗi;
PROPOSE đúng correction;
VERIFY được correction;
có nguy cơ FALSE CORRECTION bao nhiêu.

==================================================
10. CRITICAL METRICS
==================================================

Thêm:

ANOMALY DETECTION RECALL
CORRECTION PRECISION
CORRECTION RECALL
FALSE CORRECTION RATE
RESTORE PRECISION
CORRECT SERVED RESTORED
WRONG SERVED PREVENTED
HUMAN REVIEW RATE.

Đặc biệt:

FALSE CORRECTION RATE

phải là metric P0.

Không được biến:
OCR sai

thành:
AI tự tin sửa sai theo cách khác.

==================================================
11. DESIRED PRODUCT BEHAVIOR
==================================================

Mục tiêu cuối:

HIGH CONFIDENCE
→ serve.

UNCERTAIN
→ verify automatically.

RECOVERABLE
→ repair + validate + restore.

CONFLICT
→ withhold / human review.

USER FINDS ERROR
→ correction workflow
→ validate
→ improve future corpus version.

Như vậy WITHHOLD là safety state,
không phải nghĩa địa dữ liệu.

==================================================
12. AUDIT BEFORE IMPLEMENTATION
==================================================

Trước khi xây thêm subsystem, báo Founder:

1. Repo hiện đã có những capability nào tương đương?
2. Capability nào có nhưng chưa wired?
3. LLM verification đã tồn tại chưa?
4. Cross-corpus consistency đã tồn tại chưa?
5. External-source verification đã tồn tại chưa?
6. Correction/proposal workflow đã tồn tại chưa?
7. Trust/provenance model hiện có chứa đủ evidence không?
8. Phần tối thiểu nào cần bổ sung?

Sau audit:
được phép làm bounded/reversible POC trong Round 5.

Không mass reprocess.
Không auto-rewrite trusted corpus.
Không production Internet correction.
Không merge.

Mục tiêu Round 5:

OCR ACCURACY
+
MULTI-SIGNAL VERIFICATION
+
SAFE CORRECTION
+
RESTORE

chứ không chỉ:

MORE OCR
hoặc
MORE WITHHOLD.

Continue Round 5.
READY FOR FOUNDER REVIEW.
