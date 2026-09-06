/// ROUND 6 · WS-D — **GOLDEN #1: LS&ĐL 5 Bài 8** «Đấu tranh giành độc lập thời
/// kì Bắc thuộc» (SGK trang 36–39).
///
/// Đây là chỗ chuỗi giao hàng được ghim ở phía APP:
///
///   nguồn thật → SDM → sổ sửa (repair ledger) → `ValidatedRepair`
///     → TSL đã chiếu → LessonDocument → `assets/fixtures/real/`
///     → `WorkspaceCatalog` chọn ĐƯỜNG THẬT → ba Learning View → máy thật
///
/// ⚠ `assets/fixtures/real/` nằm trong `.gitignore` (Founder D4: chữ SGK
/// nguyên văn và ảnh cắt trang là NỘI BỘ / NGHIÊN CỨU, không phát hành, không
/// commit). Nên mọi test ở đây **bỏ qua** khi máy chưa sinh fixture — KHÔNG
/// xanh giả. Vòng 5 đã mất thời gian vì một fixture cũ nằm im trong
/// `.gitignore` và đọc như một test đạt; ở đây «không có file» phải nói thẳng
/// là không có file.
///
/// ⚠ VALIDATED REPAIR ≠ TRUSTED. Test nặng nhất trong tệp này không kiểm rằng
/// bản sửa ĐẾN ĐƯỢC trẻ — nó kiểm rằng bản sửa **KHÔNG** đến được trẻ: vùng đã
/// sửa và đã kiểm vẫn withheld, vẫn không mang chữ. `CONNECT ≠ TRUST`.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';
import 'package:learning_coach/features/lesson_workspace/lesson_workspace_screen.dart';
import 'package:learning_coach/features/lesson_workspace/smart_book_view.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/fixture_chip.dart';
import 'package:learning_coach/features/lesson_workspace/workspace_trace.dart';

import 'support.dart';

const _slot = FixtureSlot(book: '05-sgk-lich-su-va-dia-li-5', lessonNo: 8);

Map<String, Object?>? _rawGolden() {
  final f = File(_slot.realPath);
  if (!f.existsSync()) {
    markTestSkipped(
      'Golden #1 chưa sinh trên máy này — chạy '
      'tool/evidence/golden_delivery.py (cần poc-out/)',
    );
    return null;
  }
  return (jsonDecode(f.readAsStringSync()) as Map).cast<String, Object?>();
}

LessonDocument? _goldenDoc() {
  final j = _rawGolden();
  if (j == null) return null;
  final d = LessonDocument.fromJson(j, assetBase: FixtureSlot.realDir);
  expect(
    d,
    isNotNull,
    reason:
        'Golden #1 phải PARSE ĐƯỢC bằng chính mã app này. `fromJson` hạ CẢ '
        'tài liệu khi gặp một loại khối lạ — nên nếu WS-C phát một loại khối '
        'mới ra pack mà app chưa biết, cả bài trắng. Pack và app đi cùng nhau.',
  );
  return d;
}

void main() {
  group('§1 CHUỖI GIAO HÀNG — nguồn → TSL đã chiếu → tài liệu → app', () {
    test('⭐⭐ ĐƯỜNG THẬT thắng ĐƯỜNG MẪU: catalog nạp fixture thật, không rơi '
        'về bản mẫu', () async {
      final raw = _rawGolden();
      if (raw == null) return;
      // Bundle chỉ có ĐÚNG hai tệp: đường thật và đường mẫu. Nếu catalog vẫn
      // chọn bản mẫu thì đây là chỗ biết ngay.
      final catalog = WorkspaceCatalog(
        bundle: fixtureBundleWith({
          _slot.realPath: File(_slot.realPath).readAsStringSync(),
          _slot.syntheticPath: File(_slot.syntheticPath).readAsStringSync(),
        }),
        slots: const [_slot],
      );
      await catalog.load();
      final doc = catalog.docFor(_slot.book, _slot.lessonNo);
      expect(doc, isNotNull, reason: 'Golden #1 phải có mặt trong catalog');
      expect(
        doc!.provenance.trust,
        ContentTrust.trustedStructuredLesson,
        reason:
            'bản MẪU mang `fixtureSynthetic`; thấy giá trị đó nghĩa là app đang '
            'phục vụ chữ [MẪU] chứ không phải chữ sách',
      );
      // Không một đoạn nào được là chữ bịa.
      final texts = doc.blocks.whereType<ParagraphBlock>().map((b) => b.text);
      expect(
        texts.where((t) => t.contains('[MẪU]')),
        isEmpty,
        reason: 'chữ [MẪU] lọt vào đường thật ⇒ đang trộn hai thế hệ',
      );
      expect(WorkspaceCatalog.isResearchSlot(doc), isTrue);
    });

    test('⭐ tài liệu khai ĐỦ NĂM TRƯỜNG PHIÊN BẢN Founder yêu cầu', () {
      final raw = _rawGolden();
      if (raw == null) return;
      final p = (raw['provenance'] as Map).cast<String, Object?>();
      for (final k in [
        'sourceHash',
        'pipelineVersion',
        'sdmVersion',
        'generator',
        'tslPath',
      ]) {
        expect(
          (p[k] as String?)?.trim(),
          isNotEmpty,
          reason:
              '`assets/fixtures/real/` nằm trong .gitignore — bản ghi BÊN '
              'TRONG tệp là cách duy nhất người đọc sau biết mình đang cầm thế '
              'hệ nào. Thiếu `$k` là mất khả năng ấy.',
        );
      }
      final repair = p['repair'];
      expect(
        repair,
        isA<Map<Object?, Object?>>(),
        reason: 'Golden #1 phải mang XUẤT XỨ SỬA CHỮA, không chỉ xuất xứ nguồn',
      );
      final r = (repair! as Map).cast<String, Object?>();
      expect(r['projection'] ?? r['version'], isNotNull);
      expect(
        r['trusted'],
        0,
        reason:
            '⭐ CONNECT ≠ TRUST — không một bản sửa nào được TRUSTED. Ngưỡng tin '
            'sản xuất là cổng của Founder, không phải của pipeline.',
      );
    });
  });

  group('§2 VALIDATED REPAIR ≠ TRUSTED — bản sửa KHÔNG được tới trẻ', () {
    test('⭐⭐ mọi vùng đã sửa vẫn WITHHELD và vẫn KHÔNG mang chữ', () {
      final raw = _rawGolden();
      if (raw == null) return;
      final blocks = (raw['blocks'] as List).cast<Map<Object?, Object?>>();
      final repaired = [
        for (final b in blocks)
          if (b['repair'] != null) b.cast<String, Object?>(),
      ];
      expect(
        repaired,
        isNotEmpty,
        reason: 'Golden #1 tồn tại để CHẠY QUA một ca sửa thật',
      );
      for (final b in repaired) {
        expect(b['type'], 'withheld', reason: 'khối ${b['id']}');
        expect(b['trust'], 'withheld', reason: 'khối ${b['id']}');
        expect(
          b.containsKey('text'),
          isFalse,
          reason:
              '⭐ khối ${b['id']} mang chữ. Một bản sửa ĐÃ KIỂM vẫn là ĐỀ XUẤT: '
              'giá trị đề xuất không được rời khỏi corpus, và trẻ không được '
              'đọc nó như chữ sách.',
        );
      }
    });

    test('⭐ chỗ SAM để trống hiện ra như CHỖ TRỐNG CÓ LÝ DO, không phải chữ '
        'hỏng — mô hình app cũng không mang chữ', () {
      final doc = _goldenDoc();
      if (doc == null) return;
      final withheld = doc.blocks.whereType<WithheldBlock>().toList();
      expect(withheld, isNotEmpty);
      for (final w in withheld) {
        expect(w.reasons, isNotEmpty, reason: 'mỗi chỗ trống phải nêu LÝ DO');
      }
    });
  });

  group('§3 TRÊN MÀN HÌNH — thứ trẻ thật sự thấy', () {
    testWidgets('⭐ ba View mở được trên bài THẬT; chip «chưa kiểm định» bắt '
        'buộc còn nguyên', (t) async {
      final doc = _goldenDoc();
      if (doc == null) return;
      t.view.physicalSize = const Size(1080, 1920);
      t.view.devicePixelRatio = 2.75;
      addTearDown(t.view.reset);
      await t.pumpWidget(
        fixtureHost(LessonWorkspaceScreen(doc: doc, trace: WorkspaceTrace())),
      );
      await t.pumpAndSettle();
      expect(
        find.byType(FixtureChip),
        findsOneWidget,
        reason: 'chưa có tài liệu trustedCorpus nào — chip là bắt buộc',
      );
      expect(find.textContaining('trang 36–39'), findsWidgets);
      for (final v in WorkspaceView.values) {
        await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(v)));
        await t.pumpAndSettle();
      }
      await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.read)));
      await t.pumpAndSettle();
      expect(find.byType(SmartBookView), findsOneWidget);
    });

    testWidgets('⭐⭐ BẢN GHI SỬA KHÔNG MANG GIÁ TRỊ ĐỀ XUẤT — không có chữ nào '
        'để lọt lên màn Đọc, kể cả khi ai đó vẽ nhầm', (t) async {
      final raw = _rawGolden();
      if (raw == null) return;
      final doc = _goldenDoc();
      if (doc == null) return;

      // ĐO ĐƯỢC (2026-09-06): bản ghi sửa của Golden #1 mang repairId ·
      // disposition · failureClass · method · repairVersion · validatorId ·
      // validatorVersion · verdict · supportingLayers · changed · servable ·
      // structuredKind · caps · textLen — và KHÔNG mang một trường chữ nào.
      // Đó chính là bảo đảm: giá trị đề xuất không rời khỏi corpus, nên
      // không có gì để một lỗi vẽ làm lộ ra. Test này ghim ĐIỀU ĐÓ, chứ
      // không đi tìm một chuỗi mà theo cấu tạo không tồn tại — một test đi
      // tìm cái không có mặt sẽ XANH kể cả khi bảo đảm bị gỡ bỏ.
      const textBearing = {
        'text',
        'repairedText',
        'candidate',
        'candidateText',
        'proposed',
        'proposedText',
        'value',
        'after',
        'replacement',
        'original',
        'observed',
      };
      var seen = 0;
      for (final b in (raw['blocks']! as List).cast<Map<Object?, Object?>>()) {
        final r = b['repair'];
        if (r is! Map) continue;
        seen++;
        for (final k in r.keys) {
          expect(
            textBearing.contains(k),
            isFalse,
            reason:
                '⭐ bản ghi sửa của khối ${b['id']} mang trường «$k». Giá trị '
                'ĐỀ XUẤT không được rời khỏi corpus: một khi nó nằm trong tài '
                'liệu app nạp, chỉ còn kỷ luật của người vẽ ngăn nó tới trẻ.',
          );
        }
        expect(r['servable'], isFalse, reason: 'khối ${b['id']}');
        expect(r['disposition'], 'VALIDATED_REPAIR', reason: 'khối ${b['id']}');
      }
      expect(seen, greaterThan(0));

      // Và trên màn thật: chỗ đã sửa vẫn là CHỖ TRỐNG CÓ LÝ DO.
      t.view.physicalSize = const Size(1080, 1920);
      t.view.devicePixelRatio = 2.75;
      addTearDown(t.view.reset);
      await t.pumpWidget(
        fixtureHost(
          LessonWorkspaceScreen(
            doc: doc,
            trace: WorkspaceTrace(),
            initialView: WorkspaceView.read,
          ),
        ),
      );
      await t.pumpAndSettle();
      expect(find.byType(SmartBookView), findsOneWidget);
      final onScreen = t
          .widgetList<Text>(find.byType(Text))
          .map((w) => w.data ?? w.textSpan?.toPlainText() ?? '')
          .join('\n');
      expect(
        onScreen.contains('VALIDATED_REPAIR'),
        isFalse,
        reason: 'từ vựng của pipeline không phải chữ cho trẻ đọc',
      );
    });
  });
}
