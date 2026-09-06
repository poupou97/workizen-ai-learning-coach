/// ROUND 6 · WS-D — MẬT ĐỘ MÀN WORKSPACE SAU KHI THI HÀNH **PHƯƠNG ÁN B**.
///
/// Vòng 5 đo hiện trạng và dựng bốn cách trình bày cùng một `NextAction` từ
/// MỘT commit, rồi đo cả bốn trên Nokia 6.1. **Founder chọn B.** Tệp này
/// không còn so A/B/C — nó ghim NHỮNG GÌ B PHẢI GIỮ ĐÚNG.
///
/// ── SỐ ĐO LỊCH SỬ (không tái dựng được ở nhánh này, và đó là chủ ý) ──
/// Máy thật, Nokia 6.1, KHTN 6 Bài 17, cùng chuỗi chạm, Y của nội dung bài
/// đầu tiên ở «Học với SAM»:
///     card (vòng 4/5)  820 px · 42.7 % màn
///     A icon           634 px · 33.0 %
///     B peek (đang hé) 712 px · 37.1 %   ← ĐÃ CHỌN
///     B peek (thu gọn) 634 px · 33.0 %
///     C inlineTab      565 px · 29.4 %
/// Cây widget, khung Nokia 392.7×698.2 dp: chrome ghim ở «Học với SAM»
/// 411 dp (58.9 % khung nhìn) → 281 dp (B); nhãn View nhìn thấy 7 → 4.
/// Nguồn: `docs/design/TRACK-B-ROUND5-WORKSPACE-DUPLICATION.md` §5; tái dựng
/// được ở nhánh `lane-b/round5-experience` (PR #87). B thắng KHÔNG bằng
/// pixel — C gọn hơn — mà vì B nói ĐÍCH ĐẾN với 0 chạm và mở được «vì sao»
/// tại chỗ.
///
/// Số đo ở đây dùng fixture MẪU nên chạy được trên bản sao sạch.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/features/lesson_workspace/lesson_workspace_screen.dart';
import 'package:learning_coach/features/lesson_workspace/smart_book_view.dart';
import 'package:learning_coach/features/lesson_workspace/tutor_view.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/assist_layer.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/mode_picker.dart';
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

Finder _bodyOf(WorkspaceView v) => switch (v) {
  WorkspaceView.read => find.byType(SmartBookView),
  WorkspaceView.visual => find.byType(VisualView),
  WorkspaceView.tutor => find.byType(TutorView),
};

Future<void> _open(WidgetTester t) async {
  _nokia(t);
  await t.pumpWidget(
    fixtureHost(
      LessonWorkspaceScreen(doc: loadSyntheticDoc(), trace: WorkspaceTrace()),
    ),
  );
  await t.pumpAndSettle();
}

void main() {
  group('§1 MỘT BỘ CHỮ CHO BA VIEW — lỗi vòng 5 tìm ra, vòng 6 đóng', () {
    testWidgets('⭐⭐ mọi nhãn View trên màn «Vào bài học» đều là chữ của '
        '`WorkspaceView.label` — không có bộ chữ thứ hai', (t) async {
      // Vòng 5 đo được bộ đếm ra 5 chứ không phải 6, và CHÍNH CON SỐ ẤY là
      // phát hiện: «Học cùng SAM» (thẻ) ≠ «Học với SAM» (tab) nên bộ đếm
      // trượt một lần. Trẻ đọc SÁU nhãn cho BA thứ, hai trong số đó khác chữ.
      //
      // Đếm số lần xuất hiện KHÔNG bắt được lỗi này (nó chỉ trượt xuống). Nên
      // test đo đúng thứ hỏng: mỗi tên View phải xuất hiện ĐỦ số lần dự kiến
      // — 2 (một trên tab, một trên thẻ) — chứ không phải 1.
      await _open(t);
      expect(find.byKey(const Key('mode-picker')), findsOneWidget);
      final all = _texts(t).toList();
      for (final v in WorkspaceView.values) {
        final hits = all.where((s) => s.contains(v.label)).length;
        expect(
          hits,
          2,
          reason:
              '«${v.label}» phải xuất hiện đúng 2 lần (tab + thẻ) trên màn '
              'chọn — nếu là 1 thì thẻ đang dùng một bộ chữ khác',
        );
      }
      expect(
        viewLabelHits(t),
        6,
        reason: 'ba View × (tab + thẻ) = 6, tất cả cùng một bộ chữ',
      );
      // Bộ chữ CŨ đã biến mất hẳn khỏi màn.
      for (final gone in ['Học cùng SAM', 'Đọc như sách', 'Trực quan hoá']) {
        expect(
          all.where((s) => s.contains(gone)),
          isEmpty,
          reason: '«$gone» là bộ chữ thứ hai — đã bỏ',
        );
      }
    });

    test('⭐ nguồn: `ModePicker` không được có bảng tên riêng', () {
      final src = File('lib/features/lesson_workspace/widgets/mode_picker.dart')
          .readAsLinesSync()
          .where((l) => !l.trimLeft().startsWith('//'))
          .join('\n');
      for (final gone in ['Học cùng SAM', 'Đọc như sách', 'Trực quan hoá']) {
        expect(
          src,
          isNot(contains(gone)),
          reason: 'tên View chỉ có MỘT nguồn: WorkspaceView.label',
        );
      }
    });
  });

  group('§2 CHIỀU DỌC — thứ Founder gọi là «lặp lại và tốn chiều dọc»', () {
    testWidgets('⭐⭐ ba View có CÙNG chiều cao phần ghim; không View nào phải '
        'trả giá cho một thẻ đề xuất', (t) async {
      await _open(t);
      final chrome = <WorkspaceView, double>{};
      final labels = <WorkspaceView, int>{};
      for (final v in WorkspaceView.values) {
        await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(v)));
        await t.pumpAndSettle();
        chrome[v] = chromeDp(t, _bodyOf(v));
        labels[v] = viewLabelHits(t);
      }
      for (final v in WorkspaceView.values) {
        debugPrint(
          'B ${v.name.padRight(7)} chrome=${chrome[v]} dp '
          'labels=${labels[v]}',
        );
      }
      // Vòng 5: 411 dp ở «Học với SAM» so với 225 dp ở hai View kia — thẻ đề
      // xuất ghim chỉ ở đó. Nay không còn thẻ ⇒ ba số phải bằng nhau.
      expect(
        chrome[WorkspaceView.tutor],
        chrome[WorkspaceView.visual],
        reason: 'Học với SAM không còn ghim thêm gì so với Trực quan',
      );
      expect(chrome[WorkspaceView.read], chrome[WorkspaceView.visual]);
      // Trần cứng: phần ghim của B là tiêu đề + chip + tab + MỘT dòng gợi ý.
      // 411 dp = 58.9 % khung nhìn là con số Founder phàn nàn; ghim ở đây để
      // không ai lặng lẽ nhồi lại một thẻ nữa.
      expect(
        chrome[WorkspaceView.tutor]!,
        lessThan(300),
        reason: 'vòng 5 đo 411 dp ở đúng màn này',
      );
    });

    testWidgets('⭐ dòng gợi ý tốn ĐÚNG một dòng; thu gọn thì trả lại cả dòng '
        'ấy mà không biến mất', (t) async {
      await _open(t);
      await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.read)));
      await t.pumpAndSettle();
      final withPeek = chromeDp(t, _bodyOf(WorkspaceView.read));
      final peekBox = t.getSize(find.byKey(AssistPeek.peekKey));
      expect(
        peekBox.height,
        greaterThanOrEqualTo(48),
        reason: 'vùng chạm ≥ 48 dp',
      );
      expect(peekBox.height, lessThan(72), reason: 'một dòng, không phải thẻ');

      await t.tap(find.byKey(AssistPeek.peekKey));
      await t.pumpAndSettle();
      await t.tap(find.byKey(AssistPeek.dismissKey));
      await t.pumpAndSettle();
      final collapsed = chromeDp(t, _bodyOf(WorkspaceView.read));
      debugPrint('B peek chrome=$withPeek dp → collapsed=$collapsed dp');
      expect(
        collapsed,
        lessThan(withPeek),
        reason: '«Để sau» phải trả lại chiều dọc',
      );
      // ⚠ «hé dần, KHÔNG phải giấu đi» (lỗi D5 máy thật, vòng 5).
      expect(find.byKey(AssistIconButton.buttonKey), findsOneWidget);
    });
  });

  group('§3 B PHẢI GIỮ ĐÚNG — những điều không được đánh đổi', () {
    testWidgets('⭐⭐ ĐỀ XUẤT NHÌN THẤY ĐƯỢC Ở CẢ BA VIEW, ở cả ba trạng thái', (
      t,
    ) async {
      await _open(t);
      for (final v in WorkspaceView.values) {
        await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(v)));
        await t.pumpAndSettle();
        // PEEK (mặc định): nói ĐÍCH ĐẾN với 0 chạm.
        expect(
          find.byKey(AssistPeek.peekKey),
          findsOneWidget,
          reason: '${v.label}: PEEK phải thấy được',
        );
        expect(find.textContaining('SAM gợi ý:'), findsOneWidget);
        // EXPANDED: «vì sao» mở TẠI CHỖ, không phải sang màn khác.
        await t.tap(find.byKey(AssistPeek.peekKey));
        await t.pumpAndSettle();
        expect(find.byKey(AssistPeek.expandedKey), findsOneWidget);
        expect(find.byKey(AssistPeek.goKey), findsOneWidget);
        // COLLAPSED: vẫn còn dấu hiệu, không biến mất.
        await t.tap(find.byKey(AssistPeek.dismissKey));
        await t.pumpAndSettle();
        expect(
          find.byKey(AssistIconButton.buttonKey),
          findsOneWidget,
          reason: '${v.label}: thu gọn KHÔNG được giấu hẳn đề xuất',
        );
        // Chạm 💡 ⇒ mở lại TẠI CHỖ (không bottom sheet — đó là phương án A).
        await t.tap(find.byKey(AssistIconButton.buttonKey));
        await t.pumpAndSettle();
        expect(find.byKey(AssistPeek.expandedKey), findsOneWidget);
        expect(find.byKey(const Key('assist-sheet')), findsNothing);
      }
    });

    testWidgets('⭐ đề xuất trỏ sang View KHÁC ⇒ hé lại một lần', (t) async {
      await _open(t);
      await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.read)));
      await t.pumpAndSettle();
      await t.tap(find.byKey(AssistPeek.peekKey));
      await t.pumpAndSettle();
      await t.tap(find.byKey(AssistPeek.dismissKey));
      await t.pumpAndSettle();
      expect(find.byKey(AssistPeek.peekKey), findsNothing);
      await t.tap(
        find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.visual)),
      );
      await t.pumpAndSettle();
      expect(find.byKey(AssistPeek.peekKey), findsOneWidget);
    });

    testWidgets('⭐ trợ năng: nhãn + gợi ý cho trình đọc màn hình ở mọi dấu '
        'hiệu; vùng chạm ≥ 48 dp', (t) async {
      final handle = t.ensureSemantics();
      await _open(t);
      await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.read)));
      await t.pumpAndSettle();
      expect(
        find.bySemanticsLabel(RegExp('Gợi ý của SAM: xem')),
        findsWidgets,
        reason: '💡 một mình không đủ cho trình đọc màn hình',
      );
      await t.tap(find.byKey(AssistPeek.peekKey));
      await t.pumpAndSettle();
      await t.tap(find.byKey(AssistPeek.dismissKey));
      await t.pumpAndSettle();
      final icon = t.getSize(find.byKey(AssistIconButton.buttonKey));
      expect(icon.width, greaterThanOrEqualTo(48));
      expect(icon.height, greaterThanOrEqualTo(48));
      expect(find.bySemanticsLabel(RegExp('Gợi ý của SAM: xem')), findsWidgets);
      handle.dispose();
    });

    testWidgets('⭐ bàn phím lên (trẻ đang gõ trả lời SAM) ⇒ gợi ý nhường chỗ', (
      t,
    ) async {
      _nokia(t);
      await t.pumpWidget(
        fixtureHost(
          LessonWorkspaceScreen(
            doc: loadSyntheticDoc(),
            trace: WorkspaceTrace(),
            initialView: WorkspaceView.tutor,
          ),
        ),
      );
      await t.pumpAndSettle();
      expect(find.byKey(AssistPeek.peekKey), findsOneWidget);
      t.view.viewInsets = const FakeViewPadding(bottom: 800);
      await t.pumpAndSettle();
      expect(find.byKey(AssistPeek.peekKey), findsNothing);
      expect(find.byKey(AssistIconButton.buttonKey), findsNothing);
    });

    testWidgets('⭐ ở màn «Vào bài học» KHÔNG có lớp trợ giúp — lý do đã nằm '
        'trên thẻ được đề xuất, không lặp', (t) async {
      await _open(t);
      expect(
        find.byKey(ModePicker.cardKey(WorkspaceView.read)),
        findsOneWidget,
      );
      expect(find.byKey(AssistPeek.peekKey), findsNothing);
      expect(find.byKey(AssistIconButton.buttonKey), findsNothing);
    });

    test('⭐⭐ KHÔNG CÓ ĐỘNG CƠ THỨ HAI: lớp trợ giúp không đọc bài, không đọc '
        'trace — chỉ nhận NextAction và những chuỗi đã dựng sẵn', () {
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

    test('⭐ cờ so A/B đã gỡ: bản dựng chỉ còn MỘT cách trình bày', () {
      // Founder đã chọn. Để lại `--dart-define` là để thí nghiệm chạy tiếp,
      // không phải thi hành quyết định.
      for (final f in [
        'lib/features/lesson_workspace/widgets/assist_layer.dart',
        'lib/features/lesson_workspace/lesson_workspace_screen.dart',
      ]) {
        final src = File(f)
            .readAsLinesSync()
            .where((l) => !l.trimLeft().startsWith('//'))
            .join('\n');
        expect(src, isNot(contains('WAL_ASSIST')), reason: f);
        expect(src, isNot(contains('AssistPresentation')), reason: f);
      }
    });
  });

  group('§4 Y CỦA NỘI DUNG BÀI ĐẦU TIÊN — số thật mà trẻ thấy', () {
    testWidgets('⭐⭐ ở Trực quan, sơ đồ bắt đầu ở đâu (dp) — hé và thu gọn', (
      t,
    ) async {
      await _open(t);
      await t.tap(
        find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.visual)),
      );
      await t.pumpAndSettle();
      // ROUND 7 V1: hàng chip hình dạng đã xoá — đo bằng THẺ sơ đồ đầu tiên.
      final shape = find.byKey(
        VisualView.cardKey(loadSyntheticDoc().semantic.first.id),
      );
      final peeking = t.getTopLeft(shape).dy;
      await t.tap(find.byKey(AssistPeek.peekKey));
      await t.pumpAndSettle();
      await t.tap(find.byKey(AssistPeek.dismissKey));
      await t.pumpAndSettle();
      final collapsed = t.getTopLeft(shape).dy;
      debugPrint(
        'FIRSTCONTENT visual peek=$peeking dp collapsed=$collapsed dp',
      );
      expect(collapsed, lessThan(peeking));
      // Vòng 5 đo bản «card» ở 384.0 dp trên chính fixture này.
      expect(
        peeking,
        lessThan(384.0),
        reason: 'B phải đưa nội dung bài lên cao hơn bản thẻ thường trực',
      );
    });
  });
}
