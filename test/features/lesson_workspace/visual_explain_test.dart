/// ROUND 7 · V1 — «CHẠM MỘT Ô THÌ ĐƯỢC GIẢI THÍCH» (Founder order 49 §3).
///
/// Bốn thứ phải đúng, và ba trong bốn thứ ấy là LỜI HỨA VỚI TRẺ:
///
/// A. Chạm một BƯỚC ⇒ biết nó là bước mấy trong mấy, sách viết gì, trước/sau
///    là bước nào. Bước bị giữ lại ⇒ nói VÌ SAO trống, không bịa lời sách.
/// B. Chạm một CÁCH TÁCH ⇒ thấy sách nói nó tách cái gì (nguyên văn từng
///    chiều) và CHỖ KHÁC TRONG BÀI có nhắc đúng từ ấy. Không có chỗ nào ⇒
///    nói thẳng, không gợi bừa.
/// C. So khớp «liên hệ» là NGUYÊN TỪ, không phải chuỗi con: một cách tên
///    «Lọc» không được khớp bừa vào mọi từ có chứa «lọc».
/// D. Không danh tính bài trong mã của cả thư mục `views/` — quét mã nguồn.
///    Vòng 5 chỉ quét hai tệp renderer; vòng 7 thêm hai tệp nữa vào cùng thư
///    mục, nên phép quét phải bám THƯ MỤC, không bám danh sách tay.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/semantic_data.dart';
import 'package:learning_coach/features/lesson_workspace/views/process_flow_view.dart';
import 'package:learning_coach/features/lesson_workspace/views/visual_explain.dart';
import 'package:learning_coach/features/lesson_workspace/views/visual_explain_card.dart';
import 'package:learning_coach/features/lesson_workspace/visual_view.dart';

import 'support.dart';

ProcessSemantic _proc({
  String id = 'p1',
  String title = 'Lọc nước từ hỗn hợp (mẫu)',
  List<ProcessStep>? steps,
}) => ProcessSemantic(
  id: id,
  title: title,
  trust: ContentTrust.fixtureSynthetic,
  derivation: 'synthetic-test',
  steps:
      steps ??
      const [
        ProcessStep(order: 1, text: '· Khuấy mạnh (mẫu).', sourceBlockId: 'b1'),
        ProcessStep(order: 2, text: '· Gấp giấy lọc (mẫu).', sourceBlockId: 'b2'),
        ProcessStep(order: 3, text: '· Rót vào phễu (mẫu).', sourceBlockId: 'b3'),
      ],
);

ComparisonSemantic _cmp() => ComparisonSemantic(
  id: 'c1',
  title: 'Các cách tách chất (mẫu)',
  trust: ContentTrust.fixtureSynthetic,
  derivation: 'synthetic-test',
  entities: const [
    ComparisonEntity(name: 'Lọc', sourceBlockId: 'b1'),
    ComparisonEntity(name: 'Lắng', sourceBlockId: 'b2'),
  ],
  dimensions: [
    ComparisonDimension(
      name: 'Dùng để tách',
      cells: const [
        ComparisonValue(
          text: 'chất rắn không tan (mẫu)',
          sourceBlockId: 'b1',
          grounding: ValueGrounding.cellStated,
        ),
        ComparisonValue(
          text: null,
          sourceBlockId: 'b2',
          grounding: ValueGrounding.cellStated,
        ),
      ],
    ),
  ],
);

void main() {
  group('A. chạm một BƯỚC ⇒ giải thích bước đó', () {
    test('bước giữa: số thứ tự thật, lời sách, bước trước và bước sau', () {
      final s = _proc();
      final e = explainForStep(s, s.steps[1]);
      expect(e.headline, 'Bước 2');
      expect(e.kicker, contains('Bước 2 trong 3 bước'));
      expect(e.kicker, contains('Lọc nước từ hỗn hợp (mẫu)'));
      expect(e.verbatim, '· Gấp giấy lọc (mẫu).');
      expect(e.withheldNote, isNull);
      final names = [for (final f in e.facts) f.name];
      expect(names, ['Bước trước (bước 1)', 'Bước sau (bước 3)']);
      expect(e.facts.first.value, 'Khuấy mạnh (mẫu).');
    });

    test('bước đầu không có «bước trước»; bước cuối không có «bước sau» — '
        'KHÔNG bịa hàng xóm', () {
      final s = _proc();
      expect([for (final f in explainForStep(s, s.steps.first).facts) f.name], [
        'Bước sau (bước 2)',
      ]);
      expect([for (final f in explainForStep(s, s.steps.last).facts) f.name], [
        'Bước trước (bước 2)',
      ]);
    });

    test('⭐ bước bị giữ lại: nói VÌ SAO trống, verbatim vẫn null', () {
      final s = _proc(
        steps: const [
          ProcessStep(order: 1, withheldReason: 'math_guard', sourceBlockId: 'b1'),
          ProcessStep(order: 2, text: '· Rót ra phễu (mẫu).', sourceBlockId: 'b2'),
        ],
      );
      final e = explainForStep(s, s.steps.first);
      expect(e.verbatim, isNull);
      expect(e.withheldNote, contains('chưa đọc chắc'));
      expect(e.withheldNote, contains('không đoán hộ'));
      // hàng xóm là bước bị giữ lại ⇒ giá trị null, không phải chuỗi bịa
      expect(explainForStep(s, s.steps[1]).facts.single.value, isNull);
    });
  });

  group('B. chạm một CÁCH TÁCH ⇒ tách cái gì + bài này dùng ở đâu', () {
    test('từng chiều so sánh nguyên văn; sách không nói ⇒ giá trị null', () {
      final c = _cmp();
      final e0 = explainForEntity(c, 0);
      expect(e0.headline, 'Lọc');
      expect(e0.kicker, contains('Một trong 2 cách'));
      expect(e0.facts.single.name, 'Dùng để tách');
      expect(e0.facts.single.value, 'chất rắn không tan (mẫu)');
      // ô trống của sách KHÔNG được điền hộ
      expect(explainForEntity(c, 1).facts.single.value, isNull);
    });

    test('⭐ «liên hệ với nội dung bài» = sơ đồ KHÁC của cùng bài nhắc đúng từ',
        () {
      final c = _cmp();
      final e = explainForEntity(c, 0, alsoIn: [_proc(), c]);
      expect(e.links.map((l) => l.semanticId), ['p1']);
      expect(e.links.single.title, 'Lọc nước từ hỗn hợp (mẫu)');
      expect(e.linksEmptyNote, isNull);
    });

    test('⭐ không có liên hệ nào ⇒ NÓI THẲNG, không gợi bừa', () {
      final c = _cmp();
      final e = explainForEntity(c, 1, alsoIn: [_proc(), c]);
      expect(e.links, isEmpty);
      expect(e.linksEmptyNote, contains('chưa có sơ đồ riêng'));
      expect(e.linksEmptyNote, contains('Lắng'));
    });

    test('sơ đồ nguồn không tự liên hệ với chính nó', () {
      final c = _cmp();
      expect(explainForEntity(c, 0, alsoIn: [c]).links, isEmpty);
    });

    test('khớp trong LỜI BƯỚC, không chỉ tiêu đề', () {
      final c = _cmp();
      final p = _proc(
        id: 'p2',
        title: 'Tách dầu ăn khỏi nước (mẫu)',
        steps: const [
          ProcessStep(order: 1, text: '· Rót ra phễu chiết (mẫu).', sourceBlockId: 'x'),
          ProcessStep(order: 2, text: '· Để lắng vài phút (mẫu).', sourceBlockId: 'y'),
        ],
      );
      expect(
        explainForEntity(c, 1, alsoIn: [p, c]).links.map((l) => l.semanticId),
        ['p2'],
        reason: '«Lắng» xuất hiện trong lời bước của sơ đồ kia',
      );
    });
  });

  group('C. so khớp là NGUYÊN TỪ, không phải chuỗi con', () {
    test('có biên chữ cái hai đầu; không phân biệt hoa thường', () {
      expect(containsWord('Lọc nước từ hỗn hợp', 'Lọc'), isTrue);
      expect(containsWord('đem lọc lấy nước', 'Lọc'), isTrue, reason: 'hoa/thường');
      expect(containsWord('nước lọc.', 'lọc'), isTrue, reason: 'dấu câu là biên');
      expect(containsWord('phễu chiết', 'chiết'), isTrue);
      // chuỗi con giữa một từ dài hơn KHÔNG được tính
      expect(containsWord('lọcxyz', 'lọc'), isFalse);
      expect(containsWord('xyzlọc', 'lọc'), isFalse);
      // dấu tiếng Việt là chữ cái ⇒ «lo» không khớp «lọc»
      expect(containsWord('lọc', 'lo'), isFalse);
      expect(containsWord(null, 'lọc'), isFalse);
    });

    test('rút gọn lời bước: bỏ dấu đầu dòng, cắt có dấu «…»', () {
      expect(shortenStep('· Khuấy mạnh.'), 'Khuấy mạnh.');
      expect(shortenStep(null), isNull);
      final long = shortenStep('· ${'a' * 100}')!;
      expect(long.length, lessThanOrEqualTo(65));
      expect(long.endsWith('…'), isTrue);
    });
  });

  group('trên màn: chạm nút ⇒ giải thích ĐỨNG TRÊN nguồn', () {
    testWidgets('⭐⭐ chạm một cách tách ⇒ thấy chiều so sánh + liên hệ, rồi '
        'mới tới «Sách viết»', (t) async {
      final d = loadSyntheticDoc();
      await t.pumpWidget(
        fixtureHost(Scaffold(body: VisualView(doc: d, onShowInRead: (_) {}))),
      );
      await t.pumpAndSettle();
      final cmp = d.semantic.whereType<ComparisonSemantic>().first;
      final first = cmp.entities.first.name;
      await t.ensureVisible(find.text(first).first);
      await t.tap(find.text(first).first);
      await t.pumpAndSettle();
      expect(find.byKey(VisualExplainCard.rootKey), findsOneWidget);
      expect(find.byKey(VisualExplainCard.kickerKey), findsOneWidget);
      expect(find.text(explainLinksLabel), findsOneWidget);
      // giải thích TRƯỚC nguồn — không phải một sheet thứ hai
      expect(find.text('Sách viết'), findsOneWidget);
      expect(
        t.getTopLeft(find.byKey(VisualExplainCard.rootKey)).dy,
        lessThan(t.getTopLeft(find.text('Sách viết')).dy),
      );
    });

    testWidgets('⭐ chạm một bước ⇒ «Bước n trong N» + hàng xóm của bước', (
      t,
    ) async {
      final d = loadSyntheticDoc();
      final proc = d.semantic.whereType<ProcessSemantic>().first;
      await t.pumpWidget(
        fixtureHost(Scaffold(body: VisualView(doc: d, onShowInRead: (_) {}))),
      );
      await t.pumpAndSettle();
      await t.tap(find.textContaining('Bước hai'));
      await t.pumpAndSettle();
      expect(find.byKey(VisualExplainCard.rootKey), findsOneWidget);
      expect(
        find.textContaining('Bước 2 trong ${proc.steps.length} bước'),
        findsOneWidget,
      );
      expect(find.textContaining('Bước trước (bước 1)'), findsOneWidget);
    });

    testWidgets('⭐⭐ lời sách của bước KHÔNG in hai lần — block nguồn của '
        'sheet chính là bước ấy (lỗi máy thật vòng 2)', (t) async {
      final d = loadSyntheticDoc();
      final proc = d.semantic.whereType<ProcessSemantic>().first;
      final step = proc.steps.firstWhere((s) => s.text != null);
      await t.pumpWidget(
        fixtureHost(Scaffold(body: VisualView(doc: d, onShowInRead: (_) {}))),
      );
      await t.pumpAndSettle();
      await t.tap(find.byKey(ProcessFlowView.stepKey(step.order)));
      await t.pumpAndSettle();
      expect(find.byKey(VisualExplainCard.rootKey), findsOneWidget);
      // Phần «Sách viết ở bước này» BIẾN MẤT khi nó trùng phần nguồn ngay dưới.
      expect(find.text(explainVerbatimLabel), findsNothing);
      expect(find.text('Sách viết'), findsOneWidget);
      // Đếm TRONG sheet — sơ đồ phía sau vẫn còn trong cây widget, và nút của
      // nó mang đúng câu ấy một cách chính đáng.
      final shown = t
          .widgetList<Text>(
            find.descendant(
              of: find.byKey(const Key('source-sheet')),
              matching: find.byType(Text),
            ),
          )
          .map((w) => w.data ?? '')
          .where((s) => s.contains(step.text!.trim()))
          .length;
      expect(shown, 1, reason: 'một câu sách, in một lần trong sheet');
    });

    testWidgets('bước KHÔNG trùng block nguồn ⇒ vẫn in lời bước', (t) async {
      // Hai bước cùng trỏ về MỘT block: lời của bước ≠ lời cả block.
      final d = loadSyntheticDoc();
      final proc = d.semantic.whereType<ProcessSemantic>().first;
      final e = explainForStep(proc, proc.steps.first);
      expect(e.verbatim, isNotNull);
      expect(e.withoutVerbatim().verbatim, isNull);
      expect(e.withoutVerbatim().facts, e.facts);
      expect(e.withoutVerbatim().kicker, e.kicker);
    });
  });

  group('D. mã của views/ không khoá theo danh tính bài', () {
    /// Vòng 5 liệt kê hai tệp bằng tay. Vòng 7 thêm `visual_explain.dart` +
    /// `visual_explain_card.dart` vào cùng thư mục — danh sách tay thì tệp
    /// mới không bao giờ bị soi. Quét THƯ MỤC.
    test('⭐⭐ quét cả thư mục views/, không phải danh sách tay', () {
      final dir = Directory('lib/features/lesson_workspace/views');
      expect(dir.existsSync(), isTrue);
      final identity = RegExp(
        r'(KHTN|LS&ĐL|Bài\s*\d+|bai-\d+|0\d-sgk-|lessonNo\s*==|slotKey'
        r'|doc\.book\s*==|\.lessonNo\b)',
      );
      final scanned = <String>[];
      for (final f in dir.listSync(recursive: true).whereType<File>()) {
        if (!f.path.endsWith('.dart')) continue;
        scanned.add(f.path);
        // Chú thích được phép nêu tên bài đã chứng minh; MÃ thì không.
        final code = f
            .readAsLinesSync()
            .where((l) => !l.trimLeft().startsWith('//'))
            .where((l) => !l.trimLeft().startsWith('///'))
            .toList();
        for (final line in code) {
          expect(
            identity.hasMatch(line),
            isFalse,
            reason: '${f.path} khoá theo danh tính bài: «${line.trim()}»',
          );
        }
      }
      expect(scanned.length, greaterThanOrEqualTo(5));
    });

    test('lớp GIẢI THÍCH không chạm tới LessonDocument', () {
      for (final f in [
        'lib/features/lesson_workspace/views/visual_explain.dart',
        'lib/features/lesson_workspace/views/visual_explain_card.dart',
      ]) {
        expect(
          File(f).readAsStringSync(),
          isNot(contains('lesson_document.dart')),
          reason: '$f: lời giải thích chỉ được dựng từ dữ liệu CÓ KIỂU',
        );
      }
    });
  });
}
