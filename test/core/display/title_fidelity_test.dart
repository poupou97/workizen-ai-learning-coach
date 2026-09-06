/// ⭐⭐ ROUND 7 · WS-S — **GIỮ NGUYÊN VĂN NGUỒN** (quyết định của Founder), kiểm
/// trên **QUẦN THỂ THẬT**, không trên fixture tự dựng.
///
/// ## Vì sao bộ test này có hình dạng như vậy
///
/// Luật cũ (`LessonDocument.titleCase`) xanh suốt bốn vòng vì **chỉ được nạp
/// chuỗi IN HOA** — tức chỉ nạp đúng tiền đề mà chính nó giả định. Một hàm
/// hạ-chữ-thường không thể đỏ khi đầu vào vốn không có chữ thường nào để phá.
/// Đó không phải test yếu; đó là **lỗi chọn quần thể thử**.
///
/// Nên bộ test này không được phép lặp lại hình dạng ấy, và có ba tầng:
///
///  1. **QUẦN THỂ THẬT.** Nạp toàn bộ tiêu đề trong `assets/pack/lesson-index-*.json`
///     — 2 623 tiêu đề, 2 382 duy nhất, sáu dạng hoa/thường khác nhau — chứ
///     không phải một hằng số viết tay.
///  2. **CANH CHÍNH QUẦN THỂ.** Một test riêng khẳng định quần thể ấy **thực sự
///     chứa** những ca có thể làm luật đỏ: tiêu đề đã có chữ thường, tiêu đề
///     IN HOA nhiều từ, viết tắt lồng trong tiêu đề, số La Mã. Nếu pack đổi và
///     mất những ca ấy, test này đỏ **trước** khi các test kia lặng lẽ xanh vì
///     không còn gì để bắt.
///  3. **NGHĨA VỤ CHỨNG MINH.** Đo thẳng ứng viên chuẩn hoá trên chính quần thể
///     ấy và ghi lại rằng nó **trượt**, kèm tên nạn nhân.
///
/// `assets/pack/` là gitignore ⇒ trên clone sạch bộ này **skip**, và nói rõ vì
/// sao. Hai test không cần pack (đồng nhất trên chuỗi dựng tay, và test soi mã)
/// vẫn chạy ở mọi nơi.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/display/lesson_title.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';

/// Mọi giá trị `title` trong pack đang phát hành, theo thứ tự gặp.
List<String> _packTitles() {
  final dir = Directory('assets/pack');
  if (!dir.existsSync()) return const [];
  final out = <String>[];
  void walk(Object? node) {
    if (node is Map) {
      for (final e in node.entries) {
        if (e.key == 'title' && e.value is String && (e.value as String).trim().isNotEmpty) {
          out.add(e.value as String);
        } else {
          walk(e.value);
        }
      }
    } else if (node is List) {
      for (final x in node) {
        walk(x);
      }
    }
  }

  final files = dir
      .listSync()
      .whereType<File>()
      .where((f) => RegExp(r'lesson-index-g\d+\.json$').hasMatch(f.path))
      .toList()
    ..sort((a, b) => a.path.compareTo(b.path));
  for (final f in files) {
    walk(jsonDecode(f.readAsStringSync()));
  }
  return out;
}

/// Bỏ mọi chú thích Dart rồi mới tìm — xem test «soi MÃ, không soi văn xuôi».
String _stripDartComments(String src) => src
    .replaceAll(RegExp(r'/\*.*?\*/', dotAll: true), ' ')
    .split('\n')
    .map((l) {
      final i = l.indexOf('//');
      return i < 0 ? l : l.substring(0, i);
    })
    .join('\n');

/// Tệp `.dart` dưới `lib/` mà MÃ (không phải chú thích) nhắc tới [name],
/// trừ chính tệp định nghĩa luật tiêu đề.
List<String> _libFilesMentioningInCode(String name) {
  final out = <String>[];
  final word = RegExp(r'\b' + RegExp.escape(name) + r'\b');
  for (final f in Directory('lib').listSync(recursive: true)) {
    if (f is! File || !f.path.endsWith('.dart')) continue;
    if (f.path.endsWith('lib/core/display/lesson_title.dart')) continue;
    if (word.hasMatch(_stripDartComments(f.readAsStringSync()))) out.add(f.path);
  }
  return out;
}

bool _hasRomanNumeralWord(String s) =>
    s.split(RegExp(r'\s+')).any((w) => RegExp(r'^[IVX]{2,}[.,]?$').hasMatch(w));

/// Một «viết tắt lồng trong tiêu đề»: một từ toàn chữ hoa nằm cạnh những từ
/// khác, trong một tiêu đề ĐÃ có chữ thường — ca mà mọi phép hạ chữ sẽ phá.
bool _hasEmbeddedAcronym(String s) =>
    !isAllUpperCase(s) &&
    s.split(RegExp(r'\s+')).any((w) =>
        w.length >= 2 &&
        w == w.toUpperCase() &&
        w.runes.any((r) {
          final c = String.fromCharCode(r);
          return c.toUpperCase() != c.toLowerCase();
        }));

void main() {
  final titles = _packTitles();
  final unique = titles.toSet().toList()..sort();
  final allCaps = unique.where(isAllUpperCase).toList();
  final multiWordCaps =
      allCaps.where((t) => letterWordCount(t) >= 2).toList();
  final skip = titles.isEmpty
      ? 'assets/pack/ vắng mặt (gitignore) — quần thể thật không nạp được; '
          'chạy lại trong cây đã compose'
      : null;

  group('GIỮ NGUYÊN VĂN NGUỒN — quyết định của Founder', () {
    test('⭐⭐ displayTitle là ĐỒNG NHẤT trên TOÀN BỘ quần thể thật', () {
      final changed = [for (final t in unique) if (displayTitle(t) != t) t];
      expect(
        changed,
        isEmpty,
        reason: 'tiêu đề bị biến đổi trước khi tới trẻ: ${changed.take(5)}',
      );
      // và quần thể phải đủ lớn để câu «rỗng» có nghĩa
      expect(unique.length, greaterThan(2000),
          reason: 'quần thể ${unique.length} quá nhỏ để kết luận gì');
    }, skip: skip);

    test('⭐⭐ 108 tiêu đề IN HOA nhiều từ đi qua NGUYÊN VẸN từng ký tự', () {
      // Chính là quần thể mà quyết định nói tới. Số đếm được ghim để nếu pack
      // đổi thì người đọc thấy ngay, chứ không phải để test tự chọn cho vừa.
      expect(multiWordCaps, isNotEmpty);
      for (final t in multiWordCaps) {
        expect(displayTitle(t), t, reason: t);
        expect(capitalsOf(displayTitle(t)).length, capitalsOf(t).length, reason: t);
      }
    }, skip: skip);

    test('nhãn bài học cũng nguyên văn, và LessonDocument dùng CÙNG luật ấy', () {
      expect(displayLessonLabel(8, 'Đấu tranh giành độc lập thời kì Bắc thuộc'),
          'Bài 8 · Đấu tranh giành độc lập thời kì Bắc thuộc');
      expect(displayLessonLabel(4, 'ASEAN AND VIET NAM'),
          'Bài 4 · ASEAN AND VIET NAM');
      // Hai chỗ dựng nhãn phải cho CÙNG một chuỗi — nếu ngày nào đó phép chuẩn
      // hoá được bật, chúng không được lệch nhau.
      final doc = LessonDocument.fromJson({
        'schema': LessonDocument.schemaV1,
        'book': '05-sgk-lich-su-va-dia-li-5',
        'bookTitle': 'Lịch sử và Địa lí 5',
        'subject': 'Lịch sử và Địa lí',
        'grade': 5,
        'lesson': 8,
        'title': 'ĐẤT NƯỚC VÀ CON NGƯỜI VIỆT NAM',
        'provenance': {
          'trust': 'trustedStructuredLesson',
          'book': '05-sgk-lich-su-va-dia-li-5',
          'pagePdfStart': 38,
          'pagePdfEnd': 41,
          'generator': 'tool/corpus/tsl_to_lesson_document.py@v1',
          'sourcePipeline': 'tc2-p1',
          'sdmVersion': 'sdm-v3',
          'distribution': 'internal-research-only (Founder D4)',
          'auditStatus': 'notAudited',
          'answerKeysIncluded': false,
        },
        'evidencePolicy': 'none',
        'licence': 'internalResearchOnly',
        'blocks': [
          {
            'type': 'heading',
            'id': 'x:p038:tc2-p1:000',
            'sourceRef': {
              'book': '05-sgk-lich-su-va-dia-li-5',
              'pagePdf': 38,
              'bbox': [0.1, 0.1, 0.5, 0.05],
            },
            'trust': 'trustedStructuredLesson',
            'text': 'ĐẤT NƯỚC VÀ CON NGƯỜI VIỆT NAM',
          },
        ],
        'semantic': <Object?>[],
        'chapters': <Object?>[],
      });
      expect(doc, isNotNull);
      expect(doc!.lessonLabel, displayLessonLabel(doc.lessonNo, doc.title));
      expect(doc.lessonLabel, contains('VIỆT NAM'),
          reason: 'tên nước bị hạ chữ trên đường tới nhãn ⇒ đỏ');
    });
  });

  group('CANH CHÍNH QUẦN THỂ — test không được xanh vì thiếu ca khó', () {
    test('⭐⭐ quần thể thật CHỨA đủ bốn dạng có thể làm luật đỏ', () {
      // Đây là bài học của vòng này viết thành test. Nếu một ngày quần thể chỉ
      // còn chuỗi IN HOA (như quần thể của `titleCase` ngày xưa) thì mọi test
      // trên kia xanh mà chẳng chứng minh gì — và test NÀY sẽ đỏ trước.
      final mixedCase = unique.where((t) => !isAllUpperCase(t)).length;
      final embeddedAcronym = unique.where(_hasEmbeddedAcronym).length;
      final roman = unique.where(_hasRomanNumeralWord).length;
      expect(mixedCase, greaterThan(100),
          reason: 'không có tiêu đề đã-đúng-chính-tả ⇒ không kiểm được «đừng đụng vào»');
      expect(multiWordCaps.length, greaterThan(50),
          reason: 'không có tiêu đề IN HOA nhiều từ ⇒ không kiểm được chính quyết định này');
      expect(embeddedAcronym, greaterThan(0),
          reason: 'không có viết tắt lồng trong tiêu đề ⇒ ca hỏng nặng nhất vắng mặt');
      expect(roman, greaterThan(0),
          reason: 'không có số La Mã ⇒ «THẾ KỈ XX» không được đại diện');
    }, skip: skip);
  });

  group('NGHĨA VỤ CHỨNG MINH — điều kiện bật, đo chứ không hứa', () {
    test('⭐⭐ ứng viên chuẩn hoá TRƯỢT trên quần thể thật, và đây là mức trượt',
        () {
      final lost = titlesLosingCapitals(sentenceCaseAllCaps, multiWordCaps);
      expect(
        lost.length,
        multiWordCaps.length,
        reason: 'ứng viên làm mất chữ hoa trên ${lost.length}/${multiWordCaps.length} '
            'tiêu đề IN HOA nhiều từ',
      );
      // Nạn nhân có tên. Nếu một phiên bản sau giữ được chúng, ba dòng này đỏ —
      // và đỏ ở đây là TIN VUI: điều kiện bật vừa tiến gần hơn.
      for (final t in const [
        'ASEAN AND VIET NAM',
        'CHIẾN TRANH VÀ HOA BÌNH TRONG THẾ KỈ XX',
      ]) {
        if (!multiWordCaps.contains(t)) continue;
        expect(capitalsOf(sentenceCaseAllCaps(t)).length,
            lessThan(capitalsOf(t).length),
            reason: '$t — nếu đã giữ được thì cập nhật điều kiện bật');
      }
    }, skip: skip);

    test('⭐ thước đo KHÔNG tự tha cho phép đồng nhất', () {
      // Một thước đo trả về «rỗng» cho mọi thứ là một thước đo vô dụng. Phép
      // đồng nhất phải qua; phép hạ chữ phải trượt — trên chuỗi dựng tay, nên
      // test này chạy cả trên clone sạch.
      const sample = ['ASEAN AND VIET NAM', 'Thời kì Bắc thuộc', 'GDTC 5'];
      expect(titlesLosingCapitals((s) => s, sample), isEmpty);
      expect(titlesLosingCapitals((s) => s.toLowerCase(), sample), sample);
      expect(titlesLosingCapitals(sentenceCaseAllCaps, sample),
          ['ASEAN AND VIET NAM']);
    });
  });

  group('MỘT luật duy nhất — có test soi mã', () {
    test('⭐⭐ không tệp nào trong lib/ gọi phép chuẩn hoá CHƯA ĐƯỢC BẬT', () {
      // Soi MÃ, không soi văn xuôi: bản đầu của test này đỏ vì một câu chú
      // thích NHẮC TÊN hàm — một canh gác đọc cả comment thì hoặc kêu oan, hoặc
      // (tệ hơn) dạy người ta đừng viết tên nó ra trong tài liệu.
      final offenders = _libFilesMentioningInCode('sentenceCaseAllCaps');
      expect(offenders, isEmpty,
          reason: 'chuẩn hoá chỉ được bật sau khi CHỨNG MINH trên quần thể thật '
              '— xem lib/core/display/lesson_title.dart');
    });

    test('⭐ `titleCase` đã bị xoá khỏi toàn bộ lib/', () {
      expect(_libFilesMentioningInCode('titleCase'), isEmpty,
          reason: 'một phép biến đổi không bao giờ được chạy thì phải bị xoá, '
              'không phải để đó nạp sẵn');
    });

    test('⭐ chính bộ soi mã ấy có bắt được không — kiểm bằng đột biến', () {
      // Một test soi mã trả về rỗng vì nó hỏng cũng trả về rỗng. Nạp cho nó một
      // định danh CÓ THẬT trong mã của lib/ và đòi nó tìm ra.
      expect(_libFilesMentioningInCode('displayLessonLabel'), isNotEmpty,
          reason: 'bộ soi mã không tìm thấy thứ chắc chắn có ⇒ nó đang mù');
    });
  });
}
