/// ⭐⭐ GOLDEN JOURNEY V1 — MỘT BUỔI HỌC BÀI 17 TỪ ĐẦU ĐẾN CUỐI.
///
/// Trên Nokia tôi đi được tới Câu 2 rồi tắc: câu tự luận cần gõ tiếng Việt CÓ
/// DẤU, mà `adb input text` không gõ được. Thẻ kết phiên và hành động tiếp
/// theo vì thế chưa từng được xác minh trên máy.
///
/// Tệp này đóng đúng khoảng trống ấy — chạy trọn phiên ở khổ máy thật (360 dp)
/// và khẳng định BA NHÁNH mà hành động tiếp theo phải phân biệt:
///
///   A. phiên còn dang dở  ⇒ về ĐÚNG block nguồn của câu còn dở
///   B. sai rồi TỰ SỬA     ⇒ KHÔNG kéo trẻ về lỗi đã sửa
///   C. phiên làm trọn     ⇒ sang việc tiếp theo của kịch bản
///
/// Rẻ hơn nhiều so với tự động hoá bàn phím tiếng Việt, và nó chạy trên CI.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/tutor_script.dart';
import 'package:learning_coach/features/lesson_workspace/tutor_view.dart';

import 'support.dart';

const _nokia = Size(360, 640);

/// Ở khổ Nokia phần lớn nút nằm dưới nếp gấp — cuộn tới rồi mới chạm, đúng
/// như trẻ phải làm trên máy.
Future<void> tapScrolled(WidgetTester t, Finder f) async {
  await t.ensureVisible(f.first);
  await t.pumpAndSettle();
  await t.tap(f.first);
  await t.pumpAndSettle();
}

/// Chuyện đã xảy ra ở lần bấm hành động chính — đích và neo, đúng thứ
/// `onNext` nhận được. Không có nó thì test chỉ chứng minh chữ, không chứng
/// minh nút dẫn đi đâu.
class _Landed {
  NextTarget? target;
  String? anchor;
  bool get tapped => target != null;
}

Future<_Landed> _open(WidgetTester t) async {
  final landed = _Landed();
  await t.binding.setSurfaceSize(_nokia);
  addTearDown(() => t.binding.setSurfaceSize(null));
  await t.pumpWidget(
    fixtureHost(
      Scaffold(
        body: TutorView(
          doc: loadSyntheticDoc(),
          onNext: (target, anchor) {
            landed.target = target;
            landed.anchor = anchor;
          },
        ),
      ),
    ),
  );
  await t.pumpAndSettle();
  await tapScrolled(t, find.text('Tiếp ▸'));
  return landed;
}

Future<void> _choose(WidgetTester t, String option) =>
    tapScrolled(t, find.widgetWithText(FilledButton, option));

Future<void> _type(WidgetTester t, String answer) async {
  await t.ensureVisible(find.byKey(const Key('tutor-answer-field')));
  await t.pumpAndSettle();
  await t.enterText(find.byKey(const Key('tutor-answer-field')), answer);
  await tapScrolled(t, find.byKey(const Key('tutor-send')));
}

/// Sai đủ số lần để cạn thang gợi ý ⇒ runner scaffold rồi đi tiếp, KHÔNG kẹt.
Future<void> _exhaustChoice(WidgetTester t, String wrong) async {
  for (var i = 0; i < 3; i++) {
    if (find.widgetWithText(FilledButton, wrong).evaluate().isEmpty) return;
    await _choose(t, wrong);
  }
}

Future<void> _exhaustText(WidgetTester t) async {
  for (var i = 0; i < 3; i++) {
    if (find.byKey(const Key('tutor-answer-field')).evaluate().isEmpty) return;
    await _type(t, 'zzz qqq');
  }
}

void main() {
  testWidgets('⭐⭐ TRỌN PHIÊN: giải thích → sai → gợi ý → thử lại → đúng → '
      'câu 2 → thẻ kết → MỘT hành động tiếp theo', (t) async {
    final landed = await _open(t);

    // Câu 1 — sai «Lọc» trước, rồi tự sửa thành «Cô cạn».
    expect(find.textContaining('Làm muối từ nước biển'), findsOneWidget);
    await _choose(t, 'Lọc');
    // Vòng lặp CHƯA đóng: câu hỏi còn đó, có lời mời thử lại.
    expect(find.widgetWithText(FilledButton, 'Cô cạn'), findsOneWidget);
    await _choose(t, 'Cô cạn');

    // Câu 2 — tự luận, trả lời khớp.
    await _type(t, 'nặng hơn');

    // Thẻ kết phiên phải hiện, và nói bằng BẰNG CHỨNG, không phải điểm.
    await t.ensureVisible(find.byKey(TutorView.endCardKey));
    await t.pumpAndSettle();
    expect(find.byKey(TutorView.endCardKey), findsOneWidget);
    expect(find.byKey(const Key('tutor-end-story')), findsOneWidget);
    expect(find.textContaining('chưa '), findsWidgets,
        reason: 'thẻ kết phải nói rõ THAM GIA ≠ đã hiểu');

    // C. phiên làm trọn ⇒ hành động chính là việc tiếp theo của kịch bản,
    // KHÔNG phải lời mời quay lại.
    expect(find.textContaining('Xem lại chỗ này trong sách'), findsNothing,
        reason: 'B: trẻ đã tự sửa — kéo về là phủ nhận nỗ lực vừa bỏ ra');
    await tapScrolled(t, find.textContaining('Đọc lại phần'));
    expect(landed.tapped, isTrue, reason: 'nút phải THẬT SỰ dẫn đi đâu đó');
    expect(landed.target, NextTarget.read);
  });

  testWidgets('⭐ A. phiên còn DANG DỞ ⇒ hành động chính đưa về ĐÚNG chỗ sách '
      'của câu còn dở', (t) async {
    final landed = await _open(t);

    // Cạn thang gợi ý ở CẢ hai câu ⇒ đã thử mà chưa từng khớp.
    await _exhaustChoice(t, 'Lọc');
    await _exhaustText(t);

    await t.ensureVisible(find.byKey(TutorView.endCardKey));
    await t.pumpAndSettle();
    expect(find.byKey(TutorView.endCardKey), findsOneWidget);

    final back = find.textContaining('Xem lại chỗ này trong sách');
    expect(back, findsOneWidget,
        reason: 'còn câu dở mà vẫn mời sang việc mới là gợi ý giả');
    await tapScrolled(t, back);
    expect(landed.target, NextTarget.read);
    expect(landed.anchor, contains('p063'),
        reason: 'phải neo về câu CÒN DỞ ĐẦU TIÊN, không phải một chỗ bất kỳ');
  });

  testWidgets('⭐ B. sai rồi TỰ SỬA ở câu 1, câu 2 dở ⇒ neo về CÂU 2, không '
      'lôi trẻ về lỗi đã sửa', (t) async {
    final landed = await _open(t);
    await _choose(t, 'Lọc');     // sai
    await _choose(t, 'Cô cạn');  // tự sửa
    await _exhaustText(t);       // câu 2 bỏ dở

    await t.ensureVisible(find.byKey(TutorView.endCardKey));
    await t.pumpAndSettle();
    await tapScrolled(t, find.textContaining('Xem lại chỗ này trong sách'));
    expect(landed.anchor, contains('p061'),
        reason: 'neo phải là câu 2 — câu 1 đã tự sửa xong');
  });
}
