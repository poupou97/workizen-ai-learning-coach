/// ⭐⭐ WAL-180 — Parent Session Summary: CÙNG evidence Learning Map dùng,
/// không hệ tính riêng.
/// ⭐⭐ WAL-210 — Founder D1: «Con đã tự làm được» chỉ từ tự làm ĐÃ CHẤM đúng;
/// tự báo/hoàn thành ⇒ câu hoàn thành, nói rõ không chấm.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/coach/parent_session_summary.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/learning_map_state.dart';

LearningSession _session(
  String id,
  DateTime at,
  List<LearningEvent> events,
) =>
    LearningSession(
      sessionId: id,
      learnerId: 'l',
      subjectId: 'khoa-hoc',
      startedAt: at,
      trigger: SessionTrigger.manual,
      events: events,
    );

LearningEvent _ev(
  EvidenceKind kind,
  DateTime at, {
  String? sourceDocumentId,
  int? lessonNo,
  bool? correct,
}) =>
    LearningEvent(
      eventId: 'e-${at.millisecondsSinceEpoch}',
      skillCaseId: 'c',
      kind: kind,
      correct: correct,
      at: at,
      sourceDocumentId: sourceDocumentId,
      lessonNo: lessonNo,
    );

RecentLessonTouch _touch(LearningMapState s) => RecentLessonTouch(
    sourceDocumentId: 'b', lessonNo: 1, state: s, at: DateTime(2026, 9, 4));

void main() {
  test('⭐ event thiếu lineage bị bỏ qua, không đoán bài nào', () {
    final touches = recentLessonTouches([
      _session('s1', DateTime(2026, 9, 4), [
        _ev(EvidenceKind.independentAttempt, DateTime(2026, 9, 4),
            correct: true)
      ]),
    ]);
    expect(touches, isEmpty);
  });

  test(
      '⭐⭐ trạng thái Parent đọc ĐÚNG bằng learningMapStateFor — một nguồn '
      'sự thật, hai phép chiếu', () {
    final touches = recentLessonTouches([
      _session('s1', DateTime(2026, 9, 4), [
        _ev(EvidenceKind.independentAttempt, DateTime(2026, 9, 4),
            sourceDocumentId: '05-sgk-khoa-hoc-5', lessonNo: 1, correct: true),
      ]),
    ]);
    expect(touches.single.state, LearningMapState.independentEvidence,
        reason: '⭐⭐ đột biến tính lại trạng thái theo luật khác ⇒ đỏ — '
            'Parent và Child PHẢI đọc cùng một sự thật');
  });

  test('⭐⭐ D1: tự báo (participation) ⇒ Parent thấy participation, KHÔNG '
      'independentEvidence — và dữ liệu cũ correct-null cũng vậy', () {
    final touches = recentLessonTouches([
      _session('s1', DateTime(2026, 9, 3), [
        _ev(EvidenceKind.participation, DateTime(2026, 9, 3),
            sourceDocumentId: '05-sgk-khoa-hoc-5', lessonNo: 1),
      ]),
      _session('s2', DateTime(2026, 9, 4), [
        _ev(EvidenceKind.independentAttempt, DateTime(2026, 9, 4),
            sourceDocumentId: '05-sgk-khoa-hoc-5', lessonNo: 2), // correct null
      ]),
    ]);
    expect(touches.map((t) => t.state),
        everyElement(LearningMapState.participation),
        reason: '⭐⭐ audit C6b: một nút bấm không được thành «tự làm được» '
            'ở phụ huynh');
  });

  test('sách+bài khác nhau ⇒ hai dòng riêng, không gộp nhầm', () {
    final touches = recentLessonTouches([
      _session('s1', DateTime(2026, 9, 3), [
        _ev(EvidenceKind.independentAttempt, DateTime(2026, 9, 3),
            sourceDocumentId: '05-sgk-khoa-hoc-5', lessonNo: 1, correct: true),
      ]),
      _session('s2', DateTime(2026, 9, 4), [
        _ev(EvidenceKind.hintShown, DateTime(2026, 9, 4),
            sourceDocumentId: '05-sgk-khoa-hoc-5', lessonNo: 3),
      ]),
    ]);
    expect(touches, hasLength(2));
    // Gần nhất trước.
    expect(touches.first.lessonNo, 3);
    expect(touches.first.state, LearningMapState.engaged);
    expect(touches.last.lessonNo, 1);
    expect(touches.last.state, LearningMapState.independentEvidence);
  });

  test('⭐ maxLessons giới hạn số dòng, ưu tiên GẦN NHẤT', () {
    final touches = recentLessonTouches([
      for (var i = 1; i <= 3; i++)
        _session('s$i', DateTime(2026, 9, i), [
          _ev(EvidenceKind.independentAttempt, DateTime(2026, 9, i),
              sourceDocumentId: 'b', lessonNo: i, correct: true),
        ]),
    ], maxLessons: 2);
    expect(touches, hasLength(2));
    expect(touches.map((t) => t.lessonNo), [3, 2],
        reason: '⭐ đột biến giữ bài CŨ thay vì MỚI ⇒ đỏ — phụ huynh cần '
            'biết gần đây, không phải lịch sử xa');
  });

  test('parentLineFor: "tự làm được" khác câu "mới học cùng SAM"', () {
    expect(parentLineFor(_touch(LearningMapState.independentEvidence)),
        contains('Con đã tự làm được'));
    expect(parentLineFor(_touch(LearningMapState.engaged)),
        contains('chưa có lần nào tự làm được'),
        reason: 'không được nói trẻ tự làm được khi chưa có bằng chứng đó — '
            'câu phải PHỦ ĐỊNH rõ, không chỉ lặng im');
  });

  test('⭐⭐ D1: participation ⇒ câu HOÀN THÀNH «Con đã học Bài N», nói rõ '
      'không chấm, KHÔNG BAO GIỜ «tự làm được»', () {
    final line = parentLineFor(_touch(LearningMapState.participation));
    expect(line, startsWith('Con đã học Bài 1'));
    expect(line, contains('không chấm'));
    expect(line.contains('tự làm được'), isFalse,
        reason: '⭐⭐ Founder D1: «No parent-facing claim such as Con đã tự làm '
            'được may be derived solely from an unvalidated tap»');
    // Chỉ MỘT trạng thái được nói «tự làm được».
    for (final s in LearningMapState.values) {
      if (s == LearningMapState.unseen) continue;
      expect(parentLineFor(_touch(s)).startsWith('Con đã tự làm được'),
          s == LearningMapState.independentEvidence,
          reason: 'trạng thái $s');
    }
  });

  test('⭐ không có tên bài thật ⇒ dùng "Bài N" trần, không bịa tên', () {
    final t = RecentLessonTouch(
        sourceDocumentId: 'b',
        lessonNo: 7,
        state: LearningMapState.independentEvidence,
        at: DateTime(2026, 9, 4));
    expect(parentLineFor(t), contains('Bài 7'));
  });

  test('có tên bài thật ⇒ dùng tên, không dùng "Bài N"', () {
    final t = RecentLessonTouch(
        sourceDocumentId: 'b',
        lessonNo: 7,
        state: LearningMapState.independentEvidence,
        at: DateTime(2026, 9, 4));
    final line = parentLineFor(t, lessonTitle: 'Thành phần của đất');
    expect(line, contains('Thành phần của đất'));
    expect(line, isNot(contains('Bài 7')));
  });
}
