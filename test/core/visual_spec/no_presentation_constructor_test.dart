/// ⭐ LANE E2 (round 5) — TIỀN LỆ LÀN A2 (PR #84) áp cho tầng hình.
///
/// `MathExpression` của A2 có `from_json` nhưng CỐ Ý không có `from_latex`:
/// `latex` là thuộc tính TÍNH RA, không có setter — nên một chuỗi để in ra
/// không thể quay ngược thành cấu trúc, và LaTeX do mô hình sinh không có
/// đường nào rửa mình thành sự thật.
///
/// Cùng một lỗ tồn tại ở tầng hình, chỉ đổi định dạng: `VisualSpec.fromSvg`,
/// `.fromMermaid`, `.fromMarkdown` sẽ biến «một hình ai đó vẽ» thành «một
/// sơ đồ có nguồn». Test này quét MÃ NGUỒN — nó bắt được cả thứ mà kiểu dữ
/// liệu không chặn được, và nó fail ngay ngày ai đó thêm hàm ấy.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('không có hàm dựng nào từ MỘT DẠNG TRÌNH BÀY', () {
    // `fromJson` được phép: JSON ở đây là artefact đã dựng sẵn, có nguồn,
    // và đi qua đường fail-closed. Các dạng dưới đây thì không.
    final forbidden = RegExp(
      r'\b(?:factory\s+\w+|static\s+\w+\??\s+)?from'
      r'(Svg|Latex|Tex|Markdown|Md|Mermaid|Html|Dot|Graphviz|Rendered|Image|'
      r'Png|Text|String|Prompt|Llm|Model)\s*\(',
      caseSensitive: false,
    );
    final scanned = <String>[];
    for (final f in Directory('lib/core/visual_spec')
        .listSync(recursive: true)
        .whereType<File>()) {
      if (!f.path.endsWith('.dart')) continue;
      scanned.add(f.path);
      final code = f
          .readAsLinesSync()
          .where((l) => !l.trimLeft().startsWith('//'))
          .join('\n');
      final m = forbidden.firstMatch(code);
      expect(
        m,
        isNull,
        reason: '${f.path}: một dạng trình bày không được quay ngược thành '
            'cấu trúc — «${m?.group(0)}»',
      );
    }
    expect(scanned.length, greaterThanOrEqualTo(5));
  });

  test('tầng spec KHÔNG import mạng, mô hình, hay bất kỳ gói ngoài nào', () {
    // «0 lệnh gọi LLM lúc chạy» phải là điều KHÔNG VIẾT RA ĐƯỢC, không phải
    // một lời hứa. `lib/core/visual_spec/**` chỉ được import `lesson_model`
    // và thư viện chuẩn của Dart.
    final allowed = RegExp(
      r"^import '(dart:(convert|core|math)|\.\./lesson_model/[a-z_]+\.dart"
      r"|[a-z_]+\.dart)';$",
    );
    for (final f in Directory('lib/core/visual_spec')
        .listSync(recursive: true)
        .whereType<File>()) {
      if (!f.path.endsWith('.dart')) continue;
      for (final line in f.readAsLinesSync()) {
        if (!line.startsWith('import ')) continue;
        expect(
          allowed.hasMatch(line.trim()),
          isTrue,
          reason: '${f.path}: import ngoài vòng cho phép — «$line»',
        );
        expect(line.contains('package:http'), isFalse);
        expect(line.contains('dart:io'), isFalse, reason: 'không đọc/ghi đĩa');
      }
    }
  });

  test('artefact spec TÁCH khỏi pack bài — họ hình mới không làm mất BÀI', () {
    // `LessonDocument.fromJson` là union kín: một loại block lạ ⇒ hỏng cả tài
    // liệu. Làn này KHÔNG thêm loại block nào vào pack; hình sống trong
    // artefact riêng, có phiên bản riêng.
    final model = File('lib/core/lesson_model/lesson_document.dart')
        .readAsStringSync();
    expect(model.contains('sealed class LessonBlock'), isTrue);
    for (final f in Directory('lib/core/visual_spec')
        .listSync(recursive: true)
        .whereType<File>()) {
      if (!f.path.endsWith('.dart')) continue;
      final src = f.readAsStringSync();
      expect(
        src.contains('extends LessonBlock'),
        isFalse,
        reason: '${f.path}: thêm loại block = pack và app phải ship cùng nhau',
      );
    }
  });
}
