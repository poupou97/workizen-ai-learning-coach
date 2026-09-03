/// WAL-164 — REVIEW PRIORITY RESOLVER (quyết định Founder D2, 2026-09-03).
///
/// ⭐⭐ BẤT BIẾN: **CÂU SAI SINH BẰNG CHỨNG, KHÔNG TỰ ĐỘNG THÀNH BÁO ĐỘNG.**
///
/// Câu hỏi mở ở WAL-143: con vừa làm sai một câu mà màn Hôm nay vẫn nói «nghỉ
/// ngơi nhé». Founder không chọn A (bỏ qua tới lịch 7 ngày — quá điếc) cũng
/// không chọn B (mọi lỗi thành urgent — quá ồn, và biến mỗi sai sót thành báo
/// động). Đường đi bắt buộc là:
///
///     WRONG ANSWER → LearningEvidence → ReviewCandidate → Resolver
///
/// Tầng này là bảng luật ĐẶT MỘT CHỖ, tất định, kiểm thử được. UI đọc kết quả
/// và câu chữ đi kèm — KHÔNG tự suy từ một câu sai.
///
/// Không thay `reviewStateOf` (lịch giãn cách) mà PHỦ LÊN nó: lịch trả lời
/// «tới hạn chưa», resolver trả lời «có gì đáng đưa lên trước không».
library;

import '../student/mastery.dart';
import '../student/review_schedule.dart';
import 'error_hypothesis.dart';

/// Mức ưu tiên ôn. Thứ tự tăng dần — `today` là mức DUY NHẤT được phép chiếm
/// chỗ trên màn Hôm nay.
enum ReviewPriority { none, normal, nearTerm, elevated, today }

class ReviewCandidate {
  const ReviewCandidate({
    required this.skillCaseId,
    required this.priority,
    required this.reason,
    required this.becauseOfError,
    this.dueBy,
  });

  final String skillCaseId;
  final ReviewPriority priority;

  /// Câu đọc được, do resolver sở hữu. UI hiển thị chứ không tự chế — nếu UI
  /// tự viết thì luật lại nằm ở UI, đúng thứ D2 cấm.
  final String reason;

  /// ⭐ `false` khi ứng viên KHÔNG đến từ một lỗi (ví dụ: đúng-nhờ-trợ-giúp).
  /// Để UI không bao giờ gọi một lần làm được là «sai».
  final bool becauseOfError;

  /// Mốc nên gặp lại. `null` = theo lịch giãn cách sẵn có.
  final DateTime? dueBy;
}

/// Ngưỡng CÓ TÊN, có lý do, thay được (ADR-004). Giả thuyết V1.
class ReviewPriorityPolicy {
  const ReviewPriorityPolicy({
    this.nearTermWindow = const Duration(days: 2),
    this.slipCorrectTolerance = 2,
    this.repeatThreshold = 2,
  });

  /// Founder D2 nói dải 1–3 ngày; lấy GIỮA dải, có tên để chỉnh sau khi có
  /// dữ liệu thật (WAL-49) chứ không rải số 2 trong mã.
  final Duration nearTermWindow;

  /// Bao nhiêu lần TỰ LÀM ĐÚNG thì một lần sai lẻ được coi là sơ suất.
  /// Đứa trẻ làm đúng nhiều lần rồi sai một câu thì đó là con người, không
  /// phải lỗ hổng kiến thức.
  final int slipCorrectTolerance;

  /// Bao nhiêu bằng chứng cùng hướng thì gọi là hiểu sai LẶP LẠI.
  final int repeatThreshold;
}

/// ⭐ Bảng luật. Tất định: cùng đầu vào + cùng mốc thời gian ⇒ cùng kết quả.
///
/// [uncertainMappingCaseIds] — ca mà việc gán bài↔dạng còn mơ hồ (OCR đoán,
/// dạng chưa nhận ra). FAIL CONSERVATIVE: không nâng mạnh, vì nâng ưu tiên
/// dựa trên một phép gán sai là bắt trẻ ôn thứ nó không hề làm sai.
///
/// [prerequisiteCaseIds] — tiền đề mà BÀI ĐANG HỌC cần tới. Chỉ ca nào ĐÃ có
/// bằng chứng mà đang yếu mới được lên Hôm nay; chưa học thì đó là việc HỌC,
/// không phải việc ÔN.
List<ReviewCandidate> resolveReviewCandidates({
  required ConceptMastery mastery,
  required DateTime now,
  List<ErrorHypothesis> hypotheses = const [],
  Set<String> prerequisiteCaseIds = const {},
  Set<String> uncertainMappingCaseIds = const {},
  ReviewPriorityPolicy policy = const ReviewPriorityPolicy(),
  ReviewPolicy schedule = const ReviewPolicy(),
}) {
  final out = <ReviewCandidate>[];
  final ids = mastery.cases.keys.toList()..sort(); // tất định

  for (final id in ids) {
    final c = mastery.cases[id]!;
    final state = reviewStateOf(c, now, policy: schedule);

    // Chưa có bằng chứng độc lập nào ⇒ KHÔNG có gì để ôn. Gửi bài ôn cho thứ
    // chưa từng học là gộp hai việc khác nhau.
    if (state.urgency == ReviewUrgency.nothingToReview &&
        c.supportedCount == 0) {
      continue;
    }

    // ① MAPPING KHÔNG CHẮC ⇒ fail conservative. Đặt TRƯỚC mọi luật nâng.
    if (uncertainMappingCaseIds.contains(id)) {
      out.add(ReviewCandidate(
        skillCaseId: id,
        priority: ReviewPriority.normal,
        becauseOfError: false,
        reason: 'SAM chưa chắc bài đó thuộc dạng nào nên không dám xếp gấp — '
            'cứ ôn theo lịch bình thường.',
        dueBy: state.nextReviewAt,
      ));
      continue;
    }

    // ② HIỂU SAI LẶP LẠI ⇒ nâng. Một lần sai là chuyện thường; cùng một kiểu
    // sai lặp lại mới là tín hiệu.
    final repeated = hypotheses.any((h) =>
        h.skillCaseId == id &&
        h.status != HypothesisStatus.retired &&
        h.type != ErrorHypothesisType.careless &&
        h.supportingEvidence.length >= policy.repeatThreshold);
    if (repeated) {
      out.add(ReviewCandidate(
        skillCaseId: id,
        priority: ReviewPriority.elevated,
        becauseOfError: true,
        reason: 'Cùng một chỗ vướng lặp lại vài lần — nên xem lại cách làm '
            'chứ không chỉ làm thêm bài.',
        dueBy: now,
      ));
      continue;
    }

    // ③ TIỀN ĐỀ YẾU mà BÀI ĐANG HỌC cần tới ⇒ được phép lên Hôm nay. Đây là
    // mức duy nhất chiếm chỗ ở Hôm nay, và nó cần HAI điều kiện cùng lúc.
    final weak = c.independentIncorrect > 0 || !c.hasEvidence;
    if (prerequisiteCaseIds.contains(id) && weak && c.evidenceCount + c.supportedCount > 0) {
      out.add(ReviewCandidate(
        skillCaseId: id,
        priority: ReviewPriority.today,
        becauseOfError: c.independentIncorrect > 0,
        reason: 'Bài hôm nay dựa vào chỗ này, mà chỗ này còn chưa chắc — '
            'mình xem lại một chút trước đã.',
        dueBy: now,
      ));
      continue;
    }

    // ④ TỰ LÀM SAI. Sai LẺ giữa nhiều lần đúng = sơ suất ⇒ giữ nhịp bình
    // thường. Còn lại ⇒ gặp lại gần (dải 1–3 ngày).
    if (c.independentIncorrect > 0) {
      final slip = c.independentIncorrect == 1 &&
          c.independentCorrect >= policy.slipCorrectTolerance;
      out.add(ReviewCandidate(
        skillCaseId: id,
        priority: slip ? ReviewPriority.normal : ReviewPriority.nearTerm,
        becauseOfError: true,
        reason: slip
            ? 'Một câu lỡ tay giữa nhiều câu đúng — chưa cần làm gì thêm.'
            : 'Con còn vướng dạng này — mình gặp lại trong ít ngày tới nhé.',
        dueBy: slip ? state.nextReviewAt : now.add(policy.nearTermWindow),
      ));
      continue;
    }

    // ⑤ ĐÚNG NHỜ TRỢ GIÚP, chưa có lần tự làm nào ⇒ gặp lại SỚM HƠN mastery
    // tự làm, nhưng KHÔNG phải là một lỗi.
    if (c.supportedCount > 0 && c.independentCorrect == 0) {
      out.add(ReviewCandidate(
        skillCaseId: id,
        priority: ReviewPriority.nearTerm,
        becauseOfError: false,
        reason: 'Con làm được khi có SAM đi cùng — cần một lần con tự làm thì '
            'mới chắc.',
        dueBy: now.add(policy.nearTermWindow),
      ));
      continue;
    }

    // ⑥ Còn lại: theo LỊCH giãn cách sẵn có.
    if (state.urgency == ReviewUrgency.reviewDue ||
        state.urgency == ReviewUrgency.overdue) {
      out.add(ReviewCandidate(
        skillCaseId: id,
        priority: ReviewPriority.normal,
        becauseOfError: false,
        reason: 'Tới lúc gặp lại dạng này rồi.',
        dueBy: state.nextReviewAt,
      ));
    }
  }

  out.sort((a, b) {
    final p = b.priority.index.compareTo(a.priority.index);
    return p != 0 ? p : a.skillCaseId.compareTo(b.skillCaseId);
  });
  return out;
}

/// Ứng viên đủ tư cách chiếm chỗ trên màn Hôm nay. CHỈ mức `today`.
///
/// ⭐⭐ Đây là chỗ bất biến D2 được thi hành: một câu sai đơn lẻ đi qua luật ④
/// nên nhiều nhất chỉ tới `nearTerm` — không có đường nào từ MỘT lỗi thẳng lên
/// màn Hôm nay.
List<ReviewCandidate> todayCandidates(List<ReviewCandidate> all) =>
    [for (final c in all) if (c.priority == ReviewPriority.today) c];
