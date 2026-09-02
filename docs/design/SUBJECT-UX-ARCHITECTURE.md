# SUBJECT UX ARCHITECTURE (Task Order §21.F)

**Luật chung:** MỘT Subject Home shell (concept 07 làm base: position + provenance +
map-mini + hành động) — mỗi môn đổi TRỤC TƯƠNG TÁC, không đổi khung (F2: một template
KHÔNG đủ, nhưng N template rời cũng sai — shell + adapter).

- **Toán:** trục Workspace (viết tay = evidence quá trình) + method-card từ catalogue
  29 method có trang; hint ladder engine-quyết; formula surface từ THCS.
- **TV/Ngữ văn:** trục Reader/Compose (đã build); thêm SourceReader cho văn bản; SkillCase
  recognize≠explain≠apply≠write giữ tách (đúng store); chính tả = nghe-viết (STT/TTS §27).
- **KHTN (6-9):** MỘT môn — Subject Home hiện phân-môn (Lý/Hoá/Sinh) như tab con;
  trục Experiment/Observation (units đã bắt) + Formula + Table.
- **Lý/Hoá/Sinh (10-12):** kế thừa 25/26 (sim giữ, POC-gated đo learning value F16);
  Hoá: bảng tuần hoàn ✓, cân bằng PT ✓.
- **Sử:** Timeline + **SourceReader ba-nhãn: LỜI NGUỒN ≠ DIỄN GIẢI ≠ KẾT LUẬN CỦA EM**
  (thiếu trong concept 27 — bắt buộc thêm); nhân vật: tư liệu thật, không ảnh AI-gen.
- **Địa:** Map-first (28 giữ) + layer + Table/Chart; số liệu phải mang nguồn.
- **Tin/CN:** Procedure + Artifact (Canvas §27.4); an toàn số first-class.
- **Ngoại ngữ:** Voice-first (STT/TTS) + Reader + Quiz; 4 kỹ năng tách evidence.
- **AI (QĐ2422):** render từ AiCurriculum 267 YCCĐ — mỗi bài gắn code + strand A-D;
  hoạt động dạng Reflection/Diagram/Reader; TUYỆT ĐỐI không tool-list ChatGPT.
- **ÂN/MT/GDTC/HĐTN:** Activity-guide (family G): hướng dẫn từng bước + tự đánh giá
  cảm nhận, KHÔNG chấm đúng/sai, KHÔNG %.

## WAL-118 (2026-09-02) — SUBJECT SURFACE VALIDATION: bảng 6-câu × candidate

Nguồn số: units-k12 SGK toàn corpus (regex minh bạch; caveat ghi tại chỗ).
«VALIDATED» CHỈ khi POC đã chạy data thật (đúng luật không-claim-thiếu-evidence).

| Candidate | Learning job | Corpus evidence (unit id mẫu) | Generic đủ? | Specialized mode? | LearningEvidence? | Hub reuse | VERDICT |
|---|---|---|---|---|---|---|---|
| Experiment/Observation | dự đoán→làm→quan sát→so sánh | 5 khối «Chuẩn bị/Tiến hành» KH5 (05-sgk-khoa-hoc-5:p16…) + 11 khối g10 Lý/Hoá | KHÔNG (cần PREDICT-gate) | ✓ đã build | independentAttempt correct=null | camera (chụp kết quả — sau) | **VALIDATED (WAL-144, walk+JSONL)** |
| Map | nhìn lược đồ→chỉ ra→kết luận | 21 trang lược đồ + 31 bản đồ LS&ĐL5; câu hỏi p013 | KHÔNG (zoom + asset nguồn) | ✓ đã build (InteractiveViewer) | independentAttempt correct=null | design-tokens | **VALIDATED (WAL-144, walk+JSONL)** |
| SourceReader | nguồn→diễn giải→kết luận | TƯ LIỆU p018/p043 LS&ĐL5 | KHÔNG (3 tầng claim) | ✓ đã build | correct=null | — | **VALIDATED (WAL-113 B2)** |
| Reader / Compose | đọc-trả lời / viết-quá-trình | 68 bài đọc + 57 đề viết TV5 | — | ✓ đã build (WAL-98/113/144) | có (chuỗi process) | — | **VALIDATED** |
| Formula | tra/đọc công thức rồi áp | «công thức» 739 lượt — Toán 193, Hoá 121, CĐ 121 (⚠ regex dính «công thức làm bánh» TV/ngoại ngữ — số Toán/Hoá là tín hiệu thật) | Workspace Toán chứa được phần áp; TRA công thức chưa có | mode «formula sheet» ứng viên (band 6-12) | qua bài áp dụng | — | EVIDENCE CÓ — chưa build, KHÔNG claim |
| Reflection | tự đánh giá/chia sẻ cảm xúc | 375 lượt — HĐTN 82, Công nghệ 49, GDTC 47 (01-sgk-dao-duc-1:p020…) | Compose-lite gần (không chấm) | nhẹ: prompt+self-rating KHÔNG điểm | selfReport? — cần thiết kế evidence riêng (KHÔNG độn mastery) | — | EVIDENCE CÓ — chưa build |
| Diagram (đọc/hoàn thành) | quan sát/hoàn thành sơ đồ | 75 lượt — TN&XH 11, KHTN 9 (01-sgk-tu-nhien-va-xa-hoi-1:p081 «Cùng hoàn thành sơ đồ») | KHÔNG (cần slot-fill trên hình) | ✓ cần (kéo-thả nhãn) | selectIdentify-family | smart-canvas (ADAPTER) | EVIDENCE CÓ — chưa build |
| Graph/Data (đọc) | đọc đồ thị/số liệu→kết luận | đọc-đồ-thị 9 lượt (10-sgk-vat-li-10:p037…) + đọc-biểu-đồ 46 (Toán 18, LS&ĐL 12) | bảng/biểu đồ: ảnh-nguồn + câu hỏi mở (MapReader-family!) | đồ thị tương tác: chỉ band 10-12, evidence mỏng | correct=null | — | CHART: MapReader-family khả thi; GRAPH: evidence MỎNG (9) — KHÔNG ưu tiên |
| ActivityGuide | làm theo hướng dẫn nhóm/cộng đồng | 45 lượt — Công nghệ 34 (01-sgk-hoat-dong-trai-nghiem-1:p064) | hoạt-động-nhóm ngoài scope 1-learner | guide-view tĩnh đủ | KHÔNG (không đo được từ app) | — | GIỮ HƯỚNG DẪN TĨNH — không claim learning evidence |

Kết luận P1-C: **5 surface VALIDATED bằng data+device thật; 4 candidate có
evidence chờ lượt build (Formula/Reflection/Diagram/Chart); Graph 10-12 và
ActivityGuide không đủ evidence để cam kết** — đúng luật «không surface nào
claim validated mà thiếu corpus evidence». Screen decisions 03-report: KHÔNG
falsified thêm (giữ verdict hiện hành).
