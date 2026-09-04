/// ⭐⭐ WAL-176 (Missing #1) — gợi ý CẤP SÁCH cho Home khi môn CHƯA có
/// `SliceCurriculum` (Khoa học…) nhưng CÓ bìa + bài + TKB thật.
///
/// Không hỏi tên môn nào cụ thể trong test này nữa lần thứ hai — cùng luật
/// `proposeIntent` (WAL-175) đã kiểm ở `test/core/intent/learning_intent_test.dart`;
/// ở đây chỉ kiểm phần MỚI: quét NHIỀU sách và chọn đúng bài đầu tiên có căn cứ.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/intent/next_lesson.dart';
import 'package:learning_coach/core/store/timetable.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

LessonIndex _index() => LessonIndex.fromJsonString('''
{"grade":5,"subjects":{"Khoa học":[
  {"sourceDocumentId":"05-sgk-khoa-hoc-5","volume":null,
   "lessons":[{"no":1,"title":"SỰ BIẾN ĐỔI CỦA CHẤT","pageStart":6}]}]},
 "toanExercises":{},
 "khoaExperiments":[{"book":"05-sgk-khoa-hoc-5","lesson":1,"page":7,
   "title":"Trộn giấm và soda","subject":"Khoa học","duDoan":"?",
   "tienHanh":["Đổ giấm vào soda","Quan sát hiện tượng"]}],
 "books":[{"sourceDocumentId":"05-sgk-khoa-hoc-5","subject":"Khoa học",
   "title":"Khoa học 5","cover":"covers/kh5.png","lessonCount":1}]}
''')!;

void main() {
  test('⭐⭐ mai có tiết Khoa học ⇒ đề nghị ĐÚNG sách/bài/ý định Chuẩn bị', () {
    final now = DateTime(2026, 9, 4); // thứ Sáu
    final tomorrow = DateTime(2026, 9, 5).weekday; // thứ Bảy
    final rec = nextBookRecommendation(
      index: _index(),
      now: now,
      timetable: [
        TimetableEntry(
            learnerId: 'l', weekday: tomorrow, period: 1, subjectId: 'khoa-hoc'),
      ],
    );
    expect(rec, isNotNull);
    expect(rec!.sourceDocumentId, '05-sgk-khoa-hoc-5');
    expect(rec.subject, 'Khoa học');
    expect(rec.lessonNo, 1);
    expect(rec.intent, LearningIntent.prepare);
    expect(rec.reason, contains('Khoa học'));
    expect(rec.reason, contains('Bài 1'));
  });

  test('⭐ KHÔNG có TKB ⇒ null, không bịa đề nghị', () {
    final rec = nextBookRecommendation(
        index: _index(), now: DateTime(2026, 9, 4), timetable: const []);
    expect(rec, isNull);
  });

  test('⭐ TKB có môn KHÁC (không phải sách nào trên giá) ⇒ null', () {
    final tomorrow = DateTime(2026, 9, 5).weekday;
    final rec = nextBookRecommendation(
      index: _index(),
      now: DateTime(2026, 9, 4),
      timetable: [
        TimetableEntry(
            learnerId: 'l', weekday: tomorrow, period: 1, subjectId: 'toan'),
      ],
    );
    expect(rec, isNull);
  });

  test('⭐ tiết NGÀY KHÁC (không phải mai) ⇒ null', () {
    final notTomorrow =
        DateTime(2026, 9, 5).add(const Duration(days: 3)).weekday;
    final rec = nextBookRecommendation(
      index: _index(),
      now: DateTime(2026, 9, 4),
      timetable: [
        TimetableEntry(
            learnerId: 'l',
            weekday: notTomorrow,
            period: 1,
            subjectId: 'khoa-hoc'),
      ],
    );
    expect(rec, isNull);
  });

  test('⭐ sách có trong subjects nhưng KHÔNG có bìa trên giá ⇒ bỏ qua', () {
    // «books» rỗng: dữ liệu bài vẫn có nhưng chưa lên giá ⇒ chưa đề nghị được
    // ở CẤP SÁCH (khác với việc mở bài trực tiếp trong Book Home).
    final index = LessonIndex.fromJsonString('''
{"grade":5,"subjects":{"Khoa học":[
  {"sourceDocumentId":"05-sgk-khoa-hoc-5","volume":null,
   "lessons":[{"no":1,"title":"SỰ BIẾN ĐỔI CỦA CHẤT","pageStart":6}]}]},
 "toanExercises":{},
 "khoaExperiments":[{"book":"05-sgk-khoa-hoc-5","lesson":1,"page":7,
   "title":"Trộn giấm và soda","subject":"Khoa học","duDoan":"?",
   "tienHanh":["Đổ giấm vào soda","Quan sát hiện tượng"]}]}
''')!;
    final tomorrow = DateTime(2026, 9, 5).weekday;
    final rec = nextBookRecommendation(
      index: index,
      now: DateTime(2026, 9, 4),
      timetable: [
        TimetableEntry(
            learnerId: 'l', weekday: tomorrow, period: 1, subjectId: 'khoa-hoc'),
      ],
    );
    expect(rec, isNull);
  });
}
