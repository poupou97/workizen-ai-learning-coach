# SCREEN FLOW MATRIX — entry/context/exit (Task Order §21.E)

Định dạng: Screen → entry · context cần · actions · exit.

- **Home**: entry app-start/switch-profile · cần LearnerProfile+Agenda(recompute) ·
  actions: intent chip, đề xuất, tiếp tục, đổi người học · exit → Subject/Camera/Tutor/Parent-tile.
- **Subject Home**: entry Home/Subjects · cần position(curriculum-structure)+ConceptSummary ·
  exit → Lesson browser/Tutor/Review/Map.
- **Camera**: entry Home chip «Làm bài»/Subject · cần activeLearner XÁC ĐỊNH (fail-closed §26.7) ·
  exit → Confirm (bắt buộc, không đường tắt).
- **Confirm**: cần PerceptionHypothesis · actions confirm/sửa/chụp lại · exit → Tutor Start
  (ConfirmedProblem) — UNCONFIRMED không có exit nào khác vào learning.
- **Tutor Start**: cần TutorScope+TeachingProvenance (null ⇒ màn «SAM chưa chắc» fail-closed) ·
  exit → Diagnostic (intent Làm bài) / Explain (intent Học trước).
- **Workspace/Hint/YourTurn**: cần TutorSession · mỗi action phát đúng 1 LearningEvent ·
  exit → Success (finalCorrectness) / thoát giữa chừng = session lưu dở («Tiếp tục học» Home).
- **Success**: cần TutorOutcome+feedbackFor · exit → next action (Agenda) / Why Method / Home.
- **Why/Source**: cần TeachingProvenance đã render · entry TỪ MỌI TeachingAct (F22: NO —
  provenance available từ đầu, đây chỉ là màn đào sâu) · exit quay lại.
- **Quiz**: cần activity pool · hint cho phép, ghi hintRequested · exit → kết quả nhẹ + Agenda.
- **Assessment Start→Mode→Result**: cần profile-confirm + AssistancePolicy.assessment ·
  trong bài: KHÔNG hint/reveal; thoát giữa chừng = nộp dở có ghi chú · exit → Result → remediation.
- **Review**: cần reviewStateOf list · exit → Tutor/Quiz đúng ca.
- **Learning Map**: cần ConceptClaim per concept + coverage · exit → node → Subject/Lesson.
- **Parent Home/Detail/Family**: entry Parent Mode (PIN) · cần Parent Projection
  (claim-gated) · KHÔNG đường nào từ Parent Mode phát LearningEvidence.
- **Sessions/Progress**: projection từ store — read-only.
- **Voice**: entry contextual (nút mic) — KHÔNG tab riêng cấp 1 · cần activeLearner + scope
  như tutor · exit về surface gọi nó.
- **Library**: entry «Thêm» · 5 khu A-E · exit → Reader/Tutor với nguồn gắn nhãn đúng loại.
- **Notifications/Settings**: theo role/mode; child thấy bản child-safe.
