# 04 — PROPOSED LEARNING UX & FLOWS (WAL-111 · solution)

## IA cuối (evidence-based)

`Learning Shell → LearnerContext → CurriculumContext(pack) → SubjectContext(family
adapter) → ActivityContext → TutorScope → SurfaceResolver → Surface(state-machine) →
TeachingAct → Response → Evidence → State → NextAction` — falsified qua 3 kiểm chéo môn
(§26 order): Toán problem-solving ✓ (kernel chạy) · TV reading/writing ✓ (Reader/Compose
chạy) · Sử/KHTN [I→POC]: SourceReader/Experiment dùng CÙNG chuỗi, chỉ đổi surface —
kiến trúc KHÔNG overfit Toán ở mức chuỗi; overfit nằm ở SURFACE COVERAGE (đã liệt kê).

**16 surfaces** (7 built ✓): QuizSelect✓ · LearningWorkspace✓(+4 states +drawing-mode
mới) · Reader✓ · Compose✓ · Camera✓ · Confirm✓ · Voice(P2▲) · Diagram/Drawing(P1▲) ·
Formula · Table/Data · Timeline · SourceReader · Map · Experiment/Observation ·
ActivityGuide(G) · Assessment-mode. Simulation = R&D gate (F16 đo trước).

## Learning flows (ENTRY→CONTEXT→SURFACE→ACT→ACTION→EVIDENCE→NEXT)

- **Problem Solving:** Home/Camera → scope+method → Workspace[independent→probe→hint(±1)
  →yourTurn→success] → evidence lineage → Agenda next. [chạy thật rồi]
- **Reading:** Text → Reader[READ gate] → câu hỏi → trả lời → feedbackFor → reflection.
- **Writing:** Đề → hiểu → outline → draft(independent) → SAM critique (không viết hộ) →
  revise(selfCorrection) → reflection. [Compose-lite đã đúng khung]
- **Science:** Hiện tượng → Observation → giả thuyết(learner) → Experiment/data → Table
  → giải thích → kết luận + evidence experiment-reasoning.
- **History:** Sự kiện → context → SourceReader[3 nhãn: NGUỒN NÓI/DIỄN GIẢI/EM KẾT LUẬN]
  → chronology(Timeline) → claim → giải thích.
- **Geography:** Map → locate → layer → so sánh → data-reasoning → kết luận.
- **Creative/Performance (G):** prompt → thực hiện → artifact (chụp/ghi âm — Camera/
  record Hub) → tự đánh giá checklist → phản hồi nỗ lực (không chấm).
- **Language (EN):** 4 kỹ năng tách: nghe(TTS/audio)→đáp; nói(STT)→phản hồi phát âm [R];
  đọc→Reader; viết→Compose. Adapter lexicon EN cho extractor [gap đã ghi].
- **AI Education:** YCCĐ code → Reader/Reflection/Diagram theo strand; không tool-list.
- **Assessment:** profile-confirm → mode khoá hint → làm → nộp → Result(independent/
  assisted) → remediation.

## Business flows (order §23-35)

- **STUDENT FREE:** toàn bộ learning loop trên + pack local + basic voice. KHÔNG paywall
  trong learning; cloud-LLM routing local-first→free→cloud (Hub ai_router + policy).
- **TEACHER FREE:** persona riêng (P-sau): tra chương trình (curriculum browser ĐÃ có
  data 7.6k bài) · soạn practice từ pack · worksheet/QR chia sẻ. Acquisition hypothesis
  — falsify bằng pilot [R].
- **PARENT BASIC (free):** tạo/quản lý learner, consent, privacy, delete/export, xem
  tình-hình-cơ-bản claim-gated.
- **PARENT PREMIUM (family-unit):** Daily Brief · «Tối nay giúp con gì» · Parent Coach
  (10 flows ĐỪNG-làm) · independent-vs-assisted insight · kế hoạch ôn · multi-child
  advanced · backup/sync · **ad-free toàn family [R]**. Bán INSIGHT+COACHING+CONVENIENCE.
- **ADS (nếu triển khai):** CHỈ contextual/non-personalized [pending legal child-ads VN/
  Play/Apple — R] · vị trí: sau-session transition, Library browsing, teacher utility ·
  **NEVER**: toàn bộ learning loop, assessment, essay, voice, reading, notif ·
  CẤM rewarded-ads đổi hint/answer/streak · SPONSORED ≠ RECOMMENDATION (nhãn rõ).
- **Invariants code-được:** PAYMENT ≠ LEARNING TRUTH (subscription không đụng
  mastery/evidence — test được) · AD VIEW không bao giờ phát LearningEvent.

## Shell còn lại theo audit cũ (giữ): shared-device switcher, Parent PIN, age-band
policy 4 mức, notifications learning-only, Settings child-safe.
