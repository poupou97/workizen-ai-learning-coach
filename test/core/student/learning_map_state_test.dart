/// ⭐⭐ WAL-181 — trạng thái Learning Map suy từ lineage thật, không phải %.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/pedagogy/pedagogy_model.dart'
    show TeachingAct;
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/learning_map_state.dart';

LearningEvent _ev(
  EvidenceKind kind, {
  String? sourceDocumentId,
  int? lessonNo,
}) =>
    LearningEvent(
      eventId: 'e',
      skillCaseId: 'c',
      kind: kind,
      at: DateTime(2026, 9, 4),
      sourceDocumentId: sourceDocumentId,
      lessonNo: lessonNo,
      act: TeachingAct.askExplanation,
    );

void main() {
  test('⭐ không event nào khớp lineage ⇒ unseen', () {
    final s = learningMapStateFor(
      sourceDocumentId: '05-sgk-khoa-hoc-5',
      lessonNo: 1,
      allEvents: [
        _ev(EvidenceKind.independentAttempt,
            sourceDocumentId: '05-sgk-khoa-hoc-5', lessonNo: 2),
      ],
    );
    expect(s, LearningMapState.unseen);
  });

  test('⭐ event thiếu lineage (dữ liệu cũ) KHÔNG đếm ⇒ unseen, không đoán',
      () {
    final s = learningMapStateFor(
      sourceDocumentId: '05-sgk-khoa-hoc-5',
      lessonNo: 1,
      allEvents: [_ev(EvidenceKind.independentAttempt)],
    );
    expect(s, LearningMapState.unseen,
        reason: '⭐ đột biến suy lineage rỗng khớp mọi bài ⇒ đỏ');
  });

  test('có event khớp nhưng không có lần tự làm nào ⇒ engaged', () {
    final s = learningMapStateFor(
      sourceDocumentId: '05-sgk-khoa-hoc-5',
      lessonNo: 1,
      allEvents: [
        _ev(EvidenceKind.hintShown,
            sourceDocumentId: '05-sgk-khoa-hoc-5', lessonNo: 1),
      ],
    );
    expect(s, LearningMapState.engaged);
  });

  test('⭐⭐ có independentAttempt khớp lineage ⇒ independentEvidence', () {
    final s = learningMapStateFor(
      sourceDocumentId: '05-sgk-khoa-hoc-5',
      lessonNo: 1,
      allEvents: [
        _ev(EvidenceKind.hintShown,
            sourceDocumentId: '05-sgk-khoa-hoc-5', lessonNo: 1),
        _ev(EvidenceKind.independentAttempt,
            sourceDocumentId: '05-sgk-khoa-hoc-5', lessonNo: 1),
      ],
    );
    expect(s, LearningMapState.independentEvidence,
        reason: '⭐⭐ đột biến bỏ qua independentAttempt ⇒ đỏ — đây là tín '
            'hiệu quan trọng nhất trong 3 trạng thái');
  });

  test('selfCorrection cũng tính là bằng chứng tự làm', () {
    final s = learningMapStateFor(
      sourceDocumentId: '05-sgk-khoa-hoc-5',
      lessonNo: 1,
      allEvents: [
        _ev(EvidenceKind.selfCorrection,
            sourceDocumentId: '05-sgk-khoa-hoc-5', lessonNo: 1),
      ],
    );
    expect(s, LearningMapState.independentEvidence);
  });

  test('sách khác/bài khác không lẫn vào nhau', () {
    final events = [
      _ev(EvidenceKind.independentAttempt,
          sourceDocumentId: '05-sgk-khoa-hoc-5', lessonNo: 1),
    ];
    expect(
        learningMapStateFor(
            sourceDocumentId: '05-sgk-khoa-hoc-5',
            lessonNo: 2,
            allEvents: events),
        LearningMapState.unseen,
        reason: 'khác bài, cùng sách ⇒ không lẫn');
    expect(
        learningMapStateFor(
            sourceDocumentId: '05-sgk-toan-5-tap-mot',
            lessonNo: 1,
            allEvents: events),
        LearningMapState.unseen,
        reason: 'cùng số bài, khác sách ⇒ không lẫn');
  });

  test('⭐ không % hay số nào trong nhãn — chỉ chữ/icon', () {
    for (final s in LearningMapState.values) {
      final (icon, label) = childLabelFor(s);
      expect(icon.contains('%'), isFalse);
      expect(label.contains('%'), isFalse);
      expect(RegExp(r'\d').hasMatch(label), isFalse,
          reason: '⭐ đột biến thêm số vào nhãn ⇒ đỏ — CẤM số giả vờ chính xác');
    }
  });
}
