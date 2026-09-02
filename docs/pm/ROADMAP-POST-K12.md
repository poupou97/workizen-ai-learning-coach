# ROADMAP — Post-K12 Production Validation (Founder Master Order 2026-09-02)

> Jira là bộ nhớ thực thi — file này là bản chiếu (mirror) để đọc offline.
> Umbrella Epic: **WAL-112**. Baseline: 5 report `docs/design/01→05` @ 2f5e96f, snapshot corpus `docs/ingest-manifests/SNAPSHOT-K12.json` @ e47277a (531/531, 62.729 trang, 126.552 units).
> Caution giữ nguyên: STRUCTURAL COVERAGE ≠ DEEP SEMANTIC COVERAGE.

## Execution order

| # | Workstream | Ticket | Ghi chú |
|---|---|---|---|
| P0-A | First Vertical Slice — Toán 5 B6 phân số khác mẫu, 17 bước Home→Next Action | **WAL-108** | GO. Không fake bằng static demo. S24 acceptance. |
| P0-B | Cross-subject validation — TV Reader + Sử SourceReader + Architecture Verdict | **WAL-113** | blocked by 108. Không claim cross-subject vì interface nhìn generic. |
| P0-C | Multi-profile / shared device — A→B→A isolation | **WAL-109** | NO CROSS-LEARNER EVIDENCE CONTAMINATION. |
| P0-D | Hub Education Safety Adapter + capability audit 26 mục | **WAL-110** | OCR≠Evidence · Chat≠Tutor · Provider≠authority · Import≠curriculum · Analytics≠telemetry. |
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
