/// ⭐⭐ F4 — Lời nói với phụ huynh: TẤT ĐỊNH, TRUY VẾT ĐƯỢC, KHÔNG VƯỢT BẰNG CHỨNG.
///
/// Founder Decision 5 (2026-09-01):
/// - claim với phụ huynh/học sinh KHÔNG BAO GIỜ phụ thuộc thứ tự chèn Map;
/// - nếu bằng chứng không chọn được MỘT ca yếu nhất ⇒ nói "chưa đủ bằng chứng"
///   hoặc tóm tắt CẢ NHÓM — không bịa một thứ tự;
/// - mọi câu giải thích truy vết được về bằng chứng.
///
/// Tầng này ăn `ConceptSummary` (đã tất định — ADR-004) và chỉ làm MỘT việc:
/// dịch claim thành câu tiếng Việt kèm chứng cứ. Nó KHÔNG tính toán lại gì —
/// một tầng phát ngôn mà tự suy diễn thêm là chỗ để claim vượt bằng chứng
/// chui vào sau cùng.
library;

import '../student/concept_summary.dart';

/// ⭐ Một mẩu chứng cứ đỡ cho câu nói — đủ để một người (hoặc một audit) lần
/// ngược từ câu chữ về số liệu. Câu nói không kèm citation là câu nói suông.
class EvidenceCitation {
  const EvidenceCitation({
    required this.skillCaseId,
    required this.observation,
  });

  final String skillCaseId;

  /// Mô tả NGẮN của số liệu: "3 lần tự làm, gần nhất 2026-08-30" — sinh tất
  /// định từ summary, không viết tay.
  final String observation;
}

/// Câu nói + chứng cứ. Immutable — Parent Coach hiển thị, không sửa.
class ParentExplanation {
  const ParentExplanation({
    required this.conceptId,
    required this.claim,
    required this.message,
    required this.citations,
  });

  final String conceptId;
  final ConceptClaim claim;
  final String message;
  final List<EvidenceCitation> citations;
}

/// ⭐⭐ Sinh lời giải thích từ summary. TẤT ĐỊNH: cùng summary ⇒ cùng câu.
///
/// [conceptDisplayName] — tên hiển thị (tiếng của SÁCH, không phải id nội bộ).
/// [caseDisplayNames] — tên hiển thị từng ca; ca thiếu tên dùng id (và đó là
/// lỗi dữ liệu nên lộ ra, không nên giấu).
ParentExplanation explainConcept(
  ConceptSummary s, {
  required String conceptDisplayName,
  Map<String, String> caseDisplayNames = const {},
}) {
  String nameOf(String id) => caseDisplayNames[id] ?? id;

  List<EvidenceCitation> cite(Iterable<String> caseIds) => [
        for (final id in caseIds)
          EvidenceCitation(
            skillCaseId: id,
            observation: _observationOf(s, id),
          ),
      ];

  switch (s.claim) {
    case ConceptClaim.noEvidence:
      return ParentExplanation(
        conceptId: s.conceptId,
        claim: s.claim,
        message: 'Con chưa làm bài nào về "$conceptDisplayName" trong ứng dụng, '
            'nên chưa thể nói gì về phần này. Chưa làm KHÔNG có nghĩa là chưa '
            'biết.',
        citations: const [],
      );

    case ConceptClaim.insufficientEvidence:
      final practiced = s.supportedPracticeCount > 0 && s.evidenceCount == 0;
      return ParentExplanation(
        conceptId: s.conceptId,
        claim: s.claim,
        message: practiced
            ? 'Con đang luyện "$conceptDisplayName" với gợi ý của ứng dụng '
                '(${s.supportedPracticeCount} lần). Chưa có bằng chứng con tự '
                'làm được, nên chưa thể kết luận — theo cả hai hướng.'
            : 'Bằng chứng về "$conceptDisplayName" chưa đủ để kết luận '
                '(${s.evidenceCount} lần tự làm). Cần thêm vài bài con tự làm '
                'trước khi nói con vững hay cần ôn.',
        citations: cite(s.coverage.observedCases),
      );

    case ConceptClaim.needsWork:
      final weak = s.weakestObservedCases;
      // ⭐ Decision 5: một ca ⇒ nêu đích danh; nhiều ca không phân giải được
      // ⇒ tóm tắt CẢ NHÓM. Không bao giờ tự chọn lấy một.
      final message = weak.length == 1
          ? 'Con đang vướng ở dạng "${nameOf(weak.first)}" của '
              '"$conceptDisplayName". Các dạng khác đã quan sát thì ổn hơn.'
          : 'Con đang vướng ở ${weak.length} dạng của "$conceptDisplayName": '
              '${weak.map(nameOf).map((n) => '"$n"').join(', ')}. Bằng chứng '
              'hiện có chưa phân biệt được dạng nào yếu hơn dạng nào.';
      return ParentExplanation(
        conceptId: s.conceptId,
        claim: s.claim,
        message: message,
        citations: cite(weak),
      );

    case ConceptClaim.developing:
      return ParentExplanation(
        conceptId: s.conceptId,
        claim: s.claim,
        message: 'Con đang tiến bộ ở "$conceptDisplayName" — chưa dạng nào '
            'đáng lo, nhưng cũng chưa dạng nào đủ chắc để nói là vững.',
        citations: cite(s.coverage.observedCases),
      );

    case ConceptClaim.strongOnObserved:
      final unseen = s.unobservedCases;
      return ParentExplanation(
        conceptId: s.conceptId,
        claim: s.claim,
        // ⭐⭐ Cấm chữ "vững [khái niệm]" — chỉ được nói vững NHỮNG DẠNG ĐÃ
        // KIỂM, và phải NÓI RA còn dạng chưa kiểm. Đây là câu F1 tồn tại để
        // sửa.
        message: 'Con làm tốt các dạng của "$conceptDisplayName" đã được kiểm '
            '(${s.coverage.observedCases.length}/${s.coverage.knownCaseCount}). '
            'Còn ${unseen.length} dạng chưa kiểm: '
            '${unseen.map(nameOf).map((n) => '"$n"').join(', ')} — nên thử '
            'các dạng đó trước khi kết luận về cả phần này.',
        citations: cite(s.coverage.observedCases),
      );

    case ConceptClaim.mastered:
      return ParentExplanation(
        conceptId: s.conceptId,
        claim: s.claim,
        message: 'Con đã vững "$conceptDisplayName": tự làm đúng ổn định ở cả '
            '${s.coverage.knownCaseCount} dạng đã biết của phần này '
            '(${s.evidenceCount} lần tự làm).',
        citations: cite(s.coverage.observedCases),
      );
  }
}

String _observationOf(ConceptSummary s, String caseId) {
  final f = s.observedCaseFacts[caseId];
  if (f == null) return 'chưa có lần tự làm nào';
  final when =
      f.lastEvidenceAt != null ? ', gần nhất ${_ymd(f.lastEvidenceAt!)}' : '';
  return '${f.evidenceCount} lần tự làm$when';
}

String _ymd(DateTime d) =>
    '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';
