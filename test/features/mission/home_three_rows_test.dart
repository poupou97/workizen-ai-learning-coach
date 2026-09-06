/// ⭐ Concept «05 Home» — BA DẢI NGANG, ba ngữ nghĩa KHÁC NHAU.
///
///   SẮP TỚI          = thời khoá biểu từ NGÀY MAI  (home_upcoming_test.dart)
///   CÁC MÔN CỦA CON  = cửa vào Giá sách
///   TIẾP TỤC HỌC     = bài đang học DỞ
///
/// Bài kiểm này giữ hai điều concept vẽ mà sản phẩm KHÔNG được nói:
///   • không phần trăm tiến độ  (OPENED != UNDERSTOOD)
///   • không nhãn năng lực «Tốt» / «Ôn tập» dưới tên môn
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/features/mission/home_cards.dart';

import '../lesson_workspace/support.dart';

HomeLessonThread _t(LessonDocument d, Set<WorkspaceView> opened) =>
    HomeLessonThread(doc: d, openedViews: opened);

LessonDocument _asSubject(LessonDocument d, String subject, int grade) =>
    LessonDocument(
      schema: d.schema,
      book: d.book,
      bookTitle: d.bookTitle,
      subject: subject,
      grade: grade,
      lessonNo: d.lessonNo,
      title: d.title,
      provenance: d.provenance,
      blocks: d.blocks,
      semantic: d.semantic,
      tutorScript: d.tutorScript,
    );

void main() {
  group('TIẾP TỤC HỌC — chỉ bài đang học DỞ', () {
    test('chưa mở cách nào ⇒ KHÔNG nằm trong «tiếp tục học»', () {
      final d = loadSyntheticDoc();
      expect(continueLearning([_t(d, const {})]), isEmpty);
    });

    test('mở một phần ⇒ CÓ nằm trong «tiếp tục học»', () {
      final d = loadSyntheticDoc();
      expect(
        continueLearning([
          _t(d, {WorkspaceView.read}),
        ]),
        hasLength(1),
      );
    });

    test('⭐ mở HẾT ⇒ không còn là «đang học dở»', () {
      final d = loadSyntheticDoc();
      final all = HomeLessonThread(doc: d).availableViews.toSet();
      expect(
        continueLearning([_t(d, all)]),
        isEmpty,
        reason: 'mở hết rồi thì không phải việc còn dở',
      );
    });

    test('dấu vết của bài KHÁC không biến bài này thành đang-học-dở', () {
      final d = loadSyntheticDoc();
      // Một view bài này KHÔNG có ⇒ `openedHere` rỗng ⇒ không tính.
      final foreign = <WorkspaceView>{}
        ..addAll(
          WorkspaceView.values.where(
            (v) => !HomeLessonThread(doc: d).availableViews.contains(v),
          ),
        );
      if (foreign.isEmpty) return; // bài mẫu có đủ mọi view ⇒ không kiểm được
      expect(continueLearning([_t(d, foreign)]), isEmpty);
    });
  });

  group('CÁC MÔN CỦA CON — cửa vào Giá sách', () {
    final d = loadSyntheticDoc();

    test('gộp môn có bài SAM và môn chỉ có sách, KHÔNG lặp', () {
      final chips = homeSubjectChips(
        threads: [_t(_asSubject(d, 'KHTN', 6), const {})],
        shelf: const [
          HomeShelfSubject(
            subject: 'KHTN',
            listedLessons: 55,
            openableLessons: 1,
          ),
          HomeShelfSubject(
            subject: 'Toán',
            listedLessons: 43,
            openableLessons: 0,
          ),
        ],
        learnerGrade: 6,
      );
      expect(chips.map((c) => c.subject), ['KHTN', 'Toán']);
      expect(chips.first.hasSamLesson, isTrue);
      expect(chips.last.hasSamLesson, isFalse);
    });

    test('⭐ bài lớp KHÁC không làm môn của lớp này thành «có bài»', () {
      final chips = homeSubjectChips(
        threads: [_t(_asSubject(d, 'LS&ĐL', 5), const {})],
        shelf: const [
          HomeShelfSubject(
            subject: 'LS&ĐL',
            listedLessons: 28,
            openableLessons: 0,
          ),
        ],
        learnerGrade: 6,
      );
      expect(
        chips.single.hasSamLesson,
        isFalse,
        reason: 'bài lớp 5 không phải bài của học sinh lớp 6',
      );
    });

    test('môn có bài nhưng vắng trên giá vẫn có ô', () {
      final chips = homeSubjectChips(
        threads: [_t(_asSubject(d, 'KHTN', 6), const {})],
        shelf: const [],
        learnerGrade: 6,
      );
      expect(chips.single.subject, 'KHTN');
      expect(chips.single.hasSamLesson, isTrue);
    });

    test('⛔ ô môn KHÔNG mang nhãn năng lực nào', () {
      const chip = HomeSubjectChip(subject: 'Toán', hasSamLesson: true);
      // Giữ bằng KIỂU: chỉ có tên môn và có-bài-hay-không. Không có trường nào
      // để nhét «Tốt» / «Ôn tập» / «60%» vào.
      expect(chip.subject, 'Toán');
      expect(chip.hasSamLesson, isTrue);
    });

    test('không môn nào ⇒ rỗng, không nổ', () {
      expect(
        homeSubjectChips(threads: const [], shelf: const [], learnerGrade: 6),
        isEmpty,
      );
    });
  });
}
