# SAM-MULTI-ROLE-FAMILY-CLASSROOM-RESEARCH — 4 vai trò, một Learning Truth, QR linking

**Ngày:** 2026-09-02 · Task Order Multi-Role · research-only (§28: không gián đoạn P0, không implement).

## 1. Audit truth hiện tại (những gì ĐÃ tồn tại — §29.1)

| Mảnh | Trạng thái |
|---|---|
| One-Truth→Projections | ⭐ ĐÃ LÀ KIẾN TRÚC và vừa được falsify đứng vững (§25.9, PARENT-COACH doc §3): Student view (Mission/T1/E1) + Parent view (Tối-nay claim-gated) đọc CÙNG ConceptSummary — cùng truth, khác projection, có test |
| Identity | PARTIAL: LearnerProfile{learnerId, guardianId?} — guardian là MỘT string; User≠Learner đã đúng (F11-cũ fail sẵn) |
| GuardianRelationship n-n / Class / Enrollment / TeacherAssignment | ❌ MISSING toàn bộ |
| Camera→Assessment flow (PHASE F của order) | ⭐ PHẦN LỚN ĐÃ BUILT — order dường như chưa biết: IMAGE→PerceptionHypothesis→LEARNER CONFIRMATION→CanonicalProblem→evidence ĐANG CHẠY có test; exam-mode + tutoringViolationsInExam đã có; thiếu: error-analysis sâu trong-ca (= WS-B của P0 pedagogy, đã spec) |
| AI score ≠ official grade | nền đã đúng hướng: văn KHÔNG chấm đúng/sai (correct=null, test); claim-gate; thiếu: khái niệm «suggested feedback theo rubric» cho tự luận |
| Teacher (bộ môn/GVCN) | ❌ MISSING hoàn toàn — và OSS audit cho thấy không có mẫu để chép (open-tutor-ai-CE không có parent; classroom-intelligence thật chưa thấy ở đâu) |
| QR / device pairing | ❌ MISSING |
| Authorization | ❌ MISSING (app 1 máy local-first hiện chưa cần — sẽ cần khi có teacher/cloud-link) |

## 2. Falsify sơ đồ Founder + 18 câu F (nén, mỗi câu một verdict)

Sơ đồ 4-role/3-phía: **ĐỨNG VỮNG về ngữ nghĩa** với 1 chỉnh: «NHÀ TRƯỜNG» không phải node dữ
liệu — là NGỮ CẢNH QUAN HỆ (Class/TeacherAssignment); truth vẫn một, không có «school truth» riêng.

F1 (4 UX riêng?): 4 CÂU HỎI HOME khác nhau là thật ⇒ 4 home-projection; nhưng KHÔNG phải 4 app-UI
độc lập — shell + role-projection (giống surface composable). F2 (mấy app?): MỘT app cho
Student+Parent (đã vậy); Teacher = SAU, có thể web — quyết khi tới phase, không khoá.
F3 (chiều QR parent-child): hypothesis Founder (child scan parent) BỊ NGHIÊNG-BÁC: trẻ nhỏ
không đánh giá được «đây có phải mẹ mình» về mặt consent; **OPTION C thắng cho MVP**: parent
tạo LearnerProfile trước rồi pairing thiết-bị-của-trẻ bằng QR — khớp luôn kiến trúc
parent-managed hiện tại + không cần trẻ có account (F13 giải luôn: recovery qua guardian).
Option A/B giữ cho ca trẻ-đã-dùng-trước. F4 (QR > code?): CÓ cho trẻ (không gõ), code/deep-link
là fallback bắt buộc (máy không camera / QR hỏng). F5 (permanent QR): **BÁC** — chỉ
purpose-specific invitation {purpose, issuer, nonce, expiry, maxUses, revocable, confirm};
không encode userId trần. F6 (GVCN xem gì): MINIMUM NECESSARY = aggregate cross-subject
(«Toán: cần chú ý») + trend; KHÔNG raw per-subject detail mặc định. F7/F8 (teacher/parent xem
transcript?): KHÔNG mặc định — Evidence ≠ Transcript đã là bất biến; transcript thuộc tầng
retention ngắn + private; escalation cụ thể mới mở theo policy. F9 (AI score bị hiểu nhầm):
RỦI RO THẬT — thuốc: không hiển thị «điểm», chỉ claim-gated statements + «góp ý theo rubric»
cho tự luận; deterministic (MCQ/numeric) được chấm đúng/sai nhưng vẫn không phải điểm chính
thức. F10 (teacher input đáng tin mãi?): KHÔNG — teacher-confirmed position là NGUỒN TIN CẬY
CÓ THỜI HẠN + provenance (đúng khuôn KnowledgeOrigin: thêm nguồn «teacherStated» tương lai);
giải đúng bài TIMETABLE≠LESSON (F4 cũ). F11 (một truth đủ?): ĐÃ CHỨNG MINH bằng 2 role đang
chạy. F12 (backend phức tạp?): local-first một-máy hiện tại chưa cần authz server; teacher
phase mới cần — đó là lý do MVP không có teacher. F14 (nhiều guardian): GuardianRelationship
n-n với authority level; consent = guardian có authority-primary; ly hôn/chia quyền = policy
per-relationship — model chứa được, luật cụ thể là LEGAL REVIEW PENDING. F15 (QR bị share):
expiry ngắn + maxUses + teacher-confirm từng enrollment + revoke. F16 (scan nhầm lớp): bước
xác nhận hiển thị «TOÁN 5A1 — Cô Lan» trước khi join + teacher approve + leave dễ. F17
(teacher rời): TeacherAssignment có lifecycle (§18 order) — REVOKE cắt quyền đọc ngay, dữ
liệu evidence KHÔNG đi theo giáo viên. F18 (nhiều con nhiều trường): Parent Home = danh sách
learner (switch context — đã thiết kế trong WAL-94), Class gắn theo learner không theo parent.

## 3. Identity model TỐI THIỂU đề xuất (conceptual — không khoá schema)

UserAccount(authn) —— GuardianRelationship{guardianUserId, learnerId, authority, status,
lifecycle} n-n —— LearnerProfile (đã có; bỏ dần guardianId đơn khi có relationship) ——
Enrollment{learnerId, classId, status} —— Class{school?, grade, subjectContext} ——
TeacherAssignment{teacherUserId, classId, subjectId|homeroom, status}. QRInvitation
{purpose, issuerId, nonce, expiresAt, maxUses, revoked} — MỘT scanner, purpose trong payload
đã ký (§16 order); **SCAN ≠ AUTHORIZATION** (§17): quan hệ chỉ tạo sau validate+confirm.

## 4. Bốn Home = 4 câu hỏi (đưa vào backlog, không design UI)
Student «hôm nay học gì» (ĐÃ CÓ) · Parent «con học gì, tôi giúp thế nào» (ĐÃ CÓ V0) ·
SubjectTeacher «lớp hiểu tới đâu, tiết sau dạy lại gì» (classroom intelligence: phân bố claim
+ lỗi phổ biến từ misconception-catalog khi có + danh sách chưa-đủ-evidence nói thật) ·
Homeroom «ai/môn nào cần tôi quan tâm» (aggregate + change-detection, minimum-necessary).

## 5. Phasing — phản biện thứ tự Founder (§25)
GỘP A+B (identity+family onboarding — LearnerProfile đã có nửa); **F chuyển lên sớm nhất vì
ĐÃ BUILT phần lớn** (chỉ còn error-analysis = P0 pedagogy WS-B); D (QR) TRƯỚC C (teacher cần
QR class-invite; nhưng parent-pairing cần trước nữa); E chạy song song mỗi phase. Thứ tự đề
xuất: **[A+B] → F(hoàn thiện) → G(parent nâng cấp) → D(QR parent-pairing) → C+D(class QR)
→ H → I**. MVP (§26): **phương án A — Student+Parent** (thắng: user value tự đứng, không
network-dependency, không school-adoption barrier, evidence quality đã có; teacher = cold-start
+ authz server + GTM khác hẳn — phase sau khi có dữ liệu thật đáng cho giáo viên xem).

## 6. KHÔNG build bây giờ
Teacher UX/authz server · QR infra · school SSO · classroom aggregation — TRUTH ĐÃ GHI để
thiết kế sau không lệch; constraint đã gắn vào ticket đang sống (WAL-95/96 comments).

## 7. Founder decisions cần chốt sau
① MVP = Student+Parent? ② Option C pairing làm mặc định? ③ authority model đa-guardian
(pháp lý VN — REVIEW PENDING) ④ teacher input = KnowledgeOrigin.teacherStated mới hay
provenance hiện có đủ ⑤ ngưỡng minimum-necessary cho GVCN.
