/// ⭐⭐ WAL-181 — trạng thái Learning Map suy từ lineage thật, không phải %.
/// ⭐⭐ WAL-210 — Founder D1: «Tự làm được» CHỈ từ tự làm ĐÃ CHẤM đúng; tự
/// báo/hoàn thành là trạng thái riêng; dữ liệu cũ đọc theo cùng luật.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/pedagogy/pedagogy_model.dart'
    show TeachingAct;
import 'package:learning_coach/core/student/evidence_validation.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/learning_map_state.dart';

const _book = '05-sgk-khoa-hoc-5';

/// Sự kiện CÓ CHẤM ở đây mang dấu `fraction-check-v1` (đường Deep thật);
/// dữ liệu cũ không dấu được dựng riêng ở nhóm ROUND 4 bên dưới.
LearningEvent _ev(
  EvidenceKind kind, {
  String? sourceDocumentId,
  int? lessonNo,
  bool? correct,
  bool stamped = true,
}) =>
    LearningEvent(
      eventId: 'e',
      skillCaseId: 'c',
      kind: kind,
      correct: correct,
      at: DateTime(2026, 9, 4),
      sourceDocumentId: sourceDocumentId,
      lessonNo: lessonNo,
      act: TeachingAct.askExplanation,
      validation: (correct != null && stamped) ? _r4Stamp : null,
    );

LearningMapState _state(List<LearningEvent> events, {int lessonNo = 1}) =>
    learningMapStateFor(
        sourceDocumentId: _book, lessonNo: lessonNo, allEvents: events);

/// ROUND 4 (strict default): sự kiện CÓ CHẤM trong test này mô phỏng đường
/// Deep (TutorSession) — mang dấu `fraction-check-v1` như emitter thật.
const _r4Stamp =
    EvidenceValidation(validatorId: 'fraction-check-v1', validatorVersion: '1');

void main() {
  test('⭐ không event nào khớp lineage ⇒ unseen', () {
    final s = _state([
      _ev(EvidenceKind.independentAttempt,
          sourceDocumentId: _book, lessonNo: 2, correct: true),
    ]);
    expect(s, LearningMapState.unseen);
  });

  test('⭐ event thiếu lineage (dữ liệu cũ) KHÔNG đếm ⇒ unseen, không đoán',
      () {
    final s = _state([_ev(EvidenceKind.independentAttempt, correct: true)]);
    expect(s, LearningMapState.unseen,
        reason: '⭐ đột biến suy lineage rỗng khớp mọi bài ⇒ đỏ');
  });

  test('có event khớp nhưng không có lần tự làm nào ⇒ engaged', () {
    final s = _state([
      _ev(EvidenceKind.hintShown, sourceDocumentId: _book, lessonNo: 1),
    ]);
    expect(s, LearningMapState.engaged);
  });

  test('⭐⭐ independentAttempt ĐÚNG khớp lineage ⇒ independentEvidence', () {
    final s = _state([
      _ev(EvidenceKind.hintShown, sourceDocumentId: _book, lessonNo: 1),
      _ev(EvidenceKind.independentAttempt,
          sourceDocumentId: _book, lessonNo: 1, correct: true),
    ]);
    expect(s, LearningMapState.independentEvidence,
        reason: '⭐⭐ đột biến bỏ qua independentAttempt ⇒ đỏ — đây là tín '
            'hiệu quan trọng nhất trong các trạng thái');
  });

  test('selfCorrection ĐÚNG cũng tính là bằng chứng tự làm', () {
    final s = _state([
      _ev(EvidenceKind.selfCorrection,
          sourceDocumentId: _book, lessonNo: 1, correct: true),
    ]);
    expect(s, LearningMapState.independentEvidence);
  });

  // ---- WAL-210 / Founder D1 ---------------------------------------------

  test('⭐⭐ D1: participation ⇒ trạng thái participation, KHÔNG «Tự làm được»',
      () {
    final s = _state([
      _ev(EvidenceKind.participation, sourceDocumentId: _book, lessonNo: 1),
    ]);
    expect(s, LearningMapState.participation,
        reason: '⭐⭐ đột biến đọc tự báo thành 🔵 ⇒ đỏ (audit C6b)');
    expect(s, isNot(LearningMapState.unseen),
        reason: 'bài trẻ đã làm xong không được hiện «Chưa học» (audit C7)');
  });

  test('⭐⭐ D1 tương thích: independentAttempt + correct null (dữ liệu cũ) đọc '
      'như participation — KHÔNG viết lại, KHÔNG «Tự làm được»', () {
    final s = _state([
      _ev(EvidenceKind.independentAttempt,
          sourceDocumentId: _book, lessonNo: 1), // correct: null
    ]);
    expect(s, LearningMapState.participation,
        reason: '⭐⭐ đây chính là sự kiện «Con đã trả lời xong» trước D1 — '
            'đột biến cho nó lên 🔵 ⇒ đỏ');
  });

  test('D1: tự làm SAI (đã chấm) ⇒ engaged — có bằng chứng, chưa tự làm được',
      () {
    final s = _state([
      _ev(EvidenceKind.independentAttempt,
          sourceDocumentId: _book, lessonNo: 1, correct: false),
    ]);
    expect(s, LearningMapState.engaged);
  });

  test('D1: đúng SAU gợi ý (postHintSuccess) ⇒ engaged, không phải tự làm', () {
    final s = _state([
      _ev(EvidenceKind.postHintSuccess,
          sourceDocumentId: _book, lessonNo: 1, correct: true),
    ]);
    expect(s, LearningMapState.engaged);
  });

  test('D1: selfCorrection KHÔNG chấm (correct null, vd Compose tự sửa) ⇒ '
      'không phải «Tự làm được»', () {
    final s = _state([
      _ev(EvidenceKind.selfCorrection, sourceDocumentId: _book, lessonNo: 1),
    ]);
    expect(s, isNot(LearningMapState.independentEvidence),
        reason: 'chưa ai chấm bản sửa — không được nói tự làm được');
  });

  test('thứ tự ưu tiên: tự-làm-đúng › học cùng SAM › tự báo', () {
    final participation =
        _ev(EvidenceKind.participation, sourceDocumentId: _book, lessonNo: 1);
    final hint = _ev(EvidenceKind.hintRequested,
        sourceDocumentId: _book, lessonNo: 1);
    final success = _ev(EvidenceKind.independentAttempt,
        sourceDocumentId: _book, lessonNo: 1, correct: true);
    expect(_state([participation, hint]), LearningMapState.engaged);
    expect(_state([participation, hint, success]),
        LearningMapState.independentEvidence);
  });

  test('sách khác/bài khác không lẫn vào nhau', () {
    final events = [
      _ev(EvidenceKind.independentAttempt,
          sourceDocumentId: _book, lessonNo: 1, correct: true),
    ];
    expect(_state(events, lessonNo: 2), LearningMapState.unseen,
        reason: 'khác bài, cùng sách ⇒ không lẫn');
    expect(
        learningMapStateFor(
            sourceDocumentId: '05-sgk-toan-5-tap-mot',
            lessonNo: 1,
            allEvents: events),
        LearningMapState.unseen,
        reason: 'cùng số bài, khác sách ⇒ không lẫn');
  });

  // ---- ROUND 4 / Founder §4 — STRICT EVIDENCE là mặc định ------------------

  test('⭐⭐ ROUND 4: tự làm ĐÚNG nhưng KHÔNG DẤU (dữ liệu trước hợp đồng) ⇒ '
      'engaged (historicalUnvalidated), KHÔNG «Tự làm được» — không viết lại',
      () {
    final legacy = _ev(EvidenceKind.independentAttempt,
        sourceDocumentId: _book, lessonNo: 1, correct: true, stamped: false);
    expect(legacy.readClass, EvidenceReadClass.historicalUnvalidated);
    expect(legacy.isValidatedIndependentSuccess, isFalse);
    expect(legacy.isLegacyUnstampedSuccess, isTrue);
    expect(_state([legacy]), LearningMapState.engaged,
        reason: '⭐⭐ đột biến đọc dữ liệu cũ thành 🔵 ở mặc định ⇒ đỏ');
    expect(childLabelFor(_state([legacy])).$2.contains('Tự làm'), isFalse);
    // Luật đọc-cũ chỉ khi GỌI TƯỜNG MINH (audit) — không phải mặc định.
    expect(
        learningMapStateFor(
            sourceDocumentId: _book,
            lessonNo: 1,
            allEvents: [legacy],
            requireValidation: false),
        LearningMapState.independentEvidence);
  });

  test('ROUND 4: selfCorrection đúng KHÔNG dấu cũng là historicalUnvalidated ⇒ '
      'engaged', () {
    final s = _state([
      _ev(EvidenceKind.selfCorrection,
          sourceDocumentId: _book, lessonNo: 1, correct: true, stamped: false),
    ]);
    expect(s, LearningMapState.engaged);
  });

  test('ROUND 4: có dấu được duyệt ⇒ vẫn 🔵 — đường Deep thật không mất gì', () {
    final s = _state([
      _ev(EvidenceKind.independentAttempt,
          sourceDocumentId: _book, lessonNo: 1, correct: true),
    ]);
    expect(s, LearningMapState.independentEvidence);
  });

  test('ROUND 4: nhãn lịch sử của lớp đọc — không «đúng», không «tự làm được»',
      () {
    expect(EvidenceReadClass.historicalUnvalidated.historyLabel,
        historicalUnvalidatedLabel);
    expect(historicalUnvalidatedLabel, 'ghi nhận trước hợp đồng mới');
    for (final c in EvidenceReadClass.values) {
      final l = c.historyLabel.toLowerCase();
      expect(l.contains('tự làm được'), isFalse, reason: c.name);
      expect(l.contains('đúng'), isFalse, reason: c.name);
      expect(RegExp(r'\d|%').hasMatch(l), isFalse, reason: c.name);
    }
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

  test('⭐ D1: nhãn «Tự làm được» CHỈ ở independentEvidence; participation có '
      'nhãn riêng, trung thực', () {
    for (final s in LearningMapState.values) {
      final (_, label) = childLabelFor(s);
      expect(label.contains('Tự làm được'), s == LearningMapState.independentEvidence,
          reason: 'trạng thái $s');
    }
    expect(childLabelFor(LearningMapState.participation).$2, 'Đã học');
    expect(childLabelFor(LearningMapState.participation),
        isNot(childLabelFor(LearningMapState.engaged)),
        reason: 'tự báo và học-cùng-SAM là hai trạng thái khác nhau');
  });
}
