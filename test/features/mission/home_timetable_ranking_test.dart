/// ⭐ Lệnh 56 §P1 / §P1.1 — thời khoá biểu XẾP LẠI Home, và chỉ xếp lại.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/store/timetable.dart';
import 'package:learning_coach/features/mission/home_cards.dart';
import 'package:learning_coach/features/mission/timetable_context.dart';

import '../lesson_workspace/support.dart';

LessonDocument _subj(LessonDocument d, String subject, String book) =>
    LessonDocument(
      schema: d.schema,
      book: book,
      bookTitle: '$subject 6',
      subject: subject,
      grade: 6,
      lessonNo: d.lessonNo,
      title: d.title,
      provenance: d.provenance,
      blocks: d.blocks,
      semantic: d.semantic,
      tutorScript: d.tutorScript,
    );

final _monday = DateTime(2026, 9, 7, 8);

void main() {
  final base = loadSyntheticDoc();
  final khtn = _subj(base, 'KHTN', '06-khtn');
  final toan = _subj(base, 'Toán', '06-toan');
  final nguVan = _subj(base, 'Ngữ văn', '06-ngu-van');

  /// Hôm nay (T2): Toán. Ngày mai (T3): Ngữ văn. KHTN không có tiết.
  final ctx = timetableContext([
    const TimetableEntry(
      learnerId: 'na',
      weekday: DateTime.monday,
      period: 1,
      subjectId: 'toan',
    ),
    const TimetableEntry(
      learnerId: 'na',
      weekday: DateTime.tuesday,
      period: 1,
      subjectId: 'ngu-van',
    ),
  ], now: _monday);

  test('⭐ thẻ: môn HÔM NAY lên trước, rồi NGÀY MAI, rồi còn lại', () {
    final row = buildHomeCards(
      // cố ý đảo thứ tự truyền vào
      threads: [
        HomeLessonThread(doc: khtn),
        HomeLessonThread(doc: nguVan),
        HomeLessonThread(doc: toan),
      ],
      learnerGrade: 6,
      timetable: ctx,
    );
    expect(row.cards.map((c) => c.thread!.doc.subject).toList(), [
      'Toán',
      'Ngữ văn',
      'KHTN',
    ]);
  });

  test('không có thời khoá biểu ⇒ giữ NGUYÊN thứ tự cũ', () {
    final row = buildHomeCards(
      threads: [
        HomeLessonThread(doc: khtn),
        HomeLessonThread(doc: nguVan),
        HomeLessonThread(doc: toan),
      ],
      learnerGrade: 6,
    );
    expect(row.cards.map((c) => c.thread!.doc.subject).toList(), [
      'KHTN',
      'Ngữ văn',
      'Toán',
    ]);
  });

  test('⛔ TIMETABLE SUBJECT ≠ SAM LESSON: có tiết KHÔNG tạo thêm thẻ bài', () {
    final row = buildHomeCards(
      threads: const [],
      shelf: const [
        HomeShelfSubject(
          subject: 'Toán',
          listedLessons: 40,
          openableLessons: 0,
        ),
      ],
      learnerGrade: 6,
      timetable: ctx,
    );
    expect(
      row.cards.where((c) => c.isRealLesson),
      isEmpty,
      reason: 'thời khoá biểu tự sinh ra một bài học',
    );
  });

  test('§P1.1 — dải môn cũng theo ngữ cảnh: hôm nay → ngày mai → còn lại', () {
    final chips = homeSubjectChips(
      threads: const [],
      shelf: const [
        HomeShelfSubject(
          subject: 'KHTN',
          listedLessons: 55,
          openableLessons: 0,
        ),
        HomeShelfSubject(
          subject: 'Ngữ văn',
          listedLessons: 6,
          openableLessons: 0,
        ),
        HomeShelfSubject(
          subject: 'Toán',
          listedLessons: 43,
          openableLessons: 0,
        ),
      ],
      learnerGrade: 6,
      timetable: ctx,
    );
    expect(chips.map((c) => c.subject).toList(), ['Toán', 'Ngữ văn', 'KHTN']);
  });

  test('⛔ §P1.5 — thời khoá biểu KHÔNG mở rộng phạm vi lớp', () {
    final g5 = LessonDocument(
      schema: base.schema,
      book: '05-khoa-hoc-5',
      bookTitle: 'Khoa học 5',
      subject: 'Toán', // môn CÓ tiết hôm nay
      grade: 5,
      lessonNo: base.lessonNo,
      title: base.title,
      provenance: base.provenance,
      blocks: base.blocks,
    );
    final row = buildHomeCards(
      threads: [HomeLessonThread(doc: g5)],
      learnerGrade: 6,
      timetable: ctx,
    );
    expect(
      row.cards.where((c) => c.isRealLesson),
      isEmpty,
      reason: 'môn có tiết hôm nay được dùng để lách bộ lọc lớp',
    );
  });
}
