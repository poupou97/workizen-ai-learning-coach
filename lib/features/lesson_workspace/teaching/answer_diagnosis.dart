/// TRACK B ROUND 7 · V2 — **PHẢN HỒI PHỤ THUỘC LỖI** (Founder order 49 §2).
///
/// Founder bác câu mặc định «Chưa đúng — nhưng gần rồi»: một câu thông cảm
/// dùng lại cho MỌI đáp án sai là NGHI THỨC, không phải dạy — nó không nói
/// cho trẻ điều gì về LỖI CỦA CHÍNH TRẺ. Ba nhánh bắt buộc:
///
/// - **gần đúng** ⇒ nói VÌ SAO gần đúng;
/// - **sai bản chất** ⇒ giải thích MISCONCEPTION tương ứng;
/// - **chưa đủ bằng chứng** ⇒ KHÔNG suy diễn trạng thái hiểu bài.
///
/// ⚠ Bốn luật, giữ bằng test (`answer_diagnosis_test.dart`):
///
/// 1. **Không sinh chữ nội dung.** Câu nói về NỘI DUNG là NGUYÊN VĂN của
///    `SemanticData` (lời sách). Thứ tệp này thêm vào là *quan hệ* máy đọc
///    được: tên nào trẻ chọn, sách viết gì về tên ấy, bài dùng nó ở đâu.
///    Không có LLM trong đường này.
/// 2. **Không lộ đáp án ở nhánh «sai bản chất».** Lời giải thích chỉ soi CÁI
///    TRẺ CHỌN; tên phương án đúng chỉ xuất hiện ở `scaffold` của kịch bản
///    (hết thang gợi ý). Lộ đáp án ngay lần sai đầu thì «thử lại» vô nghĩa.
/// 3. **Không có căn cứ ⇒ nói ít đi, không bịa.** Không tìm được lời sách cho
///    lựa chọn của trẻ ⇒ nhánh `insufficient`, và câu ấy nói THẲNG rằng SAM
///    không kết luận gì về việc trẻ hiểu hay chưa.
/// 4. **Không danh tính bài.** Hàm thuần trên `SemanticData` + `AskStep` —
///    cùng dữ liệu ⇒ cùng lời, ở bất kỳ bài nào. Test quét cả thư mục.
///
/// Phép so khớp tên dùng LẠI `views/visual_explain.dart` (vòng 1): so khớp
/// NGUYÊN TỪ trên lớp chữ cái Unicode, và `explainForEntity` dựng sẵn phần
/// «sách viết gì + bài này dùng ở đâu». Không viết lại lần thứ hai.
library;

import '../../../core/lesson_model/semantic_data.dart';
import '../../../core/lesson_model/tutor_script.dart';
import '../views/visual_explain.dart';

/// Ba nhánh của order 49 §2 — không có nhánh thứ tư, không có nhánh mặc định.
enum DiagnosisKind {
  /// Trẻ trúng MỘT PHẦN điều sách nêu — nói rõ phần nào trúng.
  nearMiss,

  /// Trẻ chọn một thứ sách CÓ nói tới, nhưng nó làm việc khác ⇒ đối chiếu
  /// nguyên văn «cái con chọn làm gì».
  misconception,

  /// SAM không có căn cứ để nói gì ⇒ nói đúng giới hạn của mình, KHÔNG suy
  /// diễn trạng thái hiểu bài.
  insufficient,
}

/// Lời SAM đáp lại MỘT câu trả lời cụ thể. Tất định: cùng đầu vào ⇒ cùng
/// đầu ra (view dựng lại nó khi vẽ, không cần lưu).
class AnswerDiagnosis {
  const AnswerDiagnosis({
    required this.kind,
    required this.headline,
    this.facts = const [],
    this.links = const [],
    this.linksEmptyNote,
    this.limitNote,
    this.retry,
    this.sourceBlockId,
  });

  final DiagnosisKind kind;

  /// Câu SAM nói ra — PHẢI nhắc lại chính lựa chọn của trẻ, để hai đáp án sai
  /// không bao giờ nhận cùng một câu.
  final String headline;

  /// Nguyên văn lời sách (tên chiều → giá trị). `value == null` ⇒ sách không
  /// nói ở chiều ấy — hiện ô trống có lời, không điền hộ.
  final List<ExplainFact> facts;

  /// Chỗ KHÁC trong cùng bài có nhắc tới cái trẻ chọn — chạm là nhảy tới.
  final List<ExplainLink> links;

  /// Không có chỗ nào ⇒ nói thẳng (không gợi bừa).
  final String? linksEmptyNote;

  /// Câu nói ĐÚNG GIỚI HẠN của SAM. Bắt buộc ở nhánh [DiagnosisKind
  /// .insufficient] — đó là chỗ luật «không suy diễn trạng thái hiểu bài»
  /// thành một câu trẻ đọc được.
  final String? limitNote;

  /// Lời mời THỬ LẠI — vòng lặp của order 49 §2 kết thúc ở đây, không ở điểm.
  final String? retry;

  /// Block sách của thứ trẻ chọn (nếu có) — «📖 Xem trong Đọc».
  final String? sourceBlockId;

  /// Toàn văn phản hồi, để test chứng minh HAI đáp án sai ⇒ HAI lời khác
  /// nhau (yêu cầu quyết định của vòng này).
  String get fullText => [
    headline,
    for (final f in facts) '${f.name}: ${f.value ?? '(sách không nói)'}',
    for (final l in links) l.title,
    ?linksEmptyNote,
    ?limitNote,
    ?retry,
  ].join(' | ');
}

/// Nhãn phần «lời mời thử lại» — một bộ chữ duy nhất.
const String diagnosisRetryLabel = 'Thử lại';

/// ⭐ HÀM QUYẾT ĐỊNH CỦA VÒNG 2.
///
/// `null` ⇒ câu trả lời KHỚP mẫu kịch bản (phản hồi khớp là việc của
/// `TutorRunner`), hoặc rỗng.
AnswerDiagnosis? diagnoseAnswer({
  required AskStep step,
  required String answer,
  required List<SemanticData> semantic,
  List<String> earlierAnswers = const [],
}) {
  final a = answer.trim();
  if (a.isEmpty) return null;
  if (answerMatches(a, step.acceptable)) return null;
  final repeated = earlierAnswers.any(
    (e) => normalizeAnswer(e) == normalizeAnswer(a),
  );
  return step.isChoice
      ? _forChoice(step, a, semantic, repeated)
      : _forFreeText(step, a, semantic, repeated);
}

// ── Câu chọn (MCQ) ──────────────────────────────────────────────────────────

AnswerDiagnosis _forChoice(
  AskStep step,
  String answer,
  List<SemanticData> semantic,
  bool repeated,
) {
  final chosen = entityHits(answer, semantic);

  // Không có lời sách nào cho lựa chọn này ⇒ nói ít đi, và nói thẳng rằng
  // SAM không kết luận gì (luật 3).
  if (chosen.isEmpty) {
    return AnswerDiagnosis(
      kind: DiagnosisKind.insufficient,
      headline:
          '${repeated ? 'Con vẫn chọn' : 'Con chọn'} «$answer». SAM không tìm '
          'được chỗ nào trong bài này nói về lựa chọn ấy.',
      limitNote:
          'Không có lời sách để đối chiếu thì SAM không giải thích thêm — và '
          'SAM cũng KHÔNG kết luận gì về việc con hiểu hay chưa hiểu.',
      retry: 'Con xin SAM một gợi ý, hoặc đọc lại câu hỏi rồi chọn lại nhé.',
    );
  }

  // Phương án ĐÚNG theo chính kịch bản (không phải theo suy đoán của SAM).
  final keyed = _keyedOption(step);
  final keyedNames = keyed == null
      ? const <String>{}
      : {for (final h in entityHits(keyed, semantic)) h.name};
  final chosenNames = {for (final h in chosen) h.name};
  final shared = chosenNames.intersection(keyedNames);

  if (shared.isNotEmpty)
    return _nearMissChoice(chosen, shared, keyedNames, semantic);

  // Sai bản chất: soi ĐÚNG cái trẻ chọn. Tên phương án đúng KHÔNG xuất hiện
  // ở đây (luật 2) — nó chỉ đến ở scaffold khi hết thang gợi ý.
  final hit = chosen.first;
  final ex = explainForEntity(hit.table, hit.index, alsoIn: semantic);
  final lead = _leadFact(ex.facts);
  final entity = hit.table.entities[hit.index];
  return AnswerDiagnosis(
    kind: DiagnosisKind.misconception,
    headline: lead == null
        ? '${repeated ? 'Con vẫn chọn' : 'Con chọn'} «${entity.name}». Sách có '
              'nêu tên cách này, nhưng chỗ nói nó làm gì thì để trống — SAM '
              'không đoán hộ lời sách.'
        : '${repeated ? 'Con vẫn chọn' : 'Con chọn'} «${entity.name}». Sách '
              'viết — ${lead.name}: ${lead.value}.',
    facts: [
      for (final f in ex.facts)
        if (f != lead) f,
    ],
    links: ex.links,
    linksEmptyNote: ex.linksEmptyNote,
    // ⭐⭐ NÓI CHO TỚI Ý CỐT LÕI, không dừng ở «con tự so đi».
    //
    // Bản trước dừng ở «Con so dòng sách ở trên với câu hỏi — có khớp không?»
    // — đúng nhưng GIỐNG NHAU ở mọi đáp án sai, nên nó vẫn là một nghi thức.
    // Trẻ đã đọc lời sách rồi mà vẫn chọn sai thì lời mời so lại không thêm gì.
    //
    // Nay hỏi thẳng vào ĐIỀU KIỆN của chính cách trẻ chọn: «Lắng» dùng để
    // tách «các chất rắn lơ lửng» ⇒ SAM hỏi thứ cần tách ở câu này có đúng là
    // thế không. Đó chính là chỗ hiểu sai — muối đã tan thì không còn hạt rắn
    // lơ lửng nào để lắng.
    //
    // Vẫn KHÔNG sinh chữ nội dung (luật 1): cụm điều kiện cắt NGUYÊN VĂN từ
    // lời sách. Vẫn KHÔNG lộ đáp án (luật 2): chỉ soi cái trẻ chọn.
    retry:
        _conditionCheck(lead?.value) ??
        'Con so dòng sách ở trên với câu hỏi — có khớp không?',
    sourceBlockId: entity.sourceBlockId,
  );
}

/// Câu hỏi kiểm ĐIỀU KIỆN, cắt nguyên văn từ lời sách về cách trẻ đã chọn.
///
/// «tách các chất rắn lơ lửng nặng hơn ra khỏi các chất nhẹ hơn»
///   → «thứ cần tách ở câu này có đúng là *các chất rắn lơ lửng nặng hơn* không?»
///
/// `null` ⇒ không cắt được cụm đủ gọn ⇒ chỗ gọi dùng lại câu cũ. Thà nói câu
/// chung còn hơn ghép một cụm cụt nghĩa.
String? _conditionCheck(String? value) {
  final v = (value ?? '').trim();
  if (v.isEmpty) return null;
  var obj = v;
  final m = RegExp(r'^tách\s+(.+)$', caseSensitive: false).firstMatch(obj);
  if (m != null) obj = m.group(1)!.trim();
  // «A ra khỏi B» — điều kiện nằm ở A, phần trẻ cần đối chiếu.
  final cut = obj.indexOf(' ra khỏi ');
  if (cut > 0) obj = obj.substring(0, cut).trim();
  obj = obj.replaceAll(RegExp(r'[.;,]+$'), '').trim();
  if (obj.length < 6 || obj.length > 60) return null;
  return 'Con thử kiểm một điều: thứ cần tách ở câu này có đúng là «$obj» không?';
}

/// Trẻ gọi đúng MỘT PHẦN cách sách dùng ⇒ nói rõ phần nào trúng, và trúng vì
/// sách viết gì. Không nói nốt phần còn thiếu là cách nào (đó là đáp án).
AnswerDiagnosis _nearMissChoice(
  List<EntityHit> chosen,
  Set<String> shared,
  Set<String> keyedNames,
  List<SemanticData> semantic,
) {
  final names = shared.toList()..sort();
  final facts = <ExplainFact>[];
  String? blockId;
  for (final h in chosen) {
    if (!shared.contains(h.name)) continue;
    final ex = explainForEntity(h.table, h.index, alsoIn: semantic);
    final lead = _leadFact(ex.facts);
    if (lead != null) {
      facts.add(
        ExplainFact(name: '«${h.name}» — ${lead.name}', value: lead.value),
      );
    }
    blockId ??= h.table.entities[h.index].sourceBlockId;
  }
  final missing = keyedNames.length - shared.length;
  final rest = missing > 0
      ? 'Nhưng cách sách nêu ghép $missing bước nữa mà câu con chọn chưa có.'
      : 'Nhưng câu con chọn vẫn chưa khớp với lời sách.';
  return AnswerDiagnosis(
    kind: DiagnosisKind.nearMiss,
    headline:
        'Con nói trúng một phần: «${names.join('», «')}» đúng là cách sách '
        'dùng cho việc này. $rest',
    facts: facts,
    retry:
        'Con giữ phần đã trúng, rồi nghĩ thêm: sau bước đó thì còn phải làm '
        'gì nữa? Con chọn lại nhé.',
    sourceBlockId: blockId,
  );
}

/// Phương án khớp `acceptable` — chính kịch bản nói đâu là đáp án, SAM không
/// tự chấm. Không có phương án nào khớp ⇒ `null` (khoá nằm ngoài danh sách).
String? _keyedOption(AskStep step) {
  for (final o in step.options) {
    if (answerMatches(o, step.acceptable)) return o;
  }
  return null;
}

/// Chiều ĐẦU TIÊN sách có nói — dùng làm câu SAM đọc lên. Sách không nói ở
/// chiều nào ⇒ `null` ⇒ SAM nói thẳng là trống.
ExplainFact? _leadFact(List<ExplainFact> facts) {
  for (final f in facts) {
    if (f.value != null && f.value!.trim().isNotEmpty) return f;
  }
  return null;
}

// ── Câu trả lời tự viết ─────────────────────────────────────────────────────

/// Trẻ GÕ câu trả lời. SAM chỉ biết SO CHỮ với lời sách — nên nó chỉ được
/// nói đúng chừng ấy:
///
/// - có chữ đối chiếu được ⇒ `nearMiss`, kể ra ĐÚNG những chữ ấy, và nói rõ
///   «chữ trùng chưa phải là hiểu»;
/// - không có chữ nào ⇒ `insufficient`, và SAM nói thẳng là KHÔNG BIẾT.
///
/// Không có nhánh nào ở đây kết luận trẻ hiểu hay chưa hiểu bài.
AnswerDiagnosis _forFreeText(
  AskStep step,
  String answer,
  List<SemanticData> semantic,
  bool repeated,
) {
  final echoed = echoedWords(answer, semantic);
  if (echoed.isEmpty) {
    return AnswerDiagnosis(
      kind: DiagnosisKind.insufficient,
      headline: 'SAM chưa đủ căn cứ để nói gì về câu này của con.',
      limitNote:
          'SAM chỉ đối chiếu được CHỮ con viết với lời sách trong bài. Câu của '
          'con không có chữ nào SAM đối chiếu được, nên SAM KHÔNG BIẾT con đã '
          'hiểu hay chưa — và SAM không đoán.',
      retry: repeated
          ? 'Con thử dùng vài chữ trong bài để viết lại, hoặc xin SAM một gợi '
                'ý — SAM vẫn chờ ở đây.'
          : 'Con thử viết lại bằng vài chữ có trong bài, hoặc xin SAM một gợi '
                'ý nhé.',
    );
  }
  final links = <ExplainLink>[];
  for (final w in echoed) {
    for (final l in mentionsOf(w, semantic)) {
      if (!links.any((x) => x.semanticId == l.semanticId)) links.add(l);
    }
  }
  return AnswerDiagnosis(
    kind: DiagnosisKind.nearMiss,
    headline:
        'SAM đối chiếu được ${echoed.length} chữ trong câu của con với lời '
        'sách: «${echoed.join('», «')}». Nhưng SAM chưa khớp được ý chính mà '
        'câu hỏi cần.',
    limitNote:
        'Chữ trùng nhau chưa nói con hiểu hay chưa hiểu — SAM so CHỮ, không '
        'chấm Ý.',
    links: links,
    retry:
        'Con nói thêm một ý nữa xem sao — hoặc mở đúng chỗ dưới đây rồi viết '
        'lại. SAM vẫn chờ.',
  );
}

/// Những chữ trong câu trẻ viết mà bài CÓ nhắc tới (nguyên từ). Bỏ hư từ và
/// chữ quá ngắn; giữ tối đa [max] chữ theo thứ tự trẻ viết, không lặp.
///
/// Đây là một phép SO CHỮ máy làm được và trẻ kiểm lại được bằng mắt — nó
/// KHÔNG phải phép đo hiểu bài, và lời SAM nói đúng như vậy.
List<String> echoedWords(
  String answer,
  List<SemanticData> semantic, {
  int max = 4,
}) {
  final out = <String>[];
  for (final w in normalizeAnswer(
    answer,
  ).split(RegExp(r'[^\p{L}\p{N}]+', unicode: true))) {
    if (w.length < 2 || _functionWords.contains(w)) continue;
    if (out.contains(w)) continue;
    if (mentionsOf(w, semantic).isEmpty) continue;
    out.add(w);
    if (out.length >= max) break;
  }
  return out;
}

/// Hư từ tiếng Việt + đại từ trong lời SAM: chúng có mặt ở mọi trang sách nên
/// «đối chiếu được» chúng KHÔNG nói lên điều gì.
const _functionWords = {
  'và',
  'là',
  'của',
  'vì',
  'để',
  'thì',
  'có',
  'không',
  'cho',
  'một',
  'các',
  'những',
  'trong',
  'ra',
  'vào',
  'khi',
  'nên',
  'mà',
  'với',
  'này',
  'đó',
  'ở',
  'bị',
  'được',
  'con',
  'em',
  'sách',
  'sam',
  'nó',
  'ta',
  'mình',
  'rồi',
  'sẽ',
  'đã',
  'cũng',
  'nếu',
  'hay',
  'hoặc',
  'thế',
  'ấy',
  'lại',
  'từ',
  'về',
  'theo',
  'bằng',
  'do',
  'nhưng',
  'chỉ',
  'còn',
  'phải',
  'làm',
  'đi',
  'lên',
  'xuống',
};

// ── So khớp tên: dùng lại phép của vòng 1 ───────────────────────────────────

/// Một thực thể của MỘT bảng so sánh — bảng + chỉ số, đủ để gọi
/// `explainForEntity`.
class EntityHit {
  const EntityHit(this.table, this.index);
  final ComparisonSemantic table;
  final int index;
  String get name => table.entities[index].name;
}

/// Tên thực thể nào của bài xuất hiện trong [text] (hoặc ngược lại).
///
/// Hai chiều là CỐ Ý: dữ liệu thật viết tên trần («Lọc») còn lựa chọn có thể
/// là cả một câu («Chiết bằng phễu chiết») ⇒ chiều A; ngược lại fixture mẫu
/// gắn hậu tố vào tên thực thể («Lọc (mẫu)») trong khi lựa chọn là tên trần
/// ⇒ chiều B. Cả hai chiều đều so NGUYÊN TỪ (`containsWord`), nên không có
/// phép khớp chuỗi con nào lọt qua.
List<EntityHit> entityHits(String text, List<SemanticData> semantic) {
  final out = <EntityHit>[];
  for (final s in semantic.whereType<ComparisonSemantic>()) {
    for (var i = 0; i < s.entities.length; i++) {
      final n = s.entities[i].name;
      if (n.trim().isEmpty) continue;
      if (containsWord(text, n) || containsWord(n, text)) {
        out.add(EntityHit(s, i));
      }
    }
  }
  return out;
}
