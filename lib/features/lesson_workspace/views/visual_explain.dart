/// TRACK B ROUND 7 · V1 — «CHẠM MỘT Ô THÌ ĐƯỢC GIẢI THÍCH».
///
/// Founder (order 49 §3): «Chạm "Bay hơi" → giải thích bước đó. Chạm "Lọc" →
/// thấy: dùng khi nào · tách cái gì · liên hệ với nội dung bài. Không cần
/// animation phức tạp. Nhưng Visual Learning phải có giá trị hơn một hình
/// tĩnh đẹp.»
///
/// Vòng 5/6 đã có nút + cạnh; chạm vào một nút thì mở sheet «Sách viết» —
/// đúng nguồn, nhưng **không giải thích gì**: trẻ thấy lại đúng câu vừa đọc
/// trong ô. Tệp này là phần còn thiếu: từ DỮ LIỆU CÓ KIỂU đã tin được, dựng
/// một lời giải thích TẤT ĐỊNH cho MỘT nút.
///
/// ⚠ Ba luật, giữ bằng test:
///
/// 1. **Không sinh chữ.** Mọi câu chữ nội dung là NGUYÊN VĂN của `SemanticData`
///    (lời sách). Thứ tệp này thêm vào là *quan hệ* máy đọc được — thứ tự
///    bước, tên chiều so sánh, và chỗ khác trong bài có nhắc tới cùng một từ.
/// 2. **Không danh tính bài.** Không có `lessonNo`, không tên sách, không
///    «bai17». Hàm thuần trên `SemanticData` — cùng dữ liệu ⇒ cùng lời giải
///    thích, ở bất kỳ bài nào. `visual_identity_free_test.dart` soi mã.
/// 3. **Không biết thì nói không biết.** Sách không nói ở một chiều ⇒ ô để
///    trống có chữ, không điền hộ. Không tìm được liên hệ nào trong bài ⇒
///    nói thẳng «bài này không có sơ đồ riêng cho cách đó», không gợi ý bừa.
///
/// «Liên hệ với nội dung bài» là SO KHỚP TỪ NGUYÊN VĂN giữa hai mẩu dữ liệu
/// có kiểu của CÙNG một tài liệu (tên một cách tách xuất hiện trong tiêu đề
/// hoặc lời bước của một quy trình). Nó không suy ra kiến thức mới: nó chỉ
/// nói «chỗ kia trong bài có nhắc đúng từ này» — kiểm lại được bằng mắt.
library;

import '../../../core/lesson_model/semantic_data.dart';

/// Một dòng «tên: giá trị» lấy nguyên văn từ dữ liệu có kiểu.
class ExplainFact {
  const ExplainFact({required this.name, required this.value});

  /// Tên chiều («Dùng để tách») hoặc nhãn quan hệ máy đọc được («Bước trước»).
  final String name;

  /// Chữ sách. `null` ⇒ sách KHÔNG nói ở chiều này — hiện ô trống có lời,
  /// không bao giờ điền hộ.
  final String? value;
}

/// Một chỗ khác trong CÙNG bài có nhắc tới nút này.
class ExplainLink {
  const ExplainLink({required this.semanticId, required this.title});

  /// `SemanticData.id` của sơ đồ được nhắc tới — màn hình dùng để nhảy tới.
  final String semanticId;
  final String title;
}

/// Lời giải thích TẤT ĐỊNH cho một nút của sơ đồ.
class VisualExplain {
  const VisualExplain({
    required this.headline,
    required this.kicker,
    this.verbatim,
    this.facts = const [],
    this.links = const [],
    this.linksEmptyNote,
    this.withheldNote,
  });

  /// Tên nút — chữ đã có trong dữ liệu («Lọc», «Bước 2»).
  final String headline;

  /// Nút này là gì trong sơ đồ («Bước 2 trong 3», «Một trong 4 cách sách nêu»).
  final String kicker;

  /// Lời sách của chính nút này (bước quy trình). `null` cho nút chỉ có tên.
  final String? verbatim;

  /// «Dùng để tách: …», «Bước trước: …» — nguyên văn, có thể `null` giá trị.
  final List<ExplainFact> facts;

  /// «Trong bài này con gặp nó ở …».
  final List<ExplainLink> links;

  /// Câu nói thật khi [links] rỗng — không có liên hệ thì phải nói ra.
  final String? linksEmptyNote;

  /// Bước bị giữ lại: lời giải thích nói VÌ SAO trống, không giả vờ có chữ.
  final String? withheldNote;
}

/// Nhãn phần «liên hệ» — một bộ chữ duy nhất cho mọi sơ đồ.
const String explainLinksLabel = 'Bài này dùng ở đâu';

/// Nhãn phần «lời sách của bước».
const String explainVerbatimLabel = 'Sách viết ở bước này';

// ── Bước quy trình ──────────────────────────────────────────────────────────

/// Chạm một bước ⇒ «bước đó là bước nào, sách viết gì, trước/sau là gì».
///
/// Thứ tự là thứ tự SÁCH; «trước»/«sau» là hàng xóm trong chính danh sách
/// bước, rút gọn để đọc được trong một dòng. Không có bước nào được thêm.
VisualExplain explainForStep(ProcessSemantic s, ProcessStep step) {
  final steps = s.steps;
  final i = steps.indexWhere((x) => x.order == step.order);
  final at = i < 0 ? 0 : i;
  final before = at > 0 ? steps[at - 1] : null;
  final after = at < steps.length - 1 ? steps[at + 1] : null;
  return VisualExplain(
    headline: 'Bước ${step.order}',
    kicker: 'Bước ${step.order} trong ${steps.length} bước sách viết cho '
        '«${s.title}»',
    verbatim: step.text,
    withheldNote: step.isWithheld
        ? 'Bước này SAM chưa đọc chắc nên để trống — con xem đúng bước này '
              'trong sách nhé. SAM không đoán hộ lời sách.'
        : null,
    facts: [
      if (before != null)
        ExplainFact(
          name: 'Bước trước (bước ${before.order})',
          value: shortenStep(before.text),
        ),
      if (after != null)
        ExplainFact(
          name: 'Bước sau (bước ${after.order})',
          value: shortenStep(after.text),
        ),
    ],
  );
}

/// Rút một câu bước xuống độ dài đọc lướt được. `null` ⇒ bước bị giữ lại.
String? shortenStep(String? text, {int max = 64}) {
  if (text == null) return null;
  final t = text.replaceFirst(RegExp(r'^[·•\-\s]+'), '').trim();
  if (t.length <= max) return t;
  return '${t.substring(0, max).trimRight()}…';
}

// ── Ô của bảng so sánh ──────────────────────────────────────────────────────

/// Chạm một cách («Lọc») ⇒ tách cái gì (chiều so sánh, nguyên văn) + bài này
/// dùng nó ở đâu (so khớp từ với các sơ đồ khác của CÙNG tài liệu).
VisualExplain explainForEntity(
  ComparisonSemantic s,
  int index, {
  List<SemanticData> alsoIn = const [],
}) {
  final name = s.entities[index].name;
  final links = mentionsOf(name, alsoIn, excludeId: s.id);
  return VisualExplain(
    headline: name,
    kicker: 'Một trong ${s.entities.length} cách sách nêu ở «${s.title}»',
    facts: [
      for (final d in s.dimensions)
        ExplainFact(name: d.name, value: d.values[index]),
    ],
    links: links,
    linksEmptyNote: links.isEmpty
        ? 'Bài này chưa có sơ đồ riêng cho cách «$name» — sách chỉ nhắc tên '
              'nó ở phần tóm tắt. SAM không dựng thêm sơ đồ.'
        : null,
  );
}

// ── Quan hệ của sơ đồ khái niệm ─────────────────────────────────────────────

/// Chạm một nhánh ⇒ nói lại đúng quan hệ dữ liệu có, không thêm.
VisualExplain explainForRelation(
  ConceptMapSemantic s,
  ConceptRelation r,
  String hub, {
  List<SemanticData> alsoIn = const [],
}) {
  final other = r.a == hub ? r.b : r.a;
  final links = mentionsOf(other, alsoIn, excludeId: s.id);
  return VisualExplain(
    headline: other,
    kicker: 'Một trong ${s.relations.length} quan hệ sách nêu ở «${s.title}»',
    facts: [
      ExplainFact(name: 'Quan hệ sách nêu', value: '${r.a} ${r.relation} ${r.b}'),
    ],
    links: links,
    linksEmptyNote: links.isEmpty
        ? 'Bài này chưa có sơ đồ nào khác nhắc tới «$other».'
        : null,
  );
}

// ── So khớp từ giữa hai mẩu dữ liệu có kiểu ─────────────────────────────────

/// Những sơ đồ KHÁC của cùng tài liệu có nhắc [term] — trong tiêu đề hoặc
/// trong lời bước. So khớp NGUYÊN TỪ (có biên chữ cái), không phân biệt hoa
/// thường: «Lọc» khớp «Lọc nước từ hỗn hợp…» và «lọc», nhưng KHÔNG khớp
/// «lọc» nằm trong một từ dài hơn.
///
/// Đây là quan hệ máy đọc được giữa hai chuỗi có sẵn — không phải suy luận
/// nội dung. Trả về theo thứ tự tài liệu; trùng thì lấy một lần.
List<ExplainLink> mentionsOf(
  String term,
  List<SemanticData> all, {
  String? excludeId,
}) {
  final needle = term.trim();
  if (needle.isEmpty) return const [];
  final out = <ExplainLink>[];
  for (final s in all) {
    if (s.id == excludeId) continue;
    if (out.any((l) => l.semanticId == s.id)) continue;
    if (_mentions(s, needle)) {
      out.add(ExplainLink(semanticId: s.id, title: s.title));
    }
  }
  return out;
}

bool _mentions(SemanticData s, String term) {
  if (containsWord(s.title, term)) return true;
  return switch (s) {
    ProcessSemantic(:final steps) => steps.any(
      (st) => containsWord(st.text, term),
    ),
    ComparisonSemantic(:final entities, :final dimensions) =>
      entities.any((e) => containsWord(e.name, term)) ||
          dimensions.any((d) => d.values.any((v) => containsWord(v, term))),
    ConceptMapSemantic(:final relations) => relations.any(
      (r) => containsWord(r.a, term) || containsWord(r.b, term),
    ),
    TimelineSemantic(:final events) => events.any(
      (e) => containsWord(e.title, term) || containsWord(e.text, term),
    ),
  };
}

/// [term] xuất hiện trong [haystack] như MỘT TỪ (biên là ký tự không phải
/// chữ cái). Tiếng Việt có dấu ⇒ so khớp trên lớp chữ cái Unicode, không
/// phải `\w` của ASCII.
bool containsWord(String? haystack, String term) {
  if (haystack == null) return false;
  final escaped = RegExp.escape(term);
  final re = RegExp(
    '(?<!\\p{L})$escaped(?!\\p{L})',
    unicode: true,
    caseSensitive: false,
  );
  return re.hasMatch(haystack);
}
