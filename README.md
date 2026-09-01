# Workizen AI Learning Coach

Gia sư thích ứng **có ý thức sư phạm** cho học sinh phổ thông Việt Nam.

> ⚠️ **Trạng thái: DOMAIN KERNEL + RESEARCH.** Chưa có màn hình nào. `lib/features/*` là
> thư mục rỗng. Đừng đọc sơ đồ kiến trúc rồi tưởng đã có UI — xem bảng độ chín bên dưới.

---

## Vì sao dự án này tồn tại

Một học sinh lớp 5 làm sai `3/4 + 2/5` **có thể không hề hổng quy đồng**.

Sách Toán 4 (Bài 57, tr.62) dạy quy đồng cho ca **mẫu này chia hết cho mẫu kia** → lấy
mẫu lớn. Sách Toán 5 (Bài 6, tr.20) dạy ca **không chia hết** → lấy **tích** hai mẫu. Em
ấy có thể đã vững ca lớp 4 và đang bối rối vì **luật đổi**.

Can thiệp đúng là **đối chiếu hai ca**, không phải bắt em học lại thứ đã vững.

Một gia sư chỉ biết "sai phép cộng phân số" không phân biệt được hai tình huống đó. Đây
là toàn bộ lý do của kiến trúc `Concept → SkillCase → Method`.

## Độ chín từng phần — dùng đúng từ vựng, không báo cáo vượt thực tế

| Hệ con | Độ chín |
|---|---|
| Educational Knowledge Model (`Concept`, `CurriculumEdge`, provenance) | **DOMAIN IMPLEMENTED** |
| `SkillCase` + method applicability | **DOMAIN IMPLEMENTED** |
| `TutorScope` (fail closed) | **DOMAIN IMPLEMENTED** |
| Student mastery — BKT theo ca (ADR-001) | **DOMAIN IMPLEMENTED** |
| Learning Evidence — log thô 7 loại sự kiện, replay được (ADR-004) | **DOMAIN IMPLEMENTED** |
| `ConceptSummary` — mastery ≠ coverage ≠ confidence (ADR-004) | **DOMAIN IMPLEMENTED** |
| Adaptive Decision Engine (rule-based) | **DOMAIN IMPLEMENTED** |
| Q-matrix đa kỹ năng + quy lỗi `attributionUnresolved` (ADR-005) | **DOMAIN IMPLEMENTED** |
| Lịch ôn tập (tách khỏi ước lượng tri thức, ADR-005) | **DOMAIN IMPLEMENTED** |
| Parent Coach — tầng phát ngôn claim-gated (ADR-005) | **DOMAIN IMPLEMENTED** — UI chưa có |
| Trích cấu trúc SGK từ mục lục | **POC VERIFIED** (0 LLM, 0 đ) |
| OCR trang sách | **POC VERIFIED** trên bản quét · công thức toán 53% |
| Camera Tutor | **DESIGNED** — chưa đo trên ảnh điện thoại |
| Exercise → Concept/ca mapping | **POC VERIFIED** trên quét — precision 5/5, trần recall ~38–50%, nút thắt: ghép biểu thức |
| Misconception model | **RESEARCHED** — không có nguồn văn bản, phải học lúc chạy |
| Toàn bộ UI / Student / Parent experience | **NOT STARTED** |

Từ vựng độ chín: `RESEARCHED` → `DESIGNED` → `DOMAIN IMPLEMENTED` → `POC VERIFIED` →
`UI IMPLEMENTED` → `DEVICE VERIFIED` → `PRODUCTION READY`.

## Kiến trúc — chuỗi từ bài tập tới bằng chứng học tập

```
Nguồn tri thức  →  Educational Knowledge Model  →  Concept  →  SkillCase
                                                                   ↓
                                                    Method + Applicability
                                                                   ↓
Camera / OCR  →  Problem Understanding  →  phát hiện ca của bài tập
                                                                   ↓
                              Student Knowledge / Mastery (BKT theo ca)
                                                                   ↓
                                          Adaptive Decision Engine
                                                                   ↓
                       TutorScope = APPLICABLE ∩ PEDAGOGICALLY_ALLOWED
                                                                   ↓
                                                    AI Tutor  →  Learning Evidence
                                                                   ↺
```

Bất biến trung tâm:

```
AVAILABLE_TO_TUTOR = APPLICABLE_TO_PROBLEM ∩ PEDAGOGICALLY_ALLOWED
```

Không xác định được ca ⇒ **fail closed**: Tutor nhận tập rỗng. Thà nói *"chưa chắc"* còn
hơn dạy nhầm dạng bài.

## Tài liệu

| | |
|---|---|
| Quyết định (ADR) | [`docs/decisions/`](docs/decisions/) |
| Kiến trúc | [`docs/architecture/`](docs/architecture/) |
| Nghiên cứu | [`docs/research/`](docs/research/) |
| Sản phẩm | [`docs/product/`](docs/product/) |
| Báo cáo gần nhất | [`docs/OVERNIGHT-REPORT-2026-08-31.md`](docs/OVERNIGHT-REPORT-2026-08-31.md) |

## ⛔ An toàn nguồn — đọc trước khi chạm corpus

Nguồn SGK có **điều khoản cấm sao chép/lưu trữ/chuyển thể bằng văn bản**. Trạng thái:

- `TECHNICAL_POC_ALLOWED_BY_FOUNDER`
- `COMMERCIAL_USE_LEGAL_REVIEW_PENDING`

**Không** commit PDF, text trích xuất, ảnh trang, chunk hay embedding. **Không** tự nâng
lên `LEGAL_APPROVED`. Chi tiết: [`TEXTBOOK-LICENSING-QUESTIONS.md`](docs/research/TEXTBOOK-LICENSING-QUESTIONS.md)
· ba lớp bảo vệ corpus đã đo: [`ADR-002`](docs/decisions/ADR-002-bao-ve-corpus-nhieu-lop.md).

## Governance

| | |
|---|---|
| GitHub | [poupou97/workizen-ai-learning-coach](https://github.com/poupou97/workizen-ai-learning-coach) (PRIVATE) |
| Jira | `WAL` — ⛔ chưa tạo, xem [`GOVERNANCE-BOOTSTRAP.md`](docs/pm/GOVERNANCE-BOOTSTRAP.md) |
| Confluence | `WAL` — ⛔ chưa tạo |
| Cấu hình agent | [`.workforce.json`](.workforce.json) |

## Công cụ

| | |
|---|---|
| `tool/ocr/ocr_pdf.swift` | OCR local bằng Apple Vision — 0 LLM, 0 đ, 0,37 s/trang |
| `tool/extract/parse_structure.py` | ✅ **v2, dùng cái này** — tự phát hiện bố cục |
| `tool/extract/parse_toc.py` | ⛔ v1, **sai IM LẶNG** trên mục lục 2 cột. Đừng dùng |

## Phát triển

```bash
flutter pub get
flutter test       # 48 test (39 chức năng + 9 falsification)
flutter analyze
```

Quy ước: **tài liệu, comment, commit message viết bằng tiếng Việt**; thuật ngữ kỹ thuật
giữ nguyên tiếng Anh (SkillCase, provenance, fail closed, mastery).
