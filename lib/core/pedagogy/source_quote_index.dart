/// ⭐⭐ ROUND 4 (A-runtime, Founder §5) — SOURCE QUOTE INDEX: luật TẤT ĐỊNH
/// «câu SAM trích có thật trong sách không».
///
/// Founder §5(a): gợi ý chỉ được coi là runtime-guided khi chữ của nó là
/// NGUYÊN VĂN / dẫn xuất được từ một block nguồn tin cậy có xuất xứ. Cách
/// duy nhất máy chứng minh được điều đó mà không suy diễn ngữ nghĩa: mọi
/// đoạn SAM đặt trong ngoặc kép «…» phải là CHUỖI CON NGUYÊN VĂN (sau chuẩn
/// hoá chữ thường / khoảng trắng / dấu câu đầu-cuối) của ĐÚNG MỘT block chữ
/// trong bài, và block đó được ghi lại làm `sourceBlockId`.
///
/// Không làm: không paraphrase-check (ngữ nghĩa — không tất định), không
/// sửa lỗi OCR của nguồn (nguồn sai thì nguồn phải sửa — lane A-pipeline),
/// không nới «…» thành khớp-từng-mảnh (trích bị lược không phải nguyên văn).
/// Mọi từ chối đều có mã đọc được để Lane B / Founder thấy đúng chỗ hỏng.
///
/// Ưu tiên khớp: block cùng MỤC (`headingPath` của block câu hỏi — §5(a)
/// «the SGK block the question refers to») trước, rồi mới tới block khác
/// của bài; cùng mục thì theo thứ tự đọc.
library;

import '../lesson_model/lesson_document.dart';
import '../lesson_model/tutor_script.dart' show normalizeAnswer;

/// Một block chữ của bài — đủ để tra trích dẫn. Lane B dựng từ
/// `LessonDocument.blocks` (`LessonDocument.textOf(b)` + `b.relations`).
class SourceQuoteBlock {
  const SourceQuoteBlock({
    required this.id,
    required this.text,
    this.headingPath = const [],
  });

  final String id;
  final String text;
  final List<String> headingPath;
}

/// Kết quả tra MỘT đoạn trích.
class QuoteLookup {
  const QuoteLookup({required this.span, this.blockId, this.refusal});

  /// Đoạn trích nguyên trạng (không có ngoặc).
  final String span;

  /// Block chứa đoạn trích nguyên văn; `null` ⇒ không tìm thấy.
  final String? blockId;

  /// `QUOTE_ELIDED:<span>` (có «…»), `QUOTE_NOT_IN_SOURCE:<span>`.
  final String? refusal;

  bool get found => blockId != null;
}

/// Kết quả kiểm MỘT câu (gợi ý / phản hồi / scaffold).
class QuoteVerification {
  const QuoteVerification({
    required this.lookups,
    required this.sourceBlockId,
    required this.refusals,
  });

  /// Không có «…» nào trong câu.
  static const noQuotes = QuoteVerification(
      lookups: [], sourceBlockId: null, refusals: ['HINT_UNSOURCED']);

  final List<QuoteLookup> lookups;

  /// Block của đoạn trích ĐẦU TIÊN tìm thấy — để UI hiện thẻ «Sách viết».
  final String? sourceBlockId;

  /// Rỗng ⇒ mọi đoạn trích đều nguyên văn trong bài.
  final List<String> refusals;

  bool get hasQuotes => lookups.isNotEmpty;

  /// ⭐ Câu được coi là CÓ NGUỒN: ≥ 1 đoạn trích, và KHÔNG đoạn nào hỏng.
  bool get isSourced => hasQuotes && refusals.isEmpty;
}

class SourceQuoteIndex {
  SourceQuoteIndex(Iterable<SourceQuoteBlock> blocks)
      : _blocks = [
          for (final b in blocks)
            if (normalizeAnswer(b.text).isNotEmpty) b
        ];

  /// Mọi block CÓ CHỮ của tài liệu (withheld/ảnh không có chữ ⇒ bỏ qua).
  /// Trust của block là việc của chip tài liệu — chỉ mục chỉ trả lời «có
  /// nguyên văn trong bài không».
  factory SourceQuoteIndex.fromLessonDocument(LessonDocument doc) =>
      SourceQuoteIndex([
        for (final b in doc.blocks)
          if (LessonDocument.textOf(b) case final String t)
            SourceQuoteBlock(
                id: b.id, text: t, headingPath: b.relations.headingPath),
      ]);

  final List<SourceQuoteBlock> _blocks;

  int get blockCount => _blocks.length;

  /// Mục (headingPath) của một block theo id; không có ⇒ rỗng.
  List<String> headingPathOf(String blockId) {
    for (final b in _blocks) {
      if (b.id == blockId) return b.headingPath;
    }
    return const [];
  }

  /// «…» trong câu — chỉ ngoặc kép kiểu sách («»), đúng thứ kịch bản dùng.
  static final RegExp quotePattern = RegExp(r'«([^«»]+)»');

  static bool _isElided(String span) =>
      span.contains('…') || span.contains('...');

  /// Tra một đoạn trích. [preferHeadingPath] = mục của block câu hỏi; khớp
  /// trong cùng mục thắng, rồi mới tới mục khác.
  QuoteLookup lookup(String span, {List<String> preferHeadingPath = const []}) {
    if (_isElided(span)) {
      return QuoteLookup(span: span, refusal: 'QUOTE_ELIDED:$span');
    }
    final needle = normalizeAnswer(span);
    if (needle.isEmpty) {
      return QuoteLookup(span: span, refusal: 'QUOTE_NOT_IN_SOURCE:$span');
    }
    String? inSection, anywhere;
    for (final b in _blocks) {
      if (!normalizeAnswer(b.text).contains(needle)) continue;
      anywhere ??= b.id;
      if (preferHeadingPath.isNotEmpty &&
          _sameSection(b.headingPath, preferHeadingPath)) {
        inSection ??= b.id;
      }
    }
    final hit = inSection ?? anywhere;
    return hit == null
        ? QuoteLookup(span: span, refusal: 'QUOTE_NOT_IN_SOURCE:$span')
        : QuoteLookup(span: span, blockId: hit);
  }

  /// Kiểm MỌI đoạn trích của một câu. Không có «…» ⇒ [QuoteVerification
  /// .noQuotes] (`HINT_UNSOURCED`) — câu không trích gì thì máy không chứng
  /// minh được nó từ sách.
  QuoteVerification verify(String text,
      {List<String> preferHeadingPath = const []}) {
    final spans = [
      for (final m in quotePattern.allMatches(text)) m.group(1)!.trim()
    ];
    if (spans.isEmpty) return QuoteVerification.noQuotes;
    final lookups = [
      for (final s in spans) lookup(s, preferHeadingPath: preferHeadingPath)
    ];
    return QuoteVerification(
      lookups: lookups,
      sourceBlockId:
          lookups.where((l) => l.found).map((l) => l.blockId).firstOrNull,
      refusals: [for (final l in lookups) if (l.refusal != null) l.refusal!],
    );
  }

  /// Cùng mục = headingPath này là tiền tố của kia (hoặc ngược lại), và
  /// cả hai không rỗng.
  static bool _sameSection(List<String> a, List<String> b) {
    if (a.isEmpty || b.isEmpty) return false;
    final n = a.length < b.length ? a.length : b.length;
    for (var i = 0; i < n; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }
}
