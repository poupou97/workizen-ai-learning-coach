/// WAL-169 — HAI DÒNG «Bài 1» Y HỆT NHAU.
///
/// Đo trên Nokia (khung MAIN-n03, môn Khoa học): mục lục đổ ra «Bài 1», «Bài 1»,
/// «Bài 2», «Bài 2»… Trẻ nhìn vào chỉ có thể kết luận máy hỏng.
///
/// Nhưng hai nguyên nhân KHÁC HẲN nhau, và trộn hai thứ này là xoá bài của trẻ:
///  · 7/251 bản ghi TRÙNG HỆT (cùng số, cùng tên, cùng trang) — nhiễu, bỏ được.
///  · GDTC đánh số LẠI theo từng chủ đề: 5 bài mang số 1, mỗi bài một tên và
///    một trang. Đây là cấu trúc THẬT của cuốn sách.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import 'package:learning_coach/features/subjects/subject_home_screen.dart';

import '../../support/pack_bundle.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'Na', grade: 5);

/// Đúng hình dạng dữ liệu thật: GDTC lặp số CÓ tên; Khoa học lặp số KHÔNG tên,
/// một bản ghi có trang một bản ghi không; và một cặp trùng hệt.
LessonIndex _idx() => LessonIndex.fromJsonString('''
{"grade":5,"subjects":{
 "GDTC":[{"sourceDocumentId":"05-sgk-giao-duc-the-chat-5","volume":null,
  "lessons":[
   {"no":1,"title":"BÀI TẬP ĐỘI HÌNH ĐỘI NGŨ","pageStart":8},
   {"no":1,"title":"BÀI TẬP ĐỘI HÌNH ĐỘI NGŨ","pageStart":8},
   {"no":1,"title":"DẪN BÓNG THEO ĐƯỜNG VÒNG","pageStart":53}]}],
 "Khoa học":[{"sourceDocumentId":"05-sgk-khoa-hoc-5","volume":null,
  "lessons":[
   {"no":1,"title":null,"pageStart":64},
   {"no":1,"title":null,"pageStart":null}]}]},
 "toanExercises":{}}
''')!;

void main() {
// ⭐ ROUND 7 · WS-S — QUYẾT ĐỊNH CỦA FOUNDER: tiêu đề hiển thị NGUYÊN VĂN NGUỒN.
// Các kỳ vọng dưới đây từng ghim chuỗi ĐÃ ĐƯỢC HẠ CHỮ; nay chúng ghim đúng chuỗi
// mà fixture của chính test này mang. Sửa TIỀN ĐỀ, không nới assertion: mỗi kỳ
// vọng vẫn đòi một chuỗi CỤ THỂ, chỉ là chuỗi thật thay vì chuỗi biến đổi.

  test('⭐ bản ghi TRÙNG HỆT bị bỏ — bỏ đi không mất thông tin nào', () {
    final gdtc = _idx().subjects['GDTC']!.single.lessons;
    expect(gdtc.length, 2,
        reason: '⭐ đột biến bỏ dedupe ⇒ 3 bản ghi ⇒ đỏ');
  });

  test('⭐⭐ KHÔNG gộp theo số bài: GDTC có nhiều bài số 1 THẬT', () {
    final gdtc = _idx().subjects['GDTC']!.single.lessons;
    expect(gdtc.where((l) => l.no == 1).length, 2,
        reason: '⭐⭐ đột biến gộp theo `no` ⇒ còn 1 bài ⇒ đỏ. Gộp theo số là '
            'XOÁ BÀI của trẻ — GDTC đánh số lại theo từng chủ đề.');
    expect(gdtc.map((l) => l.pageStart), [8, 53]);
  });

  testWidgets('⭐ số bài lặp mà không có tên ⇒ nói TRANG IN để phân biệt',
      (t) async {
    await t.pumpWidget(packHost(SubjectHomeScreen(
        profile: _p,
        store: JsonlLearnerStore(),
        index: _idx(),
        subject: 'Khoa học')));
    await t.pumpAndSettle();
    expect(find.text('Bài 1 · trang 64'), findsOneWidget,
        reason: '⭐ đột biến bỏ hậu tố trang ⇒ hai dòng «Bài 1» y hệt ⇒ đỏ');
    expect(find.text('Bài 1'), findsOneWidget,
        reason: 'bản ghi không có trang thì để trần — KHÔNG bịa «(2)»');
  });

  testWidgets('bài có TÊN thì tên đủ phân biệt, không cần thêm trang',
      (t) async {
    await t.pumpWidget(packHost(SubjectHomeScreen(
        profile: _p,
        store: JsonlLearnerStore(),
        index: _idx(),
        subject: 'GDTC')));
    await t.pumpAndSettle();
    expect(find.text('Bài 1 · BÀI TẬP ĐỘI HÌNH ĐỘI NGŨ'), findsOneWidget);
    expect(find.text('Bài 1 · DẪN BÓNG THEO ĐƯỜNG VÒNG'), findsOneWidget);
    expect(find.textContaining('trang'), findsNothing,
        reason: 'có tên rồi thì thêm trang là nhiễu');
  });

  test('FILE THẬT: pack lớp 5 không còn bản ghi trùng hệt nào', () {
    final f = _realIndex();
    if (f == null) return;
    for (final books in f.subjects.values) {
      for (final b in books) {
        final keys = <String>{};
        for (final l in b.lessons) {
          expect(keys.add('${l.no}|${l.title}|${l.pageStart}'), isTrue,
              reason: '${b.sourceDocumentId} còn bản ghi trùng hệt bài ${l.no}');
        }
      }
    }
  });
}

LessonIndex? _realIndex() {
  const path = 'assets/pack/lesson-index-g5.json';
  final file = File(path);
  if (!file.existsSync()) {
    markTestSkipped('pack chưa build');
    return null;
  }
  return LessonIndex.fromJsonString(file.readAsStringSync());
}
