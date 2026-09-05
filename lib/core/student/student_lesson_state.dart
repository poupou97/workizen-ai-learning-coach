/// ⭐ WAL-210 round 3 (A-runtime) — STUDENT LESSON STATE: trạng thái tri thức
/// của trẻ về MỘT BÀI, suy TẤT ĐỊNH từ log thô theo lineage (cùng hàm với
/// Learning Map / Parent — ONE EVIDENCE TRUTH, MULTIPLE PROJECTIONS).
///
/// Là đầu vào «Student State» của Pedagogy Runtime (A7) và Next Best Learning
/// Action (A8). Cố ý NHỎ: không phút, không phần trăm, không mastery bịa —
/// chỉ những gì tính được từ sự kiện có lineage. Bài không phát sự kiện nào
/// (Track B, `EvidencePolicy.none`) ⇒ `unseen` — đúng sự thật.
library;

import '../curriculum/semantic_binding.dart' show LessonRef;
import 'learning_evidence.dart';
import 'learning_map_state.dart';

class StudentLessonState {
  const StudentLessonState({
    required this.lessonRef,
    required this.mapState,
    this.eventCount = 0,
    this.hasApprovedValidatedSuccess = false,
  });

  final LessonRef lessonRef;

  /// Cùng bốn trạng thái trẻ thấy trên Learning Map.
  final LearningMapState mapState;

  /// Số sự kiện khớp lineage của bài (để nói «chưa có gì ghi lại» trung thực).
  final int eventCount;

  /// ⭐ A3: có ít nhất một lần tự-làm-đúng mang DẤU validator được duyệt.
  /// Đây là thứ DUY NHẤT A8 dùng để đề xuất «sang bài tiếp» — không phải
  /// participation, không phải dữ liệu cũ không dấu.
  final bool hasApprovedValidatedSuccess;

  bool get hasAnyEvidence => eventCount > 0;
  bool get isUnseen => mapState == LearningMapState.unseen;

  /// Hàm THUẦN trên toàn bộ sự kiện của learner — lineage tự lọc đúng bài.
  static StudentLessonState fromEvents(
      LessonRef ref, Iterable<LearningEvent> allEvents) {
    final matching = allEvents
        .where((e) =>
            e.sourceDocumentId == ref.sourceDocumentId &&
            e.lessonNo == ref.lessonNo)
        .toList();
    return StudentLessonState(
      lessonRef: ref,
      mapState: learningMapStateFor(
          sourceDocumentId: ref.sourceDocumentId,
          lessonNo: ref.lessonNo,
          allEvents: matching),
      eventCount: matching.length,
      hasApprovedValidatedSuccess: matching.any(
          (e) => e.isValidatedIndependentSuccess && e.hasApprovedValidation),
    );
  }

  /// Trạng thái «chưa có gì» cho một bài — dùng khi không có kho.
  static StudentLessonState unseen(LessonRef ref) =>
      StudentLessonState(lessonRef: ref, mapState: LearningMapState.unseen);
}
