/// ⭐⭐ WAL-187 — sheet "Con muốn làm phần nào trước?" (2+ activity cùng ý
/// định, vd Đọc bài + Luyện viết của một bài Tiếng Việt).
///
/// Phát hiện khi đi Golden Journey thật trên Nokia (WAL-176): tap "Đọc bài"/
/// "Luyện viết" ở đúng toạ độ hiển thị KHÔNG phản hồi trên máy thật — cùng
/// lỗi WAL-145 đã bắt ở sheet ý định phía trên (thiếu isScrollControlled +
/// bọc cuộn). Đã áp cùng fix.
///
/// ⚠️ THÀNH THẬT VỀ GIỚI HẠN TEST: đã thử assert `getRect().bottom` nằm
/// trong màn hình để bắt lỗi tự động — KHÔNG bắt được (test xanh cả trước
/// và sau khi revert fix), vì `flutter test` không mô phỏng đúng cơ chế gây
/// lỗi thật (dispatch chạm thật + status bar/window inset thật trên máy).
/// Đây là lớp lỗi CHỈ xác nhận được bằng thiết bị thật — test này chỉ giữ
/// đúng chức năng (điều hướng đúng lựa chọn), KHÔNG thay được bằng chứng
/// Nokia cho chính bug đã tìm thấy.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import 'package:learning_coach/features/subjects/subject_home_screen.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'M', grade: 5);

LessonIndex _idx() => LessonIndex.fromJsonString('''
{"grade":5,"subjects":{
  "Tiếng Việt":[{"sourceDocumentId":"05-sgk-tieng-viet-5-tap-mot","volume":"1",
    "lessons":[{"no":2,"title":"Đọc: cánh đồng hoa","pageStart":15}]}]},
 "tvReadings":[{"book":"05-sgk-tieng-viet-5-tap-mot","lesson":2,"page":15,
    "passage":"Cánh đồng hoa trải dài đến tận chân trời...",
    "questions":[{"prompt":"Cánh đồng hoa được tả như thế nào?","page":15}]}],
 "tvWritings":[{"book":"05-sgk-tieng-viet-5-tap-mot","lesson":2,"page":16,
    "prompt":"Viết đoạn văn tả một cánh đồng em từng thấy."}]}
''')!;

void main() {
  testWidgets(
      '⭐⭐ sheet nhiều lựa chọn: cả 2 hiện đúng, "Đọc bài" điều hướng đúng '
      'ReaderScreen (không lẫn sang Luyện viết)', (t) async {
    // Kích thước THẬT của Nokia 6.1 — cùng khuôn book_shelf_test.dart. Không
    // bắt được bug hit-test qua kênh này (xem ghi chú đầu file), nhưng vẫn
    // giữ để test chạy đúng điều kiện gần máy thật nhất có thể.
    t.view.physicalSize = const Size(1080, 1920);
    t.view.devicePixelRatio = 2.75;
    addTearDown(t.view.reset);

    await t.pumpWidget(MaterialApp(
        home: SubjectHomeScreen(
            profile: _p,
            store: JsonlLearnerStore(),
            index: _idx(),
            subject: 'Tiếng Việt')));
    await t.pumpAndSettle();

    await t.tap(find.textContaining('Đọc: cánh đồng hoa'));
    await t.pumpAndSettle();
    expect(find.text('Con muốn làm phần nào trước?'), findsOneWidget);
    expect(find.text('📖 Đọc bài'), findsOneWidget);
    expect(find.text('✍️ Luyện viết'), findsOneWidget);

    // Bấm thật phải đưa đúng tới ReaderScreen (READ gate + đoạn văn thật) —
    // không lẫn sang ComposeLiteScreen (Luyện viết).
    await t.tap(find.text('📖 Đọc bài'));
    await t.pumpAndSettle();
    expect(find.textContaining('đọc kỹ đoạn văn này trước nhé'), findsOneWidget,
        reason: '⭐⭐ đột biến điều hướng sai (Đọc bài → Luyện viết hoặc '
            'ngược lại) ⇒ đỏ');
  });
}
