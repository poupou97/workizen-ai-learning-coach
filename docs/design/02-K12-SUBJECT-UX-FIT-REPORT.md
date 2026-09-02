# 02 — K12 SUBJECT × UX FIT REPORT (WAL-111 · snapshot e47277a)

Nhãn evidence: [S]=SOURCE_EVIDENCE [A]=ARCHITECTURE [I]=INFERENCE [U]=UNKNOWN.
Ad eligibility per-môn: mặc định **NEVER trong mọi learning surface** (§28) — cột ads
chỉ nói về transition/browsing của môn đó.

| Môn (units) | Verb/Role thật [S] | Surface chính | Concept 38 fit | Thiếu | Hub reuse | Ads |
|---|---|---|---|---|---|---|
| **Tiếng Anh (22.913)** | lexicon VN không áp [U] — cần adapter EN | Voice + Reader + Quiz | KHÔNG có màn riêng — gap LỚN NHẤT bộ concept | Language surface 4-kỹ-năng | STT/TTS ✓✓ | transition-only |
| **Tiếng Việt (10.570)** | viết 1.148 · đọc 868 · READING 705 | Reader+Compose (đã build ✓) | 23 KEEP xác nhận bằng số | nghe-viết (chính tả) | TTS/STT | transition-only |
| **Chuyên đề 10-12 (9.889)** | vẽ·tìm·thực hành | Workspace+Diagram | KHÔNG màn nào đụng — gap 10-12 đã báo | chuyên-đề browser | Canvas POC | transition |
| **Công nghệ (8.720)** | quan sát 270 · trình bày 189 | Procedure+Artifact | không màn riêng (ok — dùng shell) | — | Canvas | transition |
| **Toán (8.496 + tầng sâu)** | vẽ 270 · tính 171 · EXAMPLE 1.305 | Workspace+Quiz+**Diagram** | 07/12 base ✓ nhưng **vẽ nhiều hơn tưởng** → thêm hình-học surface | drawing | Canvas POC ✓ | NEVER-learning |
| **Ngữ văn (7.377)** | viết 836 · đọc 430 | Compose full + SourceReader | 24 MODIFY xác nhận | văn bản dài + phân tích | doc reader | transition |
| **Tin học (6.871)** | thực hành 239 · chọn 116 | Procedure + Quiz | không màn riêng (ok) | thực-hành-máy guide | — | transition |
| **GDTC (5.204)** | vận dụng 253 · nói/kể | Activity-guide (G) | không màn — dùng G | video/animation hướng dẫn [I] | — | transition |
| **HĐTN/HĐTN-HN (7.777)** | đo(472?)·thảo luận·đánh giá | Activity-guide (G) + Reflection | không màn — G xác nhận | reflection surface | — | transition |
| **Mĩ thuật (4.513)** | (đo?)·vẽ·sắp xếp | Creative (G) | không màn | artifact capture (chụp bài vẽ!) | Camera ✓ | transition |
| **KHTN 6-9 (4.091)** | đánh giá·quan sát 91·EXPERIMENT 100 | Experiment+Observation+Table | 25/26 SAI cấu trúc môn (tách Lý/Hoá) — MODIFY giữ | experiment surface | Canvas/graph | NEVER-learning |
| **LS&ĐL 4-5 + Sử (7.7k)** | vẽ(sơ đồ) 438 · SOURCE_TEXT 54 · NOTE 395 | Timeline+SourceReader+Diagram | 27 MODIFY xác nhận (thiếu source-reading) | 3-nhãn nguồn≠diễn giải | doc reader | transition |
| **Âm nhạc (3.548)** | đọc(nhạc) 174 · hát 88 · nghe 75 | Listen+Perform (G) | không màn | audio playback+record | TTS/record ✓ | transition |
| **GDKT&PL (2.651)** | vẽ(sơ đồ) 179 · vận dụng | Reader+Diagram+tình huống | không màn | case-study surface [I] | — | transition |
| **Sinh/Hoá/Lý 10-12 (6.2k)** | vẽ·tính·quan sát·giải | Formula+Graph+Experiment | 25/26 đúng cho BAND NÀY | data-table | Canvas | NEVER-learning |
| **Khoa học 4-5 (1.904)** | quan sát 108 · nêu | Observation+Quiz | ok qua shell | — | — | transition |
| **TN&XH 1-3 (2.062)** | nói 203 · MCQ-family 10% | QuizSelect+Voice | ok ✓ | — | STT | NEVER (band 1-2) |
| **Địa lí (1.699)** | vẽ 121 · vận dụng | Map+Chart | 28 KEEP ✓ | data provenance | — | transition |
| **AI Education** | theo QĐ2422 [A] | Reader+Reflection+Diagram | 29 REPLACE giữ nguyên verdict | — | AI Router (realize-only) | NEVER (child) |

## Matrix band × surface (rút từ bảng + File 1)

- 1-2: QuizSelect · Voice · Reader-ngắn · Activity-guide — **KHÔNG Workspace phức tạp**.
- 3-5: + Workspace nhẹ · Observation · Compose-lite (đã build ✓ đúng band).
- 6-9: + Experiment · Diagram/Drawing · Formula · SourceReader · Map.
- 10-12: + Graph/Data · chuyên-đề browser · Formula-first density.

## SkillCase implication [S→A]

«SAME CONCEPT ≠ SAME EVIDENCE» xác nhận: TV tách viết/đọc/tìm/nói là các lệnh khác nhau
trên cùng bài — recognize≠apply≠write phải là SkillCase riêng (store đã thuận). Toán:
EXAMPLE 1.305 ⇒ worked-example là bước dạy chuẩn — TeachingAct DEMONSTRATE có chất liệu
thật ở mọi lớp.

## WAL-116 (2026-09-02) — «VẼ» TAXONOMY: SỐ ĐO THẬT + VERDICT

Classifier rule minh bạch (tool/design/classify_ve.py, v3 — «vẽ» ở VỊ TRÍ LỆNH,
không đếm nhắc-tới-vẽ giữa văn; OCR-variant «đoạn thắng» đã vá; rule đầu khớp
thắng, in samples để kiểm mắt): **729 lệnh «vẽ»** trong SGK toàn corpus.

| Loại | n | % | Chủ lực |
|---|---|---|---|
| TECHNICAL | 204 | 28.0% | Công nghệ 8/10/11 + Mĩ thuật 10-12 (bản vẽ kĩ thuật/phác thảo) |
| UNKNOWN | 160 | 21.9% | giữ nguyên UNKNOWN — không ép |
| GEOMETRY | 141 | 19.3% | Toán 2/6-9 (đoạn thẳng/hình/đường tròn) |
| DIAGRAM | 77 | 10.6% | TN&XH/KHTN/HĐTN (sơ đồ) |
| ARTISTIC | 59 | 8.1% | Mĩ thuật/HĐTN tiểu học |
| GRAPH | 35 | 4.8% | Vật lí/Toán (đồ thị) |
| CHART | 31 | 4.3% | Toán (biểu đồ) |
| ANNOTATE/MAP_SKETCH/VECTOR | 22 | 3.0% | rải rác |

**VERDICT: SHARED ENGINE + SPECIALIZED MODES** — không ONE-DRAWING-SURFACE:
GEOMETRY cần ràng buộc số kiểm được (độ dài/góc — engine chấm được «vẽ đúng»
không cần mắt); TECHNICAL cần lớp + chú thích kích thước (tiêu chí = checklist
cấu trúc, không chấm thẩm mỹ); CHART/GRAPH cần data-binding; ARTISTIC tự do
(không chấm). Stroke/layer/undo dùng chung. POC object model 2 loại top:
`lib/core/drawing/drawing_model.dart` (+ test trên 2 bài THẬT: «Vẽ đoạn thẳng
AB 9 cm» Toán 2, «Vẽ phác thảo sản phẩm» Công nghệ). UNKNOWN 21.9% giữ nguyên
UNKNOWN — phần lớn là «vẽ» trong tên bài đọc/lời kể, không phải lệnh vẽ được.
Hub Canvas (WAL-110 matrix): ứng viên reuse cho engine chung — adapter khi build.
