/// ⭐⭐ WAL-175 — Ý ĐỊNH đi xuyên suốt, và KHÔNG tạo lựa chọn giả.
///
/// Khoảng cách lớn nhất giữa mã và mô hình (Convergence §25): Home có đúng các
/// động từ, nhưng «Học trước» mở ra giá sách — giá sách không phải ý định — nên
/// từ đó MỌI lối vào cho ra cùng một trải nghiệm.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/timetable.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import 'package:learning_coach/features/subjects/subject_home_screen.dart';

import '../../support/pack_bundle.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'Na', grade: 5);

/// Bài Tiếng Việt có ĐỌC + VIẾT — đúng hình dạng corpus thật (một bài TV liệt
/// kê nhiều hoạt động: Đọc / Nói và nghe / Viết).
LessonIndex _tv() => LessonIndex.fromJsonString('''
{"grade":5,"subjects":{"Tiếng Việt":[
  {"sourceDocumentId":"05-sgk-tieng-viet-5-tap-mot","volume":"1",
   "lessons":[{"no":1,"title":"THANH ÂM CỦA GIÓ","pageStart":8}]}]},
 "toanExercises":{},
 "tvReadings":[{"book":"05-sgk-tieng-viet-5-tap-mot","lesson":1,"page":8,
   "passage":"Chúng tôi ra bờ suối.","questions":[{"prompt":"Vì sao?","page":8}]}],
 "tvWritings":[{"book":"05-sgk-tieng-viet-5-tap-mot","lesson":1,"page":11,
   "prompt":"Viết đoạn văn tả cảnh."}]}
''')!;

/// Bài có ĐỌC + BÀI TẬP: ý định ĐỔI ĐƯỢC thứ tự (chuẩn bị đọc trước, ôn làm
/// bài trước) ⇒ bộ chọn ý định phải hiện. Bài chỉ có Đọc + Viết thì mọi ý định
/// cho cùng thứ tự ⇒ hệ thống CỐ Ý không hỏi (không tạo lựa chọn giả).
LessonIndex _mixed() => LessonIndex.fromJsonString('''
{"grade":5,"subjects":{"Tiếng Việt":[
  {"sourceDocumentId":"05-sgk-tieng-viet-5-tap-mot","volume":"1",
   "lessons":[{"no":1,"title":"THANH ÂM CỦA GIÓ","pageStart":8}]}]},
 "toanExercises":{"1":[{"expr":"1/2 - 1/5","book":"05-sgk-tieng-viet-5-tap-mot"}]},
 "tvReadings":[{"book":"05-sgk-tieng-viet-5-tap-mot","lesson":1,"page":8,
   "passage":"Chúng tôi ra bờ suối.","questions":[{"prompt":"Vì sao?","page":8}]}]}
''')!;

void main() {
  test('⭐⭐ ý định XẾP THỨ TỰ hoạt động, KHÔNG nuốt hoạt động nào', () {
    const r = ReadingActivity(TvReading(
        book: 'b', lesson: 1, passage: 'p', questions: []));
    const w = WritingActivity(TvWriting(book: 'b', lesson: 1, prompt: 'q'));
    const e = ExerciseActivity([CorpusExercise(expr: '1/2+1/3', book: 'b')]);

    for (final intent in [
      LearningIntent.prepare,
      LearningIntent.review,
      LearningIntent.practice,
    ]) {
      final out = SubjectHomeScreen.activitiesForIntent(intent, [r, w, e]);
      expect(out.length, 3,
          reason: '⭐⭐ đột biến chỉ mở hoạt động ĐẦU hợp ý định ⇒ «Luyện viết» '
              'biến mất khỏi sản phẩm ⇒ đỏ');
    }

    // Chuẩn bị: quan sát/đọc TRƯỚC bài tập. Ôn: việc sinh bằng chứng trước.
    expect(SubjectHomeScreen.activitiesForIntent(LearningIntent.prepare, [e, r]).first,
        isA<ReadingActivity>());
    expect(SubjectHomeScreen.activitiesForIntent(LearningIntent.review, [r, e]).first,
        isA<ExerciseActivity>());
  });

  test('⭐ TRA CỨU không mời làm bài tập (không sinh bằng chứng)', () {
    const e = ExerciseActivity([CorpusExercise(expr: '1/2+1/3', book: 'b')]);
    const r = ReadingActivity(TvReading(
        book: 'b', lesson: 1, passage: 'p', questions: []));
    final out =
        SubjectHomeScreen.activitiesForIntent(LearningIntent.lookup, [e, r]);
    expect(out.whereType<ExerciseActivity>(), isEmpty,
        reason: '⭐ đột biến để bài tập lọt vào tra cứu ⇒ đỏ: xem sách sinh '
            'TRACE, không sinh EVIDENCE');
  });

  testWidgets('⭐⭐ mai có tiết ⇒ SAM ĐỀ NGHỊ, và nói LÝ DO', (t) async {
    // Tính thứ của NGÀY MAI từ chính đồng hồ chạy test ⇒ tất định, không phụ
    // thuộc hôm nay là thứ mấy.
    final now = DateTime.now();
    final tomorrow = DateTime(now.year, now.month, now.day + 1).weekday;
    await t.pumpWidget(packHost(SubjectHomeScreen(
      profile: _p,
      store: JsonlLearnerStore(),
      index: _mixed(),
      subject: 'Tiếng Việt',
      timetable: [
        TimetableEntry(
            learnerId: 'l',
            weekday: tomorrow,
            period: 1,
            subjectId: 'tieng-viet')
      ],
    )));
    await t.pumpAndSettle();
    await t.tap(find.textContaining('Thanh âm'));
    await t.pumpAndSettle();

    expect(find.text('Mai lớp con có tiết này.'), findsOneWidget,
        reason: '⭐⭐ đột biến bỏ lý do ⇒ đỏ: đề xuất không nêu được lý do thì '
            'không được hiện');
    expect(find.text('Mai có tiết này'), findsOneWidget);
    expect(find.text('Xem trong sách'), findsOneWidget,
        reason: 'tra cứu LUÔN có lối, kể cả khi SAM đã đề nghị việc khác');
  });

  testWidgets('⭐ KHÔNG có tín hiệu ⇒ SAM HỎI, không bịa lý do', (t) async {
    await t.pumpWidget(packHost(SubjectHomeScreen(
        profile: _p,
        store: JsonlLearnerStore(),
        index: _mixed(),
        subject: 'Tiếng Việt')));
    await t.pumpAndSettle();
    await t.tap(find.textContaining('Thanh âm'));
    await t.pumpAndSettle();
    expect(find.text('Con muốn bắt đầu thế nào?'), findsOneWidget);
    expect(find.textContaining('Mai lớp con'), findsNothing,
        reason: '⭐ đột biến đề nghị mặc định ⇒ đỏ');
  });

  testWidgets('⭐⭐ ý định KHÔNG đổi được gì ⇒ KHÔNG hỏi (không lựa chọn giả)',
      (t) async {
    // Bài chỉ có Đọc + Viết: mọi ý định cho cùng thứ tự ⇒ bỏ qua bộ chọn ý
    // định, vào thẳng bộ chọn VIỆC.
    await t.pumpWidget(packHost(SubjectHomeScreen(
        profile: _p,
        store: JsonlLearnerStore(),
        index: _tv(),
        subject: 'Tiếng Việt')));
    await t.pumpAndSettle();
    await t.tap(find.textContaining('Thanh âm'));
    await t.pumpAndSettle();
    expect(find.text('Con muốn bắt đầu thế nào?'), findsNothing,
        reason: '⭐⭐ đột biến luôn hỏi ý định ⇒ đỏ: hỏi mà mọi lựa chọn cho '
            'cùng kết quả là lựa chọn giả');
    expect(find.text('✍️ Luyện viết'), findsOneWidget,
        reason: 'và hoạt động VIẾT vẫn phải tới được');
  });
}
