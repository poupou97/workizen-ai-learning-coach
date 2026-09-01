# Task Order 2026-09-01 — Learner-Contextual UX × Corpus Semantics × Pedagogical Provenance

**Ba lệnh Founder cùng ngày, hội tụ một tầng kiến trúc — trả lời hợp nhất.**
Mã đã ship kèm: lineage LearningEvent · sourceDemonstrated + Method.provenance ·
explainTeaching fail-closed · test no-collapse liên-kết-câu (commit c856856, 184 test).

## 1. BACKLOG AUDIT (§22)

JQL quét onboarding/profile/parent/timetable/session/subject/assessment/essay/age:
liên quan hiện có = WAL-8 (E8), 35/53 (parent, Done), 49 (UX validation), 50 (age),
45/48 (UX foundation/wireframes) + docs/design/* . **KHÔNG có ticket nào** cho: learner
profile/onboarding, multi-child, timetable, LearningSession, subject-shell/surfaces,
assessment mode, essay. ⇒ MỘT Epic mới (E17) + task theo giai đoạn; KHÔNG per-subject/grade.
Provenance (Delta-2) KHÔNG cần epic riêng — đã vá vào E5/E15 hiện có (theo §12 Delta-2).

## 2. LEARNER PROFILE (§1) — ACCEPT, bất biến đã CÓ SẴN trong kiến trúc

Audit: `LearningStage` = VỊ TRÍ chương trình (grade+series+lesson); mastery = evidence-only
(BKT+claim gate). **Grade↔mastery KHÔNG bị couple** — F3 «grade determines mastery» đã
fail sẵn về cấu trúc (không cần sửa gì). BirthYear chưa tồn tại ở đâu ⇒ khi tạo
LearnerProfile: birthYear và curriculumPosition là HAI trường độc lập, grade confirmable/
đổi được. Onboarding V1 tối thiểu: tên gọi + lớp (2 câu hỏi); mọi thứ khác về sau.

## 3. PARENT / MULTI-CHILD (§2) — MODIFY

`learnerId` = **0 lần xuất hiện trong toàn lib/** — chưa có account model nào, cũng chưa
có persistence. ⇒ đúng THỜI ĐIỂM RẺ NHẤT: thiết kế persistence schema với learnerId
first-class NGAY TỪ BẢN ĐẦU (schema là thứ đắt nhất để đổi muộn — luật của chính repo);
UI multi-child SHIP SAU (đồng ý challenge của lệnh: không thuộc MVP-UI). Parent≠learner
đã đúng ở UI hiện tại (chế độ phụ huynh là surface riêng, claim-gated). F11 fail ✅.

## 4. HOME (§3) — kiến trúc hiện tại ĐÃ ĐI ĐÚNG HƯỚNG, không redesign (§25)

Mission Center hiện có = «hôm nay làm gì» chạy từ decide() — KHÔNG phải tool-grid.
Chuỗi LearnerProfile→…→HOME của lệnh chính là pipeline buildDemoMission + decide + review
đã ship. Mở rộng TODAY/COMING-UP/MY-SUBJECTS chỉ có nghĩa khi >1 môn có dữ liệu — gắn vào
E17 sau timetable; KHÔNG lock IA trước WAL-49 (đúng lệnh).

## 5. TIMETABLE (§4) — ACCEPT mô hình tối thiểu; F4 + F13

TimetableEntry{learnerId, weekday, period, subjectId} — đủ. **F4 fail ✅ bằng kiến trúc**:
timetable-môn ≠ bài-cụ-thể; «ngày mai có Toán» chỉ được phép chọn ƯU TIÊN giữa các
next-best-action đã hợp lệ theo LearningStage — KHÔNG sinh dự đoán bài học (dự đoán phải
mang nhãn dự đoán; nguồn tin cậy tương lai: KHDH/teacher input — nối WAL-93). Camera
timetable = tái dùng nguyên PerceptionHypothesis→Confirmed. **F13: onboarding KHÔNG hỏi
timetable** — optional, skip-first; friction thật đo ở WAL-49 (chưa có bằng chứng thì
đứng về phía ít-câu-hỏi).

## 6. LEARNING SESSION (§5-6) — MISSING→CREATE (E17)

Chưa có session model/persistence. Thiết kế: session lưu MỘT lần, các view (ngày/môn/
tri thức) là PROJECTION — khớp triết lý replay hiện có (evidence đã có at/exerciseId ⇒
chiếu được). tutorPolicyVersion đã nằm TRÊN EVENT (vá hôm nay) — session không cần lặp.
Trigger enum giữ ở mức giả thuyết trong ticket.

## 7. TRANSCRIPT ≠ EVIDENCE (§7) — GAP THẬT, ĐÃ VÁ TRONG NGÀY

Audit đúng như Founder nghi: LearningEvent KHÔNG mang assistance level — «đúng sau 1 hint
nhỏ» và «đúng sau xem TRỌN lời giải» đều chỉ là postHintSuccess; tái dựng chỉ bằng đếm
hintRequested đứng trước (mỏng manh, không sống qua ghép phiên). KHÔNG có policyVersion,
KHÔNG có pre/post link. **Vá (commit c856856): support/policyId/priorEventId trên event,
TutorSession phát kèm; test tái dựng ĐÚNG VÍ DỤ NGUYÊN VĂN của lệnh (sai-0 → hint →
đúng-1) + test phân biệt hint-nhỏ vs fullSolution; dữ liệu cũ support=null (không đoán
0). Đột biến đỏ.** F6 fail ✅ (đã có từ trước + nay mạnh hơn trong DỮ LIỆU).

## 8. RETENTION (§8) — nguyên tắc chốt, legal tách riêng

Bậc thang: ảnh camera NGẮN NHẤT (đã có: xoá sau confirm — child-safety doc) < transcript
(giới hạn, F12 challenge chấp nhận: transcript-vĩnh-viễn bị bác — evidence mới là thứ
sống lâu) < interaction events < LearningEvidence (dài) < derived state (replay được).
ADR-006 giữ: không cloud-history mặc định. Câu hỏi pháp lý → WAL-43/child-safety
(LEGAL REVIEW PENDING), không trộn vào kiến trúc.

## 9. SUBJECT FAMILIES & SURFACES (§9-15) — falsify bằng CORPUS

**Bằng chứng corpus 2.202 unit hôm nay:**
- Động từ mở đầu 1.706 EXERCISE (đo): Tìm 119 · Đọc 87 · Chọn 76 · Viết 67 · Tính 44 ·
  Nêu 37 · Đặt 34… ⇒ taxonomy response TỐI THIỂU cho lớp 4-5 Toán+TV:
  SELECT/IDENTIFY (Tìm/Chọn) · NUMERIC/STEP (Tính/Đặt tính) · SHORT_TEXT (Nêu/Trả lời) ·
  COMPOSE (Viết) · READ_RESPOND (Đọc…trả lời). **MCQ-4/MAP/EXPERIMENT/ORAL-độc-lập:
  0 xuất hiện trong corpus này ⇒ CHƯA TẠO TYPE** (NÓI-VÀ-NGHE tồn tại ở TV như SECTION —
  oral là activity, chưa phải exercise-stem). Danh sách 11-type của lệnh: cắt còn 5 + mở
  dần khi corpus chạm môn mới. F-taxonomy: minimize ✅.
- **F1 «mỗi môn một UI» — BÁC**: Tìm/Chọn/Đọc/Viết xuất hiện Ở CẢ Toán lẫn TV ⇒ surface
  dùng chung (Quiz/Select phục vụ LTVC bài 1-3 LẪN Toán Tìm/Chọn). Section nguồn phân
  loại theo TƯƠNG TÁC, không theo môn — đúng giả thuyết §10 của lệnh.
- **F2 «một chat là đủ» — BÁC**: camera/confirm/thang-hint đã vượt chat; VIẾT cần
  workspace nháp; nguồn TỰ tách activity (ĐỌC/VIẾT/NÓI-NGHE/LTVC).
- Kiến trúc: **SHELL + SURFACE COMPOSABLE** (ACCEPT hướng lệnh §9): SAM một persona,
  surface theo activity. V1 surfaces = 3 ĐÃ CÓ (Problem+Step=T1, Camera=C2, Evidence=E1)
  + 2 KẾ (Quiz/Select — phục vụ cả 2 môn từ corpus thật; Reader/Compose-lite cho TV).
  Map/Timeline/Lab: DEFER tới khi corpus chạm Sử/Địa/Lý-Hoá (gate bằng chứng, không bịa).
- **F10 «mỗi môn một chatbot memory» — BÁC**: context = LẮP lúc chạy từ knowledge state
  (learner-global) + curriculum position (subject-longitudinal) + problem state
  (session-local, vứt được) — retrievable, không silo. §14 trả lời xong.
- **F8 «curriculum graph chứa UI» — BÁC MẠNH** (đồng thuận cả 3 lệnh): chuỗi
  Truth → Activity semantics → Resolver → Surface → UI; graph sạch (ADR-008 giữ nguyên).
- **F14 «UI chuyên biệt cần AI nặng» — BÁC**: surface = widget local + pack local
  (27KB curriculum + ~30MB corpus); 0 embedding, 0 vision liên tục.

## 10. EXAM ≠ LEARN (§12, F7) — ACCEPT, thiết kế trong session model

ExamSession = loại session với TutorScope RỖNG CƯỠNG BỨC trong lúc làm + evidence đánh
dấu assessment; phân tích SAU khi nộp. Khớp sẵn ngữ nghĩa support (bài thi ⇒ support=none
tuyệt đối; nhiễm hỗ trợ = vi phạm phát hiện được từ DỮ LIỆU nhờ lineage mới). Không code
trước khi có session model — vào E17.

## 11. ESSAY (§13) — surface COMPOSE, quy trình = REVEAL-gate họ hàng

Corpus TV VIẾT (67 bài «Viết…») + Ghi nhớ cấu-trúc-đoạn (b9/17/27) = nguyên liệu thật.
SAM không viết hộ = cùng fail-closed family với không-lộ-lời-giải-trước-khi-thử.
Evidence từ QUÁ TRÌNH: draft→revise khớp selfCorrection/attempt sẵn có. E17 Ideas.

## 12. AGE-ADAPTIVE (§16, F9) — MERGE vào WAL-50

MỘT design system + PRESENTATION POLICY theo BĂNG lớp (1-2 / 3-5 / THCS / THPT) —
băng, không phải 12 UI. F9 bác hiển nhiên (mật độ chữ tiểu học ≠ THPT); WAL-50 đã đúng
hướng («chế độ gọn THCS») — mở rộng thành policy 4 băng, không ticket mới.

## 13. COMPETITOR (§19) — trích nguyên tắc, không chép giao diện

IXL: thích ứng 2 tầng (item + skill) · skill-plan bám chuẩn/lớp ⇒ khớp curriculum-position.
CK-12 Flexi 2.0: tutor NHÚNG TRONG hoạt động/course (không phải chat rời) + mastery-gap
ước lượng ⇒ khớp SAM-overlay-trên-surface. Seterra/GeoGuessr: map = QUIZ TRÊN KHÔNG GIAN
(select-on-map = SELECT response trên surface Map — củng cố taxonomy tương tác). Timeline
builders: timeline = SEQUENCE response. Điểm SAM khác biệt: claim-gate + provenance sư
phạm (không nhà nào nói «vì sao dạy cách này, nguồn đâu, sách nói hay minh hoạ»).
(Nguồn: ixl.com/math, info.ck12.org/flexi-overview, seterra app — 2026-09.)

## 14. DELTA-1 CORPUS SEMANTICS — trả lời từng mục

§1 Phân bố (đếm): Toán 803 EX/216 ST/26 RULE/7 EXAMPLE/1 CAND · TV 903 EX/230 ST/16 RULE.
SECTION_TEXT ≈20% = UNKNOWN trung thực. TABLE/FIGURE: OCR dòng-chữ KHÔNG THẤY bảng/hình ⇒
không tạo type khi chưa có năng lực trích (không thêm type để đẹp danh sách). DEFINITION:
chưa tách được khỏi RULE bằng marker đo được — để ngỏ.
§2 EXPLICIT/DEMONSTRATED/INFERRED: **VÀO CANONICAL MODEL** — KnowledgeOrigin.sourceDemonstrated
(mới) + assertion trong extractor + map=INFERRED. Demonstrated ≠ stated giữ bằng test.
§3 Cạnh xuyên lớp: **REMEDIATION như nhãn content-graph — BÁC**. Corpus chỉ chứng minh
RE-EXPOSURE (cả hai nguồn ĐỀU DẠY). Kiến trúc hiện tại ĐÃ đúng hướng lệnh: remediationFor
là hàm RUNTIME từ mastery+goal — pedagogical intent không nằm trong content truth.
Nhãn cạnh content giữ tối thiểu: TEACHES (+ sourceSequence cho thứ tự).
§4 Exercise semantics: xem §9 trên (đo động từ; tách truth→semantics→resolver→surface).
§5 Liên-kết-câu: **KHÔNG có collapse-gap** — test mới chứng minh coverage chặn «vững
liên kết câu» khi dùng-khi-viết chưa quan sát, và NÊU ĐÍCH DANH demand thiếu. Gap là
CONTENT (case catalogue TV chưa dựng), không phải kiến trúc.
§6 Subject adapter: **shared framework + adapter/môn** — universal extractor ĐÃ BỊ BÁC
bằng đo (TV fail-closed); pipeline độc lập bị bác vì 70% logic chung (OCR/flush/stem/strip).
§7 Scale gate: CHƯA QUA — checklist: provenance-per-unit ✅ · leak xuyên-sách ✅ (ad-hoc,
cần thành test tự động) · EXERCISE→case ❌ (batch ④) · explicit/demonstrated ✅ ·
adapter ✅ (2 môn) · activity/evidence ✅ · ca Toán+TV ✅. Điều kiện scale: đóng 2 ô ❌.

## 15. DELTA-2 PROVENANCE — trạng thái sau vá hôm nay

Chuỗi §3 audit: Source→Unit (✅ id+trang+assertion) → Concept (✅ map INFERRED 25/27,
unmapped giữ unmapped — §9 Delta-2 khen đúng hành vi này) → **Method (✅ MỚI:
Provenance? trên TeachingMethod)** → TutorScope (✅ APPLICABLE∩ALLOWED + MethodRejection
có lý do) → TeachingAct/phát ngôn (✅ MỚI: explainTeaching, fail-closed F2/F7) →
Evidence (✅ MỚI: support/policyId/priorEventId). Versions: sourceId+policyId+bake-at-write
phủ F8-replay. **Metrics §11**: thêm vào bộ WAL-63/41 khi chạy batch ④: support-type
correctness + method-attribution + unsupported-teaching-claim (UNKNOWN hợp lệ).
Ca «nguồn mâu thuẫn» (F5): chưa gặp trong corpus — ghi chờ, không bịa cơ chế trước.

## 16. MA TRẬN INTERACTION SURFACE (§20) — hàng đại diện, từ ca THẬT

| Môn × mục tiêu | Activity | Response | Surface | TeachingAct | Evidence | Băng |
|---|---|---|---|---|---|---|
| Toán × cộng phân số khác mẫu (B6-L5, nguồn EXPLICIT tr.21) | guided practice | STEP | Problem+Step (T1 ✅) | probe/hint±1/YOUR_TURN | independent/postHint+support | 3-5 |
| Toán × quy đồng (B57-L4, nguồn DEMONSTRATED tr.62) | worked example | STEP | Problem+Step + nguồn «SAM làm theo ví dụ…» | model→fade | guided→independent | 3-5 |
| Toán × nhận dạng ca (camera) | intake | — | Camera+Confirm (C2 ✅) | ADMIT_UNCERTAINTY | cp:/man: | 3-5 |
| TV × liên kết câu — nhận biết (b9 bt3) | identify | SELECT | Quiz/Select (KẾ) | probe | independent per-case | 3-5 |
| TV × liên kết câu — dùng khi viết (b9 bt4) | compose | COMPOSE | Compose-lite (KẾ) | critique→revise | selfCorrection/attempt case riêng | 3-5 |
| TV × đọc hiểu (ĐỌC) | read-respond | SHORT_TEXT | Reader | ask-evidence | independent | 3-5 |
| AI (QĐ2422 7.A1.MR1) × kiểm chứng AI | verification task | SHORT_TEXT | Quiz/Reader | ASK-FOR-VERIFICATION (=probe param) | independent | THCS |
| Ôn tập (review due) | retrieval | NUMERIC/SELECT | Quiz | none-first | independent (lịch F5) | mọi băng |

## 17. FALSIFIED F1–F14 (UX-order) — một dòng mỗi cái

F1 BÁC (surface chung đo được) · F2 BÁC (nguồn tự tách activity) · F3 fail-sẵn (cấu trúc)
· F4 fail-bằng-thiết-kế (ưu-tiên-hoá, không dự-đoán-bài) · F5 fail-sẵn (hintRequested
không vào mastery; transcript≠evidence) · F6 fail-sẵn + mạnh hơn (lineage) · F7 ACCEPT-
tách (exam = scope rỗng cưỡng bức) · F8 BÁC MẠNH (resolver layer) · F9 BÁC (băng lớp) ·
F10 BÁC (context lắp runtime) · F11 fail-sẵn (parent surface riêng) · F12 BÁC transcript-
vĩnh-viễn (bậc thang retention) · F13 timetable optional-skip (đo thật ở WAL-49) ·
F14 BÁC (local pack + widget, 0 compute nặng).

## 18. ADR? (§24)

**KHÔNG ADR mới.** sourceDemonstrated/Method.provenance/lineage = mở rộng tự nhiên của
ADR-004/005 + Provenance model (đã ghi trong code + doc này); shell/surface = research
chưa tới độ chín quyết định (ADR khi build surface đầu tiên). Đúng lệnh: không ADR chỉ
vì có nghiên cứu.
