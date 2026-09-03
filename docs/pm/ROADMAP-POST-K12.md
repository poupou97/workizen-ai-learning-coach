# ROADMAP — Post-K12 Production Validation (Founder Master Order 2026-09-02)

> Jira là bộ nhớ thực thi — file này là bản chiếu (mirror) để đọc offline.
> Umbrella Epic: **WAL-112**. Baseline: 5 report `docs/design/01→05` @ 2f5e96f, snapshot corpus `docs/ingest-manifests/SNAPSHOT-K12.json` @ e47277a (531/531, 62.729 trang, 126.552 units).
> Caution giữ nguyên: STRUCTURAL COVERAGE ≠ DEEP SEMANTIC COVERAGE.

## Execution order

| # | Workstream | Ticket | Ghi chú |
|---|---|---|---|
| P0-A | First Vertical Slice — Toán 5 B6 phân số khác mẫu, 17 bước Home→Next Action | **WAL-108** | GO. Không fake bằng static demo. S24 acceptance. |
| P0-B | Cross-subject validation — TV Reader + Sử SourceReader + Architecture Verdict | **WAL-113 ✅** | blocked by 108. Không claim cross-subject vì interface nhìn generic. |
| P0-C | Multi-profile / shared device — A→B→A isolation | **WAL-109** | NO CROSS-LEARNER EVIDENCE CONTAMINATION. |
| P0-D | Hub Education Safety Adapter + capability audit 26 mục | **WAL-110 ✅** | OCR≠Evidence · Chat≠Tutor · Provider≠authority · Import≠curriculum · Analytics≠telemetry. |
| P0-E | Pedagogical Provenance end-to-end — lineage 10 tầng, fail-closed 5 điều kiện | **WAL-114** | blocked by 108. Không fabricate citation. |
| P0-F | Unit Economics — instrument runtime, MODE A/B/C, COGS Student Free | **WAL-115** | blocked by 108. Không build Ads SDK để chữa COGS. |
| P1-A | Drawing/Diagram taxonomy từ corpus → rồi mới quyết surface | **WAL-116** | "vẽ" ≠ một interaction. |
| P1-B | English 4-skill semantic adapter + child-speech research | **WAL-117** | Môn lớn nhất corpus (22.9k units), VN lexicon không áp được. |
| P1-C | Subject surface validation (KHTN→Địa→Sử→Ngôn ngữ→Creative→10-12) | **WAL-118** | blocked by 113. |
| P1-D | Age-adaptive UX — 1 Design System × 4 age policy | **WAL-50** | reuse, scope mở rộng. |
| P1-E | Parent Premium — value + entitlement architecture, chưa payment | **WAL-119** | ROLE+AGE+SUB+CAP+SAFETY→ENTITLEMENT. |
| P1-F | Teacher Free — use-case research + pilot design | **WAL-120** | Không LMS. Pilot live = Founder Gate. |
| P2-A | Semantic depth expansion theo batch (EN→Sử→KHTN→Địa→Toán 6-12→TV/Văn) | **WAL-121** | blocked by 117. llmInferred phải explicit. |
| P2-B | Assessment Mode — policy khác Tutor Mode | **WAL-122** | blocked by 108. assisted ≠ independent evidence. |
| P2-C | Voice — sau EN adapter + band 1-2 findings | **WAL-123** | blocked by 117. Uncertainty cao → không thành evidence. |
| P2-D | Knowledge Pack real-device scale 100MB→2GB+, FULL vs MODULAR | **WAL-84** | In Progress. Breakpoint 654ms→4.6ms đã vá. |
| P2-E | Business experiments — fake-door, pilot design, canary, ads research | **WAL-124** | blocked by 119. KHÔNG ad SDK, KHÔNG thu tiền thật. |
| GATE | Ads for children — legal research VN + Play Families + Apple Kids | **WAL-125** | Research-only → trình Founder. |

**Checkpoint #1 (§29) posted 2026-09-02 trên WAL-112**: P0-A+P0-B DONE (WAL-108 S24, WAL-113
Nokia máy-trắng — TV Reader câu-hỏi-mở + Sử SourceReader 3 tầng + verdict docs/design/07;
bug index-sau-onboarding fix kèm test). WAL-114 ✅ (lineage, b2bbdf9) · WAL-115 ✅ (unit economics — MODE A $0 theo cấu trúc, f265962; addendum AI COST trên WAL-112). WAL-110 ✅ (ADR-010 e9ffb56).
**Checkpoint #2 posted 2026-09-02 trên WAL-112 — P0 HOÀN TẤT (108/113/109/110/114/115).**
P1: WAL-132 ✅ (PresentationPolicy, 6b49869) · WAL-144 ✅ (6 surface: TV/Sử/Essay/KHTN/Địa/
Lý-Hoá-g10 — walks n23→n42, JSONL 4 môn mới, c557730). WAL-116 ✅ (taxonomy 729 lệnh «vẽ» → SHARED ENGINE +
SPECIALIZED MODES, POC object model, 6488318). WAL-117 ✅ (EN adapter v2 + child-speech
memo, 3e69d12 — mở khoá WAL-121/123). WAL-119 ✅ (entitlement-v1, PAYMENT≠TRUTH cấu trúc, a92571f). WAL-120 ✅ (matrix+POC+pilot design, 420e158). WAL-118 ✅ (bảng 6-câu: 5 VALIDATED thật / 4 evidence-chờ / 2 không-claim, 80c0470). KS-F ✅ + Epic WAL-147 KHÉP (đa-môn=0 falsified tại
scale slice — fail-closed; bench store <1ms; §37 SCALE-có-điều-kiện chờ Founder). WAL-125 ✅ research (memo+bảng+lawyer-questions, STOP trình
Founder, d5d87f9) · WAL-84 mốc-3 Nokia (100MB FTS p95 7ms; breakpoint ×105 tái xác nhận máy thấp)
· WAL-33 mitigation ① (plausibility, 987550f). Còn mở: WAL-30 (chờ Founder) · WAL-84 (tier
500MB+/battery) · WAL-33 (recall chờ ảnh thật) · WAL-50 (P3 — tokens/dark/motion/density XONG a43b70c, còn wire consumer)
· WAL-84 mốc-4 670MB Nokia (FTS p95 49ms — interactive-class; mystery app-biến-mất = integration_test tự gỡ app, đã đính chính). WAL-84 mốc-5 trọn tier (2.7GB/3.82M units Nokia:
FTS p95 92ms — KHÔNG điểm gãy tới hết scale mục tiêu; ngưỡng đề xuất 4-5GB; FULL-vs-MODULAR
thành câu hỏi product) · WAL-141 ✅ (drill-down #16 walked n50-n53 + #17 «Nguồn bài học» SubjectHome, 97f68a7).
WAL-142 ✅ DONE (Progress/Map/Sessions phủ truths — maxSupportIn/explainConcept/
reviewStateOf/badge-chỉ-khi-evidence, 3 mutations killed, 3a48621; walk Nokia n57-n65 xác nhận
claim-gate «1 lần đúng CHƯA đủ kết luận» hiện đúng trên máy). QA máy lộ lỗi Bản đồ đổ 251 dòng
theo thứ tự JSON ⇒ bài có badge bị chôn dưới ~200 dòng — sửa 6bb66b5 (môn có bằng chứng lên đầu
+ mở sẵn, môn khác gập kèm số bài, nhãn Tập 1/2; 2 mutations killed). ⚠️ bản sửa CHƯA đi lại máy
(Nokia rút lúc build xong) — việc đầu tiên khi cắm lại. Nợ: badge còn gắn slice cứng Toán-B6,
tổng quát hoá khi curriculum mở môn. Deferred: 121-124, 137-140/143-146 UI backlog, ALA 155-158, MA 159-162.

**WAL-163 ✅ CI GATE** (2026-09-03, blocker billing tháo): `.github/workflows/ci.yml` — analyze +
toàn suite trên PR/main, hẹp có chủ ý (không build/ký/deploy/secrets). Run đầu 33708714147 ĐỎ vì
lỗi THẬT: map_reader_test phụ thuộc crop PNG chỉ có ở máy tôi (gitignore WAL-43) — «xanh» từ
WAL-144 mà không ai biết. Sửa: tiêm bundle test + assert tên asset (chặt hơn bản cũ) + errorBuilder
nói thật khi thiếu crop. Run 33709174817/33709383804 XANH, main = 32c0592. Bài học đã thành quy
trình: xác minh test trong `git clone` sạch, vì file gitignore làm test xanh giả ở máy dev.
⚠️ Founder quyết: bật branch protection thì «vỡ là không merge được» — hiện chưa bật.

**WAL-143 ✅ Kiểm tra hiểu bài** (af921d9 + c207878, CI xanh): mặt tiền của
`AssistancePolicy.assessment` — dependency WAL-122 hoá ra đã thoả ở tầng engine (WAL-104), repo
thắng ticket. Cấm gợi ý bằng CẤU TRÚC (test quét mã nguồn cấm 5 chuỗi), cùng bộ chấm với lúc học,
không parse được ⇒ không dám chấm, kết quả không điểm-số, hỏi đúng người trước khi ghi bằng chứng
độc lập. Walk Nokia n70-n77: 2 đúng 1 sai ⇒ vẫn «chưa đủ để kết luận (7 lần tự làm)». 487 test,
3+1 đột biến bị giết. Nợ: MCQ-family TN&XH (#20); chọn câu theo ca yếu thay vì 3 bài đầu.
⚠️ **Founder quyết (A/B)**: con vừa sai một câu mà Hôm nay vẫn «nghỉ ngơi nhé» — giữ nguyên
(không nag) hay cho lỗi MỚI nâng ưu tiên sớm hơn lịch 7 ngày? Không tự đổi chính sách ôn tập.

**WAL-133 ✅ DONE slice 1+2** (7b3ea37, CI xanh): pipeline `SourceAsset` chạy thật ở **3 môn** —
LS&ĐL bản đồ tr.10, Toán hình phân số tr.22, Khoa học ảnh thí nghiệm «Hình 5» tr.16 (walk WiFi
n78-n80). Công cụ: `preview_page_grid.py` (lưới 0.1 chấm bbox bằng mắt) + `crop_source_assets.py`
(một registry chung). ⭐ Cắt tới môn THỨ HAI mới lộ lỗ hổng model: hình Toán không có caption in
trong sách, mà model slice 1 bắt buộc `caption` ⇒ phải bịa lời sách. Sửa: `printedCaption` nullable
+ `samGloss` có nhãn «SAM NÓI THÊM» riêng. ⚠️ CI bắt lỗi «test đo tủ đồ của tôi» LẦN THỨ HAI (đếm
chữ lệch vì máy có PNG) ⇒ dựng `test/support/pack_bundle.dart` (packHost/missingPackHost) để sửa
bằng cấu trúc chứ không bằng trí nhớ. Cố ý để lại: `SamGeneratedAsset` chưa có chỗ dùng thật.

**WAL-163 ✅ D1 THI HÀNH** (e987399): branch protection `main` — check «Analyze & Test» bắt buộc,
strict, cấm force-push/xoá nhánh, giữ admin bypass. Bật xong lộ ngay bẫy `paths-ignore` ×
`required check` (PR tài liệu treo PENDING vĩnh viễn) — đã bỏ lọc ở `pull_request`. Quy trình từ
nay: nhánh → PR → CI → merge. LOCAL GREEN ≠ MERGEABLE.

**WAL-164 📋 MỚI** (Founder D2): Review Priority Resolver — câu SAI sinh BẰNG CHỨNG, không tự động
thành báo động. Bảng luật: slip đơn lẻ giữ normal · tự-làm-sai + mapping tin cậy ⇒ ôn 1–3 ngày ·
hiểu sai LẶP LẠI ⇒ nâng · tiền đề yếu cho bài đang học ⇒ được vào Today · mapping không chắc ⇒
fail conservative · đúng-có-trợ-giúp ⇒ ôn sớm hơn nhưng KHÔNG phải failure. Hàng đợi: sau 137/140/145.

**WAL-133 (cũ) slice 1** (07d1459, CI xanh): `sealed LearningAsset` 3 loại — `SourceAsset` không dựng
được nếu thiếu nguồn/trang/bbox/extractionVersion, và assert luôn «phải nằm dưới assets/pack/»
(WAL-43). Hình SAM vẽ KHÔNG mượn được dòng nguồn; nhãn «Minh hoạ của SAM» không tắt được bằng tham
số. Fallback theo loại (ảnh nguồn NÓI, trang trí IM). Builder+DiaMap tải provenance crop từ
registry, thiếu ⇒ bỏ bản đồ. MapReader là consumer thật (Nokia n78). Test WAL-43 THẬT chạy
`git ls-files assets/pack/`. 10 test, 3 đột biến bị giết. **Còn**: crop tool ≥3 môn (curate bbox
người làm), visual identity doc, `SamGeneratedAsset` chưa có chỗ dùng thật.

## Founder Gates (không tự vượt)
Textbook licensing (WAL-43) · child-ads commitment (WAL-125) · Premium pricing · production payment · external pilot go-live · generative learner-visible (WAL-30 KEEP SHADOW) · real-learner claim (WAL-49) · major cloud spend · destructive ops · irreversible branding.

## Checkpoints
- **#1** sau WAL-108 + WAL-113 (format §29 Master Order — 22 mục). KHÔNG build toàn bộ production UI trước đó.
- **#2** sau toàn bộ P0 (108, 113, 109, 110, 114, 115): production readiness, risks, COGS, child safety, local-first, isolation, generalization, P1 priorities.
- Ngoài checkpoint + gate + falsification quan trọng + cost threshold: tự động lấy ticket Ready tiếp theo.

## Business invariants
STUDENT FREE · TEACHER FREE · PARENT BASIC FREE · PARENT PREMIUM (family unit). PAYMENT ≠ LEARNING TRUTH. AD VIEW ≠ LearningEvidence. Ads không trong learning loop; không rewarded-ads hint/answer/streak; Grade 1-2 = NO ADS (hypothesis). Không monetize: hint, answer, assessment, mastery, evidence, child data, streak, dependence. North Star ≠ time-in-app.

## Concept reconciliation
38 concept = reference, không phải spec. ~24 routes / ~16 surfaces = PROPOSED v0.1. POC được falsify; mọi thay đổi verdict cập nhật `docs/design/03-38-CONCEPT-SCREEN-REAUDIT.md` — không silently drift.

## Pedagogy layer (Founder Order 2026-09-02 #2 — Epic WAL-126)

| Phase | Workstream | Ticket |
|---|---|---|
| 1 | SGV Pedagogy Mining (File 01) | WAL-127 |
| 2 | Pedagogical Pattern Model + ladder v2/misconception/transfer/age/provenance (File 02) | WAL-128 |
| 3 | LearningExperienceBlueprint + 5-10 mẫu (File 03) | WAL-129 |
| 4-6 | 5-Subject Pedagogy Validation (File 04) | WAL-130 |
| 7 | Pedagogical QA Harness + LLM Realization Contract (File 05) | WAL-131 |
| 8 | Presentation Policy + Surface Binding | WAL-132 |

Invariant trung tâm: **LLM KHÔNG PHẢI PEDAGOGICAL AUTHORITY** — chỉ realization trong contract. Artifacts: `docs/pedagogy/01→05`. Versioning thêm: pedagogyModelVersion, blueprintVersion, presentationPolicyVersion — replay không silently reinterpret. Không đảo UI trước pedagogy.

## Founder Direction 2026-09-02 (tối) — UI/UX FIRST + Content Enrichment on demand

Production UI/UX **được mở** (hết chốt chờ-checkpoint): triển khai UI từ 38 concept + Design
System + dữ liệu thật hiện có + subject surfaces. Không mở lại data/OCR foundation trừ khi UI
bị chặn thật. Làn chính: WAL-108 (device walk ✓) → **WAL-132** surfaces + visual identity theo
môn/bài → enrichment scoped khi màn cần (WAL-133: SOURCE_ASSET có provenance đầy đủ /
SAM_GENERATED «Minh họa của SAM» / UI_DECORATIVE; OCR lại chỉ scoped book/page/lesson/asset,
không rebuild corpus). OCR-perfection không bao giờ là blocker của UI.

## Knowledge Stories (Founder Order 2026-09-02 #4 — Epic WAL-147, P1 HIGH)

| WS | Ticket |
|---|---|
| KS-A Sample đa-môn + model + precision | WAL-148 |
| KS-B Verification + review states + quote rules | WAL-149 |
| KS-C Portrait/visual extraction (WAL-133 assets) | WAL-150 |
| KS-D Local store + FTS search | WAL-151 |
| KS-E Discovery UI slice (Settings/Library/Detail/Loading/Today) | WAL-152 |
| KS-F Cross-subject + device validation + checkpoint §36 | WAL-153 |

Pipeline: SOURCE→CANDIDATE→VERIFY→NORMALIZE→CURATED→UI. POC sample trước, đo precision, mới scale.

## Adaptive Learning Activities Research (Founder Order 2026-09-02 #5 — Epic WAL-154, P2 · SAU CÙNG)

| WS | Ticket | Ghi chú |
|---|---|---|
| ALA-A Discovery/shortlist/matrix + gamification review | WAL-155 | discovery nhẹ được phép sớm |
| ALA-B Hub Game AI + Academy deep audit | WAL-156 | được phép lật verdict matrix nếu có bằng chứng |
| ALA-C Primitives + Adaptive Activity Engine proposal | WAL-157 | blocked by 155 |
| ALA-D Signature activities (Bắt lỗi SAM, Dạy lại SAM…) + ≤3 POC recs | WAL-158 | blocked by 155+156 |

KHÔNG chen trước UI core/M1/P0/KS. North star §36: trẻ suy nghĩ nhiều hơn, tự làm nhiều hơn,
giải thích tốt hơn, dần cần SAM ít hơn — game là MỘT surface, không phải sản phẩm.
Report đích: docs/research/SAM-ADAPTIVE-LEARNING-ACTIVITIES-OSS-REVIEW.md (một file duy nhất).

## Multi-Agent Learning & Academic Perspective Graph (Founder Order 2026-09-02 #6 — Epic WAL-159, P2 · RESEARCH LATER)

| WS | Ticket | Ghi chú |
|---|---|---|
| MA-A Research hai chiều (Solution/Academic Perspective) + ontology + repo study | WAL-160 | relates WAL-131 |
| MA-B Graph Pattern Discovery — matcher trên graph thật, đếm instance | WAL-161 | blocked by 160; relates WAL-77 |
| MA-C ≤3 POC (cross-grade / model-evolution / Historical Council) + eval cost/latency/pedagogy | WAL-162 | blocked by 161; relates WAL-158 |

Thesis Founder: multi-agent = làm CẤU TRÚC tri thức/phương pháp/bằng chứng/góc nhìn hiện ra để
HỌC SINH làm việc nhận thức — «Student cognitive work > AI conversation»; AI nói nhiều hơn mà
học sinh nghĩ ít hơn = FAIL. Khoá: PERSON FOLLOWS CONCEPT · SOURCE FACT ≠ DOCUMENTED POSITION ≠
RECONSTRUCTION ≠ SAM EXPLANATION ≠ STUDENT INTERPRETATION · multi-agent ≠ UI lộ agent ≠ nhiều
LLM call (deterministic graph → planner → 1 LLM constrained → verifier). Learning Opportunity =
Graph Pattern × Learner State × Curriculum Permission × Pedagogical Policy.
KHÔNG chen trước P0/P1/ALA; KHÔNG persona chatbot; KHÔNG đổi production UI vì hướng này.

**Delta 2026-09-02 — PRIOR ART FIRST:** trước mọi ontology/architecture mới phải nghiên cứu
Educational KG có sẵn — seeds: EduKG (Tsinghua/THU-KEG) · K12-KGraph · KnowEdu · tự search thêm;
protocol SEARCH→VERIFY→CLONE→INSPECT(code/data/pipeline/license)→RUN, không chỉ README, không
copy code vào production; comparison matrix Research × SAM × Extension; mục FALSIFY IT (8 kết
luận phủ định hợp lệ); đầu ra: 2 hypothesis verdicts + khuyến nghị TỐI ĐA 1 bounded graph POC.
«DO NOT INVENT AN EDUCATIONAL GRAPH FROM ZERO.»
