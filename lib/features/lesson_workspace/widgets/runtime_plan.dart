/// ROUND 3 — cầu nối Lane B ↔ Lane A-runtime (PR #69, contracts A6/A7/A8).
///
/// Workspace không có kho, không có learner state từ sự kiện — nên Student
/// State ở đây LUÔN là `unseen` (đúng sự thật: bài này không phát sự kiện
/// nào, `EvidencePolicy.none`). Context được giải ra ĐÚNG bài (sách + số bài)
/// để runtime ràng buộc được binding; `learnerId` thật khi tầng trên có, còn
/// không thì là hằng [noLearnerId] — context này KHÔNG BAO GIỜ đi vào một sự
/// kiện học (runtime không phát `LearningEvent`, `validator` luôn `null`).
///
/// Lane B chỉ TIÊU THỤ `RuntimePlan` / `LessonNextAction` — không tự dựng
/// `PlannedStep`, không tự dựng `EvidenceValidation` (hợp đồng A7.2/A7.3).
library;

import '../../../core/agenda/lesson_next_action.dart';
import '../../../core/context/learning_context.dart';
import '../../../core/curriculum/semantic_binding.dart'
    show LessonRef, SemanticBinding;
import '../../../core/curriculum/semantic_binding_registry.dart';
import '../../../core/lesson_model/lesson_document.dart';
import '../../../core/lesson_model/next_action.dart';
import '../../../core/pedagogy/pedagogy_runtime.dart';
import '../../../core/student/student_lesson_state.dart';

/// Mã learner khi workspace được mở mà không có hồ sơ (test / đường cũ).
/// Không có bằng chứng nào mang mã này — workspace không ghi gì.
const noLearnerId = 'workspace-no-learner';

LessonRef lessonRefOf(LessonDocument doc) => LessonRef(doc.book, doc.lessonNo);

LearningContext learningContextFor(LessonDocument doc, {String? learnerId}) =>
    LearningContext(
      learnerId: learnerId ?? noLearnerId,
      grade: doc.grade,
      subject: doc.subject,
      sourceDocumentId: doc.book,
      lessonNo: doc.lessonNo,
    );

/// Kế hoạch runtime cho kịch bản của bài — `null` khi bài không có kịch bản.
RuntimePlan? planForDoc(LessonDocument doc, {String? learnerId}) {
  final script = doc.tutorScript;
  if (script == null) return null;
  final ref = lessonRefOf(doc);
  return PedagogyRuntime.planForScript(
    script: script,
    binding: SemanticBindingRegistry.resolveFor(
      ref,
      SemanticBinding.tutorScriptActivity,
    ),
    studentState: StudentLessonState.unseen(ref),
    context: learningContextFor(doc, learnerId: learnerId),
    blockText: (id) {
      final b = doc.blockById(id);
      return b == null ? null : LessonDocument.textOf(b);
    },
  );
}

/// «SAM đề xuất» theo thứ tự Founder A8 (Đọc → Trực quan → Học với SAM) —
/// thay luật prototype «có sơ đồ ⇒ Trực quan trước» của `nextActionFor`.
/// Trả về [NextAction] để thẻ đề xuất / màn chọn cách học dùng chung.
NextAction founderNextAction(
  LessonDocument doc, {
  required Set<WorkspaceView> seen,
  String? learnerId,
}) {
  final ref = lessonRefOf(doc);
  final a = nextBestLessonAction(
    state: StudentLessonState.unseen(ref),
    context: learningContextFor(doc, learnerId: learnerId),
    lesson: LessonSummary.fromDocument(doc),
    viewsSeen: seen,
  );
  return NextAction(view: a.view, reason: a.reason, basis: '${a.rule} · ${a.basis}');
}
