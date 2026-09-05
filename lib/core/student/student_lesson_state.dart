/// ⭐ WAL-210 round 3 (A-runtime) — STUDENT LESSON STATE: trạng thái tri thức
/// của trẻ về MỘT BÀI, suy TẤT ĐỊNH từ log thô theo lineage (cùng hàm với
/// Learning Map / Parent — ONE EVIDENCE TRUTH, MULTIPLE PROJECTIONS).
///
/// Là đầu vào «Student State» của Pedagogy Runtime (A7) và Next Best Learning
/// Action (A8). Cố ý NHỎ: không phút, không phần trăm, không mastery bịa —
/// chỉ những gì tính được từ sự kiện có lineage. Bài không phát sự kiện nào
/// (Track B, `EvidencePolicy.none`) ⇒ `unseen` — đúng sự thật.
///
/// ⭐⭐ ROUND 4 (Founder §4): đọc dưới luật SIẾT mặc định — `mapState` và
/// [hasApprovedValidatedSuccess] chỉ từ sự kiện có dấu validator được duyệt.
/// Dữ liệu cũ có chấm-không-dấu được ĐẾM RIÊNG ([historicalUnvalidatedCount])
/// để Next Action / Lane B nói thật «có lần làm được ghi nhận trước hợp đồng
/// mới — chưa được kiểm», thay vì im lặng hoặc nói «tự làm được».
library;

import '../curriculum/semantic_binding.dart' show LessonRef;
import 'learning_evidence.dart';
import 'learning_map_state.dart';

/// ⭐ ROUND 4 — «đứng ở đâu» về bằng chứng của MỘT bài, cho luật A8 và cho
/// Lane B kể lại. Ba giá trị, không số, không phần trăm.
enum LessonEvidenceStanding {
  /// Không sự kiện nào khớp lineage của bài.
  none,

  /// Có sự kiện (tự báo / học cùng SAM / dữ liệu cũ có chấm-không-dấu) nhưng
  /// KHÔNG có lần tự-làm-đúng nào mang dấu validator được duyệt —
  /// «đã tham gia nhưng chưa được kiểm».
  participatedUnverified,

  /// Có ít nhất một lần tự-làm-đúng ĐÃ KIỂM (validator đăng ký).
  validated,
}

class StudentLessonState {
  const StudentLessonState({
    required this.lessonRef,
    required this.mapState,
    this.eventCount = 0,
    this.hasApprovedValidatedSuccess = false,
    this.participationCount = 0,
    this.historicalUnvalidatedCount = 0,
    this.validatedSuccessCount = 0,
  });

  final LessonRef lessonRef;

  /// Cùng bốn trạng thái trẻ thấy trên Learning Map (luật siết mặc định).
  final LearningMapState mapState;

  /// Số sự kiện khớp lineage của bài (để nói «chưa có gì ghi lại» trung thực).
  final int eventCount;

  /// ⭐ A3: có ít nhất một lần tự-làm-đúng mang DẤU validator được duyệt.
  /// Đây là thứ DUY NHẤT A8 dùng để đề xuất «sang bài tiếp» — không phải
  /// participation, không phải dữ liệu cũ không dấu.
  final bool hasApprovedValidatedSuccess;

  /// Số sự kiện TỰ BÁO / hoàn thành (không chấm).
  final int participationCount;

  /// ⭐ ROUND 4: số sự kiện CÓ CHẤM nhưng KHÔNG DẤU (trước hợp đồng A3 /
  /// emitter chưa đóng dấu). Giữ trong lịch sử, không tính là năng lực.
  final int historicalUnvalidatedCount;

  /// Số lần tự-làm-đúng ĐÃ KIỂM (chỉ để nói «đã có», không phải điểm).
  final int validatedSuccessCount;

  bool get hasAnyEvidence => eventCount > 0;
  bool get isUnseen => mapState == LearningMapState.unseen;
  bool get hasParticipation => participationCount > 0;
  bool get hasHistoricalUnvalidated => historicalUnvalidatedCount > 0;

  /// ⭐ ROUND 4 — vị thế bằng chứng của bài (xem [LessonEvidenceStanding]).
  LessonEvidenceStanding get standing => hasApprovedValidatedSuccess
      ? LessonEvidenceStanding.validated
      : hasAnyEvidence
          ? LessonEvidenceStanding.participatedUnverified
          : LessonEvidenceStanding.none;

  /// ⭐ ROUND 4 — câu TRUNG THỰC về bằng chứng của bài, cho trẻ/phụ huynh
  /// đọc dưới đề xuất. `null` khi không có gì đáng nói (chưa học, hoặc đã
  /// kiểm — R1 tự nói). Không số, không phần trăm, không «đúng/sai».
  String? get evidenceNote => switch (standing) {
        LessonEvidenceStanding.none => null,
        LessonEvidenceStanding.validated => null,
        LessonEvidenceStanding.participatedUnverified => hasHistoricalUnvalidated
            ? 'Có lần làm được ghi nhận trước hợp đồng mới — SAM chưa kiểm '
                'lại nên chưa tính là tự làm được.'
            : mapState == LearningMapState.participation
                ? 'SAM ghi nhận con đã tham gia bài này, chưa chấm phần nào.'
                : 'Con đã học cùng SAM ở bài này — chưa có lần tự làm được '
                    'nào được kiểm.',
      };

  /// Hàm THUẦN trên toàn bộ sự kiện của learner — lineage tự lọc đúng bài.
  static StudentLessonState fromEvents(
      LessonRef ref, Iterable<LearningEvent> allEvents) {
    final matching = allEvents
        .where((e) =>
            e.sourceDocumentId == ref.sourceDocumentId &&
            e.lessonNo == ref.lessonNo)
        .toList();
    var participation = 0, historical = 0, validated = 0;
    for (final e in matching) {
      switch (e.readClass) {
        case EvidenceReadClass.participation:
          participation++;
        case EvidenceReadClass.historicalUnvalidated:
          historical++;
        case EvidenceReadClass.validatedCompetence:
          if (e.isValidatedIndependentSuccess) validated++;
        case EvidenceReadClass.rejectedValidation:
        case EvidenceReadClass.unscored:
          break;
      }
    }
    return StudentLessonState(
      lessonRef: ref,
      mapState: learningMapStateFor(
          sourceDocumentId: ref.sourceDocumentId,
          lessonNo: ref.lessonNo,
          allEvents: matching),
      eventCount: matching.length,
      hasApprovedValidatedSuccess: validated > 0,
      participationCount: participation,
      historicalUnvalidatedCount: historical,
      validatedSuccessCount: validated,
    );
  }

  /// Trạng thái «chưa có gì» cho một bài — dùng khi không có kho.
  static StudentLessonState unseen(LessonRef ref) =>
      StudentLessonState(lessonRef: ref, mapState: LearningMapState.unseen);
}
