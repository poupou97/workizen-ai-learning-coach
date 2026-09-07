/// ⭐⭐ QUYẾT ĐỊNH C-1 (lệnh 54) — HOME FAIL-CLOSED THEO LỚP.
///
/// Bảy phép kiểm Founder liệt kê, theo đúng thứ tự lệnh:
///
/// 1. Lớp 5 không nhận Home card Lớp 6.
/// 2. Lớp 6 không nhận Home card Lớp 5.
/// 3. Continue Learning không cross-grade.
/// 4. Next Action không cross-grade.
/// 5. Đổi hồ sơ ⇒ Home tính lại theo learner mới.
/// 6. Không tái dùng WorkspaceTrace của learner trước.
/// 7. Thời khoá biểu chỉ sinh gợi ý từ môn của learner hiện tại.
///
/// Nguyên tắc chung: lọc xảy ra TRƯỚC xếp hạng. Bài ngoài lớp không «thua» —
/// nó không có mặt.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/core/store/timetable.dart';
import 'package:learning_coach/core/store/timetable_generator.dart';
import 'package:learning_coach/features/lesson_workspace/workspace_trace.dart';
import 'package:learning_coach/features/mission/home_cards.dart';

import '../lesson_workspace/support.dart';

/// Cùng một bài, gán sang lớp khác — giữ mọi thứ còn lại y hệt để phép kiểm
/// chỉ nói về LỚP.
LessonDocument _atGrade(LessonDocument d, int grade, String book) =>
    LessonDocument(
      schema: d.schema,
      book: book,
      bookTitle: '$book-title',
      subject: d.subject,
      grade: grade,
      lessonNo: d.lessonNo,
      title: d.title,
      provenance: d.provenance,
      blocks: d.blocks,
      semantic: d.semantic,
      tutorScript: d.tutorScript,
    );

void main() {
  final base = loadSyntheticDoc();
  final g5 = _atGrade(base, 5, '05-sgk-lich-su-va-dia-li-5');
  final g6 = _atGrade(base, 6, '06-sgk-khoa-hoc-tu-nhien-6');

  test('1. học sinh LỚP 5 không nhận thẻ Home của bài LỚP 6', () {
    final row = buildHomeCards(
      threads: [
        HomeLessonThread(doc: g6),
        HomeLessonThread(doc: g5),
      ],
      learnerGrade: 5,
    );
    final ids = row.cards.map((c) => c.id).toList();
    expect(ids, contains(g5.slotKey));
    expect(ids, isNot(contains(g6.slotKey)));
  });

  test('2. học sinh LỚP 6 không nhận thẻ Home của bài LỚP 5', () {
    final row = buildHomeCards(
      threads: [
        HomeLessonThread(doc: g6),
        HomeLessonThread(doc: g5),
      ],
      learnerGrade: 6,
    );
    final ids = row.cards.map((c) => c.id).toList();
    expect(ids, contains(g6.slotKey));
    expect(ids, isNot(contains(g5.slotKey)));
  });

  test('3. «Tiếp tục học» không bao giờ vượt lớp', () {
    final opened = {HomeLessonThread(doc: g5).availableViews.first};
    final threads = [
      HomeLessonThread(doc: g5, openedViews: opened),
      HomeLessonThread(doc: g6, openedViews: opened),
    ];
    expect(
      continueLearning(threads, learnerGrade: 5).map((t) => t.doc.grade),
      everyElement(5),
    );
    expect(
      continueLearning(threads, learnerGrade: 6).map((t) => t.doc.grade),
      everyElement(6),
    );
  });

  test('4. việc tiếp theo được đề xuất KHÔNG bao giờ trỏ sang lớp khác', () {
    final row = buildHomeCards(
      threads: [
        HomeLessonThread(doc: g5),
        HomeLessonThread(doc: g6),
      ],
      learnerGrade: 6,
    );
    final i = promotedCardIndex(row.cards);
    // Có thể không thẻ nào đủ tư cách — nhưng nếu có, nó phải của lớp 6.
    if (i != null) {
      expect(row.cards[i].thread!.doc.grade, 6);
    }
    for (final c in row.cards.where((c) => c.isRealLesson)) {
      expect(
        c.thread!.doc.grade,
        6,
        reason: 'thẻ lớp khác vẫn tới được tầng đề xuất',
      );
    }
  });

  test('5. đổi lớp ⇒ hàng thẻ tính LẠI, không giữ thẻ của lớp trước', () {
    final threads = [HomeLessonThread(doc: g5), HomeLessonThread(doc: g6)];
    final asG6 = buildHomeCards(threads: threads, learnerGrade: 6);
    final asG5 = buildHomeCards(threads: threads, learnerGrade: 5);
    expect(
      asG6.cards.map((c) => c.id),
      isNot(equals(asG5.cards.map((c) => c.id))),
    );
    expect(asG6.cards.map((c) => c.id), contains(g6.slotKey));
    expect(asG5.cards.map((c) => c.id), contains(g5.slotKey));
  });

  test('6. dấu vết «đã mở» của learner trước KHÔNG được tái dùng', () {
    final trace = WorkspaceTrace();
    trace.markView(g6.slotKey, WorkspaceView.read);
    expect(trace.viewsFor(g6.slotKey), isNotEmpty);

    trace.clear(); // đúng thứ `_selectProfile` gọi khi đổi hồ sơ

    expect(trace.viewsFor(g6.slotKey), isEmpty);
    expect(trace.opened(g6.slotKey), isFalse);
  });

  test('7. thời khoá biểu chỉ sinh từ MÔN CỦA LỚP HIỆN TẠI', () {
    const g5Subjects = ['toan', 'tieng-viet', 'khoa-hoc', 'ls-dl'];
    const g6Subjects = ['toan', 'ngu-van', 'khtn', 'tin-hoc'];

    final forG5 = generateTimetable(
      learnerId: 'minh',
      subjects: g5Subjects,
      seed: 1,
      slotsPerDay: 2,
    );
    final forG6 = generateTimetable(
      learnerId: 'na',
      subjects: g6Subjects,
      seed: 1,
      slotsPerDay: 2,
    );

    final s5 = {for (final e in forG5) e.subjectId};
    final s6 = {for (final e in forG6) e.subjectId};
    // Môn chỉ có ở cấp 2 không được rơi vào TKB của học sinh lớp 5.
    expect(s5, isNot(contains('khtn')));
    expect(s5, isNot(contains('ngu-van')));
    // …và ngược lại.
    expect(s6, isNot(contains('khoa-hoc')));
    expect(s6, isNot(contains('tieng-viet')));
    // Mỗi tiết mang đúng chủ.
    expect(forG5.every((e) => e.learnerId == 'minh'), isTrue);
    expect(forG6.every((e) => e.learnerId == 'na'), isTrue);
  });

  test(
    '⛔ TKB của learner này không bao giờ mang learnerId của learner kia',
    () {
      final t = generateTimetable(
        learnerId: 'minh',
        subjects: const ['toan'],
        seed: 7,
        slotsPerDay: 1,
      );
      expect(t.map((e) => e.learnerId).toSet(), {'minh'});
      expect(t.first, isA<TimetableEntry>());
    },
  );
}
