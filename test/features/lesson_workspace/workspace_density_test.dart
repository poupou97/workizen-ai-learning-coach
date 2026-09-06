/// ROUND 5 · Lane B — ĐO MẬT ĐỘ MÀN WORKSPACE (phản hồi Founder trên máy).
///
/// Founder cầm máy: «lặp lại, tốn chiều dọc, quá nhiều hiện diện của cùng ba
/// Learning View, thẻ đề xuất chiếm chỗ thường trực, CTA lặp lại điều hướng
/// đã thấy». Trước khi đổi bất cứ thứ gì, ĐO — bằng cây widget ở đúng khung
/// nhìn Nokia 6.1 (1080×1920 @2.75 ⇒ 392.7×698.2 dp), không ước lượng bằng mắt.
///
/// Số đo (mỗi số là một câu trả lời được, không phải cảm giác):
///  - `chromeDp`  : chiều cao phần GHIM trên đầu (từ đỉnh tới đỉnh thân View)
///  - `firstContentDp` : Y của nội dung bài ĐẦU TIÊN (đã trừ cuộn)
///  - `viewLabels`: số lần ba tên View xuất hiện trên một màn
///  - `viewCtas`  : số nút/ô ĐỔI VIEW nhìn thấy (tab + thẻ + CTA)
/// Test này KHÔNG chốt ngưỡng đẹp — nó ghim SỰ THẬT hiện tại để so sánh A/B,
/// và ghim rằng phương án mới KHÔNG được tệ hơn ở các số đó.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/features/lesson_workspace/lesson_workspace_screen.dart';
import 'package:learning_coach/features/lesson_workspace/smart_book_view.dart';
import 'package:learning_coach/features/lesson_workspace/tutor_view.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/assist_layer.dart';
import 'package:learning_coach/features/lesson_workspace/visual_view.dart';
import 'package:learning_coach/features/lesson_workspace/workspace_trace.dart';

import 'support.dart';

/// Nokia 6.1 dọc.
void _nokia(WidgetTester t) {
  t.view.physicalSize = const Size(1080, 1920);
  t.view.devicePixelRatio = 2.75;
  addTearDown(t.view.reset);
}

Iterable<String> _texts(WidgetTester t) => t
    .widgetList<Text>(find.byType(Text))
    .map((w) => w.data ?? w.textSpan?.toPlainText() ?? '');

/// Số lần ba tên View xuất hiện trong chữ NHÌN THẤY.
int viewLabelHits(WidgetTester t) {
  var n = 0;
  for (final s in _texts(t)) {
    for (final v in WorkspaceView.values) {
      if (s.contains(v.label)) n++;
    }
  }
  return n;
}

/// Chiều cao phần ghim: đỉnh màn → đỉnh thân View.
double chromeDp(WidgetTester t, Finder body) => t.getTopLeft(body).dy;

void main() {
  group('§0 ĐO HIỆN TRẠNG — thứ Founder gọi là «lặp lại và tốn chiều dọc»', () {
    testWidgets('⭐ màn «Vào bài học»: ba tên View xuất hiện bao nhiêu lần', (
      t,
    ) async {
      _nokia(t);
      await t.pumpWidget(
        fixtureHost(
          LessonWorkspaceScreen(
            doc: loadSyntheticDoc(),
            trace: WorkspaceTrace(),
          ),
        ),
      );
      await t.pumpAndSettle();
      final hits = viewLabelHits(t);
      debugPrint('PICKER viewLabelHits=$hits');
      // ĐO ĐƯỢC: 5 — và con số này tự nó là một phát hiện. Ba View được gọi
      // bằng BA CÁCH khác nhau trên cùng màn: tab «Đọc / Trực quan / Học với
      // SAM», thẻ «Đọc như sách / Trực quan hoá / Học cùng SAM». Bộ đếm chỉ
      // bắt được 5 vì «Học cùng SAM» ≠ «Học với SAM» — tức là trẻ đọc SÁU
      // nhãn cho BA thứ, và hai trong số đó còn khác chữ.
      expect(
        hits,
        5,
        reason: 'màn chọn đang gọi ba View bằng hai bộ chữ khác nhau',
      );
    });

    testWidgets('⭐ trong một View: chrome ghim + số CTA đổi view', (t) async {
      _nokia(t);
      await t.pumpWidget(
        fixtureHost(
          LessonWorkspaceScreen(
            doc: loadSyntheticDoc(),
            trace: WorkspaceTrace(),
          ),
        ),
      );
      await t.pumpAndSettle();
      await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.read)));
      await t.pumpAndSettle();

      final chrome = chromeDp(t, find.byType(SmartBookView));
      final hits = viewLabelHits(t);
      debugPrint('READ chromeDp=$chrome viewLabelHits=$hits');
      expect(chrome, greaterThan(0));

      await t.tap(
        find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.visual)),
      );
      await t.pumpAndSettle();
      final chromeVisual = chromeDp(t, find.byType(VisualView));
      debugPrint(
        'VISUAL chromeDp=$chromeVisual '
        'viewLabelHits=${viewLabelHits(t)}',
      );

      await t.tap(
        find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.tutor)),
      );
      await t.pumpAndSettle();
      final chromeTutor = chromeDp(t, find.byType(TutorView));
      debugPrint(
        'TUTOR chromeDp=$chromeTutor '
        'viewLabelHits=${viewLabelHits(t)}',
      );

      // Màn Học với SAM còn GHIM thẻ đề xuất ⇒ chrome cao hơn Đọc/Trực quan.
      expect(
        chromeTutor,
        greaterThan(chromeVisual),
        reason:
            'thẻ đề xuất vẫn ghim ở Học với SAM (vòng 4/5 chỉ gỡ ở Đọc '
            'và Trực quan) — đây chính là chỗ Founder thấy tốn chiều dọc',
      );
    });

    testWidgets('⭐ thẻ «SAM đề xuất» có mặt ở CẢ BA View — nó thường trực', (
      t,
    ) async {
      _nokia(t);
      await t.pumpWidget(
        fixtureHost(
          LessonWorkspaceScreen(
            doc: loadSyntheticDoc(),
            trace: WorkspaceTrace(),
          ),
        ),
      );
      await t.pumpAndSettle();
      for (final v in WorkspaceView.values) {
        await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(v)));
        await t.pumpAndSettle();
        expect(
          find.byKey(LessonWorkspaceScreen.nextActionKey),
          findsOneWidget,
          reason: 'đề xuất hiện thường trực ở ${v.label}',
        );
      }
    });
  });

  group('§1 SO SÁNH A/B/C — cùng bài, cùng trạng thái, cùng khung nhìn', () {
    tearDown(() => AssistPresentation.debugOverride = null);

    /// Đo một phương án trên CẢ BA View. Trả về map để in thành bảng.
    Future<Map<String, Object>> measure(
      WidgetTester t,
      AssistPresentation mode,
    ) async {
      AssistPresentation.debugOverride = mode;
      _nokia(t);
      await t.pumpWidget(
        fixtureHost(
          LessonWorkspaceScreen(
            doc: loadSyntheticDoc(),
            trace: WorkspaceTrace(),
          ),
        ),
      );
      await t.pumpAndSettle();
      final out = <String, Object>{};
      for (final v in WorkspaceView.values) {
        await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(v)));
        await t.pumpAndSettle();
        final body = switch (v) {
          WorkspaceView.read => find.byType(SmartBookView),
          WorkspaceView.visual => find.byType(VisualView),
          WorkspaceView.tutor => find.byType(TutorView),
        };
        out['chrome.${v.name}'] = chromeDp(t, body);
        out['labels.${v.name}'] = viewLabelHits(t);
      }
      return out;
    }

    testWidgets('⭐⭐ bảng số: chrome ghim (dp) và số nhãn View, bốn phương án', (
      t,
    ) async {
      final rows = <AssistPresentation, Map<String, Object>>{};
      for (final m in AssistPresentation.values) {
        rows[m] = await measure(t, m);
      }
      for (final e in rows.entries) {
        debugPrint(
          'ASSIST ${e.key.flagName.padRight(10)} '
          'chrome read=${e.value['chrome.read']} '
          'visual=${e.value['chrome.visual']} '
          'tutor=${e.value['chrome.tutor']} | '
          'labels read=${e.value['labels.read']} '
          'visual=${e.value['labels.visual']} '
          'tutor=${e.value['labels.tutor']}',
        );
      }
      final card = rows[AssistPresentation.card]!;
      for (final m in [
        AssistPresentation.icon,
        AssistPresentation.peek,
        AssistPresentation.inlineTab,
      ]) {
        expect(
          rows[m]!['chrome.tutor']! as double,
          lessThan(card['chrome.tutor']! as double),
          reason:
              '${m.flagName} phải trả lại chiều dọc ở Học với SAM — đó là '
              'màn Founder thấy tốn nhất (411 dp = 58.9 % khung nhìn)',
        );
      }
    });

    testWidgets(
      '⭐ AI-FIRST KHÔNG BIẾN MẤT: mọi phương án đều cho trẻ thấy có gợi ý và '
      'mở được «vì sao» — không có phương án nào chỉ giấu đi',
      (t) async {
        for (final m in AssistPresentation.values) {
          AssistPresentation.debugOverride = m;
          _nokia(t);
          await t.pumpWidget(
            fixtureHost(
              LessonWorkspaceScreen(
                doc: loadSyntheticDoc(),
                trace: WorkspaceTrace(),
              ),
            ),
          );
          await t.pumpAndSettle();
          await t.tap(
            find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.tutor)),
          );
          await t.pumpAndSettle();
          final visible = switch (m) {
            AssistPresentation.card => find.byKey(
              LessonWorkspaceScreen.nextActionKey,
            ),
            AssistPresentation.icon => find.byKey(AssistIconButton.buttonKey),
            AssistPresentation.peek => find.byKey(AssistPeek.peekKey),
            AssistPresentation.inlineTab => find.byKey(
              const Key('assist-tab-badge'),
            ),
          };
          expect(
            visible,
            findsOneWidget,
            reason: '${m.flagName}: đề xuất phải NHÌN THẤY ĐƯỢC, không bị giấu',
          );
        }
      },
    );

    testWidgets('⭐ B: hé → mở → «Để sau» → thu gọn; đề xuất MỚI thì hé lại', (
      t,
    ) async {
      AssistPresentation.debugOverride = AssistPresentation.peek;
      _nokia(t);
      await t.pumpWidget(
        fixtureHost(
          LessonWorkspaceScreen(
            doc: loadSyntheticDoc(),
            trace: WorkspaceTrace(),
          ),
        ),
      );
      await t.pumpAndSettle();
      await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.read)));
      await t.pumpAndSettle();
      expect(find.byKey(AssistPeek.peekKey), findsOneWidget);
      expect(find.textContaining('SAM gợi ý:'), findsOneWidget);
      await t.tap(find.byKey(AssistPeek.peekKey));
      await t.pumpAndSettle();
      expect(find.byKey(AssistPeek.expandedKey), findsOneWidget);
      expect(find.byKey(AssistPeek.goKey), findsOneWidget);
      await t.tap(find.byKey(AssistPeek.dismissKey));
      await t.pumpAndSettle();
      expect(find.byKey(AssistPeek.peekKey), findsNothing);
      expect(find.byKey(AssistPeek.expandedKey), findsNothing);
      // Đổi View ⇒ đề xuất trỏ đi chỗ KHÁC ⇒ hé lại một lần.
      await t.tap(
        find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.visual)),
      );
      await t.pumpAndSettle();
      expect(find.byKey(AssistPeek.peekKey), findsOneWidget);
    });

    testWidgets('⭐ A: 💡 mở bottom sheet có lý do + một CTA; CTA đổi View', (
      t,
    ) async {
      AssistPresentation.debugOverride = AssistPresentation.icon;
      _nokia(t);
      await t.pumpWidget(
        fixtureHost(
          LessonWorkspaceScreen(
            doc: loadSyntheticDoc(),
            trace: WorkspaceTrace(),
          ),
        ),
      );
      await t.pumpAndSettle();
      await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.read)));
      await t.pumpAndSettle();
      await t.tap(find.byKey(AssistIconButton.buttonKey));
      await t.pumpAndSettle();
      expect(find.byKey(const Key('assist-sheet')), findsOneWidget);
      expect(find.textContaining('Gợi ý của SAM'), findsWidgets);
      await t.tap(find.byKey(AssistPeek.goKey));
      await t.pumpAndSettle();
      expect(find.byType(VisualView), findsOneWidget);
    });

    testWidgets(
      '⭐ C: huy hiệu 💡 nằm trên TAB được đề xuất, không thêm dòng; chạm huy '
      'hiệu mới mở «vì sao»',
      (t) async {
        AssistPresentation.debugOverride = AssistPresentation.inlineTab;
        _nokia(t);
        await t.pumpWidget(
          fixtureHost(
            LessonWorkspaceScreen(
              doc: loadSyntheticDoc(),
              trace: WorkspaceTrace(),
            ),
          ),
        );
        await t.pumpAndSettle();
        await t.tap(
          find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.read)),
        );
        await t.pumpAndSettle();
        expect(find.byKey(const Key('assist-tab-badge')), findsOneWidget);
        expect(find.byKey(AssistPeek.expandedKey), findsNothing);
        await t.tap(find.byKey(const Key('assist-tab-badge')));
        await t.pumpAndSettle();
        expect(find.byKey(AssistPeek.expandedKey), findsOneWidget);
      },
    );

    test('⭐⭐ KHÔNG CÓ ĐỘNG CƠ THỨ HAI: lớp trợ giúp không đọc bài, không đọc '
        'trace — chỉ nhận NextAction', () {
      // Chỉ soi MÃ, không soi chú thích: chú thích được phép NHẮC TÊN thứ
      // mà lớp này bị cấm dùng (đó chính là chỗ ghi lý do cấm).
      final src =
          File('lib/features/lesson_workspace/widgets/assist_layer.dart')
              .readAsLinesSync()
              .where((l) => !l.trimLeft().startsWith('//'))
              .join('\n');
      for (final forbidden in [
        'LessonDocument',
        'WorkspaceTrace',
        'nextActionFor',
        'founderNextAction',
        'lesson_document.dart',
      ]) {
        expect(
          src,
          isNot(contains(forbidden)),
          reason: 'assist_layer chỉ được TRÌNH BÀY một NextAction có sẵn',
        );
      }
    });

    testWidgets('⭐⭐ Y của NỘI DUNG BÀI đầu tiên ở Trực quan — số thật mà trẻ '
        'thấy (thẻ đề xuất của bản cũ nằm TRONG vùng cuộn nên chrome ghim '
        'không kể hết)', (t) async {
      final firstContent = <String, double>{};
      for (final m in AssistPresentation.values) {
        AssistPresentation.debugOverride = m;
        _nokia(t);
        await t.pumpWidget(
          fixtureHost(
            LessonWorkspaceScreen(
              doc: loadSyntheticDoc(),
              trace: WorkspaceTrace(),
            ),
          ),
        );
        await t.pumpAndSettle();
        await t.tap(
          find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.visual)),
        );
        await t.pumpAndSettle();
        firstContent[m.flagName] = t
            .getTopLeft(find.byKey(VisualView.shapeKey('Sơ đồ quy trình')))
            .dy;
      }
      for (final e in firstContent.entries) {
        debugPrint('FIRSTCONTENT ${e.key.padRight(10)} y=${e.value} dp');
      }
      for (final m in ['icon', 'peek', 'inlineTab']) {
        expect(
          firstContent[m]!,
          lessThan(firstContent['card']!),
          reason: '$m phải đưa nội dung bài lên cao hơn bản hiện tại',
        );
      }
    });
  });
}
