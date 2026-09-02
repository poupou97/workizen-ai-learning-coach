# SAM-PEDAGOGY-ARCHITECTURE-RECOMMENDATION — A/B/C + khuyến nghị B+ (§19/§25.17)

**Ngày:** 2026-09-02 · WAL-99 · research-only, chờ Founder.

## 1. Chấm 3 mức (1-5, cao=tốt; effort cao=đắt)

| Tiêu chí | A: Curriculum+RAG+Prompt | B: Structured Tutor | C: Full Adaptive Engine |
|---|---|---|---|
| Educational value | 2 (theater risk — socratiq-ai) | 4 | 4.5 (biên lợi ích giảm) |
| Complexity | 1 khái niệm nhưng KHÔNG kiểm soát được | 3 | 5 (DKT/IRT/misconception-ML) |
| Data requirements | thấp | vừa (đang có) | LỚN (chưa có; EdNet cấm) |
| Observability/Explainability | 1 — không giải thích được | 5 — mọi quyết định truy vết | 3 — model nặng mờ |
| Effort | thấp | vừa (≈60% ĐÃ BUILT — audit CURRENT-TRUTH) | rất cao |
| Child safety | thấp (không gate cấu trúc) | cao (gate = kiểu dữ liệu) | cao nếu làm đúng, khó audit |
| Maintainability | prompt-drift | tốt (test+đột biến) | kém (retrain, drift) |
| Differentiation | 0 — ai cũng làm được | CAO (provenance+claim-gate: OSS chưa ai có) | cao nhưng không ai thấy khác B |

## 2. KHUYẾN NGHỊ: **B+** — smallest viable learning engine

**B+ = B (đã có ~60%) + 4 bổ sung có evidence, THEO THỨ TỰ:**
1. **Tutor Eval harness tầng 1+2** (deterministic-trên-lineage + scenario bank) — vì nó là
   GATE của mọi thứ khác (WAL-30) và rẻ nhất: đo từ data model sẵn có.
2. **Learning Agenda** (signals→resolve, stop-rest hạng nhất; pattern OpenTutor) — biến các
   mảnh sẵn có (decide/review/timetable) thành «hôm nay làm gì» một chỗ.
3. **forgettingRisk** cho REVIEW lane (FSRS-style, property-tests; KHÔNG đụng pMastery).
4. **TransferProbe** — khái niệm mới duy nhất được phép (gap thật §16-#9).

**Hoãn (chưa build):** misconception-ML (chờ catalog nguồn thật + WAL-49) · DKT/IRT (data
+explainability) · voice (STT trẻ em VN + privacy) · adaptive-difficulty trong-ca ·
learning-velocity/affect-sensing. **Không làm lại:** những thứ REJECTED trong CURRENT-TRUTH.

## 3. Chứng minh flow bắt buộc (§25.19) — chạy trên model HIỆN CÓ + 4 bổ sung
Attempt (2/5+1/3 sai, support=none) → Diagnosis (attributeFailure: ca non-divisible yếu, loại
lỗi=conceptual vì probe nền fail) → Strategy (novice⇒worked-example; nguồn B6 tr.21 EXPLICIT)
→ TeachingAct (workedStep+YOUR_TURN, explainTeaching≠null) → Student action (làm lại đúng,
postHint) → LearningEvidence (đủ lineage) → KnowledgeState (replay; claim vẫn <mastered vì
coverage) → Next (Agenda: TransferProbe ngày mai + review 7d; parent brief 1 câu).
Mọi bước là kiểu dữ liệu ĐÃ TỒN TẠI trừ Agenda/TransferProbe (mục 2).

## 4. §25.20 — hai cực đoan đều bác
Black-box tutor: bác bằng toàn bộ provenance line (không truy vết = không dạy). Provenance-UI
quá nặng: bác bằng bằng chứng tuổi (trẻ lớp 2 không đọc «sourceDemonstrated») — backend
TƯỜNG MINH TỐI ĐA (đã là kiến trúc), frontend qua sourceLineForChild + băng tuổi (WAL-50).

## 5. Trả lời khối FINAL (§22)
**TOP 5 findings:** (1) ~60% «structured tutor» văn liệu đòi hỏi ĐÃ BUILT và đã qua falsification
nội bộ; (2) OSS không có parent-coach thật lẫn provenance sư phạm — differentiation nằm đúng
chỗ SAM đã mạnh; (3) eval đo được KHÔNG CẦN LLM cho tầng 1-2 — premature-answer/hint-strength/
independence-trend đọc thẳng từ lineage; (4) expertise-reversal meta = evidence văn liệu đầu
tiên ỦNG HỘ fading ±1 theo trình độ; (5) scalar mastery bị falsify bằng 4 phản ví dụ (3 đo được).
**TOP 5 patterns adopt:** BKT-pure-function+heuristic-seam (OATutor) · pipeline Seed→Dialogue
→Judge với undecidable (socratic-bench) · is-question/mistake-location metrics (mathtutorbench)
· signals→resolve+stop-rest (OpenTutor) · property-tests cho công thức trí nhớ (OpenTutor).
**TOP 3 repo POC:** socratic-bench methodology (khi tới WAL-30) · OpenTutor agenda-tick ·
mathtutorbench task-registry cho scenario bank.
**TOP 5 must-NOT:** đáp án trước nỗ lực · một-số-mastery cho phụ huynh · misconception bằng
LLM tự do · tối ưu engagement/streak · AI score = điểm chính thức.
**Parent Coach rec:** giữ claim-gate + thêm weekly nudge-brief (evidence EEF) + 10 flows đã spec.
**Student model rec:** giữ multi-view; thêm commonMistakes-catalog (chờ nguồn) + forgettingRisk.
**Tutor eval rec:** 3 tầng như framework; tầng 1 làm TRƯỚC WAL-30.
**Smallest viable engine:** B+ ở mục 2.
**Biggest technical risk:** eval-judge không calibrate được với giáo viên VN (κ thấp).
**Biggest educational risk:** over-scaffolding tạo dependency — ngược mục tiêu tồn tại.
**NOT build yet:** danh sách hoãn mục 2.
**Founder decisions required:** ① duyệt B+ và thứ tự 4 bổ sung; ② nguyên tắc 15 (independence
làm metric số 1); ③ nguồn cho misconception-catalog (SGV? GV cộng tác?); ④ ngưỡng kill #3/#5
(dependency); ⑤ có nâng FSRS thành lịch chính thay SM-2-shape không.
