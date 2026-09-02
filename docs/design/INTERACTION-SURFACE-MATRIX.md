# INTERACTION SURFACE MATRIX (Task Order §16-17)

## Kiến trúc resolver (mở rộng ADR-009 đã chạy thật)

`LearnerContext → CurriculumContext → SubjectContext → ActivityContext →
resolveSurface → Surface(s) → TeachingAct → LearningEvidence.`
resolveSurface ĐÃ TỒN TẠI (learning_activity.dart) — mở rộng ResponseKind theo
evidence corpus, giữ luật: surface mới chỉ sinh khi corpus có activity tương ứng
(MCQ-4 từng bị bác vì 0 hit).

## Surface inventory (hiện có → cần thêm theo corpus)

| Surface | Trạng thái | Nuôi bởi corpus |
|---|---|---|
| QuizSelect | ✅ built | EXERCISE selectIdentify |
| ProblemStep/Workspace | ✅ built (T1) + cần handwriting (Canvas §27) | EXERCISE numericStep |
| Reader | ✅ built | READING (159 units TV1-5 đã trích) |
| ComposeLite | ✅ built | viết đoạn TLV |
| Voice | concept 35 → adapter STT/TTS Hub | oral/language |
| Formula/Graph/Diagram | cần (Lý/Hoá/Toán THCS+) | FORMULA/DIAGRAM units khi adapter môn chạy |
| Timeline | cần (Sử) | events (LS&ĐL đã OCR) |
| Map | cần (Địa) | MAP units |
| Table/Data | cần | TABLE units |
| SourceReader | cần (Sử/Văn — SOURCE_TEXT đã có role) | tư liệu |
| Experiment/Observation | cần (KHTN — 23 EXPERIMENT units đã bắt!) | thí nghiệm |
| Simulation | POC-gated (25/26 concept có giá trị; đo learning value trước — F16) | — |
| Assessment | cần (mode riêng — F9) | AssistancePolicy.assessment sẵn |

## Taxonomy activity §17 — verdict falsify

A Problem-Solving ✓ · B Scientific Investigation ✓ (EXPERIMENT units chứng thực) ·
C Reading/Argument/Source ✓ · D Spatial/Data ✓ · E Language ✓ · F Assessment ✓ —
**GIỮ nhưng thêm G: Creative/Performance** (ÂN, MT, HĐTN — 42-89 units/sách lớp 1
toàn ACTIVITY thực hành, không khớp A-F; corpus bắt buộc thêm). Không UI component
nào vào Curriculum Graph (F10: NO — graph = WHAT, resolver = WHICH).

## Ma trận family × surface chính

Toán: Workspace+Quiz+Formula · TV/Văn: Reader+Compose+Voice+SourceReader ·
KHTN/Lý/Hoá/Sinh: Experiment+Formula+Graph+Table+Workspace · Sử: Timeline+
SourceReader+Compose · Địa: Map+Table+Chart · Tin/CN: Procedure+Artifact(Canvas) ·
NN: Voice+Reader+Quiz · AI: theo strand A-D → Reader+Reflection+Diagram (KHÔNG
chat-tool list) · ÂN/MT/GDTC/HĐTN: Activity-guide surface (G) — hướng dẫn + phản hồi,
không chấm.
