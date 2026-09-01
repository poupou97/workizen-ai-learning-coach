# ADR-005 — Q-matrix đa kỹ năng, phát ngôn truy vết được, lịch ôn tách khỏi ước lượng

**Ngày:** 2026-09-01 · **Trạng thái:** ACCEPTED (thi hành quyết định Founder P1: F4 · F6 · F5)
**Bằng chứng:** `multi_skill_test.dart` (9) · `parent_explanation_test.dart` (7) ·
`review_schedule_test.dart` (5) · EduStudio `cpt_seq` · văn liệu SM-2/FSRS/DINA

---

## F6 · `ExerciseSkillMap` — Q-matrix nhị phân có xuất xứ

- Một bài = một DANH SÁCH `SkillRequirement{conceptId, skillCaseId, provenance}`.
  `skillCaseId` bắt buộc (doctrine F2); provenance bắt buộc (hàng Q-matrix LLM đoán
  không bao giờ thành lời sách). KHÔNG phải DINA/NCDM đầy đủ — Founder cấm nhận nguyên
  mô hình CD chỉ vì Q-matrix tồn tại; biểu diễn tiến hoá bằng cách THÊM trường.
- Mô hình kết hợp **conjunctive (AND-gate)** với hệ quả bất đối xứng CỐ Ý:
  - đúng ⇒ công cho TỪNG thành phần (`attributeEvidence` sinh sự kiện thô, F3 áp
    nguyên: post-hint không được chấm);
  - sai ⇒ sự kiện ĐƯỢC GHI (`finalCorrectness`, không chấm), quy lỗi đi qua
    `attributeFailure` — luật loại trừ: mọi thành phần vững ⇒ `executionError`;
    đúng một thành phần không vững ⇒ delegate `decide` (tái dùng, không chép luật);
    ≥2 ⇒ **`attributionUnresolved` + `isolateSkills`** — biểu diễn mà ADR-003 §F6
    ghi là còn thiếu: *"sai, nhưng chưa biết vì thành phần nào"*.

## F4 · `ParentExplanation` — tầng phát ngôn không suy diễn

- Ăn `ConceptSummary` (tất định), chỉ dịch claim → câu tiếng Việt + `EvidenceCitation`
  per-case (`ConceptSummary.observedCaseFacts` thêm cho việc này). Không tính lại gì.
- Decision 5 thi hành: nhóm ca yếu không phân giải được ⇒ nói cả nhóm + "chưa phân
  biệt được"; ca chưa kiểm ⇒ nêu TÊN; cấm chữ "vững" ngoài claim `mastered` (kể cả
  trong câu phủ định — phụ huynh đọc lướt); id nội bộ không lộ ra câu chữ.

## F5 · `ReviewSchedule` — hai câu hỏi, hai chỗ trả lời

| Câu hỏi | Nơi trả lời |
|---|---|
| Claim còn được bảo chứng không? | `ConfidenceFactors.recency` (ADR-004) |
| pMastery có tự tụt theo thời gian? | CHƯA — BKT-forget chờ dữ liệu; bật = đổi policy + replay log (F3 đã có timestamp) |
| Bao giờ đưa bài ôn? | `reviewStateOf` — hình dạng giãn nở SM-2/FSRS |

- Hình dạng (khoảng ôn giãn theo bằng chứng) vào kiến trúc — kết quả tái lặp nhất của
  văn liệu; hằng số vào `ReviewPolicy` có tên + lý do (nền 7 ngày = nhịp tuần học;
  hệ số 2 = đáy bảo thủ dải SM-2; trần 112 ngày < một học kỳ), chờ dữ liệu thật.
- `nothingToReview` tách khỏi `reviewDue`: chưa từng học thì cần HỌC/ĐO, không phải ôn.

## CONSEQUENCE

- `DiagnosticOutcome` 7→8 (`attributionUnresolved`), `LearningAction` +`isolateSkills`;
  `actionFor` vẫn vét cạn (compiler giữ).
- `decide()` đơn-concept GIỮ NGUYÊN cho đường đơn kỹ năng; đường đa kỹ năng đi
  `attributeFailure`. Hợp nhất hai đường là việc của lát cắt Tutor thật, chưa đến.
- Chưa có: trọng số Q-matrix (cần dữ liệu), compensatory model (đo đã: toán nhiều bước
  là conjunctive), BKT-forget (chờ dữ liệu chọn tham số).
