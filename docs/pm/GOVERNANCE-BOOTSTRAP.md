# Governance Bootstrap — Jira · Confluence · GitHub

**Ngày:** 2026-09-01 · **Trạng thái:** GitHub ✅ · Jira ✅ · Confluence ✅ — **BOOTSTRAP HOÀN TẤT**

> ✅ **2026-09-01 (cập nhật):** Founder đã tạo Jira `WAL` + Confluence space `WAL`.
> Agent đã backfill: **10 Epic (WAL-1…10) + 34 issue (WAL-11…44)** theo trạng thái bằng
> chứng, trên Kanban 7 cột (Ideas→Analysis→Ready→In Progress→Code Review→QA→Done) mà
> Founder đã cấu hình sẵn; **16 trang Confluence** (00 Start Here … 15 Current Status).
> Bảng backlog dưới đây từ nay là BẢN LƯU LỊCH SỬ — nguồn sự thật vận hành là Jira WAL.

---

## 1. Vì sao Jira/Confluence chưa tạo được — chặn ở CÔNG CỤ, không phải ở quyết định

Founder đã cấp quyền tạo. Tôi **không** tạo được, và đây là giới hạn đo được chứ không
phải tôi ngại làm:

| Kiểm tra | Kết quả |
|---|---|
| MCP Atlassian có `createJiraProject`? | ❌ không có |
| MCP Atlassian có `createConfluenceSpace`? | ❌ không có |
| Có `acli` / `jira` CLI trên máy? | ❌ không có |
| Có biến môi trường `JIRA_*` / `ATLASSIAN_*`? | ❌ không có |
| Runtime AI Workforce có cơ chế tạo project? | ❌ không có |

Bộ MCP **tạo được**: issue trong project **đã tồn tại**, page trong space **đã tồn tại**.
Bộ MCP **không tạo được**: chính project và chính space.

⇒ Cần founder bấm tay **một lần**, ~2 phút. Sau đó agent làm nốt toàn bộ backlog.

## 2. ~~Founder cần làm gì~~ — **[LỊCH SỬ — ĐÃ LÀM XONG 2026-09-01]** giữ làm hồ sơ, KHÔNG còn là việc cần làm

### 2.1 Jira project

| Trường | Giá trị | Vì sao |
|---|---|---|
| Key | **`WAL`** | Đã kiểm 9 project đang có (`AWR CH WAD WAT WC WH WN WP WTM`) — `WAL` trống, không đụng ai |
| Name | `workizen-ai-learning-coach` | Convention **mới nhất**: `WAD` = `workizen-ai-driver`, `WTM` = `workizen-tongtai-mobile` — dùng **tên repo**, không phải tên sản phẩm |
| Template | **Software / Team-managed** | 9/9 project đang có đều `projectTypeKey=software`, `style=next-gen`, `simplified=true` |
| Access | **Không private** | 9/9 project đang có `isPrivate=false` |

Issue types cần có: **Epic · Story · Task · Feature · Bug · Subtask** (đúng bộ 8/9 project
đang dùng; riêng `WH` thiếu `Feature`).

Kanban: **Ideas → Analysis → Ready → In Progress → Code Review → QA → Done** (theo AI
Workforce V1 ở `CLAUDE.md` gốc). Gate merge/release/deploy là **Founder-only**.

### 2.2 Confluence space

| Trường | Giá trị | Vì sao |
|---|---|---|
| Name | `workizen-ai-learning-coach` | Khớp Jira name, theo convention `WAD`/`WTM` |
| Type | **knowledge_base** | 12/13 space đang có đều `knowledge_base` |
| Alias/key | **`WAL`** | Space mới nhất (`workizen-ai-driver`) có key sinh tự động nhưng **alias = Jira key** (`WAD`) |

### 2.3 Sau khi tạo xong

Xoá trường `"status": "PENDING_FOUNDER_CREATE"` trong `.workforce.json`, rồi bảo agent
*"populate WAL"* — toàn bộ §3 và §4 dưới đây đã soạn sẵn, agent đẩy lên trong một lượt.

---

## 3. Backlog khởi đầu — Epic (PHASE 5)

Gộp theo **bằng chứng trong repo**, không theo danh sách ý tưởng. 12 Epic đề xuất ban đầu
rút còn **9**: gộp `Learning Experience` + `Student Experience` (chưa có gì để tách), gộp
`Content/Curriculum Pipeline` vào `Educational Knowledge Architecture` (cùng một pipeline
trích xuất), bỏ `AI Lab` khỏi đợt đầu (chưa có bằng chứng nào trong repo).

| # | Epic | Trạng thái theo bằng chứng |
|---|---|---|
| E1 | Project Foundation & Governance | IN PROGRESS |
| E2 | Educational Knowledge Architecture | IN PROGRESS |
| E3 | Student Knowledge Model | IN PROGRESS |
| E4 | Adaptive Learning Engine | IN PROGRESS |
| E5 | AI Tutor & TutorScope | IN PROGRESS |
| E6 | Camera Tutor / Problem Understanding | TODO |
| E7 | Learning & Student Experience | TODO |
| E8 | Parent Experience | TODO |
| E9 | Research & Validation | IN PROGRESS |
| E10 | Safety, Privacy & Compliance | BLOCKED |

## 4. Issue khởi đầu (PHASE 6) — trạng thái theo BẰNG CHỨNG, không theo ý muốn

⚠️ Luật: **không đánh DONE cho thứ mới chỉ được thiết kế.** Cột "Bằng chứng" phải trỏ tới
tệp hoặc commit thật.

| Epic | Issue | Trạng thái | Bằng chứng |
|---|---|---|---|
| E1 | Repository bootstrap + identity + remote | **DONE** | 11 commit · `poupou97/workizen-ai-learning-coach` · `088f26a` |
| E1 | Bảo vệ corpus nhiều lớp | **DONE** | `ADR-002` · sandbox 4 ca có đối chứng |
| E1 | Convert AI Learning Coach thành submodule của umbrella (ADR-059) | **BLOCKED — theo lệnh Founder 2026-09-01** | KHÔNG resolve phân kỳ repo cha bây giờ; repo con GitHub là canonical; không đẩy thay đổi không liên quan lên repo cha |
| E2 | Provenance model (4 mức `KnowledgeOrigin`) | **DONE** | `provenance.dart` · 4 test |
| E2 | `CurriculumEdge` + citable theo loại khẳng định | **DONE** | `curriculum_edge.dart` · 4 test |
| E2 | Chuỗi prerequisite xuyên lớp | **DONE** | `cross_grade_remediation_test.dart` · 6 test |
| E2 | Trích cấu trúc SGK v2 (tự phát hiện bố cục) | **DONE** | `parse_structure.py` · `95a7ec6` |
| E2 | Cạnh prerequisite vẫn `llmInferred` — cần nguồn | **TODO** | báo cáo đêm, ô 🟡 |
| E3 | Mastery theo SkillCase (BKT) | **DONE** | `ADR-001` · `mastery.dart` · 6 test |
| E3 | Luật tổng hợp case → concept | **CLOSED 2026-09-01** | Founder BÁC khung `min` vs `mean`; thay bằng ConceptSummary ba trục — ADR-004 |
| E3 | Learning Evidence taxonomy (7 loại sự kiện, log thô, replay) | **DONE** | `learning_evidence.dart` · `evidence_weighting.dart` · ADR-004 · 9 test |
| E3 | ConceptSummary ba trục (mastery/coverage/confidence) | **DONE** | `concept_summary.dart` · ADR-004 · 14 test golden Founder |
| E3 | Lịch ôn tách khỏi ước lượng (F5) | **DONE (khung + policy giả thuyết)** | `review_schedule.dart` · ADR-005 · 5 test |
| E4 | Rule engine + `DiagnosticOutcome` 8 mức | **DONE** | `adaptive_engine.dart` · +`attributionUnresolved` (ADR-005) |
| E4 | Q-matrix đa kỹ năng (F6) — quy công/quy lỗi | **DONE** | `exercise_skill_map.dart` · `multi_skill_diagnosis.dart` · ADR-005 · 9 test |
| E4 | Next Best Action kèm lý do đọc được | **DONE** | `d.reason` · test thin slice |
| E4 | Misconception học lúc chạy (không từ corpus) | **TODO** | giả thuyết "SGV là nguồn" đã bị **bác bằng đo** |
| E5 | `TutorScope` = APPLICABLE ∩ ALLOWED, fail closed | **DONE** | `pedagogical_boundary.dart` · 5 test |
| E5 | Method applicability theo SkillCase | **DONE** | `conditional_method_golden_test.dart` · 7 test |
| E5 | Generative Tutor (LLM thật) | **TODO** | chưa có dòng mã nào |
| E6 | OCR local Apple Vision | **DONE (POC VERIFIED)** | 0,37 s/trang · 0 đ · văn xuôi ~100% |
| E6 | **OCR trên ảnh chụp điện thoại** | **TODO — P0** | mới đo trên bản quét; công thức toán 53% |
| E6 | Exercise → Concept/SkillCase mapping | **IN PROGRESS** | POC đo trên quét: precision 5/5, trần recall ~38–50%, đối chứng âm 0 false-positive — `OCR-PROBLEM-TO-CASE-POC.md` |
| E7 | UI skeleton / Student experience | **TODO** | `lib/features/*` **rỗng hoàn toàn** |
| E8 | Parent Coach | **IN PROGRESS** | tầng phát ngôn `parent_explanation.dart` (F4, ADR-005, 7 test); UI chưa có |
| E9 | SkillCase ở khái niệm thứ hai | **TODO** | mới xác minh sâu **một** khái niệm (`quy-dong`) |
| E9 | Benchmark OSS adaptive learning | **DONE** | `OPEN-SOURCE-ADAPTIVE-LEARNING-BENCHMARK.md` |
| E9 | Toán 4/5 — hai lớp hai phương pháp | **DONE** | lớp 4 Bài 57 tr.62 · lớp 5 Bài 6 tr.20 |
| E9 | Toán 9 — kết quả **âm tính** | **DONE** | không có phân số; bảng thuật ngữ 26 mục tr.119 |
| E9 | SGV — *"trường hợp"* ×13 / ≥5 chủ đề | **DONE** | mẫu 35 trang SGV Toán 4 |
| E9 | Retrieval POC riêng | **TODO** | báo cáo ghi rõ *"chưa chạy POC riêng"* |
| E9 | Thin slice end-to-end | **DONE** | `thin_slice_test.dart` · 6 test |
| E10 | Bản quyền SGK — Legal Gate | **BLOCKED** | `COMMERCIAL_USE_LEGAL_REVIEW_PENDING` |
| E10 | Child safety / privacy | **TODO** | mới là yêu cầu kiến trúc, chưa có mã |

## 5. Cấu trúc Confluence (PHASE 8)

Trang ngắn, chi tiết kỹ thuật để trong git. Confluence là nơi **founder đọc được**.

```
workizen-ai-learning-coach (space WAL)
├── 00 — Start Here
├── 01 — Product Vision
├── 02 — Product Architecture          ← kèm bảng độ chín từng hệ con
├── 03 — Educational Knowledge Model
├── 04 — Student Knowledge Model
├── 05 — Adaptive Learning
├── 06 — AI Tutor / TutorScope
├── 07 — Camera Tutor
├── 08 — Student Experience
├── 09 — Parent Experience
├── 10 — AI Lab
├── 11 — Research
├── 12 — Decisions / ADR Index
├── 13 — Safety / Privacy / Compliance
└── 14 — Current Status
```

## 6. Liên kết (PHASE 11)

| | |
|---|---|
| GitHub | https://github.com/poupou97/workizen-ai-learning-coach (PRIVATE) |
| Jira | `https://workizen.atlassian.net/browse/WAL` — ⛔ chưa tạo |
| Confluence | `https://workizen.atlassian.net/wiki/spaces/WAL` — ⛔ chưa tạo |
