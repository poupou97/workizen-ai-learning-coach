# Re-audit OSS adaptive learning — đọc SOURCE đã clone, so với WAL hiện tại

**Ngày:** 2026-09-01 · **Phương pháp:** `git clone --depth 1` + đọc mã thật (không chỉ README)
· clone tại `~/projects/oss-research/adaptive-learning/` (MIT/Apache — chỉ tham khảo, KHÔNG vendor)
**Câu hỏi Founder:** *các hệ này biết gì về dạy học/student modeling mà WAL chưa biết?*
**Đối chiếu với:** Concept · SkillCase · Method · ExerciseSkillMap · LearningEvidence ·
ConceptSummary · AdaptiveDecision · TutorScope · ReviewSchedule.

## Phân loại tổng

| # | Phát hiện (nguồn) | WAL hiện tại | Phân loại |
|---|---|---|---|
| 1 | **Help-penalty 3 chế độ** — OATutor `helpPenaltyMode.js`: `Never` / `AnswerReveal` (chỉ phạt bottom-out) / `OnOpen` (mở hint ⇒ lần submit sau **no-credit BKT, nhưng UI VẪN báo đúng cho học sinh**) | F3 đã chặn credit, nhưng WAL chưa tách "kế toán belief" khỏi "phản hồi hiển thị" | **ADOPT PRINCIPLE** — tách hai tầng: trẻ vẫn được khen khi làm đúng sau gợi ý; model lặng lẽ không ghi công. Đúng tâm lý trẻ em + đúng bằng chứng |
| 2 | **Hint dạng "scaffold" = CÂU HỎI CON** — OATutor `HintSystem.js`: hint không chỉ là text lộ dần; scaffold là sub-question học sinh phải TRẢ LỜI; sub-hints mở khoá tuần tự | LearningEvidence có `hintShown` nhưng hint của WAL chưa có khái niệm scaffold sinh-bằng-chứng | **ADOPT NOW (thiết kế)** — mỗi bước gợi ý nên là một câu hỏi nhỏ ⇒ chính đường-gợi-ý cũng SINH LearningEvidence thay vì chỉ tiêu thụ. Ăn khớp sẵn với `guidedAttempt` |
| 3 | **Penalty tách theo NGUỒN trợ giúp** — OATutor: `hint_penalty_mode` (mặc định OnOpen) ≠ `chat_penalty_mode` (mặc định Never) | WAL gộp mọi can thiệp vào SupportLevel/EvidenceKind | **RESEARCH LATER** — khi có Generative Tutor: hỏi-đáp tự do có nên phạt như hint? OATutor nói không-mặc-định. Cần dữ liệu |
| 4 | **TTS/voice gắn TRONG hint** — OATutor `ttsPlayer` từng hint, `math-to-speech/` (LaTeX→lời đọc) | WAL chưa có voice | **POC** — trả lời câu hỏi Founder "voice cho học sinh nhỏ": đọc GỢI Ý thành lời là điểm vào tự nhiên nhất, hẹp hơn hẳn voice-chat |
| 5 | **`forgets` là tham số hạng nhất của BKT** — pyBKT `INITIALIZABLE_PARAMS = [prior, learns, guesses, slips, forgets]`; ma trận chuyển `As` chứa cả learn lẫn forget, **theo từng resource class** | ReviewSchedule tách lịch ôn; pMastery chưa decay (đúng lệnh chờ dữ liệu) | **ADOPT PRINCIPLE (đường đã vạch)** — xác nhận kế hoạch ADR-005: bật quên = fit `forgets=True` offline bằng pyBKT trên log thật, resource-class = bucket khoảng-cách-thời-gian. Không đổi gì hôm nay |
| 6 | **Mô hình quên có phổ** — EduStudio: `dkt_forget` (WWW'19), `hawkeskt` (Hawkes process, `Δt` log-scale), `lpkt` (learning gain + forgetting cùng lúc) | — | **RESEARCH LATER** — chỉ liên quan khi có chuỗi dữ liệu dài; Hawkes xác nhận trực giác "recency theo log-thời-gian" của recencyScore |
| 7 | **Schema `stu_id·exer_id·label·start_timestamp·cost_time·cpt_seq` là chuẩn de-facto** — EduStudio `datatpl` assert đúng các cột đó | LearningEvent đã có đủ 1:1 (`timeSpent` = cost_time, `conceptIds` = cpt_seq) | **ĐÃ ADOPT** (ADR-004) — xác nhận lại: dữ liệu WAL dùng được cho cả vườn 28 model KT + 19 model CD của EduStudio không cần migration |
| 8 | **skillcoco = BKT + SM-2 local-first, "mastery doesn't mean learned once"** — review queue auto-sinh khi module mastered, hiển thị NGANG HÀNG với nội dung mới trên dashboard | ReviewSchedule có; chưa có quyết định UI | **ADOPT PRINCIPLE (UX)** — hàng-đợi-ôn là bề mặt hạng nhất của Mission Center, không phải mục chìm trong settings. Đồng thời: cùng stack (BKT+SM-2+local) ⇒ lựa chọn kiến trúc WAL có thêm một bản đối chứng độc lập |
| 9 | LearningStyle (visual/textual như thuộc tính bền) — skillcoco | — | **REJECT (giữ nguyên)** — đã bác từ audit trước, không đổi |
| 10 | GKT/DINA/NCDM (graph-KT, cognitive diagnosis đầy đủ) — EduStudio | Q-matrix nhị phân + luật loại trừ | **RESEARCH LATER** — đúng lệnh Founder: không nhận nguyên mô hình CD chỉ vì Q-matrix tồn tại |

## P1 — trạng thái
- **KT-PSP**: repo không tìm thấy ở org đã thử (`UpstageAI/KT-PSP` → not found). Cần định danh lại nguồn trước khi audit. Ghi Jira.
- **EdNet**: dataset (không phải engine) — chỉ đọc schema khi cần benchmark offline; license dataset TÁCH khỏi license mã.
- **OpenTutor**: chưa audit sâu (mentor-style Q&A, khác trục với WAL); RESEARCH LATER.

## Điều các hệ này KHÔNG có mà WAL có (giữ làm định vị)
Prerequisite graph xuyên lớp bám SGK thật · SkillCase (không hệ nào mô hình hoá "trường hợp" trong một concept) · ranh giới sư phạm fail-closed (TutorScope) · ba trục mastery/coverage/confidence · provenance citable. OATutor chọn bài trên **tập phẳng theo mastery thấp nhất** — không đồ thị, không ca.

---

## Bổ sung 2026-09-01 (WAL-55) — KT-PSP định danh lại + EdNet/OpenTutor audit nông

### KT-PSP: KHÔNG PHẢI repo — là paper construct. 404 trước đây do đoán sai org.

- Nguồn đúng: **arXiv 2512.00311** — *Tracing Mathematical Proficiency Through
  Problem-Solving Processes* (Park et al.) [ACADEMIC]. Đề xuất task **KT-PSP**
  (KT dùng QUÁ TRÌNH giải, không chỉ đúng/sai) + **StatusKT** (pipeline LLM
  teacher→student→teacher trích proficiency làm tín hiệu trung gian) + dataset
  KT-PSP-25. **Trang abs KHÔNG công bố mã/dataset** ⇒ không có OSS artifact để
  audit — đóng câu hỏi "tìm nguồn": nguồn là paper, không phải repo.
- OSS lân cận CÓ MÃ: **Oia-10/PSKT** (ACM MM'24 *Remembering is Not Applying*,
  PyTorch) [OSS] — ⚠️ **KHÔNG có LICENSE file** ⇒ mặc định all-rights-reserved:
  ĐỌC Ý TƯỞNG được, KHÔNG dùng mã. Schema dữ liệu: `user_id, problem_id,
  skill_id, correct, time_stamp` — trùng phần lõi `LearningEvent` của ta.
- Ý nghĩa cho SAM: văn liệu 2024–2025 đang đi đúng hướng ta đã đi —
  **process-aware KT**. Taxonomy 7 EvidenceKind (selfCorrection, hint
  provenance, support level) là "process signal" mà KT-PSP muốn có, nhưng của
  ta TẤT ĐỊNH và giải thích được thay vì qua LLM pipeline. Camera→lời giải
  viết tay của trẻ (tương lai) đúng là input KT-PSP nhắm tới.

### EdNet (riiid) — audit nông đúng phạm vi

- **License DATASET: CC BY-NC 4.0 — PHI THƯƠNG MẠI.** ⚠️ LEGAL: SAM là sản
  phẩm thương mại tương lai ⇒ KHÔNG benchmark/train bất kỳ thành phần SẢN PHẨM
  nào trên EdNet; chỉ tham khảo THIẾT KẾ SCHEMA. Ghi cùng ngăn với Legal Gate SGK.
- Schema đáng học: KT1→KT4 tăng dần độ mịn hành vi (`elapsed_time`,
  `action_type` enter/respond/submit, xem giải thích/bài giảng, `erase_choice`).
  Xác nhận quyết định đã có: `timeSpent` là trường hạng nhất; taxonomy hành vi
  của ta nằm ở vùng KT3–KT4 nhưng mang NGỮ NGHĨA sư phạm (hintRequested ≠
  hintShown) thay vì log UI thô.

### OpenTutor (github.com/opentutor — ICT Learning Sciences, USC)

- Dialog-tutoring authoring: giáo viên tự soạn tutor hội thoại (<1h), chấm
  câu trả lời mở bằng classifier. Trục KHÁC kernel (không mastery model theo
  ca) — đúng dự đoán "mentor-style, khác trục". Đáng quay lại khi làm
  **authoring workflow cho Generative Tutor** (WAL-30, gated) — bài học
  "authoring qua công việc quen thuộc (tạo đề + chấm)" là pattern tốt.

Sources: [arXiv 2512.00311](https://arxiv.org/abs/2512.00311) ·
[Oia-10/PSKT](https://github.com/Oia-10/PSKT) ·
[riiid/ednet](https://github.com/riiid/ednet) ·
[github.com/opentutor](https://github.com/opentutor)
