/// WAL-69 — Bốn chiều phản hồi TÁCH BẠCH: CORRECTNESS · ASSISTANCE ·
/// EVIDENCE · AFFECT. Không bao giờ gộp thành một "điểm" hay một lời khen mù.
///
/// Vì sao là CORE chứ không phải chuỗi trong widget: AFFECT chịu luật doctrine
/// (SAM Philosophy, nguồn PRIMARY + Dweck): KHEN NỖ LỰC/QUÁ TRÌNH, không khen
/// tư chất. Luật đó phải là TESTABLE RULE trên một model — không phải lời dặn
/// trong comment mà widget nào cũng có thể quên.
library;

import '../student/mastery.dart';

/// Chiều EVIDENCE: hệ GHI NHẬN gì từ lượt làm này — nói thật với trẻ.
enum EvidenceNote {
  /// Tự làm ⇒ được tính là bằng chứng độc lập.
  countsAsIndependent,

  /// Tự phát hiện và tự sửa ⇒ bằng chứng độc lập MẠNH.
  countsAsSelfCorrection,

  /// Có hỗ trợ ⇒ KHÔNG tính là tự làm — nói thẳng, kèm lời hẹn thử lại.
  supportedOnly,

  /// Chưa xong / sai ⇒ ghi nhận lần thử, không phán xét.
  attemptRecorded,
}

/// Phản hồi bốn chiều cho MỘT lượt làm bài đã kết thúc.
class TutorFeedback {
  const TutorFeedback({
    required this.correct,
    required this.maxSupport,
    required this.evidenceNote,
    required this.praise,
    required this.evidenceLine,
  });

  final bool correct; // CORRECTNESS
  final SupportLevel maxSupport; // ASSISTANCE
  final EvidenceNote evidenceNote; // EVIDENCE
  final String praise; // AFFECT — chịu luật khen dưới đây
  final String evidenceLine; // EVIDENCE thành lời — luôn nói thật
}

/// ⭐ LUẬT KHEN (TESTABLE RULE — doctrine SAM Philosophy):
/// khen NỖ LỰC, QUÁ TRÌNH, CHIẾN LƯỢC; cấm khen TƯ CHẤT. Danh sách cấm là
/// hằng công khai để test quét — thêm từ mới phải thêm vào đây.
const bannedAbilityPraise = [
  'thông minh', 'giỏi quá', 'giỏi lắm', 'giỏi thế', 'thiên tài',
  'nhanh thế', 'nhanh quá', 'siêu quá', 'xuất sắc bẩm sinh', 'có khiếu',
];

/// Sinh phản hồi bốn chiều từ kết quả phiên. TẤT ĐỊNH — không LLM.
TutorFeedback feedbackFor({
  required bool correct,
  required SupportLevel maxSupport,
  required bool selfCorrected,
}) {
  final independent = maxSupport == SupportLevel.none;
  if (!correct) {
    return TutorFeedback(
      correct: false,
      maxSupport: maxSupport,
      evidenceNote: EvidenceNote.attemptRecorded,
      praise: 'Con đã dám thử — sai là một bước của học. Mình xem lại cùng '
          'nhau nhé.',
      evidenceLine: 'SAM ghi lại lần thử này. Thử là có giá trị, kể cả chưa ra.',
    );
  }
  if (selfCorrected) {
    return TutorFeedback(
      correct: true,
      maxSupport: maxSupport,
      evidenceNote: EvidenceNote.countsAsSelfCorrection,
      praise: 'Con tự tìm ra chỗ chưa đúng và tự sửa được — điều đó quý hơn '
          'cả đúng ngay lần đầu!',
      evidenceLine: 'SAM ghi lại: con TỰ soát và TỰ sửa được bài dạng này.',
    );
  }
  if (independent) {
    return TutorFeedback(
      correct: true,
      maxSupport: maxSupport,
      evidenceNote: EvidenceNote.countsAsIndependent,
      praise: 'Con tự làm được, không cần tớ gợi ý gì luôn! 🎉',
      evidenceLine: 'SAM ghi lại: con TỰ làm được bài dạng này.',
    );
  }
  return TutorFeedback(
    correct: true,
    maxSupport: maxSupport,
    evidenceNote: EvidenceNote.supportedOnly,
    praise: 'Làm đúng rồi! Con đã kiên trì làm đến cùng — tớ thích điều đó.',
    evidenceLine: 'Lần này có gợi ý nên tớ chưa tính là con tự làm được đâu — '
        'mai mình thử một bài giống vậy mà không cần gợi ý nhé!',
  );
}
